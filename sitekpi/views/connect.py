"""GA4 connect page: Google → property → 訪問者の行動 (flow, editable) + 業種 (standards)."""

from __future__ import annotations

from typing import Any

from sitekpi.ga4.oauth import base_url, redirect_uri
from sitekpi.i18n import normalize_locale
from sitekpi.i18n.pack_l10n import pack_text
from sitekpi.packs.flows import FLOW_STEPS, step_label
from sitekpi.templating import render


def _behaviors(loc: str, sel: dict[str, str], site_events: set[str] | None,
               flows: dict[str, list[dict[str, str]]]) -> list[dict[str, Any]]:
    from sitekpi.packs import INDUSTRIES
    from sitekpi.packs.behaviors import BEHAVIORS, behavior_hint, behavior_label, slug_of

    out = []
    for cat in BEHAVIORS:
        pack = slug_of(cat)
        steps = flows.get(cat) or [
            {"key": s, "event": s, "label": step_label(s, loc, pack)} for s in FLOW_STEPS.get(pack) or []
        ]
        shown = [
            {**s, "label": s.get("label") or (step_label(s["key"], loc, pack) if s["key"] in FLOW_STEPS[pack] else s["event"]),
             "found": None if site_events is None else s["event"] in site_events}
            for s in steps
        ]
        hits = sum(1 for s in shown if s["found"])
        out.append({
            "cat": cat, "pack": pack, "label": behavior_label(cat, loc), "hint": behavior_hint(cat, loc),
            "steps": shown, "hits": hits, "custom": cat in flows, "selected": sel.get("behavior") == cat,
            "industries": [m for m in INDUSTRIES[pack]["members"]],
            "std": [{"key": k, "event": k, "label": step_label(k, loc, pack)} for k in FLOW_STEPS.get(pack) or []],
        })
    best = max((b["hits"] for b in out), default=0)
    for b in out:
        b["recommended"] = best > 0 and b["hits"] == best
    return out


def _industries(loc: str, sel: dict[str, str]) -> list[dict[str, Any]]:
    from sitekpi.packs import BENCHMARKS, packs_by_category
    from sitekpi.packs.behaviors import BEHAVIORS, behavior_label

    groups = []
    for cid, _label, items in packs_by_category():
        groups.append({
            "cat": cid,
            "label": behavior_label(cid, loc) if cid in BEHAVIORS else cid,
            "packs": [
                {"slug": s, "label": pack_text(s, "label", loc, lab),
                 "cited": sum(1 for spec in BENCHMARKS[s].values() if (spec.get("source") or {}).get("url")),
                 "selected": sel.get("industry") == s}
                for s, lab, _hint in items
            ],
        })
    return groups


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
    sel: dict[str, str] | None = None,
    sel_label: str = "",
    flows: dict[str, list[dict[str, str]]] | None = None,
    event_options: list[dict[str, Any]] | None = None,
    can_edit_flow: bool = False,
    locale: str = "ja",
    rail: dict[str, Any] | None = None,
    site_events: set[str] | None = None,
    max_steps: int = 6,
) -> str:
    loc = normalize_locale(locale)
    sel = sel or {"behavior": "", "industry": ""}
    picking = connected and bool(selected)
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
        sel=sel,
        sel_label=sel_label,
        ready=bool(sel.get("behavior") and sel.get("industry")),
        behaviors=_behaviors(loc, sel, site_events, flows or {}) if picking else [],
        industry_groups=_industries(loc, sel) if picking else [],
        event_options=event_options or [],
        can_edit_flow=can_edit_flow,
        knows_events=site_events is not None,
        max_steps=max_steps,
        redirect_uri=redirect_uri(),
        base_url=base_url(),
    )
