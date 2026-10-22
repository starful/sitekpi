"""Custom dashboard builder — drag from palette to canvas (localStorage)."""

from __future__ import annotations

import json
from html import escape
from typing import Any

from sitekpi.views.branding import brand_head_links, brand_logo_css
from sitekpi.views.layout import mobile_bar_html, rail_css, rail_js
from sitekpi.i18n import html_lang, normalize_locale, t

# Sample values are demo-only; real wiring comes later.
WIDGETS: list[dict[str, Any]] = [
    # business
    {"id": "members_db", "group": "business", "label": "会員数（DB）", "value": "41,934", "hint": "有効会員の累計"},
    {"id": "paid_members", "group": "business", "label": "有料会員数（DB）", "value": "3,280", "hint": "有料プラン中"},
    {"id": "free_members", "group": "business", "label": "無料会員数（DB）", "value": "38,654", "hint": "会員 − 有料"},
    {"id": "paid_rate", "group": "business", "label": "有料化率", "value": "7.8%", "hint": "有料 ÷ 会員"},
    {"id": "new_paid", "group": "business", "label": "新規有料（期間）", "value": "312", "hint": "初回課金"},
    {"id": "churn", "group": "business", "label": "退会 / 解約", "value": "168", "hint": "期間中件数"},
    {"id": "churn_rate", "group": "business", "label": "解約率", "value": "0.40%", "hint": "退会 ÷ 会員"},
    {"id": "revenue", "group": "business", "label": "売上（期間）", "value": "¥7,240,000", "hint": "課金売上"},
    {"id": "arpu", "group": "business", "label": "ARPU", "value": "¥173", "hint": "売上 ÷ 全会員"},
    {"id": "arppu", "group": "business", "label": "ARPPU", "value": "¥2,207", "hint": "売上 ÷ 有料"},
    # digital
    {"id": "uu", "group": "digital", "label": "期間 UU", "value": "38,920", "hint": "ブラウザ単位"},
    {"id": "sessions", "group": "digital", "label": "セッション", "value": "54,210", "hint": "訪問回数"},
    {"id": "sessions_per_uu", "group": "digital", "label": "セッション / UU", "value": "1.39", "hint": "再訪の目安"},
    {"id": "pageviews", "group": "digital", "label": "ページビュー", "value": "140,946", "hint": "表示回数"},
    {"id": "pages_per_uu", "group": "digital", "label": "PV / UU", "value": "3.6", "hint": "閲覧の深さ"},
    {"id": "new_return", "group": "digital", "label": "新規 / 再訪", "value": "39.1% / 60.9%", "hint": "UUの内訳"},
    {"id": "engaged", "group": "digital", "label": "エンゲージメント率", "value": "58.6%", "hint": "見た訪問の割合"},
    {"id": "bounce_rate", "group": "digital", "label": "すぐ離脱に近い率", "value": "41.4%", "hint": "100−Engaged"},
    {"id": "avg_time", "group": "digital", "label": "平均エンゲージ時間", "value": "1:52", "hint": "分:秒"},
    {"id": "pages_session", "group": "digital", "label": "ページ / セッション", "value": "2.6", "hint": "1訪問のページ数"},
    {"id": "signups", "group": "digital", "label": "新規会員登録", "value": "1,486", "hint": "主転換件数"},
    {"id": "signup_cvr", "group": "digital", "label": "登録CVR", "value": "3.8%", "hint": "登録 ÷ UU"},
    {"id": "pay_start", "group": "digital", "label": "有料開始", "value": "702", "hint": "決済に進む"},
    {"id": "signup_to_pay", "group": "digital", "label": "登録→有料開始率", "value": "47.2%", "hint": "pay_start ÷ 登録"},
    {"id": "pay_success", "group": "digital", "label": "有料完了 / 決済CVR", "value": "341 · 48.6%", "hint": "完了と決済率"},
    # events
    {"id": "ev_sign_up", "group": "event", "label": "sign_up", "value": "1,486", "hint": "会員登録完了"},
    {"id": "ev_login", "group": "event", "label": "login", "value": "24,880", "hint": "ログイン成功"},
    {"id": "ev_view_pricing", "group": "event", "label": "view_pricing", "value": "3,420", "hint": "料金ページ"},
    {"id": "ev_trial_start", "group": "event", "label": "trial_start", "value": "780", "hint": "トライアル開始"},
    {"id": "ev_pay_start", "group": "event", "label": "pay_start", "value": "702", "hint": "決済開始"},
    {"id": "ev_pay_success", "group": "event", "label": "pay_success", "value": "341", "hint": "支払い完了"},
    # traffic
    {"id": "ch_organic", "group": "traffic", "label": "Organic Search", "value": "26%", "hint": "流入構成"},
    {"id": "ch_direct", "group": "traffic", "label": "Direct", "value": "16%", "hint": "流入構成"},
    {"id": "ch_paid_search", "group": "traffic", "label": "Paid Search", "value": "15%", "hint": "流入構成"},
    {"id": "ch_paid_social", "group": "traffic", "label": "Paid Social", "value": "13%", "hint": "流入構成"},
    {"id": "ch_organic_social", "group": "traffic", "label": "Organic Social", "value": "9%", "hint": "流入構成"},
]

