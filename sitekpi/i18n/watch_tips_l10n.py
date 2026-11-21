"""今見るべきこと · 見るポイント by 訪問者の行動 (docs/plan 「정할 것」: 見るポイント를 행동별로).

A watch row used to show the metric's common tip (metrics/help.py). The same number means different things
on a shop, a contact form or a blog, so the tip now comes from here first:

    BY_BEHAVIOR[behavior][bench key]  →  BY_GROUP[group][bench key]  →  the metric's common tip

Groups and behaviors are the keys of packs/behaviors.py (GROUPS · BEHAVIORS). Bench keys are the 業界目安 keys
(engaged_rate, bounce_rate, signup_rate = 主CVR, pages_session, signup_to_pay …). These are where to look,
not a diagnosis. Every entry has ja · en · ko.
"""

from __future__ import annotations

Tip = dict[str, str]

BY_GROUP: dict[str, dict[str, Tip]] = {
    "buy": {
        "engaged_rate": {
            "ja": "商品一覧・商品ページを開いてすぐ閉じていないか。入口ページ別に、広告や SNS から来た商品ページの参加率を見比べる。",
            "en": "Are people closing listing and product pages right away? Compare engagement by landing page, especially product pages reached from ads or social.",
            "ko": "상품 목록·상품 페이지를 열자마자 닫는지. 입구 페이지별로, 광고·SNS에서 들어온 상품 페이지의 참여율을 비교한다.",
        },
        "bounce_rate": {
            "ja": "1 ページで帰る人が多い入口を探す。広告の訴求と、着地した商品ページ（価格・在庫・写真）がずれていないか。",
            "en": "Find the landing pages people leave after one page. Does the ad's promise match the product page they land on (price, stock, photos)?",
            "ko": "한 페이지만 보고 나가는 입구를 찾는다. 광고 문구와 도착한 상품 페이지(가격·재고·사진)가 어긋나지 않는지.",
        },
        "signup_rate": {
            "ja": "購入まで進んだ人の割合。流れで「カート追加 → 購入」のどこで落ちるかを見て、送料・支払い方法・会員登録の強制を確認する。",
            "en": "The share who bought. Use the flow to see where “add to cart → purchase” drops, then check shipping costs, payment options and forced sign-up.",
            "ko": "구매까지 간 사람의 비율. 흐름에서 「장바구니 → 구매」 중 어디서 떨어지는지 보고, 배송비·결제 수단·회원가입 강제를 확인한다.",
        },
        "pages_session": {
            "ja": "商品を見比べられているか。少ないなら関連商品・カテゴリへの道、多すぎるなら目当ての商品が見つからない可能性。",
            "en": "Can people compare products? Low: add related products and category links. Very high: they may not be finding what they came for.",
            "ko": "상품을 비교해 볼 수 있는지. 적으면 관련 상품·카테고리 동선, 너무 많으면 원하는 상품을 못 찾는 것일 수 있다.",
        },
    },
    "contact": {
        "engaged_rate": {
            "ja": "サービス紹介・事例ページがしっかり読まれているか。問い合わせの前に読まれるページの参加率を入口別に見る。",
            "en": "Are the service and case-study pages being read? Check engagement by landing page for the pages people read before contacting you.",
            "ko": "서비스 소개·사례 페이지가 제대로 읽히는지. 문의 전에 읽는 페이지의 참여율을 입구별로 본다.",
        },
        "bounce_rate": {
            "ja": "入口ページに問い合わせ・資料請求への道（ボタン・電話番号）が見えているか。検索語と入口ページの内容がずれていないか。",
            "en": "Is the way to contact or request materials (button, phone number) visible on the landing page? Do search terms match what the page offers?",
            "ko": "입구 페이지에 문의·자료 요청으로 가는 길(버튼·전화번호)이 보이는지. 검색어와 입구 페이지 내용이 어긋나지 않는지.",
        },
        "signup_rate": {
            "ja": "フォームを開いた人のうち送信した割合も一緒に見る。項目数・必須項目・エラーの出し方がつまずきになりやすい。",
            "en": "Look at it together with the share who submitted after opening the form. The number of fields, required fields and error messages are the usual snags.",
            "ko": "폼을 연 사람 중 보낸 비율도 함께 본다. 항목 수·필수 항목·오류 표시가 걸림돌이 되기 쉽다.",
        },
        "pages_session": {
            "ja": "料金・事例・会社情報まで進めているか。少なければ、比べるのに必要な情報への道を見直す。",
            "en": "Do people reach pricing, case studies and company info? If not, review the links to what they need to compare.",
            "ko": "요금·사례·회사 정보까지 가는지. 적으면 비교에 필요한 정보로 가는 동선을 다시 본다.",
        },
    },
    "visit": {
        "engaged_rate": {
            "ja": "地図・営業時間・メニュー（料金）など、来店・予約の前に知りたい情報がすぐ見つかるか。",
            "en": "Can people quickly find what they need before visiting or booking — map, opening hours, menu and prices?",
            "ko": "지도·영업시간·메뉴(요금) 등 방문·예약 전에 알고 싶은 정보를 바로 찾을 수 있는지.",
        },
        "bounce_rate": {
            "ja": "スマホで 1 ページだけ見て帰る人が多いか。電話番号や地図がそのページで足りて帰った可能性もある（悪いとは限らない）。",
            "en": "Many phone visitors leave after one page? They may have got the phone number or map they needed — not always a bad sign.",
            "ko": "휴대폰에서 한 페이지만 보고 나가는 사람이 많은지. 전화번호·지도를 그 페이지에서 얻고 나갔을 수도 있다(나쁜 것만은 아니다).",
        },
        "signup_rate": {
            "ja": "予約まで進んだ割合。空き枠の見つけやすさと、外部の予約サイトへ移るところで計測が切れていないかを確認する。",
            "en": "The share who booked. Check how easy it is to find a free slot, and whether tracking stops when people move to an external booking site.",
            "ko": "예약까지 간 비율. 빈 시간을 찾기 쉬운지, 외부 예약 사이트로 넘어갈 때 측정이 끊기지 않는지 확인한다.",
        },
        "pages_session": {
            "ja": "メニュー・料金・アクセスの順に回れているか。",
            "en": "Do people move through menu, prices and directions?",
            "ko": "메뉴·요금·오시는 길 순서로 둘러보는지.",
        },
    },
    "member": {
        "engaged_rate": {
            "ja": "登録の前に機能・料金ページが読まれているか。初めての人とリピーターを分けて見る。",
            "en": "Are feature and pricing pages read before sign-up? Look at new and returning visitors separately.",
            "ko": "가입 전에 기능·요금 페이지가 읽히는지. 처음 온 사람과 재방문자를 나눠 본다.",
        },
        "bounce_rate": {
            "ja": "入口で「何ができるサービスか」「無料か」「登録の手間」がすぐ伝わっているか。",
            "en": "Does the landing page say right away what the service does, whether it's free and how much effort sign-up takes?",
            "ko": "입구에서 「무엇을 할 수 있는 서비스인지」 「무료인지」 「가입이 얼마나 번거로운지」가 바로 전해지는지.",
        },
        "signup_rate": {
            "ja": "登録フォームを開いた人のうち完了した割合。メール確認・SNS ログインの途中で離れやすい。",
            "en": "The share who finished after opening the sign-up form. Email confirmation and social login steps are where people tend to drop.",
            "ko": "가입 폼을 연 사람 중 완료한 비율. 메일 인증·SNS 로그인 도중에 빠지기 쉽다.",
        },
        "pages_session": {
            "ja": "料金・機能比較・よくある質問まで見ているか。",
            "en": "Do people get as far as pricing, feature comparison and the FAQ?",
            "ko": "요금·기능 비교·자주 묻는 질문까지 보는지.",
        },
    },
    "read": {
        "engaged_rate": {
            "ja": "記事が読まれているか。検索から来た記事の参加率を記事別に比べ、低い記事は冒頭で答えを出しているかを見る。",
            "en": "Are articles being read? Compare engagement per article for search visitors; for low ones, check the answer comes early.",
            "ko": "기사가 읽히는지. 검색으로 들어온 기사의 참여율을 기사별로 비교하고, 낮은 기사는 앞부분에서 답을 주는지 본다.",
        },
        "bounce_rate": {
            "ja": "読み物のサイトでは 1 記事で帰るのは普通。次の記事へ進む人の割合と、記事がしっかり読まれたか（参加率）と合わせて見る。",
            "en": "On a reading site, leaving after one article is normal. Read it with the share who go on to another article and with engagement.",
            "ko": "읽을거리 사이트에서는 기사 하나만 보고 나가는 게 보통이다. 다음 기사로 가는 비율, 참여율과 함께 본다.",
        },
        "signup_rate": {
            "ja": "読者が会員登録・メルマガなど次の行動に進む割合。記事の途中・末尾の案内の位置と文言を確認する。",
            "en": "The share of readers who take the next step (sign-up, newsletter). Check where the call-out sits in the article and what it says.",
            "ko": "독자가 회원가입·뉴스레터 등 다음 행동으로 가는 비율. 기사 중간·끝 안내의 위치와 문구를 확인한다.",
        },
        "pages_session": {
            "ja": "関連記事・カテゴリから次の記事へ進めているか。",
            "en": "Do related-article and category links lead people to another article?",
            "ko": "관련 기사·카테고리에서 다음 기사로 넘어가는지.",
        },
    },
}

