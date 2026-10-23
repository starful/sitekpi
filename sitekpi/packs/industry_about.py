"""One line per industry for step ② — what is characteristic about its numbers."""

from __future__ import annotations


def _l(ja: str, en: str, ko: str) -> dict[str, str]:
    return {"ja": ja, "en": en, "ko": ko}


ABOUT: dict[str, dict[str, str]] = {
    "b2c": _l("無料登録は多いが、有料・継続まで残る人は少なめ", "Many free sign-ups; fewer stay and pay", "무료 가입은 많고 유료·유지까지 남는 사람은 적은 편"),
    "saas": _l("比較検討が長く、トライアル→有料化が勝負", "Long evaluation; trial-to-paid is what counts", "비교 검토가 길고 체험→유료 전환이 관건"),
    "community": _l("登録より、その後の参加・投稿が続くかが大事", "Joining matters less than coming back to take part", "가입보다 이후 참여·게시가 이어지는지가 중요"),
    "content": _l("検索流入が多く、1 ページで帰る人も多い", "Lots of search traffic; many leave after one page", "검색 유입이 많고 한 페이지만 보고 나가는 사람도 많음"),
    "news": _l("回遊と再訪が多く、購読への転換は少なめ", "Frequent return visits; few convert to subscriptions", "회유·재방문이 많고 구독 전환은 적은 편"),
    "creator": _l("SNS からの流入が中心で、視聴の長さが鍵", "Mostly social traffic; watch time is key", "SNS 유입 중심, 시청 시간이 핵심"),
    "hr": _l("求人を何件も見比べてから応募する", "People compare many jobs before applying", "여러 공고를 비교한 뒤 지원"),
    "parttime": _l("スマホから短時間で応募まで進む", "Quick applications, mostly on phones", "스마트폰으로 짧은 시간에 지원까지 진행"),
    "agency": _l("登録・面談がゴール。検討期間は長め", "Goal is registering for a consultation; longer decisions", "등록·면담이 목표, 검토 기간이 긴 편"),
    "construction": _l("施工事例を見て、数週間かけて問い合わせる", "Visitors study past work for weeks before asking", "시공 사례를 보고 몇 주에 걸쳐 문의"),
    "b2b": _l("資料DLから商談へ。1 件の重みが大きい", "From downloads to sales talks; each lead counts", "자료 DL에서 상담으로, 리드 한 건의 비중이 큼"),
    "realestate": _l("物件を何度も見比べ、内見予約がゴール", "Listings compared repeatedly; viewings are the goal", "매물을 여러 번 비교하고 방문 예약이 목표"),
    "manufacturing": _l("技術資料・仕様の確認が多く、問い合わせは少数", "Heavy spec and document reading; few inquiries", "기술 자료·사양 확인이 많고 문의는 소수"),
    "it_services": _l("事例と料金を確認して、相談・見積もりへ", "Case studies and pricing lead to a consultation", "사례와 요금을 확인하고 상담·견적으로"),
    "legal": _l("悩みを検索して来て、相談予約まで迷いやすい", "Visitors arrive via a worry; booking takes courage", "고민을 검색해서 오고, 상담 예약까지 망설이기 쉬움"),
    "home_service": _l("急ぎの依頼が多く、電話・見積もりが中心", "Often urgent; calls and quotes dominate", "급한 의뢰가 많고 전화·견적 중심"),
    "auto": _l("在庫車を比較し、試乗・来店予約がゴール", "Stock is compared; test drives are the goal", "재고 차량을 비교하고 시승·방문 예약이 목표"),
    "ec": _l("カートに入れても、半分以上が買わずに離れる", "Over half of carts are abandoned", "장바구니에 담아도 절반 이상이 구매하지 않음"),
    "marketplace": _l("サイト内検索が多く、出品の比較が中心", "Heavy on-site search and comparing listings", "사이트 내 검색이 많고 상품 비교가 중심"),
    "d2c": _l("広告・SNS 流入が多く、定期購入が鍵", "Mostly ad and social traffic; repeat orders are key", "광고·SNS 유입이 많고 정기 구매가 관건"),
    "apparel": _l("スマホ比率が高く、閲覧は多いが購入率は低め", "Mobile-heavy; lots of browsing, lower purchase rate", "모바일 비중이 높고 열람은 많지만 구매율은 낮은 편"),
    "food_ec": _l("リピート購入が多く、購入率は高め", "Many repeat buyers; higher purchase rate", "재구매가 많고 구매율이 높은 편"),
    "furniture_ec": _l("高単価で検討期間が長く、購入率は低め", "Expensive items, long decisions, lower purchase rate", "고단가라 검토 기간이 길고 구매율은 낮은 편"),
    "edu": _l("体験・説明会の申込がゴール。保護者の検討も入る", "Trial lessons and info sessions; families decide together", "체험·설명회 신청이 목표, 보호자 검토도 포함"),
    "finance": _l("見積もり・シミュレーションから申込へ。離脱が多い", "Quotes and simulators lead to long forms with drop-off", "견적·시뮬레이션에서 신청으로, 이탈이 많음"),
    "gov": _l("目的の手続きを探して来る。迷わず着けるかが大事", "People come for one procedure; findability matters", "필요한 절차를 찾아서 옴, 헤매지 않는지가 중요"),
    "clinic": _l("地域検索から来て、予約・電話がゴール", "Local search visitors; bookings and calls are the goal", "지역 검색으로 와서 예약·전화가 목표"),
    "beauty": _l("メニューと口コミを見て予約。スマホ中心", "Menu and reviews, then a booking, mostly on phones", "메뉴와 후기를 보고 예약, 모바일 중심"),
    "travel": _l("日程・空室の検索が多く、予約まで時間がかかる", "Lots of date and availability searches; slow to book", "일정·빈방 검색이 많고 예약까지 시간이 걸림"),
    "food": _l("メニュー・地図を見て来店。サイト内の予約は一部", "Menu and map, then a visit; few book online", "메뉴·지도를 보고 방문, 사이트 예약은 일부"),
}


def industry_about(slug: str, locale: str) -> str:
    row = ABOUT.get(slug) or {}
    return row.get(locale) or row.get("ja") or ""
