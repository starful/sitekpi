"""Pack-owned labels / notes / biz copy (ja / en / ko)."""

from __future__ import annotations

from typing import Any

# slug -> field -> {ja,en,ko}  (biz/notes nested)
PACK_L10N: dict[str, dict[str, Any]] = {
  "b2c": {
    "label": {'ja': '会員・サブスク', 'en': 'Membership & subscription', 'ko': '회원·구독'},
    "hint": {'ja': '登録〜課金', 'en': 'Sign-up → paid', 'ko': '가입〜결제'},
    "signup_label": {'ja': '新規会員登録', 'en': 'New sign-ups', 'ko': '신규 회원 가입'},
    "property": {'ja': 'Demo Shop JP', 'en': 'Demo Shop JP', 'ko': 'Demo Shop JP'},
    "cvr_label": {'ja': '登録CVR', 'en': 'Sign-up CVR', 'ko': '가입 CVR'},
    "mid_label": {'ja': '有料開始', 'en': 'Start paid', 'ko': '유료 시작'},
    "bottom_label": {'ja': '有料完了', 'en': 'Paid complete', 'ko': '유료 완료'},
    "rate_a_label": {'ja': '登録→有料開始率', 'en': 'Sign-up → paid start', 'ko': '가입→유료 시작률'},
    "rate_b_label": {'ja': '決済CVR', 'en': 'Checkout CVR', 'ko': '결제 CVR'},
    "biz": {
      "members_db": {
        "label": {"ja": '会員数（DB）', "en": 'Members (DB)', "ko": '회원 수(DB)'},
        "meaning": {"ja": '業務DBの有効会員数', "en": 'Active members in business DB', "ko": '업무 DB의 유효 회원 수'},
        "formula": {"ja": 'COUNT(有効会員)', "en": 'COUNT(active members)', "ko": 'COUNT(유효 회원)'},
      },
      "paid_members": {
        "label": {"ja": '有料会員数（DB）', "en": 'Paid members (DB)', "ko": '유료 회원 수(DB)'},
        "meaning": {"ja": '有料プラン中の会員', "en": 'Members on a paid plan', "ko": '유료 플랜 회원'},
        "formula": {"ja": 'COUNT(有料かつ有効)', "en": 'COUNT(paid & active)', "ko": 'COUNT(유료·유효)'},
      },
      "paid_rate": {
        "label": {"ja": '有料化率', "en": 'Paid rate', "ko": '유료화율'},
        "meaning": {"ja": '全会員のうち有料割合', "en": 'Share of members who are paid', "ko": '전체 회원 중 유료 비율'},
        "formula": {"ja": '有料会員 ÷ 会員 × 100', "en": 'Paid ÷ members × 100', "ko": '유료 ÷ 회원 × 100'},
      },
      "revenue": {
        "label": {"ja": '売上（期間）', "en": 'Revenue (period)', "ko": '매출(기간)'},
        "meaning": {"ja": '課金・会計側の期間売上', "en": 'Billing/accounting revenue', "ko": '과금·회계 기간 매출'},
        "formula": {"ja": 'SUM(期間売上)', "en": 'SUM(period revenue)', "ko": 'SUM(기간 매출)'},
      },
      "arpu": {
        "label": {"ja": 'ARPU', "en": 'ARPU', "ko": 'ARPU'},
        "meaning": {"ja": '会員1人あたり売上', "en": 'Revenue per member', "ko": '회원 1인당 매출'},
        "formula": {"ja": '売上 ÷ 会員数', "en": 'Revenue ÷ members', "ko": '매출 ÷ 회원 수'},
      },
      "churn_rate": {
        "label": {"ja": '解約率', "en": 'Churn rate', "ko": '해지율'},
        "meaning": {"ja": '期間中の退会割合', "en": 'Cancellations in the period', "ko": '기간 중 탈퇴 비율'},
        "formula": {"ja": '退会 ÷ 会員 × 100', "en": 'Churn ÷ members × 100', "ko": '탈퇴 ÷ 회원 × 100'},
      },
    },
    "notes": {
      "7d": [
        {"ja": 'UUは伸びているが、新規比率が高め。獲得コストを要確認。', "en": 'UU is up but new-user share is high — check acquisition cost.', "ko": 'UU는 늘었지만 신규 비중이 높음. 획득 비용을 확인하세요.'},
        {"ja": 'sign_up → pay_success の落差が大きい週は、料金ページを疑う。', "en": 'Large drop from sign_up → pay_success: check the pricing page.', "ko": 'sign_up → pay_success 낙차가 큰 주는 요금 페이지를 의심하세요.'},
        {"ja": '会員数(DB)とGAの新規登録が乖離したら計測漏れを疑う。', "en": 'If DB members diverge from GA sign-ups, suspect tracking gaps.', "ko": '회원 수(DB)와 GA 신규 가입이 어긋나면 계측 누락을 의심하세요.'},
      ],
      "28d": [
        {"ja": '月次ではOrganicが安定。Paidは週ごとの振れが大きい。', "en": 'Monthly: Organic is steady; Paid swings week to week.', "ko": '월간으로는 Organic이 안정. Paid는 주간 변동이 큼.'},
        {"ja": '再訪UUが6割前後なら、コンテンツ/通知の効きを見る段階。', "en": 'If returning UU is ~60%, review content/notification effectiveness.', "ko": '재방문 UU가 60% 전후면 콘텐츠/알림 효과를 볼 단계.'},
        {"ja": '有料完了と売上(業務)を並べて、返金や計上ズレも確認する。', "en": 'Compare paid completes with business revenue for refunds/timing gaps.', "ko": '유료 완료와 매출(업무)을 나란히 보고 환불·계상 차이를 확인.'},
      ],
    },
  },
  "content": {
    "label": {'ja': 'メディア・コンテンツ', 'en': 'Media & content', 'ko': '미디어·콘텐츠'},
    "hint": {'ja': '閲覧〜メルマガ', 'en': 'View → newsletter', 'ko': '조회〜뉴스레터'},
    "signup_label": {'ja': 'メルマガ登録', 'en': 'Newsletter sign-ups', 'ko': '뉴스레터 구독'},
    "property": {'ja': 'Media Demo JP', 'en': 'Media Demo JP', 'ko': 'Media Demo JP'},
    "cvr_label": {'ja': '登録CVR', 'en': 'Sign-up CVR', 'ko': '구독 CVR'},
    "mid_label": {'ja': 'CTAクリック', 'en': 'CTA clicks', 'ko': 'CTA 클릭'},
    "bottom_label": {'ja': '有料完了', 'en': 'Paid complete', 'ko': '유료 완료'},
    "rate_a_label": {'ja': '登録→有料開始率', 'en': 'Sign-up → paid start', 'ko': '구독→유료 시작률'},
    "rate_b_label": {'ja': '決済CVR', 'en': 'Checkout CVR', 'ko': '결제 CVR'},
    "biz": {
      "members_db": {
        "label": {"ja": '読者数（DB）', "en": 'Readers (DB)', "ko": '독자 수(DB)'},
        "meaning": {"ja": 'メルマガ等の登録者数', "en": 'Newsletter subscribers', "ko": '뉴스레터 등 구독자 수'},
        "formula": {"ja": 'COUNT(有効読者)', "en": 'COUNT(active readers)', "ko": 'COUNT(유효 독자)'},
      },
      "paid_members": {
        "label": {"ja": '有料読者数', "en": 'Paid readers', "ko": '유료 독자 수'},
        "meaning": {"ja": '有料購読中', "en": 'Active paid subscribers', "ko": '유료 구독 중'},
        "formula": {"ja": 'COUNT(有料)', "en": 'COUNT(paid)', "ko": 'COUNT(유료)'},
      },
      "paid_rate": {
        "label": {"ja": '有料化率', "en": 'Paid rate', "ko": '유료화율'},
        "meaning": {"ja": '読者のうち有料割合', "en": 'Share of readers who are paid', "ko": '독자 중 유료 비율'},
        "formula": {"ja": '有料 ÷ 読者 × 100', "en": 'Paid ÷ readers × 100', "ko": '유료 ÷ 독자 × 100'},
      },
      "revenue": {
        "label": {"ja": '売上（期間）', "en": 'Revenue (period)', "ko": '매출(기간)'},
        "meaning": {"ja": '購読・広告など', "en": 'Subs + ads etc.', "ko": '구독·광고 등'},
        "formula": {"ja": 'SUM(期間売上)', "en": 'SUM(period revenue)', "ko": 'SUM(기간 매출)'},
      },
      "arpu": {
        "label": {"ja": 'ARPU', "en": 'ARPU', "ko": 'ARPU'},
        "meaning": {"ja": '読者1人あたり売上', "en": 'Revenue per reader', "ko": '독자 1인당 매출'},
        "formula": {"ja": '売上 ÷ 読者数', "en": 'Revenue ÷ readers', "ko": '매출 ÷ 독자 수'},
      },
      "churn_rate": {
        "label": {"ja": '解約率', "en": 'Churn rate', "ko": '해지율'},
        "meaning": {"ja": '購読解約の割合', "en": 'Paid cancellation rate', "ko": '구독 해지 비율'},
        "formula": {"ja": '解約 ÷ 有料 × 100', "en": 'Churn ÷ paid × 100', "ko": '해지 ÷ 유료 × 100'},
      },
    },
    "notes": {
      "7d": [
        {"ja": '新規依存が強い。記事流入の翌日再訪が弱いと定着しない。', "en": 'Heavy new-user mix. Weak next-day return from articles means poor retention.', "ko": '신규 의존이 강함. 기사 유입 다음날 재방문이 약하면 정착이 안 됨.'},
        {"ja": 'newsletter_signup を本パックの主転換に固定する。', "en": 'Keep newsletter_signup as this pack’s primary conversion.', "ko": 'newsletter_signup을 이 팩의 주전환으로 고정하세요.'},
        {"ja": 'Socialスパイク後は再訪率の落ち込みに注意。', "en": 'After Social spikes, watch returning-user rate drop.', "ko": 'Social 스파이크 뒤에는 재방문율 하락에 주의.'},
      ],
      "28d": [
        {"ja": 'SEOが主戦場。Socialスパイク後の定着率を別枠で見る。', "en": 'SEO is the main field; track retention after Social spikes separately.', "ko": 'SEO가 주전장. Social 스파이크 후 정착률은 별도로 보세요.'},
        {"ja": '登録率1%前後ならCTA位置より記事テーマのずれを疑う。', "en": 'Around 1% sign-up rate: suspect topic mismatch more than CTA placement.', "ko": '구독률 1% 전후면 CTA 위치보다 기사 주제 어긋남을 의심.'},
        {"ja": '有料導線は弱めでも、まず登録の質を安定させる。', "en": 'Even if paid path is weak, stabilize sign-up quality first.', "ko": '유료 동선이 약해도 먼저 구독 품질을 안정시키세요.'},
      ],
    },
  },
  "hr": {
    "label": {'ja': '人事・採用', 'en': 'HR & recruiting', 'ko': '인사·채용'},
    "hint": {'ja': '求人〜応募', 'en': 'Jobs → apply', 'ko': '채용공고〜지원'},
    "signup_label": {'ja': '応募完了', 'en': 'Applications', 'ko': '지원 완료'},
    "property": {'ja': '採用 Demo JP', 'en': 'Recruiting Demo JP', 'ko': '채용 Demo JP'},
    "cvr_label": {'ja': '応募CVR', 'en': 'Apply CVR', 'ko': '지원 CVR'},
    "mid_label": {'ja': '応募開始', 'en': 'Apply start', 'ko': '지원 시작'},
    "bottom_label": {'ja': 'エントリー完了', 'en': 'Entry complete', 'ko': '엔트리 완료'},
    "rate_a_label": {'ja': '応募→エントリー完了率', 'en': 'Apply → entry complete', 'ko': '지원→엔트리 완료율'},
    "rate_b_label": {'ja': '開始→完了率', 'en': 'Start → complete', 'ko': '시작→완료율'},
    "biz": {
      "members_db": {
        "label": {"ja": '応募者数（ATS）', "en": 'Applicants (ATS)', "ko": '지원자 수(ATS)'},
        "meaning": {"ja": '採用管理の期間応募者数', "en": 'Applicants in ATS for the period', "ko": '채용관리 기간 지원자 수'},
        "formula": {"ja": 'ATS: COUNT(期間応募)', "en": 'ATS: COUNT(period apps)', "ko": 'ATS: COUNT(기간 지원)'},
      },
      "paid_members": {
        "label": {"ja": '選考中（ATS）', "en": 'In pipeline (ATS)', "ko": '선고 중(ATS)'},
        "meaning": {"ja": '選考プロセス中の候補者数', "en": 'Candidates in process', "ko": '선고 프로세스 중 후보자 수'},
        "formula": {"ja": 'ATS: COUNT(選考中)', "en": 'ATS: COUNT(in process)', "ko": 'ATS: COUNT(선고 중)'},
      },
      "paid_rate": {
        "label": {"ja": '書類通過率', "en": 'Screen pass rate', "ko": '서류 통과율'},
        "meaning": {"ja": '応募のうち書類通過の割合', "en": 'Share of apps that pass screening', "ko": '지원 중 서류 통과 비율'},
        "formula": {"ja": '書類通過 ÷ 応募 × 100', "en": 'Pass ÷ apps × 100', "ko": '서류 통과 ÷ 지원 × 100'},
      },
      "revenue": {
        "label": {"ja": '採用コスト（期間）', "en": 'Hiring cost (period)', "ko": '채용 비용(기간)'},
        "meaning": {"ja": '媒体費・成功報酬など', "en": 'Media + agency fees etc.', "ko": '매체비·성공보수 등'},
        "formula": {"ja": 'SUM(期間採用コスト)', "en": 'SUM(period hiring cost)', "ko": 'SUM(기간 채용 비용)'},
      },
      "arpu": {
        "label": {"ja": '応募単価', "en": 'Cost per apply', "ko": '지원 단가'},
        "meaning": {"ja": '応募1件あたりコスト', "en": 'Cost per application', "ko": '지원 1건당 비용'},
        "formula": {"ja": '採用コスト ÷ 応募者数', "en": 'Hiring cost ÷ applicants', "ko": '채용 비용 ÷ 지원자 수'},
      },
      "churn_rate": {
        "label": {"ja": '辞退率', "en": 'Drop-out rate', "ko": '사퇴율'},
        "meaning": {"ja": '選考中の辞退・離脱割合', "en": 'Withdrawals while in process', "ko": '선고 중 사퇴·이탈 비율'},
        "formula": {"ja": '辞退 ÷ 選考中 × 100', "en": 'Drops ÷ pipeline × 100', "ko": '사퇴 ÷ 선고 중 × 100'},
      },
    },
    "notes": {
      "7d": [
        {"ja": '求人詳細（job_view）は多いのに apply_start が薄い週は、要件・年収の見せ方を疑う。', "en": 'Many job_view but thin apply_start: check requirements & salary presentation.', "ko": '채용상세(job_view)는 많은데 apply_start가 얇은 주는 요건·연봉 제시를 의심.'},
        {"ja": 'Paid Social 増でも応募CVRが落ちるときは媒体の質を切る。', "en": 'If Paid Social rises but Apply CVR falls, cut low-quality media.', "ko": 'Paid Social이 늘어도 지원 CVR이 떨어지면 매체 질을 줄이세요.'},
        {"ja": 'entry_complete と業務の応募者数（DB）のズレは計測漏れのサイン。', "en": 'Gap between entry_complete and ATS applicants signals tracking gaps.', "ko": 'entry_complete와 업무 지원자 수(DB) 차이는 계측 누락 신호.'},
      ],
      "28d": [
        {"ja": 'Organic Search（求人SEO）が柱なら、職種別ランディングの深さを見る。', "en": 'If Organic Search (job SEO) leads, check depth of role landing pages.', "ko": 'Organic Search(채용 SEO)가 기둥이면 직종별 랜딩 깊이를 보세요.'},
        {"ja": '応募CVRが目安帯を下回る月は、フォーム項目数と必須条件を見直す。', "en": 'Months below Apply CVR band: revisit form fields and required criteria.', "ko": '지원 CVR이 기준 밴드 아래인 달은 폼 항목·필수 조건을 재검토.'},
        {"ja": 'scout_open → message_reply の落差は、スカウト文面の当たり外れを示す。', "en": 'scout_open → message_reply drop shows scout message hit/miss.', "ko": 'scout_open → message_reply 낙차는 스카우트 문구 성패를 보여줌.'},
      ],
    },
  },
  "construction": {
    "label": {'ja': '建設・住宅', 'en': 'Construction & housing', 'ko': '건설·주택'},
    "hint": {'ja': '事例〜問い合わせ', 'en': 'Projects → inquiry', 'ko': '사례〜문의'},
    "signup_label": {'ja': '問い合わせ完了', 'en': 'Inquiries', 'ko': '문의 완료'},
    "property": {'ja': '建設 Demo JP', 'en': 'Construction Demo JP', 'ko': '건설 Demo JP'},
    "cvr_label": {'ja': '問い合わせCVR', 'en': 'Inquiry CVR', 'ko': '문의 CVR'},
    "mid_label": {'ja': '問い合わせ開始', 'en': 'Inquiry start', 'ko': '문의 시작'},
    "bottom_label": {'ja': '現場見学予約', 'en': 'Site visit booked', 'ko': '현장 견학 예약'},
    "rate_a_label": {'ja': '問い合わせ→見学率', 'en': 'Inquiry → visit', 'ko': '문의→견학률'},
    "rate_b_label": {'ja': '開始→問い合わせ完了率', 'en': 'Start → inquiry complete', 'ko': '시작→문의 완료율'},
    "biz": {
      "members_db": {
        "label": {"ja": 'リード数（CRM）', "en": 'Leads (CRM)', "ko": '리드 수(CRM)'},
        "meaning": {"ja": '営業DBの期間リード数', "en": 'Period leads in CRM', "ko": '영업 DB 기간 리드 수'},
        "formula": {"ja": 'CRM: COUNT(期間リード)', "en": 'CRM: COUNT(period leads)', "ko": 'CRM: COUNT(기간 리드)'},
      },
      "paid_members": {
        "label": {"ja": '商談中', "en": 'In pipeline', "ko": '상담 중'},
        "meaning": {"ja": '営業パイプライン中', "en": 'Deals in sales pipeline', "ko": '영업 파이프라인 중'},
        "formula": {"ja": 'COUNT(商談中)', "en": 'COUNT(in pipeline)', "ko": 'COUNT(상담 중)'},
      },
      "paid_rate": {
        "label": {"ja": '商談化率', "en": 'Pipeline rate', "ko": '상담화율'},
        "meaning": {"ja": 'リードのうち商談化割合', "en": 'Share of leads that become deals', "ko": '리드 중 상담화 비율'},
        "formula": {"ja": '商談 ÷ リード × 100', "en": 'Deals ÷ leads × 100', "ko": '상담 ÷ 리드 × 100'},
      },
      "revenue": {
        "label": {"ja": '受注額（期間）', "en": 'Won amount (period)', "ko": '수주액(기간)'},
        "meaning": {"ja": '受注・契約金額', "en": 'Closed contract value', "ko": '수주·계약 금액'},
        "formula": {"ja": 'SUM(期間受注)', "en": 'SUM(period won)', "ko": 'SUM(기간 수주)'},
      },
      "arpu": {
        "label": {"ja": 'リード単価', "en": 'Cost per lead', "ko": '리드 단가'},
        "meaning": {"ja": 'リード1件あたりコスト', "en": 'Cost per lead', "ko": '리드 1건당 비용'},
        "formula": {"ja": 'コスト ÷ リード', "en": 'Cost ÷ leads', "ko": '비용 ÷ 리드'},
      },
      "churn_rate": {
        "label": {"ja": '失注率', "en": 'Lost-deal rate', "ko": '실주율'},
        "meaning": {"ja": '商談の失注割合', "en": 'Share of deals lost', "ko": '상담 실주 비율'},
        "formula": {"ja": '失注 ÷ 商談 × 100', "en": 'Lost ÷ deals × 100', "ko": '실주 ÷ 상담 × 100'},
      },
    },
    "notes": {
      "7d": [
        {"ja": '施工事例（project_view）増でも inquiry_start が弱いと、CTA位置や電話導線を疑う。', "en": 'More project_view but weak inquiry_start: check CTA placement & phone path.', "ko": '시공 사례(project_view)가 늘어도 inquiry_start가 약하면 CTA·전화 동선을 의심.'},
        {"ja": 'Paid Search 増でCVRが落ちる週は、キーワードの意図ズレを疑う。', "en": 'Paid Search up + CVR down: suspect keyword intent mismatch.', "ko": 'Paid Search가 늘고 CVR이 떨어지는 주는 키워드 의도 어긋남을 의심.'},
        {"ja": '現場見学予約とCRMの見学数のズレは計測漏れのサイン。', "en": 'Gap between site-visit bookings and CRM visits signals tracking gaps.', "ko": '현장 견학 예약과 CRM 견학 수 차이는 계측 누락 신호.'},
      ],
      "28d": [
        {"ja": 'B2B寄りはセッションが長く、CVRは低めが普通。目安帯の外だけを追う。', "en": 'B2B-like traffic: longer sessions, lower CVR is normal — chase outliers only.', "ko": 'B2B 성향은 세션이 길고 CVR은 낮은 편이 보통. 기준 밖만 추적.'},
        {"ja": '施工事例SEOが柱なら、事例ページの深さと問い合わせCTAを見る。', "en": 'If project SEO leads, check case-page depth and inquiry CTAs.', "ko": '시공 사례 SEO가 기둥이면 사례 페이지 깊이와 문의 CTA를 보세요.'},
        {"ja": '見学→成約は業務DB側。サイトは問い合わせ完了までを主転換に固定。', "en": 'Visit→close lives in CRM; keep site primary as inquiry complete.', "ko": '견학→성약은 업무 DB. 사이트는 문의 완료까지를 주전환으로 고정.'},
      ],
    },
  },
  "ec": {
    "label": {'ja': 'EC・小売', 'en': 'E-commerce & retail', 'ko': 'EC·소매'},
    "hint": {'ja': '閲覧〜購入', 'en': 'Browse → purchase', 'ko': '조회〜구매'},
    "signup_label": {'ja': '購入完了', 'en': 'Purchases', 'ko': '구매 완료'},
    "property": {'ja': 'EC Demo JP', 'en': 'EC Demo JP', 'ko': 'EC Demo JP'},
    "cvr_label": {'ja': '購入CVR', 'en': 'Purchase CVR', 'ko': '구매 CVR'},
    "mid_label": {'ja': 'カート追加', 'en': 'Add to cart', 'ko': '장바구니 추가'},
    "bottom_label": {'ja': 'チェックアウト開始', 'en': 'Begin checkout', 'ko': '결제 시작'},
    "rate_a_label": {'ja': 'カート→購入率', 'en': 'Cart → purchase', 'ko': '장바구니→구매율'},
    "rate_b_label": {'ja': '決済開始→購入率', 'en': 'Checkout → purchase', 'ko': '결제 시작→구매율'},
    "biz": {
      "members_db": {
        "label": {"ja": '注文件数（受注）', "en": 'Orders (OMS)', "ko": '주문 건수(수주)'},
        "meaning": {"ja": '受注DBの期間注文件数', "en": 'Orders in OMS for the period', "ko": '수주 DB 기간 주문 건수'},
        "formula": {"ja": 'COUNT(期間注文)', "en": 'COUNT(period orders)', "ko": 'COUNT(기간 주문)'},
      },
      "paid_members": {
        "label": {"ja": '顧客数（DB）', "en": 'Customers (DB)', "ko": '고객 수(DB)'},
        "meaning": {"ja": '購入顧客数', "en": 'Purchasing customers', "ko": '구매 고객 수'},
        "formula": {"ja": 'COUNT(期間購入顧客)', "en": 'COUNT(period buyers)', "ko": 'COUNT(기간 구매 고객)'},
      },
      "paid_rate": {
        "label": {"ja": 'リピート率', "en": 'Repeat rate', "ko": '리피트율'},
        "meaning": {"ja": '再購入の割合', "en": 'Share who buy again', "ko": '재구매 비율'},
        "formula": {"ja": '再購入 ÷ 顧客 × 100', "en": 'Repeat ÷ customers × 100', "ko": '재구매 ÷ 고객 × 100'},
      },
      "revenue": {
        "label": {"ja": '売上（期間）', "en": 'Revenue (period)', "ko": '매출(기간)'},
        "meaning": {"ja": '受注金額', "en": 'Order GMV', "ko": '수주 금액'},
        "formula": {"ja": 'SUM(期間売上)', "en": 'SUM(period revenue)', "ko": 'SUM(기간 매출)'},
      },
      "arpu": {
        "label": {"ja": '客単価', "en": 'AOV', "ko": '객단가'},
        "meaning": {"ja": '注文1件あたり金額', "en": 'Average order value', "ko": '주문 1건당 금액'},
        "formula": {"ja": '売上 ÷ 注文', "en": 'Revenue ÷ orders', "ko": '매출 ÷ 주문'},
      },
      "churn_rate": {
        "label": {"ja": '返品率', "en": 'Return rate', "ko": '반품율'},
        "meaning": {"ja": '返品・キャンセル割合', "en": 'Returns/cancellations', "ko": '반품·취소 비율'},
        "formula": {"ja": '返品 ÷ 注文 × 100', "en": 'Returns ÷ orders × 100', "ko": '반품 ÷ 주문 × 100'},
      },
    },
    "notes": {
      "7d": [
        {"ja": 'view_item は多いのに add_to_cart が薄い週は、価格・在庫・レビューを疑う。', "en": 'Many view_item but thin add_to_cart: check price, stock, reviews.', "ko": 'view_item은 많은데 add_to_cart가 얇은 주는 가격·재고·리뷰를 의심.'},
        {"ja": 'Paid Social スパイク後の購入CVR低下は媒体の質を切るサイン。', "en": 'Purchase CVR drop after Paid Social spikes: cut low-quality media.', "ko": 'Paid Social 스파이크 후 구매 CVR 하락은 매체 질을 줄이라는 신호.'},
        {"ja": 'purchase と受注DBの注文件数のズレは計測漏れのサイン。', "en": 'Gap between purchase and OMS orders signals tracking gaps.', "ko": 'purchase와 수주 DB 주문 건수 차이는 계측 누락 신호.'},
      ],
      "28d": [
        {"ja": 'Organic Search（商品SEO）が柱なら、カテゴリLPの深さとカート率を見る。', "en": 'If product SEO leads, check category LP depth and cart rate.', "ko": 'Organic Search(상품 SEO)가 기둥이면 카테고리 LP 깊이와 장바구니율을 보세요.'},
        {"ja": 'カート→購入が目安を下回る月は、送料・決済手段・在庫切れを見直す。', "en": 'Months below cart→purchase band: revisit shipping, payments, stockouts.', "ko": '장바구니→구매가 기준 아래인 달은 배송비·결제수단·품절을 재검토.'},
        {"ja": 'リピート率は業務KPI。サイトは初回購入までを主転換に固定する。', "en": 'Repeat rate is a business KPI; keep site primary as first purchase.', "ko": '리피트율은 업무 KPI. 사이트는 첫 구매까지를 주전환으로 고정.'},
      ],
    },
  },
  "b2b": {
    "label": {'ja': 'B2B・リード', 'en': 'B2B & leads', 'ko': 'B2B·리드'},
    "hint": {'ja': '資料〜問い合わせ', 'en': 'Assets → contact', 'ko': '자료〜문의'},
    "signup_label": {'ja': '問い合わせ完了', 'en': 'Inquiries', 'ko': '문의 완료'},
    "property": {'ja': 'B2B Demo JP', 'en': 'B2B Demo JP', 'ko': 'B2B Demo JP'},
    "cvr_label": {'ja': '問い合わせCVR', 'en': 'Inquiry CVR', 'ko': '문의 CVR'},
    "mid_label": {'ja': '資料DL', 'en': 'Asset download', 'ko': '자료 DL'},
    "bottom_label": {'ja': 'デモ申込', 'en': 'Demo request', 'ko': '데모 신청'},
    "rate_a_label": {'ja': '問い合わせ→デモ率', 'en': 'Inquiry → demo', 'ko': '문의→데모율'},
    "rate_b_label": {'ja': '資料→問い合わせ率', 'en': 'Asset → inquiry', 'ko': '자료→문의율'},
    "biz": {
      "members_db": {
        "label": {"ja": 'リード数（CRM）', "en": 'Leads (CRM)', "ko": '리드 수(CRM)'},
        "meaning": {"ja": '営業DBの期間リード数', "en": 'Period leads in CRM', "ko": '영업 DB 기간 리드 수'},
        "formula": {"ja": 'CRM: COUNT(期間リード)', "en": 'CRM: COUNT(period leads)', "ko": 'CRM: COUNT(기간 리드)'},
      },
      "paid_members": {
        "label": {"ja": '商談中', "en": 'In pipeline', "ko": '상담 중'},
        "meaning": {"ja": '営業パイプライン中', "en": 'Deals in pipeline', "ko": '영업 파이프라인 중'},
        "formula": {"ja": 'COUNT(商談中)', "en": 'COUNT(in pipeline)', "ko": 'COUNT(상담 중)'},
      },
      "paid_rate": {
        "label": {"ja": '商談化率', "en": 'Pipeline rate', "ko": '상담화율'},
        "meaning": {"ja": 'リードのうち商談化割合', "en": 'Leads that become deals', "ko": '리드 중 상담화 비율'},
        "formula": {"ja": '商談 ÷ 리드 × 100', "en": 'Deals ÷ leads × 100', "ko": '상담 ÷ 리드 × 100'},
      },
      "revenue": {
        "label": {"ja": '受注額（期間）', "en": 'Won amount (period)', "ko": '수주액(기간)'},
        "meaning": {"ja": '受注金額', "en": 'Closed won value', "ko": '수주 금액'},
        "formula": {"ja": 'SUM(期間受注)', "en": 'SUM(period won)', "ko": 'SUM(기간 수주)'},
      },
      "arpu": {
        "label": {"ja": 'リード単価', "en": 'Cost per lead', "ko": '리드 단가'},
        "meaning": {"ja": 'リード1件あたりコスト', "en": 'Cost per lead', "ko": '리드 1건당 비용'},
        "formula": {"ja": 'コスト ÷ リード', "en": 'Cost ÷ leads', "ko": '비용 ÷ 리드'},
      },
      "churn_rate": {
        "label": {"ja": '失注率', "en": 'Lost-deal rate', "ko": '실주율'},
        "meaning": {"ja": '商談の失注割合', "en": 'Share of deals lost', "ko": '상담 실주 비율'},
        "formula": {"ja": '失注 ÷ 商談 × 100', "en": 'Lost ÷ deals × 100', "ko": '실주 ÷ 상담 × 100'},
      },
    },
    "notes": {
      "7d": [
        {"ja": 'whitepaper_dl は多いのに contact_submit が薄い週は、資料後のCTA・営業フォローを疑う。', "en": 'Many whitepaper_dl but thin contact_submit: check post-download CTA & follow-up.', "ko": 'whitepaper_dl은 많은데 contact_submit이 얇은 주는 자료 후 CTA·영업 팔로업을 의심.'},
        {"ja": 'Paid Search 増で問い合わせCVRが落ちるときはKW意図を切る。', "en": 'Paid Search up + inquiry CVR down: prune weak keyword intent.', "ko": 'Paid Search가 늘고 문의 CVR이 떨어지면 KW 의도를 줄이세요.'},
        {"ja": 'contact_submit とCRMリード数のズレは計測漏れのサイン。', "en": 'Gap between contact_submit and CRM leads signals tracking gaps.', "ko": 'contact_submit과 CRM 리드 수 차이는 계측 누락 신호.'},
      ],
      "28d": [
        {"ja": 'セッションが長くCVRが低いのはB2Bでは普通。目安帯の外だけを追う。', "en": 'Long sessions + low CVR is normal in B2B — chase band outliers only.', "ko": '세션이 길고 CVR이 낮은 것은 B2B에서 보통. 기준 밖만 추적.'},
        {"ja": '資料DL→問い合わせの歩留まりが落ちたら、フォーム項目と営業SLAを見る。', "en": 'If asset→inquiry drops, check form fields and sales SLA.', "ko": '자료 DL→문의 수익률이 떨어지면 폼 항목과 영업 SLA를 보세요.'},
        {"ja": 'デモ申込は次KPI。サイト主転換は問い合わせ完了に固定する。', "en": 'Demo requests are next KPI; keep site primary as inquiry complete.', "ko": '데모 신청은 다음 KPI. 사이트 주전환은 문의 완료로 고정.'},
      ],
    },
  },
  "edu": {
    "label": {'ja': '教育・スクール', 'en': 'Education & schools', 'ko': '교육·스쿨'},
    "hint": {'ja': '閲覧〜申込', 'en': 'View → apply', 'ko': '조회〜신청'},
    "signup_label": {'ja': '受講申込完了', 'en': 'Enrollments', 'ko': '수강 신청 완료'},
    "property": {'ja': '教育 Demo JP', 'en': 'Edu Demo JP', 'ko': '교육 Demo JP'},
    "cvr_label": {'ja': '申込CVR', 'en': 'Apply CVR', 'ko': '신청 CVR'},
    "mid_label": {'ja': '申込開始', 'en': 'Apply start', 'ko': '신청 시작'},
    "bottom_label": {'ja': '体験予約', 'en': 'Trial booked', 'ko': '체험 예약'},
    "rate_a_label": {'ja': '開始→申込完了率', 'en': 'Start → enroll', 'ko': '시작→신청 완료율'},
    "rate_b_label": {'ja': '体験→申込率', 'en': 'Trial → enroll', 'ko': '체험→신청률'},
    "biz": {
      "members_db": {
        "label": {"ja": '申込者数（学務）', "en": 'Enrollees (SIS)', "ko": '신청자 수(학무)'},
        "meaning": {"ja": '学務DBの期間申込者数', "en": 'Period enrollments in SIS', "ko": '학무 DB 기간 신청자 수'},
        "formula": {"ja": 'COUNT(期間申込)', "en": 'COUNT(period enroll)', "ko": 'COUNT(기간 신청)'},
      },
      "paid_members": {
        "label": {"ja": '在籍者数', "en": 'Active students', "ko": '재적자 수'},
        "meaning": {"ja": '受講中の人数', "en": 'Currently enrolled', "ko": '수강 중 인원'},
        "formula": {"ja": 'COUNT(在籍)', "en": 'COUNT(enrolled)', "ko": 'COUNT(재적)'},
      },
      "paid_rate": {
        "label": {"ja": '受講確定率', "en": 'Confirm rate', "ko": '수강 확정율'},
        "meaning": {"ja": '申込のうち受講確定割合', "en": 'Enrollments confirmed', "ko": '신청 중 수강 확정 비율'},
        "formula": {"ja": '確定 ÷ 申込 × 100', "en": 'Confirmed ÷ apply × 100', "ko": '확정 ÷ 신청 × 100'},
      },
      "revenue": {
        "label": {"ja": '受講料（期間）', "en": 'Tuition (period)', "ko": '수강료(기간)'},
        "meaning": {"ja": '受講料売上', "en": 'Tuition revenue', "ko": '수강료 매출'},
        "formula": {"ja": 'SUM(期間受講料)', "en": 'SUM(period tuition)', "ko": 'SUM(기간 수강료)'},
      },
      "arpu": {
        "label": {"ja": '申込単価', "en": 'Revenue per apply', "ko": '신청 단가'},
        "meaning": {"ja": '申込1件あたり売上', "en": 'Revenue per enrollment', "ko": '신청 1건당 매출'},
        "formula": {"ja": '売上 ÷ 申込', "en": 'Revenue ÷ applies', "ko": '매출 ÷ 신청'},
      },
      "churn_rate": {
        "label": {"ja": '退学率', "en": 'Dropout rate', "ko": '중퇴율'},
        "meaning": {"ja": '途中退学の割合', "en": 'Mid-course dropouts', "ko": '중도 퇴학 비율'},
        "formula": {"ja": '退学 ÷ 在籍 × 100', "en": 'Dropout ÷ enrolled × 100', "ko": '중퇴 ÷ 재적 × 100'},
      },
    },
    "notes": {
      "7d": [
        {"ja": 'course_view は多いのに trial_book が薄い週は、日程・場所・対象者の見せ方を疑う。', "en": 'Many course_view but thin trial_book: check schedule, place, audience framing.', "ko": 'course_view는 많은데 trial_book이 얇은 주는 일정·장소·대상 제시를 의심.'},
        {"ja": 'Paid Social 増で申込CVRが落ちるときは媒体の質を切る。', "en": 'Paid Social up + Apply CVR down: cut low-quality media.', "ko": 'Paid Social이 늘고 신청 CVR이 떨어지면 매체 질을 줄이세요.'},
        {"ja": '申込完了と学務DBの申込者数のズレは計測漏れのサイン。', "en": 'Gap between enroll complete and SIS enrollments signals tracking gaps.', "ko": '신청 완료와 학무 DB 신청자 수 차이는 계측 누락 신호.'},
      ],
      "28d": [
        {"ja": '体験→申込の歩留まりが目安を下回る月は、体験後フォローと料金説明を見直す。', "en": 'Months below trial→enroll band: revisit post-trial follow-up & pricing.', "ko": '체험→신청 수익률이 기준 아래인 달은 체험 후 팔로업·요금 설명을 재검토.'},
        {"ja": 'SEOが柱ならコースLPの深さと申込CTAを見る。', "en": 'If SEO leads, check course LP depth and apply CTAs.', "ko": 'SEO가 기둥이면 코스 LP 깊이와 신청 CTA를 보세요.'},
        {"ja": '在籍・退学は業務KPI。サイトは申込完了までを主転換に固定。', "en": 'Enrollment/dropout are business KPIs; keep site primary as enroll complete.', "ko": '재적·중퇴는 업무 KPI. 사이트는 신청 완료까지를 주전환으로 고정.'},
      ],
    },
  },
  "clinic": {
    "label": {'ja': '医療・クリニック', 'en': 'Clinic & healthcare', 'ko': '의료·클리닉'},
    "hint": {'ja': '診療案内〜予約', 'en': 'Services → book', 'ko': '안내〜예약'},
    "signup_label": {'ja': '予約完了', 'en': 'Bookings', 'ko': '예약 완료'},
    "property": {'ja': 'クリニック Demo JP', 'en': 'Clinic Demo JP', 'ko': '클리닉 Demo JP'},
    "cvr_label": {'ja': '予約CVR', 'en': 'Booking CVR', 'ko': '예약 CVR'},
    "mid_label": {'ja': '予約開始', 'en': 'Booking start', 'ko': '예약 시작'},
    "bottom_label": {'ja': '口コミ送信', 'en': 'Review submitted', 'ko': '후기 전송'},
    "rate_a_label": {'ja': '予約→口コミ比', 'en': 'Book → review', 'ko': '예약→후기 비'},
    "rate_b_label": {'ja': '開始→予約完了率', 'en': 'Start → book complete', 'ko': '시작→예약 완료율'},
    "biz": {
      "members_db": {
        "label": {"ja": '予約件数（受付）', "en": 'Bookings (desk)', "ko": '예약 건수(접수)'},
        "meaning": {"ja": '受付システムの期間予約数', "en": 'Period bookings in desk system', "ko": '접수 시스템 기간 예약 수'},
        "formula": {"ja": 'COUNT(期間予約)', "en": 'COUNT(period books)', "ko": 'COUNT(기간 예약)'},
      },
      "paid_members": {
        "label": {"ja": '来院者数', "en": 'Visits', "ko": '내원자 수'},
        "meaning": {"ja": '来院した患者数', "en": 'Patients who visited', "ko": '내원한 환자 수'},
        "formula": {"ja": 'COUNT(期間来院)', "en": 'COUNT(period visits)', "ko": 'COUNT(기간 내원)'},
      },
      "paid_rate": {
        "label": {"ja": '来院率', "en": 'Show rate', "ko": '내원율'},
        "meaning": {"ja": '予約のうち来院割合', "en": 'Bookings that show up', "ko": '예약 중 내원 비율'},
        "formula": {"ja": '来院 ÷ 予約 × 100', "en": 'Visits ÷ books × 100', "ko": '내원 ÷ 예약 × 100'},
      },
      "revenue": {
        "label": {"ja": '診療売上（期間）', "en": 'Clinic revenue', "ko": '진료 매출(기간)'},
        "meaning": {"ja": '診療・自費など', "en": 'Clinical + self-pay etc.', "ko": '진료·자비 등'},
        "formula": {"ja": 'SUM(期間売上)', "en": 'SUM(period revenue)', "ko": 'SUM(기간 매출)'},
      },
      "arpu": {
        "label": {"ja": '予約単価', "en": 'Revenue per booking', "ko": '예약 단가'},
        "meaning": {"ja": '予約1件あたり売上', "en": 'Revenue per booking', "ko": '예약 1건당 매출'},
        "formula": {"ja": '売上 ÷ 予約', "en": 'Revenue ÷ books', "ko": '매출 ÷ 예약'},
      },
      "churn_rate": {
        "label": {"ja": 'キャンセル率', "en": 'Cancel rate', "ko": '취소율'},
        "meaning": {"ja": '予約キャンセル割合', "en": 'Booking cancellations', "ko": '예약 취소 비율'},
        "formula": {"ja": 'キャンセル ÷ 予約 × 100', "en": 'Cancels ÷ books × 100', "ko": '취소 ÷ 예약 × 100'},
      },
    },
    "notes": {
      "7d": [
        {"ja": 'service_view は多いのに reserve_start が薄い週は、予約UI・空き枠表示を疑う。', "en": 'Many service_view but thin reserve_start: check booking UI & slot display.', "ko": 'service_view는 많은데 reserve_start가 얇은 주는 예약 UI·빈 슬롯 표시를 의심.'},
        {"ja": 'Paid Search 増で予約CVRが落ちるときはKW意図を切る。', "en": 'Paid Search up + Booking CVR down: prune weak keyword intent.', "ko": 'Paid Search가 늘고 예약 CVR이 떨어지면 KW 의도를 줄이세요.'},
        {"ja": '予約完了と受付DBの予約数のズレは計測漏れのサイン。', "en": 'Gap between booking complete and desk bookings signals tracking gaps.', "ko": '예약 완료와 접수 DB 예약 수 차이는 계측 누락 신호.'},
      ],
      "28d": [
        {"ja": '予約→来院の歩留まりは業務DB側。サイトは予約完了までを主転換に固定する。', "en": 'Book→visit lives in desk DB; keep site primary as booking complete.', "ko": '예약→내원 수익률은 업무 DB. 사이트는 예약 완료까지를 주전환으로 고정.'},
        {"ja": '口コミ送信は次KPI。主転換と混ぜない。', "en": 'Review submits are next KPI — don’t mix with primary.', "ko": '후기 전송은 다음 KPI. 주전환과 섞지 마세요.'},
        {"ja": 'キャンセル率上昇月はリマインドと空き枠運用を見直す。', "en": 'Months with rising cancels: revisit reminders and slot ops.', "ko": '취소율 상승 달은 리마인드와 빈 슬롯 운영을 재검토.'},
      ],
    },
  },
  "beauty": {
    "label": {'ja': '美容・サロン', 'en': 'Beauty & salon', 'ko': '뷰티·살롱'},
    "hint": {'ja': 'メニュー〜予約', 'en': 'Menu → book', 'ko': '메뉴〜예약'},
    "signup_label": {'ja': '来店予約完了', 'en': 'Visit bookings', 'ko': '방문 예약 완료'},
    "property": {'ja': 'サロン Demo JP', 'en': 'Salon Demo JP', 'ko': '살롱 Demo JP'},
    "cvr_label": {'ja': '予約CVR', 'en': 'Booking CVR', 'ko': '예약 CVR'},
    "mid_label": {'ja': '予約開始', 'en': 'Booking start', 'ko': '예약 시작'},
    "bottom_label": {'ja': 'リピート予約', 'en': 'Repeat booking', 'ko': '리피트 예약'},
    "rate_a_label": {'ja': '予約→リピート比', 'en': 'Book → repeat', 'ko': '예약→리피트 비'},
    "rate_b_label": {'ja': '開始→予約完了率', 'en': 'Start → book complete', 'ko': '시작→예약 완료율'},
    "biz": {
      "members_db": {
        "label": {"ja": '予約件数（台帳）', "en": 'Bookings (book)', "ko": '예약 건수(대장)'},
        "meaning": {"ja": '予約台帳の期間予約数', "en": 'Period bookings in the book', "ko": '예약 대장 기간 예약 수'},
        "formula": {"ja": 'COUNT(期間予約)', "en": 'COUNT(period books)', "ko": 'COUNT(기간 예약)'},
      },
      "paid_members": {
        "label": {"ja": '来店者数', "en": 'Visits', "ko": '방문자 수'},
        "meaning": {"ja": '来店した顧客数', "en": 'Customers who visited', "ko": '방문한 고객 수'},
        "formula": {"ja": 'COUNT(期間来店)', "en": 'COUNT(period visits)', "ko": 'COUNT(기간 방문)'},
      },
      "paid_rate": {
        "label": {"ja": '来店率', "en": 'Show rate', "ko": '방문율'},
        "meaning": {"ja": '予約のうち来店割合', "en": 'Bookings that show up', "ko": '예약 중 방문 비율'},
        "formula": {"ja": '来店 ÷ 予約 × 100', "en": 'Visits ÷ books × 100', "ko": '방문 ÷ 예약 × 100'},
      },
      "revenue": {
        "label": {"ja": '売上（期間）', "en": 'Revenue (period)', "ko": '매출(기간)'},
        "meaning": {"ja": '施術売上', "en": 'Service revenue', "ko": '시술 매출'},
        "formula": {"ja": 'SUM(期間売上)', "en": 'SUM(period revenue)', "ko": 'SUM(기간 매출)'},
      },
      "arpu": {
        "label": {"ja": '客単価', "en": 'Spend per visit', "ko": '객단가'},
        "meaning": {"ja": '来店1回あたり売上', "en": 'Revenue per visit', "ko": '방문 1회당 매출'},
        "formula": {"ja": '売上 ÷ 来店', "en": 'Revenue ÷ visits', "ko": '매출 ÷ 방문'},
      },
      "churn_rate": {
        "label": {"ja": 'キャンセル率', "en": 'Cancel rate', "ko": '취소율'},
        "meaning": {"ja": '予約キャンセル割合', "en": 'Booking cancellations', "ko": '예약 취소 비율'},
        "formula": {"ja": 'キャンセル ÷ 予約 × 100', "en": 'Cancels ÷ books × 100', "ko": '취소 ÷ 예약 × 100'},
      },
    },
    "notes": {
      "7d": [
        {"ja": 'menu_view 増でも book_start が薄い週は、空き枠・スタイリスト指名UIを疑う。', "en": 'More menu_view but thin book_start: check slots & stylist-pick UI.', "ko": 'menu_view가 늘어도 book_start가 얇은 주는 빈 슬롯·스타일리스트 지정 UI를 의심.'},
        {"ja": 'Paid Social スパイク後の予約CVR低下は媒体の質を切るサイン。', "en": 'Booking CVR drop after Paid Social spikes: cut low-quality media.', "ko": 'Paid Social 스파이크 후 예약 CVR 하락은 매체 질을 줄이라는 신호.'},
        {"ja": '予約完了と台帳の予約数のズレは計測漏れのサイン。', "en": 'Gap between booking complete and the book signals tracking gaps.', "ko": '예약 완료와 대장 예약 수 차이는 계측 누락 신호.'},
      ],
      "28d": [
        {"ja": 'リピート予約（repeat_book）は定着の指標。新規予約と分けて見る。', "en": 'repeat_book is retention; track separately from new bookings.', "ko": '리피트 예약(repeat_book)은 정착 지표. 신규 예약과 나눠 보세요.'},
        {"ja": '開始→予約完了が目安を下回る月は、必須項目と決済手段を見直す。', "en": 'Months below start→complete band: revisit required fields & payments.', "ko": '시작→예약 완료가 기준 아래인 달은 필수 항목·결제수단을 재검토.'},
        {"ja": '来店・キャンセルは業務KPI。サイトは予約完了までを主転換に固定。', "en": 'Visits/cancels are business KPIs; keep site primary as booking complete.', "ko": '방문·취소는 업무 KPI. 사이트는 예약 완료까지를 주전환으로 고정.'},
      ],
    },
  },
  "finance": {
    "label": {'ja': '金融・保険', 'en': 'Finance & insurance', 'ko': '금융·보험'},
    "hint": {'ja': '見積〜申込', 'en': 'Quote → apply', 'ko': '견적〜신청'},
    "signup_label": {'ja': '申込完了', 'en': 'Applications', 'ko': '신청 완료'},
    "property": {'ja': '金融 Demo JP', 'en': 'Finance Demo JP', 'ko': '금융 Demo JP'},
    "cvr_label": {'ja': '申込CVR', 'en': 'Apply CVR', 'ko': '신청 CVR'},
    "mid_label": {'ja': '申込開始', 'en': 'Apply start', 'ko': '신청 시작'},
    "bottom_label": {'ja': '見積完了', 'en': 'Quote complete', 'ko': '견적 완료'},
    "rate_a_label": {'ja': '開始→申込完了率', 'en': 'Start → apply complete', 'ko': '시작→신청 완료율'},
    "rate_b_label": {'ja': '見積→申込率', 'en': 'Quote → apply', 'ko': '견적→신청률'},
    "biz": {
      "members_db": {
        "label": {"ja": '申込件数（基幹）', "en": 'Applications (core)', "ko": '신청 건수(기간)'},
        "meaning": {"ja": '基幹の期間申込数', "en": 'Period apps in core system', "ko": '기간 신청 수'},
        "formula": {"ja": 'COUNT(期間申込)', "en": 'COUNT(period apps)', "ko": 'COUNT(기간 신청)'},
      },
      "paid_members": {
        "label": {"ja": '審査中', "en": 'Under review', "ko": '심사 중'},
        "meaning": {"ja": '審査プロセス中', "en": 'Apps in underwriting', "ko": '심사 프로세스 중'},
        "formula": {"ja": 'COUNT(審査中)', "en": 'COUNT(in review)', "ko": 'COUNT(심사 중)'},
      },
      "paid_rate": {
        "label": {"ja": '成約率', "en": 'Close rate', "ko": '성약률'},
        "meaning": {"ja": '申込のうち成約割合', "en": 'Apps that close', "ko": '신청 중 성약 비율'},
        "formula": {"ja": '成約 ÷ 申込 × 100', "en": 'Closed ÷ apps × 100', "ko": '성약 ÷ 신청 × 100'},
      },
      "revenue": {
        "label": {"ja": '手数料・保険料（期間）', "en": 'Fees/premiums', "ko": '수수료·보험료(기간)'},
        "meaning": {"ja": '手数料・保険料など', "en": 'Fees & premiums', "ko": '수수료·보험료 등'},
        "formula": {"ja": 'SUM(期間収益)', "en": 'SUM(period revenue)', "ko": 'SUM(기간 수익)'},
      },
      "arpu": {
        "label": {"ja": '申込単価', "en": 'Revenue per apply', "ko": '신청 단가'},
        "meaning": {"ja": '申込1件あたり収益', "en": 'Revenue per application', "ko": '신청 1건당 수익'},
        "formula": {"ja": '収益 ÷ 申込', "en": 'Revenue ÷ apps', "ko": '수익 ÷ 신청'},
      },
      "churn_rate": {
        "label": {"ja": '離脱率', "en": 'Abandon rate', "ko": '이탈률'},
        "meaning": {"ja": '申込途中離脱の割合', "en": 'Apps abandoned mid-flow', "ko": '신청 중도 이탈 비율'},
        "formula": {"ja": '離脱 ÷ 申込 × 100', "en": 'Abandon ÷ apps × 100', "ko": '이탈 ÷ 신청 × 100'},
      },
    },
    "notes": {
      "7d": [
        {"ja": 'quote_complete は多いのに apply_start が薄い週は、申込への導線・必要書類説明を疑う。', "en": 'Many quote_complete but thin apply_start: check path to apply & docs copy.', "ko": 'quote_complete는 많은데 apply_start가 얇은 주는 신청 동선·필요서류 설명을 의심.'},
        {"ja": 'Paid 増で申込CVRが落ちるときは媒体の質を切る。', "en": 'Paid up + Apply CVR down: cut low-quality media.', "ko": 'Paid가 늘고 신청 CVR이 떨어지면 매체 질을 줄이세요.'},
        {"ja": '申込完了と基幹の申込件数のズレは計測漏れのサイン。', "en": 'Gap between apply complete and core apps signals tracking gaps.', "ko": '신청 완료와 기간 신청 건수 차이는 계측 누락 신호.'},
      ],
      "28d": [
        {"ja": '高関与商品は検討が長い。目安帯の外だけを追う。', "en": 'High-consideration products take time — chase band outliers only.', "ko": '고관여 상품은 검토가 김. 기준 밖만 추적.'},
        {"ja": '見積→申込が落ちたら、金利・条件・必要書類の説明を見直す。', "en": 'If quote→apply drops, revisit rate/terms/docs explanations.', "ko": '견적→신청이 떨어지면 금리·조건·필요서류 설명을 재검토.'},
        {"ja": '成約・審査は業務KPI。サイトは申込完了までを主転換に固定。', "en": 'Close/underwriting are business KPIs; keep site primary as apply complete.', "ko": '성약·심사는 업무 KPI. 사이트는 신청 완료까지를 주전환으로 고정.'},
      ],
    },
  },
  "travel": {
    "label": {'ja': '旅行・宿泊', 'en': 'Travel & lodging', 'ko': '여행·숙박'},
    "hint": {'ja': '検索〜予約', 'en': 'Search → book', 'ko': '검색〜예약'},
    "signup_label": {'ja': '予約完了', 'en': 'Bookings', 'ko': '예약 완료'},
    "property": {'ja': '旅行 Demo JP', 'en': 'Travel Demo JP', 'ko': '여행 Demo JP'},
    "cvr_label": {'ja': '予約CVR', 'en': 'Booking CVR', 'ko': '예약 CVR'},
    "mid_label": {'ja': 'カート（部屋選択）', 'en': 'Cart (room select)', 'ko': '장바구니(객실 선택)'},
    "bottom_label": {'ja': 'チェックアウト開始', 'en': 'Begin checkout', 'ko': '결제 시작'},
    "rate_a_label": {'ja': 'カート→予約率', 'en': 'Cart → book', 'ko': '장바구니→예약률'},
    "rate_b_label": {'ja': '決済開始→予約率', 'en': 'Checkout → book', 'ko': '결제 시작→예약률'},
    "biz": {
      "members_db": {
        "label": {"ja": '予約件数（予約DB）', "en": 'Bookings (PMS)', "ko": '예약 건수(예약DB)'},
        "meaning": {"ja": '予約システムの期間予約数', "en": 'Period bookings in PMS', "ko": '예약 시스템 기간 예약 수'},
        "formula": {"ja": 'COUNT(期間予約)', "en": 'COUNT(period books)', "ko": 'COUNT(기간 예약)'},
      },
      "paid_members": {
        "label": {"ja": '宿泊者数', "en": 'Guests stayed', "ko": '숙박자 수'},
        "meaning": {"ja": 'チェックイン済み', "en": 'Checked-in guests', "ko": '체크인 완료'},
        "formula": {"ja": 'COUNT(期間宿泊)', "en": 'COUNT(period stays)', "ko": 'COUNT(기간 숙박)'},
      },
      "paid_rate": {
        "label": {"ja": '宿泊率', "en": 'Stay rate', "ko": '숙박률'},
        "meaning": {"ja": '予約のうち宿泊割合', "en": 'Bookings that stay', "ko": '예약 중 숙박 비율'},
        "formula": {"ja": '宿泊 ÷ 予約 × 100', "en": 'Stays ÷ books × 100', "ko": '숙박 ÷ 예약 × 100'},
      },
      "revenue": {
        "label": {"ja": '売上（期間）', "en": 'Revenue (period)', "ko": '매출(기간)'},
        "meaning": {"ja": '宿泊売上', "en": 'Lodging revenue', "ko": '숙박 매출'},
        "formula": {"ja": 'SUM(期間売上)', "en": 'SUM(period revenue)', "ko": 'SUM(기간 매출)'},
      },
      "arpu": {
        "label": {"ja": '予約単価', "en": 'Revenue per booking', "ko": '예약 단가'},
        "meaning": {"ja": '予約1件あたり売上', "en": 'Revenue per booking', "ko": '예약 1건당 매출'},
        "formula": {"ja": '売上 ÷ 予約', "en": 'Revenue ÷ books', "ko": '매출 ÷ 예약'},
      },
      "churn_rate": {
        "label": {"ja": 'キャンセル率', "en": 'Cancel rate', "ko": '취소율'},
        "meaning": {"ja": '予約キャンセル割合', "en": 'Booking cancellations', "ko": '예약 취소 비율'},
        "formula": {"ja": 'キャンセル ÷ 予約 × 100', "en": 'Cancels ÷ books × 100', "ko": '취소 ÷ 예약 × 100'},
      },
    },
    "notes": {
      "7d": [
        {"ja": 'search は多いのに select_room が薄い週は、価格・空室・写真の質を疑う。', "en": 'Many search but thin select_room: check price, availability, photo quality.', "ko": 'search는 많은데 select_room이 얇은 주는 가격·공실·사진 질을 의심.'},
        {"ja": 'Paid スパイク後の予約CVR低下は媒体の質を切るサイン。', "en": 'Booking CVR drop after Paid spikes: cut low-quality media.', "ko": 'Paid 스파이크 후 예약 CVR 하락은 매체 질을 줄이라는 신호.'},
        {"ja": 'purchase と予約DBの予約件数のズレは計測漏れのサイン。', "en": 'Gap between purchase and PMS bookings signals tracking gaps.', "ko": 'purchase와 예약 DB 예약 건수 차이는 계측 누락 신호.'},
      ],
      "28d": [
        {"ja": '検索→予約はファネルが長い。段ごとの落ちをイベントで見る。', "en": 'Search→book is a long funnel — watch drop-offs per event step.', "ko": '검색→예약은 퍼널이 김. 단계별 낙차를 이벤트로 보세요.'},
        {"ja": 'カート→予約が目安を下回る月は、料金内訳・キャンセルポリシーを見直す。', "en": 'Months below cart→book band: revisit fee breakdown & cancel policy.', "ko": '장바구니→예약이 기준 아래인 달은 요금 내역·취소 정책을 재검토.'},
        {"ja": '宿泊・キャンセルは業務KPI。サイトは予約完了までを主転換に固定。', "en": 'Stays/cancels are business KPIs; keep site primary as booking complete.', "ko": '숙박·취소는 업무 KPI. 사이트는 예약 완료까지를 주전환으로 고정.'},
      ],
    },
  },
  "realestate": {
    "label": {'ja': '不動産・物件', 'en': 'Real estate', 'ko': '부동산·매물'},
    "hint": {'ja': '物件〜問い合わせ', 'en': 'Listing → inquiry', 'ko': '매물〜문의'},
    "signup_label": {'ja': '問い合わせ完了', 'en': 'Inquiries', 'ko': '문의 완료'},
    "property": {'ja': '不動産 Demo JP', 'en': 'Real estate Demo JP', 'ko': '부동산 Demo JP'},
    "cvr_label": {'ja': '問い合わせCVR', 'en': 'Inquiry CVR', 'ko': '문의 CVR'},
    "mid_label": {'ja': '問い合わせ開始', 'en': 'Inquiry start', 'ko': '문의 시작'},
    "bottom_label": {'ja': '内見予約', 'en': 'Tour booked', 'ko': '내견 예약'},
    "rate_a_label": {'ja': '問い合わせ→内見率', 'en': 'Inquiry → tour', 'ko': '문의→내견률'},
    "rate_b_label": {'ja': '開始→問い合わせ完了率', 'en': 'Start → inquiry complete', 'ko': '시작→문의 완료율'},
    "biz": {
      "members_db": {
        "label": {"ja": 'リード数（CRM）', "en": 'Leads (CRM)', "ko": '리드 수(CRM)'},
        "meaning": {"ja": 'CRMの期間リード数', "en": 'Period leads in CRM', "ko": 'CRM 기간 리드 수'},
        "formula": {"ja": 'COUNT(期間リード)', "en": 'COUNT(period leads)', "ko": 'COUNT(기간 리드)'},
      },
      "paid_members": {
        "label": {"ja": '商談中', "en": 'In pipeline', "ko": '상담 중'},
        "meaning": {"ja": '内見・商談中', "en": 'Tours / deals in progress', "ko": '내견·상담 중'},
        "formula": {"ja": 'COUNT(商談中)', "en": 'COUNT(in pipeline)', "ko": 'COUNT(상담 중)'},
      },
      "paid_rate": {
        "label": {"ja": '内見率', "en": 'Tour rate', "ko": '내견률'},
        "meaning": {"ja": '問い合わせのうち内見割合', "en": 'Inquiries that book a tour', "ko": '문의 중 내견 비율'},
        "formula": {"ja": '内見 ÷ 問い合わせ × 100', "en": 'Tours ÷ inquiries × 100', "ko": '내견 ÷ 문의 × 100'},
      },
      "revenue": {
        "label": {"ja": '成約額（期間）', "en": 'Closed value', "ko": '성약액(기간)'},
        "meaning": {"ja": '成約・仲介手数料など', "en": 'Closed deals / fees', "ko": '성약·중개 수수료 등'},
        "formula": {"ja": 'SUM(期間成約)', "en": 'SUM(period closed)', "ko": 'SUM(기간 성약)'},
      },
      "arpu": {
        "label": {"ja": 'リード単価', "en": 'Cost per lead', "ko": '리드 단가'},
        "meaning": {"ja": 'リード1件あたりコスト', "en": 'Cost per lead', "ko": '리드 1건당 비용'},
        "formula": {"ja": 'コスト ÷ リード', "en": 'Cost ÷ leads', "ko": '비용 ÷ 리드'},
      },
      "churn_rate": {
        "label": {"ja": '失注率', "en": 'Lost-deal rate', "ko": '실주율'},
        "meaning": {"ja": '商談の失注割合', "en": 'Share of deals lost', "ko": '상담 실주 비율'},
        "formula": {"ja": '失注 ÷ 商談 × 100', "en": 'Lost ÷ deals × 100', "ko": '실주 ÷ 상담 × 100'},
      },
    },
    "notes": {
      "7d": [
        {"ja": 'listing_view 増でも inquiry_start が薄い週は、価格・間取り・CTAを疑う。', "en": 'More listing_view but thin inquiry_start: check price, floorplan, CTA.', "ko": 'listing_view가 늘어도 inquiry_start가 얇은 주는 가격·평면·CTA를 의심.'},
        {"ja": 'Paid 増で問い合わせCVRが落ちるときは媒体の質を切る。', "en": 'Paid up + Inquiry CVR down: cut low-quality media.', "ko": 'Paid가 늘고 문의 CVR이 떨어지면 매체 질을 줄이세요.'},
        {"ja": '問い合わせ完了とCRMリード数のズレは計測漏れのサイン。', "en": 'Gap between inquiry complete and CRM leads signals tracking gaps.', "ko": '문의 완료와 CRM 리드 수 차이는 계측 누락 신호.'},
      ],
      "28d": [
        {"ja": '内見予約まで届く率が落ちたら、日程調整・担当レスポンスを見る。', "en": 'If reach-to-tour falls, check scheduling and agent response.', "ko": '내견 예약까지 도달률이 떨어지면 일정 조율·담당 응답을 보세요.'},
        {"ja": '物件SEOが柱なら、エリアLPの深さと問い合わせCTAを見る。', "en": 'If listing SEO leads, check area LP depth and inquiry CTAs.', "ko": '매물 SEO가 기둥이면 지역 LP 깊이와 문의 CTA를 보세요.'},
        {"ja": '成約は業務KPI。サイトは問い合わせ完了までを主転換に固定。', "en": 'Closed deals are business KPIs; keep site primary as inquiry complete.', "ko": '성약은 업무 KPI. 사이트는 문의 완료까지를 주전환으로 고정.'},
      ],
    },
  },
  "food": {
    "label": {'ja': '飲食・店舗', 'en': 'Food & restaurants', 'ko': '음식·매장'},
    "hint": {'ja': 'メニュー〜予約', 'en': 'Menu → reserve', 'ko': '메뉴〜예약'},
    "signup_label": {'ja': '来店予約完了', 'en': 'Table bookings', 'ko': '방문 예약 완료'},
    "property": {'ja': '飲食 Demo JP', 'en': 'Food Demo JP', 'ko': '음식 Demo JP'},
    "cvr_label": {'ja': '予約CVR', 'en': 'Booking CVR', 'ko': '예약 CVR'},
    "mid_label": {'ja': '予約開始', 'en': 'Booking start', 'ko': '예약 시작'},
    "bottom_label": {'ja': 'テイクアウト', 'en': 'Takeout orders', 'ko': '테이크아웃'},
    "rate_a_label": {'ja': '予約→テイクアウト比', 'en': 'Book → takeout', 'ko': '예약→테이크아웃 비'},
    "rate_b_label": {'ja': '開始→予約完了率', 'en': 'Start → book complete', 'ko': '시작→예약 완료율'},
    "biz": {
      "members_db": {
        "label": {"ja": '予約件数（台帳）', "en": 'Bookings (book)', "ko": '예약 건수(대장)'},
        "meaning": {"ja": '予約台帳の期間予約数', "en": 'Period table bookings', "ko": '예약 대장 기간 예약 수'},
        "formula": {"ja": 'COUNT(期間予約)', "en": 'COUNT(period books)', "ko": 'COUNT(기간 예약)'},
      },
      "paid_members": {
        "label": {"ja": '来店組数', "en": 'Parties seated', "ko": '방문 팀 수'},
        "meaning": {"ja": '来店した組数', "en": 'Parties that came', "ko": '방문한 팀 수'},
        "formula": {"ja": 'COUNT(期間来店)', "en": 'COUNT(period visits)', "ko": 'COUNT(기간 방문)'},
      },
      "paid_rate": {
        "label": {"ja": '来店率', "en": 'Show rate', "ko": '방문율'},
        "meaning": {"ja": '予約のうち来店割合', "en": 'Bookings that show up', "ko": '예약 중 방문 비율'},
        "formula": {"ja": '来店 ÷ 予約 × 100', "en": 'Visits ÷ books × 100', "ko": '방문 ÷ 예약 × 100'},
      },
      "revenue": {
        "label": {"ja": '売上（期間）', "en": 'Revenue (period)', "ko": '매출(기간)'},
        "meaning": {"ja": '飲食売上', "en": 'F&B revenue', "ko": '음식 매출'},
        "formula": {"ja": 'SUM(期間売上)', "en": 'SUM(period revenue)', "ko": 'SUM(기간 매출)'},
      },
      "arpu": {
        "label": {"ja": '客単価', "en": 'Spend per party', "ko": '객단가'},
        "meaning": {"ja": '来店1組あたり売上', "en": 'Revenue per party', "ko": '방문 1팀당 매출'},
        "formula": {"ja": '売上 ÷ 来店', "en": 'Revenue ÷ visits', "ko": '매출 ÷ 방문'},
      },
      "churn_rate": {
        "label": {"ja": 'キャンセル率', "en": 'Cancel rate', "ko": '취소율'},
        "meaning": {"ja": '予約キャンセル割合', "en": 'Booking cancellations', "ko": '예약 취소 비율'},
        "formula": {"ja": 'キャンセル ÷ 予約 × 100', "en": 'Cancels ÷ books × 100', "ko": '취소 ÷ 예약 × 100'},
      },
    },
    "notes": {
      "7d": [
        {"ja": 'menu_view は多いのに reserve_start が薄い週は、空き状況・人数選択UIを疑う。', "en": 'Many menu_view but thin reserve_start: check availability & party-size UI.', "ko": 'menu_view는 많은데 reserve_start가 얇은 주는 빈자리·인원 선택 UI를 의심.'},
        {"ja": 'Paid スパイク後の予約CVR低下は媒体の質を切るサイン。', "en": 'Booking CVR drop after Paid spikes: cut low-quality media.', "ko": 'Paid 스파이크 후 예약 CVR 하락은 매체 질을 줄이라는 신호.'},
        {"ja": '予約完了と台帳の予約数のズレは計測漏れのサイン。', "en": 'Gap between booking complete and the book signals tracking gaps.', "ko": '예약 완료와 대장 예약 수 차이는 계측 누락 신호.'},
      ],
      "28d": [
        {"ja": 'テイクアウト（order_takeout）は別KPI。店内予約と混ぜない。', "en": 'Takeout (order_takeout) is a separate KPI — don’t mix with dine-in bookings.', "ko": '테이크아웃(order_takeout)은 별도 KPI. 매장 예약과 섞지 마세요.'},
        {"ja": '開始→予約完了が目安を下回る月は、必須項目と空き枠運用を見直す。', "en": 'Months below start→complete band: revisit required fields & slot ops.', "ko": '시작→예약 완료가 기준 아래인 달은 필수 항목·빈 슬롯 운영을 재검토.'},
        {"ja": '来店・キャンセルは業務KPI。サイトは予約完了までを主転換に固定。', "en": 'Visits/cancels are business KPIs; keep site primary as booking complete.', "ko": '방문·취소는 업무 KPI. 사이트는 예약 완료까지를 주전환으로 고정.'},
      ],
    },
  },
  "gov": {
    "label": {'ja': '自治体・公共', 'en': 'Government & public', 'ko': '지자체·공공'},
    "hint": {'ja': '案内〜申請', 'en': 'Guide → apply', 'ko': '안내〜신청'},
    "signup_label": {'ja': '申請完了', 'en': 'Form submits', 'ko': '신청 완료'},
    "property": {'ja': '公共 Demo JP', 'en': 'Public Demo JP', 'ko': '공공 Demo JP'},
    "cvr_label": {'ja': '申請CVR', 'en': 'Apply CVR', 'ko': '신청 CVR'},
    "mid_label": {'ja': '申請開始', 'en': 'Apply start', 'ko': '신청 시작'},
    "bottom_label": {'ja': '状況確認', 'en': 'Status check', 'ko': '상황 확인'},
    "rate_a_label": {'ja': '申請開始→完了率', 'en': 'Start → apply complete', 'ko': '신청 시작→완료율'},
    "rate_b_label": {'ja': '案内→申請完了率', 'en': 'Guide → apply complete', 'ko': '안내→신청 완료율'},
    "biz": {
      "members_db": {
        "label": {"ja": '申請件数（受付）', "en": 'Applications (desk)', "ko": '신청 건수(접수)'},
        "meaning": {"ja": '受付システムの期間申請数', "en": 'Period form submits', "ko": '접수 시스템 기간 신청 수'},
        "formula": {"ja": 'COUNT(期間申請)', "en": 'COUNT(period apps)', "ko": 'COUNT(기간 신청)'},
      },
      "paid_members": {
        "label": {"ja": '処理中', "en": 'In process', "ko": '처리 중'},
        "meaning": {"ja": '処理・審査中', "en": 'Apps being processed', "ko": '처리·심사 중'},
        "formula": {"ja": 'COUNT(処理中)', "en": 'COUNT(in process)', "ko": 'COUNT(처리 중)'},
      },
      "paid_rate": {
        "label": {"ja": '完了率', "en": 'Completion rate', "ko": '완료율'},
        "meaning": {"ja": '申請のうち処理完了割合', "en": 'Apps fully processed', "ko": '신청 중 처리 완료 비율'},
        "formula": {"ja": '完了 ÷ 申請 × 100', "en": 'Done ÷ apps × 100', "ko": '완료 ÷ 신청 × 100'},
      },
      "revenue": {
        "label": {"ja": '手数料（期間）', "en": 'Fees (period)', "ko": '수수료(기간)'},
        "meaning": {"ja": '手数料・証紙など', "en": 'Fees / stamps etc.', "ko": '수수료·증지 등'},
        "formula": {"ja": 'SUM(期間手数料)', "en": 'SUM(period fees)', "ko": 'SUM(기간 수수료)'},
      },
      "arpu": {
        "label": {"ja": '申請単価', "en": 'Fee per apply', "ko": '신청 단가'},
        "meaning": {"ja": '申請1件あたり手数料', "en": 'Fee per application', "ko": '신청 1건당 수수료'},
        "formula": {"ja": '手数料 ÷ 申請', "en": 'Fees ÷ apps', "ko": '수수료 ÷ 신청'},
      },
      "churn_rate": {
        "label": {"ja": '取下率', "en": 'Withdraw rate', "ko": '취하율'},
        "meaning": {"ja": '申請取下の割合', "en": 'Applications withdrawn', "ko": '신청 취하 비율'},
        "formula": {"ja": '取下 ÷ 申請 × 100', "en": 'Withdraw ÷ apps × 100', "ko": '취하 ÷ 신청 × 100'},
      },
    },
    "notes": {
      "7d": [
        {"ja": 'guide_view は多いのに form_start が薄い週は、対象者条件・必要書類の明示を疑う。', "en": 'Many guide_view but thin form_start: clarify eligibility & required docs.', "ko": 'guide_view는 많은데 form_start가 얇은 주는 대상 조건·필요서류 명시를 의심.'},
        {"ja": '検索流入増でも申請CVRが落ちるときはランディングの意図ズレを疑う。', "en": 'Search up + Apply CVR down: suspect landing intent mismatch.', "ko": '검색 유입이 늘어도 신청 CVR이 떨어지면 랜딩 의도 어긋남을 의심.'},
        {"ja": '申請完了と受付DBの申請件数のズレは計測漏れのサイン。', "en": 'Gap between form complete and desk apps signals tracking gaps.', "ko": '신청 완료와 접수 DB 신청 건수 차이는 계측 누락 신호.'},
      ],
      "28d": [
        {"ja": '申請CVRは低めが普通。目安帯の外と離脱ページを優先する。', "en": 'Apply CVR is often low — prioritize band outliers and drop-off pages.', "ko": '신청 CVR은 낮은 편이 보통. 기준 밖과 이탈 페이지를 우선.'},
        {"ja": '案内→申請が落ちたら、手順説明とフォーム項目数を見直す。', "en": 'If guide→apply drops, revisit step copy and form field count.', "ko": '안내→신청이 떨어지면 절차 설명과 폼 항목 수를 재검토.'},
        {"ja": '処理完了は業務KPI。サイトは申請完了までを主転換に固定。', "en": 'Processing complete is a business KPI; keep site primary as form complete.', "ko": '처리 완료는 업무 KPI. 사이트는 신청 완료까지를 주전환으로 고정.'},
      ],
    },
  },
  "saas": {
    "label": {"ja": 'SaaS・B2B', "en": 'SaaS & B2B', "ko": 'SaaS·B2B'},
    "hint": {"ja": 'トライアル〜有料', "en": 'Trial → paid', "ko": '트라이얼〜유료'},
    "signup_label": {"ja": 'アカウント登録', "en": 'Account sign-ups', "ko": '계정 등록'},
    "property": {"ja": 'SaaS Demo JP', "en": 'SaaS Demo JP', "ko": 'SaaS Demo JP'},
    "cvr_label": {"ja": '登録CVR', "en": 'Sign-up CVR', "ko": '가입 CVR'},
    "mid_label": {"ja": '有料開始', "en": 'Start paid', "ko": '유료 시작'},
    "bottom_label": {"ja": '有料完了', "en": 'Paid complete', "ko": '유료 완료'},
    "rate_a_label": {"ja": '登録→有料開始率', "en": 'Sign-up → paid start', "ko": '가입→유료 시작률'},
    "rate_b_label": {"ja": '決済CVR', "en": 'Checkout CVR', "ko": '결제 CVR'},
    "biz": {
      "members_db": {
        "label": {"ja": 'アカウント数（DB）', "en": 'Accounts (DB)', "ko": '계정 수(DB)'},
        "meaning": {"ja": '業務DBの有効アカウント数', "en": 'Active accounts in business DB', "ko": '업무 DB 유효 계정 수'},
        "formula": {"ja": 'COUNT(有効アカウント)', "en": 'COUNT(active accounts)', "ko": 'COUNT(유효 계정)'},
      },
      "paid_members": {
        "label": {"ja": '有料アカウント数', "en": 'Paid accounts', "ko": '유료 계정 수'},
        "meaning": {"ja": '有料プラン中', "en": 'On a paid plan', "ko": '유료 플랜 중'},
        "formula": {"ja": 'COUNT(有料かつ有効)', "en": 'COUNT(paid & active)', "ko": 'COUNT(유료·유효)'},
      },
      "paid_rate": {
        "label": {"ja": '有料化率', "en": 'Paid rate', "ko": '유료화율'},
        "meaning": {"ja": '全アカウントのうち有料割合', "en": 'Share of accounts that are paid', "ko": '전체 계정 중 유료 비율'},
        "formula": {"ja": '有料 ÷ アカウント × 100', "en": 'Paid ÷ accounts × 100', "ko": '유료 ÷ 계정 × 100'},
      },
      "revenue": {
        "label": {"ja": 'MRR（期間）', "en": 'MRR (period)', "ko": 'MRR(기간)'},
        "meaning": {"ja": '課金側の期間売上/MRR', "en": 'Billing MRR / revenue', "ko": '과금 기간 매출/MRR'},
        "formula": {"ja": 'SUM(期間MRR)', "en": 'SUM(period MRR)', "ko": 'SUM(기간 MRR)'},
      },
      "arpu": {
        "label": {"ja": 'ARPU', "en": 'ARPU', "ko": 'ARPU'},
        "meaning": {"ja": 'アカウント1件あたり売上', "en": 'Revenue per account', "ko": '계정 1건당 매출'},
        "formula": {"ja": '売上 ÷ アカウント', "en": 'Revenue ÷ accounts', "ko": '매출 ÷ 계정'},
      },
      "churn_rate": {
        "label": {"ja": '解約率', "en": 'Churn rate', "ko": '해지율'},
        "meaning": {"ja": '期間中の解約割合', "en": 'Cancellations in the period', "ko": '기간 중 해지 비율'},
        "formula": {"ja": '解約 ÷ 有料 × 100', "en": 'Churn ÷ paid × 100', "ko": '해지 ÷ 유료 × 100'},
      },
    },
    "notes": {
      "7d": [
        {"ja": 'view_pricing は多いのに trial_start が薄い週は、料金・権限比較の見せ方を疑う。', "en": 'Many view_pricing but thin trial_start: check pricing & plan comparison.', "ko": 'view_pricing은 많은데 trial_start가 얇은 주는 요금·권한 비교 제시를 의심.'},
        {"ja": 'trial_start → sign_up の落差が大きい週は、オンボーディング摩擦を疑う。', "en": 'Large drop trial_start → sign_up: check onboarding friction.', "ko": 'trial_start → sign_up 낙차가 큰 주는 온보딩 마찰을 의심.'},
        {"ja": 'pay_success と請求DBの有料件数が乖離したら計測漏れを疑う。', "en": 'If pay_success diverges from billing paid counts, suspect tracking gaps.', "ko": 'pay_success와 청구 DB 유료 건수가 어긋나면 계측 누락을 의심.'},
      ],
      "28d": [
        {"ja": 'Organic / Referral が柱なら、比較記事・パートナー導線の深さを見る。', "en": 'If Organic/Referral leads, check comparison pages & partner paths.', "ko": 'Organic/Referral이 기둥이면 비교 기사·파트너 동선 깊이를 보세요.'},
        {"ja": '登録CVRが目安を下回る月は、トライアル条件と必須項目を見直す。', "en": 'Months below Sign-up CVR band: revisit trial terms and required fields.', "ko": '가입 CVR이 기준 아래인 달은 트라이얼 조건·필수 항목을 재검토.'},
        {"ja": 'invite_sent 増でも有料化が弱いときは、チーム招待後の価値体験を疑う。', "en": 'More invite_sent but weak paid conversion: check post-invite value experience.', "ko": 'invite_sent가 늘어도 유료화가 약하면 팀 초대 후 가치 체험을 의심.'},
      ],
    },
  },
  "community": {
    "label": {"ja": 'コミュニティ・アプリ', "en": 'Community & apps', "ko": '커뮤니티·앱'},
    "hint": {"ja": '登録〜参加', "en": 'Sign-up → engage', "ko": '가입〜참여'},
    "signup_label": {"ja": '会員登録', "en": 'Member sign-ups', "ko": '회원 가입'},
    "property": {"ja": 'Community Demo JP', "en": 'Community Demo JP', "ko": 'Community Demo JP'},
    "cvr_label": {"ja": '登録CVR', "en": 'Sign-up CVR', "ko": '가입 CVR'},
    "mid_label": {"ja": '有料開始', "en": 'Start paid', "ko": '유료 시작'},
    "bottom_label": {"ja": '有料完了', "en": 'Paid complete', "ko": '유료 완료'},
    "rate_a_label": {"ja": '登録→有料開始率', "en": 'Sign-up → paid start', "ko": '가입→유료 시작률'},
    "rate_b_label": {"ja": '決済CVR', "en": 'Checkout CVR', "ko": '결제 CVR'},
    "biz": {
      "members_db": {
        "label": {"ja": '会員数（DB）', "en": 'Members (DB)', "ko": '회원 수(DB)'},
        "meaning": {"ja": 'コミュニティの有効会員数', "en": 'Active community members', "ko": '커뮤니티 유효 회원 수'},
        "formula": {"ja": 'COUNT(有効会員)', "en": 'COUNT(active members)', "ko": 'COUNT(유효 회원)'},
      },
      "paid_members": {
        "label": {"ja": '有料会員数', "en": 'Paid members', "ko": '유료 회원 수'},
        "meaning": {"ja": '有料プラン中', "en": 'On a paid plan', "ko": '유료 플랜 중'},
        "formula": {"ja": 'COUNT(有料)', "en": 'COUNT(paid)', "ko": 'COUNT(유료)'},
      },
      "paid_rate": {
        "label": {"ja": '有料化率', "en": 'Paid rate', "ko": '유료화율'},
        "meaning": {"ja": '会員のうち有料割合', "en": 'Share of members who are paid', "ko": '회원 중 유료 비율'},
        "formula": {"ja": '有料 ÷ 会員 × 100', "en": 'Paid ÷ members × 100', "ko": '유료 ÷ 회원 × 100'},
      },
      "revenue": {
        "label": {"ja": '売上（期間）', "en": 'Revenue (period)', "ko": '매출(기간)'},
        "meaning": {"ja": '課金売上', "en": 'Billing revenue', "ko": '과금 매출'},
        "formula": {"ja": 'SUM(期間売上)', "en": 'SUM(period revenue)', "ko": 'SUM(기간 매출)'},
      },
      "arpu": {
        "label": {"ja": 'ARPU', "en": 'ARPU', "ko": 'ARPU'},
        "meaning": {"ja": '会員1人あたり売上', "en": 'Revenue per member', "ko": '회원 1인당 매출'},
        "formula": {"ja": '売上 ÷ 会員', "en": 'Revenue ÷ members', "ko": '매출 ÷ 회원'},
      },
      "churn_rate": {
        "label": {"ja": '退会率', "en": 'Churn rate', "ko": '탈퇴율'},
        "meaning": {"ja": '期間退会割合', "en": 'Member churn in the period', "ko": '기간 탈퇴 비율'},
        "formula": {"ja": '退会 ÷ 会員 × 100', "en": 'Churn ÷ members × 100', "ko": '탈퇴 ÷ 회원 × 100'},
      },
    },
    "notes": {
      "7d": [
        {"ja": 'sign_up は多いのに profile_complete が薄い週は、プロフィール必須項目を疑う。', "en": 'Many sign_up but thin profile_complete: check required profile fields.', "ko": 'sign_up은 많은데 profile_complete가 얇은 주는 프로필 필수 항목을 의심.'},
        {"ja": 'Organic Social 増でも登録CVRが落ちるときはクリエイティブの質を切る。', "en": 'Organic Social up + Sign-up CVR down: cut low-quality creatives.', "ko": 'Organic Social이 늘어도 가입 CVR이 떨어지면 크리에이티브 질을 줄이세요.'},
        {"ja": '会員数(DB)とGA登録が乖離したら計測漏れを疑う。', "en": 'If DB members diverge from GA sign-ups, suspect tracking gaps.', "ko": '회원 수(DB)와 GA 가입이 어긋나면 계측 누락을 의심.'},
      ],
      "28d": [
        {"ja": '再訪が高い月は投稿・グループ参加の定着施策を見る段階。', "en": 'High returning months: review post/group retention tactics.', "ko": '재방문이 높은 달은 게시·그룹 참여 정착 정책을 볼 단계.'},
        {"ja": '有料開始が弱い月は、特典・バッジの見せ方を見直す。', "en": 'Weak paid-start months: revisit perks and badge presentation.', "ko": '유료 시작이 약한 달은 특전·배지 제시를 재검토.'},
        {"ja": '退会率上昇時は通知過多と参加導線を疑う。', "en": 'Rising churn: suspect notification overload and join paths.', "ko": '탈퇴율 상승 시 알림 과다와 참여 동선을 의심.'},
      ],
    },
  },
  "news": {
    "label": {"ja": 'ニュース・購読', "en": 'News & subscriptions', "ko": '뉴스·구독'},
    "hint": {"ja": '記事〜購読', "en": 'Article → subscribe', "ko": '기사〜구독'},
    "signup_label": {"ja": 'メルマガ登録', "en": 'Newsletter sign-ups', "ko": '뉴스레터 구독'},
    "property": {"ja": 'News Demo JP', "en": 'News Demo JP', "ko": 'News Demo JP'},
    "cvr_label": {"ja": '登録CVR', "en": 'Sign-up CVR', "ko": '구독 CVR'},
    "mid_label": {"ja": 'CTAクリック', "en": 'CTA clicks', "ko": 'CTA 클릭'},
    "bottom_label": {"ja": '購読開始', "en": 'Subscribe start', "ko": '구독 시작'},
    "rate_a_label": {"ja": '登録→購読開始率', "en": 'Sign-up → subscribe start', "ko": '구독→유료 시작률'},
    "rate_b_label": {"ja": 'CTA→購読開始率', "en": 'CTA → subscribe start', "ko": 'CTA→구독 시작률'},
    "biz": {
      "members_db": {
        "label": {"ja": '購読者数（DB）', "en": 'Subscribers (DB)', "ko": '구독자 수(DB)'},
        "meaning": {"ja": '配信DBの有効購読者', "en": 'Active newsletter subscribers', "ko": '발송 DB 유효 구독자'},
        "formula": {"ja": 'COUNT(有効購読)', "en": 'COUNT(active subs)', "ko": 'COUNT(유효 구독)'},
      },
      "paid_members": {
        "label": {"ja": '有料購読者数', "en": 'Paid subscribers', "ko": '유료 구독자 수'},
        "meaning": {"ja": '有料購読中', "en": 'Active paid subscriptions', "ko": '유료 구독 중'},
        "formula": {"ja": 'COUNT(有料)', "en": 'COUNT(paid)', "ko": 'COUNT(유료)'},
      },
      "paid_rate": {
        "label": {"ja": '有料化率', "en": 'Paid rate', "ko": '유료화율'},
        "meaning": {"ja": '購読者のうち有料', "en": 'Share of subscribers who are paid', "ko": '구독자 중 유료'},
        "formula": {"ja": '有料 ÷ 購読 × 100', "en": 'Paid ÷ subs × 100', "ko": '유료 ÷ 구독 × 100'},
      },
      "revenue": {
        "label": {"ja": '購読売上（期間）', "en": 'Sub revenue', "ko": '구독 매출(기간)'},
        "meaning": {"ja": '有料購読売上', "en": 'Paid subscription revenue', "ko": '유료 구독 매출'},
        "formula": {"ja": 'SUM(期間売上)', "en": 'SUM(period revenue)', "ko": 'SUM(기간 매출)'},
      },
      "arpu": {
        "label": {"ja": 'ARPU', "en": 'ARPU', "ko": 'ARPU'},
        "meaning": {"ja": '購読者1人あたり売上', "en": 'Revenue per subscriber', "ko": '구독자 1인당 매출'},
        "formula": {"ja": '売上 ÷ 購読者', "en": 'Revenue ÷ subscribers', "ko": '매출 ÷ 구독자'},
      },
      "churn_rate": {
        "label": {"ja": '解約率', "en": 'Churn rate', "ko": '해지율'},
        "meaning": {"ja": '購読解約割合', "en": 'Paid cancel rate', "ko": '구독 해지 비율'},
        "formula": {"ja": '解約 ÷ 有料 × 100', "en": 'Churn ÷ paid × 100', "ko": '해지 ÷ 유료 × 100'},
      },
    },
    "notes": {
      "7d": [
        {"ja": 'article_view は多いのに newsletter_signup が薄い週は、CTA位置・記事テーマを疑う。', "en": 'Many article_view but thin newsletter_signup: check CTA placement & topics.', "ko": 'article_view는 많은데 newsletter_signup이 얇은 주는 CTA·기사 주제를 의심.'},
        {"ja": 'paywall_view 増でも subscribe_start が弱いときは料金提示を見直す。', "en": 'More paywall_view but weak subscribe_start: revisit pricing presentation.', "ko": 'paywall_view가 늘어도 subscribe_start가 약하면 요금 제시를 재검토.'},
        {"ja": '登録と配信DBの購読者数が乖離したら計測漏れを疑う。', "en": 'If sign-ups diverge from delivery-DB subscribers, suspect tracking gaps.', "ko": '가입과 발송 DB 구독자 수가 어긋나면 계측 누락을 의심.'},
      ],
      "28d": [
        {"ja": 'SEOが主戦場。Socialスパイク後の翌日再訪を別枠で見る。', "en": 'SEO is the main field; track next-day return after Social spikes separately.', "ko": 'SEO가 주전장. Social 스파이크 후 다음날 재방문을 별도로 보세요.'},
        {"ja": '登録率1%前後ならテーマずれを優先して疑う。', "en": 'Around 1% sign-up rate: prioritize topic mismatch over CTA tweaks.', "ko": '구독률 1% 전후면 주제 어긋남을 우선 의심.'},
        {"ja": '有料導線は弱めでも、まず登録の質を安定させる。', "en": 'Even if paid path is weak, stabilize sign-up quality first.', "ko": '유료 동선이 약해도 먼저 구독 품질을 안정시키세요.'},
      ],
    },
  },
  "creator": {
    "label": {"ja": 'クリエイター・UGC', "en": 'Creators & UGC', "ko": '크리에이터·UGC'},
    "hint": {"ja": '視聴〜フォロー', "en": 'Watch → follow', "ko": '시청〜팔로우'},
    "signup_label": {"ja": 'フォロー完了', "en": 'Follows', "ko": '팔로우 완료'},
    "property": {"ja": 'Creator Demo JP', "en": 'Creator Demo JP', "ko": 'Creator Demo JP'},
    "cvr_label": {"ja": 'フォローCVR', "en": 'Follow CVR', "ko": '팔로우 CVR'},
    "mid_label": {"ja": 'CTAクリック', "en": 'CTA clicks', "ko": 'CTA 클릭'},
    "bottom_label": {"ja": 'メンバーシップ', "en": 'Membership joins', "ko": '멤버십'},
    "rate_a_label": {"ja": 'フォロー→メンバー率', "en": 'Follow → membership', "ko": '팔로우→멤버율'},
    "rate_b_label": {"ja": 'CTA→メンバー率', "en": 'CTA → membership', "ko": 'CTA→멤버율'},
    "biz": {
      "members_db": {
        "label": {"ja": 'フォロワー数（DB）', "en": 'Followers (DB)', "ko": '팔로워 수(DB)'},
        "meaning": {"ja": 'プラットフォームのフォロワー', "en": 'Platform followers', "ko": '플랫폼 팔로워'},
        "formula": {"ja": 'COUNT(フォロワー)', "en": 'COUNT(followers)', "ko": 'COUNT(팔로워)'},
      },
      "paid_members": {
        "label": {"ja": 'メンバー数', "en": 'Members', "ko": '멤버 수'},
        "meaning": {"ja": '有料メンバーシップ', "en": 'Paid memberships', "ko": '유료 멤버십'},
        "formula": {"ja": 'COUNT(有料メンバー)', "en": 'COUNT(paid members)', "ko": 'COUNT(유료 멤버)'},
      },
      "paid_rate": {
        "label": {"ja": 'メンバー化率', "en": 'Membership rate', "ko": '멤버화율'},
        "meaning": {"ja": 'フォロワーのうち有料', "en": 'Followers who become paid', "ko": '팔로워 중 유료'},
        "formula": {"ja": 'メンバー ÷ フォロワー × 100', "en": 'Members ÷ followers × 100', "ko": '멤버 ÷ 팔로워 × 100'},
      },
      "revenue": {
        "label": {"ja": '売上（期間）', "en": 'Revenue (period)', "ko": '매출(기간)'},
        "meaning": {"ja": 'メンバー・チップ売上', "en": 'Membership + tips', "ko": '멤버·팁 매출'},
        "formula": {"ja": 'SUM(期間売上)', "en": 'SUM(period revenue)', "ko": 'SUM(기간 매출)'},
      },
      "arpu": {
        "label": {"ja": 'ARPU', "en": 'ARPU', "ko": 'ARPU'},
        "meaning": {"ja": 'フォロワー1人あたり売上', "en": 'Revenue per follower', "ko": '팔로워 1인당 매출'},
        "formula": {"ja": '売上 ÷ フォロワー', "en": 'Revenue ÷ followers', "ko": '매출 ÷ 팔로워'},
      },
      "churn_rate": {
        "label": {"ja": '解約率', "en": 'Churn rate', "ko": '해지율'},
        "meaning": {"ja": 'メンバー解約割合', "en": 'Membership cancels', "ko": '멤버 해지 비율'},
        "formula": {"ja": '解約 ÷ メンバー × 100', "en": 'Churn ÷ members × 100', "ko": '해지 ÷ 멤버 × 100'},
      },
    },
    "notes": {
      "7d": [
        {"ja": 'content_view は多いのに follow が薄い週は、プロフィール・CTAを疑う。', "en": 'Many content_view but thin follow: check profile and CTAs.', "ko": 'content_view는 많은데 follow가 얇은 주는 프로필·CTA를 의심.'},
        {"ja": 'Paid Social スパイク後のフォローCVR低下は媒体の質を切るサイン。', "en": 'Follow CVR drop after Paid Social spikes: cut low-quality media.', "ko": 'Paid Social 스파이크 후 팔로우 CVR 하락은 매체 질을 줄이라는 신호.'},
        {"ja": 'follow とフォロワーDBのズレは計測漏れのサイン。', "en": 'Gap between follow and follower DB signals tracking gaps.', "ko": 'follow와 팔로워 DB 차이는 계측 누락 신호.'},
      ],
      "28d": [
        {"ja": 'Organic Social が柱なら、投稿フォーマット別の定着を見る。', "en": 'If Organic Social leads, check retention by post format.', "ko": 'Organic Social이 기둥이면 게시 포맷별 정착을 보세요.'},
        {"ja": 'メンバーシップ加入が弱い月は特典説明と価格帯を見直す。', "en": 'Weak membership months: revisit perk copy and price tiers.', "ko": '멤버십 가입이 약한 달은 특전 설명·가격대를 재검토.'},
        {"ja": 'チップ開始→加入の落差は決済摩擦のサイン。', "en": 'tip_start → join drop signals payment friction.', "ko": '팁 시작→가입 낙차는 결제 마찰 신호.'},
      ],
    },
  },
  "parttime": {
    "label": {"ja": 'アルバイト・シフト', "en": 'Part-time & shifts', "ko": '아르바이트·시프트'},
    "hint": {"ja": '求人〜応募', "en": 'Jobs → apply', "ko": '채용공고〜지원'},
    "signup_label": {"ja": '応募完了', "en": 'Applications', "ko": '지원 완료'},
    "property": {"ja": 'アルバイト Demo JP', "en": 'Part-time Demo JP', "ko": '아르바이트 Demo JP'},
    "cvr_label": {"ja": '応募CVR', "en": 'Apply CVR', "ko": '지원 CVR'},
    "mid_label": {"ja": '応募開始', "en": 'Apply start', "ko": '지원 시작'},
    "bottom_label": {"ja": 'シフト確定', "en": 'Shift confirmed', "ko": '시프트 확정'},
    "rate_a_label": {"ja": '応募→シフト確定率', "en": 'Apply → shift confirm', "ko": '지원→시프트 확정율'},
    "rate_b_label": {"ja": '開始→完了率', "en": 'Start → complete', "ko": '시작→완료율'},
    "biz": {
      "members_db": {
        "label": {"ja": '応募者数（ATS）', "en": 'Applicants (ATS)', "ko": '지원자 수(ATS)'},
        "meaning": {"ja": '期間応募者数', "en": 'Period applicants', "ko": '기간 지원자 수'},
        "formula": {"ja": 'ATS: COUNT(期間応募)', "en": 'ATS: COUNT(period apps)', "ko": 'ATS: COUNT(기간 지원)'},
      },
      "paid_members": {
        "label": {"ja": '勤務確定数', "en": 'Shifts confirmed', "ko": '근무 확정 수'},
        "meaning": {"ja": 'シフト確定した人数', "en": 'People with confirmed shifts', "ko": '시프트 확정 인원'},
        "formula": {"ja": 'COUNT(シフト確定)', "en": 'COUNT(shift confirmed)', "ko": 'COUNT(시프트 확정)'},
      },
      "paid_rate": {
        "label": {"ja": '確定率', "en": 'Confirm rate', "ko": '확정율'},
        "meaning": {"ja": '応募のうち確定', "en": 'Apps that confirm a shift', "ko": '지원 중 확정'},
        "formula": {"ja": '確定 ÷ 応募 × 100', "en": 'Confirmed ÷ apps × 100', "ko": '확정 ÷ 지원 × 100'},
      },
      "revenue": {
        "label": {"ja": '採用コスト（期間）', "en": 'Hiring cost', "ko": '채용 비용(기간)'},
        "meaning": {"ja": '媒体費など', "en": 'Media spend etc.', "ko": '매체비 등'},
        "formula": {"ja": 'SUM(期間コスト)', "en": 'SUM(period cost)', "ko": 'SUM(기간 비용)'},
      },
      "arpu": {
        "label": {"ja": '応募単価', "en": 'Cost per apply', "ko": '지원 단가'},
        "meaning": {"ja": '応募1件あたりコスト', "en": 'Cost per application', "ko": '지원 1건당 비용'},
        "formula": {"ja": 'コスト ÷ 応募', "en": 'Cost ÷ apps', "ko": '비용 ÷ 지원'},
      },
      "churn_rate": {
        "label": {"ja": '辞退率', "en": 'Drop-out rate', "ko": '사퇴율'},
        "meaning": {"ja": '応募後の辞退割合', "en": 'Withdrawals after apply', "ko": '지원 후 사퇴 비율'},
        "formula": {"ja": '辞退 ÷ 応募 × 100', "en": 'Drops ÷ apps × 100', "ko": '사퇴 ÷ 지원 × 100'},
      },
    },
    "notes": {
      "7d": [
        {"ja": 'job_view は多いのに apply_start が薄い週は、時給・勤務地の見せ方を疑う。', "en": 'Many job_view but thin apply_start: check wage & location presentation.', "ko": 'job_view는 많은데 apply_start가 얇은 주는 시급·근무지 제시를 의심.'},
        {"ja": 'Paid 増で応募CVRが落ちるときは媒体の質を切る。', "en": 'Paid up + Apply CVR down: cut low-quality media.', "ko": 'Paid가 늘고 지원 CVR이 떨어지면 매체 질을 줄이세요.'},
        {"ja": '応募完了とATS件数のズレは計測漏れのサイン。', "en": 'Gap between apply complete and ATS counts signals tracking gaps.', "ko": '지원 완료와 ATS 건수 차이는 계측 누락 신호.'},
      ],
      "28d": [
        {"ja": '地図・エリア検索が柱なら、地域LPの深さを見る。', "en": 'If map/area search leads, check depth of local landing pages.', "ko": '지도·지역 검색이 기둥이면 지역 LP 깊이를 보세요.'},
        {"ja": '開始→完了が目安を下回る月は、フォーム項目を見直す。', "en": 'Months below start→complete band: revisit form fields.', "ko": '시작→완료가 기준 아래인 달은 폼 항목을 재검토.'},
        {"ja": 'シフト確定は次KPI。サイト主転換は応募完了に固定。', "en": 'Shift confirm is next KPI; keep site primary as apply complete.', "ko": '시프트 확정은 다음 KPI. 사이트 주전환은 지원 완료로 고정.'},
      ],
    },
  },
  "agency": {
    "label": {"ja": '人材紹介・エージェント', "en": 'Recruiting agency', "ko": '인재소개·에이전트'},
    "hint": {"ja": '候補〜紹介', "en": 'Candidates → place', "ko": '후보〜소개'},
    "signup_label": {"ja": '応募・推薦完了', "en": 'Applications / referrals', "ko": '지원·추천 완료'},
    "property": {"ja": '人材紹介 Demo JP', "en": 'Agency Demo JP', "ko": '인재소개 Demo JP'},
    "cvr_label": {"ja": '応募CVR', "en": 'Apply CVR', "ko": '지원 CVR'},
    "mid_label": {"ja": 'マッチ開始', "en": 'Match start', "ko": '매치 시작'},
    "bottom_label": {"ja": '面接予約', "en": 'Interview booked', "ko": '면접 예약'},
    "rate_a_label": {"ja": '応募→面接率', "en": 'Apply → interview', "ko": '지원→면접률'},
    "rate_b_label": {"ja": 'マッチ→応募率', "en": 'Match → apply', "ko": '매치→지원률'},
    "biz": {
      "members_db": {
        "label": {"ja": '候補者数（CRM）', "en": 'Candidates (CRM)', "ko": '후보자 수(CRM)'},
        "meaning": {"ja": '期間候補者数', "en": 'Period candidates', "ko": '기간 후보자 수'},
        "formula": {"ja": 'CRM: COUNT(期間候補)', "en": 'CRM: COUNT(period candidates)', "ko": 'CRM: COUNT(기간 후보)'},
      },
      "paid_members": {
        "label": {"ja": '選考中', "en": 'In process', "ko": '선고 중'},
        "meaning": {"ja": '選考プロセス中', "en": 'Candidates in process', "ko": '선고 프로세스 중'},
        "formula": {"ja": 'COUNT(選考中)', "en": 'COUNT(in process)', "ko": 'COUNT(선고 중)'},
      },
      "paid_rate": {
        "label": {"ja": '面接化率', "en": 'Interview rate', "ko": '면접화율'},
        "meaning": {"ja": '応募のうち面接', "en": 'Apps that reach interview', "ko": '지원 중 면접'},
        "formula": {"ja": '面接 ÷ 応募 × 100', "en": 'Interviews ÷ apps × 100', "ko": '면접 ÷ 지원 × 100'},
      },
      "revenue": {
        "label": {"ja": '紹介成功報酬（期間）', "en": 'Placement fees', "ko": '소개 성공 보수(기간)'},
        "meaning": {"ja": '成功報酬売上', "en": 'Success-fee revenue', "ko": '성공 보수 매출'},
        "formula": {"ja": 'SUM(期間報酬)', "en": 'SUM(period fees)', "ko": 'SUM(기간 보수)'},
      },
      "arpu": {
        "label": {"ja": '応募単価', "en": 'Cost per apply', "ko": '지원 단가'},
        "meaning": {"ja": '応募1件あたりコスト', "en": 'Cost per application', "ko": '지원 1건당 비용'},
        "formula": {"ja": 'コスト ÷ 応募', "en": 'Cost ÷ apps', "ko": '비용 ÷ 지원'},
      },
      "churn_rate": {
        "label": {"ja": '辞退率', "en": 'Drop-out rate', "ko": '사퇴율'},
        "meaning": {"ja": '選考辞退割合', "en": 'Withdrawals in process', "ko": '선고 사퇴 비율'},
        "formula": {"ja": '辞退 ÷ 選考 × 100', "en": 'Drops ÷ process × 100', "ko": '사퇴 ÷ 선고 × 100'},
      },
    },
    "notes": {
      "7d": [
        {"ja": 'candidate_view 増でも match_start が薄い週は、条件マッチ表示を疑う。', "en": 'More candidate_view but thin match_start: check match condition UI.', "ko": 'candidate_view가 늘어도 match_start가 얇은 주는 조건 매치 표시를 의심.'},
        {"ja": 'resume_dl は多いのに応募が弱いときは、次CTAを見直す。', "en": 'Many resume_dl but weak apply: revisit the next CTA.', "ko": 'resume_dl은 많은데 지원이 약하면 다음 CTA를 재검토.'},
        {"ja": '応募とCRM件数のズレは計測漏れのサイン。', "en": 'Gap between apply and CRM counts signals tracking gaps.', "ko": '지원과 CRM 건수 차이는 계측 누락 신호.'},
      ],
      "28d": [
        {"ja": '紹介→面接の歩留まりが落ちたら、求人要件と候補者提示を見直す。', "en": 'If place→interview drops, revisit reqs and candidate presentation.', "ko": '소개→면접 수익률이 떨어지면 채용 요건·후보자 제시를 재검토.'},
        {"ja": 'セッションが長くCVRが低いのは普通。目安帯の外だけを追う。', "en": 'Long sessions + low CVR is normal — chase band outliers only.', "ko": '세션이 길고 CVR이 낮은 것은 보통. 기준 밖만 추적.'},
        {"ja": '内定（offer）は業務KPI。サイトは応募完了までを主転換に固定。', "en": 'Offers are a business KPI; keep site primary as apply complete.', "ko": '내정(offer)은 업무 KPI. 사이트는 지원 완료까지를 주전환으로 고정.'},
      ],
    },
  },
  "marketplace": {
    "label": {"ja": 'マーケットプレイス', "en": 'Marketplace', "ko": '마켓플레이스'},
    "hint": {"ja": '検索〜購入', "en": 'Search → buy', "ko": '검색〜구매'},
    "signup_label": {"ja": '購入完了', "en": 'Purchases', "ko": '구매 완료'},
    "property": {"ja": 'Marketplace Demo JP', "en": 'Marketplace Demo JP', "ko": 'Marketplace Demo JP'},
    "cvr_label": {"ja": '購入CVR', "en": 'Purchase CVR', "ko": '구매 CVR'},
    "mid_label": {"ja": 'カート追加', "en": 'Add to cart', "ko": '장바구니 추가'},
    "bottom_label": {"ja": 'チェックアウト開始', "en": 'Begin checkout', "ko": '결제 시작'},
    "rate_a_label": {"ja": 'カート→購入率', "en": 'Cart → purchase', "ko": '장바구니→구매율'},
    "rate_b_label": {"ja": 'チェックアウト→購入率', "en": 'Checkout → purchase', "ko": '결제 시작→구매율'},
    "biz": {
      "members_db": {
        "label": {"ja": '注文件数（受注）', "en": 'Orders', "ko": '주문 건수(수주)'},
        "meaning": {"ja": '期間注文件数', "en": 'Period orders', "ko": '기간 주문 건수'},
        "formula": {"ja": 'COUNT(期間注文)', "en": 'COUNT(period orders)', "ko": 'COUNT(기간 주문)'},
      },
      "paid_members": {
        "label": {"ja": '取引完了件数', "en": 'Completed trades', "ko": '거래 완료 건수'},
        "meaning": {"ja": '完了した取引', "en": 'Completed transactions', "ko": '완료된 거래'},
        "formula": {"ja": 'COUNT(取引完了)', "en": 'COUNT(completed)', "ko": 'COUNT(거래 완료)'},
      },
      "paid_rate": {
        "label": {"ja": '取引完了率', "en": 'Completion rate', "ko": '거래 완료율'},
        "meaning": {"ja": '注文のうち完了', "en": 'Orders that complete', "ko": '주문 중 완료'},
        "formula": {"ja": '完了 ÷ 注文 × 100', "en": 'Done ÷ orders × 100', "ko": '완료 ÷ 주문 × 100'},
      },
      "revenue": {
        "label": {"ja": '流通総額（期間）', "en": 'GMV (period)', "ko": '유통 총액(기간)'},
        "meaning": {"ja": 'GMV', "en": 'Gross merchandise value', "ko": 'GMV'},
        "formula": {"ja": 'SUM(期間GMV)', "en": 'SUM(period GMV)', "ko": 'SUM(기간 GMV)'},
      },
      "arpu": {
        "label": {"ja": '客単価', "en": 'AOV', "ko": '객단가'},
        "meaning": {"ja": '注文1件あたりGMV', "en": 'GMV per order', "ko": '주문 1건당 GMV'},
        "formula": {"ja": 'GMV ÷ 注文', "en": 'GMV ÷ orders', "ko": 'GMV ÷ 주문'},
      },
      "churn_rate": {
        "label": {"ja": 'キャンセル率', "en": 'Cancel rate', "ko": '취소율'},
        "meaning": {"ja": '注文キャンセル割合', "en": 'Order cancellations', "ko": '주문 취소 비율'},
        "formula": {"ja": 'キャンセル ÷ 注文 × 100', "en": 'Cancels ÷ orders × 100', "ko": '취소 ÷ 주문 × 100'},
      },
    },
    "notes": {
      "7d": [
        {"ja": 'search は多いのに view_item が薄い週は、検索結果の質を疑う。', "en": 'Many search but thin view_item: check search-result quality.', "ko": 'search는 많은데 view_item이 얇은 주는 검색 결과 질을 의심.'},
        {"ja": 'カート増でも購入が弱いときは送料・決済・出品者評価を見直す。', "en": 'More carts but weak purchase: revisit shipping, payments, seller ratings.', "ko": '장바구니가 늘어도 구매가 약하면 배송비·결제·판매자 평가를 재검토.'},
        {"ja": 'purchase と注文DBのズレは計測漏れのサイン。', "en": 'Gap between purchase and order DB signals tracking gaps.', "ko": 'purchase와 주문 DB 차이는 계측 누락 신호.'},
      ],
      "28d": [
        {"ja": '出品者コンタクトは別KPI。購入と混ぜない。', "en": "Seller contact is a separate KPI — don't mix with purchase.", "ko": '판매자 연락은 별도 KPI. 구매와 섞지 마세요.'},
        {"ja": 'カート→購入が目安を下回る月は、ゲスト購入と決済手段を見直す。', "en": 'Months below cart→purchase band: revisit guest checkout & payments.', "ko": '장바구니→구매가 기준 아래인 달은 게스트 구매·결제수단을 재검토.'},
        {"ja": 'リピートは業務KPI。サイトは初回購入までを主転換に固定。', "en": 'Repeat is a business KPI; keep site primary as first purchase.', "ko": '리피트는 업무 KPI. 사이트는 첫 구매까지를 주전환으로 고정.'},
      ],
    },
  },
  "d2c": {
    "label": {"ja": 'D2C・定期便', "en": 'D2C & subscription boxes', "ko": 'D2C·정기배송'},
    "hint": {"ja": '商品〜定期', "en": 'Product → subscribe', "ko": '상품〜정기'},
    "signup_label": {"ja": '購入完了', "en": 'Purchases', "ko": '구매 완료'},
    "property": {"ja": 'D2C Demo JP', "en": 'D2C Demo JP', "ko": 'D2C Demo JP'},
    "cvr_label": {"ja": '購入CVR', "en": 'Purchase CVR', "ko": '구매 CVR'},
    "mid_label": {"ja": 'カート追加', "en": 'Add to cart', "ko": '장바구니 추가'},
    "bottom_label": {"ja": 'チェックアウト開始', "en": 'Begin checkout', "ko": '결제 시작'},
    "rate_a_label": {"ja": 'カート→購入率', "en": 'Cart → purchase', "ko": '장바구니→구매율'},
    "rate_b_label": {"ja": 'チェックアウト→購入率', "en": 'Checkout → purchase', "ko": '결제 시작→구매율'},
    "biz": {
      "members_db": {
        "label": {"ja": '注文件数（受注）', "en": 'Orders', "ko": '주문 건수(수주)'},
        "meaning": {"ja": '期間注文件数', "en": 'Period orders', "ko": '기간 주문 건수'},
        "formula": {"ja": 'COUNT(期間注文)', "en": 'COUNT(period orders)', "ko": 'COUNT(기간 주문)'},
      },
      "paid_members": {
        "label": {"ja": '定期契約数', "en": 'Active subscriptions', "ko": '정기 계약 수'},
        "meaning": {"ja": '有効な定期便契約', "en": 'Active box subscriptions', "ko": '유효 정기배송 계약'},
        "formula": {"ja": 'COUNT(有効定期)', "en": 'COUNT(active subs)', "ko": 'COUNT(유효 정기)'},
      },
      "paid_rate": {
        "label": {"ja": '定期化率', "en": 'Subscribe rate', "ko": '정기화율'},
        "meaning": {"ja": '初回購入のうち定期', "en": 'First buys that become subscriptions', "ko": '첫 구매 중 정기'},
        "formula": {"ja": '定期 ÷ 初回 × 100', "en": 'Subs ÷ first buys × 100', "ko": '정기 ÷ 첫 구매 × 100'},
      },
      "revenue": {
        "label": {"ja": '売上（期間）', "en": 'Revenue (period)', "ko": '매출(기간)'},
        "meaning": {"ja": '受注売上', "en": 'Order revenue', "ko": '수주 매출'},
        "formula": {"ja": 'SUM(期間売上)', "en": 'SUM(period revenue)', "ko": 'SUM(기간 매출)'},
      },
      "arpu": {
        "label": {"ja": '客単価', "en": 'AOV', "ko": '객단가'},
        "meaning": {"ja": '注文1件あたり売上', "en": 'Revenue per order', "ko": '주문 1건당 매출'},
        "formula": {"ja": '売上 ÷ 注文', "en": 'Revenue ÷ orders', "ko": '매출 ÷ 주문'},
      },
      "churn_rate": {
        "label": {"ja": '定期解約率', "en": 'Sub churn', "ko": '정기 해지율'},
        "meaning": {"ja": '定期の解約割合', "en": 'Subscription cancels', "ko": '정기 해지 비율'},
        "formula": {"ja": '解約 ÷ 定期 × 100', "en": 'Churn ÷ subs × 100', "ko": '해지 ÷ 정기 × 100'},
      },
    },
    "notes": {
      "7d": [
        {"ja": 'quiz_complete 増でも add_to_cart が薄い週は、レコメンド結果の質を疑う。', "en": 'More quiz_complete but thin add_to_cart: check recommendation quality.', "ko": 'quiz_complete가 늘어도 add_to_cart가 얇은 주는 추천 결과 질을 의심.'},
        {"ja": 'Paid Social 増で購入CVRが落ちるときはクリエイティブを切る。', "en": 'Paid Social up + Purchase CVR down: cut weak creatives.', "ko": 'Paid Social이 늘고 구매 CVR이 떨어지면 크리에이티브를 줄이세요.'},
        {"ja": 'purchase と受注DBのズレは計測漏れのサイン。', "en": 'Gap between purchase and OMS signals tracking gaps.', "ko": 'purchase와 수주 DB 차이는 계측 누락 신호.'},
      ],
      "28d": [
        {"ja": '定期便（subscribe_box）は次KPI。初回購入と分けて見る。', "en": 'subscribe_box is next KPI — track separately from first purchase.', "ko": '정기배송(subscribe_box)은 다음 KPI. 첫 구매와 나눠 보세요.'},
        {"ja": 'カート→購入が目安を下回る月は、定期割引の見せ方を見直す。', "en": 'Months below cart→purchase band: revisit subscription discount framing.', "ko": '장바구니→구매가 기준 아래인 달은 정기 할인 제시를 재검토.'},
        {"ja": '解約・スキップは業務KPI。サイトは初回購入までを主転換に固定。', "en": 'Cancel/skip are business KPIs; keep site primary as first purchase.', "ko": '해지·스킵은 업무 KPI. 사이트는 첫 구매까지를 주전환으로 고정.'},
      ],
    },
  },
}


