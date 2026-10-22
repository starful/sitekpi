"""Shared app chrome data: the left menu (マイサイト / ツール / 見本 / 設定).

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
    """Data for templates/partials/rail*.html (マイサイト / ツール / 見本 / 設定)."""
    sample = None
    if nav_active.startswith("pack:"):
        slug = nav_active.removeprefix("pack:")
        sample = {"slug": slug, "label": pack_text(slug, "label", locale, slug)}
    return {
        "connected": connected,
        "active": "samples" if sample else nav_active,
        "sample": sample,
        "selection_label": str((connected or {}).get("selection") or ""),
    }


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
