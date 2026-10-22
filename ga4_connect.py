"""GA4 OAuth connect page — 1 Property selection (SaaS-style MVP)."""

from __future__ import annotations

import json
import os
import time
from html import escape
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from branding import brand_head_links, brand_logo_css, brand_logo_html
from i18n import get_locale, html_lang, normalize_locale, t
from i18n.pack_l10n import pack_text

# Optional Google libs — page still works in setup/demo mode without them installed
try:
    from google.auth.transport.requests import Request as GoogleAuthRequest
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import Flow

    HAS_GOOGLE_AUTH = True
except ImportError:  # pragma: no cover
    HAS_GOOGLE_AUTH = False
    Flow = None  # type: ignore[misc, assignment]
    Credentials = None  # type: ignore[misc, assignment]
    GoogleAuthRequest = None  # type: ignore[misc, assignment]

try:
    from google.analytics.admin_v1beta import AnalyticsAdminServiceClient
    from google.analytics.admin_v1beta.types import ListAccountSummariesRequest

    HAS_ADMIN = True
except ImportError:  # pragma: no cover
    HAS_ADMIN = False
    AnalyticsAdminServiceClient = None  # type: ignore[misc, assignment]

try:
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest

    HAS_DATA = True
except ImportError:  # pragma: no cover
    HAS_DATA = False
    BetaAnalyticsDataClient = None  # type: ignore[misc, assignment]

router = APIRouter(tags=["ga4-connect"])

SCOPES = ["https://www.googleapis.com/auth/analytics.readonly"]

# Cookie sessions can drop across Google redirects (localhost vs 127.0.0.1, etc.).
# Keep PKCE verifiers server-side keyed by OAuth `state` for the MVP.
_PENDING_OAUTH: dict[str, dict[str, Any]] = {}
_PENDING_TTL_SEC = 600


def _pending_put(state: str, code_verifier: str) -> None:
    now = time.time()
    expired = [k for k, v in _PENDING_OAUTH.items() if now - float(v.get("ts", 0)) > _PENDING_TTL_SEC]
    for k in expired:
        _pending_oauth_pop(k)
    _PENDING_OAUTH[state] = {"code_verifier": code_verifier, "ts": now}


def _pending_oauth_pop(state: str) -> dict[str, Any] | None:
    return _PENDING_OAUTH.pop(state, None)


DEMO_PROPERTIES = [
    {
        "id": "123456789",
        "name": "Demo Shop JP",
        "account": "Demo Account",
    },
    {
        "id": "987654321",
        "name": "Demo Media",
        "account": "Demo Account",
    },
]


def _env(name: str, default: str = "") -> str:
    return (os.getenv(name) or default).strip()


def oauth_configured() -> bool:
    return bool(_env("GOOGLE_CLIENT_ID") and _env("GOOGLE_CLIENT_SECRET"))


def redirect_uri() -> str:
    return _env(
        "GOOGLE_REDIRECT_URI",
        "http://127.0.0.1:8766/connect/callback",
    )


def base_url() -> str:
    return _env("APP_BASE_URL", "http://127.0.0.1:8766")