def pack_text(slug: str, field: str, locale: str, fallback: str = "") -> str:
    from sitekpi.packs.behaviors import behavior_hint, behavior_label, category_of, rep_of

    cat = category_of(slug)
    if cat and field == "label":
        return behavior_label(cat, locale)
    if cat and field == "hint":
        return behavior_hint(cat, locale)
    slug = rep_of(slug)
    row = (PACK_L10N.get(slug) or {}).get(field) or {}
    if isinstance(row, dict):
        return str(row.get(locale) or row.get("ja") or fallback)
    return fallback


def pack_biz_rows(slug: str, locale: str, ja_biz: list) -> list[tuple[str, str, str, str]]:
    """Return [(id, label, meaning, formula), ...] localized."""
    from sitekpi.packs.behaviors import rep_of

    loc_biz = ((PACK_L10N.get(rep_of(slug)) or {}).get("biz") or {})
    out = []
    for bid, label, meaning, formula in ja_biz:
        b = loc_biz.get(bid) or {}
        out.append(
            (
                bid,
                str((b.get("label") or {}).get(locale) or (b.get("label") or {}).get("ja") or label),
                str((b.get("meaning") or {}).get(locale) or (b.get("meaning") or {}).get("ja") or meaning),
                str((b.get("formula") or {}).get(locale) or (b.get("formula") or {}).get("ja") or formula),
            )
        )
    return out


def pack_notes(slug: str, period: str, locale: str, ja_notes: list[str]) -> list[str]:
    from sitekpi.packs.behaviors import rep_of

    loc_notes = ((PACK_L10N.get(rep_of(slug)) or {}).get("notes") or {}).get(period) or []
    out = []
    for i, ja in enumerate(ja_notes):
        if i < len(loc_notes) and isinstance(loc_notes[i], dict):
            out.append(str(loc_notes[i].get(locale) or loc_notes[i].get("ja") or ja))
        else:
            out.append(ja)
    return out
