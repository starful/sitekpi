"""サイトの設定 — done on the board itself (/live): no separate pages any more.

/live?edit=1     「どこで離れているか」 in 編集モード (ひな形 + steps as the site records them) → POST /setup
/live?industry=1 the 比べる業種 drawer → POST /setup/industry
GET /setup, /setup/industry and the old wizard URLs redirect there. Errors come back as a flash.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, Response

from sitekpi.flow import (
    MAX_FLOW_STEPS,
    get_mapping_store,
    parse_custom_flow,
    property_scope,
)
from sitekpi.cache import TTLCache
from sitekpi.ga4.data import connection_info, fetch_site_basics
from sitekpi.i18n import get_locale, t
from sitekpi.packs import INDUSTRIES
from sitekpi.packs.behaviors import BEHAVIORS, slug_of
from sitekpi.packs.flows import FLOW_STEPS, step_label
from sitekpi.selection import default_industry, is_ready, save_selection, selection

router = APIRouter(tags=["setup"])


def _connected(request: Request) -> bool:
    s = request.session
    return bool((s.get("ga4_credentials") or s.get("ga4_demo")) and s.get("ga4_property"))


def site_event_counts(request: Request) -> dict[str, int] | None:
    """Event name → 28-day count for the property (None when unknown, e.g. demo)."""
    if request.session.get("ga4_demo"):
        return None
    from sitekpi.routes.flow import site_events

    found = site_events(request)
    return {e["name"]: int(e["count"]) for e in found} if found else None


def current_flow(request: Request, behavior: str, locale: str) -> list[dict[str, str]]:
    """The behaviour's steps as this property uses them (customised, mapped or standard)."""
    pack = slug_of(behavior)
    scope = property_scope(request.session)
    steps: list[dict[str, str]] | None = None
    if scope:
        store = get_mapping_store()
        steps = store.custom_flow(scope, pack)
        if not steps:
            mapping = store.get(scope, pack)
            steps = [{"key": k, "event": mapping.get(k) or k, "label": ""} for k in FLOW_STEPS[pack]]
    steps = steps or [{"key": k, "event": k, "label": ""} for k in FLOW_STEPS[pack]]
    return [
        {**s, "label": s.get("label") or (step_label(s["key"], locale, pack) if s["key"] in FLOW_STEPS[pack] else s["event"])}
        for s in steps
    ]


_BASICS_CACHE = TTLCache(maxsize=256, ttl=300.0)


def site_basics(request: Request) -> dict[str, float] | None:
    info = connection_info(request.session)
    if not info:
        return None
    hit = _BASICS_CACHE.get(info["property_id"])
    if hit is not None:
        return hit or None
    basics = fetch_site_basics(request.session)
    _BASICS_CACHE.set(info["property_id"], basics or {})
    return basics


def _flow_counts(request: Request, behavior: str) -> tuple[dict[str, int], int, bool]:
    """Event counts for the preview (28 days) and the arrivals they are read against.

    Live: the property's own event counts. Demo: the sample packs' numbers (every
    behaviour, so switching the ひな形 still shows numbers)."""
    from sitekpi.packs import DEMO

    if request.session.get("ga4_demo"):
        counts: dict[str, int] = {}
        for cat in BEHAVIORS:
            for ev, n in (DEMO[slug_of(cat)]["28d"].get("event_counts") or {}).items():
                counts.setdefault(ev, int(n))
        own = DEMO[slug_of(behavior)]["28d"]
        counts.update({k: int(v) for k, v in (own.get("event_counts") or {}).items()})
        return counts, int(own.get("uu") or 0), True
    counts = site_event_counts(request) or {}
    basics = site_basics(request) or {}
    return counts, int(basics.get("uu") or 0), False


def _ensure(request: Request) -> dict[str, str]:
    """A connected property always has a flow to edit (the board's guess if nothing was chosen)."""
    from sitekpi.selection import ensure_selection

    sel = selection(request.session)
    if is_ready(sel):
        return sel
    counts = None if request.session.get("ga4_demo") else (site_event_counts(request) or {})
    prop = str((request.session.get("ga4_property") or {}).get("name") or "")
    return ensure_selection(request.session, counts, prop)


