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


# Every flow starts the same way, worldwide: サイトに来た (by channel) → サイトを開いた
# (session_start) → しっかり見た (user_engagement, GA4's engaged = 10 s+ by default).
# The behaviour's own steps follow, using GA4's automatically collected /
# enhanced-measurement / recommended events wherever one exists.
UNIVERSAL_STEPS = ["session_start", "user_engagement"]

# group → how step ① groups the choices (one decision, easy to scan)
GROUPS: dict[str, dict[str, str]] = {
    "buy": _l("買ってもらう", "Get a purchase", "구매로 잇기"),
    "contact": _l("問い合わせ・申し込み", "Get an inquiry or application", "문의·신청 받기"),
    "visit": _l("予約・来店", "Get a booking or visit", "예약·방문"),
    "member": _l("会員・利用", "Get sign-ups and use", "회원·이용"),
    "read": _l("読む・見る", "Get read or watched", "읽기·보기"),
}

# steps = the behaviour's own steps (after the universal ones) · primary = 主転換
# keep_copy = the board counts like the representative pack (its own wording / logic)
# industries = industries that usually use this flow (shown first in step ②);
#              default = the industry packs of the same category
BEHAVIORS: dict[str, dict[str, Any]] = {
    "commerce": {"group": "buy", "rep": "ec", "keep_copy": True,
                 "label": _l("買う", "Buy", "구매하기"),
                 "hint": _l("商品を見て、カートに入れて、購入", "View, add to cart, purchase", "상품 보기 → 장바구니 → 구매"),
                 "steps": ["view_item", "add_to_cart", "begin_checkout", "purchase"], "primary": "purchase"},
    "comparison": {"group": "buy", "rep": "marketplace",
                   "label": _l("比較して送客する", "Compare and refer", "비교 후 송객"),
                   "hint": _l("比較・口コミサイト: 探して、見て、販売先へ", "Comparison / review site: search, view, go to the seller", "비교·리뷰 사이트: 찾고 보고 판매처로"),
                   "steps": ["view_search_results", "view_item", "click"], "primary": "click",
                   "signup_label": _l("送客クリック", "Referral clicks", "송객 클릭"),
                   "cvr_label": _l("送客CVR", "Referral CVR", "송객 CVR"),
                   "industries": ["marketplace", "ec", "finance", "travel", "realestate"]},
    "donation": {"group": "buy", "rep": "community",
                 "label": _l("寄付してもらう", "Get donations", "기부 받기"),
                 "hint": _l("活動を知って、寄付フォームを完了", "Learn about the cause, complete the donation", "활동을 알고 기부 완료"),
                 "steps": ["scroll", "begin_checkout", "purchase"], "primary": "purchase",
                 "signup_label": _l("寄付完了", "Donations", "기부 완료"),
                 "cvr_label": _l("寄付CVR", "Donation CVR", "기부 CVR"),
                 "industries": ["gov", "community", "edu"]},
    "lead": {"group": "contact", "rep": "b2b",
             "label": _l("問い合わせる", "Get in touch", "문의하기"),
             "hint": _l("読んで、資料を見て、フォームを送信", "Read, download, send the form", "읽고 자료 보고 폼 제출"),
             "steps": ["scroll", "file_download", "form_start", "form_submit"], "primary": "form_submit",
             "signup_label": _l("問い合わせ送信", "Inquiries sent", "문의 제출"),
             "cvr_label": _l("問い合わせCVR", "Inquiry CVR", "문의 CVR")},
    "doc_request": {"group": "contact", "rep": "b2b",
                    "label": _l("資料請求してもらう", "Get document requests", "자료 요청 받기"),
                    "hint": _l("製品を見て、資料請求フォームを送信", "View the product, request the brochure", "제품 보고 자료 요청 폼 제출"),
                    "steps": ["view_item", "form_start", "form_submit"], "primary": "form_submit",
                    "signup_label": _l("資料請求", "Requests", "자료 요청"),
                    "cvr_label": _l("資料請求CVR", "Request CVR", "자료 요청 CVR"),
                    "industries": ["b2b", "manufacturing", "it_services", "construction", "realestate", "edu", "finance"]},
    "quote": {"group": "contact", "rep": "construction",
              "label": _l("見積もりを依頼してもらう", "Get quote requests", "견적 의뢰 받기"),
              "hint": _l("事例や料金を見て、見積もりフォームを送信", "See work and prices, send the quote form", "사례·가격 보고 견적 폼 제출"),
              "steps": ["view_item", "form_start", "form_submit"], "primary": "form_submit",
              "signup_label": _l("見積もり依頼", "Quote requests", "견적 의뢰"),
              "cvr_label": _l("見積もりCVR", "Quote CVR", "견적 CVR"),
              "industries": ["construction", "home_service", "manufacturing", "it_services", "legal", "auto"]},
    "call_line": {"group": "contact", "rep": "construction",
                  "label": _l("電話・LINEで問い合わせてもらう", "Get calls or LINE messages", "전화·LINE 문의 받기"),
                  "hint": _l("内容を見て、電話・LINE のボタンをタップ", "Read, then tap the phone / LINE button", "보고 전화·LINE 버튼 탭"),
                  "steps": ["scroll", "view_item", "click"], "primary": "click",
                  "signup_label": _l("電話・LINEタップ", "Phone / LINE taps", "전화·LINE 탭"),
                  "cvr_label": _l("タップ率", "Tap rate", "탭률"),
                  "industries": ["home_service", "legal", "clinic", "beauty", "realestate", "construction", "auto", "food"]},
    "education": {"group": "contact", "rep": "edu",
                  "label": _l("申し込む", "Apply", "신청하기"),
                  "hint": _l("内容を読んで、資料を見て、申込フォームを完了", "Read, download, complete the form", "내용·자료 확인 후 신청 완료"),
                  "steps": ["scroll", "file_download", "form_start", "form_submit"], "primary": "form_submit",
                  "signup_label": _l("申込完了", "Applications", "신청 완료"),
                  "cvr_label": _l("申込CVR", "Application CVR", "신청 CVR")},
    "recruit": {"group": "contact", "rep": "hr",
                "label": _l("応募する", "Apply for a job", "지원하기"),
                "hint": _l("求人を探して、見て、応募フォームを送信", "Search, view a job, send the form", "공고 검색·열람 후 지원 폼 제출"),
                "steps": ["view_search_results", "view_item", "form_start", "form_submit"], "primary": "form_submit",
                "signup_label": _l("応募完了", "Applications", "지원 완료"),
                "cvr_label": _l("応募CVR", "Application CVR", "지원 CVR")},
    "booking": {"group": "visit", "rep": "clinic",
                "label": _l("予約する", "Book", "예약하기"),
                "hint": _l("メニューや料金を見て、予約フォームを送信", "Check menu or prices, send the booking form", "메뉴·가격 확인 후 예약 폼 제출"),
                "steps": ["view_item", "form_start", "form_submit"], "primary": "form_submit",
                "signup_label": _l("予約完了", "Bookings", "예약 완료"),
                "cvr_label": _l("予約CVR", "Booking CVR", "예약 CVR")},
    "store_visit": {"group": "visit", "rep": "food",
                    "label": _l("来店予約してもらう", "Get store visits booked", "방문 예약 받기"),
                    "hint": _l("店舗を見て、地図を開いて、来店予約", "See the store, open the map, book a visit", "매장 보고 지도 열고 방문 예약"),
                    "steps": ["view_item", "click", "form_start", "form_submit"], "primary": "form_submit",
                    "signup_label": _l("来店予約", "Visit bookings", "방문 예약"),
                    "cvr_label": _l("来店予約CVR", "Visit booking CVR", "방문 예약 CVR"),
                    "industries": ["food", "beauty", "clinic", "realestate", "auto", "travel"]},
    "membership": {"group": "member", "rep": "b2c", "keep_copy": True,
                   "label": _l("会員になって使い続ける", "Sign up and stay", "회원 가입 후 계속 이용"),
                   "hint": _l("登録して、ログインして、有料へ", "Sign up, log in, go paid", "가입 → 로그인 → 유료 전환"),
                   "steps": ["sign_up", "login", "begin_checkout", "purchase"], "primary": "sign_up"},
    "free_trial": {"group": "member", "rep": "saas",
                   "label": _l("無料トライアルを始めてもらう", "Get free-trial starts", "무료 체험 시작"),
                   "hint": _l("料金を見て、トライアル登録、ログインして使う", "See pricing, start the trial, log in", "요금 보고 체험 등록, 로그인해 이용"),
                   "steps": ["view_item", "sign_up", "login"], "primary": "sign_up",
                   "signup_label": _l("トライアル登録", "Trial sign-ups", "체험 등록"),
                   "cvr_label": _l("トライアルCVR", "Trial CVR", "체험 CVR"),
                   "industries": ["saas", "b2c", "edu", "it_services"]},
    "app_download": {"group": "member", "rep": "b2c",
                     "label": _l("アプリをダウンロードしてもらう", "Get app downloads", "앱 다운로드 받기"),
                     "hint": _l("アプリを知って、ストアへ移動", "Learn about the app, go to the store", "앱을 알고 스토어로 이동"),
                     "steps": ["scroll", "view_item", "click"], "primary": "click",
                     "signup_label": _l("ストアへ移動", "Store visits", "스토어 이동"),
                     "cvr_label": _l("ストア移動率", "Store-visit rate", "스토어 이동률"),
                     "industries": ["b2c", "community", "creator", "food", "finance"]},
    "members_only": {"group": "member", "rep": "news",
                     "label": _l("会員限定コンテンツで登録してもらう", "Members-only content sign-ups", "회원 전용 콘텐츠로 가입"),
                     "hint": _l("限定記事の入口を見て、登録・ログイン", "Hit a members-only article, sign up or log in", "전용 글 입구에서 가입·로그인"),
                     "steps": ["view_item", "sign_up", "login"], "primary": "sign_up",
                     "signup_label": _l("会員登録", "Sign-ups", "회원가입"),
                     "cvr_label": _l("登録CVR", "Sign-up CVR", "가입 CVR"),
                     "industries": ["news", "content", "b2c", "community", "creator"]},
    "content": {"group": "read", "rep": "content",
                "label": _l("読んで登録・購読する", "Read and subscribe", "읽고 구독·등록"),
                "hint": _l("記事を読んで、会員登録・購読へ", "Read, then sign up or subscribe", "읽고 회원가입·구독"),
                "steps": ["scroll", "click", "sign_up"], "primary": "sign_up",
                "signup_label": _l("登録・購読", "Sign-ups", "가입·구독"),
                "cvr_label": _l("登録CVR", "Sign-up CVR", "가입 CVR")},
    "blog": {"group": "read", "rep": "content",
             "label": _l("ブログ・記事を読んでもらう", "Blog: get articles read", "블로그·글 읽히기"),
             "hint": _l("記事を読んで、ほかの記事やリンクへ進む", "Read, then go on to other articles or links", "글을 읽고 다른 글·링크로"),
             "steps": ["scroll", "view_search_results", "click"], "primary": "click",
             "signup_label": _l("リンククリック", "Link clicks", "링크 클릭"),
             "cvr_label": _l("クリック率", "Click rate", "클릭률"),
             "industries": []},
    "video": {"group": "read", "rep": "content",
              "label": _l("動画を見てもらう", "Get videos watched", "동영상 시청"),
              "hint": _l("動画を再生して、最後まで見る", "Play a video and watch to the end", "동영상 재생 후 끝까지 시청"),
              "steps": ["video_start", "video_progress", "video_complete"], "primary": "video_complete",
              "signup_label": _l("最後まで視聴", "Watched to the end", "끝까지 시청"),
              "cvr_label": _l("完全視聴率", "Completion rate", "완전 시청률"),
              "industries": ["content", "creator", "edu", "news"]},
}

