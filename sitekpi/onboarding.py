"""オンボーディング成功指標: GA4 連携完了 → 初回ボード表示 → 初回インサイトカードのクリック。

Each step is logged once per browser (session-scoped owner id, no PII — same
anonymous-owner pattern as benchmarks.scope_for). ``onboarding_ttfv`` is
recomputed on every new step, so "time from connecting to the first real
value" is always up to date for that owner.
"""

from __future__ import annotations

import os
import secrets
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any, MutableMapping

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

ROOT = Path(__file__).resolve().parents[1]

EVENT_GA4_CONNECTED = "ga4_connected"
EVENT_BOARD_VIEW = "board_view_first"
EVENT_INSIGHT_CLICK = "insight_click_first"
STEPS = (EVENT_GA4_CONNECTED, EVENT_BOARD_VIEW, EVENT_INSIGHT_CLICK)

router = APIRouter(tags=["onboarding"])


def ttfv_from_events(events: dict[str, int]) -> dict[str, int]:
    """{..._at, ttfv_board_seconds, ttfv_insight_seconds} — elapsed since ga4_connected."""
    out = {f"{e}_at": events[e] for e in STEPS if e in events}
    connected = events.get(EVENT_GA4_CONNECTED)
    if connected:
        if EVENT_BOARD_VIEW in events:
            out["ttfv_board_seconds"] = max(0, events[EVENT_BOARD_VIEW] - connected)
        if EVENT_INSIGHT_CLICK in events:
            out["ttfv_insight_seconds"] = max(0, events[EVENT_INSIGHT_CLICK] - connected)
    return out


class OnboardingStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._lock = threading.Lock()
        from sitekpi.sqlite_util import connect, init_wal

        init_wal(path)
        with connect(path) as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS onboarding_events ("
                " owner TEXT NOT NULL, event TEXT NOT NULL, at INTEGER NOT NULL,"
                " PRIMARY KEY (owner, event))"
            )
            db.execute(
                "CREATE TABLE IF NOT EXISTS onboarding_ttfv ("
                " owner TEXT PRIMARY KEY,"
                " ga4_connected_at INTEGER, board_view_first_at INTEGER, insight_click_first_at INTEGER,"
                " ttfv_board_seconds INTEGER, ttfv_insight_seconds INTEGER, updated_at INTEGER NOT NULL)"
            )

    def _connect(self) -> sqlite3.Connection:
        from sitekpi.sqlite_util import connect

        return connect(self.path)

    def log_first(self, owner: str, event: str) -> bool:
        """Records ``event`` for ``owner`` the first time only; returns whether it was new."""
        now = int(time.time())
        with self._lock, self._connect() as db:
            cur = db.execute(
                "INSERT OR IGNORE INTO onboarding_events (owner, event, at) VALUES (?, ?, ?)",
                (owner, event, now),
            )
            if cur.rowcount == 0:
                return False
            rows = db.execute(
                "SELECT event, at FROM onboarding_events WHERE owner = ?", (owner,)
            ).fetchall()
            events = {e: a for e, a in rows}
            ttfv = ttfv_from_events(events)
            db.execute(
                "INSERT INTO onboarding_ttfv (owner, ga4_connected_at, board_view_first_at,"
                " insight_click_first_at, ttfv_board_seconds, ttfv_insight_seconds, updated_at)"
                " VALUES (?, ?, ?, ?, ?, ?, ?)"
                " ON CONFLICT(owner) DO UPDATE SET ga4_connected_at = excluded.ga4_connected_at,"
                " board_view_first_at = excluded.board_view_first_at,"
                " insight_click_first_at = excluded.insight_click_first_at,"
                " ttfv_board_seconds = excluded.ttfv_board_seconds,"
                " ttfv_insight_seconds = excluded.ttfv_insight_seconds, updated_at = excluded.updated_at",
                (
                    owner,
                    events.get(EVENT_GA4_CONNECTED),
                    events.get(EVENT_BOARD_VIEW),
                    events.get(EVENT_INSIGHT_CLICK),
                    ttfv.get("ttfv_board_seconds"),
                    ttfv.get("ttfv_insight_seconds"),
                    now,
                ),
            )
            return True

    def ttfv(self, owner: str) -> dict[str, Any]:
        with self._connect() as db:
            row = db.execute(
                "SELECT ga4_connected_at, board_view_first_at, insight_click_first_at,"
                " ttfv_board_seconds, ttfv_insight_seconds FROM onboarding_ttfv WHERE owner = ?",
                (owner,),
            ).fetchone()
        if not row:
            return {}
        keys = ("ga4_connected_at", "board_view_first_at", "insight_click_first_at",
                "ttfv_board_seconds", "ttfv_insight_seconds")
        return {k: v for k, v in zip(keys, row) if v is not None}


_store: OnboardingStore | None = None
_store_lock = threading.Lock()


def get_store() -> Any:
    global _store
    with _store_lock:
        from sitekpi import firestore_store

        if firestore_store.enabled():  # Cloud Run: shared and persistent
            if not isinstance(_store, firestore_store.FirestoreOnboardingStore):
                _store = firestore_store.FirestoreOnboardingStore()  # type: ignore[assignment]
            return _store
        if not isinstance(_store, OnboardingStore):
            path = Path(os.getenv("APP_DB_PATH") or (ROOT / ".data" / "app.sqlite3"))
            _store = OnboardingStore(path)
        return _store


def _owner(session: MutableMapping[str, Any], *, create: bool) -> str | None:
    owner = session.get("onboard_owner")
    if not owner and create:
        owner = secrets.token_urlsafe(16)
        session["onboard_owner"] = owner
    return owner if isinstance(owner, str) else None


def _log(session: MutableMapping[str, Any], event: str) -> None:
    """Connected sessions only — anonymous browsing never gets an owner id."""
    if not (session.get("ga4_credentials") or session.get("ga4_demo")):
        return
    owner = _owner(session, create=True)
    if not owner:
        return
    try:
        get_store().log_first(owner, event)
    except Exception:  # noqa: BLE001 — analytics must never break the request
        pass


def log_ga4_connected(session: MutableMapping[str, Any]) -> None:
    _log(session, EVENT_GA4_CONNECTED)


def log_board_view(session: MutableMapping[str, Any]) -> None:
    _log(session, EVENT_BOARD_VIEW)


def log_insight_click(session: MutableMapping[str, Any]) -> None:
    _log(session, EVENT_INSIGHT_CLICK)


@router.post("/track/insight-click")
async def track_insight_click(request: Request) -> JSONResponse:
    log_insight_click(request.session)
    return JSONResponse({"ok": True})