FLASH_KEY = "board_edit_flash"


def _flash(request: Request, error: str, steps: list[dict[str, str]] | None = None,
           behavior: str | None = None, where: str = "edit") -> Response:
    request.session[FLASH_KEY] = {"error": error, "steps": steps, "behavior": behavior, "where": where}
    return RedirectResponse("/live?edit=1#flow" if where == "edit" else "/live?industry=1", status_code=303)


def board_setup(request: Request, flow_users: dict[str, int] | None = None,
                flow_entry: int = 0) -> dict[str, Any]:
    """What the board needs for 編集モード and the 比べる業種 drawer (connected boards only).

    flow_users / flow_entry: the people the board's flow shows (same period). 編集モード uses
    them for the steps already on the board, so its numbers match the view it replaces."""
    from sitekpi.i18n.pack_l10n import pack_text
    from sitekpi.views.setup import flow_editor_context

    loc = get_locale(request.session)
    sel = _ensure(request)
    flash = request.session.pop(FLASH_KEY, None) or {}
    behavior = flash.get("behavior") if flash.get("behavior") in BEHAVIORS else sel["behavior"]
    counts, entry, is_demo = _flow_counts(request, behavior)
    same = bool(flow_users) and behavior == sel["behavior"]
    if same:
        entry = flow_entry or entry
    editor = flow_editor_context(
        locale=loc, behavior=behavior, industry=sel["industry"],
        steps=flash.get("steps") if flash.get("steps") is not None else current_flow(request, behavior, loc),
        counts=counts, entry=entry, is_demo=is_demo, max_steps=MAX_FLOW_STEPS,
        step_counts=flow_users if same else None,
    )
    editor["error"] = flash.get("error") if flash.get("where") == "edit" else None
    ind = _industry_ctx(request)
    ind["error"] = flash.get("error") if flash.get("where") == "industry" else None
    name = pack_text(sel["industry"], "label", loc, str(INDUSTRIES[sel["industry"]]["label"])) \
        if sel["industry"] in INDUSTRIES else ""
    return {"editor": editor, "industry": ind, "ind_name": name,
            "open": "edit" if flash.get("where") == "edit" else ("industry" if flash.get("where") == "industry" else "")}


@router.post("/setup/keep")
def setup_keep(request: Request) -> Response:
    """「このままでよい」 on the board: the guessed flow becomes the user's choice."""
    from sitekpi.selection import AUTO_KEY

    request.session.pop(AUTO_KEY, None)
    return RedirectResponse("/live", status_code=303)


@router.get("/setup")
def setup_page(request: Request) -> Response:
    if not _connected(request):
        return RedirectResponse("/connect", status_code=302)
    return RedirectResponse("/live?edit=1#flow", status_code=302)


@router.post("/setup")
async def setup_save(request: Request) -> Response:
    """Save the edited flow: its ひな形 (behaviour) and the steps as the site records them."""
    if not _connected(request):
        return RedirectResponse("/connect", status_code=303)
    form = await request.form()
    loc = get_locale(request.session)
    sel = _ensure(request)
    behavior = str(form.get("behavior") or sel["behavior"])
    if behavior not in BEHAVIORS:
        return _flash(request, t("setup.err.flow", loc))
    keys = [str(x) for x in form.getlist("key")]
    events = [str(x) for x in form.getlist("event")]
    labels = [str(x) for x in form.getlist("label")]
    pack = slug_of(behavior)
    # only a ひな形 posted (no steps) → that behaviour's standard flow
    steps, err = parse_custom_flow(pack, keys, events, labels, loc) if events else (None, None)
    if err:
        posted = [{"key": k, "event": e, "label": lab} for k, e, lab in zip(keys, events, labels)]
        return _flash(request, t(err, loc, n=MAX_FLOW_STEPS), steps=posted, behavior=behavior)
    industry = sel["industry"] if behavior == sel["behavior"] else (default_industry(behavior) or sel["industry"])
    save_selection(request.session, behavior, industry)  # also ends the 仮 notice
    scope = property_scope(request.session)
    if scope:
        store = get_mapping_store()
        store.set_custom_flow(scope, pack, steps)
        if steps is None:  # back to the standard flow: forget per-step event choices too
            for k in FLOW_STEPS[pack]:
                store.set(scope, pack, k, None)
    period = str(form.get("period") or "")
    return RedirectResponse("/live?period=7d" if period == "7d" else "/live", status_code=303)


