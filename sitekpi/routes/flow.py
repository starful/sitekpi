"""行動フロー — live data (cached) and POST /flow/mapping (pack step → site event)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, RedirectResponse, Response

from sitekpi.cache import TTLCache
from sitekpi.flow import (
    BRANCH_POS,
    MAX_BRANCHES,
    clean_label,
    get_mapping_store,
    load_branches,
    load_custom_flow,
    property_scope,
    resolved_steps,
    sample_flow,
    step_keys,
    valid_event_name,
)
from sitekpi.ga4.data import connection_info, discover_event_names, fetch_flow
from sitekpi.i18n import get_locale, t
from sitekpi.packs.flows import FLOW_STEPS
from sitekpi.selection import flow_pack, selection
from sitekpi.views.flow import flow_context

router = APIRouter(tags=["flow"])

_FLOW_CACHE = TTLCache(maxsize=256, ttl=300.0)
_EVENTS_CACHE = TTLCache(maxsize=256, ttl=300.0)


def site_events(request: Request) -> list[dict[str, Any]]:
    """The property's event names with 28-day counts (for the mapping picker)."""
    info = connection_info(request.session)
    if not info:
        return []
    key = info["property_id"]
    hit = _EVENTS_CACHE.get(key)
    if hit is not None:
        return hit
    found, err = discover_event_names(request.session, period="28d", limit=200)
    if not err:
        _EVENTS_CACHE.set(key, found)
    return found


def sample_flow_context(pack: str, data: dict[str, Any], locale: str) -> dict[str, Any] | None:
    return flow_context(pack=pack, flow=sample_flow(pack, data), steps=resolved_steps(pack, {}),
                        locale=locale, live=False)


def live_flow_context(
    request: Request, pack: str, period: str, mapping: dict[str, str], locale: str
) -> dict[str, Any] | None:
    info = connection_info(request.session)
    custom = load_custom_flow(request.session, pack)
    steps = resolved_steps(pack, mapping, custom)
    branches = load_branches(request.session, pack, custom)
    if not info:
        return None
    events = [s["event"] for s in steps] + [b["event"] for b in branches if b["event"] not in
                                            {s["event"] for s in steps}]
    key = f"{info['property_id']}|{period}|{pack}|{','.join(events)}"
    flow = _FLOW_CACHE.get(key)
    err = None
    if flow is None:
        flow, err = fetch_flow(request.session, period=period, events=events)
        if flow is not None:
            _FLOW_CACHE.set(key, flow)
    return flow_context(pack=pack, flow=flow, steps=steps, locale=locale, live=True,
                        event_options=site_events(request), error=err, branches=branches, max_branches=MAX_BRANCHES)


_STORY_CACHE = TTLCache(maxsize=256, ttl=300.0)
RELEASES_KEY = "story_releases"
MAX_RELEASES = 10


def load_releases(session: Any) -> list[dict[str, Any]]:
    """Fixes the viewer shipped (直したら効いた？), oldest first — per GA4 property, in the session."""
    scope = property_scope(session)
    if not scope:
        return []
    rows = (session.get(RELEASES_KEY) or {}).get(scope) or []
    return [r for r in rows if isinstance(r, dict) and r.get("date")]


def live_story_x(request: Request, pack: str, period: str, mapping: dict[str, str]) -> dict[str, Any] | None:
    """board/story_x.py numbers from GA4 (cached 5 min per property · period · flow · latest release)."""
    from sitekpi.ga4.story import fetch_story_x

    info = connection_info(request.session)
    if not info:
        return None
    custom = load_custom_flow(request.session, pack)
    steps = resolved_steps(pack, mapping, custom)
    events = [s["event"] for s in steps if s.get("event")]
    rels = load_releases(request.session)
    release = rels[-1] if rels else None
    key = f"{info['property_id']}|{period}|{pack}|{','.join(events)}|{(release or {}).get('date', '')}"
    hit = _STORY_CACHE.get(key)
    if hit is not None:
        return hit
    sx, _err = fetch_story_x(request.session, period=period, events=events, last=events[-1] if events else "",
                            release=release)
    if sx is not None:
        _STORY_CACHE.set(key, sx)
    return sx


