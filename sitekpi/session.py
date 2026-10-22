"""Server-side sessions.

The browser only holds a random session id (HttpOnly cookie). Session data —
including the GA4 OAuth grant (refresh token) — lives server-side in SQLite,
encrypted at rest (Fernet). Rows are keyed by sha256(session id), so a copy of
the DB alone cannot be turned back into working cookies.

`request.session` keeps working exactly like Starlette's SessionMiddleware.
Call `regenerate_session(request)` after a privilege change (e.g. Google login)
to issue a fresh id (prevents session fixation).
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import secrets
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any

from cryptography.fernet import Fernet, InvalidToken
from starlette.datastructures import MutableHeaders
from starlette.requests import HTTPConnection, Request
from starlette.types import ASGIApp, Message, Receive, Scope, Send

ROOT = Path(__file__).resolve().parents[1]
_ROTATE_KEY = "sitekpi.session.rotate"
DEV_SECRET = "kpistarter-dev-secret-change-me"


def _fernet_key(secret: str) -> bytes:
    explicit = (os.getenv("SESSION_ENCRYPTION_KEY") or "").strip()
    if explicit:
        return explicit.encode()
    digest = hashlib.sha256(b"sitekpi-session-v1:" + secret.encode()).digest()
    return base64.urlsafe_b64encode(digest)


class SQLiteSessionStore:
    """Encrypted session rows in a single SQLite file (one host, many workers)."""

    def __init__(self, path: Path, secret: str, max_age: int) -> None:
        self.path = path
        self.max_age = max_age
        self._fernet = Fernet(_fernet_key(secret))
        self._lock = threading.Lock()
        path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute(
                "CREATE TABLE IF NOT EXISTS sessions ("
                " id_hash TEXT PRIMARY KEY,"
                " data BLOB NOT NULL,"
                " expires_at INTEGER NOT NULL)"
            )
        self.purge_expired()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path, timeout=5, isolation_level=None)

    @staticmethod
    def _key(sid: str) -> str:
        return hashlib.sha256(sid.encode()).hexdigest()

    def load(self, sid: str) -> tuple[dict[str, Any], int] | None:
        with self._connect() as db:
            row = db.execute(
                "SELECT data, expires_at FROM sessions WHERE id_hash = ?", (self._key(sid),)
            ).fetchone()
        if not row or row[1] < time.time():
            return None
        try:
            data = json.loads(self._fernet.decrypt(row[0]))
        except (InvalidToken, ValueError):
            return None  # key rotated or corrupt row → treat as a fresh session
        return (data if isinstance(data, dict) else {}), int(row[1])

    def save(self, sid: str, data: dict[str, Any]) -> None:
        blob = self._fernet.encrypt(json.dumps(data, ensure_ascii=False).encode())
        expires = int(time.time()) + self.max_age
        with self._lock, self._connect() as db:
            db.execute(
                "INSERT INTO sessions (id_hash, data, expires_at) VALUES (?, ?, ?)"
                " ON CONFLICT(id_hash) DO UPDATE SET data = excluded.data,"
                " expires_at = excluded.expires_at",
                (self._key(sid), blob, expires),
            )

    def delete(self, sid: str) -> None:
        with self._lock, self._connect() as db:
            db.execute("DELETE FROM sessions WHERE id_hash = ?", (self._key(sid),))

    def purge_expired(self) -> None:
        with self._lock, self._connect() as db:
            db.execute("DELETE FROM sessions WHERE expires_at < ?", (int(time.time()),))


class ServerSessionMiddleware:
    """Drop-in replacement for Starlette's cookie SessionMiddleware."""

    def __init__(
        self,
        app: ASGIApp,
        *,
        store: SQLiteSessionStore,
        cookie_name: str = "sitekpi_sid",
        https_only: bool = False,
        same_site: str = "lax",
        legacy_cookies: tuple[str, ...] = (),
    ) -> None:
        self.app = app
        self.store = store
        self.cookie_name = cookie_name
        self.https_only = https_only
        self.same_site = same_site
        self.legacy_cookies = legacy_cookies

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        conn = HTTPConnection(scope)
        sid = conn.cookies.get(self.cookie_name) or ""
        loaded = self.store.load(sid) if sid else None
        initial, expires_at = loaded if loaded else ({}, 0)
        scope["session"] = dict(initial)
        before = json.dumps(initial, sort_keys=True, default=str)
        stale_legacy = [c for c in self.legacy_cookies if c in conn.cookies]

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                session = scope["session"]
                rotate = bool(scope.get(_ROTATE_KEY))
                if not session:
                    if sid:
                        if loaded:
                            self.store.delete(sid)
                        headers.append("Set-Cookie", self._cookie("", expire=True))
                elif rotate or not loaded:
                    if sid and loaded:
                        self.store.delete(sid)
                    new_sid = secrets.token_urlsafe(32)
                    self.store.save(new_sid, session)
                    headers.append("Set-Cookie", self._cookie(new_sid))
                else:
                    changed = json.dumps(session, sort_keys=True, default=str) != before
                    # sliding expiry, but write at most ~once a day when unchanged
                    if changed or expires_at - time.time() < self.store.max_age - 86400:
                        self.store.save(sid, session)
                        headers.append("Set-Cookie", self._cookie(sid))
                for name in stale_legacy:
                    headers.append(
                        "Set-Cookie", f"{name}=; Path=/; Max-Age=0; HttpOnly; SameSite=lax"
                    )
            await send(message)

        await self.app(scope, receive, send_wrapper)

    def _cookie(self, value: str, *, expire: bool = False) -> str:
        max_age = 0 if expire else self.store.max_age
        parts = [
            f"{self.cookie_name}={value}",
            "Path=/",
            f"Max-Age={max_age}",
            "HttpOnly",
            f"SameSite={self.same_site}",
        ]
        if self.https_only:
            parts.append("Secure")
        return "; ".join(parts)


def regenerate_session(request: Request) -> None:
    """Issue a new session id at the end of this request (keeps the data)."""
    request.scope[_ROTATE_KEY] = True


def session_settings() -> dict[str, Any]:
    """Resolve secret / cookie flags from env; refuse insecure config on https."""
    base = (os.getenv("APP_BASE_URL") or "").lower()
    on_https = base.startswith("https://")
    secret = (os.getenv("SESSION_SECRET") or "").strip()
    if not secret or secret in (DEV_SECRET, "change-me-to-a-long-random-string"):
        if on_https:
            raise RuntimeError(
                "SESSION_SECRET must be set to a long random value when APP_BASE_URL is https."
            )
        secret = DEV_SECRET
    secure_env = (os.getenv("SESSION_COOKIE_SECURE") or "").strip().lower()
    https_only = on_https if not secure_env else secure_env in ("1", "true", "yes")
    db_path = Path(os.getenv("SESSION_DB_PATH") or (ROOT / ".data" / "sessions.sqlite3"))
    return {"secret": secret, "https_only": https_only, "db_path": db_path}
