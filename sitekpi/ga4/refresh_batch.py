"""Daily batch: refresh every connected site's GA4 OAuth grant before it's close to expiring.

GA4 grants live in the server-side session store (sitekpi.session / sitekpi.firestore_store),
keyed by sha256(session id) — there's no separate "site" registry, so this walks every live
session row instead of looking sites up by id. ``creds_from_session`` (sitekpi.ga4.oauth)
already refreshes lazily on the next request after expiry; this batch does it proactively so a
site never shows up broken because nobody happened to load the board right after expiry.

A grant that fails to refresh (revoked, network, ...) is recorded so a future notification
banner can read ``list_failures()`` (served at GET /hq/api/ga4-refresh-failures, sitekpi/visitlog.py)
instead of only finding out when the board breaks. A later successful refresh clears the record.

Run once a day via scripts/ga4_refresh_batch.py (cron / Cloud Scheduler wiring is deploy
config, not this module's job).
"""

from __future__ import annotations

import datetime as dt
import json
import threading
from pathlib import Path
from typing import Any

from sitekpi import firestore_store
from sitekpi.ga4.oauth import Credentials, GoogleAuthRequest, HAS_GOOGLE_AUTH, SCOPES

ROOT = Path(__file__).resolve().parents[2]
REFRESH_WINDOW = 24 * 60 * 60  # proactively refresh grants expiring within a day
_FAILURES_PATH = ROOT / ".data" / "ga4_refresh_failures.json"
_lock = threading.Lock()


def _session_store() -> Any:
    from sitekpi.session import SQLiteSessionStore, session_settings

    s = session_settings()
    max_age = 14 * 24 * 60 * 60  # same as sitekpi.app.SESSION_MAX_AGE
    if firestore_store.enabled():
        return firestore_store.FirestoreSessionStore(s["secret"], max_age)
    return SQLiteSessionStore(s["db_path"], s["secret"], max_age)


def _load_local_failures() -> dict[str, Any]:
    if not _FAILURES_PATH.exists():
        return {}
    try:
        data = json.loads(_FAILURES_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def _save_local_failures(rows: dict[str, Any]) -> None:
    _FAILURES_PATH.parent.mkdir(parents=True, exist_ok=True)
    _FAILURES_PATH.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _record_failure(id_hash: str, email: str, error: str) -> None:
    row = {"email": email, "error": error[:300], "at": int(dt.datetime.now(dt.timezone.utc).timestamp())}
    if firestore_store.enabled():
        firestore_store.FirestoreGa4RefreshFailureStore().put(id_hash, row)
        return
    with _lock:
        rows = _load_local_failures()
        rows[id_hash] = row
        _save_local_failures(rows)


def _clear_failure(id_hash: str) -> None:
    if firestore_store.enabled():
        firestore_store.FirestoreGa4RefreshFailureStore().delete(id_hash)
        return
    with _lock:
        rows = _load_local_failures()
        if rows.pop(id_hash, None) is not None:
            _save_local_failures(rows)


def list_failures() -> list[dict[str, Any]]:
    """Sites whose GA4 grant is currently failing to refresh — for a future notification banner."""
    if firestore_store.enabled():
        return firestore_store.FirestoreGa4RefreshFailureStore().all()
    rows = _load_local_failures()
    return [{"id_hash": k, **v} for k, v in rows.items()]


def _seconds_until_expiry(creds: Any) -> float | None:
    if not creds.expiry:
        return None
    now = dt.datetime.now(dt.timezone.utc) if creds.expiry.tzinfo else dt.datetime.utcnow()
    return (creds.expiry - now).total_seconds()


def refresh_all() -> dict[str, int]:
    """Refresh every connected session's GA4 grant that's close to expiring.

    Returns {"checked", "refreshed", "failed"} (sites with a grant, proactively refreshed,
    refresh attempted and failed) for the caller to log.
    """
    counts = {"checked": 0, "refreshed": 0, "failed": 0}
    if not HAS_GOOGLE_AUTH:
        return counts
    store = _session_store()
    # store.all_rows() decrypts every live session regardless of GA4 status; this loop is the
    # only place that narrows that down to "sessions with a GA4 grant" — keep it that way as
    # more batches read all_rows() so decrypting the whole session table stays scoped to need.
    for id_hash, data, expires_at in store.all_rows():
        info = data.get("ga4_credentials")
        if not info:
            continue
        counts["checked"] += 1
        try:
            creds = Credentials.from_authorized_user_info(info, SCOPES)
        except ValueError:
            continue  # malformed grant — nothing this batch can refresh
        if not creds.refresh_token:
            continue
        left = _seconds_until_expiry(creds)
        if left is not None and left > REFRESH_WINDOW:
            continue  # not due yet
        email = str(data.get("ga4_email") or "")
        try:
            creds.refresh(GoogleAuthRequest())
        except Exception as exc:  # noqa: BLE001 — one bad grant (revoked, network, ...) must not stop the batch
            counts["failed"] += 1
            _record_failure(id_hash, email, str(exc))
            continue
        data["ga4_credentials"] = json.loads(creds.to_json())
        store.save_by_hash(id_hash, data, expires_at)
        _clear_failure(id_hash)
        counts["refreshed"] += 1
    return counts
