"""Board pages — home, sample packs (/{slug}), connected /live, builder, settings."""

from __future__ import annotations

import copy
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Literal

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from sitekpi.benchmarks import load_effective
from sitekpi.board.prev import sample_prev
from sitekpi.cache import TTLCache
from sitekpi.flow import apply_mapping, board_mapping, load_custom_flow, load_mapping
from sitekpi.ga4.data import (
    build_live_builder_widgets,
    connection_info,
    discover_event_names,
    fetch_pack_overlay,
    saved_events,
)
from sitekpi.packs.behaviors import behavior_label
from sitekpi.i18n import get_locale, set_locale, t
from sitekpi.routes.flow import live_flow_context, sample_flow_context
from sitekpi.selection import (
    auto_notice,
    compose_benchmarks,
    ensure_selection,
    flow_pack,
    is_ready,
    selection,
    selection_label,
)
from sitekpi.routes.nav import nav_context, nav_rail_context
from sitekpi.i18n.pack_l10n import pack_text
from sitekpi.metrics.help import PERIODS
from sitekpi.packs import BENCHMARKS, DEMO, INDUSTRIES
from sitekpi.views.benchmarks import bench_context
from sitekpi.views.board import render_sample_dense
from sitekpi.views.builder import render_builder
from sitekpi.views.home import render_home
from sitekpi.views.settings import render_settings_page

router = APIRouter(tags=["pages"])

Period = Literal["7d", "28d"]


@router.get("/", response_class=HTMLResponse)
def index(request: Request, lang: str = Query(default="")):
    """Connected → the board. Otherwise the public landing page (?lang=ja|en|ko for SEO links)."""
    from sitekpi.i18n import normalize_locale
    from sitekpi.views.landing import render_landing

    if nav_context(request)["connected"]:
        return RedirectResponse("/live", status_code=302)
    loc = normalize_locale(lang) if lang else get_locale(request.session)
    return HTMLResponse(render_landing(locale=loc))


# Short-lived per-process cache so switching periods does not re-hit GA4 every
# click. Keyed by property (access is checked when the property is selected),
# bounded, and locked because sync routes run in a thread pool.
_LIVE_PACK_CACHE = TTLCache(maxsize=256, ttl=300.0)  # GA4 data moves daily; 5 min is plenty


def _live_pack(
    request: Request, industry: str, period: Period, mapping: dict[str, str] | None = None
) -> tuple[dict[str, Any], bool, str | None, str]:
    """GA4 overlay for the connected board. ``mapping`` adds the site's own event
    names for 行動フロー steps so they are fetched even with a saved event list."""
    mapping = mapping or {}
    base = dict(DEMO[industry][period])
    pack_events = list(INDUSTRIES[industry].get("events") or [])
    primary = str(INDUSTRIES[industry].get("primary_event") or (pack_events[0] if pack_events else ""))

    # Sample-pack browsing: skip GA4 entirely when not connected (keeps nav snappy)
    info = connection_info(request.session)
    if not info:
        return base, False, None, ""

    saved = saved_events(request.session)
    cache_key = (
        f"{info['property_id']}|{period}|{industry}|"
        f"{','.join(saved['events']) if saved else 'discover'}|"
        f"{saved.get('primary') if saved else primary}|"
        f"{','.join(f'{k}={v}' for k, v in sorted(mapping.items()))}"
    )
    hit = _LIVE_PACK_CACHE.get(cache_key)
    if hit:
        cached_overlay, prop = hit
        merged = dict(base)
        merged.update(copy.deepcopy(cached_overlay))  # callers may mutate nested rows
        return merged, True, None, prop

    if saved:
        events = list(saved["events"])
        primary = str(saved.get("primary") or primary)
    else:
        discovered, _ = discover_event_names(request.session, period=period, limit=200)
        if discovered:
            events = [e["name"] for e in discovered]
            if primary not in events:
                primary = events[0] if events else primary
        else:
            events = pack_events
    events = events + [e for e in mapping.values() if e not in events]
    overlay, err = fetch_pack_overlay(
        request.session,
        period=period,
        event_names=events,
        primary_event=primary,
    )
    if not overlay:
        return base, False, err, ""
    prop = str(overlay.pop("_ga4_property", "") or "")
    overlay.pop("_ga4_label", None)
    overlay.pop("_ga4_property_id", None)
    # Live: replace event_counts with GA4 (don't keep fake pack events)
    stash = dict(overlay)
    stash["_live_events"] = events
    stash["_live_primary"] = primary
    _LIVE_PACK_CACHE.set(cache_key, (stash, prop))
    base.update(stash)
    return base, True, None, prop


