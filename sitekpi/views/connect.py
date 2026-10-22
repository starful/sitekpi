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

    # 行動 first (type-<category>), then the industry inside it (optional)
    from sitekpi.packs import BENCHMARKS, INDUSTRIES
    from sitekpi.packs.behaviors import BEHAVIORS, behavior_hint, behavior_label, slug_of

    groups: list[dict[str, Any]] = []
    for cat in BEHAVIORS if pack_groups is not None else []:
        vslug = slug_of(cat)
        members = INDUSTRIES[vslug]["members"]
        industries = [
            {"slug": m, "label": pack_text(m, "label", loc, str(INDUSTRIES[m]["label"])), "flow": flow_of(m),
             "cited": sum(1 for spec in BENCHMARKS[m].values()
                          if (spec.get("source") or {}).get("url"))}
            for m in members
        ]
        flow = flow_of(vslug)
        best_member = max((i["flow"]["hits"] for i in industries), default=0)
        groups.append({
            "cat": cat, "slug": vslug, "label": behavior_label(cat, loc), "hint": behavior_hint(cat, loc),
            "flow": flow, "hits": max(flow["hits"], best_member), "industries": industries,
            "selected": benchmark_pack == vslug or benchmark_pack in members,
            "industry_selected": benchmark_pack in members,
        })
    best = max((b["hits"] for b in groups), default=0)
    for b in groups:
        b["recommended"] = best > 0 and b["hits"] == best
        for i in b["industries"]:
            # an industry is the better pick when its own flow matches more than the behaviour's
            i["recommended"] = b["recommended"] and i["flow"]["hits"] == b["hits"] > b["flow"]["hits"]
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
        error=error,
        pack_groups=groups,
        benchmark_pack=benchmark_pack,
        benchmark_pack_label=benchmark_pack_label,
        knows_events=site_events is not None,
        redirect_uri=redirect_uri(),
        base_url=base_url(),
    )
