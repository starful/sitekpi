"""In-app Settings — display language (session)."""

from __future__ import annotations

from html import escape

from branding import brand_head_links, brand_logo_css, brand_logo_html
from i18n import html_lang, locale_options, normalize_locale, t
from sample_dense import _rail_nav_html


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
    .shell {{ display: flex; min-height: 100vh; }}
    .rail {{
      width: var(--rail-w); flex-shrink: 0; background: #fff; border-right: 1px solid var(--line);
      padding: 16px 12px; display: flex; flex-direction: column; gap: 8px;
      position: sticky; top: 0; height: 100vh; overflow-y: auto;
      font-family: var(--font-ui);
    }}
    .rail .logo {{
      margin: 0 0 8px; padding: 4px 8px 12px;
    }}
    .rail nav {{ display: flex; flex-direction: column; gap: 1px; font-size: 0.9rem; }}
    .rail .nav-group {{
      margin: 16px 8px 6px; font-size: 0.66rem; font-weight: 700;
      letter-spacing: 0.04em; color: #8b97a8; text-transform: none;
    }}
    .rail .pack-search-wrap {{ padding: 0 8px 8px; }}
    .rail .pack-search {{
      width: 100%; box-sizing: border-box;
      border: 1px solid var(--line); border-radius: 8px;
      padding: 7px 10px; font: inherit; font-size: 0.78rem;
      background: #fff; color: var(--ink);
    }}
    .rail .pack-search-empty {{
      margin: 6px 0 0; font-size: 0.72rem; color: #94a3b8; font-weight: 600;
    }}
    .visually-hidden {{
      position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px;
      overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap; border: 0;
    }}
    .rail a {{
      display: block; padding: 7px 10px; border-radius: 6px;
      color: #3d4a5c; text-decoration: none; font-weight: 600;
    }}
    .rail a:hover {{ background: #f3f6fa; color: var(--ink); }}
    .rail a.is-on {{ background: #eef4ff; color: var(--accent); }}
    .rail a.nav-muted {{ color: #8b97a8; font-weight: 500; }}
    .rail a.nav-add {{ font-size: 0.75rem; color: var(--accent); font-weight: 600; }}
    .rail .nav-sub {{ display: flex; flex-direction: column; gap: 2px; }}
    .rail .pack-cat {{ margin: 0 0 8px; border: none; background: transparent; }}
    .rail .pack-cat summary {{
      list-style: none; cursor: pointer; user-select: none;
      display: flex; align-items: center; gap: 4px;
      padding: 8px 10px; border-radius: 4px;
      font-family: "Noto Sans JP", sans-serif;
      font-weight: 700; font-size: 0.9rem; letter-spacing: 0.02em;
      color: #8b97a8; background: transparent;
    }}
    .rail .pack-cat[open] summary {{ color: #6b7788; }}
    .rail .pack-cat summary:hover {{ color: #5a6575; background: transparent; }}
    .rail .pack-cat summary::-webkit-details-marker {{ display: none; }}
    .rail .pack-cat summary::before {{
      content: "▸"; flex: 0 0 auto; width: 0.75em;
      color: #a8b2c1; font-size: 0.8rem; line-height: 1;
    }}
    .rail .pack-cat[open] summary::before {{ content: "▾"; }}
    .rail .pack-cat-label {{ flex: 1 1 auto; min-width: 0; }}
    .rail .pack-cat-body {{
      display: flex; flex-direction: column; gap: 2px;
      padding: 2px 0 8px; margin: 0; border: none;
    }}
    .rail .pack-cat-body a {{
      margin: 0; padding: 9px 10px 9px 26px; border-radius: 6px;
      background: transparent;
    }}
    .rail .pack-cat-body a:hover {{ background: transparent; color: inherit; }}
    .rail .pack-cat-body a.is-on {{ background: #eef4ff; color: var(--accent); }}
    .rail .pack-cat-body a.is-on:hover {{ background: #eef4ff; color: var(--accent); }}
    .rail .pack-name {{
      display: block; font-family: var(--font-ui);
      font-size: 0.9rem; font-weight: 600;
    }}
    .rail .pack-hint {{
      display: none; font-size: 0.66rem; color: #8b97a8; font-weight: 500;
    }}
    .rail a.is-on .pack-hint {{ display: block; margin-top: 2px; }}
    .main {{ flex: 1; min-width: 0; }}
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
  <div class="shell">
    <aside class="rail">
      {brand_logo_html()}
      <nav>{rail}</nav>
    </aside>
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
</body>
</html>"""