def _industry_ctx(request: Request) -> dict[str, Any]:
    from sitekpi.board.data import build_dense_board
    from sitekpi.packs import BENCHMARKS, DEMO
    from sitekpi.selection import flow_pack
    from sitekpi.views.setup import industry_context

    loc = get_locale(request.session)
    sel = _ensure(request)
    pack = flow_pack(sel)
    demo = DEMO[pack]["28d"]
    board = build_dense_board(industry=pack, period="28d", ind=INDUSTRIES[pack], data=demo,
                              benches_raw=BENCHMARKS[pack], locale=loc)
    rows = {r["id"]: r for r in board["summary"] + board["funnel"] + board["engage"]}
    labels = {"signup_rate": rows["signup_cvr"]["label"], "engaged_rate": rows["engaged"]["label"],
              "bounce_rate": rows["bounce_like"]["label"], "signup_to_pay": rows["funnel_rate_a"]["label"]}
    if request.session.get("ga4_demo"):
        mine = {"signup_rate": rows["signup_cvr"].get("value_num"), "engaged_rate": rows["engaged"].get("value_num"),
                "bounce_rate": rows["bounce_like"].get("value_num"), "signup_to_pay": rows["funnel_rate_a"].get("value_num")}
    else:
        basics = site_basics(request) or {}
        eng = basics.get("engaged_rate")
        mine = {"signup_rate": None, "engaged_rate": eng, "bounce_rate": (100 - eng) if eng is not None else None,
                "signup_to_pay": None}
    return industry_context(locale=loc, behavior=sel["behavior"], industry=sel["industry"], mine=mine, labels=labels)


@router.get("/setup/industry")
def setup_industry_page(request: Request) -> Response:
    if not _connected(request):
        return RedirectResponse("/connect", status_code=302)
    return RedirectResponse("/live?industry=1", status_code=302)


@router.post("/setup/industry")
async def setup_industry(request: Request) -> Response:
    if not _connected(request):
        return RedirectResponse("/connect", status_code=303)
    industry = str((await request.form()).get("industry") or "")
    sel = _ensure(request)
    if industry not in INDUSTRIES or INDUSTRIES[industry].get("virtual"):
        return _flash(request, t("setup.err.industry", get_locale(request.session)), where="industry")
    save_selection(request.session, sel["behavior"], industry)
    return RedirectResponse("/live", status_code=303)


@router.get("/setup/{step}")
def setup_old_steps(step: str) -> Response:
    """The old 3-step wizard (steps / flow / adjust) is one page now."""
    return RedirectResponse("/live?edit=1#flow", status_code=302)


def summary(request: Request, locale: str) -> dict[str, Any] | None:
    """For /connect once a property is chosen: what is set, with links to change it."""
    from sitekpi.i18n.pack_l10n import pack_text
    from sitekpi.packs.behaviors import behavior_label

    sel = selection(request.session)
    if not sel["behavior"] and not sel["industry"]:
        return None
    rows = []
    if sel["behavior"]:
        steps = current_flow(request, sel["behavior"], locale)
        rows.append({"k": t("setupx.template", locale), "v": behavior_label(sel["behavior"], locale), "href": "/live?edit=1#flow"})
        rows.append({"k": t("flow.title", locale), "v": " → ".join(s["label"] for s in steps), "href": "/live?edit=1#flow"})
    if sel["industry"]:
        ind = sel["industry"]
        rows.insert(1, {"k": t("setup.industry.all", locale),
                        "v": pack_text(ind, "label", locale, str(INDUSTRIES[ind]["label"])),
                        "href": "/live?industry=1"})
    return {"rows": rows, "ready": is_ready(sel)}