GROUP_META = {
    "layout": {"label": "レイアウト", "tone": "lay"},
    "business": {"label": "業務KPI", "tone": "biz"},
    "digital": {"label": "デジタルKPI", "tone": "dig"},
    "event": {"label": "イベント", "tone": "evt"},
    "traffic": {"label": "流入チャネル", "tone": "trf"},
}

CARD_COLORS = [
    {"id": "default", "label": "白"},
    {"id": "sky", "label": "空"},
    {"id": "blue", "label": "青"},
    {"id": "teal", "label": "緑"},
    {"id": "amber", "label": "琥珀"},
    {"id": "rose", "label": "薔薇"},
    {"id": "indigo", "label": "藍"},
    {"id": "slate", "label": "灰"},
]


def _group_header(gid: str, label: str, tone: str, count: int) -> str:
    return (
        f'<button type="button" class="pal-group-title tone-{escape(tone)}" '
        f'data-toggle-group="{escape(gid)}" aria-expanded="false">'
        f'<span class="chev" aria-hidden="true">▶</span>'
        f'<span class="pal-group-name">{escape(label)}</span>'
        f'<span class="pal-count">{count}</span>'
        f"</button>"
    )


def _value_is_empty(val: Any) -> bool:
    s = str(val if val is not None else "").strip()
    return s in ("", "—", "-", "–", "N/A", "n/a")


def _palette_item_html(w: dict[str, Any]) -> str:
    val = w.get("value")
    empty = _value_is_empty(val)
    display = "—" if empty else str(val)
    state = "no-value" if empty else "has-value"
    return f"""
            <div class="pal-item {state}" data-type="widget" data-id="{escape(w["id"])}"
                 data-group="{escape(w["group"])}" data-has-value="{"0" if empty else "1"}">
              <div class="pal-top">
                <span class="pal-label">{escape(w["label"])}</span>
                <span class="pal-value" title="期間中の値">{escape(display)}</span>
              </div>
              <span class="pal-hint">{escape(w.get("hint") or "")}</span>
            </div>
            """


def _palette_html(widgets: list[dict[str, Any]] | None = None) -> str:
    source = widgets if widgets is not None else WIDGETS
    blocks: list[str] = []

    # Layout tools first (category title — unlimited clones)
    blocks.append(
        f"""
        <div class="pal-group" data-group-key="layout">
          {_group_header("layout", "レイアウト", "lay", 1)}
          <div class="pal-list" data-palette="layout">
            <div class="pal-item pal-section" data-type="section" data-id="__section__">
              <span class="pal-label">＋ カテゴリ見出し</span>
              <span class="pal-hint">何度でも追加可 · 右で名前を編集</span>
            </div>
          </div>
        </div>
        """
    )

    for gid, meta in GROUP_META.items():
        if gid == "layout":
            continue
        items = [w for w in source if w["group"] == gid]
        cards = "".join(_palette_item_html(w) for w in items)
        # Expand digital/event when live (many items) — still start collapsed
        blocks.append(
            f"""
            <div class="pal-group is-collapsed" data-group-key="{escape(gid)}">
              {_group_header(gid, meta["label"], meta["tone"], len(items))}
              <div class="pal-list" data-palette="{escape(gid)}">{cards}</div>
            </div>
            """
        )
    return "".join(blocks)


