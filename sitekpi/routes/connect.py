"""GA4 connect routes — OAuth (PKCE), property + 業界パック selection, disconnect."""

from __future__ import annotations

import json
import secrets
from typing import Any
from urllib.parse import urlsplit

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from sitekpi.ga4.oauth import (
    DEMO_PROPERTIES,
    HAS_ADMIN,
    HAS_DATA,
    HAS_GOOGLE_AUTH,
    SCOPES,
    Flow,
    client_config,
    creds_from_session,
    demo_preview,
    fetch_preview,
    list_properties,
    oauth_configured,
    redirect_uri,
)
from sitekpi.i18n import get_locale, t
from sitekpi.i18n.pack_l10n import pack_text
from sitekpi.routes.nav import nav_rail_context
from sitekpi.session import regenerate_session
from sitekpi.views.connect import render_connect_page

router = APIRouter(tags=["ga4-connect"])

def _page_from_request(request: Request, error: str | None = None) -> HTMLResponse:
    from sitekpi.packs import INDUSTRIES, packs_by_category

    session = request.session
    configured = oauth_configured()
    demo = bool(session.get("ga4_demo"))
    connected = bool(session.get("ga4_credentials") or demo)
    email = str(session.get("ga4_email") or ("demo@kpistarter.local" if demo else ""))
    selected = session.get("ga4_property")
    properties: list[dict[str, str]] = []
    preview: dict[str, Any] | None = None
    err = error
    loc = get_locale(session)
    pack_slug = str(session.get("benchmark_pack") or "")
    if pack_slug not in INDUSTRIES:
        pack_slug = ""
    pack_label = (
        pack_text(pack_slug, "label", loc, str(INDUSTRIES[pack_slug]["label"]))
        if pack_slug
        else ""
    )

    if demo and connected and not selected:
        properties = DEMO_PROPERTIES
    elif connected and not demo and not selected:
        creds = creds_from_session(session)
        if creds:
            try:
                properties = list_properties(creds)
            except Exception as exc:  # noqa: BLE001
                err = t("connect.err.list_props", loc, exc=exc)

    if selected:
        if demo:
            preview = demo_preview(str(selected.get("id", "")))
        else:
            creds = creds_from_session(session)
            if creds:
                try:
                    preview = fetch_preview(creds, str(selected["id"]))
                except Exception as exc:  # noqa: BLE001
                    err = t("connect.err.preview", loc, exc=exc)

    html = render_connect_page(
        configured=configured,
        connected=connected,
        demo=demo,
        email=email,
        properties=properties,
        selected=selected if isinstance(selected, dict) else None,
        preview=preview,
        error=err,
        libs_ok=HAS_GOOGLE_AUTH and HAS_ADMIN and HAS_DATA,
        pack_groups=packs_by_category() if (connected and selected) else None,
        benchmark_pack=pack_slug,
        benchmark_pack_label=pack_label,
        locale=loc,
        rail=nav_rail_context(request, "connect"),
    )
    return HTMLResponse(html)


@router.get("/connect", response_class=HTMLResponse)
def connect_page(request: Request):
    return _page_from_request(request)


@router.get("/connect/demo")
def connect_demo(request: Request):
    request.session.clear()
    request.session["ga4_demo"] = True
    request.session["ga4_email"] = "demo@kpistarter.local"
    # leave property unset → show picker
    return RedirectResponse("/connect", status_code=302)


@router.get("/connect/google")
def connect_google(request: Request):
    if not oauth_configured() or not HAS_GOOGLE_AUTH:
        # User-facing: don't dump .env instructions — fall back to demo flow
        return RedirectResponse("/connect/demo", status_code=302)
    # The session cookie is per-host: start the flow on the same host Google will
    # call back to (127.0.0.1 vs localhost), otherwise the state check below fails.
    canonical = urlsplit(redirect_uri())
    if canonical.netloc and request.url.netloc != canonical.netloc:
        return RedirectResponse(
            f"{canonical.scheme}://{canonical.netloc}/connect/google", status_code=302
        )
    flow = Flow.from_client_config(client_config(), scopes=SCOPES)
    flow.redirect_uri = redirect_uri()
    # Do not include_granted_scopes — other Google products (GSC etc.) widen the
    # returned scope and oauthlib raises "Scope has changed".
    auth_url, state = flow.authorization_url(
        access_type="offline",
        prompt="consent",
    )
    # state (CSRF) + PKCE verifier live only in this browser's session; the
    # callback must come back to the same browser that started the flow.
    request.session["oauth_state"] = state
    request.session["oauth_code_verifier"] = flow.code_verifier
    request.session.pop("ga4_demo", None)
    return RedirectResponse(auth_url, status_code=302)


