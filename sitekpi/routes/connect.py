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
    list_properties,
    oauth_configured,
    redirect_uri,
)
from sitekpi.i18n import get_locale, t
from sitekpi.i18n.pack_l10n import pack_text
from sitekpi.routes.nav import nav_rail_context
from sitekpi.flow import MAX_FLOW_STEPS
from sitekpi.packs.flows import FLOW_STEPS
from sitekpi.selection import clear_selection, is_ready, save_selection, selection, selection_label
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
    err = error
    loc = get_locale(session)
    sel = selection(session)

    if demo and connected and not selected:
        properties = DEMO_PROPERTIES
    elif connected and not demo and not selected:
        creds = creds_from_session(session)
        if creds:
            try:
                properties = list_properties(creds)
            except Exception as exc:  # noqa: BLE001
                err = t("connect.err.list_props", loc, exc=exc)

    setup = None
    if connected and selected:
        from sitekpi.routes.setup import summary

        setup = summary(request, loc)

    html = render_connect_page(
        configured=configured,
        connected=connected,
        demo=demo,
        email=email,
        properties=properties,
        selected=selected if isinstance(selected, dict) else None,
        error=err,
        libs_ok=HAS_GOOGLE_AUTH and HAS_ADMIN and HAS_DATA,
        setup=setup,
        locale=loc,
        rail=nav_rail_context(request, "connect"),
    )
    return HTMLResponse(html)


@router.get("/connect", response_class=HTMLResponse)
def connect_page(request: Request):
    err = request.session.pop("connect_error", None)
    return _page_from_request(request, error=str(err) if err else None)


def _clear_keep_locale(request: Request) -> None:
    """Start a fresh session but keep the display language (set on the landing page or in 設定)."""
    from sitekpi.i18n import SESSION_KEY

    loc = request.session.get(SESSION_KEY)
    request.session.clear()
    if loc:
        request.session[SESSION_KEY] = loc


def _mark(resp: RedirectResponse, event: str = "", conn: str | None = None) -> RedirectResponse:
    """Analytics hand-off for static/js/track.js: a one-shot event name (sk_ev) and the connection
    state (sk_conn: none · demo · live). Both are SiteKPI's own words — no ids, no GA4 data."""
    if event:
        resp.set_cookie("sk_ev", event, max_age=300, samesite="lax", path="/")
    if conn == "none":
        resp.delete_cookie("sk_conn", path="/")
    elif conn:
        resp.set_cookie("sk_conn", conn, max_age=14 * 24 * 3600, samesite="lax", path="/")
    return resp


def _back_to_connect(request: Request, error: str, reason: str = "other") -> RedirectResponse:
    """Callback failures: show the message on /connect, never on a page whose URL still
    carries ?code=/state= (that URL would end up in analytics and browser history)."""
    request.session["connect_error"] = error
    return _mark(RedirectResponse("/connect", status_code=302), f"oauth_error.{reason}")


def demo_allowed() -> bool:
    """The demo connection is a dev / test mode only (DEMO_CONNECT=1, or OAuth not set up).
    In production the public sees sample boards instead (docs/plan: 見本だけ公開)."""
    import os

    return os.environ.get("DEMO_CONNECT") == "1" or not oauth_configured() or not HAS_GOOGLE_AUTH


@router.get("/connect/demo")
def connect_demo(request: Request, start: int = 0):
    if not demo_allowed():
        return RedirectResponse("/samples", status_code=302)
    _clear_keep_locale(request)
    request.session["ga4_demo"] = True
    request.session["ga4_email"] = "demo@kpistarter.local"
    if start:  # 「デモで試す」 from the start page: one click to a board
        request.session["ga4_property"] = DEMO_PROPERTIES[0]
        return _mark(RedirectResponse("/live", status_code=302), "demo_start.one_click", "demo")
    # leave property unset → show picker
    return _mark(RedirectResponse("/connect", status_code=302), "demo_start.connect", "demo")


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
        return _back_to_connect(request, t("connect.err.oauth_state", loc), "state")
    if request.query_params.get("error"):
        # e.g. access_denied — user cancelled on Google's consent screen
        return _back_to_connect(request, t("connect.err.oauth_denied", loc), "denied")
    if not code_verifier or not request.query_params.get("code"):
        return _back_to_connect(request, t("connect.err.oauth_state", loc), "state")

    # Rebuild authorization_response on the registered redirect host
    q = request.url.query
    auth_response = f"{redirect_uri()}?{q}" if q else redirect_uri()

    flow = Flow.from_client_config(client_config(), scopes=SCOPES, state=expected_state)
    flow.redirect_uri = redirect_uri()
    flow.code_verifier = code_verifier
    try:
        flow.fetch_token(authorization_response=auth_response)
    except Exception as exc:  # noqa: BLE001
        return _back_to_connect(request, t("connect.err.token", loc, exc=exc), "token")

    creds = flow.credentials
    request.session["ga4_credentials"] = json.loads(creds.to_json())
    request.session.pop("ga4_property", None)
    request.session.pop("ga4_demo", None)
    request.session["ga4_email"] = ""
    regenerate_session(request)  # new session id once signed in (anti-fixation)
    return _mark(RedirectResponse("/connect", status_code=302), "login", "live")


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
    # Numbers first: straight to the board (it guesses the flow if none is chosen yet)
    return RedirectResponse("/live", status_code=302)