@router.post("/story/release")
async def story_release(request: Request) -> Response:
    """Save the day a fix went live (form: act · title · date) → the board compares 14 days before / after."""
    from datetime import date

    from sitekpi.board.story_x import today_jst

    form = await request.form()
    scope = property_scope(request.session)
    if not scope:
        return RedirectResponse("/live#q5", status_code=303)
    try:
        day = date.fromisoformat(str(form.get("date") or ""))
    except ValueError:
        return RedirectResponse("/live#q5", status_code=303)
    if day > today_jst():
        return RedirectResponse("/live#q5", status_code=303)
    title = clean_label(str(form.get("title") or ""))
    act = str(form.get("act") or "")
    if not title and act.isdigit():
        title = clean_label(str(form.get(f"act_title_{act}") or ""))
    store = dict(request.session.get(RELEASES_KEY) or {})
    rows = [r for r in store.get(scope) or [] if isinstance(r, dict)]
    rows.append({"date": day.isoformat(), "act": act if act.isdigit() else "", "title": title})
    rows.sort(key=lambda r: str(r.get("date")))
    store[scope] = rows[-MAX_RELEASES:]
    request.session[RELEASES_KEY] = store
    return RedirectResponse("/live#q5", status_code=303)


@router.post("/story/release/delete")
async def story_release_delete(request: Request) -> Response:
    form = await request.form()
    scope = property_scope(request.session)
    if scope:
        store = dict(request.session.get(RELEASES_KEY) or {})
        rows = list(store.get(scope) or [])
        try:
            rows.pop(int(str(form.get("idx") or "-1")))
        except (ValueError, IndexError):
            pass
        store[scope] = rows
        request.session[RELEASES_KEY] = store
    return RedirectResponse("/live#q5", status_code=303)


@router.post("/flow/mapping")
async def flow_mapping(request: Request) -> Response:
    form = await request.form()
    loc = get_locale(request.session)
    pack = str(form.get("pack") or "")
    step = str(form.get("step") or "")
    event = str(form.get("event") or "").strip()
    wants_json = "application/json" in (request.headers.get("accept") or "")

    def fail(msg: str, status: int) -> Response:
        if wants_json:
            return JSONResponse({"ok": False, "error": msg}, status_code=status)
        return RedirectResponse("/live#flow", status_code=303)

    scope = property_scope(request.session)
    if not scope or pack != flow_pack(selection(request.session)):
        return fail(t("flow.err.live", loc), 403)
    store = get_mapping_store()
    custom = store.custom_flow(scope, pack)
    if step not in step_keys(pack, custom):
        return fail(t("flow.err.event", loc), 400)
    if event and not valid_event_name(event):
        return fail(t("flow.err.event", loc), 400)
    if custom:  # a customised flow: change that step's event
        for c in custom:
            if c["key"] == step:
                c["event"] = event or (step if step in (FLOW_STEPS.get(pack) or []) else c["event"])
        store.set_custom_flow(scope, pack, custom)
    else:
        store.set(scope, pack, step, event or None)
    if wants_json:
        return JSONResponse({"ok": True, "step": step, "event": event or step})
    return RedirectResponse("/live#flow", status_code=303)


@router.post("/flow/branch")
async def flow_branch(request: Request) -> Response:
    """分岐: another behaviour at the same stage, above or below it (max MAX_BRANCHES)."""
    form = await request.form()
    loc = get_locale(request.session)
    pack = str(form.get("pack") or "")
    action = str(form.get("action") or "add")
    event = str(form.get("event") or "").strip()
    label = clean_label(str(form.get("label") or ""))
    wants_json = "application/json" in (request.headers.get("accept") or "")

    def done(payload: dict, status: int = 200) -> Response:
        if wants_json:
            return JSONResponse(payload, status_code=status)
        return RedirectResponse("/live#flow", status_code=303)

    scope = property_scope(request.session)
    if not scope or pack != flow_pack(selection(request.session)) or pack not in FLOW_STEPS:
        return done({"ok": False, "error": t("flow.err.live", loc)}, 403)
    store = get_mapping_store()
    if action == "delete":
        store.delete_branch(scope, pack, str(form.get("id") or ""))
        return done({"ok": True})
    if not valid_event_name(event):
        return done({"ok": False, "error": t("flow.err.event", loc)}, 400)
    if action == "update":
        ok = store.update_branch(scope, pack, str(form.get("id") or ""), event, label)
        return done({"ok": ok}, 200 if ok else 404)
    at, pos = str(form.get("at") or ""), str(form.get("pos") or "below")
    if at not in step_keys(pack, store.custom_flow(scope, pack)) or pos not in BRANCH_POS:
        return done({"ok": False, "error": t("flow.err.event", loc)}, 400)
    new_id = store.add_branch(scope, pack, at, pos, event, label)
    if not new_id:
        return done({"ok": False, "error": t("flow.err.max", loc, n=MAX_BRANCHES)}, 400)
    return done({"ok": True, "id": new_id})