for _b in BEHAVIORS.values():
    _b["flow"] = UNIVERSAL_STEPS + _b["steps"]

BOARD_TEXT_FIELDS = ("signup_label", "cvr_label", "mid_label", "bottom_label", "rate_a_label", "rate_b_label")
_RATE = {"ja": "{a}→{b}率", "en": "{a} → {b}", "ko": "{a}→{b}율"}


def board_events(cat: str) -> dict[str, str]:
    """primary / mid / bottom events the board counts (mid, bottom = the steps before the primary)."""
    b = BEHAVIORS[cat]
    flow = b["flow"]
    i = flow.index(b["primary"])
    return {"primary": b["primary"], "mid": flow[max(i - 1, 0)], "bottom": flow[max(i - 2, 0)]}


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
    if not is_behavior(slug) or field not in BOARD_TEXT_FIELDS:
        return None
    cat = category_of(slug)
    b = BEHAVIORS[cat]
    if b.get("keep_copy"):
        return None
    if field in ("signup_label", "cvr_label"):
        return b[field].get(locale) or b[field]["ja"]
    from sitekpi.packs.flows import step_label

    ev = board_events(cat)
    mid, bottom = step_label(ev["mid"], locale, slug), step_label(ev["bottom"], locale, slug)
    primary = b["signup_label"].get(locale) or b["signup_label"]["ja"]
    rate = _RATE.get(locale) or _RATE["ja"]
    return {"mid_label": mid, "bottom_label": bottom,
            "rate_a_label": rate.format(a=mid, b=primary),
            "rate_b_label": rate.format(a=bottom, b=primary)}[field]


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