def render_builder(
    *,
    live_values: dict[str, str] | None = None,
    property_name: str = "",
    live_error: str | None = None,
    widgets: list[dict[str, Any]] | None = None,
    locale: str = "ja",
    nav_html: str = "",
) -> str:
    loc = normalize_locale(locale)
    source = widgets if widgets is not None else WIDGETS
    catalog: dict[str, Any] = {w["id"]: dict(w) for w in source}
    # Keep legacy sample ids so older localStorage boards still resolve
    for w in WIDGETS:
        catalog.setdefault(w["id"], dict(w))
    if live_values:
        for wid, val in live_values.items():
            if wid in catalog:
                catalog[wid]["value"] = val
                hint = catalog[wid].get("hint") or ""
                if "GA4" not in hint:
                    catalog[wid]["hint"] = (hint + " · GA4").strip(" ·")
    if property_name:
        for wid, meta in catalog.items():
            if meta.get("group") == "business":
                meta["value"] = "—"
                meta["hint"] = t("builder.biz_hint", loc)
    catalog_json = json.dumps(catalog, ensure_ascii=False)
    colors_json = json.dumps(CARD_COLORS, ensure_ascii=False)
    n_digital = sum(1 for w in source if w.get("group") == "digital")
    n_event = sum(1 for w in source if w.get("group") == "event")
    live_banner = ""
    if property_name:
        live_banner = (
            f'<p class="live-banner">'
            f'{escape(t("builder.live_on", loc, name=property_name, n_digital=n_digital, n_event=n_event))}'
            f"</p>"
        )
    elif live_error:
        live_banner = (
            f'<p class="live-err">{escape(t("builder.live_err", loc, err=live_error))}</p>'
        )
    else:
        live_banner = (
            f'<p class="live-hint"><a href="/connect">{escape(t("builder.nav.connect", loc))}</a>'
            f" — {escape(t('builder.live_hint', loc))}</p>"
        )
    return f"""<!doctype html>
<html lang="{escape(html_lang(loc))}">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>SiteKPI · {escape(t("builder.title", loc))}</title>
  {brand_head_links()}
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;500;600;700&family=Noto+Sans+JP:wght@400;500;700;800&display=swap" rel="stylesheet" />
  <script src="https://cdn.jsdelivr.net/npm/sortablejs@1.15.6/Sortable.min.js"></script>
  <style>
    {brand_logo_css()}
    :root {{
      --bg: #f6f8fc;
      --ink: #1c2430;
      --muted: #6b7788;
      --line: #e6eaf0;
      --accent: #2f6fed;
      --card: #ffffff;
      --shadow: 0 8px 24px rgba(21,32,51,0.06);
      --font-ui: "IBM Plex Sans JP", "Noto Sans JP", sans-serif;
      --font-num: "DM Sans", "IBM Plex Sans JP", sans-serif;
      --rail-w: 268px;
    }}
    {rail_css()}
    .main {{ min-width: 0; }}
    .page-title {{ margin: 0; font-size: 1.05rem; font-weight: 800; color: #152033; }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0; min-height: 100vh; color: var(--ink);
      font-family: "Noto Sans JP", "DM Sans", sans-serif;
      background: var(--bg);
    }}
    .top {{
      display: flex; justify-content: space-between; align-items: center;
      gap: 12px; flex-wrap: wrap;
      padding: 14px 20px; background: #fff; border-bottom: 1px solid var(--line);
      position: sticky; top: 0; z-index: 20;
    }}
    .top-actions {{ display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }}
    button {{
      font: inherit; font-weight: 700; padding: 8px 12px; border-radius: 10px;
      border: 1px solid var(--line); background: #fff; color: var(--ink); cursor: pointer;
    }}
    button.primary {{ background: var(--accent); color: #fff; border-color: var(--accent); }}
    button.ghost:hover {{ border-color: var(--accent); color: var(--accent); }}
    .status {{ font-size: 0.82rem; color: var(--muted); min-width: 8rem; }}
    .status.ok {{ color: #0f766e; }}
    .layout {{
      display: grid;
      grid-template-columns: minmax(260px, 320px) 1fr;
      gap: 0; min-height: calc(100vh - 58px);
    }}
    @media (max-width: 900px) {{
      .layout {{ grid-template-columns: 1fr; }}
      .main > .top {{ position: static; }}
      .palette, .canvas-wrap {{ max-height: none; }}
    }}
    .palette {{
      background: #fff; border-right: 1px solid var(--line);
      padding: 16px; overflow: auto; max-height: calc(100vh - 58px);
    }}
    .palette h2 {{ margin: 0 0 6px; font-size: 1.05rem; color: #152033; }}
    .palette .sub {{
      margin: 0 0 14px; font-size: 0.85rem; color: var(--muted); line-height: 1.5;
    }}
    .search-wrap {{ margin-bottom: 12px; }}
    .search-wrap input {{
      width: 100%; font: inherit; padding: 10px 12px; border-radius: 10px;
      border: 1px solid var(--line); background: #fff; color: var(--ink);
    }}
    .search-wrap input:focus {{
      outline: 2px solid rgba(47,111,237,0.25); outline-offset: 1px; border-color: #bfd2f8;
    }}
    .search-empty {{
      display: none; margin: 8px 0 0; font-size: 0.82rem; color: var(--muted); font-weight: 700;
    }}
    .search-empty.show {{ display: block; }}
    .pal-group {{ margin-bottom: 10px; }}
    .pal-group.is-hidden {{ display: none; }}
    .pal-group.is-collapsed .pal-list {{ display: none; }}
    .pal-group-title {{
      width: 100%; margin: 0 0 8px; font: inherit; font-size: 0.72rem; font-weight: 800;
      letter-spacing: 0.06em; text-transform: uppercase;
      display: flex; align-items: center; gap: 8px;
      padding: 7px 10px; border-radius: 8px; border: none; cursor: pointer;
      text-align: left;
    }}
    .pal-group-title .chev {{
      font-size: 0.65rem; width: 0.9rem; flex-shrink: 0;
      transition: transform 0.15s ease;
    }}
    .pal-group:not(.is-collapsed) .pal-group-title .chev {{
      transform: rotate(90deg);
    }}
    .pal-group-name {{ flex: 1; min-width: 0; }}
    .pal-count {{
      font-variant-numeric: tabular-nums; opacity: 0.75;
      background: rgba(255,255,255,0.55); border-radius: 999px;
      padding: 1px 7px; font-size: 0.7rem;
    }}
    .tone-lay {{ background: #f3eefe; color: #6d28d9; }}
    .tone-biz {{ background: #eef1f5; color: #5b6b86; }}
    .tone-dig {{ background: #eaf1ff; color: #1d4ed8; }}
    .tone-evt {{ background: #eef0ff; color: #4338ca; }}
    .tone-trf {{ background: #e8f6fc; color: #0b6e99; }}
    .pal-list {{ display: flex; flex-direction: column; gap: 6px; min-height: 8px; }}
    .pal-fold-bar {{
      display: flex; gap: 6px; margin: 0 0 12px; flex-wrap: wrap;
    }}
    .pal-fold-bar button {{
      font-size: 0.75rem; padding: 5px 9px; border-radius: 8px;
    }}
    .pal-item {{
      padding: 10px 12px; border: 1px solid var(--line); border-radius: 10px;
      background: #fafbfd; cursor: grab; user-select: none;
    }}
    .pal-item.has-value {{
      border-color: #c5d7f5; background: #f7faff;
    }}
    .pal-item.no-value {{
      opacity: 0.72;
    }}
    .pal-item:active {{ cursor: grabbing; }}
    .pal-item.in-canvas {{ opacity: 0.45; }}
    .pal-item.is-hidden {{ display: none; }}
    .pal-section {{
      background: #f3eefe; border-color: #ddd0f7;
    }}
    .pal-top {{
      display: flex; align-items: baseline; justify-content: space-between;
      gap: 8px;
    }}
    .pal-label {{
      display: block; font-size: 0.86rem; font-weight: 700;
      min-width: 0; flex: 1;
    }}
    .pal-value {{
      font-family: "DM Sans", "Noto Sans JP", sans-serif;
      font-size: 0.82rem; font-weight: 800; font-variant-numeric: tabular-nums;
      color: #1d4ed8; flex-shrink: 0; max-width: 46%;
      overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
    }}
    .pal-item.no-value .pal-value {{
      color: #93a0b4; font-weight: 700;
    }}
    .pal-hint {{ display: block; font-size: 0.75rem; color: var(--muted); margin-top: 2px; }}
    .pal-filters {{
      display: flex; gap: 10px; flex-wrap: wrap; align-items: center;
      margin: 0 0 10px; font-size: 0.78rem; color: var(--muted); font-weight: 700;
    }}
    .pal-filters label {{
      display: inline-flex; align-items: center; gap: 5px; cursor: pointer;
      user-select: none;
    }}
    .pal-filters input {{ accent-color: var(--accent); }}
    .canvas-wrap {{
      padding: 20px; overflow: auto; max-height: calc(100vh - 58px);
    }}
    .canvas-head {{
      display: flex; justify-content: space-between; align-items: end;
      gap: 12px; margin-bottom: 14px; flex-wrap: wrap;
    }}
    .canvas-head h2 {{
      margin: 0; font-family: "DM Sans", "Noto Sans JP", sans-serif;
      font-size: 1.35rem; color: #152033;
    }}
    .canvas-head p {{ margin: 4px 0 0; color: var(--muted); font-size: 0.88rem; }}
    .canvas {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      min-height: 320px;
      padding: 16px;
      border: 2px dashed #cfd9ea;
      border-radius: 16px;
      background: #fff;
      align-content: start;
    }}
    @media (max-width: 1100px) {{ .canvas {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}
    @media (max-width: 640px) {{ .canvas {{ grid-template-columns: 1fr; }} }}
    .canvas.empty::before {{
      content: "左から「カテゴリ見出し」やKPIをドラッグ";
      grid-column: 1 / -1;
      text-align: center; color: #94a3b8; font-weight: 700;
      padding: 48px 12px; pointer-events: none;
    }}
    .dash-card {{
      position: relative;
      padding: 14px 14px 12px;
      border: 1px solid var(--line);
      border-radius: 12px;
      background: var(--card);
      box-shadow: var(--shadow);
      cursor: grab;
    }}
    .dash-card:active {{ cursor: grabbing; }}
    .dash-card .kind {{
      font-size: 0.64rem; font-weight: 800; letter-spacing: 0.04em;
      padding: 2px 6px; border-radius: 999px; display: inline-block; margin-bottom: 6px;
    }}
    .dash-card.g-business .kind {{ background: #eef1f5; color: #5b6b86; }}
    .dash-card.g-digital .kind {{ background: #eaf1ff; color: #1d4ed8; }}
    .dash-card.g-event .kind {{ background: #eef0ff; color: #4338ca; }}
    .dash-card.g-traffic .kind {{ background: #e8f6fc; color: #0b6e99; }}
    .dash-card .label {{
      font-size: 0.78rem; font-weight: 700; color: var(--muted); margin-bottom: 6px;
      padding-right: 28px;
    }}
    .dash-card .value {{
      font-family: "DM Sans", "Noto Sans JP", sans-serif;
      font-size: 1.35rem; font-weight: 800; letter-spacing: -0.02em;
      font-variant-numeric: tabular-nums; color: #152033;
    }}
    .dash-card .hint {{
      margin-top: 6px; font-size: 0.75rem; color: var(--muted);
    }}
    .color-row {{
      display: flex; flex-wrap: wrap; gap: 5px; margin-top: 10px;
      padding-top: 8px; border-top: 1px solid rgba(0,0,0,0.06);
    }}
    .swatch {{
      width: 18px; height: 18px; border-radius: 99px; border: 2px solid transparent;
      padding: 0; cursor: pointer; box-shadow: inset 0 0 0 1px rgba(0,0,0,0.12);
    }}
    .swatch.is-active {{ border-color: #152033; }}
    .swatch[data-color="default"] {{ background: #ffffff; }}
    .swatch[data-color="sky"] {{ background: #7dd3fc; }}
    .swatch[data-color="blue"] {{ background: #60a5fa; }}
    .swatch[data-color="teal"] {{ background: #5eead4; }}
    .swatch[data-color="amber"] {{ background: #fcd34d; }}
    .swatch[data-color="rose"] {{ background: #fda4af; }}
    .swatch[data-color="indigo"] {{ background: #a5b4fc; }}
    .swatch[data-color="slate"] {{ background: #94a3b8; }}

    .tone-default {{ background: #fff; border-color: #e6eaf0; }}
    .tone-sky {{ background: #e8f6fc; border-color: #b9e3f5; }}
    .tone-blue {{ background: #eaf1ff; border-color: #c5d7ff; }}
    .tone-teal {{ background: #e7f7f3; border-color: #b7e5d8; }}
    .tone-amber {{ background: #fff6e5; border-color: #f5d9a6; }}
    .tone-rose {{ background: #fff1f2; border-color: #fecdd3; }}
    .tone-indigo {{ background: #eef0ff; border-color: #cdd3ff; }}
    .tone-slate {{ background: #eef1f5; border-color: #d8dee8; }}

    .dash-section {{
      grid-column: 1 / -1;
      position: relative;
      display: flex; flex-wrap: wrap; align-items: center; gap: 10px;
      padding: 10px 40px 10px 14px;
      border-radius: 10px;
      border: 1px solid #d9e4f5;
      cursor: grab;
    }}
    .dash-section:active {{ cursor: grabbing; }}
    .dash-section .sec-badge {{
      flex-shrink: 0; font-size: 0.64rem; font-weight: 800; letter-spacing: 0.06em;
      text-transform: uppercase; color: #1d4ed8; background: #fff;
      border: 1px solid #c5d7ff; border-radius: 6px; padding: 3px 7px;
    }}
    .dash-section .sec-title {{
      flex: 1; min-width: 140px; font: inherit; font-size: 1.05rem; font-weight: 800;
      color: #152033; border: none; background: transparent; padding: 4px 0;
      border-bottom: 1px dashed transparent;
    }}
    .dash-section .sec-title:hover,
    .dash-section .sec-title:focus {{
      outline: none; border-bottom-color: #bfd2f8;
    }}
    .dash-section .color-row {{
      width: 100%; margin-top: 4px; border-top: none; padding-top: 0;
    }}
    .rm {{
      position: absolute; top: 8px; right: 8px;
      width: 24px; height: 24px; border-radius: 999px;
      border: 1px solid var(--line); background: #fff;
      color: var(--muted); font-size: 0.85rem; line-height: 1;
      padding: 0; cursor: pointer;
    }}
    .rm:hover {{ color: #b91c1c; border-color: #fecaca; }}
    .dash-section .rm {{ top: 10px; }}
    .sortable-ghost {{ opacity: 0.35; }}
    .sortable-chosen {{ box-shadow: 0 12px 28px rgba(47,111,237,0.18); }}
    .live-banner {{
      margin: 0; padding: 10px 20px; background: #e7f7f3; border-bottom: 1px solid #b7e5d8;
      color: #0f766e; font-size: 0.88rem; font-weight: 700;
    }}
    .live-err {{
      margin: 0; padding: 10px 20px; background: #fff1f2; border-bottom: 1px solid #fecdd3;
      color: #9f1239; font-size: 0.88rem;
    }}
    .live-hint {{
      margin: 0; padding: 10px 20px; background: #f8fafc; border-bottom: 1px solid var(--line);
      color: var(--muted); font-size: 0.88rem;
    }}
    .live-hint a {{ color: var(--accent); font-weight: 700; text-decoration: none; }}
  </style>
</head>
<body>
  {mobile_bar_html(loc)}
  <div class="shell">
  {nav_html}
  <div class="main">
  <header class="top">
    <div>
      <h1 class="page-title">{escape(t("builder.title", loc))}</h1>
    </div>
    <div class="top-actions">
      <span class="status" id="status">{escape(t("builder.status.unsaved", loc))}</span>
      <button type="button" class="ghost" id="btn-clear">{escape(t("builder.btn.clear", loc))}</button>
      <button type="button" class="primary" id="btn-save">{escape(t("builder.btn.save", loc))}</button>
    </div>
  </header>
  {live_banner}

  <div class="layout">
    <aside class="palette">
      <h2>{escape(t("builder.palette", loc))}</h2>
      <p class="sub">{escape(t("builder.palette_sub", loc))}</p>
      <div class="search-wrap">
        <input type="search" id="pal-search" placeholder="{escape(t("builder.search_ph", loc))}" autocomplete="off" />
        <p class="search-empty" id="search-empty">{escape(t("builder.search_empty", loc))}</p>
      </div>
      <div class="pal-filters">
        <label><input type="checkbox" id="flt-has-value" /> {escape(t("builder.filter_valued", loc))}</label>
        <span id="flt-value-stats"></span>
      </div>
      <div class="pal-fold-bar">
        <button type="button" class="ghost" id="btn-expand-all">{escape(t("builder.expand_all", loc))}</button>
        <button type="button" class="ghost" id="btn-collapse-all">{escape(t("builder.collapse_all", loc))}</button>
      </div>
      {_palette_html(source)}
    </aside>
    <section class="canvas-wrap">
      <div class="canvas-head">
        <div>
          <h2>{escape(t("builder.canvas", loc))}</h2>
          <p>{escape(t("builder.canvas_help", loc))}</p>
        </div>
        <span id="count-label" style="font-size:0.85rem;color:#6b7788;font-weight:700;">0 件</span>
      </div>
      <div class="canvas empty" id="canvas" aria-label="ダッシュボード"></div>
    </section>
  </div>

  <script>
    const CATALOG = {catalog_json};
    const COLORS = {colors_json};
    const STORAGE_KEY = "kpistarter.builder.v3";
    const LEGACY_KEYS = ["kpistarter.builder.v2", "kpistarter.builder.v1"];
    const FOLD_KEY = "kpistarter.builder.folds.v1";
    const GROUP_LABEL = {{
      business: "業務",
      digital: "デジタル",
      event: "イベント",
      traffic: "流入",
    }};

    const canvas = document.getElementById("canvas");
    const statusEl = document.getElementById("status");
    const countLabel = document.getElementById("count-label");
    const searchInput = document.getElementById("pal-search");
    const searchEmpty = document.getElementById("search-empty");
    let foldsLockedBySearch = false;

    function getOpenFolds() {{
      try {{
        const raw = JSON.parse(localStorage.getItem(FOLD_KEY) || "null");
        if (Array.isArray(raw)) return new Set(raw);
      }} catch (_) {{}}
      return new Set(["layout"]);
    }}

    function saveOpenFolds() {{
      if (foldsLockedBySearch) return;
      const open = [...document.querySelectorAll(".pal-group:not(.is-collapsed)")]
        .map((g) => g.dataset.groupKey)
        .filter(Boolean);
      localStorage.setItem(FOLD_KEY, JSON.stringify(open));
    }}

    function setGroupCollapsed(group, collapsed) {{
      group.classList.toggle("is-collapsed", collapsed);
      const btn = group.querySelector("[data-toggle-group]");
      if (btn) btn.setAttribute("aria-expanded", collapsed ? "false" : "true");
    }}

    function applySavedFolds() {{
      const open = getOpenFolds();
      document.querySelectorAll(".pal-group").forEach((group) => {{
        const key = group.dataset.groupKey;
        setGroupCollapsed(group, !open.has(key));
      }});
    }}

    function expandAll() {{
      foldsLockedBySearch = false;
      document.querySelectorAll(".pal-group").forEach((g) => setGroupCollapsed(g, false));
      saveOpenFolds();
    }}

    function collapseAll() {{
      foldsLockedBySearch = false;
      document.querySelectorAll(".pal-group").forEach((g) => setGroupCollapsed(g, true));
      saveOpenFolds();
    }}

    function setStatus(msg, ok) {{
      statusEl.textContent = msg;
      statusEl.classList.toggle("ok", !!ok);
    }}

    function usedIds() {{
      return [...canvas.querySelectorAll(".dash-card")].map((el) => el.dataset.id);
    }}

    function colorRowHtml(active) {{
      return (
        '<div class="color-row" role="group" aria-label="色">' +
        COLORS.map((c) => {{
          const on = c.id === active ? " is-active" : "";
          return (
            '<button type="button" class="swatch' + on + '" data-color="' +
            c.id + '" title="' + c.label + '" aria-label="' + c.label + '"></button>'
          );
        }}).join("") +
        "</div>"
      );
    }}

    function applyTone(el, color) {{
      const c = color || "default";
      el.dataset.color = c;
      COLORS.forEach((x) => el.classList.remove("tone-" + x.id));
      el.classList.add("tone-" + c);
      el.querySelectorAll(".swatch").forEach((s) => {{
        s.classList.toggle("is-active", s.dataset.color === c);
      }});
    }}

    function bindColorRow(el) {{
      el.querySelector(".color-row")?.addEventListener("click", (e) => {{
        const btn = e.target.closest(".swatch");
        if (!btn) return;
        e.stopPropagation();
        applyTone(el, btn.dataset.color);
        setStatus("未保存");
      }});
    }}

    function refreshPaletteState() {{
      const used = new Set(usedIds());
      document.querySelectorAll('.pal-item[data-type="widget"]').forEach((el) => {{
        el.classList.toggle("in-canvas", used.has(el.dataset.id));
      }});
      const nCards = canvas.querySelectorAll(".dash-card").length;
      const nSec = canvas.querySelectorAll(".dash-section").length;
      countLabel.textContent = nCards + " 項目" + (nSec ? " · " + nSec + " 見出し" : "");
      canvas.classList.toggle("empty", nCards + nSec === 0);
      applySearch();
    }}

    const fltHasValue = document.getElementById("flt-has-value");
    const fltValueStats = document.getElementById("flt-value-stats");

    function updateValueStats() {{
      const widgets = [...document.querySelectorAll('.pal-item[data-type="widget"]')];
      const withVal = widgets.filter((el) => el.dataset.hasValue === "1").length;
      if (fltValueStats) {{
        fltValueStats.textContent = "値あり " + withVal + " / " + widgets.length;
      }}
    }}

    function applySearch() {{
      const q = (searchInput.value || "").trim().toLowerCase();
      const onlyVal = !!(fltHasValue && fltHasValue.checked);
      let visible = 0;
      const filtering = !!(q || onlyVal);
      if (!filtering) {{
        foldsLockedBySearch = false;
        document.querySelectorAll(".pal-item").forEach((el) => el.classList.remove("is-hidden"));
        document.querySelectorAll(".pal-group").forEach((g) => g.classList.remove("is-hidden"));
        applySavedFolds();
        searchEmpty.classList.remove("show");
        updateValueStats();
        return;
      }}
      foldsLockedBySearch = true;
      document.querySelectorAll(".pal-group").forEach((group) => {{
        let groupVisible = 0;
        group.querySelectorAll(".pal-item").forEach((el) => {{
          if (el.dataset.type === "section") {{
            el.classList.toggle("is-hidden", onlyVal); // hide layout when filtering values
            if (!onlyVal && !q) {{
              groupVisible += 1;
              visible += 1;
            }} else if (!onlyVal) {{
              const label = (el.querySelector(".pal-label")?.textContent || "").toLowerCase();
              const match = !q || label.includes(q);
              el.classList.toggle("is-hidden", !match);
              if (match) {{ groupVisible += 1; visible += 1; }}
            }}
            return;
          }}
          const label = (el.querySelector(".pal-label")?.textContent || "").toLowerCase();
          const hint = (el.querySelector(".pal-hint")?.textContent || "").toLowerCase();
          const val = (el.querySelector(".pal-value")?.textContent || "").toLowerCase();
          const id = (el.dataset.id || "").toLowerCase();
          const textOk = !q || label.includes(q) || hint.includes(q) || id.includes(q) || val.includes(q);
          const valOk = !onlyVal || el.dataset.hasValue === "1";
          const match = textOk && valOk;
          el.classList.toggle("is-hidden", !match);
          if (match) {{
            groupVisible += 1;
            visible += 1;
          }}
        }});
        group.classList.toggle("is-hidden", groupVisible === 0);
        if (groupVisible > 0) setGroupCollapsed(group, false);
      }});
      searchEmpty.classList.toggle("show", visible === 0);
      updateValueStats();
    }}

    function bindRemove(el) {{
      el.querySelector(".rm").addEventListener("click", (e) => {{
        e.stopPropagation();
        el.remove();
        refreshPaletteState();
        setStatus("未保存");
      }});
    }}

    function makeCard(id, color) {{
      const w = CATALOG[id];
      if (!w) return null;
      const el = document.createElement("article");
      el.className = "dash-card g-" + w.group;
      el.dataset.type = "widget";
      el.dataset.id = w.id;
      el.innerHTML =
        '<button type="button" class="rm" aria-label="削除">×</button>' +
        '<span class="kind">' + (GROUP_LABEL[w.group] || w.group) + "</span>" +
        '<div class="label">' + escapeHtml(w.label) + "</div>" +
        '<div class="value">' + escapeHtml(w.value) + "</div>" +
        '<div class="hint">' + escapeHtml(w.hint) + "</div>" +
        colorRowHtml(color || "default");
      bindRemove(el);
      bindColorRow(el);
      applyTone(el, color || "default");
      return el;
    }}

    function makeSection(title, color) {{
      const el = document.createElement("div");
      el.className = "dash-section";
      el.dataset.type = "section";
      el.innerHTML =
        '<button type="button" class="rm" aria-label="削除">×</button>' +
        '<span class="sec-badge">カテゴリ</span>' +
        '<input class="sec-title" type="text" maxlength="40" placeholder="カテゴリ名" />' +
        colorRowHtml(color || "blue");
      const input = el.querySelector(".sec-title");
      input.value = title || "新しいカテゴリ";
      input.addEventListener("click", (e) => e.stopPropagation());
      input.addEventListener("mousedown", (e) => e.stopPropagation());
      input.addEventListener("input", () => setStatus("未保存"));
      bindRemove(el);
      bindColorRow(el);
      applyTone(el, color || "blue");
      return el;
    }}

    function escapeHtml(s) {{
      return String(s)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
    }}

    function serialize() {{
      return [...canvas.children].map((el) => {{
        if (el.classList.contains("dash-section")) {{
          return {{
            type: "section",
            title: el.querySelector(".sec-title")?.value || "カテゴリ",
            color: el.dataset.color || "blue",
          }};
        }}
        return {{
          type: "widget",
          id: el.dataset.id,
          color: el.dataset.color || "default",
        }};
      }}).filter((x) => x.type === "section" || (x.type === "widget" && x.id));
    }}

    function save() {{
      localStorage.setItem(STORAGE_KEY, JSON.stringify(serialize()));
      setStatus("保存しました", true);
    }}

    function normalizeItems(raw) {{
      if (!Array.isArray(raw)) return [];
      if (raw.length && typeof raw[0] === "string") {{
        return raw.map((id) => ({{ type: "widget", id, color: "default" }}));
      }}
      return raw
        .filter((x) => x && (x.type === "section" || x.type === "widget"))
        .map((x) => ({{
          ...x,
          color: x.color || (x.type === "section" ? "blue" : "default"),
        }}));
    }}

    function readStorage() {{
      for (const key of [STORAGE_KEY, ...LEGACY_KEYS]) {{
        try {{
          const raw = JSON.parse(localStorage.getItem(key) || "null");
          if (raw != null) return raw;
        }} catch (_) {{}}
      }}
      return [];
    }}

    function load() {{
      const items = normalizeItems(readStorage());
      canvas.innerHTML = "";
      items.forEach((item) => {{
        if (item.type === "section") {{
          canvas.appendChild(makeSection(item.title || "カテゴリ", item.color));
        }} else if (item.id) {{
          const card = makeCard(item.id, item.color);
          if (card) canvas.appendChild(card);
        }}
      }});
      refreshPaletteState();
      if (items.length) setStatus("読み込み済み", true);
      else setStatus("未保存");
    }}

    function clearAll() {{
      if (!canvas.children.length) return;
      if (!confirm("ダッシュボードを空にしますか？")) return;
      canvas.innerHTML = "";
      refreshPaletteState();
      setStatus("未保存");
    }}

    document.getElementById("btn-save").addEventListener("click", save);
    document.getElementById("btn-clear").addEventListener("click", clearAll);
    document.getElementById("btn-expand-all").addEventListener("click", expandAll);
    document.getElementById("btn-collapse-all").addEventListener("click", collapseAll);
    searchInput.addEventListener("input", applySearch);
    fltHasValue?.addEventListener("change", applySearch);
    updateValueStats();

    document.querySelectorAll("[data-toggle-group]").forEach((btn) => {{
      btn.addEventListener("click", () => {{
        if (foldsLockedBySearch) return;
        const group = btn.closest(".pal-group");
        if (!group) return;
        setGroupCollapsed(group, !group.classList.contains("is-collapsed"));
        saveOpenFolds();
      }});
    }});

    applySavedFolds();

    document.querySelectorAll(".pal-list").forEach((list) => {{
      Sortable.create(list, {{
        group: {{ name: "kpi", pull: "clone", put: false }},
        sort: false,
        animation: 150,
        ghostClass: "sortable-ghost",
        chosenClass: "sortable-chosen",
        filter: ".in-canvas, .is-hidden",
        onClone: (evt) => {{
          evt.item.dataset.pendingId = evt.item.dataset.id;
          evt.item.dataset.pendingType = evt.item.dataset.type || "widget";
        }},
      }});
    }});

    Sortable.create(canvas, {{
      group: {{ name: "kpi", pull: true, put: true }},
      animation: 150,
      ghostClass: "sortable-ghost",
      chosenClass: "sortable-chosen",
      filter: ".sec-title, .rm, .swatch, .color-row",
      preventOnFilter: false,
      onAdd: (evt) => {{
        const type = evt.item.dataset.type || evt.item.dataset.pendingType || "widget";
        const id = evt.item.dataset.id || evt.item.dataset.pendingId;

        if (type === "section" || id === "__section__") {{
          const sec = makeSection("新しいカテゴリ", "blue");
          evt.item.replaceWith(sec);
          refreshPaletteState();
          setStatus("未保存");
          const input = sec.querySelector(".sec-title");
          input?.focus();
          input?.select();
          return;
        }}

        if (!id || !CATALOG[id]) {{
          evt.item.remove();
          return;
        }}
        const existing = [...canvas.querySelectorAll(".dash-card")].filter(
          (c) => c.dataset.id === id && c !== evt.item
        );
        if (existing.length) {{
          evt.item.remove();
          setStatus("すでに追加済み");
          refreshPaletteState();
          return;
        }}
        if (evt.item.classList.contains("pal-item")) {{
          const card = makeCard(id, "default");
          if (!card) {{
            evt.item.remove();
            return;
          }}
          evt.item.replaceWith(card);
        }}
        refreshPaletteState();
        setStatus("未保存");
      }},
      onUpdate: () => setStatus("未保存"),
      onRemove: () => {{
        refreshPaletteState();
        setStatus("未保存");
      }},
    }});

    load();
  </script>
  </div>
  </div>
  {rail_js()}
</body>
</html>
"""
