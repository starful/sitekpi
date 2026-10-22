"""Home page (HTML)."""

from __future__ import annotations

from html import escape

from sitekpi.packs import INDUSTRIES
from sitekpi.views.branding import BRAND_NAME, brand_head_links, brand_logo_css, brand_logo_html


def render_home() -> str:
    links = "".join(
        f'<a class="home-card" href="/{escape(slug)}">'
        f"<strong>{escape(meta['label'])}（サンプル）</strong>"
        f"<span>{escape(meta['blurb'])} · 業界パックの見本。本番はビルダー＋GA4接続を推奨。</span>"
        f"</a>"
        for slug, meta in INDUSTRIES.items()
    )
    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{BRAND_NAME}</title>
  {brand_head_links()}
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;500;600;700&family=Noto+Sans+JP:wght@400;500;700;800&display=swap" rel="stylesheet" />
  <style>
    {brand_logo_css()}
    body {{
      margin: 0; min-height: 100vh; color: #1c2430;
      font-family: "Noto Sans JP", "DM Sans", sans-serif;
      background: #ffffff;
    }}
    main {{ max-width: 720px; margin: 0 auto; padding: 48px 20px; }}
    .home-brand {{ margin: 0 0 8px; }}
    .home-brand.logo {{ font-size: 2.2rem; gap: 12px; }}
    .home-brand .logo-mark {{ width: 40px; height: 40px; }}
    p {{ color: #6b7788; line-height: 1.6; }}
    .grid {{ display: grid; gap: 12px; margin-top: 28px; }}
    .home-card {{
      display: block; padding: 18px; background: #fff; border: 1px solid #e6eaf0;
      border-radius: 14px; text-decoration: none; color: inherit;
      box-shadow: 0 6px 20px rgba(21,32,51,0.04);
    }}
    .home-card strong {{ display: block; margin-bottom: 6px; font-size: 1.1rem; }}
    .home-card span {{ color: #6b7788; font-size: 0.92rem; line-height: 1.5; }}
    .home-card:hover {{ border-color: #3b82c4; box-shadow: 0 10px 28px rgba(59,130,196,0.1); }}
  </style>
</head>
<body>
  <main>
    {brand_logo_html(css_class="logo home-brand")}
    <p>まずは GA4 を接続し、ビルダーで自分の指標・イベントを並べるのが本線です。業界パックは見本サンプルです。</p>
    <div class="grid">
      <a class="home-card" href="/hr">
        <strong>サイトKPI（密集ボード）</strong>
        <span>全業界パック共通レイアウト。業種ごとに数字・イベント・業界目安だけが変わります（例: 人事・採用）。</span>
      </a>
      <a class="home-card" href="/connect">
        <strong>GA4 接続</strong>
        <span>OAuth で Google 連携 → Property を1つ選択。接続後、実データがパレットに入ります。</span>
      </a>
      <a class="home-card" href="/builder">
        <strong>カスタムビルダー</strong>
        <span>接続 Property の指標・イベントをドラッグして、自分用ダッシュボードを組み立てます。</span>
      </a>
      {links}
    </div>
  </main>
</body>
</html>"""
