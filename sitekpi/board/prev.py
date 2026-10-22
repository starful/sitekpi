"""Previous period for sample boards (DEMO has only the current period).

Deterministic per pack/period so the 見本 always shows the same 前期比, and
consistent with the DEMO's own uu_delta / sessions_delta.
"""

from __future__ import annotations

from typing import Any


def _seed(text: str) -> int:
    h = 2166136261
    for ch in text:
        h = ((h ^ ord(ch)) * 16777619) & 0xFFFFFFFF
    return h


def _jitter(key: str, lo: float, hi: float) -> float:
    return lo + (hi - lo) * ((_seed(key) % 1000) / 999)


def sample_prev(slug: str, period: str, data: dict[str, Any]) -> dict[str, Any]:
    tag = f"{slug}|{period}|"
    prev = dict(data)
    uu = int(data.get("uu") or 0)
    sessions = int(data.get("sessions") or 0)
    prev["uu"] = round(uu / (1 + float(data.get("uu_delta") or 0) / 100))
    prev["sessions"] = round(sessions / (1 + float(data.get("sessions_delta") or 0) / 100))
    growth = prev["uu"] / uu if uu else 1.0
    for key in ("new_users", "returning_users", "pageviews"):
        prev[key] = round(int(data.get(key) or 0) * growth * _jitter(tag + key, 0.95, 1.05))
    prev["engaged_rate"] = round(float(data.get("engaged_rate") or 0) + _jitter(tag + "eng", -2.5, 2.0), 1)
    prev["pages_session"] = round(float(data.get("pages_session") or 0) * _jitter(tag + "pps", 0.94, 1.05), 2)
    sec = _mmss(data.get("avg_time"))
    if sec is not None:
        p = int(sec * _jitter(tag + "time", 0.9, 1.08))
        prev["avg_time"] = f"{p // 60}:{p % 60:02d}"
    counts = {k: max(0, round(int(v) * growth * _jitter(tag + "ev:" + k, 0.85, 1.12)))
              for k, v in (data.get("event_counts") or {}).items()}
    prev["event_counts"] = counts
    for key in ("signups", "pay_start", "pay_success"):
        prev[key] = max(0, round(int(data.get(key) or 0) * growth * _jitter(tag + key, 0.85, 1.12)))
    prev["signup_rate"] = round(100 * prev["signups"] / prev["uu"], 2) if prev["uu"] else 0.0
    prev["pay_cvr"] = round(100 * prev["pay_success"] / prev["pay_start"], 1) if prev["pay_start"] else 0.0
    return prev


def _mmss(raw: Any) -> int | None:
    try:
        parts = [int(x) for x in str(raw).split(":")]
    except ValueError:
        return None
    if len(parts) == 2:
        return parts[0] * 60 + parts[1]
    if len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    return None
