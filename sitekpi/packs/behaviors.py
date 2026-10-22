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

def _l(ja: str, en: str, ko: str) -> dict[str, str]:
    return {"ja": ja, "en": en, "ko": ko}


# Every flow starts the same way (worldwide): サイトに来た (by channel) → page_view.
# The rest uses GA4's automatically collected / enhanced-measurement / recommended
# events where one exists, so most sites already record them.
# "board": how the board counts this behaviour (主転換 = primary, rates between
# primary and mid / bottom); without it the representative pack's wording is used.
BEHAVIORS: dict[str, dict[str, Any]] = {
    "commerce": {"rep": "ec", "label": _l("買う", "Buy", "구매하기"),
                 "hint": _l("商品を見て、カートに入れて、購入", "View, add to cart, purchase", "상품 보기 → 장바구니 → 구매"),
                 "flow": ["page_view", "view_item", "add_to_cart", "begin_checkout", "purchase"]},
    "membership": {"rep": "b2c", "label": _l("会員になって使い続ける", "Sign up and stay", "회원 가입 후 계속 이용"),
                   "hint": _l("登録して、ログインして、有料へ", "Sign up, log in, go paid", "가입 → 로그인 → 유료 전환"),
                   "flow": ["page_view", "sign_up", "login", "begin_checkout", "purchase"]},
    "lead": {"rep": "b2b", "label": _l("問い合わせる", "Get in touch", "문의하기"),
             "hint": _l("読んで、資料を見て、フォームを送信", "Read, download, send the form", "읽고 자료 보고 폼 제출"),
             "flow": ["page_view", "scroll", "file_download", "form_start", "form_submit"],
             "board": {"primary": "form_submit", "mid": "form_start", "bottom": "file_download",
                       "signup_label": _l("問い合わせ送信", "Inquiries sent", "문의 제출"),
                       "cvr_label": _l("問い合わせCVR", "Inquiry CVR", "문의 CVR"),
                       "mid_label": _l("フォーム開始", "Form started", "폼 시작"),
                       "bottom_label": _l("資料DL", "Downloads", "자료 다운로드"),
                       "rate_a_label": _l("フォーム開始→送信率", "Form start → submit", "폼 시작→제출률"),
                       "rate_b_label": _l("資料DL→問い合わせ率", "Download → inquiry", "자료→문의율")}},
    "booking": {"rep": "clinic", "label": _l("予約する", "Book", "예약하기"),
                "hint": _l("メニューや料金を見て、予約フォームを送信", "Check menu or prices, send the booking form", "메뉴·가격 확인 후 예약 폼 제출"),
                "flow": ["page_view", "scroll", "view_item", "form_start", "form_submit"],
                "board": {"primary": "form_submit", "mid": "form_start", "bottom": "view_item",
                          "signup_label": _l("予約完了", "Bookings", "예약 완료"),
                          "cvr_label": _l("予約CVR", "Booking CVR", "예약 CVR"),
                          "mid_label": _l("予約を開始", "Booking started", "예약 시작"),
                          "bottom_label": _l("メニュー・プランを見た", "Viewed menu / plans", "메뉴·플랜 열람"),
                          "rate_a_label": _l("予約開始→完了率", "Booking start → done", "예약 시작→완료율"),
                          "rate_b_label": _l("閲覧→予約率", "View → booking", "열람→예약률")}},
    "education": {"rep": "edu", "label": _l("申し込む", "Apply", "신청하기"),
                  "hint": _l("内容を読んで、資料を見て、申込フォームを完了", "Read, download, complete the form", "내용·자료 확인 후 신청 완료"),
                  "flow": ["page_view", "scroll", "file_download", "form_start", "form_submit"],
                  "board": {"primary": "form_submit", "mid": "form_start", "bottom": "file_download",
                            "signup_label": _l("申込完了", "Applications", "신청 완료"),
                            "cvr_label": _l("申込CVR", "Application CVR", "신청 CVR"),
                            "mid_label": _l("申込を開始", "Application started", "신청 시작"),
                            "bottom_label": _l("資料DL", "Downloads", "자료 다운로드"),
                            "rate_a_label": _l("申込開始→完了率", "Start → complete", "신청 시작→완료율"),
                            "rate_b_label": _l("資料DL→申込率", "Download → application", "자료→신청률")}},
    "recruit": {"rep": "hr", "label": _l("応募する", "Apply for a job", "지원하기"),
                "hint": _l("求人を探して、見て、応募フォームを送信", "Search, view a job, send the form", "공고 검색·열람 후 지원 폼 제출"),
                "flow": ["page_view", "view_search_results", "view_item", "form_start", "form_submit"],
                "board": {"primary": "form_submit", "mid": "form_start", "bottom": "view_item",
                          "signup_label": _l("応募完了", "Applications", "지원 완료"),
                          "cvr_label": _l("応募CVR", "Application CVR", "지원 CVR"),
                          "mid_label": _l("応募を開始", "Application started", "지원 시작"),
                          "bottom_label": _l("求人を見た", "Viewed jobs", "공고 열람"),
                          "rate_a_label": _l("応募開始→完了率", "Start → complete", "지원 시작→완료율"),
                          "rate_b_label": _l("求人閲覧→応募率", "Job view → application", "공고 열람→지원율")}},
    "content": {"rep": "content", "label": _l("読んで登録・購読する", "Read and subscribe", "읽고 구독·등록"),
                "hint": _l("記事を読んで、会員登録・購読へ", "Read, then sign up or subscribe", "읽고 회원가입·구독"),
                "flow": ["page_view", "user_engagement", "scroll", "click", "sign_up"],
                "board": {"primary": "sign_up", "mid": "click", "bottom": "scroll",
                          "signup_label": _l("登録・購読", "Sign-ups", "가입·구독"),
                          "cvr_label": _l("登録CVR", "Sign-up CVR", "가입 CVR"),
                          "mid_label": _l("リンククリック", "Link clicks", "링크 클릭"),
                          "bottom_label": _l("最後まで読んだ", "Read to the end", "끝까지 읽음"),
                          "rate_a_label": _l("クリック→登録率", "Click → sign-up", "클릭→가입률"),
                          "rate_b_label": _l("読了→登録率", "Read → sign-up", "완독→가입률")}},
    "blog": {"rep": "content", "label": _l("ブログ・記事を読んでもらう", "Blog: get articles read", "블로그·글 읽히기"),
             "hint": _l("記事を読んで、ほかの記事やリンクへ進む", "Read, then go on to other articles or links", "글을 읽고 다른 글·링크로"),
             "flow": ["page_view", "user_engagement", "scroll", "view_search_results", "click"],
             "board": {"primary": "click", "mid": "view_search_results", "bottom": "scroll",
                       "signup_label": _l("リンククリック", "Link clicks", "링크 클릭"),
                       "cvr_label": _l("クリック率", "Click rate", "클릭률"),
                       "mid_label": _l("サイト内検索", "Site searches", "사이트 내 검색"),
                       "bottom_label": _l("最後まで読んだ", "Read to the end", "끝까지 읽음"),
                       "rate_a_label": _l("検索→クリック率", "Search → click", "검색→클릭률"),
                       "rate_b_label": _l("読了→クリック率", "Read → click", "완독→클릭률")}},
}

BOARD_TEXT_FIELDS = ("signup_label", "cvr_label", "mid_label", "bottom_label", "rate_a_label", "rate_b_label")


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


def behavior_board_text(slug: str, field: str, locale: str) -> str | None:
    """Board wording for a behaviour pack that counts its own events."""
    board = BEHAVIORS.get(category_of(slug), {}).get("board") if is_behavior(slug) else None
    if not board or field not in BOARD_TEXT_FIELDS:
        return None
    return board[field].get(locale) or board[field]["ja"]


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
