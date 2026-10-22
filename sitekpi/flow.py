"""行動フロー: event mapping (pack step → the site's own GA4 event) + flow data.

- Mappings are stored per GA4 property (scope ``prop:<id>``) in the app DB, so
  everyone who connects the same property sees the same flow.
- ``apply_mapping`` aliases the site's counts onto the pack event names before
  the board computes its funnel, so 主転換 / 率 work with the site's naming.
- Sample boards get a flow synthesised from the pack DEMO (clearly labelled 見本).
"""

from __future__ import annotations

import os
import re
import secrets
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any, MutableMapping

from sitekpi.benchmarks import ROOT
from sitekpi.packs.flows import FLOW_STEPS

MAX_BRANCHES = 3
BRANCH_POS = ("above", "below")
LABEL_MAX = 24
EVENT_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,39}$")  # GA4 event-name rules

# Sample only: how strongly each channel converts relative to the site average.
_SAMPLE_CHANNEL_LIFT = {
    "Email": 1.7, "Direct": 1.35, "Paid Search": 1.25, "Organic Search": 1.05,
    "Referral": 1.0, "Affiliates": 0.95, "Organic Social": 0.7, "Paid Social": 0.6,
    "Display": 0.45, "Other": 0.8,
}


class MappingStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._lock = threading.Lock()
        path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute(
                "CREATE TABLE IF NOT EXISTS flow_branches ("
                " scope TEXT NOT NULL, pack TEXT NOT NULL, id TEXT NOT NULL,"
                " at TEXT NOT NULL, pos TEXT NOT NULL, event TEXT NOT NULL, label TEXT NOT NULL,"
                " created_at INTEGER NOT NULL, PRIMARY KEY (scope, pack, id))"
            )
            db.execute(
                "CREATE TABLE IF NOT EXISTS event_mappings ("
                " scope TEXT NOT NULL, pack TEXT NOT NULL, step TEXT NOT NULL,"
                " event TEXT NOT NULL, updated_at INTEGER NOT NULL,"
                " PRIMARY KEY (scope, pack, step))"
            )

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path, timeout=5, isolation_level=None)

    def get(self, scope: str, pack: str) -> dict[str, str]:
        with self._connect() as db:
            rows = db.execute(
                "SELECT step, event FROM event_mappings WHERE scope = ? AND pack = ?", (scope, pack)
            ).fetchall()
        return {s: e for s, e in rows}

    def set(self, scope: str, pack: str, step: str, event: str | None) -> None:
        with self._lock, self._connect() as db:
            if not event or event == step:
                db.execute(
                    "DELETE FROM event_mappings WHERE scope = ? AND pack = ? AND step = ?",
                    (scope, pack, step),
                )
                return
            db.execute(
                "INSERT INTO event_mappings (scope, pack, step, event, updated_at) VALUES (?, ?, ?, ?, ?)"
                " ON CONFLICT(scope, pack, step) DO UPDATE SET event = excluded.event,"
                " updated_at = excluded.updated_at",
                (scope, pack, step, event, int(time.time())),
            )


    # --- 分岐 (branches): another behaviour at the same stage, shown above / below it ---
    def branches(self, scope: str, pack: str) -> list[dict[str, str]]:
        with self._connect() as db:
            rows = db.execute(
                "SELECT id, at, pos, event, label FROM flow_branches WHERE scope = ? AND pack = ?"
                " ORDER BY created_at, rowid", (scope, pack),
            ).fetchall()
        return [{"id": i, "at": a, "pos": p, "event": e, "label": lb} for i, a, p, e, lb in rows]

    def add_branch(self, scope: str, pack: str, at: str, pos: str, event: str, label: str) -> str | None:
        """Returns the new id, or None when the limit is reached."""
        with self._lock, self._connect() as db:
            n = db.execute(
                "SELECT COUNT(*) FROM flow_branches WHERE scope = ? AND pack = ?", (scope, pack)
            ).fetchone()[0]
            if n >= MAX_BRANCHES:
                return None
            new_id = secrets.token_hex(4)
            db.execute(
                "INSERT INTO flow_branches (scope, pack, id, at, pos, event, label, created_at)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (scope, pack, new_id, at, pos, event, label, time.time_ns()),
            )
            return new_id

    def update_branch(self, scope: str, pack: str, branch_id: str, event: str, label: str) -> bool:
        with self._lock, self._connect() as db:
            cur = db.execute(
                "UPDATE flow_branches SET event = ?, label = ? WHERE scope = ? AND pack = ? AND id = ?",
                (event, label, scope, pack, branch_id),
            )
            return cur.rowcount > 0

    def delete_branch(self, scope: str, pack: str, branch_id: str) -> None:
        with self._lock, self._connect() as db:
            db.execute(
                "DELETE FROM flow_branches WHERE scope = ? AND pack = ? AND id = ?", (scope, pack, branch_id)
            )