_BUILDER_CACHE = TTLCache(maxsize=64, ttl=300.0)


@router.get("/builder", response_class=HTMLResponse)
def page_builder(request: Request):
    """Shell first — GA4 values load via /builder/values (or cache hit)."""
    from sitekpi.metrics.help import palette_widgets

    loc = get_locale(request.session)
    info = connection_info(request.session)
    prop_name = str((info or {}).get("property_name") or "")
    widgets = None
    live_error = None
    live_fetch = False
    live_loading = False
    if info:
        cache_key = f"builder|help|{info.get('property_id')}|28d|{loc}"
        hit = _BUILDER_CACHE.get(cache_key)
        if hit is not None:
            widgets, live_error = hit
        else:
            # Instant HTML: HELP palette with — ; JS fills from /builder/values
            widgets = palette_widgets(sample=False, locale=loc)
            for w in widgets:
                if w.get("group") == "business":
                    w["value"] = "—"
            live_fetch = True
            live_loading = True
    else:
        from sitekpi.views.builder import fill_sample_values

        widgets = fill_sample_values(palette_widgets(sample=True, locale=loc))
    return HTMLResponse(
        render_builder(
            property_name=prop_name,
            live_error=live_error,
            live_loading=live_loading,
            live_fetch=live_fetch,
            widgets=widgets or None,
            locale=loc,
            rail=nav_rail_context(request, "builder"),
        )
    )


@router.get("/builder/values")
def page_builder_values(request: Request):
    """JSON: HELP-palette values from GA4 (cached). Used after fast /builder shell."""
    from fastapi.responses import JSONResponse

    widgets, prop_name, live_error = build_live_builder_widgets(
        request.session,
        period="28d",
        cache=_BUILDER_CACHE,
        locale=get_locale(request.session),
    )
    if not prop_name and not widgets:
        return JSONResponse({"ok": False, "widgets": [], "error": None})
    slim = [
        {
            "id": w["id"],
            "value": w.get("value") or "—",
            "hint": w.get("hint") or "",
        }
        for w in widgets
    ]
    return JSONResponse(
        {"ok": not live_error, "property_name": prop_name, "widgets": slim, "error": live_error}
    )


@router.get("/glossary", response_class=HTMLResponse)
def page_glossary(request: Request):
    from sitekpi.views.glossary import render_glossary

    return HTMLResponse(
        render_glossary(
            locale=get_locale(request.session),
            rail=nav_rail_context(request, "glossary"),
        )
    )


@router.get("/sample", response_class=HTMLResponse)
def page_sample_dense():
    # Dense board template — default vertical is 人事
    return RedirectResponse("/hr", status_code=302)


@router.get("/settings", response_class=HTMLResponse)
def page_settings_get(request: Request, saved: int = Query(default=0)):
    extras = nav_context(request)
    loc = get_locale(request.session)
    return HTMLResponse(
        render_settings_page(
            locale=loc,
            saved=bool(saved),
            pack_links=extras["pack_links"],
            pack_groups=extras["pack_groups"],
            connected=extras["connected"],
            back_href="/live" if extras["connected"] else "/",
        )
    )


