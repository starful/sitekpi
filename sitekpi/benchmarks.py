"""業界目安: pack defaults + user overrides (自社目安).

Pack defaults live in sitekpi/packs/*.py. They are provisional values set by
SiteKPI (no external source yet) — every default is labelled that way. A pack
benchmark may later carry ``"source": {"label": ..., "url": ...}``.

Overrides are stored per *scope*:
- ``prop:<GA4 property id>`` — the connected /live board (shared by everyone who
  connects that property here; access is checked when the property is chosen).
- ``sess:<random owner id>`` — sample/demo boards, this browser only.
"""

from __future__ import annotations

import math
import os
import secrets
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any, MutableMapping

ROOT = Path(__file__).resolve().parents[1]

PERCENT_MAX = 100.0
OTHER_MAX = 1000.0


class BenchmarkStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._lock = threading.Lock()
        path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute(
                "CREATE TABLE IF NOT EXISTS benchmark_overrides ("
                " scope TEXT NOT NULL, pack TEXT NOT NULL, metric TEXT NOT NULL,"
                " low REAL NOT NULL, high REAL NOT NULL, updated_at INTEGER NOT NULL,"
                " PRIMARY KEY (scope, pack, metric))"
            )

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path, timeout=5, isolation_level=None)

    def get(self, scope: str, pack: str) -> dict[str, dict[str, float]]:
        with self._connect() as db:
            rows = db.execute(
                "SELECT metric, low, high, updated_at FROM benchmark_overrides"
                " WHERE scope = ? AND pack = ?",
                (scope, pack),
            ).fetchall()
        return {m: {"low": lo, "high": hi, "updated_at": ts} for m, lo, hi, ts in rows}

    def set_many(self, scope: str, pack: str, values: dict[str, tuple[float, float]]) -> None:
        now = int(time.time())
        with self._lock, self._connect() as db:
            db.executemany(
                "INSERT INTO benchmark_overrides (scope, pack, metric, low, high, updated_at)"
                " VALUES (?, ?, ?, ?, ?, ?) ON CONFLICT(scope, pack, metric) DO UPDATE SET"
                " low = excluded.low, high = excluded.high, updated_at = excluded.updated_at",
                [(scope, pack, m, lo, hi, now) for m, (lo, hi) in values.items()],
            )

    def reset(self, scope: str, pack: str, metric: str | None = None) -> None:
        with self._lock, self._connect() as db:
            if metric:
                db.execute(
                    "DELETE FROM benchmark_overrides WHERE scope = ? AND pack = ? AND metric = ?",
                    (scope, pack, metric),
                )
            else:
                db.execute(
                    "DELETE FROM benchmark_overrides WHERE scope = ? AND pack = ?", (scope, pack)
                )


_store: BenchmarkStore | None = None
_store_lock = threading.Lock()


def get_store() -> BenchmarkStore:
    global _store
    with _store_lock:
        if _store is None:
            path = Path(os.getenv("APP_DB_PATH") or (ROOT / ".data" / "app.sqlite3"))
            _store = BenchmarkStore(path)
        return _store


def scope_for(session: MutableMapping[str, Any], *, live: bool, create: bool = False) -> str | None:
    """Where overrides for the board being shown are kept.

    Sample/demo boards use a per-browser owner id that is only created when the
    user saves something (create=True), so plain visits don't create sessions.
    """
    prop = session.get("ga4_property")
    if live and session.get("ga4_credentials") and isinstance(prop, dict) and prop.get("id"):
        return f"prop:{prop['id']}"
    owner = session.get("bench_owner")
    if not owner and create:
        owner = secrets.token_urlsafe(16)
        session["bench_owner"] = owner
    return f"sess:{owner}" if owner else None


def load_effective(
    session: MutableMapping[str, Any], pack: str, defaults: dict[str, dict[str, Any]], *, live: bool
) -> dict[str, dict[str, Any]]:
    scope = scope_for(session, live=live)
    overrides = get_store().get(scope, pack) if scope else {}
    return effective_benchmarks(defaults, overrides)


def source_of(spec: dict[str, Any]) -> dict[str, str]:
    src = spec.get("source")
    if isinstance(src, dict) and src.get("label"):
        return {"kind": "cited", "label": str(src["label"]), "url": str(src.get("url") or "")}
    return {"kind": "provisional", "label": "", "url": ""}


def effective_benchmarks(
    defaults: dict[str, dict[str, Any]], overrides: dict[str, dict[str, float]]
) -> dict[str, dict[str, Any]]:
    """Pack defaults with 自社目安 applied; each spec says whether it is custom."""
    out: dict[str, dict[str, Any]] = {}
    for key, spec in defaults.items():
        merged = dict(spec)
        merged["source"] = source_of(spec)
        merged["default_low"], merged["default_high"] = spec["low"], spec["high"]
        ov = overrides.get(key)
        merged["custom"] = bool(ov)
        if ov:
            merged["low"], merged["high"] = ov["low"], ov["high"]
        out[key] = merged
    return out


def parse_range(raw_low: str, raw_high: str, unit: str) -> tuple[float, float] | str:
    """Validate one row from the form. Returns (low, high) or an error key."""
    try:
        low = float(str(raw_low).strip().replace(",", ""))
        high = float(str(raw_high).strip().replace(",", ""))
    except ValueError:
        return "bench_edit.err.number"
    if not (math.isfinite(low) and math.isfinite(high)):
        return "bench_edit.err.number"
    upper = PERCENT_MAX if unit == "%" else OTHER_MAX
    if low < 0 or high > upper:
        return "bench_edit.err.range_pct" if unit == "%" else "bench_edit.err.range"
    if low >= high:
        return "bench_edit.err.order"
    return (round(low, 4), round(high, 4))
