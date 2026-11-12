"""Assemble kwargs for the connected /live board (GA4 numbers × selection × 業界目安).

Kept under routes/ (not views/) because it needs live_flow_context and board_setup.
pages._live stays thin: call build_live_kwargs → render_sample_dense (or redirect).
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from collections.abc import Callable
from typing import Any

from fastapi import Request
from fastapi.responses import RedirectResponse

from sitekpi.benchmarks import load_effective
from sitekpi.board.prev import sample_prev
from sitekpi.flow import apply_mapping, board_mapping, load_custom_flow, load_mapping
from sitekpi.i18n import get_locale, t
from sitekpi.metrics.help import PERIODS
from sitekpi.packs import INDUSTRIES
from sitekpi.packs.behaviors import behavior_label
from sitekpi.routes.flow import live_flow_context, sample_flow_context
from sitekpi.routes.nav import nav_context
from sitekpi.selection import (
    auto_notice,
    compose_benchmarks,
    ensure_selection,
    flow_pack,
    is_ready,
    selection,
    selection_label,
)
from sitekpi.views.benchmarks import bench_context

# pages._live_pack signature — passed in so this module does not import pages.
LivePackFn = Callable[
    [Request, str, str, dict[str, str] | None],
    tuple[dict[str, Any], bool, str | None, str],
]


def build_live_kwargs(
    request: Request,
    period: str,
    *,
    fragment: bool = False,
    live_pack: LivePackFn,
) -> RedirectResponse | dict[str, Any]:
    """Return a redirect to /connect, or kwargs for render_sample_dense.

    Numbers first: if behaviour×industry is unset, ensure_selection guesses from
    GA4 events and the board shows a 仮 notice — never a wizard before numbers.
    """
    if period not in PERIODS:
        period = "28d"
    extras = nav_context(request)
    if not extras["connected"]:
        return RedirectResponse("/connect", status_code=302)

    # 訪問者の行動 → flow / events / wording; 業種 → 業界目安 only
    sel = selection(request.session)
    if not is_ready(sel):
        # Numbers first: never send a connected user to a setup wizard before the board.
        from sitekpi.routes.setup import site_event_counts

        is_demo_conn = bool(request.session.get("ga4_demo"))
        counts = None if is_demo_conn else (site_event_counts(request) or {})
        prop_name = str((request.session.get("ga4_property") or {}).get("name") or "")
        sel = ensure_selection(request.session, counts, prop_name)
        extras = nav_context(request)

    pack_slug = flow_pack(sel)
    industry = sel["industry"]
    loc = get_locale(request.session)
    primary_ev = str(INDUSTRIES[pack_slug].get("primary_event") or "")
    mapping = board_mapping(
        pack_slug,
        load_mapping(request.session, pack_slug),
        load_custom_flow(request.session, pack_slug),
        primary_ev,
    )

    # Board numbers and the 行動フロー are independent GA4 calls → fetch side by side
    with ThreadPoolExecutor(max_workers=2) as pool:
        flow_job = pool.submit(live_flow_context, request, pack_slug, period, mapping, loc)
        data, live, err, prop = live_pack(request, pack_slug, period, mapping)
        live_flow = flow_job.result()

    prev = data.pop("_prev", None) if live else sample_prev(pack_slug, period, data)
    if live and mapping:
        data = apply_mapping(data, pack_slug, mapping, primary=primary_ev)
        if prev:
            prev = apply_mapping(prev, pack_slug, mapping, primary=primary_ev)
    flow = live_flow if live else sample_flow_context(pack_slug, data, loc)

    label = extras["connected"]["name"]
    pack_label = selection_label(sel, loc)
    is_demo = bool(extras["connected"].get("demo"))
    if flow:
        flow["sessions"] = f"{int(data.get('sessions') or 0):,}"
        flow["demo"] = is_demo

    from sitekpi.board.extras import live_extras, sample_extras
    from sitekpi.routes.setup import board_setup

    details_src, extras_x = "", None
    if live and not fragment:
        details_src = f"/live/details?period={period}"
    elif live:
        ev_names = list(INDUSTRIES[pack_slug].get("events") or []) + list(
            (data.get("event_counts") or {}).keys()
        )
        extras_x, _x_err = live_extras(
            request.session,
            period=period,
            events=list(dict.fromkeys(ev_names)),
            primary=primary_ev,
        )
    else:
        extras_x = sample_extras(pack_slug, data, prev)

    stages = (flow or {}).get("stages") or []
    flow_users = {
        str(st["event"]): int(st["users"])
        for st in stages[1:]
        if st.get("event") and st.get("users")
    }
    setup_ctx = None if fragment else board_setup(
        request,
        flow_users=flow_users,
        flow_entry=int(stages[0]["users"]) if stages else 0,
    )

    if is_demo:
        note = t("live.note.demo_mode", loc, pack=pack_label)
    elif live:
        note = t("live.note.ok", loc, pack=pack_label)
    elif err:
        note = t("live.note.err", loc, pack=pack_label)
    else:
        note = t("live.note.demo", loc, pack=pack_label)

    effective = load_effective(
        request.session, industry, compose_benchmarks(sel["behavior"], industry), live=True
    )
    return {
        "industry": pack_slug,
        "period": period,
        "data": data,
        "ind": INDUSTRIES[pack_slug],
        "benches_raw": effective,
        "bench": bench_context(
            pack=industry,
            board="live" if not is_demo else "sample",
            effective=effective,
            locale=loc,
            labels_from=pack_slug,
            property_name=str((request.session.get("ga4_property") or {}).get("name") or ""),
        ),
        "property_name": prop or label,
        "industry_label": label,
        "industry_note": note,
        "pack_links": extras["pack_links"],
        "pack_groups": extras["pack_groups"],
        "nav_active": "live",
        "connected": extras["connected"],
        "locale": loc,
        "board_kind": "live",
        "flow": flow,
        "prev": prev,
        "notice": None if fragment else auto_notice(request.session, loc),
        "extras": extras_x,
        "details_src": details_src,
        "fragment": fragment,
        "editor": (setup_ctx or {}).get("editor"),
        "industry_drawer": (setup_ctx or {}).get("industry"),
        "ind_name": (setup_ctx or {}).get("ind_name", ""),
        "meta_short": " · ".join(
            x
            for x in (
                t("connect.badge.demo", loc) if is_demo else "",
                behavior_label(sel["behavior"], loc),
            )
            if x
        ),
        "auto_open": (
            "edit"
            if request.query_params.get("edit")
            else "industry"
            if request.query_params.get("industry")
            else (setup_ctx or {}).get("open", "")
        ),
    }