_store: MappingStore | None = None
_store_lock = threading.Lock()


def get_mapping_store() -> MappingStore:
    global _store
    with _store_lock:
        path = Path(os.getenv("APP_DB_PATH") or (ROOT / ".data" / "app.sqlite3"))
        if _store is None or _store.path != path:
            _store = MappingStore(path)
        return _store


def property_scope(session: MutableMapping[str, Any]) -> str | None:
    prop = session.get("ga4_property")
    if session.get("ga4_credentials") and not session.get("ga4_demo") and isinstance(prop, dict) and prop.get("id"):
        return f"prop:{prop['id']}"
    return None


def load_mapping(session: MutableMapping[str, Any], pack: str) -> dict[str, str]:
    scope = property_scope(session)
    if not scope:
        return {}
    steps = set(FLOW_STEPS.get(pack) or [])
    return {k: v for k, v in get_mapping_store().get(scope, pack).items() if k in steps}


def load_branches(session: MutableMapping[str, Any], pack: str) -> list[dict[str, str]]:
    scope = property_scope(session)
    steps = set(FLOW_STEPS.get(pack) or [])
    rows = get_mapping_store().branches(scope, pack) if scope else []
    return [r for r in rows if r["at"] in steps and r["pos"] in BRANCH_POS]


def resolved_steps(pack: str, mapping: dict[str, str]) -> list[dict[str, Any]]:
    """[{step, event}] — event is what GA4 is asked for (mapped or the pack's own)."""
    return [{"step": s, "event": mapping.get(s) or s} for s in FLOW_STEPS.get(pack) or []]


def apply_mapping(data: dict[str, Any], pack: str, mapping: dict[str, str], *, primary: str) -> dict[str, Any]:
    """Alias the site's event counts onto pack event names (live board)."""
    if not mapping:
        return data
    out = dict(data)
    counts = dict(out.get("event_counts") or {})
    prev = dict(out.get("event_counts_prev") or {})
    alias: dict[str, str] = {}
    for step, site_event in mapping.items():
        if site_event in counts:
            counts[step] = counts[site_event]
        if site_event in prev:
            prev[step] = prev[site_event]
        alias[step] = site_event
    out["event_counts"], out["event_counts_prev"], out["event_alias"] = counts, prev, alias
    uu = int(out.get("uu") or 0)
    if primary in mapping:
        out["signups"] = int(counts.get(primary, 0))
        out["signup_rate"] = round(100 * out["signups"] / uu, 1) if uu else 0.0
    for field, names in (("pay_start", ("pay_start", "begin_checkout")), ("pay_success", ("pay_success", "purchase"))):
        for n in names:
            if n in mapping:
                out[field] = int(counts.get(n, 0))
                break
    if out.get("pay_start"):
        out["pay_cvr"] = round(100 * int(out.get("pay_success") or 0) / int(out["pay_start"]), 1)
    return out


def sample_flow(pack: str, data: dict[str, Any]) -> dict[str, Any]:
    """Flow numbers synthesised from the DEMO (unique users per step, per channel)."""
    entry = int(data.get("uu") or 0)
    counts = data.get("event_counts") or {}
    steps = FLOW_STEPS.get(pack) or []
    totals: dict[str, int] = {}
    prev = entry
    for s in steps:
        users = min(int(counts.get(s, 0)), int(prev * 0.92))
        totals[s] = max(users, 0)
        prev = totals[s] or prev
    channels = [(str(n), float(p)) for n, p in (data.get("channels") or [])]
    entry_by = {n: round(entry * p / 100) for n, p in channels}
    by_ch: dict[str, dict[str, int]] = {n: {} for n, _ in channels}
    for i, s in enumerate(steps, start=1):
        depth = i / max(len(steps), 1)
        raw = {n: entry_by[n] * (totals[s] / entry if entry else 0) * (_SAMPLE_CHANNEL_LIFT.get(n, 1.0) ** (0.6 + depth))
               for n, _ in channels}
        scale = totals[s] / sum(raw.values()) if sum(raw.values()) else 0
        for n in raw:
            before = by_ch[n][steps[i - 2]] if i > 1 else entry_by[n]
            by_ch[n][s] = min(round(raw[n] * scale), before)
    return {"entry": entry, "entry_by": entry_by, "totals": totals, "by_channel": by_ch, "sample": True}


def valid_event_name(name: str) -> bool:
    return bool(EVENT_NAME_RE.match(name))


def clean_label(raw: str) -> str:
    return " ".join(str(raw or "").split())[:LABEL_MAX]
