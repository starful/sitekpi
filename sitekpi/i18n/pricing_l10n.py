"""Copy + plan-boundary data for the public pricing page (/pricing) — ja / en / ko.

``FEATURE_ROWS`` is kept separate from the pricing.html template on purpose: the
actual Free/Pro line is not decided yet (see billing.py — FREE_SITE_LIMIT,
PRO_FEATURES), so this table is a placeholder shape. Once the plan-boundary
doc is final, only this list (and the two price numbers in PRICING) should
need to change — the template just renders whatever rows/cells are here.

A cell is one of:
  True   -> included (rendered as a check)
  False  -> not included (rendered as a dash)
  dict   -> a localized string per locale (e.g. {"ja": "1件", "en": "1", "ko": "1개"})
"""

from __future__ import annotations

from typing import Any

FEATURE_GROUPS: dict[str, dict[str, str]] = {
    "basic": {"ja": "基本", "en": "Basics", "ko": "기본"},
    "data": {"ja": "データ", "en": "Data", "ko": "데이터"},
    "support": {"ja": "サポート", "en": "Support", "ko": "지원"},
}

# Placeholder plan line — not final. Mirrors sitekpi/billing.py (FREE_SITE_LIMIT,
# PRO_FEATURES) where a gate already exists; everything else here is a guess for
# how the comparison table will eventually read.
FEATURE_ROWS: list[dict[str, Any]] = [
    {
        "group": "basic", "id": "sites",
        "label": {"ja": "接続できるサイト数", "en": "Connected sites", "ko": "연결 가능한 사이트 수"},
        "free": {"ja": "1件", "en": "1", "ko": "1개"},
        "pro": {"ja": "複数件", "en": "Multiple", "ko": "복수"},
    },
    {
        "group": "basic", "id": "board",
        "label": {"ja": "GA4 KPI ボード", "en": "GA4 KPI board", "ko": "GA4 KPI 보드"},
        "free": True, "pro": True,
    },
    {
        "group": "basic", "id": "benchmarks",
        "label": {"ja": "業界目安での判定", "en": "Benchmark verdicts", "ko": "업계 기준 판정"},
        "free": True, "pro": True,
    },
    {
        "group": "data", "id": "site_compare",
        "label": {"ja": "サイト一覧（複数サイト比較）", "en": "Site list (compare sites)", "ko": "사이트 목록(비교)"},
        "free": True, "pro": True,
    },
    {
        "group": "data", "id": "advanced_report",
        "label": {"ja": "高度なレポート・書き出し", "en": "Advanced reports & export", "ko": "고급 리포트 · 내보내기"},
        "free": False, "pro": True,
    },
    {
        "group": "data", "id": "history",
        "label": {"ja": "データの保存期間", "en": "Data retention", "ko": "데이터 보관 기간"},
        "free": {"ja": "直近のみ", "en": "Recent only", "ko": "최근 데이터만"},
        "pro": {"ja": "未定（検討中）", "en": "TBD", "ko": "미정(검토 중)"},
    },
    {
        "group": "support", "id": "support",
        "label": {"ja": "サポート", "en": "Support", "ko": "지원"},
        "free": {"ja": "ヘルプページ", "en": "Help pages", "ko": "도움말 페이지"},
        "pro": {"ja": "未定（検討中）", "en": "TBD", "ko": "미정(검토 중)"},
    },
]

