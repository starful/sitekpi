"""GA4 connect page."""

from __future__ import annotations

from typing import Any

from sitekpi.ga4.oauth import base_url, redirect_uri
from sitekpi.i18n import normalize_locale, t
from sitekpi.i18n.pack_l10n import pack_text
from sitekpi.packs.flows import FLOW_STEPS, step_label
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
    site_events: set[str] | None = None,
) -> str:
    loc = normalize_locale(locale)

    def flow_of(slug: str) -> dict[str, Any]:
        """The pack's 行動フロー, and (when we know the site's events) which steps it records."""
        steps = [
            {"label": step_label(ev, loc, slug), "event": ev,
             "found": None if site_events is None else ev in site_events}
            for ev in FLOW_STEPS.get(slug) or []
        ]
        hits = sum(1 for s in steps if s["found"])
        return {"steps": steps, "hits": hits, "total": len(steps)}

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
                        "flow": flow_of(slug),
                    }
                    for slug, label, hint in items
                ],
            }
        )
    best = max((p["flow"]["hits"] for g in groups for p in g["packs"]), default=0)
    for g in groups:
        for p in g["packs"]:
            p["recommended"] = best > 0 and p["flow"]["hits"] == best
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
        knows_events=site_events is not None,
        redirect_uri=redirect_uri(),
        base_url=base_url(),
    )
