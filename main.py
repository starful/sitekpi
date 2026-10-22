"""SiteKPI — industry packs, dense board, GA4 connect, builder."""

from __future__ import annotations

import os
import time
from html import escape
from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# Allow OAuth token exchange on local http:// (dev only)
_redirect = (os.getenv("GOOGLE_REDIRECT_URI") or os.getenv("APP_BASE_URL") or "").lower()
if _redirect.startswith("http://") and not os.getenv("OAUTHLIB_INSECURE_TRANSPORT"):
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

from branding import BRAND_NAME, brand_head_links, brand_logo_css, brand_logo_html
from builder import render_builder
from ga4_connect import router as ga4_router
from ga4_data import (
    build_live_builder_widgets,
    connection_info,
    discover_event_names,
    fetch_pack_overlay,
    saved_events,
)
from i18n import get_locale, set_locale, t
from i18n.pack_l10n import pack_text
from sample_dense import render_sample_dense
from settings_page import render_settings_page

app = FastAPI(title=f"{BRAND_NAME}")
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET", "kpistarter-dev-secret-change-me"),
    session_cookie="kpistarter_session",
    same_site="lax",
    https_only=False,
    max_age=14 * 24 * 60 * 60,
)
app.include_router(ga4_router)
app.mount(
    "/static",
    StaticFiles(directory=str(Path(__file__).resolve().parent / "static")),
    name="static",
)

Period = Literal["7d", "28d"]
Arrow = Literal["up", "mid", "down", "none"]

# Pack + metric catalogs (add industries in packs/, help keys in metrics/)
from metrics.help import HELP, KINDS, PERIODS
from packs import (
    BENCHMARKS,
    DEMO,
    EVENT_DESC,
    INDUSTRIES,
    pack_links,
    packs_by_category,
)


def fmt_int(n: int) -> str:
    return f"{n:,}"


def fmt_yen(n: float | int) -> str:
    return f"¥{int(round(n)):,}"


def fmt_delta(v: float) -> str:
    sign = "+" if v > 0 else ""
    return f"{sign}{v:.1f}%"


def band_meta(industry: str, key: str) -> dict[str, Any] | None:
    spec = BENCHMARKS.get(industry, {}).get(key)
    if not spec:
        return None
    low, high = float(spec["low"]), float(spec["high"])
    unit = str(spec.get("unit", ""))
    return {
        "low": low,
        "high": high,
        "unit": unit,
        "label": f"{low:g}–{high:g}{unit}",
        "higher_is_better": bool(spec["higher_is_better"]),
    }


def band_arrow(value: float, industry: str, key: str) -> Arrow:
    meta = band_meta(industry, key)
    if not meta:
        return "none"
    low, high = meta["low"], meta["high"]
    if low <= value <= high:
        return "mid"
    if value > high:
        return "up" if meta["higher_is_better"] else "down"
    return "down" if meta["higher_is_better"] else "up"


def arrow_html(arrow: Arrow) -> str:
    if arrow == "none":
        return ""
    # Geometric icons (not text arrows) with distinct colors
    icons = {
        "up": ("▲", "業界目安より上"),
        "mid": ("●", "業界目安の範囲内"),
        "down": ("▼", "業界目安より下"),
    }
    symbol, label = icons[arrow]
    return (
        f'<span class="bench-icon bench-{arrow}" title="{escape(label)}" '
        f'aria-label="{escape(label)}">{symbol}</span>'
    )


# Distinct soft tones so each card's 業界目安 stands out
BENCH_TONES: dict[str, str] = {
    "new_pct": "tone-sky",
    "engaged_rate": "tone-blue",
    "bounce_rate": "tone-amber",
    "pages_session": "tone-indigo",
    "sessions_per_uu": "tone-teal",
    "pages_per_uu": "tone-indigo",
    "signup_rate": "tone-teal",
    "signup_to_pay": "tone-amber",
    "pay_cvr": "tone-amber",
    "paid_rate": "tone-indigo",
    "churn_rate": "tone-sky",
}

# Fixed palette for up to ~10 GA-style channel groups
CHANNEL_TONES: dict[str, str] = {
    "Organic Search": "chan-teal",
    "Direct": "chan-slate",
    "Paid Search": "chan-amber",
    "Paid Social": "chan-rose",
    "Organic Social": "chan-blue",
    "Social": "chan-blue",
    "Referral": "chan-indigo",
    "Email": "chan-sky",
    "Display": "chan-violet",
    "Affiliates": "chan-lime",
    "Other": "chan-gray",
}


def bench_row(industry: str, key: str) -> str:
    meta = band_meta(industry, key)
    if not meta:
        return ""
    tone = BENCH_TONES.get(key, "tone-blue")
    return (
        f'<div class="bench {tone}">'
        f'<span class="bench-label">業界目安</span>'
        f'<span class="bench-num">{escape(meta["label"])}</span>'
        f"</div>"
    )


def kind_badge(kind: str) -> str:
    meta = KINDS[kind]
    return f'<span class="kind kind-{escape(kind)}">{escape(meta["short"])}</span>'


def help_button(help_id: str) -> str:
    title = HELP[help_id]["title"]
    return (
        f'<button type="button" class="help-btn" data-help="{escape(help_id)}" '
        f'aria-label="{escape(title)}の説明">?</button>'
    )


def title_row(label: str, help_id: str) -> str:
    kind = HELP[help_id]["kind"]
    return (
        f'<div class="k">'
        f"<span>{escape(label)}</span>"
        f'<span class="k-right">{kind_badge(kind)}{help_button(help_id)}</span>'
        f"</div>"
    )


