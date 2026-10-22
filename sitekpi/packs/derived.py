"""Industry packs built on an existing pack's flow, events and board copy.

Added because a published benchmark exists for the industry (see sources.py):
each one gets its own 業界目安 (cited where a source matches), label, wording
for the flow steps and a scaled sample — everything else comes from ``base``.
"""

from __future__ import annotations

from typing import Any

L = dict[str, str]

DERIVED: dict[str, dict[str, Any]] = {
    "apparel": {
        "base": "ec", "category": "commerce", "scale": 0.8,
        "label": {"ja": "アパレル・ファッション", "en": "Apparel & fashion", "ko": "의류·패션"},
        "hint": {"ja": "商品〜購入", "en": "Browse → purchase", "ko": "조회〜구매"},
    },
    "food_ec": {
        "base": "ec", "category": "commerce", "scale": 0.45,
        "label": {"ja": "食品・飲料EC", "en": "Food & beverage e-commerce", "ko": "식품·음료 EC"},
        "hint": {"ja": "商品〜購入（リピート多め）", "en": "Browse → purchase (repeat buyers)", "ko": "조회〜구매(재구매 많음)"},
    },
    "furniture_ec": {
        "base": "ec", "category": "commerce", "scale": 0.35,
        "label": {"ja": "家具・インテリアEC", "en": "Home & furniture e-commerce", "ko": "가구·인테리어 EC"},
        "hint": {"ja": "比較が長い高単価の購入", "en": "Long comparison, high ticket", "ko": "비교가 긴 고단가 구매"},
    },
    "manufacturing": {
        "base": "b2b", "category": "lead", "scale": 0.6,
        "label": {"ja": "製造業・BtoB製品", "en": "Manufacturing (B2B products)", "ko": "제조·B2B 제품"},
        "hint": {"ja": "製品資料〜問い合わせ", "en": "Product info → inquiry", "ko": "제품 자료〜문의"},
        "steps": {"case_view": {"ja": "製品・事例を見た", "en": "Viewed products", "ko": "제품·사례 열람"}},
    },
    "it_services": {
        "base": "b2b", "category": "lead", "scale": 0.7,
        "label": {"ja": "IT・システム開発", "en": "IT services & development", "ko": "IT·시스템 개발"},
        "hint": {"ja": "事例〜問い合わせ", "en": "Case studies → inquiry", "ko": "사례〜문의"},
    },
    "legal": {
        "base": "construction", "category": "lead", "scale": 0.5,
        "label": {"ja": "士業・法律事務所", "en": "Legal & professional services", "ko": "법률·전문 서비스"},
        "hint": {"ja": "取扱分野〜相談予約", "en": "Practice areas → consultation", "ko": "취급 분야〜상담 예약"},
        "steps": {
            "project_view": {"ja": "取扱分野を見た", "en": "Viewed practice areas", "ko": "취급 분야 열람"},
            "site_visit_book": {"ja": "相談を予約", "en": "Booked consultation", "ko": "상담 예약"},
        },
    },
    "home_service": {
        "base": "construction", "category": "lead", "scale": 0.8,
        "label": {"ja": "リフォーム・設備工事", "en": "Home repair & HVAC", "ko": "리폼·설비 공사"},
        "hint": {"ja": "施工例〜見積・訪問", "en": "Projects → quote / visit", "ko": "시공 사례〜견적·방문"},
        "steps": {"site_visit_book": {"ja": "訪問見積を予約", "en": "Booked on-site quote", "ko": "방문 견적 예약"}},
    },
    "auto": {
        "base": "realestate", "category": "lead", "scale": 0.7,
        "label": {"ja": "自動車・ディーラー", "en": "Auto dealers", "ko": "자동차·딜러"},
        "hint": {"ja": "在庫車〜試乗予約", "en": "Inventory → test drive", "ko": "재고 차량〜시승 예약"},
        "steps": {
            "listing_view": {"ja": "車両を見た", "en": "Viewed vehicle", "ko": "차량 열람"},
            "tour_book": {"ja": "試乗を予約", "en": "Booked test drive", "ko": "시승 예약"},
        },
    },
}


def base_of(slug: str) -> str:
    return DERIVED[slug]["base"] if slug in DERIVED else slug


def derived_text(slug: str, field: str, locale: str) -> str | None:
    d = DERIVED.get(slug)
    if not d:
        return None
    if field in ("label", "hint"):
        return d[field].get(locale) or d[field]["ja"]
    if field == "property":
        return f"{d['label'].get(locale) or d['label']['ja']} Demo"
    return None


def scaled_demo(demo: dict[str, dict[str, Any]], scale: float) -> dict[str, dict[str, Any]]:
    counts = ("uu", "sessions", "new_users", "returning_users", "pageviews", "signups",
              "pay_start", "pay_success", "revenue")
    out: dict[str, dict[str, Any]] = {}
    for period, data in demo.items():
        d = dict(data)
        for k in counts:
            if isinstance(d.get(k), (int, float)):
                d[k] = round(d[k] * scale)
        d["event_counts"] = {k: round(v * scale) for k, v in (data.get("event_counts") or {}).items()}
        out[period] = d
    return out
