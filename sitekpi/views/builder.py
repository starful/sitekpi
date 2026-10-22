"""Custom dashboard builder — drag from palette to canvas (localStorage)."""

from __future__ import annotations

from typing import Any

from sitekpi.i18n import normalize_locale, t
from sitekpi.templating import render

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


def _value_is_empty(val: Any) -> bool:
    s = str(val if val is not None else "").strip()
    return s in ("", "—", "-", "–", "N/A", "n/a")


def _palette(widgets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Palette groups (layout tools first, then each widget group, collapsed)."""
    groups: list[dict[str, Any]] = [
        {"id": "layout", "label": "レイアウト", "tone": "lay", "count": 1, "collapsed": False, "widgets": []}
    ]
    for gid, meta in GROUP_META.items():
        if gid == "layout":
            continue
        items = [w for w in widgets if w["group"] == gid]
        groups.append(
            {
                "id": gid,
                "label": meta["label"],
                "tone": meta["tone"],
                "count": len(items),
                "collapsed": True,
                "widgets": [
                    {
                        "id": w["id"],
                        "group": w["group"],
                        "label": w["label"],
                        "hint": w.get("hint") or "",
                        "empty": _value_is_empty(w.get("value")),
                        "display": "—" if _value_is_empty(w.get("value")) else str(w.get("value")),
                    }
                    for w in items
                ],
            }
        )
    return groups


def render_builder(
    *,
    live_values: dict[str, str] | None = None,
    property_name: str = "",
    live_error: str | None = None,
    widgets: list[dict[str, Any]] | None = None,
    locale: str = "ja",
    rail: dict[str, Any] | None = None,
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
        for meta in catalog.values():
            if meta.get("group") == "business":
                meta["value"] = "—"
                meta["hint"] = t("builder.biz_hint", loc)
    return render(
        "builder.html",
        loc=loc,
        rail=rail,
        property_name=property_name,
        live_error=live_error,
        n_digital=sum(1 for w in source if w.get("group") == "digital"),
        n_event=sum(1 for w in source if w.get("group") == "event"),
        palette=_palette(source),
        builder_data={"catalog": catalog, "colors": CARD_COLORS},
    )
