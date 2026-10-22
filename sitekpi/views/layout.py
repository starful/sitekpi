"""Shared app chrome data: the left rail (サンプルパック / 接続済み / アプリ).

Markup: templates/partials/rail.html, rail_nav.html, mobile_bar.html
Styles: static/css/rail.css   Behaviour: static/js/rail.js
"""

from __future__ import annotations

from typing import Any

from sitekpi.i18n import t
from sitekpi.i18n.pack_l10n import pack_text


def rail_context(
    *,
    nav_active: str,
    locale: str,
    connected: dict[str, str] | None = None,
    pack_groups: Any = None,
    pack_links: Any = None,
    industry: str = "",
) -> dict[str, Any]:
    """Data for templates/partials/rail*.html."""
    if pack_groups is None:
        from sitekpi.packs import packs_by_category

        pack_groups = packs_by_category()
    elif not pack_groups and pack_links:
        items_: list[tuple[str, str, str]] = []
        for item in pack_links:
            items_.append((item[0], item[1], item[2] if len(item) >= 3 else ""))
        pack_groups = [("all", t("cat.all", locale), items_)]
    active_slug = nav_active.removeprefix("pack:") if nav_active.startswith("pack:") else ""
    groups: list[dict[str, Any]] = []
    for cid, cat_label, items in pack_groups:
        shown = t(f"cat.{cid}", locale) if cid != "all" else cat_label
        if shown.startswith("cat."):
            shown = cat_label
        rows = []
        for slug, label, hint in items:
            shown_label = pack_text(slug, "label", locale, label)
            shown_hint = pack_text(slug, "hint", locale, hint) if hint else ""
            rows.append(
                {
                    "slug": slug,
                    "label": shown_label,
                    "hint": shown_hint,
                    "q": f"{shown_label} {shown_hint} {slug}".strip().lower(),
                    "on": nav_active == f"pack:{slug}",
                }
            )
        groups.append(
            {
                "label": shown,
                "open": bool(active_slug) and any(s == active_slug for s, _, _ in items),
                "packs": rows,
            }
        )
    return {"groups": groups, "connected": connected, "active": nav_active}


def _rail_nav_html(
    *,
    industry: str = "",
    nav_active: str,
    locale: str,
    connected: dict[str, str] | None = None,
    pack_groups: Any = None,
    pack_links: Any = None,
) -> str:
    """Rendered rail nav (used by scripts/smoke_packs.py)."""
    from sitekpi.templating import render

    rail = rail_context(
        nav_active=nav_active, locale=locale, connected=connected,
        pack_groups=pack_groups, pack_links=pack_links, industry=industry,
    )
    return render("partials/rail_nav.html", rail=rail, loc=locale)
