"""In-app Settings — display language (session)."""

from __future__ import annotations

from html import escape

from sitekpi.views.branding import brand_head_links, brand_logo_css
from sitekpi.i18n import html_lang, locale_options, normalize_locale, t
from sitekpi.views.layout import _rail_nav_html, mobile_bar_html, rail_css, rail_html, rail_js


def render_settings_page(
    *,
    locale: str = "ja",
    saved: bool = False,
    pack_links: list | None = None,
    pack_groups: list | None = None,
    connected: dict[str, str] | None = None,
    back_href: str = "/hr",
) -> str:
    loc = normalize_locale(locale)
    rail = _rail_nav_html(
        industry="",
        pack_links=pack_links,
        pack_groups=pack_groups,
        nav_active="settings",
        connected=connected,
        locale=loc,
    )
    opts = "".join(
        f'<option value="{escape(code)}"{" selected" if code == loc else ""}>'
        f"{escape(label)}</option>"
        for code, label in locale_options()
    )
    saved_html = (
        f'<p class="saved" role="status">{escape(t("settings.saved", loc))}</p>'
        if saved
        else ""
    )
    return f"""<!doctype html>
<html lang="{escape(html_lang(loc))}">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>SiteKPI · {escape(t("settings.title", loc))}</title>
  {brand_head_links()}
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,500;600;700;800&family=IBM+Plex+Sans+JP:wght@400;500;600;700&family=Noto+Sans+JP:wght@400;500;700;800&display=swap" rel="stylesheet" />
  <style>
    {brand_logo_css()}
    :root {{
      --ink: #152033; --muted: #6b7788; --line: #e5eaf1; --bg: #f4f6fa;
      --panel: #ffffff; --accent: #2f6fed;
      --font-ui: "IBM Plex Sans JP", "Noto Sans JP", sans-serif;
      --font-num: "DM Sans", "IBM Plex Sans JP", sans-serif;
      --rail-w: 268px;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0; min-height: 100vh; color: var(--ink);
      font-family: var(--font-ui); background: var(--bg);
    }}
    {rail_css()}
    .main {{ min-width: 0; }}
    .top {{
      padding: 18px 24px 8px; background: #fff; border-bottom: 1px solid var(--line);
    }}
    .top h1 {{ margin: 0; font-size: 1.35rem; font-weight: 800; }}
    .content {{ padding: 24px; max-width: 520px; }}
    .card {{
      background: var(--panel); border: 1px solid var(--line); border-radius: 12px;
      padding: 20px; box-shadow: 0 6px 18px rgba(21,32,51,0.04);
    }}
    .lead {{ margin: 0 0 16px; color: var(--muted); line-height: 1.6; font-size: 0.92rem; }}
    label.field {{ display: block; font-weight: 700; font-size: 0.88rem; margin-bottom: 6px; }}
    select {{
      width: 100%; padding: 10px 12px; border-radius: 8px; border: 1px solid var(--line);
      font: inherit; background: #fff;
    }}
    .hint {{ margin: 8px 0 0; font-size: 0.8rem; color: var(--muted); line-height: 1.5; }}
    .actions {{ display: flex; gap: 10px; align-items: center; margin-top: 18px; flex-wrap: wrap; }}
    button.primary {{
      border: 0; background: var(--accent); color: #fff; font-weight: 700;
      padding: 10px 16px; border-radius: 8px; cursor: pointer; font: inherit;
    }}
    a.back {{ color: var(--accent); font-weight: 700; text-decoration: none; font-size: 0.88rem; }}
    .saved {{
      margin: 0 0 14px; padding: 10px 12px; border-radius: 8px;
      background: #ecfdf5; color: #0f766e; font-weight: 700; font-size: 0.88rem;
    }}
  </style>
</head>
<body>
  {mobile_bar_html(loc)}
  <div class="shell">
    {rail_html(rail, loc)}
    <div class="main">
      <header class="top"><h1>{escape(t("settings.title", loc))}</h1></header>
      <div class="content">
        {saved_html}
        <div class="card">
          <p class="lead">{escape(t("settings.lead", loc))}</p>
          <form method="post" action="/settings">
            <label class="field" for="locale">{escape(t("settings.language", loc))}</label>
            <select id="locale" name="locale">{opts}</select>
            <p class="hint">{escape(t("settings.language_help", loc))}</p>
            <div class="actions">
              <button type="submit" class="primary">{escape(t("settings.save", loc))}</button>
              <a class="back" href="{escape(back_href)}">{escape(t("settings.back", loc))}</a>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
  {rail_js()}
</body>
</html>"""