def help_dialogs_html(notes: list[str]) -> str:
    blocks = []
    for help_id, h in HELP.items():
        kind = KINDS[h["kind"]]
        formula_html = "<br>".join(escape(line) for line in h["formula"].split("\n"))
        blocks.append(
            f"""
            <dialog class="help-dialog" id="help-{escape(help_id)}" data-help-dialog>
              <form method="dialog" class="help-sheet">
                <header>
                  <div>
                    <p class="help-kind">{escape(kind["label"])}</p>
                    <h3>{escape(h["title"])}</h3>
                  </div>
                  <button type="submit" class="help-close" aria-label="閉じる">×</button>
                </header>
                <section>
                  <h4>意味</h4>
                  <p>{"<br>".join(escape(line) for line in h["meaning"].split(chr(10)))}</p>
                </section>
                <section>
                  <h4>計算式 / 定義</h4>
                  <p class="formula">{formula_html}</p>
                </section>
                <section>
                  <h4>見るポイント</h4>
                  <p>{escape(h["tip"])}</p>
                </section>
              </form>
            </dialog>
            """
        )

    notes_html = "".join(f"<li>{escape(n)}</li>" for n in notes)
    blocks.append(
        f"""
        <dialog class="help-dialog" id="help-guide" data-help-dialog>
          <form method="dialog" class="help-sheet">
            <header>
              <div>
                <p class="help-kind">ガイド</p>
                <h3>この画面の見方</h3>
              </div>
              <button type="submit" class="help-close" aria-label="閉じる">×</button>
            </header>
            <section>
              <h4>デジタルデータ</h4>
              <p>{escape(KINDS["digital"]["desc"])}</p>
            </section>
            <section>
              <h4>業務データ</h4>
              <p>{escape(KINDS["business"]["desc"])}</p>
            </section>
            <section>
              <h4>業界目安とアイコン</h4>
              <p>{escape(HELP["benchmark"]["meaning"])}</p>
              <p class="formula">{'<br>'.join(escape(x) for x in HELP["benchmark"]["formula"].split(chr(10)))}</p>
            </section>
            <section>
              <h4>読み順</h4>
              <p>①業務KPI → ②デジタルKPI → ③イベント（カテゴリ別） → ④流入チャネル</p>
            </section>
            <section>
              <h4>いまの期間メモ</h4>
              <ul class="notes">{notes_html}</ul>
            </section>
          </form>
        </dialog>
        """
    )
    return "\n".join(blocks)


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


def _biz_na_card(label: str, help_id: str) -> str:
    return f"""
        <article class="card panel is-na">
          {title_row(label, help_id)}
          <div class="value-row"><div class="v na">—</div></div>
          <div class="d">未連携 · 業務DB</div>
        </article>
        """


def _business_cards_html(
    *,
    live: bool,
    industry: str,
    data: dict[str, Any],
    free_members: int,
    paid_rate: float,
    churn_rate: float,
    arpu: float,
    arppu: float,
    paid_rate_arrow: Arrow,
    churn_rate_arrow: Arrow,
) -> str:
    if live:
        return "".join(
            _biz_na_card(label, hid)
            for label, hid in [
                ("会員数（DB）", "members_db"),
                ("有料会員数（DB）", "paid_members"),
                ("無料会員数（DB）", "free_members"),
                ("有料化率", "paid_rate"),
                ("新規有料（期間）", "new_paid"),
                ("退会 / 解約", "churn"),
                ("解約率", "churn_rate"),
                ("売上（期間）", "revenue"),
                ("ARPU", "arpu"),
                ("ARPPU", "arppu"),
            ]
        )
    return f"""
        <article class="card panel">
          {title_row("会員数（DB）", "members_db")}
          <div class="value-row"><div class="v">{fmt_int(data["members_db"])}</div></div>
          <div class="d">{fmt_delta(data["members_delta"])}</div>
        </article>
        <article class="card panel">
          {title_row("有料会員数（DB）", "paid_members")}
          <div class="value-row"><div class="v">{fmt_int(data["paid_members"])}</div></div>
          <div class="d">{fmt_delta(data["paid_delta"])}</div>
        </article>
        <article class="card panel">
          {title_row("無料会員数（DB）", "free_members")}
          <div class="value-row"><div class="v">{fmt_int(free_members)}</div></div>
          <div class="d">会員 − 有料</div>
        </article>
        <article class="card panel">
          {title_row("有料化率", "paid_rate")}
          <div class="value-row">
            <div class="v">{paid_rate}%</div>
            {arrow_html(paid_rate_arrow)}
          </div>
          {bench_row(industry, "paid_rate")}
        </article>
        <article class="card panel">
          {title_row("新規有料（期間）", "new_paid")}
          <div class="value-row"><div class="v">{fmt_int(data["new_paid"])}</div></div>
          <div class="d">初回課金 · 業務DB</div>
        </article>
        <article class="card panel">
          {title_row("退会 / 解約", "churn")}
          <div class="value-row"><div class="v">{fmt_int(data["churn"])}</div></div>
          <div class="d">期間中 · 件数</div>
        </article>
        <article class="card panel">
          {title_row("解約率", "churn_rate")}
          <div class="value-row">
            <div class="v">{churn_rate}%</div>
            {arrow_html(churn_rate_arrow)}
          </div>
          {bench_row(industry, "churn_rate")}
        </article>
        <article class="card panel">
          {title_row("売上（期間）", "revenue")}
          <div class="value-row"><div class="v">{fmt_yen(data["revenue"])}</div></div>
          <div class="d">{fmt_delta(data["revenue_delta"])}</div>
        </article>
        <article class="card panel">
          {title_row("ARPU", "arpu")}
          <div class="value-row"><div class="v">{fmt_yen(arpu)}</div></div>
          <div class="d">売上 ÷ 全会員</div>
        </article>
        <article class="card panel">
          {title_row("ARPPU", "arppu")}
          <div class="value-row"><div class="v">{fmt_yen(arppu)}</div></div>
          <div class="d">売上 ÷ 有料会員</div>
        </article>
        """


