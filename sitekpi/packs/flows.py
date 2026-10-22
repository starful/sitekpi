"""行動フロー: the steps a visitor takes in each industry pack (entry → … → conversion).

Each pack lists 3–4 GA4 events in the order people usually do them. The flow
starts with 流入 (users who arrived) and ends at the pack's main conversion
or the step right after it. A connected site can map any step to its own
event name (see sitekpi/flow.py).
"""

from __future__ import annotations

FLOW_STEPS: dict[str, list[str]] = {
    "b2c": ["sign_up", "trial_start", "pay_start", "pay_success"],
    "saas": ["view_pricing", "trial_start", "pay_start", "pay_success"],
    "community": ["sign_up", "profile_complete", "pay_start", "pay_success"],
    "content": ["scroll_90", "click_cta", "newsletter_signup"],
    "news": ["article_view", "paywall_view", "click_cta", "newsletter_signup"],
    "creator": ["content_view", "like", "follow", "membership_join"],
    "hr": ["job_view", "apply_start", "apply_submit", "entry_complete"],
    "parttime": ["job_view", "apply_start", "apply_submit", "shift_confirm"],
    "agency": ["candidate_view", "match_start", "apply_submit", "interview_book"],
    "construction": ["project_view", "inquiry_start", "inquiry_submit", "site_visit_book"],
    "ec": ["view_item", "add_to_cart", "begin_checkout", "purchase"],
    "marketplace": ["view_item", "add_to_cart", "begin_checkout", "purchase"],
    "d2c": ["view_item", "add_to_cart", "begin_checkout", "purchase"],
    "b2b": ["case_view", "pricing_view", "whitepaper_dl", "contact_submit"],
    "edu": ["course_view", "trial_book", "enroll_start", "enroll_complete"],
    "clinic": ["service_view", "price_view", "reserve_start", "reserve_complete"],
    "beauty": ["menu_view", "style_view", "book_start", "book_complete"],
    "finance": ["product_view", "quote_complete", "apply_start", "apply_complete"],
    "travel": ["view_offer", "select_room", "book_start", "purchase"],
    "realestate": ["listing_view", "inquiry_start", "inquiry_submit", "tour_book"],
    "food": ["menu_view", "store_view", "reserve_start", "reserve_complete"],
    "gov": ["guide_view", "form_start", "doc_upload", "form_complete"],
}

