"""Shared number formatting for board / flow / GA4 views.

Prefer these helpers over ad-hoc f-strings so L0 tiles, L2 rows, and 行動フロー
use the same commas / % digits / empty glyph (—). Do not invent locale-specific
currency here — money stays pack DEMO or 業務DB.
"""

from __future__ import annotations

from typing import Any


def fmt_int(n: int | float) -> str:
    """Whole number with thousands separators (users, sessions, event counts)."""
    return f"{int(round(n)):,}"


def fmt_pct(n: float | None, digits: int = 1, *, empty: str = "—") -> str:
    """Percent with a fixed number of decimals. Tiny values (<1) use 2 decimals when digits=1."""
    if n is None:
        return empty
    if digits == 1 and n and abs(n) < 1:
        return f"{n:.2f}%"
    return f"{n:.{digits}f}%"


def fmt_delta_pct(v: float) -> tuple[str, str]:
    """Return ('+1.2%', 'up'|'down') for 前期比 colouring — caller maps tone → CSS."""
    sign = "+" if v > 0 else ""
    tone = "up" if v >= 0 else "down"
    return f"{sign}{v:.1f}%", tone


def mmss_to_seconds(raw: Any) -> float | None:
    """Parse 'm:ss' / 'h:mm:ss' demo strings into seconds for charts."""
    if raw is None or raw in ("", "—", "–"):
        return None
    if isinstance(raw, (int, float)):
        return float(raw)
    parts = str(raw).strip().split(":")
    try:
        nums = [int(p) for p in parts]
    except ValueError:
        return None
    if len(nums) == 2:
        return float(nums[0] * 60 + nums[1])
    if len(nums) == 3:
        return float(nums[0] * 3600 + nums[1] * 60 + nums[2])
    return None