def render(
    industry: str,
    period: Period,
    *,
    data: dict[str, Any] | None = None,
    live: bool = False,
    live_error: str | None = None,
    property_name: str = "",
) -> str:
    ind = INDUSTRIES[industry]
    data = data or DEMO[industry][period]
    notes = ind["notes"][period]
    new_pct = round(100 * data["new_users"] / max(data["uu"], 1), 1)
    ret_pct = round(100 - new_pct, 1)
    sessions_per_uu = round(data["sessions"] / max(data["uu"], 1), 2)
    pages_per_uu = round(data["pageviews"] / max(data["uu"], 1), 1)
    bounce_rate = round(100 - float(data["engaged_rate"]), 1)
    signup_to_pay = round(100 * data["pay_start"] / max(data["signups"], 1), 1)
    free_members = max(data["members_db"] - data["paid_members"], 0)
    paid_rate = round(100 * data["paid_members"] / max(data["members_db"], 1), 1)
    churn_rate = round(100 * data["churn"] / max(data["members_db"], 1), 2)
    arpu = data["revenue"] / max(data["members_db"], 1)
    arppu = data["revenue"] / max(data["paid_members"], 1)
    live_events = data.get("_live_events")
    live_primary = data.get("_live_primary")
    primary = str(live_primary or ind["primary_event"])
    signup_label = ind["signup_label"] if not live else (primary or ind["signup_label"])

    engaged_arrow = band_arrow(data["engaged_rate"], industry, "engaged_rate")
    bounce_arrow = band_arrow(bounce_rate, industry, "bounce_rate")
    signup_arrow = band_arrow(data["signup_rate"], industry, "signup_rate")
    pay_arrow = band_arrow(data["pay_cvr"], industry, "pay_cvr")
    pages_arrow = band_arrow(data["pages_session"], industry, "pages_session")
    spu_arrow = band_arrow(sessions_per_uu, industry, "sessions_per_uu")
    ppu_arrow = band_arrow(pages_per_uu, industry, "pages_per_uu")
    stp_arrow = band_arrow(signup_to_pay, industry, "signup_to_pay")
    new_arrow = band_arrow(new_pct, industry, "new_pct")
    paid_rate_arrow = band_arrow(paid_rate, industry, "paid_rate")
    churn_rate_arrow = band_arrow(churn_rate, industry, "churn_rate")

    channel_rows = "".join(
        f"""
        <div class="chan-row {CHANNEL_TONES.get(name, "chan-gray")}">
          <span class="chan-name">{escape(name)}</span>
          <div class="bar" role="presentation"><i style="width:{pct}%"></i></div>
          <span class="chan-pct">{pct}%</span>
        </div>
        """
        for name, pct in data["channels"]
    )
    event_counts: dict[str, int] = data.get("event_counts") or {}

    def event_row_html(e: str) -> str:
        desc = EVENT_DESC.get(e, "")
        if live and not desc:
            desc = "GA4 イベント件数"
        return f"""
        <div class="event-row{" is-primary" if e == primary else ""}">
          <div class="event-main">
            <div class="event-name">
              <code>{escape(e)}</code>
              {"<span class='event-tag'>主転換</span>" if e == primary else ""}
            </div>
            <p class="event-desc">{escape(desc)}</p>
          </div>
          <div class="event-count">{fmt_int(int(event_counts.get(e, 0)))}</div>
        </div>
        """

    if live and isinstance(live_events, list) and live_events:
        others = [e for e in live_events if e != primary]
        categories: list[dict[str, Any]] = []
        if primary in live_events:
            categories.append({"label": "主転換", "events": [primary]})
        if others:
            categories.append({"label": "イベント（GA4）", "events": others})
        if not categories:
            categories = [{"label": "イベント（GA4）", "events": list(live_events)}]
    else:
        categories = ind.get("event_categories") or [
            {"label": "イベント", "events": ind["events"]}
        ]
    event_categories_html = "".join(
        f"""
        <div class="event-cat">
          <h3 class="event-cat-title">{escape(cat["label"])}</h3>
          <div class="event-list">
            {"".join(event_row_html(e) for e in cat["events"])}
          </div>
        </div>
        """
        for cat in categories
    )
    period_opts = "".join(
        f'<option value="{escape(k)}"{" selected" if k == period else ""}>{escape(v)}</option>'
        for k, v in PERIODS.items()
    )
    other_links = "".join(
        f'<a href="/{escape(slug)}">{escape(meta["label"])}</a>'
        for slug, meta in INDUSTRIES.items()
        if slug != industry
    )

    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{BRAND_NAME} · {escape(ind["label"])}</title>
  {brand_head_links()}
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;500;600;700&family=Noto+Sans+JP:wght@400;500;700;800&display=swap" rel="stylesheet" />
  <style>
    :root {{
      --bg: #ffffff;
      --ink: #1c2430;
      --muted: #6b7788;
      --card: #ffffff;
      --line: #e6eaf0;
      --soft: #f5f7fa;
      --accent: #2f6fed;
      --accent-soft: #eaf1ff;
      --business: #5b6b86;
      --shadow: 0 8px 24px rgba(21,32,51,0.04);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      color: var(--ink);
      font-family: "Noto Sans JP", "DM Sans", sans-serif;
      background: #ffffff;
      min-height: 100vh;
    }}
    main {{ max-width: 1040px; margin: 0 auto; padding: 36px 20px 72px; }}
    .topnav {{
      display: flex; justify-content: space-between; gap: 12px; flex-wrap: wrap;
      margin-bottom: 18px; font-size: 0.88rem; color: var(--muted);
    }}
    .topnav a {{ color: var(--accent); text-decoration: none; font-weight: 600; }}
    .topnav a:hover {{ text-decoration: underline; }}
    .banner-live {{
      margin: 0 0 10px; padding: 10px 12px; border-radius: 10px; font-size: 0.88rem;
      background: #e7f7f3; border: 1px solid #b7e5d8; color: #0f766e; font-weight: 700;
    }}
    .banner-err {{
      margin: 0 0 10px; padding: 10px 12px; border-radius: 10px; font-size: 0.88rem;
      background: #fff1f2; border: 1px solid #fecdd3; color: #9f1239;
    }}
    .card.is-na {{ opacity: 0.72; background: #f8fafc; }}
    .card .v.na {{ color: #94a3b8; font-weight: 700; letter-spacing: 0.04em; }}
    .badge {{
      font-size: 0.72rem; font-weight: 800; letter-spacing: 0.08em;
      text-transform: uppercase; color: #93a0b4; margin: 0 0 8px;
    }}
    .brand {{
      font-family: "DM Sans", "Noto Sans JP", sans-serif;
      font-weight: 700; font-size: clamp(2rem, 4.5vw, 2.7rem);
      margin: 0 0 6px; letter-spacing: -0.02em; color: #152033;
    }}
    .lead {{
      margin: 0 0 18px; color: var(--muted); max-width: 40rem; line-height: 1.65;
    }}
    .panel {{
      background: var(--card); border: 1px solid var(--line);
      border-radius: 14px; box-shadow: var(--shadow);
    }}
    .nav-sub {{ margin: -8px 0 18px; font-size: 0.88rem; color: var(--muted); }}
    .nav-sub a {{ color: var(--accent); text-decoration: none; font-weight: 600; margin-right: 10px; }}
    .page-tools {{
      display: flex; flex-wrap: wrap; gap: 10px; align-items: center;
      margin: 0;
    }}
    .page-tools label {{
      display: inline-flex; align-items: center; gap: 8px;
      font-size: 0.8rem; font-weight: 700; color: var(--muted); margin: 0;
    }}
    .page-tools select {{
      font: inherit; padding: 8px 12px; border-radius: 10px;
      border: 1px solid var(--line); background: #fff; color: var(--ink);
      min-width: 140px;
    }}
    .page-tools select:focus {{ outline: 2px solid rgba(47,111,237,0.25); outline-offset: 1px; }}
    button.ghost {{
      font: inherit; padding: 8px 12px; border-radius: 10px;
      border: 1px solid var(--line); background: #fff; color: var(--ink);
      cursor: pointer; font-weight: 700;
    }}
    button.ghost:hover {{ border-color: var(--accent); color: var(--accent); }}
    .channel-section {{
      margin-bottom: 8px; padding: 20px; border-radius: 18px;
      background: #ffffff;
      color: var(--ink);
      border: 1px solid #d9e4f5;
      box-shadow: 0 10px 30px rgba(47,111,237,0.06);
    }}
    .channel-section .section-label {{
      margin: 0 0 6px; font-size: 0.7rem; font-weight: 800;
      letter-spacing: 0.12em; text-transform: uppercase; color: var(--accent);
    }}
    .block-head {{
      display: flex; justify-content: space-between; align-items: flex-start;
      gap: 8px; margin-bottom: 4px;
    }}
    .channel-section h2 {{
      margin: 0; font-family: "DM Sans", "Noto Sans JP", sans-serif; font-size: 1.4rem; color: #152033;
      padding-left: 12px; border-left: 4px solid #2f6fed;
    }}
    .channel-section .sub {{
      margin: 0 0 14px; color: var(--muted); font-size: 0.9rem; line-height: 1.5;
    }}
    .chan-list {{
      display: flex; flex-direction: column; gap: 8px;
    }}
    .chan-row {{
      display: grid;
      grid-template-columns: minmax(7.5rem, 9.5rem) 1fr 3.2rem;
      align-items: center; gap: 12px; min-height: 30px;
    }}
    @media (max-width: 560px) {{
      .chan-row {{
        grid-template-columns: minmax(5.5rem, 7rem) 1fr 2.8rem; gap: 8px;
      }}
    }}
    .chan-name {{
      font-size: 0.82rem; font-weight: 700; color: var(--ink);
      white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }}
    .chan-pct {{
      font-family: "DM Sans", "Noto Sans JP", sans-serif;
      font-size: 0.95rem; font-weight: 800; letter-spacing: -0.02em;
      font-variant-numeric: tabular-nums; text-align: right; color: var(--ink);
    }}
    .bar {{
      height: 10px; background: #eef2f8; border-radius: 99px; overflow: hidden;
    }}
    .bar i {{
      display: block; height: 100%; border-radius: 99px; min-width: 2px;
    }}
    .chan-teal .bar i {{ background: #0d9488; }}
    .chan-slate .bar i {{ background: #64748b; }}
    .chan-amber .bar i {{ background: #d97706; }}
    .chan-rose .bar i {{ background: #e11d48; }}
    .chan-blue .bar i {{ background: #2f6fed; }}
    .chan-indigo .bar i {{ background: #6366f1; }}
    .chan-sky .bar i {{ background: #0ea5e9; }}
    .chan-violet .bar i {{ background: #8b5cf6; }}
    .chan-lime .bar i {{ background: #65a30d; }}
    .chan-gray .bar i {{ background: #94a3b8; }}

    .section-head {{
      display: flex; justify-content: space-between; align-items: end;
      gap: 12px; margin: 0 0 12px;
    }}
    .section-head h2 {{
      margin: 0; font-family: "DM Sans", "Noto Sans JP", sans-serif; font-size: 1.35rem; color: #152033;
      padding-left: 12px; border-left: 4px solid var(--accent);
    }}
    .kpi-business .section-head h2 {{ border-left-color: #5b6b86; }}
    .kpi-digital .section-head h2 {{ border-left-color: #2f6fed; }}
    .kpi-events .section-head h2 {{ border-left-color: #2f6fed; }}
    .section-head p {{ margin: 0; color: var(--muted); font-size: 0.88rem; }}

    .grid {{
      display: grid;
      gap: 12px; margin-bottom: 0;
    }}
    .grid-digital {{
      grid-template-columns: repeat(3, minmax(0, 1fr));
    }}
    .grid-business {{
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }}
    @media (max-width: 900px) {{
      .grid-digital {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    }}
    @media (max-width: 640px) {{
      .grid-digital, .grid-business {{ grid-template-columns: 1fr; }}
    }}
    .card {{ padding: 15px; }}
    .card:hover {{ border-color: #cfd9ea; }}
    .k {{
      display: flex; justify-content: space-between; align-items: center; gap: 8px;
      font-size: 0.74rem; color: var(--muted); font-weight: 700; margin-bottom: 8px;
    }}
    .k-right {{ display: inline-flex; align-items: center; gap: 6px; flex-shrink: 0; }}
    .kind {{
      font-size: 0.64rem; font-weight: 800; letter-spacing: 0.04em;
      padding: 3px 7px; border-radius: 999px; border: 1px solid #d9e4f5;
      background: var(--accent-soft); color: #2f6fed;
    }}
    .kind-business {{
      background: #eef1f5; color: var(--business); border-color: #d8dee8;
    }}
    .help-btn {{
      width: 22px; height: 22px; border-radius: 999px; border: 1px solid var(--line);
      background: #fff; color: var(--accent); font-size: 0.75rem; font-weight: 800;
      cursor: pointer; line-height: 1; padding: 0;
    }}
    .help-btn:hover {{ background: var(--accent-soft); border-color: #bfd2f8; }}
    .value-row {{
      display: flex; align-items: baseline; justify-content: space-between; gap: 8px;
      margin-bottom: 8px;
    }}
    .card .v {{
      font-family: "DM Sans", "Noto Sans JP", sans-serif; font-size: 1.65rem; font-weight: 700;
      letter-spacing: -0.02em; line-height: 1.1; font-variant-numeric: tabular-nums;
      color: #152033;
    }}
    .bench-icon {{
      display: inline-flex; align-items: center; justify-content: center;
      width: 28px; height: 28px; border-radius: 8px;
      font-size: 0.85rem; line-height: 1; flex-shrink: 0;
    }}
    .bench-up {{
      color: #1d4ed8; background: #e8f0ff; border: 1px solid #c9dbff;
    }}
    .bench-mid {{
      color: #64748b; background: #f1f5f9; border: 1px solid #e2e8f0;
    }}
    .bench-down {{
      color: #475569; background: #eef1f5; border: 1px solid #d8dee8;
    }}
    .card .d {{ font-size: 0.82rem; color: var(--muted); line-height: 1.4; }}
    .bench {{
      display: flex; justify-content: space-between; align-items: center;
      gap: 8px; margin-top: 12px; padding: 8px 10px;
      border-radius: 10px; font-size: 0.8rem; border: 1px solid transparent;
    }}
    .bench-label {{ font-weight: 800; letter-spacing: 0.02em; }}
    .bench-num {{
      font-weight: 800; font-variant-numeric: tabular-nums;
      font-family: "DM Sans", "Noto Sans JP", sans-serif; font-size: 1.02rem;
    }}
    .tone-sky {{ background: #e8f6fc; border-color: #b9e3f5; color: #0b6e99; }}
    .tone-sky .bench-num {{ color: #08658d; }}
    .tone-blue {{ background: #eaf1ff; border-color: #c5d7ff; color: #1d4ed8; }}
    .tone-blue .bench-num {{ color: #1e40af; }}
    .tone-indigo {{ background: #eef0ff; border-color: #cdd3ff; color: #4338ca; }}
    .tone-indigo .bench-num {{ color: #3730a3; }}
    .tone-teal {{ background: #e7f7f3; border-color: #b7e5d8; color: #0f766e; }}
    .tone-teal .bench-num {{ color: #0d5f59; }}
    .tone-amber {{ background: #fff6e5; border-color: #f5d9a6; color: #b45309; }}
    .tone-amber .bench-num {{ color: #92400e; }}

    .event-cats {{ display: flex; flex-direction: column; gap: 18px; margin-top: 4px; }}
    .event-cat-title {{
      margin: 0 0 10px; font-size: 0.82rem; font-weight: 800; letter-spacing: 0.06em;
      text-transform: uppercase; color: #1e40af;
      display: inline-flex; align-items: center; gap: 8px;
      padding: 6px 10px; border-radius: 8px; background: #eaf1ff; border: 1px solid #d9e4f5;
    }}
    .event-cat-title::before {{
      content: ""; width: 6px; height: 6px; border-radius: 99px; background: #2f6fed;
    }}
    .event-list {{
      display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px;
    }}
    @media (max-width: 700px) {{
      .event-list {{ grid-template-columns: 1fr; }}
    }}
    .event-row {{
      display: flex; justify-content: space-between; align-items: center; gap: 16px;
      padding: 14px 16px; border: 1px solid var(--line); border-radius: 12px; background: #fff;
      box-shadow: var(--shadow);
    }}
    .section-head .k-right {{ margin-bottom: 2px; }}
    .kpi-block {{ margin-bottom: 28px; }}

    .event-row.is-primary {{
      border-color: #bfd2f8; background: var(--accent-soft);
    }}
    .event-main {{ min-width: 0; flex: 1; }}
    .event-name {{ display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 4px; }}
    .event-name code {{
      font-family: "DM Sans", ui-monospace, monospace;
      font-size: 0.92rem; font-weight: 700; color: #152033;
    }}
    .event-desc {{
      margin: 0; color: var(--muted); font-size: 0.9rem; line-height: 1.45;
    }}
    .event-tag {{
      font-size: 0.68rem; font-weight: 800; letter-spacing: 0.04em;
      padding: 2px 7px; border-radius: 999px; background: #2f6fed; color: #fff;
    }}
    .event-count {{
      font-family: "DM Sans", "Noto Sans JP", sans-serif; font-size: 1.35rem; font-weight: 700;
      font-variant-numeric: tabular-nums; color: #152033; flex-shrink: 0;
    }}
    .event-count::after {{
      content: " 件"; font-size: 0.72rem; font-family: "Noto Sans JP", "DM Sans", sans-serif;
      font-weight: 700; color: var(--muted); margin-left: 2px;
    }}
    footer {{ margin-top: 20px; color: var(--muted); font-size: 0.84rem; }}
    .notes {{ margin: 0; padding-left: 1.1rem; line-height: 1.65; }}
    .notes li {{ margin-bottom: 0.45rem; }}

    .help-dialog {{
      border: none; border-radius: 16px; padding: 0;
      max-width: min(440px, calc(100vw - 24px));
      box-shadow: 0 24px 80px rgba(21,32,51,0.18);
    }}
    .help-dialog::backdrop {{ background: rgba(21,32,51,0.28); }}
    .help-sheet {{ margin: 0; padding: 18px; }}
    .help-sheet header {{
      display: flex; justify-content: space-between; gap: 12px; align-items: flex-start;
      margin-bottom: 12px;
    }}
    .help-sheet h3 {{
      margin: 0; font-family: "DM Sans", "Noto Sans JP", sans-serif; font-size: 1.18rem; line-height: 1.35;
      color: #152033;
    }}
    .help-kind {{
      margin: 0 0 4px; font-size: 0.72rem; font-weight: 800; letter-spacing: 0.06em; color: var(--accent);
    }}
    .help-close {{
      width: 32px; height: 32px; border: 1px solid var(--line); border-radius: 10px;
      background: #fff; font-size: 1.2rem; cursor: pointer; line-height: 1; color: var(--muted);
    }}
    .help-sheet section {{
      margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--line);
    }}
    .help-sheet h4 {{
      margin: 0 0 6px; font-size: 0.74rem; letter-spacing: 0.06em;
      text-transform: uppercase; color: var(--muted);
    }}
    .help-sheet p {{ margin: 0; line-height: 1.65; font-size: 0.94rem; }}
    .help-sheet .formula {{
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 0.86rem;
      background: var(--soft); padding: 10px 12px; border-radius: 10px; color: #4a5d7a;
    }}
  </style>
</head>
<body>
  <main>
    <div class="topnav">
      <span>
        <a href="/">← 業界一覧</a>
        · <a href="/builder">カスタムビルダー</a>
        · <a href="/connect">GA4接続</a>
      </span>
      <div class="page-tools">
        <form method="get" action="/{escape(industry)}" id="period-form">
          <label>
            期間
            <select name="period" onchange="this.form.submit()">{period_opts}</select>
          </label>
        </form>
        <button type="button" class="ghost" data-help="guide">見方</button>
      </div>
    </div>
    <p class="nav-sub">他パック: {other_links}</p>

    <p class="badge">{"Industry KPI Pack · GA4接続" if live else "Industry KPI Pack · MVP · デモデータ"}{" · " + escape(property_name) if property_name else ""}</p>
    {"<p class='banner-live'>デジタル・イベント・流入は GA4 実データ。業務KPIは未連携（DB連携後に表示）です。</p>" if live else ""}
    {f"<p class='banner-err'>GA4取得エラー: {escape(live_error)}</p>" if live_error else ""}
    <h1 class="brand">{escape(ind["label"])}</h1>
    <p class="lead">
      {escape(ind["blurb"])}
      業界目安との位置はカード内の数値とアイコンで確認。説明は「見方」から。
    </p>

    <div class="kpi-block kpi-business">
      <div class="section-head">
        <div>
          <h2>業務KPI</h2>
          <p>{"会員DB・売上はまだ未接続。GA4には含まれません。" if live else "会員DB・売上など社内データ。デジタル数値とズレることがあります。"}</p>
        </div>
        <span class="k-right">{kind_badge("business")}</span>
      </div>
      <section class="grid grid-business">
        {_business_cards_html(
            live=live,
            industry=industry,
            data=data,
            free_members=free_members,
            paid_rate=paid_rate,
            churn_rate=churn_rate,
            arpu=arpu,
            arppu=arppu,
            paid_rate_arrow=paid_rate_arrow,
            churn_rate_arrow=churn_rate_arrow,
        )}
      </section>
    </div>

    <div class="kpi-block kpi-digital">
      <div class="section-head">
        <div>
          <h2>デジタルKPI</h2>
          <p>GAなどサイト計測 · ▲上 ●標準 ▼下 · 色付き「業界目安」がパック標準値</p>
        </div>
        <span class="k-right">{kind_badge("digital")}</span>
      </div>
      <section class="grid grid-digital">
        <article class="card panel">
          {title_row("期間 UU", "uu")}
          <div class="value-row"><div class="v">{fmt_int(data["uu"])}</div></div>
          <div class="d">{fmt_delta(data["uu_delta"])} vs 前期間 · ブラウザ単位</div>
        </article>
        <article class="card panel">
          {title_row("セッション", "sessions")}
          <div class="value-row"><div class="v">{fmt_int(data["sessions"])}</div></div>
          <div class="d">{fmt_delta(data["sessions_delta"])} vs 前期間 · 訪問回数</div>
        </article>
        <article class="card panel">
          {title_row("セッション / UU", "sessions_per_uu")}
          <div class="value-row">
            <div class="v">{sessions_per_uu}</div>
            {arrow_html(spu_arrow)}
          </div>
          <div class="d">1ブラウザあたり訪問回数</div>
          {bench_row(industry, "sessions_per_uu")}
        </article>
        <article class="card panel">
          {title_row("ページビュー", "pageviews")}
          <div class="value-row"><div class="v">{fmt_int(data["pageviews"])}</div></div>
          <div class="d">表示回数の合計</div>
        </article>
        <article class="card panel">
          {title_row("PV / UU", "pages_per_uu")}
          <div class="value-row">
            <div class="v">{pages_per_uu}</div>
            {arrow_html(ppu_arrow)}
          </div>
          <div class="d">1ブラウザあたり閲覧ページ</div>
          {bench_row(industry, "pages_per_uu")}
        </article>
        <article class="card panel">
          {title_row("新規 / 再訪", "new_return")}
          <div class="value-row">
            <div class="v">{new_pct}% / {ret_pct}%</div>
            {arrow_html(new_arrow)}
          </div>
          <div class="d">{fmt_int(data["new_users"])} 新規 · {fmt_int(data["returning_users"])} 再訪</div>
          {bench_row(industry, "new_pct")}
        </article>
        <article class="card panel">
          {title_row("エンゲージメント率", "engaged")}
          <div class="value-row">
            <div class="v">{data["engaged_rate"]}%</div>
            {arrow_html(engaged_arrow)}
          </div>
          {bench_row(industry, "engaged_rate")}
        </article>
        <article class="card panel">
          {title_row("すぐ離脱に近い率", "bounce_rate")}
          <div class="value-row">
            <div class="v">{bounce_rate}%</div>
            {arrow_html(bounce_arrow)}
          </div>
          <div class="d">100 − エンゲージメント率</div>
          {bench_row(industry, "bounce_rate")}
        </article>
        <article class="card panel">
          {title_row("平均エンゲージ時間", "avg_time")}
          <div class="value-row"><div class="v">{escape(str(data["avg_time"]))}</div></div>
          <div class="d">分:秒 · 意識を向けていた時間</div>
        </article>
        <article class="card panel">
          {title_row("ページ / セッション", "pages_session")}
          <div class="value-row">
            <div class="v">{data["pages_session"]}</div>
            {arrow_html(pages_arrow)}
          </div>
          {bench_row(industry, "pages_session")}
        </article>
        <article class="card panel">
          {title_row(signup_label, "signups")}
          <div class="value-row"><div class="v">{fmt_int(data["signups"])}</div></div>
          <div class="d">件数 · {escape(primary)}</div>
        </article>
        <article class="card panel">
          {title_row("登録CVR", "signup_cvr")}
          <div class="value-row">
            <div class="v">{data["signup_rate"]}%</div>
            {arrow_html(signup_arrow)}
          </div>
          {bench_row(industry, "signup_rate")}
        </article>
        <article class="card panel">
          {title_row("有料開始", "pay_start")}
          <div class="value-row"><div class="v">{fmt_int(data["pay_start"])}</div></div>
          <div class="d">決済に進もうとした回数</div>
        </article>
        <article class="card panel">
          {title_row("登録→有料開始率", "signup_to_pay")}
          <div class="value-row">
            <div class="v">{signup_to_pay}%</div>
            {arrow_html(stp_arrow)}
          </div>
          <div class="d">pay_start ÷ 主転換</div>
          {bench_row(industry, "signup_to_pay")}
        </article>
        <article class="card panel">
          {title_row("有料完了 / 決済CVR", "pay_success")}
          <div class="value-row">
            <div class="v">{fmt_int(data["pay_success"])}</div>
            {arrow_html(pay_arrow)}
          </div>
          <div class="d">決済CVR {data["pay_cvr"]}%</div>
          {bench_row(industry, "pay_cvr")}
        </article>
      </section>
    </div>

    <div class="kpi-block kpi-events">
      <div class="section-head">
        <div>
          <h2>イベント</h2>
          <p>6イベント · カテゴリ別 · 1行2件 · 説明と期間中の件数</p>
        </div>
        <span class="k-right">{kind_badge("digital")}{help_button("events_section")}</span>
      </div>
      <div class="event-cats">{event_categories_html}</div>
    </div>

    <section class="channel-section" aria-labelledby="channel-title">
      <p class="section-label">Traffic</p>
      <div class="block-head">
        <h2 id="channel-title">流入チャネル</h2>
        <span class="k-right">{kind_badge("digital")}{help_button("channels")}</span>
      </div>
      <p class="sub">KPI・イベントのあと、入り口の内訳を確認。最大10チャネル想定の横棒グラフです。</p>
      <div class="chan-list">{channel_rows}</div>
    </section>

    <footer>{BRAND_NAME} · demo · /{escape(industry)}</footer>
  </main>

  {help_dialogs_html(notes)}

  <script>
    document.querySelectorAll("[data-help]").forEach((btn) => {{
      btn.addEventListener("click", () => {{
        const id = btn.getAttribute("data-help");
        const dialog = document.getElementById("help-" + id);
        if (dialog) dialog.showModal();
      }});
    }});
    document.querySelectorAll("[data-help-dialog]").forEach((dialog) => {{
      dialog.addEventListener("click", (e) => {{
        if (e.target === dialog) dialog.close();
      }});
    }});
  </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(render_home())


# Short-lived cache so switching sample packs does not re-hit GA4 every click
_LIVE_PACK_CACHE: dict[str, tuple[float, dict[str, Any], str]] = {}
_LIVE_PACK_TTL_SEC = 60.0


def _live_pack(request: Request, industry: str, period: Period) -> tuple[dict[str, Any], bool, str | None, str]:
    """Optional GA4 overlay for packs (unused by dense sample routes; kept for tooling)."""
    base = dict(DEMO[industry][period])
    pack_events = list(INDUSTRIES[industry].get("events") or [])
    primary = str(INDUSTRIES[industry].get("primary_event") or (pack_events[0] if pack_events else ""))

    # Sample-pack browsing: skip GA4 entirely when not connected (keeps nav snappy)
    info = connection_info(request.session)
    if not info:
        return base, False, None, ""

    saved = saved_events(request.session)
    cache_key = (
        f"{info['property_id']}|{period}|{industry}|"
        f"{','.join(saved['events']) if saved else 'discover'}|"
        f"{saved.get('primary') if saved else primary}"
    )
    now = time.time()
    hit = _LIVE_PACK_CACHE.get(cache_key)
    if hit and now - hit[0] < _LIVE_PACK_TTL_SEC:
        cached_overlay, prop = hit[1], hit[2]
        merged = dict(base)
        merged.update(cached_overlay)
        return merged, True, None, prop

    if saved:
        events = list(saved["events"])
        primary = str(saved.get("primary") or primary)
    else:
        discovered, _ = discover_event_names(request.session, period=period, limit=200)
        if discovered:
            events = [e["name"] for e in discovered]
            if primary not in events:
                primary = events[0] if events else primary
        else:
            events = pack_events
    overlay, err = fetch_pack_overlay(
        request.session,
        period=period,
        event_names=events,
        primary_event=primary,
    )
    if not overlay:
        return base, False, err, ""
    prop = str(overlay.pop("_ga4_property", "") or "")
    overlay.pop("_ga4_label", None)
    overlay.pop("_ga4_property_id", None)
    # Live: replace event_counts with GA4 (don't keep fake pack events)
    stash = dict(overlay)
    stash["_live_events"] = events
    stash["_live_primary"] = primary
    _LIVE_PACK_CACHE[cache_key] = (now, stash, prop)
    base.update(stash)
    return base, True, None, prop


@app.get("/builder", response_class=HTMLResponse)
def page_builder(request: Request):
    widgets, prop_name, live_error = build_live_builder_widgets(
        request.session, period="28d"
    )
    return HTMLResponse(
        render_builder(
            property_name=prop_name,
            live_error=live_error,
            widgets=widgets or None,
            locale=get_locale(request.session),
        )
    )


def _nav_extras(request: Request) -> dict[str, Any]:
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
    pack = request.session.get("benchmark_pack")
    benchmark_pack = str(pack) if isinstance(pack, str) and pack in INDUSTRIES else ""
    return {
        "connected": connected,
        "pack_links": pack_links(),
        "pack_groups": packs_by_category(),
        "benchmark_pack": benchmark_pack,
    }


@app.get("/sample", response_class=HTMLResponse)
def page_sample_dense():
    # Dense board template — default vertical is 人事
    return RedirectResponse("/hr", status_code=302)


@app.get("/settings", response_class=HTMLResponse)
def page_settings_get(request: Request, saved: int = Query(default=0)):
    extras = _nav_extras(request)
    loc = get_locale(request.session)
    return HTMLResponse(
        render_settings_page(
            locale=loc,
            saved=bool(saved),
            pack_links=extras["pack_links"],
            pack_groups=extras["pack_groups"],
            connected=extras["connected"],
            back_href="/hr",
        )
    )


@app.post("/settings")
async def page_settings_post(request: Request):
    form = await request.form()
    set_locale(request.session, str(form.get("locale") or ""))
    return RedirectResponse("/settings?saved=1", status_code=303)


@app.get("/live", response_class=HTMLResponse)
def page_live(request: Request, period: str = Query(default="28d")):
    """Connected GA4 board (separate menu category from sample packs)."""
    if period not in PERIODS:
        period = "28d"
    extras = _nav_extras(request)
    if not extras["connected"]:
        return RedirectResponse("/connect", status_code=302)
    # Industry pack = 業界目安 source only (not DEMO revenue as live)
    pack_slug = extras.get("benchmark_pack") or ""
    if not pack_slug or pack_slug not in INDUSTRIES:
        return RedirectResponse("/connect", status_code=302)
    data, live, err, prop = _live_pack(request, pack_slug, period)  # type: ignore[arg-type]
    loc = get_locale(request.session)
    label = extras["connected"]["name"]
    pack_label = pack_text(
        pack_slug, "label", loc, str(INDUSTRIES[pack_slug]["label"])
    )
    is_demo = bool(extras["connected"].get("demo"))
    if is_demo:
        # Demo connect: pack sample site numbers, clearly labelled (business stays —)
        note = t("live.note.demo_mode", loc, pack=pack_label)
    elif live:
        note = t("live.note.ok", loc, pack=pack_label)
    elif err:
        note = t("live.note.err", loc, pack=pack_label)
    else:
        note = t("live.note.demo", loc, pack=pack_label)
    return HTMLResponse(
        render_sample_dense(
            industry=pack_slug,
            period=period,
            data=data,
            ind=INDUSTRIES[pack_slug],
            benches_raw=BENCHMARKS[pack_slug],
            property_name=prop or label,
            industry_label=label,
            industry_note=note,
            pack_links=extras["pack_links"],
            pack_groups=extras["pack_groups"],
            nav_active="live",
            connected=extras["connected"],
            locale=loc,
            board_kind="live",
        )
    )


@app.get("/b2c_membership")
def legacy_b2c():
    return RedirectResponse("/b2c", status_code=302)


@app.get("/content_media")
def legacy_content():
    return RedirectResponse("/content", status_code=302)


@app.get("/{slug}", response_class=HTMLResponse)
def page_industry(request: Request, slug: str, period: str = Query(default="28d")):
    """Dense board for industry sample packs (DEMO only — live is /live)."""
    if slug not in INDUSTRIES:
        return HTMLResponse("<h1>Not Found</h1>", status_code=404)
    if period not in PERIODS:
        period = "28d"
    extras = _nav_extras(request)
    data = dict(DEMO[slug][period])
    return HTMLResponse(
        render_sample_dense(
            industry=slug,
            period=period,
            data=data,
            ind=INDUSTRIES[slug],
            benches_raw=BENCHMARKS[slug],
            property_name="",
            pack_links=extras["pack_links"],
            pack_groups=extras["pack_groups"],
            nav_active=f"pack:{slug}",
            connected=extras["connected"],
            locale=get_locale(request.session),
        )
    )
