"""Shared SQLite open settings for local stores (.data/app.sqlite3 and friends).

Used by session / benchmarks / flow mapping — not by Cloud Run (Firestore there).
WAL + short timeout keeps concurrent sync routes from blocking each other;
isolation_level=None = autocommit (callers wrap explicit transactions when needed).
"""

from __future__ import annotations

import sqlite3
from pathlib import Path


def connect(path: Path | str) -> sqlite3.Connection:
    """Open with a 5s busy timeout and autocommit."""
    return sqlite3.connect(Path(path), timeout=5, isolation_level=None)


def init_wal(path: Path | str) -> None:
    """Ensure parent dirs exist and turn on WAL once for this file."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with connect(p) as db:
        db.execute("PRAGMA journal_mode=WAL")
