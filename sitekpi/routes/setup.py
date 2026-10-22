"""サイトの設定 — three short questions after choosing a GA4 property.

① 流れ: which flow is closest to your site (訪問者の行動)
② 業種: which industry's standards to compare with (業界目安)
③ 調整: fix the steps that differ from your site (optional)
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response

from sitekpi.flow import (
    MAX_FLOW_STEPS,
    get_mapping_store,
    parse_custom_flow,
    property_scope,
)
from sitekpi.i18n import get_locale, t
from sitekpi.packs import INDUSTRIES
from sitekpi.packs.behaviors import BEHAVIORS, slug_of
from sitekpi.packs.flows import FLOW_STEPS, step_label
from sitekpi.routes.nav import nav_rail_context
from sitekpi.selection import is_ready, save_selection, selection
from sitekpi.views.setup import render_setup

router = APIRouter(tags=["setup"])

STEPS = ("flow", "industry", "adjust")


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


def _page(request: Request, step: str, error: str | None = None) -> HTMLResponse:
    loc = get_locale(request.session)
    sel = selection(request.session)
    counts = site_event_counts(request)
    flows = {cat: current_flow(request, cat, loc) for cat in BEHAVIORS}
    return HTMLResponse(render_setup(
        step=step, sel=sel, locale=loc, counts=counts, flows=flows, error=error,
        can_adjust=property_scope(request.session) is not None, max_steps=MAX_FLOW_STEPS,
        rail=nav_rail_context(request, "connect"),
    ))


@router.get("/setup")
def setup_start(request: Request) -> Response:
    if not _connected(request):
        return RedirectResponse("/connect", status_code=302)
    sel = selection(request.session)
    step = "flow" if not sel["behavior"] else ("industry" if not sel["industry"] else "adjust")
    return RedirectResponse(f"/setup/{step}", status_code=302)


@router.get("/setup/{step}", response_class=HTMLResponse)
def setup_step(request: Request, step: str) -> Response:
    if not _connected(request):
        return RedirectResponse("/connect", status_code=302)
    if step not in STEPS:
        return RedirectResponse("/setup", status_code=302)
    sel = selection(request.session)
    if step != "flow" and not sel["behavior"]:
        return RedirectResponse("/setup/flow", status_code=302)
    if step == "adjust" and not sel["industry"]:
        return RedirectResponse("/setup/industry", status_code=302)
    return _page(request, step)


@router.post("/setup/flow")
async def setup_flow(request: Request) -> Response:
    if not _connected(request):
        return RedirectResponse("/connect", status_code=303)
    behavior = str((await request.form()).get("behavior") or "")
    if behavior not in BEHAVIORS:
        return _page(request, "flow", t("setup.err.flow", get_locale(request.session)))
    sel = selection(request.session)
    save_selection(request.session, behavior, sel["industry"])
    return RedirectResponse("/setup/industry", status_code=303)


@router.post("/setup/industry")
async def setup_industry(request: Request) -> Response:
    if not _connected(request):
        return RedirectResponse("/connect", status_code=303)
    industry = str((await request.form()).get("industry") or "")
    sel = selection(request.session)
    if industry not in INDUSTRIES or INDUSTRIES[industry].get("virtual") or not sel["behavior"]:
        return _page(request, "industry", t("setup.err.industry", get_locale(request.session)))
    save_selection(request.session, sel["behavior"], industry)
    # ③ needs the property's events; a demo connection goes straight to the board
    if property_scope(request.session) is None:
        return RedirectResponse("/live", status_code=303)
    return RedirectResponse("/setup/adjust", status_code=303)


@router.post("/setup/adjust")
async def setup_adjust(request: Request) -> Response:
    sel = selection(request.session)
    scope = property_scope(request.session)
    if not _connected(request) or not is_ready(sel):
        return RedirectResponse("/setup", status_code=303)
    if scope is None:
        return RedirectResponse("/live", status_code=303)
    form = await request.form()
    loc = get_locale(request.session)
    pack = slug_of(sel["behavior"])
    steps, err = parse_custom_flow(
        pack,
        [str(x) for x in form.getlist("key")],
        [str(x) for x in form.getlist("event")],
        [str(x) for x in form.getlist("label")],
        loc,
    )
    if err:
        return _page(request, "adjust", t(err, loc, n=MAX_FLOW_STEPS))
    store = get_mapping_store()
    store.set_custom_flow(scope, pack, steps)
    if steps is None:  # standard flow: forget per-step event choices too
        for k in FLOW_STEPS[pack]:
            store.set(scope, pack, k, None)
    return RedirectResponse("/live", status_code=303)


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
        rows.append({"k": t("setup.s1", locale), "v": behavior_label(sel["behavior"], locale), "href": "/setup/flow"})
        rows.append({"k": t("setup.s3", locale), "v": " → ".join(s["label"] for s in steps), "href": "/setup/adjust"})
    if sel["industry"]:
        ind = sel["industry"]
        rows.insert(1, {"k": t("setup.s2", locale), "v": pack_text(ind, "label", locale, str(INDUSTRIES[ind]["label"])),
                        "href": "/setup/industry"})
    return {"rows": rows, "ready": is_ready(sel)}
