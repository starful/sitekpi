"""Board pages — home, sample packs (/{slug}), connected /live, builder, settings."""

from __future__ import annotations

import time
from typing import Any, Literal

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from sitekpi.ga4.data import (
    build_live_builder_widgets,
    connection_info,
    discover_event_names,
    fetch_pack_overlay,
    saved_events,
)
from sitekpi.i18n import get_locale, set_locale, t
from sitekpi.i18n.pack_l10n import pack_text
from sitekpi.metrics.help import PERIODS
from sitekpi.packs import BENCHMARKS, DEMO, INDUSTRIES, pack_links, packs_by_category
from sitekpi.views.board import render_sample_dense
from sitekpi.views.builder import render_builder
from sitekpi.views.home import render_home
from sitekpi.views.settings import render_settings_page

router = APIRouter(tags=["pages"])

Period = Literal["7d", "28d"]


@router.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(render_home())


# Short-lived cache so switching sample packs does not re-hit GA4 every click
_LIVE_PACK_CACHE: dict[str, tuple[float, dict[str, Any], str]] = {}
_LIVE_PACK_TTL_SEC = 60.0


def _live_pack(request: Request, industry: str, period: Period) -> tuple[dict[str, Any], bool, str | None, str]:
    """Optional GA4 overlay for packs (unused by dense sample routes; kept for tooling)."""
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
        f"{saved.get('primary') if saved else primary}"
    )
    now = time.time()
    hit = _LIVE_PACK_CACHE.get(cache_key)
    if hit and now - hit[0] < _LIVE_PACK_TTL_SEC:
        cached_overlay, prop = hit[1], hit[2]
        merged = dict(base)
        merged.update(cached_overlay)
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
    _LIVE_PACK_CACHE[cache_key] = (now, stash, prop)
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
        )
    )


def _nav_extras(request: Request) -> dict[str, Any]:
    session = request.session
    info = connection_info(session)
    prop = session.get("ga4_property")
    is_demo = bool(session.get("ga4_demo"))
    connected: dict[str, str] | None = None
    if isinstance(prop, dict) and prop.get("id") and (info or is_demo):
        name = str(prop.get("name") or f"Property {prop.get('id')}")
        if is_demo:
            name = t("nav.demo_name", get_locale(session), name=name)
        connected = {
            "id": str(prop.get("id") or ""),
            "name": name,
            "email": str((info or {}).get("email") or session.get("ga4_email") or ""),
            "demo": "1" if is_demo else "",
        }
    pack = request.session.get("benchmark_pack")
    benchmark_pack = str(pack) if isinstance(pack, str) and pack in INDUSTRIES else ""
    return {
        "connected": connected,
        "pack_links": pack_links(),
        "pack_groups": packs_by_category(),
        "benchmark_pack": benchmark_pack,
    }


@router.get("/sample", response_class=HTMLResponse)
def page_sample_dense():
    # Dense board template — default vertical is 人事
    return RedirectResponse("/hr", status_code=302)


@router.get("/settings", response_class=HTMLResponse)
def page_settings_get(request: Request, saved: int = Query(default=0)):
    extras = _nav_extras(request)
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
    extras = _nav_extras(request)
    if not extras["connected"]:
        return RedirectResponse("/connect", status_code=302)
    # Industry pack = 業界目安 source only (not DEMO revenue as live)
    pack_slug = extras.get("benchmark_pack") or ""
    if not pack_slug or pack_slug not in INDUSTRIES:
        return RedirectResponse("/connect", status_code=302)
    data, live, err, prop = _live_pack(request, pack_slug, period)  # type: ignore[arg-type]
    loc = get_locale(request.session)
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
            benches_raw=BENCHMARKS[pack_slug],
            property_name=prop or label,
            industry_label=label,
            industry_note=note,
            pack_links=extras["pack_links"],
            pack_groups=extras["pack_groups"],
            nav_active="live",
            connected=extras["connected"],
            locale=loc,
            board_kind="live",
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
    extras = _nav_extras(request)
    data = dict(DEMO[slug][period])
    return HTMLResponse(
        render_sample_dense(
            industry=slug,
            period=period,
            data=data,
            ind=INDUSTRIES[slug],
            benches_raw=BENCHMARKS[slug],
            property_name="",
            pack_links=extras["pack_links"],
            pack_groups=extras["pack_groups"],
            nav_active=f"pack:{slug}",
            connected=extras["connected"],
            locale=get_locale(request.session),
        )
    )
