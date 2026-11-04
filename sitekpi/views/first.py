"""接続直後の「はじめての5分」— numbers first, then continue to flow setup.

Metric names / tips come from HELP (uu, sessions, engaged) — same as 指標辞典.
"""

from __future__ import annotations

from typing import Any

from sitekpi.i18n import normalize_locale, t
from sitekpi.metrics.help import get_help
from sitekpi.templating import render

_FIRST_IDS = ("uu", "sessions", "engaged")


def _line(help_id: str, locale: str) -> str:
    h = get_help(help_id, locale) or {}
    meaning = str(h.get("meaning") or "")
    return meaning.split("\n", 1)[0]


def render_first(
    *,
    locale: str,
    rail: dict[str, Any],
    property_name: str,
    basics: dict[str, float] | None,
    is_demo: bool,
) -> str:
    loc = normalize_locale(locale)
    names = {
        k: str((get_help(k, loc) or {}).get("title") or k) for k in _FIRST_IDS
    }
    lines = {k: _line(k, loc) for k in _FIRST_IDS}

    if basics and basics.get("uu") is not None:
        uu = int(basics.get("uu") or 0)
        eng = basics.get("engaged_rate")
        sessions = int(basics.get("sessions") or 0)
        metrics = [
            {
                "id": "uu",
                "name": names["uu"],
                "value": f"{uu:,}",
                "line": lines["uu"],
                "tone": "ok",
            },
            {
                "id": "sessions",
                "name": names["sessions"],
                "value": f"{sessions:,}",
                "line": lines["sessions"],
                "tone": "ok",
            },
            {
                "id": "engaged",
                "name": names["engaged"],
                "value": (f"{eng:.1f}%" if eng is not None else "—"),
                "line": lines["engaged"],
                "tone": "up" if eng is not None and eng >= 50 else "down",
            },
        ]
        meta = t("first.meta_live", loc, name=property_name)
        badge = t("first.badge_live", loc)
        tip = t("first.tip_live", loc)
        note = t("first.note_live", loc)
    else:
        metrics = [
            {
                "id": "uu",
                "name": names["uu"],
                "value": "12,400",
                "line": lines["uu"],
                "tone": "down",
            },
            {
                "id": "sessions",
                "name": names["sessions"],
                "value": "18,200",
                "line": lines["sessions"],
                "tone": "down",
            },
            {
                "id": "engaged",
                "name": names["engaged"],
                "value": "58.0%",
                "line": lines["engaged"],
                "tone": "up",
            },
        ]
        meta = t("first.meta_sample", loc, name=property_name)
        badge = t("sample_tag", loc)
        tip = t("first.tip_sample", loc)
        note = t("first.note_sample", loc)
        if is_demo:
            tip = t("first.tip_demo", loc)

    return render(
        "first.html",
        loc=loc,
        rail=rail,
        metrics=metrics,
        title=t("first.title", loc),
        lead=t("first.lead", loc),
        meta=meta,
        tip=tip,
        cta=t("first.cta", loc),
        skip=t("first.skip", loc),
        note=note,
        badge=badge,
    )