PRICING: dict[str, dict[str, Any]] = {
    "ja": {
        "meta_title": "料金 | SiteKPI",
        "meta_desc": "SiteKPI の Free / Pro プラン比較。料金はまだ確定していません（準備中）。",
        "kicker": "料金",
        "title": "Free でまず使って、必要になったら Pro へ",
        "lead": "今の SiteKPI はすべて Free の範囲で使えます。Pro の内容と料金はまだ確定していません（下表は検討中のたたき台です）。",
        "toggle_monthly": "月払い",
        "toggle_yearly": "年払い",
        "toggle_yearly_badge": "想定：2カ月分お得",
        "price_tbd": "準備中",
        "price_free": "¥0",
        "price_note_free": "ずっと無料",
        "price_note_pro_monthly": "月あたり（想定・未確定）",
        "price_note_pro_yearly": "月あたり（年払い時・想定・未確定）",
        "plan_free": "Free",
        "plan_pro": "Pro",
        "plan_free_tagline": "個人・小さなサイトのための、今の SiteKPI",
        "plan_pro_tagline": "複数サイトや高度なレポートが必要なチーム向け（準備中）",
        "cta_free": "無料で始める",
        "cta_pro": "アップグレード",
        "disclaimer": "表示している Pro の内容・料金は確定前の案です。変更される場合があります。",
        "table_title": "できることの比較",
        "th_feature": "できること",
        "th_free": "Free",
        "th_pro": "Pro",
    },
    "en": {
        "meta_title": "Pricing | SiteKPI",
        "meta_desc": "Compare SiteKPI Free and Pro. Pricing is not final yet (coming soon).",
        "kicker": "Pricing",
        "title": "Start on Free, move to Pro when you need to",
        "lead": "Everything in SiteKPI today is within the Free plan. Pro's scope and price are not final yet — the table below is a working draft.",
        "toggle_monthly": "Monthly",
        "toggle_yearly": "Yearly",
        "toggle_yearly_badge": "Planned: ~2 months free",
        "price_tbd": "Coming soon",
        "price_free": "¥0",
        "price_note_free": "Free forever",
        "price_note_pro_monthly": "per month (planned, not final)",
        "price_note_pro_yearly": "per month, billed yearly (planned, not final)",
        "plan_free": "Free",
        "plan_pro": "Pro",
        "plan_free_tagline": "Today's SiteKPI, for individuals and small sites",
        "plan_pro_tagline": "For teams that need multiple sites or advanced reports (coming soon)",
        "cta_free": "Start for free",
        "cta_pro": "Upgrade",
        "disclaimer": "The Pro scope and price shown are a draft and may change before launch.",
        "table_title": "Feature comparison",
        "th_feature": "Feature",
        "th_free": "Free",
        "th_pro": "Pro",
    },
    "ko": {
        "meta_title": "요금제 | SiteKPI",
        "meta_desc": "SiteKPI Free / Pro 플랜 비교. 요금은 아직 확정되지 않았습니다(준비 중).",
        "kicker": "요금제",
        "title": "먼저 Free로 쓰고, 필요할 때 Pro로",
        "lead": "지금의 SiteKPI는 전부 Free 범위 안에서 쓸 수 있습니다. Pro의 범위와 요금은 아직 확정되지 않았어요 — 아래 표는 검토 중인 초안입니다.",
        "toggle_monthly": "월간 결제",
        "toggle_yearly": "연간 결제",
        "toggle_yearly_badge": "예정: 약 2개월 무료",
        "price_tbd": "준비 중",
        "price_free": "¥0",
        "price_note_free": "계속 무료",
        "price_note_pro_monthly": "월 기준(예정, 미확정)",
        "price_note_pro_yearly": "월 기준 · 연간 결제 시(예정, 미확정)",
        "plan_free": "Free",
        "plan_pro": "Pro",
        "plan_free_tagline": "개인·소규모 사이트를 위한 지금의 SiteKPI",
        "plan_pro_tagline": "복수 사이트, 고급 리포트가 필요한 팀을 위한 플랜(준비 중)",
        "cta_free": "무료로 시작하기",
        "cta_pro": "업그레이드",
        "disclaimer": "표시된 Pro 범위·요금은 확정 전 초안이며 출시 전 변경될 수 있습니다.",
        "table_title": "기능 비교",
        "th_feature": "기능",
        "th_free": "Free",
        "th_pro": "Pro",
    },
}


def grouped_features(loc: str) -> list[dict[str, Any]]:
    """FEATURE_ROWS bucketed by FEATURE_GROUPS, with labels localized for ``loc``."""
    groups = []
    for gid, label in FEATURE_GROUPS.items():
        rows = [r for r in FEATURE_ROWS if r["group"] == gid]
        if rows:
            groups.append({"id": gid, "label": label[loc], "rows": rows})
    return groups