BY_BEHAVIOR: dict[str, dict[str, Tip]] = {
    "commerce": {
        "signup_to_pay": {
            "ja": "カートに入れたのに買わなかった人。送料・合計金額が分かるタイミング、支払い方法の数、会員登録の強制を確認する。",
            "en": "People who added to cart but didn't buy. Check when shipping and the total appear, how many payment options there are, and forced sign-up.",
            "ko": "장바구니에 넣고 사지 않은 사람. 배송비·총액이 보이는 시점, 결제 수단 수, 회원가입 강제를 확인한다.",
        },
    },
    "comparison": {
        "signup_rate": {
            "ja": "比較から外部サイトへのクリックを数えている。比較表のボタンの位置と、比べたい項目がそろっているかを確認する。",
            "en": "This counts clicks out to the compared sites. Check where the buttons sit in the comparison table and whether the items people compare are all there.",
            "ko": "비교에서 외부 사이트로 가는 클릭을 센다. 비교표 버튼 위치와, 비교하고 싶은 항목이 다 있는지 확인한다.",
        },
    },
    "donation": {
        "signup_rate": {
            "ja": "寄付の完了まで進んだ割合。金額の選び方と、支払い方法の少なさでつまずいていないか。",
            "en": "The share who completed a donation. Are people stuck on choosing an amount or on too few payment options?",
            "ko": "기부 완료까지 간 비율. 금액 고르기나 결제 수단이 적어서 막히지 않는지.",
        },
    },
    "call_line": {
        "signup_rate": {
            "ja": "電話・LINE ボタンのクリックを数えている。スマホで押しやすい位置にあるか、営業時間外の表示も確認する。",
            "en": "This counts phone and LINE button clicks. Check the button is easy to tap on phones, and what it says outside opening hours.",
            "ko": "전화·LINE 버튼 클릭을 센다. 휴대폰에서 누르기 쉬운 위치인지, 영업시간 외 표시도 확인한다.",
        },
    },
    "app_download": {
        "signup_rate": {
            "ja": "ストアへのリンクのクリックを数えている。実際のインストール数はストア側の数字で確かめる。",
            "en": "This counts clicks on the store links. Confirm actual installs in the app store's own numbers.",
            "ko": "스토어 링크 클릭을 센다. 실제 설치 수는 스토어 쪽 숫자로 확인한다.",
        },
    },
    "video": {
        "signup_rate": {
            "ja": "動画を最後まで見た人の割合。冒頭の数秒で離れていないか、動画の長さと置き場所を確認する。",
            "en": "The share who watched to the end. Check whether people leave in the first seconds, and the video's length and placement.",
            "ko": "영상을 끝까지 본 사람의 비율. 처음 몇 초 만에 떠나지 않는지, 영상 길이와 위치를 확인한다.",
        },
    },
}


def watch_tip(behavior: str, group: str, bench_key: str, locale: str) -> str:
    """The behavior's 見るポイント for this metric, or "" (callers fall back to the metric's common tip)."""
    for tip in ((BY_BEHAVIOR.get(behavior) or {}).get(bench_key), (BY_GROUP.get(group) or {}).get(bench_key)):
        if tip:
            return tip.get(locale) or tip["ja"]
    return ""