def _client_config() -> dict[str, Any]:
    return {
        "web": {
            "client_id": _env("GOOGLE_CLIENT_ID"),
            "client_secret": _env("GOOGLE_CLIENT_SECRET"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [redirect_uri()],
        }
    }


def _creds_from_session(session: dict[str, Any]) -> Any | None:
    if not HAS_GOOGLE_AUTH:
        return None
    info = session.get("ga4_credentials")
    if not info:
        return None
    creds = Credentials.from_authorized_user_info(info, SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(GoogleAuthRequest())
        session["ga4_credentials"] = json.loads(creds.to_json())
    return creds


def _list_properties(creds: Any) -> list[dict[str, str]]:
    if not HAS_ADMIN:
        return []
    client = AnalyticsAdminServiceClient(credentials=creds)
    out: list[dict[str, str]] = []
    for summary in client.list_account_summaries(request=ListAccountSummariesRequest()):
        account_name = summary.display_name or summary.name
        for ps in summary.property_summaries:
            # property resource name: properties/123456
            pid = ps.property.split("/")[-1] if ps.property else ""
            if not pid:
                continue
            out.append(
                {
                    "id": pid,
                    "name": ps.display_name or pid,
                    "account": account_name,
                }
            )
    return out


def _fetch_preview(creds: Any, property_id: str) -> dict[str, Any] | None:
    if not HAS_DATA:
        return None
    client = BetaAnalyticsDataClient(credentials=creds)
    req = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date="28daysAgo", end_date="yesterday")],
        metrics=[
            Metric(name="activeUsers"),
            Metric(name="sessions"),
            Metric(name="screenPageViews"),
            Metric(name="engagementRate"),
        ],
    )
    resp = client.run_report(req)
    if not resp.rows:
        return {
            "activeUsers": "0",
            "sessions": "0",
            "screenPageViews": "0",
            "engagementRate": "0%",
            "period": "直近28日",
        }
    row = resp.rows[0]
    values = [v.value for v in row.metric_values]
    eng = values[3] if len(values) > 3 else "0"
    try:
        eng_pct = f"{float(eng) * 100:.1f}%"
    except ValueError:
        eng_pct = eng
    return {
        "activeUsers": values[0] if values else "0",
        "sessions": values[1] if len(values) > 1 else "0",
        "screenPageViews": values[2] if len(values) > 2 else "0",
        "engagementRate": eng_pct,
        "period": "直近28日",
    }


def _demo_preview(property_id: str) -> dict[str, Any]:
    if property_id == "987654321":
        return {
            "activeUsers": "86,400",
            "sessions": "112,000",
            "screenPageViews": "212,800",
            "engagementRate": "51.4%",
            "period": "直近28日（デモ）",
        }
    return {
        "activeUsers": "38,920",
        "sessions": "54,210",
        "screenPageViews": "140,946",
        "engagementRate": "58.6%",
        "period": "直近28日（デモ）",
    }


