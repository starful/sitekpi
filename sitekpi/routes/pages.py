"""Board pages — home, sample packs (/{slug}), connected /live, builder, settings."""

from __future__ import annotations

import copy
from typing import Any, Literal

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from sitekpi.benchmarks import load_effective
from sitekpi.cache import TTLCache
from sitekpi.flow import apply_mapping, load_mapping
from sitekpi.ga4.data import (
    build_live_builder_widgets,
    connection_info,
    discover_event_names,
    fetch_pack_overlay,
    saved_events,
)
from sitekpi.i18n import get_locale, set_locale, t
from sitekpi.routes.flow import live_flow_context, sample_flow_context
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
def index():
    return HTMLResponse(render_home())


# Short-lived per-process cache so switching periods does not re-hit GA4 every
# click. Keyed by property (access is checked when the property is selected),
# bounded, and locked because sync routes run in a thread pool.
_LIVE_PACK_CACHE = TTLCache(maxsize=256, ttl=60.0)


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


@router.get("/builder", response_class=HTMLResponse)
def page_builder(request: Request):
    widgets, prop_name, live_error = build_live_builder_widgets(
        request.session, period="28d"
    )
    return HTMLResponse(
        render_builder(
            property_name=prop_name,
            live_error=live_error,
            widgets=widgets or None,
            locale=get_locale(request.session),
            rail=nav_rail_context(request, "builder"),
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
            back_href="/hr",
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
    if period not in PERIODS:
        period = "28d"
    extras = nav_context(request)
    if not extras["connected"]:
        return RedirectResponse("/connect", status_code=302)
    # Industry pack = 業界目安 source only (not DEMO revenue as live)
    pack_slug = extras.get("benchmark_pack") or ""
    if not pack_slug or pack_slug not in INDUSTRIES:
        return RedirectResponse("/connect", status_code=302)
    mapping = load_mapping(request.session, pack_slug)
    data, live, err, prop = _live_pack(request, pack_slug, period, mapping)  # type: ignore[arg-type]
    loc = get_locale(request.session)
    if live and mapping:
        data = apply_mapping(data, pack_slug, mapping,
                             primary=str(INDUSTRIES[pack_slug].get("primary_event") or ""))
    flow = (live_flow_context(request, pack_slug, period, mapping, loc) if live
            else sample_flow_context(pack_slug, data, loc))
    label = extras["connected"]["name"]
    pack_label = pack_text(
        pack_slug, "label", loc, str(INDUSTRIES[pack_slug]["label"])
    )
    is_demo = bool(extras["connected"].get("demo"))
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
            benches_raw=(effective := load_effective(request.session, pack_slug, BENCHMARKS[pack_slug], live=True)),
            bench=bench_context(
                pack=pack_slug, board="live" if not is_demo else "sample", effective=effective, locale=loc,
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
        )
    )


@router.get("/b2c_membership")
def legacy_b2c():
    return RedirectResponse("/b2c", status_code=302)


@router.get("/content_media")
def legacy_content():
    return RedirectResponse("/content", status_code=302)


@router.get("/{slug}", response_class=HTMLResponse)
def page_industry(request: Request, slug: str, period: str = Query(default="28d")):
    """Dense board for industry sample packs (DEMO only — live is /live)."""
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
            flow=sample_flow_context(slug, data, get_locale(request.session)),
        )
    )