@router.post("/connect/property/change")
def change_property(request: Request):
    """Pick another property: keep the Google sign-in, forget the property and its choices."""
    request.session.pop("ga4_property", None)
    clear_selection(request.session)
    return RedirectResponse("/connect", status_code=303)


@router.post("/connect/selection")
async def save_choice(request: Request):
    """訪問者の行動 (+ its edited flow) and 業種 — both required."""
    from sitekpi.flow import get_mapping_store, parse_custom_flow, property_scope
    from sitekpi.packs import INDUSTRIES
    from sitekpi.packs.behaviors import BEHAVIORS, slug_of

    session = request.session
    if not (session.get("ga4_credentials") or session.get("ga4_demo")) or not session.get("ga4_property"):
        return RedirectResponse("/connect", status_code=303)
    form = await request.form()
    loc = get_locale(session)
    behavior = str(form.get("behavior") or "")
    industry = str(form.get("industry") or "")
    if behavior not in BEHAVIORS or industry not in INDUSTRIES or INDUSTRIES[industry].get("virtual"):
        return _page_from_request(request, error=t("connect.err.choose_both", loc))
    scope = property_scope(session)
    if scope and form.get(f"{behavior}-edited"):
        pack = slug_of(behavior)
        steps, err = parse_custom_flow(
            pack,
            [str(x) for x in form.getlist(f"{behavior}-key")],
            [str(x) for x in form.getlist(f"{behavior}-event")],
            [str(x) for x in form.getlist(f"{behavior}-label")],
            loc,
        )
        if err:
            return _page_from_request(request, error=t(err, loc, n=MAX_FLOW_STEPS))
        store = get_mapping_store()
        store.set_custom_flow(scope, pack, steps)
        if steps is None:  # back to the standard flow: forget per-step event choices too
            for k in FLOW_STEPS[pack]:
                store.set(scope, pack, k, None)
    save_selection(session, behavior, industry)
    return RedirectResponse("/live", status_code=303)


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
    # legacy one-field form: an industry implies its usual behaviour
    from sitekpi.packs.behaviors import category_of, is_behavior

    if is_behavior(pack_slug):
        save_selection(session, category_of(pack_slug), selection(session)["industry"])
    else:
        save_selection(session, str(INDUSTRIES[pack_slug].get("category") or ""), pack_slug)
    return RedirectResponse("/live" if is_ready(selection(session)) else "/connect", status_code=302)


def _revoke_at_google(creds: dict) -> None:
    """Best effort, in the background: revoke the grant at Google (privacy policy §4)."""
    import threading
    import urllib.parse
    import urllib.request

    token = str(creds.get("refresh_token") or creds.get("token") or "")
    if not token:
        return

    def run() -> None:
        try:
            req = urllib.request.Request(
                "https://oauth2.googleapis.com/revoke",
                data=urllib.parse.urlencode({"token": token}).encode(),
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            urllib.request.urlopen(req, timeout=5).close()
        except Exception:  # noqa: BLE001 — the session is gone either way
            pass

    threading.Thread(target=run, daemon=True).start()


@router.post("/connect/disconnect")
def disconnect(request: Request):
    creds = request.session.get("ga4_credentials")
    if isinstance(creds, dict) and not request.session.get("ga4_demo"):
        _revoke_at_google(creds)
    _clear_keep_locale(request)  # the language the person chose stays; everything else goes
    return _mark(RedirectResponse("/connect", status_code=302), conn="none")
