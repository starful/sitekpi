"""はじめての5分 — judgment scene for beginners (sample numbers only)."""

from __future__ import annotations

from typing import Any

from sitekpi.i18n import normalize_locale, t
from sitekpi.templating import render


def render_beginner(*, locale: str, rail: dict[str, Any]) -> str:
    loc = normalize_locale(locale)
    metrics = [
        {
            "name": t("beginner.m1_name", loc),
            "value": t("beginner.m1_value", loc),
            "line": t("beginner.m1_line", loc),
            "tone": "down",
        },
        {
            "name": t("beginner.m2_name", loc),
            "value": t("beginner.m2_value", loc),
            "line": t("beginner.m2_line", loc),
            "tone": "down",
        },
        {
            "name": t("beginner.m3_name", loc),
            "value": t("beginner.m3_value", loc),
            "line": t("beginner.m3_line", loc),
            "tone": "up",
        },
    ]
    return render(
        "beginner.html",
        loc=loc,
        rail=rail,
        metrics=metrics,
        title=t("beginner.title", loc),
        lead=t("beginner.lead", loc),
        meta=t("beginner.meta", loc),
        tip=t("beginner.tip", loc),
        cta=t("beginner.cta", loc),
        more=t("beginner.more", loc),
        note=t("beginner.note", loc),
        badge=t("sample_tag", loc),
    )