@router.post("/settings")
async def page_settings_post(request: Request):
    form = await request.form()
    set_locale(request.session, str(form.get("locale") or ""))
    return RedirectResponse("/settings?saved=1", status_code=303)


@router.get("/live", response_class=HTMLResponse)
def page_live(request: Request, period: str = Query(default="28d")):
    """Connected GA4 board (separate menu category from sample packs)."""
    return _live(request, period)


@router.get("/live/details", response_class=HTMLResponse)
def page_live_details(request: Request, period: str = Query(default="28d")):
    """詳しい数字 only — board.js loads it after the page (the extra GA4 reports are the slow part)."""
    return _live(request, period, fragment=True)


def _live(request: Request, period: str, *, fragment: bool = False):
    if period not in PERIODS:
        period = "28d"
    extras = nav_context(request)
    if not extras["connected"]:
        return RedirectResponse("/connect", status_code=302)
    # 訪問者の行動 → flow / events / wording;  業種 → 業界目安
    sel = selection(request.session)
    if not is_ready(sel):
        # Numbers first: never send a connected user to a setup wizard before the board.
        # Guess the behaviour from the site's own events; the board says it is a guess.
        from sitekpi.routes.setup import site_event_counts

        is_demo_conn = bool(request.session.get("ga4_demo"))
        counts = None if is_demo_conn else (site_event_counts(request) or {})
        prop_name = str((request.session.get("ga4_property") or {}).get("name") or "")
        sel = ensure_selection(request.session, counts, prop_name)
        extras = nav_context(request)  # the rail shows the new 行動 × 業種
    pack_slug = flow_pack(sel)
    industry = sel["industry"]
    loc = get_locale(request.session)
    primary_ev = str(INDUSTRIES[pack_slug].get("primary_event") or "")
    mapping = board_mapping(pack_slug, load_mapping(request.session, pack_slug),
                            load_custom_flow(request.session, pack_slug), primary_ev)
    # Board numbers and the 行動フロー are independent GA4 calls → fetch them side by side
    with ThreadPoolExecutor(max_workers=2) as pool:
        flow_job = pool.submit(live_flow_context, request, pack_slug, period, mapping, loc)
        data, live, err, prop = _live_pack(request, pack_slug, period, mapping)  # type: ignore[arg-type]
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
        ev_names = list(INDUSTRIES[pack_slug].get("events") or []) + list((data.get("event_counts") or {}).keys())
        extras_x, _x_err = live_extras(request.session, period=period, events=list(dict.fromkeys(ev_names)),
                                       primary=primary_ev)
    else:
        extras_x = sample_extras(pack_slug, data, prev)
    stages = (flow or {}).get("stages") or []
    flow_users = {str(st["event"]): int(st["users"]) for st in stages[1:] if st.get("event") and st.get("users")}
    setup_ctx = None if fragment else board_setup(
        request, flow_users=flow_users, flow_entry=int(stages[0]["users"]) if stages else 0)
    if is_demo:
        # Demo connect: pack sample site numbers, clearly labelled (business stays —)
        note = t("live.note.demo_mode", loc, pack=pack_label)
    elif live:
        note = t("live.note.ok", loc, pack=pack_label)
    elif err:
        note = t("live.note.err", loc, pack=pack_label)
    else:
        note = t("live.note.demo", loc, pack=pack_label)
    return HTMLResponse(
        render_sample_dense(
            industry=pack_slug,
            period=period,
            data=data,
            ind=INDUSTRIES[pack_slug],
            benches_raw=(effective := load_effective(
                request.session, industry, compose_benchmarks(sel["behavior"], industry), live=True)),
            bench=bench_context(
                pack=industry, board="live" if not is_demo else "sample", effective=effective, locale=loc,
                labels_from=pack_slug,
                property_name=str((request.session.get("ga4_property") or {}).get("name") or ""),
            ),
            property_name=prop or label,
            industry_label=label,
            industry_note=note,
            pack_links=extras["pack_links"],
            pack_groups=extras["pack_groups"],
            nav_active="live",
            connected=extras["connected"],
            locale=loc,
            board_kind="live",
            flow=flow,
            prev=prev,
            notice=None if fragment else auto_notice(request.session, loc),
            extras=extras_x,
            details_src=details_src,
            fragment=fragment,
            editor=(setup_ctx or {}).get("editor"),
            industry_drawer=(setup_ctx or {}).get("industry"),
            ind_name=(setup_ctx or {}).get("ind_name", ""),
            meta_short=" · ".join(x for x in (t("connect.badge.demo", loc) if is_demo else "",
                                                behavior_label(sel["behavior"], loc)) if x),
            auto_open=("edit" if request.query_params.get("edit") else
                       "industry" if request.query_params.get("industry") else (setup_ctx or {}).get("open", "")),
        )
    )


