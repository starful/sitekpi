"""GA4 connect page (HTML)."""

from __future__ import annotations

from html import escape
from typing import Any

from sitekpi.ga4.oauth import base_url, redirect_uri
from sitekpi.i18n import html_lang, normalize_locale, t
from sitekpi.i18n.pack_l10n import pack_text
from sitekpi.views.branding import brand_head_links, brand_logo_css
from sitekpi.views.layout import mobile_bar_html, rail_css, rail_js


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
    nav_html: str = "",
) -> str:
    loc = normalize_locale(locale)
    err_html = (
        f'<div class="banner err">{escape(error)}</div>' if error else ""
    )

    # Setup help (collapsed) — only while OAuth/packages are not ready.
    # Once the app is configured, end users never see it.
    setup_needed = not (configured and libs_ok)
    status_line = (
        f'<p class="ok">{escape(t("connect.dev.ok", loc))}</p>'
        if configured and libs_ok
        else (
            f'<p class="note">{escape(t("connect.dev.unset", loc))}</p>'
            if not configured
            else f'<p class="note">{escape(t("connect.dev.pkgs", loc))}</p>'
        )
    )
    setup = "" if not setup_needed else f"""
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
SESSION_SECRET=（長いランダム文字列）
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
      --font-ui: "IBM Plex Sans JP", "Noto Sans JP", sans-serif;
      --font-num: "DM Sans", "IBM Plex Sans JP", sans-serif;
      --rail-w: 268px;
    }}
    {rail_css()}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0; min-height: 100vh; color: var(--ink);
      font-family: "Noto Sans JP", "DM Sans", sans-serif; background: var(--bg);
    }}
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
  {mobile_bar_html(loc)}
  <div class="shell">
  {nav_html}
  <div class="main">
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
  </div>
  </div>
  {rail_js()}
</body>
</html>"""
