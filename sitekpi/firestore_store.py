"""Firestore-backed stores for Cloud Run (STORE_BACKEND=firestore).

Cloud Run's disk is per instance and wiped on restart, so sessions, flow edits, 自社目安 and
feedback live in Firestore there. Locally (default) the SQLite stores are used unchanged.

Layout (one top-level collection per site, like the other starful sites):

    {FIRESTORE_COLLECTION}/sessions/rows/{sha256(session id)}   data (Fernet-encrypted), expires_at
    {FIRESTORE_COLLECTION}/flow/rows/{scope}|{pack}             mapping, custom, branches
    {FIRESTORE_COLLECTION}/benchmarks/rows/{scope}|{pack}       metrics: {metric: {low, high, updated_at}}
    {FIRESTORE_COLLECTION}/feedback/rows/{auto id}              screen, vote, comment, locale, at

Sessions also carry ``expire_at`` (a timestamp) so a Firestore TTL policy on that field can
delete old ones; nothing else depends on it.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import secrets
import threading
import time
from typing import Any

from cryptography.fernet import Fernet, InvalidToken

_client: Any = None
_client_lock = threading.Lock()


def enabled() -> bool:
    return (os.getenv("STORE_BACKEND") or "").strip().lower() == "firestore"


def collection_root() -> str:
    return (os.getenv("FIRESTORE_COLLECTION") or "sitekpi").strip() or "sitekpi"


def get_client() -> Any:
    """google.cloud.firestore.Client with Application Default Credentials (Cloud Run SA)."""
    global _client
    with _client_lock:
        if _client is None:
            from google.cloud import firestore  # imported only when the backend is used

            project = (os.getenv("FIRESTORE_PROJECT") or "").strip() or None
            _client = firestore.Client(project=project)
        return _client


def set_client(client: Any) -> None:
    """Tests: plug in a fake client."""
    global _client
    with _client_lock:
        _client = client


class _Rows:
    """{root}/{kind}/rows/{id} — get / put / delete one document."""

    def __init__(self, kind: str, client: Any | None = None) -> None:
        self.kind = kind
        self._client = client

    def _col(self) -> Any:
        db = self._client or get_client()
        return db.collection(collection_root()).document(self.kind).collection("rows")

    def get(self, doc_id: str) -> dict[str, Any] | None:
        snap = self._col().document(doc_id).get()
        return snap.to_dict() if snap.exists else None

    def put(self, doc_id: str, data: dict[str, Any]) -> None:
        self._col().document(doc_id).set(data)

    def add(self, data: dict[str, Any]) -> None:
        self._col().document().set(data)

    def delete(self, doc_id: str) -> None:
        self._col().document(doc_id).delete()


def _pair(scope: str, pack: str) -> str:
    return f"{scope}|{pack}".replace("/", "_")


# --- sessions ------------------------------------------------------------------------------


class FirestoreSessionStore:
    """Same interface as session.SQLiteSessionStore; rows are encrypted the same way."""

    def __init__(self, secret: str, max_age: int, client: Any | None = None) -> None:
        from sitekpi.session import _fernet_key

        self.max_age = max_age
        self._fernet = Fernet(_fernet_key(secret))
        self._rows = _Rows("sessions", client)

    @staticmethod
    def _key(sid: str) -> str:
        return hashlib.sha256(sid.encode()).hexdigest()

    def load(self, sid: str) -> tuple[dict[str, Any], int] | None:
        row = self._rows.get(self._key(sid))
        if not row or int(row.get("expires_at") or 0) < time.time():
            return None
        try:
            data = json.loads(self._fernet.decrypt(bytes(row["data"])))
        except (InvalidToken, ValueError, KeyError, TypeError):
            return None
        return (data if isinstance(data, dict) else {}), int(row["expires_at"])

    def save(self, sid: str, data: dict[str, Any]) -> None:
        expires = int(time.time()) + self.max_age
        self._rows.put(self._key(sid), {
            "data": self._fernet.encrypt(json.dumps(data, ensure_ascii=False).encode()),
            "expires_at": expires,
            "expire_at": dt.datetime.fromtimestamp(expires, tz=dt.timezone.utc),
        })

    def delete(self, sid: str) -> None:
        self._rows.delete(self._key(sid))

    def purge_expired(self) -> None:
        """Firestore: a TTL policy on ``expire_at`` does this."""


# --- 行動フロー (same interface as flow.MappingStore) ---------------------------------------


class FirestoreMappingStore:
    path = None  # flow.get_mapping_store compares paths for the SQLite store

    def __init__(self, client: Any | None = None) -> None:
        self._rows = _Rows("flow", client)
        self._lock = threading.Lock()

    def _load(self, scope: str, pack: str) -> dict[str, Any]:
        return self._rows.get(_pair(scope, pack)) or {"scope": scope, "pack": pack}

    def _save(self, scope: str, pack: str, doc: dict[str, Any]) -> None:
        doc.update({"scope": scope, "pack": pack, "updated_at": int(time.time())})
        if not doc.get("mapping") and not doc.get("custom") and not doc.get("branches"):
            self._rows.delete(_pair(scope, pack))
        else:
            self._rows.put(_pair(scope, pack), doc)

    def get(self, scope: str, pack: str) -> dict[str, str]:
        return dict(self._load(scope, pack).get("mapping") or {})

    def set(self, scope: str, pack: str, step: str, event: str | None) -> None:
        with self._lock:
            doc = self._load(scope, pack)
            mapping = dict(doc.get("mapping") or {})
            if not event or event == step:
                mapping.pop(step, None)
            else:
                mapping[step] = event
            doc["mapping"] = mapping
            self._save(scope, pack, doc)

    def custom_flow(self, scope: str, pack: str) -> list[dict[str, str]] | None:
        steps = self._load(scope, pack).get("custom")
        return steps if isinstance(steps, list) and steps else None

    def set_custom_flow(self, scope: str, pack: str, steps: list[dict[str, str]] | None) -> None:
        with self._lock:
            doc = self._load(scope, pack)
            doc["custom"] = list(steps) if steps else None
            self._save(scope, pack, doc)

    def branches(self, scope: str, pack: str) -> list[dict[str, str]]:
        rows = self._load(scope, pack).get("branches") or []
        return [{k: str(b.get(k) or "") for k in ("id", "at", "pos", "event", "label")} for b in rows]

    def add_branch(self, scope: str, pack: str, at: str, pos: str, event: str, label: str) -> str | None:
        from sitekpi.flow import MAX_BRANCHES

        with self._lock:
            doc = self._load(scope, pack)
            rows = list(doc.get("branches") or [])
            if len(rows) >= MAX_BRANCHES:
                return None
            new_id = secrets.token_hex(4)
            rows.append({"id": new_id, "at": at, "pos": pos, "event": event, "label": label})
            doc["branches"] = rows
            self._save(scope, pack, doc)
            return new_id

    def update_branch(self, scope: str, pack: str, branch_id: str, event: str, label: str) -> bool:
        with self._lock:
            doc = self._load(scope, pack)
            rows = list(doc.get("branches") or [])
            hit = False
            for b in rows:
                if b.get("id") == branch_id:
                    b["event"], b["label"], hit = event, label, True
            if hit:
                doc["branches"] = rows
                self._save(scope, pack, doc)
            return hit

    def delete_branch(self, scope: str, pack: str, branch_id: str) -> None:
        with self._lock:
            doc = self._load(scope, pack)
            doc["branches"] = [b for b in doc.get("branches") or [] if b.get("id") != branch_id]
            self._save(scope, pack, doc)


# --- 自社目安 (same interface as benchmarks.BenchmarkStore) --------------------------------


class FirestoreBenchmarkStore:
    def __init__(self, client: Any | None = None) -> None:
        self._rows = _Rows("benchmarks", client)
        self._lock = threading.Lock()

    def get(self, scope: str, pack: str) -> dict[str, dict[str, float]]:
        doc = self._rows.get(_pair(scope, pack)) or {}
        return {m: dict(v) for m, v in (doc.get("metrics") or {}).items()}

    def set_many(self, scope: str, pack: str, values: dict[str, tuple[float, float]]) -> None:
        now = int(time.time())
        with self._lock:
            metrics = self.get(scope, pack)
            for m, (lo, hi) in values.items():
                metrics[m] = {"low": float(lo), "high": float(hi), "updated_at": now}
            self._rows.put(_pair(scope, pack), {"scope": scope, "pack": pack, "metrics": metrics})

    def reset(self, scope: str, pack: str, metric: str | None = None) -> None:
        with self._lock:
            if not metric:
                self._rows.delete(_pair(scope, pack))
                return
            metrics = self.get(scope, pack)
            metrics.pop(metric, None)
            if metrics:
                self._rows.put(_pair(scope, pack), {"scope": scope, "pack": pack, "metrics": metrics})
            else:
                self._rows.delete(_pair(scope, pack))


# --- feedback -----------------------------------------------------------------------------


class FirestoreFeedbackStore:
    def __init__(self, client: Any | None = None) -> None:
        self._rows = _Rows("feedback", client)

    def add(self, row: dict[str, Any]) -> None:
        self._rows.add(dict(row))