def _with_sessions(flow: dict[str, Any] | None, data: dict[str, Any]) -> dict[str, Any] | None:
    if flow:
        flow["sessions"] = f"{int(data.get('sessions') or 0):,}"
    return flow


@router.get("/beginner", response_class=HTMLResponse)
def page_beginner(request: Request):
    """Sample judgment scene — kept for direct links; not a rail menu item.
    After connecting, the board's いまの状態 is the first scene (/live)."""
    from sitekpi.views.beginner import render_beginner

    return HTMLResponse(
        render_beginner(
            locale=get_locale(request.session),
            rail=nav_rail_context(request, "beginner"),
        )
    )


@router.get("/first")
def page_first():
    """Old 「はじめての5分」 URL: the board's いまの状態 is the first scene now."""
    return RedirectResponse("/live", status_code=302)


@router.get("/samples", response_class=HTMLResponse)
def page_samples(request: Request, b: str | None = None, i: str | None = None):
    """見本ボード: goal list + a preview of that board (?b=behaviour&i=industry)."""
    from sitekpi.views.samples import render_samples

    return HTMLResponse(render_samples(locale=get_locale(request.session),
                                       rail=nav_rail_context(request, "samples"), cat=b, ind=i))


@router.get("/samples/preview", response_class=HTMLResponse)
def page_samples_preview(request: Request, b: str | None = None, i: str | None = None):
    """Just the preview pane — swapped in by samples.js when a goal or industry is picked."""
    from sitekpi.views.samples import render_samples

    return HTMLResponse(render_samples(locale=get_locale(request.session), rail={}, cat=b, ind=i,
                                       fragment=True))


@router.get("/b2c_membership")
def legacy_b2c():
    return RedirectResponse("/b2c", status_code=302)


@router.get("/content_media")
def legacy_content():
    return RedirectResponse("/content", status_code=302)


@router.get("/{slug}", response_class=HTMLResponse)
def page_industry(request: Request, slug: str, period: str = Query(default="28d")):
    """Dense board for industry sample packs (DEMO only — live is /live)."""
    from sitekpi.board.extras import sample_extras

    if slug not in INDUSTRIES:
        return HTMLResponse("<h1>Not Found</h1>", status_code=404)
    if period not in PERIODS:
        period = "28d"
    extras = nav_context(request)
    data = dict(DEMO[slug][period])
    return HTMLResponse(
        render_sample_dense(
            industry=slug,
            period=period,
            data=data,
            ind=INDUSTRIES[slug],
            benches_raw=(effective := load_effective(request.session, slug, BENCHMARKS[slug], live=False)),
            bench=bench_context(
                pack=slug, board="sample", effective=effective, locale=get_locale(request.session),
            ),
            property_name="",
            pack_links=extras["pack_links"],
            pack_groups=extras["pack_groups"],
            nav_active=f"pack:{slug}",
            connected=extras["connected"],
            locale=get_locale(request.session),
            flow=_with_sessions(sample_flow_context(slug, data, get_locale(request.session)), data),
            prev=(prev := sample_prev(slug, period, data)),
            extras=sample_extras(slug, data, prev),
        )
    )
