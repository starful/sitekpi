"""マイサイト一覧 /sites — every GA4 property of the signed-in account, one 総評 row each (sitekpi/portfolio.py)."""

from __future__ import annotations

from fastapi import APIRouter, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from sitekpi.billing import plan_allows
from sitekpi.ga4.oauth import DEMO_PROPERTIES, creds_from_session, list_properties
from sitekpi.i18n import get_locale
from sitekpi.metrics.help import PERIODS
from sitekpi.routes.nav import nav_rail_context

router = APIRouter()


def _billing_id(session: dict) -> str | None:
    uid = session.get("billing_user_id") or session.get("stripe_customer_id")
    return uid if isinstance(uid, str) else None


def _properties(session: dict) -> tuple[list[dict[str, str]], bool]:
    """(properties, ok). Demo → the demo properties."""
    if session.get("ga4_demo"):
        return list(DEMO_PROPERTIES), True
    creds = creds_from_session(session)
    if not creds:
        return [], False
    try:
        return list_properties(creds), True
    except Exception:  # noqa: BLE001
        return [], False


@router.get("/sites", response_class=HTMLResponse)
def page_sites(request: Request, period: str = Query(default="28d")):
    from sitekpi.portfolio import MAX_SITES, site_rows
    from sitekpi.selection import selection
    from sitekpi.templating import render

    session = request.session
    demo = bool(session.get("ga4_demo"))
    if not (demo or session.get("ga4_credentials")):
        return RedirectResponse("/connect", status_code=302)
    if period not in PERIODS:
        period = "28d"
    loc = get_locale(session)
    props, ok = _properties(session)
    cur = session.get("ga4_property") if isinstance(session.get("ga4_property"), dict) else {}
    full = demo or plan_allows(_billing_id(session), "site_compare")
    rows = site_rows(session, props, period=period, locale=loc, current_id=str(cur.get("id") or ""),
                     selection=selection(session), full=full, demo=demo) if ok else []
    return HTMLResponse(render(
        "sites.html", loc=loc, rows=rows, ok=ok, full=full, period=period, more=max(0, len(props) - MAX_SITES),
        locked=sum(1 for r in rows if r["locked"]), rail=nav_rail_context(request, "sites"),
    ))


@router.post("/sites/open")
def open_site(request: Request, property_id: str = Form(...)):
    """Open another site's board: the same as 「別のプロパティ」 + choosing it (one site connected at a time)."""
    from sitekpi.onboarding import log_ga4_connected
    from sitekpi.selection import clear_selection

    session = request.session
    props, ok = _properties(session)
    chosen = next((p for p in props if p["id"] == property_id), None) if ok else None
    if not chosen:
        return RedirectResponse("/sites", status_code=303)
    cur = session.get("ga4_property")
    if not (isinstance(cur, dict) and cur.get("id") == chosen["id"]):
        clear_selection(session)
        session["ga4_property"] = chosen
        log_ga4_connected(session)
    return RedirectResponse("/live", status_code=303)
