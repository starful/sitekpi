"""行動タイプ: pick what visitors do first, the industry second (optional).

Each behaviour groups the industry packs of one category. Choosing a behaviour
without an industry uses a *behaviour pack* (slug ``type-<category>``):

- flow, events, board copy and sample numbers: the category's representative pack
- 業界目安: only site-wide metrics whose meaning is the same in every industry of
  the behaviour, set to the median of those industries' 目安 (labelled as such).
  Funnel-step rates differ by industry, so they get no 目安 until one is chosen.
"""

from __future__ import annotations

from statistics import median
from typing import Any

PREFIX = "type-"

BEHAVIORS: dict[str, dict[str, Any]] = {
    "commerce": {"rep": "ec", "label": {"ja": "買う", "en": "Buy", "ko": "구매하기"},
                 "hint": {"ja": "商品を見て、カートに入れて、購入", "en": "View, add to cart, purchase", "ko": "상품 보기 → 장바구니 → 구매"}},
    "membership": {"rep": "b2c", "label": {"ja": "会員になって使い続ける", "en": "Sign up and stay", "ko": "회원 가입 후 계속 이용"},
                   "hint": {"ja": "登録・トライアルから有料へ", "en": "Sign-up or trial, then paid", "ko": "가입·체험 후 유료 전환"}},
    "lead": {"rep": "b2b", "label": {"ja": "問い合わせる", "en": "Get in touch", "ko": "문의하기"},
             "hint": {"ja": "事例や資料を見て、問い合わせ", "en": "Read, download, contact", "ko": "사례·자료 확인 후 문의"}},
    "booking": {"rep": "clinic", "label": {"ja": "予約する", "en": "Book", "ko": "예약하기"},
                "hint": {"ja": "メニューや料金を見て、予約", "en": "Check menu or prices, then book", "ko": "메뉴·가격 확인 후 예약"}},
    "education": {"rep": "edu", "label": {"ja": "申し込む", "en": "Apply", "ko": "신청하기"},
                  "hint": {"ja": "内容を見て、申込フォームを完了", "en": "Read, then complete the form", "ko": "내용 확인 후 신청 완료"}},
    "recruit": {"rep": "hr", "label": {"ja": "応募する", "en": "Apply for a job", "ko": "지원하기"},
                "hint": {"ja": "求人を見て、応募", "en": "View jobs, apply", "ko": "공고 보기 → 지원"}},
    "content": {"rep": "content", "label": {"ja": "読む・見る", "en": "Read or watch", "ko": "읽기·보기"},
                "hint": {"ja": "記事を読んで、登録・購読", "en": "Read, then subscribe", "ko": "읽고 구독·등록"}},
}

# Same meaning in every industry → a behaviour-level median is fair.
SHARED_METRICS = ("engaged_rate", "bounce_rate", "pages_session", "sessions_per_uu",
                  "pages_per_uu", "new_pct", "signup_rate")


def slug_of(cat: str) -> str:
    return PREFIX + cat


def is_behavior(slug: str) -> bool:
    return slug.startswith(PREFIX) and slug[len(PREFIX):] in BEHAVIORS


def category_of(slug: str) -> str:
    return slug[len(PREFIX):] if is_behavior(slug) else ""


def rep_of(slug: str) -> str:
    """The pack whose flow / copy / wording a behaviour or derived pack borrows."""
    from sitekpi.packs.derived import base_of

    return BEHAVIORS[category_of(slug)]["rep"] if is_behavior(slug) else base_of(slug)


def behavior_label(cat: str, locale: str) -> str:
    lab = BEHAVIORS[cat]["label"]
    return lab.get(locale) or lab["ja"]


def behavior_hint(cat: str, locale: str) -> str:
    h = BEHAVIORS[cat]["hint"]
    return h.get(locale) or h["ja"]


def blended_benchmarks(members: list[str], benchmarks: dict[str, dict[str, dict[str, Any]]],
                       member_labels: list[str]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for key in SHARED_METRICS:
        specs = [benchmarks[m][key] for m in members if key in benchmarks.get(m, {})]
        if len(specs) < len(members) or not specs:
            continue
        low = round(median(float(s["low"]) for s in specs), 2)
        high = round(median(float(s["high"]) for s in specs), 2)
        first = specs[0]
        out[key] = {
            "low": low, "high": high, "unit": first["unit"],
            "higher_is_better": first["higher_is_better"],
            "source": {"kind": "blend", "label": " / ".join(member_labels), "url": "", "rule": ""},
        }
    return out
