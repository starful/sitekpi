"""Board pages — home, sample packs (/{slug}), connected /live, builder, settings.

/live assembly lives in routes.live_board.build_live_kwargs so this file stays route glue.
"""

from __future__ import annotations

import copy
from typing import Any, Literal

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from sitekpi.benchmarks import load_effective
from sitekpi.board.prev import sample_prev
from sitekpi.cache import TTLCache
from sitekpi.ga4.data import (
    build_live_builder_widgets,
    connection_info,
    discover_event_names,
    fetch_pack_overlay,
    saved_events,
)
from sitekpi.i18n import get_locale, set_locale
from sitekpi.routes.flow import sample_flow_context
from sitekpi.routes.live_board import build_live_kwargs
from sitekpi.routes.nav import nav_context, nav_rail_context
from sitekpi.metrics.help import PERIODS
from sitekpi.packs import BENCHMARKS, DEMO, INDUSTRIES
from sitekpi.views.benchmarks import bench_context
from sitekpi.views.board import render_sample_dense
from sitekpi.views.builder import render_builder
from sitekpi.views.settings import render_settings_page

router = APIRouter(tags=["pages"])

Period = Literal["7d", "28d"]


@router.get("/", response_class=HTMLResponse)
def index(request: Request, lang: str = Query(default=""), home: int = 0):
    """Connected → the board (unless ?home=1 from the menu). Otherwise the public landing page.
    ?lang=ja|en|ko is remembered in the session, so the board after connecting keeps the language."""
    from sitekpi.i18n import set_locale
    from sitekpi.views.landing import render_landing

    connected = bool(nav_context(request)["connected"])
    if lang:
        set_locale(request.session, lang)
    if connected and not home:
        return RedirectResponse("/live", status_code=302)
    return HTMLResponse(render_landing(locale=get_locale(request.session), connected=connected))


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


@router.get("/help", response_class=HTMLResponse)
def page_help(request: Request, lang: str = Query(default="")):
    """使い方・ヘルプ: connecting (the unverified-app screen), reading the board, verdict words, tasks."""
    from sitekpi.i18n import set_locale
    from sitekpi.i18n.guide_l10n import GUIDE
    from sitekpi.templating import render
    from sitekpi.views.seo import seo_context

    if lang:
        set_locale(request.session, lang)
    loc = get_locale(request.session)
    g = GUIDE[loc]
    return HTMLResponse(render(
        "help.html", loc=loc, g=g, rail=nav_rail_context(request, "help"),
        seo=seo_context(path="/help", loc=loc, title=f"{g['title']} | SiteKPI", description=g["meta_desc"]),
    ))


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
    """/live and /live/details — kwargs from live_board; HTML from render_sample_dense."""
    result = build_live_kwargs(request, period, fragment=fragment, live_pack=_live_pack)
    if isinstance(result, RedirectResponse):
        return result
    return HTMLResponse(render_sample_dense(**result))


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
    from sitekpi.routes.setup import sample_setup

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
            editor=(try_ := sample_setup(request, slug, data) or {}).get("editor"),
            industry_drawer=try_.get("industry"),
            ind_name=try_.get("ind_name", ""),
        )
    )