def render_connect_page(
    *,
    configured: bool,
    connected: bool,
    demo: bool,
    email: str,
    properties: list[dict[str, str]],
    selected: dict[str, str] | None,
    preview: dict[str, Any] | None,
    error: str | None,
    libs_ok: bool,
    pack_groups: list[tuple[str, str, list[tuple[str, str, str]]]] | None = None,
    benchmark_pack: str = "",
    benchmark_pack_label: str = "",
    locale: str = "ja",
) -> str:
    loc = normalize_locale(locale)
    err_html = (
        f'<div class="banner err">{escape(error)}</div>' if error else ""
    )

    # Developer-only block (collapsed). Never the main user path.
    status_line = (
        f'<p class="ok">{escape(t("connect.dev.ok", loc))}</p>'
        if configured and libs_ok
        else (
            f'<p class="note">{escape(t("connect.dev.unset", loc))}</p>'
            if not configured
            else f'<p class="note">{escape(t("connect.dev.pkgs", loc))}</p>'
        )
    )
    setup = f"""
    <details class="dev">
      <summary>{escape(t("connect.dev.summary", loc))}</summary>
      <div class="dev-body">
        {status_line}
        <ol class="steps">
          <li>GCP で OAuth クライアント（ウェブ）を作成</li>
          <li>リダイレクト URI: <code>{escape(redirect_uri())}</code></li>
          <li>Analytics Admin / Data API を有効化</li>
          <li><code>.env</code> に Client ID / Secret を入れる（<code>.env.example</code> 参照）</li>
        </ol>
        <pre class="env">GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REDIRECT_URI={escape(redirect_uri())}
SESSION_SECRET=change-me
APP_BASE_URL={escape(base_url())}</pre>
      </div>
    </details>
    """

    pack_html = ""
    if connected and selected:
        pack_note = (
            f'<p class="meta">{escape(t("connect.pack.selected", loc))}'
            f'<strong>{escape(benchmark_pack_label)}</strong></p>'
            if benchmark_pack_label
            else f'<p class="meta">{escape(t("connect.pack.pick", loc))}</p>'
        )
        pack_rows = ""
        for cid, cat_label, items in pack_groups or []:
            shown_cat = t(f"cat.{cid}", loc) if cid != "all" else cat_label
            if shown_cat.startswith("cat."):
                shown_cat = cat_label
            opts = "".join(
                f"""
                <label class="prop">
                  <input type="radio" name="pack_slug" value="{escape(slug)}"
                    {"checked" if slug == benchmark_pack else ""} required />
                  <span>
                    <strong>{escape(pack_text(slug, "label", loc, label))}</strong>
                    <small>{escape(pack_text(slug, "hint", loc, hint) if hint else shown_cat)}</small>
                  </span>
                </label>
                """
                for slug, label, hint in items
            )
            pack_rows += (
                f'<div class="pack-group"><h3>{escape(shown_cat)}</h3>'
                f'<div class="prop-list">{opts}</div></div>'
            )
        pack_html = f"""
        <section class="card">
          <h2>{escape(t("connect.pack.title", loc))}</h2>
          {pack_note}
          <form method="post" action="/connect/pack">
            {pack_rows}
            <button type="submit" class="primary">{escape(t("connect.pack.submit", loc))}</button>
          </form>
        </section>
        """
        badge = escape(t("connect.badge.on", loc))
        if demo:
            badge += " · " + escape(t("connect.badge.demo", loc))
        live_btn = (
            f'<a class="btn primary" href="/live">{escape(t("connect.live_board", loc))}</a>'
            if benchmark_pack
            else ""
        )
        sel = f"""
        <section class="card hero">
          <div class="badge">{badge}</div>
          <h2>{escape(selected.get("name", ""))}</h2>
          <p class="meta">Property ID: <code>{escape(selected.get("id", ""))}</code>
            · {escape(selected.get("account", ""))}
            {" · " + escape(email) if email else ""}</p>
          <form method="post" action="/connect/disconnect" class="row">
            <button type="submit" class="ghost">{escape(t("connect.disconnect", loc))}</button>
            {live_btn}
            <a class="btn ghost" href="/builder">{escape(t("connect.open_builder", loc))}</a>
            <a class="btn ghost" href="/hr">{escape(t("connect.open_samples", loc))}</a>
          </form>
        </section>
        """
    elif connected:
        sel = f"""
        <section class="card hero">
          <div class="badge">{escape(t("connect.badge.google_ok", loc))}</div>
          <h2>{escape(t("connect.pick_property", loc))}</h2>
          <p class="meta">{escape(t("connect.pick_property_meta", loc))}</p>
        </section>
        """
    else:
        google_href = "/connect/google" if (configured and libs_ok) else "/connect/demo"
        google_note = (
            ""
            if (configured and libs_ok)
            else f'<p class="hint">{escape(t("connect.hint.demo_oauth", loc))}</p>'
        )
        sel = f"""
        <section class="card hero">
          <h2>{escape(t("connect.hero.title", loc))}</h2>
          <p class="meta">{escape(t("connect.hero.meta", loc))}</p>
          <div class="actions">
            <a class="btn primary" href="{google_href}">{escape(t("connect.btn.google", loc))}</a>
            <a class="btn ghost" href="/connect/demo">{escape(t("connect.btn.demo", loc))}</a>
          </div>
          {google_note}
        </section>
        """

    if connected and not selected and properties:
        rows = "".join(
            f"""
            <label class="prop">
              <input type="radio" name="property_id" value="{escape(p["id"])}" required />
              <span>
                <strong>{escape(p["name"])}</strong>
                <small>{escape(p["account"])} · {escape(p["id"])}</small>
              </span>
            </label>
            """
            for p in properties
        )
        props = f"""
        <section class="card">
          <h2>{escape(t("connect.property_list", loc, n=len(properties)))}</h2>
          <form method="post" action="/connect/property">
            <div class="prop-list">{rows}</div>
            <button type="submit" class="primary">{escape(t("connect.use_property", loc))}</button>
          </form>
        </section>
        """
    elif connected and not selected:
        props = f"""
        <section class="card">
          <h2>{escape(t("connect.no_property", loc))}</h2>
          <p class="meta">{escape(t("connect.no_property_meta", loc))}</p>
        </section>
        """
    else:
        props = ""

    if preview:
        preview_html = f"""
        <section class="card">
          <h2>{escape(t("connect.preview", loc))}</h2>
          <p class="meta">{escape(str(preview.get("period", "")))}</p>
          <div class="kpi-grid">
            <div><span>UU</span><strong>{escape(str(preview.get("activeUsers", "—")))}</strong></div>
            <div><span>Sessions</span><strong>{escape(str(preview.get("sessions", "—")))}</strong></div>
            <div><span>PV</span><strong>{escape(str(preview.get("screenPageViews", "—")))}</strong></div>
            <div><span>Engagement</span><strong>{escape(str(preview.get("engagementRate", "—")))}</strong></div>
          </div>
        </section>
        """
    else:
        preview_html = ""

    return f"""<!doctype html>
<html lang="{escape(html_lang(loc))}">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>SiteKPI · {escape(t("connect.title", loc))}</title>
  {brand_head_links()}
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;500;600;700&family=Noto+Sans+JP:wght@400;500;700;800&display=swap" rel="stylesheet" />
  <style>
    {brand_logo_css()}
    :root {{
      --ink: #1c2430; --muted: #6b7788; --line: #e6eaf0; --accent: #2f6fed;
      --bg: #f6f8fc; --card: #fff;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0; min-height: 100vh; color: var(--ink);
      font-family: "Noto Sans JP", "DM Sans", sans-serif; background: var(--bg);
    }}
    .top {{
      display: flex; justify-content: space-between; align-items: center; gap: 12px; flex-wrap: wrap;
      padding: 14px 20px; background: #fff; border-bottom: 1px solid var(--line);
    }}
    .brand {{ font-weight: 800; text-decoration: none; color: #152033; }}
    .top a.nav {{ color: var(--muted); text-decoration: none; font-weight: 700; font-size: 0.88rem; margin-left: 10px; }}
    .top a.nav:hover {{ color: var(--accent); }}
    main {{ max-width: 720px; margin: 0 auto; padding: 28px 20px 48px; }}
    h1 {{
      font-family: "DM Sans", "Noto Sans JP", sans-serif;
      font-size: 1.8rem; margin: 0 0 8px; color: #152033;
    }}
    .lead {{ color: var(--muted); line-height: 1.6; margin: 0 0 20px; }}
    .card {{
      background: var(--card); border: 1px solid var(--line); border-radius: 14px;
      padding: 18px; margin-bottom: 14px; box-shadow: 0 8px 24px rgba(21,32,51,0.04);
    }}
    .card.hero {{ padding: 22px; }}
    .card h2 {{ margin: 0 0 8px; font-size: 1.15rem; }}
    .meta {{ margin: 0; color: var(--muted); font-size: 0.9rem; line-height: 1.6; }}
    .hint {{ margin: 10px 0 0; color: var(--muted); font-size: 0.82rem; }}
    .badge {{
      display: inline-block; font-size: 0.7rem; font-weight: 800; letter-spacing: 0.06em;
      text-transform: uppercase; color: #0f766e; background: #e7f7f3;
      border: 1px solid #b7e5d8; border-radius: 999px; padding: 3px 8px; margin-bottom: 8px;
    }}
    .steps {{ margin: 8px 0 0; padding-left: 1.2rem; color: var(--ink); line-height: 1.7; font-size: 0.88rem; }}
    .env {{
      margin: 12px 0 0; padding: 12px; background: #0f172a; color: #e2e8f0;
      border-radius: 10px; font-size: 0.78rem; overflow: auto; line-height: 1.5;
    }}
    .note {{ margin: 0 0 8px; color: var(--muted); font-size: 0.88rem; }}
    .ok {{ color: #0f766e; font-weight: 700; margin: 0 0 8px; font-size: 0.88rem; }}
    .banner {{
      padding: 12px 14px; border-radius: 10px; margin-bottom: 14px; font-size: 0.9rem; line-height: 1.5;
    }}
    .banner.err {{ background: #fff1f2; border: 1px solid #fecdd3; color: #9f1239; }}
    .actions {{ display: flex; flex-wrap: wrap; gap: 10px; margin: 16px 0 0; }}
    .row {{ display: flex; flex-wrap: wrap; gap: 10px; margin-top: 14px; }}
    a.btn, button {{
      display: inline-flex; align-items: center; justify-content: center;
      font: inherit; font-weight: 700; padding: 10px 14px; border-radius: 10px;
      border: 1px solid var(--line); background: #fff; color: var(--ink);
      text-decoration: none; cursor: pointer;
    }}
    a.btn.primary, button.primary {{ background: var(--accent); color: #fff; border-color: var(--accent); }}
    a.btn.ghost:hover, button.ghost:hover {{ border-color: var(--accent); color: var(--accent); }}
    .prop-list {{ display: flex; flex-direction: column; gap: 8px; margin: 12px 0 16px; }}
    .prop {{
      display: flex; gap: 10px; align-items: flex-start; padding: 12px;
      border: 1px solid var(--line); border-radius: 10px; cursor: pointer; background: #fafbfd;
    }}
    .prop:has(input:checked) {{ border-color: #bfd2f8; background: #eaf1ff; }}
    .prop strong {{ display: block; font-size: 0.95rem; }}
    .prop small {{ color: var(--muted); font-size: 0.8rem; }}
    .pack-group {{ margin: 0 0 14px; }}
    .pack-group h3 {{
      margin: 0 0 8px; font-size: 0.78rem; font-weight: 800; color: var(--muted);
      letter-spacing: 0.04em;
    }}
    .pack-group .prop-list {{ margin-top: 0; }}
    .kpi-grid {{
      display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; margin-top: 12px;
    }}
    .kpi-grid div {{
      padding: 12px; border-radius: 10px; background: #f6f8fc; border: 1px solid var(--line);
    }}
    .kpi-grid span {{ display: block; font-size: 0.75rem; color: var(--muted); font-weight: 700; }}
    .kpi-grid strong {{
      font-family: "DM Sans", "Noto Sans JP", sans-serif;
      font-size: 1.35rem; font-weight: 800;
    }}
    code {{ font-size: 0.85em; }}
    .dev {{
      margin-top: 28px; border: 1px dashed #d8dee8; border-radius: 12px;
      background: #fafbfd; padding: 0 14px;
    }}
    .dev summary {{
      cursor: pointer; font-size: 0.82rem; font-weight: 700; color: #93a0b4;
      padding: 12px 0; list-style: none;
    }}
    .dev summary::-webkit-details-marker {{ display: none; }}
    .dev summary::before {{ content: "▸ "; }}
    .dev[open] summary::before {{ content: "▾ "; }}
    .dev-body {{ padding: 0 0 14px; }}
  </style>
</head>
<body>
  <header class="top">
    <div>
      {brand_logo_html(css_class="logo brand")}
      <a class="nav" href="/builder">{escape(t("connect.nav.builder", loc))}</a>
      <a class="nav" href="/hr">{escape(t("connect.nav.samples", loc))}</a>
      <a class="nav" href="/settings">{escape(t("connect.nav.settings", loc))}</a>
    </div>
  </header>
  <main>
    <h1>{escape(t("connect.title", loc))}</h1>
    <p class="lead">{escape(t("connect.lead", loc))}</p>
    {err_html}
    {sel}
    {props}
    {pack_html}
    {preview_html}
    {setup}
  </main>
</body>
</html>"""