# Short behaviour labels (what the person did), ja / en / ko.
STEP_LABELS: dict[str, dict[str, str]] = {
    "sign_up": {"ja": "会員登録", "en": "Signed up", "ko": "회원가입"},
    "trial_start": {"ja": "トライアル開始", "en": "Started trial", "ko": "체험 시작"},
    "pay_start": {"ja": "決済を開始", "en": "Started payment", "ko": "결제 시작"},
    "pay_success": {"ja": "支払い完了", "en": "Paid", "ko": "결제 완료"},
    "view_pricing": {"ja": "料金を見た", "en": "Viewed pricing", "ko": "요금 확인"},
    "profile_complete": {"ja": "プロフィール完成", "en": "Completed profile", "ko": "프로필 완성"},
    "scroll_90": {"ja": "記事を読み切った", "en": "Read to the end", "ko": "끝까지 읽음"},
    "click_cta": {"ja": "CTAをクリック", "en": "Clicked CTA", "ko": "CTA 클릭"},
    "newsletter_signup": {"ja": "メルマガ登録", "en": "Joined newsletter", "ko": "뉴스레터 구독"},
    "article_view": {"ja": "記事を見た", "en": "Viewed article", "ko": "기사 열람"},
    "paywall_view": {"ja": "有料の壁を見た", "en": "Hit paywall", "ko": "페이월 노출"},
    "content_view": {"ja": "作品を見た", "en": "Viewed content", "ko": "콘텐츠 열람"},
    "like": {"ja": "いいね", "en": "Liked", "ko": "좋아요"},
    "follow": {"ja": "フォロー", "en": "Followed", "ko": "팔로우"},
    "membership_join": {"ja": "メンバー加入", "en": "Joined membership", "ko": "멤버십 가입"},
    "job_view": {"ja": "求人を見た", "en": "Viewed job", "ko": "공고 열람"},
    "apply_start": {"ja": "応募を開始", "en": "Started application", "ko": "지원 시작"},
    "apply_submit": {"ja": "応募を送信", "en": "Submitted application", "ko": "지원 제출"},
    "entry_complete": {"ja": "エントリー完了", "en": "Entry completed", "ko": "엔트리 완료"},
    "shift_confirm": {"ja": "シフト確定", "en": "Shift confirmed", "ko": "근무 확정"},
    "candidate_view": {"ja": "候補者を見た", "en": "Viewed candidate", "ko": "후보자 열람"},
    "match_start": {"ja": "マッチング開始", "en": "Started matching", "ko": "매칭 시작"},
    "interview_book": {"ja": "面接を予約", "en": "Booked interview", "ko": "면접 예약"},
    "project_view": {"ja": "施工例を見た", "en": "Viewed project", "ko": "시공 사례 열람"},
    "inquiry_start": {"ja": "問い合わせ開始", "en": "Started inquiry", "ko": "문의 시작"},
    "inquiry_submit": {"ja": "問い合わせ送信", "en": "Sent inquiry", "ko": "문의 제출"},
    "site_visit_book": {"ja": "現地調査を予約", "en": "Booked site visit", "ko": "현장 방문 예약"},
    "view_item": {"ja": "商品を見た", "en": "Viewed item", "ko": "상품 열람"},
    "add_to_cart": {"ja": "カートに追加", "en": "Added to cart", "ko": "장바구니 담기"},
    "begin_checkout": {"ja": "購入手続きへ", "en": "Began checkout", "ko": "결제 단계 진입"},
    "purchase": {"ja": "購入", "en": "Purchased", "ko": "구매"},
    "case_view": {"ja": "導入事例を見た", "en": "Viewed case study", "ko": "도입 사례 열람"},
    "pricing_view": {"ja": "料金を見た", "en": "Viewed pricing", "ko": "요금 확인"},
    "whitepaper_dl": {"ja": "資料DL", "en": "Downloaded paper", "ko": "자료 다운로드"},
    "contact_submit": {"ja": "問い合わせ送信", "en": "Sent contact form", "ko": "문의 제출"},
    "course_view": {"ja": "講座を見た", "en": "Viewed course", "ko": "강좌 열람"},
    "trial_book": {"ja": "体験を予約", "en": "Booked trial", "ko": "체험 예약"},
    "enroll_start": {"ja": "申込を開始", "en": "Started enrolment", "ko": "신청 시작"},
    "enroll_complete": {"ja": "申込完了", "en": "Enrolled", "ko": "신청 완료"},
    "service_view": {"ja": "診療内容を見た", "en": "Viewed service", "ko": "진료 안내 열람"},
    "price_view": {"ja": "料金を見た", "en": "Viewed prices", "ko": "가격 확인"},
    "reserve_start": {"ja": "予約を開始", "en": "Started booking", "ko": "예약 시작"},
    "reserve_complete": {"ja": "予約完了", "en": "Booked", "ko": "예약 완료"},
    "menu_view": {"ja": "メニューを見た", "en": "Viewed menu", "ko": "메뉴 열람"},
    "style_view": {"ja": "スタイルを見た", "en": "Viewed styles", "ko": "스타일 열람"},
    "book_start": {"ja": "予約を開始", "en": "Started booking", "ko": "예약 시작"},
    "book_complete": {"ja": "予約完了", "en": "Booked", "ko": "예약 완료"},
    "product_view": {"ja": "商品を見た", "en": "Viewed product", "ko": "상품 열람"},
    "quote_complete": {"ja": "見積もり完了", "en": "Got a quote", "ko": "견적 완료"},
    "apply_complete": {"ja": "申込完了", "en": "Applied", "ko": "신청 완료"},
    "view_offer": {"ja": "プランを見た", "en": "Viewed offer", "ko": "상품 열람"},
    "select_room": {"ja": "部屋を選んだ", "en": "Chose a room", "ko": "객실 선택"},
    "listing_view": {"ja": "物件を見た", "en": "Viewed listing", "ko": "매물 열람"},
    "tour_book": {"ja": "内見を予約", "en": "Booked viewing", "ko": "방문 예약"},
    "store_view": {"ja": "店舗情報を見た", "en": "Viewed store", "ko": "매장 정보 열람"},
    "guide_view": {"ja": "案内を見た", "en": "Viewed guide", "ko": "안내 열람"},
    "form_start": {"ja": "申請を開始", "en": "Started form", "ko": "신청 시작"},
    "doc_upload": {"ja": "書類を提出", "en": "Uploaded documents", "ko": "서류 제출"},
    "form_complete": {"ja": "申請完了", "en": "Form completed", "ko": "신청 완료"},
}


# Same event name, different wording in a given industry.
PACK_STEP_LABELS: dict[tuple[str, str], dict[str, str]] = {
    ("finance", "apply_start"): {"ja": "申込を開始", "en": "Started application", "ko": "신청 시작"},
    ("parttime", "job_view"): {"ja": "求人を見た", "en": "Viewed shift job", "ko": "알바 공고 열람"},
    ("marketplace", "view_item"): {"ja": "出品を見た", "en": "Viewed listing", "ko": "상품 열람"},
}


def _add_behavior_flows() -> None:
    from sitekpi.packs.behaviors import BEHAVIORS, slug_of
    from sitekpi.packs.derived import DERIVED

    for dslug, spec in DERIVED.items():
        FLOW_STEPS[dslug] = list(FLOW_STEPS[spec["base"]])
        for ev, labels in (spec.get("steps") or {}).items():
            PACK_STEP_LABELS[(dslug, ev)] = labels

    for cat, beh in BEHAVIORS.items():
        FLOW_STEPS[slug_of(cat)] = list(FLOW_STEPS[beh["rep"]])


_add_behavior_flows()


def step_label(event: str, locale: str, pack: str = "") -> str:
    from sitekpi.packs.behaviors import rep_of

    labels = (PACK_STEP_LABELS.get((pack, event)) or PACK_STEP_LABELS.get((rep_of(pack), event))
              or STEP_LABELS.get(event) or {})
    return labels.get(locale) or labels.get("ja") or event
