"""Navigation context shared by every page route (rail: samples / connected / app)."""

from __future__ import annotations

from typing import Any

from fastapi import Request

from sitekpi.ga4.data import connection_info
from sitekpi.i18n import get_locale, t
from sitekpi.packs import INDUSTRIES, pack_links, packs_by_category
from sitekpi.views.layout import rail_context


def nav_context(request: Request) -> dict[str, Any]:
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
    from sitekpi.selection import selection, selection_label

    sel = selection(session)
    if connected is not None:
        connected["selection"] = selection_label(sel, get_locale(session))
    return {
        "connected": connected,
        "pack_links": pack_links(),
        "pack_groups": packs_by_category(),
        "selection": sel,
    }


def nav_rail_context(request: Request, nav_active: str) -> dict[str, Any]:
    """Rail data for templates (templates/partials/rail.html)."""
    ctx = nav_context(request)
    return rail_context(
        nav_active=nav_active,
        locale=get_locale(request.session),
        connected=ctx["connected"],
    )