def _page_from_request(request: Request, error: str | None = None) -> HTMLResponse:
    from packs import INDUSTRIES, packs_by_category

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
        creds = _creds_from_session(session)
        if creds:
            try:
                properties = _list_properties(creds)
            except Exception as exc:  # noqa: BLE001
                err = t("connect.err.list_props", loc, exc=exc)

    if selected:
        if demo:
            preview = _demo_preview(str(selected.get("id", "")))
        else:
            creds = _creds_from_session(session)
            if creds:
                try:
                    preview = _fetch_preview(creds, str(selected["id"]))
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
    flow = Flow.from_client_config(_client_config(), scopes=SCOPES)
    flow.redirect_uri = redirect_uri()
    # Do not include_granted_scopes — other Google products (GSC etc.) widen the
    # returned scope and oauthlib raises "Scope has changed".
    auth_url, state = flow.authorization_url(
        access_type="offline",
        prompt="consent",
    )
    # PKCE: keep verifier in session AND server memory (keyed by state)
    request.session["oauth_state"] = state
    request.session["oauth_code_verifier"] = flow.code_verifier
    _pending_put(state, str(flow.code_verifier or ""))
    request.session.pop("ga4_demo", None)
    return RedirectResponse(auth_url, status_code=302)


@router.get("/connect/callback")
def connect_callback(request: Request):
    if not HAS_GOOGLE_AUTH:
        return RedirectResponse("/connect", status_code=302)

    # Prefer state from Google callback query — session cookie may be missing
    state = (
        request.query_params.get("state")
        or request.session.get("oauth_state")
        or ""
    )
    pending = _pending_oauth_pop(state) if state else None
    code_verifier = (
        (pending or {}).get("code_verifier")
        or request.session.get("oauth_code_verifier")
        or ""
    )
    if not state:
        return _page_from_request(
            request,
            error="OAuth state がありません。もう一度「Google で接続」からやり直してください。",
        )
    if not code_verifier:
        return _page_from_request(
            request,
            error="OAuth code_verifier がありません。もう一度「Google で接続」からやり直してください。"
            "（127.0.0.1 と localhost を混ぜないでください）",
        )

    # Rebuild authorization_response on the registered redirect host
    # (avoids localhost vs 127.0.0.1 mismatch with GOOGLE_REDIRECT_URI)
    q = request.url.query
    auth_response = f"{redirect_uri()}?{q}" if q else redirect_uri()

    flow = Flow.from_client_config(_client_config(), scopes=SCOPES, state=state)
    flow.redirect_uri = redirect_uri()
    flow.code_verifier = code_verifier
    # If Google still returns extra scopes, don't fail the token exchange
    os.environ.setdefault("OAUTHLIB_RELAX_TOKEN_SCOPE", "1")
    try:
        flow.fetch_token(authorization_response=auth_response)
    except Exception as exc:  # noqa: BLE001
        return _page_from_request(request, error=f"トークン取得に失敗: {exc}")

    creds = flow.credentials
    request.session["ga4_credentials"] = json.loads(creds.to_json())
    request.session.pop("ga4_property", None)
    request.session.pop("ga4_demo", None)
    request.session.pop("oauth_state", None)
    request.session.pop("oauth_code_verifier", None)
    request.session["ga4_email"] = ""
    return RedirectResponse("/connect", status_code=302)


