"""GA4 connect page."""

from __future__ import annotations

from typing import Any

from sitekpi.ga4.oauth import base_url, redirect_uri
from sitekpi.i18n import normalize_locale, t
from sitekpi.i18n.pack_l10n import pack_text
from sitekpi.templating import render


def render_connect_page(
    *,
    configured: bool,
    connected: bool,
    demo: bool,
    email: str,
    properties: list[dict[str, str]],
    selected: dict[str, str] | None,
    preview: dict[str, Any] | None,
    error: str | None,
    libs_ok: bool,
    pack_groups: list[tuple[str, str, list[tuple[str, str, str]]]] | None = None,
    benchmark_pack: str = "",
    benchmark_pack_label: str = "",
    locale: str = "ja",
    rail: dict[str, Any] | None = None,
) -> str:
    loc = normalize_locale(locale)
    groups = []
    for cid, cat_label, items in pack_groups or []:
        shown_cat = t(f"cat.{cid}", loc) if cid != "all" else cat_label
        if shown_cat.startswith("cat."):
            shown_cat = cat_label
        groups.append(
            {
                "label": shown_cat,
                "packs": [
                    {
                        "slug": slug,
                        "label": pack_text(slug, "label", loc, label),
                        "hint": pack_text(slug, "hint", loc, hint) if hint else shown_cat,
                    }
                    for slug, label, hint in items
                ],
            }
        )
    return render(
        "connect.html",
        loc=loc,
        rail=rail,
        configured=configured,
        oauth_ready=configured and libs_ok,
        connected=connected,
        demo=demo,
        email=email,
        properties=properties,
        selected=selected,
        preview=preview,
        error=error,
        pack_groups=groups,
        benchmark_pack=benchmark_pack,
        benchmark_pack_label=benchmark_pack_label,
        redirect_uri=redirect_uri(),
        base_url=base_url(),
    )