@router.get("/connect/callback")
def connect_callback(request: Request):
    if not HAS_GOOGLE_AUTH:
        return RedirectResponse("/connect", status_code=302)

    loc = get_locale(request.session)
    # One-shot: whatever happens below, this state/verifier pair is consumed.
    expected_state = str(request.session.pop("oauth_state", "") or "")
    code_verifier = str(request.session.pop("oauth_code_verifier", "") or "")
    returned_state = request.query_params.get("state") or ""

    if not expected_state or not returned_state or not secrets.compare_digest(
        expected_state, returned_state
    ):
        return _page_from_request(request, error=t("connect.err.oauth_state", loc))
    if request.query_params.get("error"):
        # e.g. access_denied — user cancelled on Google's consent screen
        return _page_from_request(request, error=t("connect.err.oauth_denied", loc))
    if not code_verifier or not request.query_params.get("code"):
        return _page_from_request(request, error=t("connect.err.oauth_state", loc))

    # Rebuild authorization_response on the registered redirect host
    q = request.url.query
    auth_response = f"{redirect_uri()}?{q}" if q else redirect_uri()

    flow = Flow.from_client_config(client_config(), scopes=SCOPES, state=expected_state)
    flow.redirect_uri = redirect_uri()
    flow.code_verifier = code_verifier
    try:
        flow.fetch_token(authorization_response=auth_response)
    except Exception as exc:  # noqa: BLE001
        return _page_from_request(request, error=t("connect.err.token", loc, exc=exc))

    creds = flow.credentials
    request.session["ga4_credentials"] = json.loads(creds.to_json())
    request.session.pop("ga4_property", None)
    request.session.pop("ga4_demo", None)
    request.session["ga4_email"] = ""
    regenerate_session(request)  # new session id once signed in (anti-fixation)
    return RedirectResponse("/connect", status_code=302)


@router.post("/connect/property")
def select_property(request: Request, property_id: str = Form(...)):
    session = request.session
    demo = bool(session.get("ga4_demo"))
    props: list[dict[str, str]]
    if demo:
        props = DEMO_PROPERTIES
    else:
        creds = creds_from_session(session)
        if not creds:
            return RedirectResponse("/connect", status_code=302)
        try:
            props = list_properties(creds)
        except Exception as exc:  # noqa: BLE001
            return _page_from_request(request, error=str(exc))

    chosen = next((p for p in props if p["id"] == property_id), None)
    if not chosen:
        return _page_from_request(request, error="選択した Property が見つかりません。")
    session["ga4_property"] = chosen
    return RedirectResponse("/connect", status_code=302)


@router.post("/connect/pack")
def select_pack(request: Request, pack_slug: str = Form(...)):
    from sitekpi.packs import INDUSTRIES

    session = request.session
    if not (session.get("ga4_credentials") or session.get("ga4_demo")):
        return RedirectResponse("/connect", status_code=302)
    if not session.get("ga4_property"):
        return _page_from_request(request, error="先に Property を選んでください。")
    if pack_slug not in INDUSTRIES:
        return _page_from_request(request, error="選択した業界パックが見つかりません。")
    session["benchmark_pack"] = pack_slug
    return RedirectResponse("/live", status_code=302)


@router.post("/connect/disconnect")
def disconnect(request: Request):
    request.session.clear()  # server row + cookie are dropped by the session middleware
    return RedirectResponse("/connect", status_code=302)