@router.post("/connect/property")
def select_property(request: Request, property_id: str = Form(...)):
    session = request.session
    demo = bool(session.get("ga4_demo"))
    props: list[dict[str, str]]
    if demo:
        props = DEMO_PROPERTIES
    else:
        creds = _creds_from_session(session)
        if not creds:
            return RedirectResponse("/connect", status_code=302)
        try:
            props = _list_properties(creds)
        except Exception as exc:  # noqa: BLE001
            return _page_from_request(request, error=str(exc))

    chosen = next((p for p in props if p["id"] == property_id), None)
    if not chosen:
        return _page_from_request(request, error="選択した Property が見つかりません。")
    session["ga4_property"] = chosen
    # Persist lightweight choice for local MVP
    _save_local_choice(
        chosen,
        demo=demo,
        benchmark_pack=str(session.get("benchmark_pack") or ""),
    )
    return RedirectResponse("/connect", status_code=302)


@router.post("/connect/pack")
def select_pack(request: Request, pack_slug: str = Form(...)):
    from packs import INDUSTRIES

    session = request.session
    if not (session.get("ga4_credentials") or session.get("ga4_demo")):
        return RedirectResponse("/connect", status_code=302)
    if not session.get("ga4_property"):
        return _page_from_request(request, error="先に Property を選んでください。")
    if pack_slug not in INDUSTRIES:
        return _page_from_request(request, error="選択した業界パックが見つかりません。")
    session["benchmark_pack"] = pack_slug
    prop = session.get("ga4_property")
    if isinstance(prop, dict):
        _save_local_choice(
            prop,
            demo=bool(session.get("ga4_demo")),
            benchmark_pack=pack_slug,
        )
    return RedirectResponse("/live", status_code=302)


@router.post("/connect/disconnect")
def disconnect(request: Request):
    request.session.clear()
    path = Path(__file__).resolve().parent / ".ga4_connection.json"
    if path.exists():
        path.unlink()
    return RedirectResponse("/connect", status_code=302)


def _save_local_choice(
    prop: dict[str, str], *, demo: bool, benchmark_pack: str = ""
) -> None:
    path = Path(__file__).resolve().parent / ".ga4_connection.json"
    path.write_text(
        json.dumps(
            {"property": prop, "demo": demo, "benchmark_pack": benchmark_pack},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
