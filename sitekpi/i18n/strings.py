"""UI chrome strings (ja / en / ko). Pack KPI copy stays pack-owned for now."""

from __future__ import annotations

LOCALES: dict[str, dict[str, str]] = {
    "ja": {"label": "日本語", "html_lang": "ja"},
    "en": {"label": "English", "html_lang": "en"},
    "ko": {"label": "한국어", "html_lang": "ko"},
}

# key -> {ja, en, ko}
UI: dict[str, dict[str, str]] = {
    # Nav
    "nav.samples": {
        "ja": "サンプルパック",
        "en": "Sample packs",
        "ko": "샘플 팩",
    },
    "nav.connected": {
        "ja": "接続済み",
        "en": "Connected",
        "ko": "연결됨",
    },
    "nav.app": {
        "ja": "アプリ",
        "en": "App",
        "ko": "앱",
    },
    "nav.builder": {
        "ja": "ビルダー",
        "en": "Builder",
        "ko": "빌더",
    },
    "nav.connect": {
        "ja": "GA4 接続",
        "en": "GA4 connect",
        "ko": "GA4 연결",
    },
    "nav.settings": {
        "ja": "設定",
        "en": "Settings",
        "ko": "설정",
    },
    "nav.packs_aria": {
        "ja": "業界パック",
        "en": "Industry packs",
        "ko": "업계 팩",
    },
    "nav.ga4_aria": {
        "ja": "GA4接続",
        "en": "GA4 connection",
        "ko": "GA4 연결",
    },
    "nav.demo_name": {
        "ja": "{name}（デモ）",
        "en": "{name} (demo)",
        "ko": "{name} (데모)",
    },
    "nav.menu": {"ja": "メニュー", "en": "Menu", "ko": "메뉴"},
    "nav.property": {
        "ja": "接続プロパティ",
        "en": "Connected property",
        "ko": "연결된 속성",
    },
    "nav.change_property": {
        "ja": "+ プロパティ変更",
        "en": "+ Change property",
        "ko": "+ 속성 변경",
    },
    "nav.disconnected": {
        "ja": "未接続",
        "en": "Not connected",
        "ko": "미연결",
    },
    "nav.add_ga4": {
        "ja": "+ GA4 接続",
        "en": "+ Connect GA4",
        "ko": "+ GA4 연결",
    },
    # Categories
    "cat.membership": {"ja": "会員・継続", "en": "Membership", "ko": "회원·구독"},
    "cat.content": {"ja": "コンテンツ", "en": "Content", "ko": "콘텐츠"},
    "cat.recruit": {"ja": "採用", "en": "Recruiting", "ko": "채용"},
    "cat.lead": {"ja": "問い合わせ・リード", "en": "Leads & inquiry", "ko": "문의·리드"},
    "cat.commerce": {"ja": "コマース", "en": "Commerce", "ko": "커머스"},
    "cat.education": {"ja": "教育・申込", "en": "Education & apply", "ko": "교육·신청"},
    "cat.booking": {"ja": "予約", "en": "Booking", "ko": "예약"},
    "cat.all": {"ja": "すべて", "en": "All", "ko": "전체"},
    # Board chrome
    "help": {"ja": "説明", "en": "Help", "ko": "설명"},
    "help_of": {
        "ja": "{title}の説明",
        "en": "Help: {title}",
        "ko": "{title} 설명",
    },
    "focus": {"ja": "重点", "en": "Focus", "ko": "중점"},
    "vs_prev": {"ja": "前期比", "en": "vs prior", "ko": "전기 대비"},
    "col.help": {"ja": "説明", "en": "Help", "ko": "설명"},
    "col.metric": {"ja": "指標", "en": "Metric", "ko": "지표"},
    "col.value": {"ja": "値", "en": "Value", "ko": "값"},
    "col.bench": {"ja": "業界目安", "en": "Industry std.", "ko": "업계 기준"},
    "col.gap": {"ja": "目安差", "en": "Gap vs std.", "ko": "기준 차이"},
    "col.event": {"ja": "イベント", "en": "Event", "ko": "이벤트"},
    "col.count": {"ja": "件数", "en": "Count", "ko": "건수"},
    "col.delta": {"ja": "前期比", "en": "vs prior", "ko": "전기 대비"},
    "bench": {"ja": "業界目安", "en": "Industry std.", "ko": "업계 기준"},
    "bench_gap": {"ja": "目安差", "en": "Gap vs std.", "ko": "기준 차이"},
    "bench_band": {"ja": "帯", "en": "range", "ko": "범위"},
    "bench_title": {
        "ja": "パック標準帯 {band}（平均目安 {avg}）",
        "en": "Pack standard range {band} (average {avg})",
        "ko": "팩 기준 범위 {band} (평균 기준 {avg})",
    },
    "bench_empty": {
        "ja": "比較可能な業界目安がない指標です（件数など）",
        "en": "No comparable industry standard (e.g. counts).",
        "ko": "비교 가능한 업계 기준이 없습니다(건수 등).",
    },
    "bench_empty_short": {
        "ja": "比較可能な業界目安なし",
        "en": "No industry standard",
        "ko": "업계 기준 없음",
    },
    "view.list": {"ja": "リスト", "en": "List", "ko": "리스트"},
    "view.card": {"ja": "カード", "en": "Cards", "ko": "카드"},
    "view.compact": {"ja": "コンパクト", "en": "Compact", "ko": "콤팩트"},
    "view.bar": {"ja": "バー", "en": "Bars", "ko": "바"},
    "view.gauge": {"ja": "ゲージ", "en": "Gauge", "ko": "게이지"},
    "view.funnel": {"ja": "ファネル", "en": "Funnel", "ko": "퍼널"},
    "view.compare": {"ja": "比較", "en": "Compare", "ko": "비교"},
    "view.trend": {"ja": "トレンド", "en": "Trend", "ko": "추이"},
    "view.stack": {"ja": "スタック", "en": "Stack", "ko": "스택"},
    "compare.current": {"ja": "今期", "en": "Current", "ko": "현재"},
    "compare.prior": {"ja": "前期", "en": "Prior", "ko": "전기"},
    "compare.bench": {"ja": "目安", "en": "Std.", "ko": "기준"},
    "view.switch": {"ja": "表示切替", "en": "View", "ko": "표시 전환"},
    "panel.audience": {"ja": "オーディエンス", "en": "Audience", "ko": "오디언스"},
    "panel.channels": {"ja": "流入チャネル", "en": "Channels", "ko": "유입 채널"},
    "panel.engage": {"ja": "エンゲージ", "en": "Engagement", "ko": "참여"},
    "panel.funnel": {"ja": "転換ファネル", "en": "Conversion funnel", "ko": "전환 퍼널"},
    # 判定チップ (vs 業界目安)
    "judge.up": {"ja": "良好", "en": "Good", "ko": "좋음"},
    "judge.mid": {"ja": "目安内", "en": "On par", "ko": "보통"},
    "judge.down": {"ja": "要注意", "en": "Watch", "ko": "주의"},
    # 業務KPI (unlinked)
    "biz.collapsed": {
        "ja": "業務データ未連携（{n}指標）",
        "en": "Business data not linked ({n} metrics)",
        "ko": "업무 데이터 미연결({n}개 지표)",
    },
    "biz.collapsed_hint": {
        "ja": "注文・売上・会員など社内DBの数字はまだ接続されていません。GA4 の数字だけで判断できる指標を上に並べています。",
        "en": "Orders, revenue and members from your own database aren't connected yet. The board above uses GA4 numbers only.",
        "ko": "주문·매출·회원 등 사내 DB 수치는 아직 연결되지 않았습니다. 위 보드는 GA4 수치만으로 판단합니다.",
    },
    "biz.show": {"ja": "対象の指標を見る", "en": "Show these metrics", "ko": "해당 지표 보기"},
    # 流入チャネル grouping
    "channels.other": {"ja": "その他（{n}チャネル）", "en": "Others ({n} channels)", "ko": "기타({n}개 채널)"},
    "channels.other_meaning": {
        "ja": "上位5チャネル以外をまとめた構成比です: {names}",
        "en": "Combined share of channels outside the top 5: {names}",
        "ko": "상위 5개 외 채널을 합친 구성비입니다: {names}",
    },
    "channels.other_formula": {
        "ja": "上記チャネルのセッション構成比の合計",
        "en": "Sum of the session share of the channels above",
        "ko": "위 채널들의 세션 구성비 합계",
    },
    "channels.other_tip": {
        "ja": "個別の数字は「詳細」表示の各チャネルではなく GA4 の集客レポートで確認できます。",
        "en": "See GA4's acquisition report for each of these channels.",
        "ko": "개별 수치는 GA4 획득 보고서에서 확인할 수 있습니다.",
    },
    # かんたん / 詳細
    "mode.simple": {"ja": "かんたん", "en": "Simple", "ko": "간단히"},
    "mode.detail": {"ja": "詳細", "en": "Detailed", "ko": "자세히"},
    "mode.aria": {"ja": "表示モード", "en": "View mode", "ko": "보기 모드"},
    "mode.show_detail": {
        "ja": "すべての指標を見る（詳細表示へ）",
        "en": "See every metric (switch to Detailed)",
        "ko": "모든 지표 보기(자세히 보기로)",
    },
    # 今見るべきこと
    "watch.title": {"ja": "今見るべきこと", "en": "What to look at now", "ko": "지금 봐야 할 것"},
    "watch.sub": {
        "ja": "業界目安から外れている指標を、外れ幅の大きい順に最大3つ",
        "en": "Up to 3 metrics furthest outside the industry standard",
        "ko": "업계 기준에서 가장 많이 벗어난 지표 최대 3개",
    },
    "watch.bad": {"ja": "{label}が目安より{dir}", "en": "{label} is {dir} than the standard", "ko": "{label}이(가) 기준보다 {dir}"},
    "watch.good": {"ja": "{label}は目安より良好", "en": "{label} is better than the standard", "ko": "{label}은(는) 기준보다 좋음"},
    "watch.dir_high": {"ja": "高い", "en": "higher", "ko": "높음"},
    "watch.dir_low": {"ja": "低い", "en": "lower", "ko": "낮음"},
    "watch.numbers": {
        "ja": "いま {value} · 目安 {avg}（{band}）· 差 {gap}",
        "en": "Now {value} · standard {avg} ({band}) · gap {gap}",
        "ko": "현재 {value} · 기준 {avg}({band}) · 차이 {gap}",
    },
    "watch.tip": {"ja": "見るポイント", "en": "Where to look", "ko": "확인할 점"},
    "watch.keep": {
        "ja": "今の打ち手を続けつつ、他の指標を下げていないか確認します。",
        "en": "Keep what works, and check it isn't pulling other metrics down.",
        "ko": "지금 방식을 유지하면서 다른 지표를 끌어내리지 않는지 확인합니다.",
    },
    "watch.none": {
        "ja": "業界目安から大きく外れている指標はありません。",
        "en": "No metric is far outside its industry standard.",
        "ko": "업계 기준에서 크게 벗어난 지표가 없습니다.",
    },
    "watch.sample": {
        "ja": "見本データでの例です。GA4 を接続すると自分のサイトで判定します。",
        "en": "Example using sample data. Connect GA4 to judge your own site.",
        "ko": "샘플 데이터 예시입니다. GA4를 연결하면 내 사이트로 판정합니다.",
    },
    "panel.events": {"ja": "イベント", "en": "Events", "ko": "이벤트"},
    "events.missing": {"ja": "未計測（0件）:", "en": "Not tracked (0):", "ko": "미측정(0건):"},
    "events.missing_hint": {
        "ja": "業界パックの想定イベントのうち、この期間に1件も記録されていないもの。サイトに機能がないか、GA4 にイベントが未設定です。",
        "en": "Pack events with no hits in this period — the site lacks the feature, or the GA4 event isn't set up.",
        "ko": "업종 팩이 상정한 이벤트 중 이 기간에 한 건도 기록되지 않은 것. 사이트에 기능이 없거나 GA4 이벤트가 설정되지 않았습니다.",
    },
    "events.empty": {
        "ja": "この期間に記録されたイベントはありません。",
        "en": "No events were recorded in this period.",
        "ko": "이 기간에 기록된 이벤트가 없습니다.",
    },
    "panel.biz": {"ja": "業務KPI", "en": "Business KPIs", "ko": "업무 KPI"},
    "panel.channels_sub": {
        "ja": "セッション構成",
        "en": "Session mix",
        "ko": "세션 구성",
    },
    "panel.biz_sub": {
        "ja": "未連携 · 業務DB",
        "en": "Unlinked · business DB",
        "ko": "미연동 · 업무 DB",
    },
    "biz.linked": {"ja": "連携済", "en": "Linked", "ko": "연동됨"},
    "biz.unlinked": {"ja": "業務DB", "en": "Biz DB", "ko": "업무 DB"},
    "period.28d": {"ja": "直近28日", "en": "Last 28 days", "ko": "최근 28일"},
    "period.7d": {"ja": "直近7日", "en": "Last 7 days", "ko": "최근 7일"},
    "period.label": {"ja": "期間", "en": "Period", "ko": "기간"},
    "sample_meta": {
        "ja": "業界パック見本",
        "en": "Industry pack sample",
        "ko": "업계 팩 샘플",
    },
    "close": {"ja": "閉じる", "en": "Close", "ko": "닫기"},
    "meaning": {"ja": "意味", "en": "Meaning", "ko": "의미"},
    "formula": {"ja": "計算式", "en": "Formula", "ko": "계산식"},
    "tip": {"ja": "見るポイント", "en": "What to watch", "ko": "볼 포인트"},
    # Settings
    "settings.title": {
        "ja": "設定",
        "en": "Settings",
        "ko": "설정",
    },
    "settings.lead": {
        "ja": "表示言語を選ぶと、メニュー・表ヘッダ・説明ボタン・指標名・説明文が切り替わります。",
        "en": "Choose a display language for menus, headers, help, metric names, and help copy.",
        "ko": "표시 언어를 고르면 메뉴·표 헤더·설명 버튼·지표명·설명 문구가 바뀝니다.",
    },
    "settings.language": {
        "ja": "表示言語",
        "en": "Display language",
        "ko": "표시 언어",
    },
    "settings.language_help": {
        "ja": "イベントID（例: apply_complete）とチャネル名（Organic Search など）はそのまま表示します。",
        "en": "Event IDs (e.g. apply_complete) and channel names (e.g. Organic Search) stay as-is.",
        "ko": "이벤트 ID(예: apply_complete)와 채널명(Organic Search 등)은 그대로 둡니다.",
    },
    "settings.save": {
        "ja": "保存する",
        "en": "Save",
        "ko": "저장",
    },
    "settings.saved": {
        "ja": "保存しました。",
        "en": "Saved.",
        "ko": "저장했습니다.",
    },
    "settings.back": {
        "ja": "ボードに戻る",
        "en": "Back to board",
        "ko": "보드로 돌아가기",
    },
    "primary_tag": {"ja": "主転換", "en": "Primary", "ko": "주전환"},
    "more_n": {
        "ja": "ほか {n} 件を見る",
        "en": "Show {n} more",
        "ko": "외 {n}건 더 보기",
    },
    "count_more": {
        "ja": "{shown}件 · ほか{more}件",
        "en": "{shown} · +{more} more",
        "ko": "{shown}건 · 외 {more}건",
    },
    "count_n": {"ja": "{n}件", "en": "{n}", "ko": "{n}건"},
    "next_watch": {
        "ja": "次に見るポイント",
        "en": "What to watch next",
        "ko": "다음에 볼 포인트",
    },
    "summary_aria": {"ja": "要約KPI", "en": "Summary KPIs", "ko": "요약 KPI"},
    "sample_title_suffix": {"ja": "（見本）", "en": " (sample)", "ko": " (샘플)"},
    "kind.digital": {"ja": "デジタル", "en": "Digital", "ko": "디지털"},
    "kind.event": {"ja": "イベント", "en": "Event", "ko": "이벤트"},
    "kind.traffic": {"ja": "流入", "en": "Traffic", "ko": "유입"},
    "kind.business": {"ja": "業務", "en": "Business", "ko": "업무"},
    # Series honesty (sample trend/bar)
    "series.sample_note": {
        "ja": "見本系列 · サンプル用の推定カーブです（実測の日次ではありません）",
        "en": "Sample series · illustrative curve for the pack demo (not measured daily data)",
        "ko": "샘플 시계열 · 팩 데모용 추정 곡선입니다(실측 일별 아님)",
    },
    "nav.pack_search": {
        "ja": "パックを検索",
        "en": "Search packs",
        "ko": "팩 검색",
    },
    "nav.pack_search_ph": {
        "ja": "名前・ヒントで絞り込み",
        "en": "Filter by name or hint",
        "ko": "이름·힌트로 필터",
    },
    "nav.pack_search_empty": {
        "ja": "該当するパックがありません",
        "en": "No matching packs",
        "ko": "맞는 팩이 없습니다",
    },
    # Connect page chrome
    "connect.title": {"ja": "GA4 接続", "en": "Connect GA4", "ko": "GA4 연결"},
    "connect.lead": {
        "ja": "Google でログインして、使うデータ（Property）を1つ選ぶだけです。",
        "en": "Sign in with Google and pick one Property to analyze.",
        "ko": "Google로 로그인한 뒤 분석할 Property를 하나 고르면 됩니다.",
    },
    "connect.hero.title": {"ja": "GA4 を接続", "en": "Connect GA4", "ko": "GA4 연결"},
    "connect.hero.meta": {
        "ja": "Google アカウントでログインし、分析したい Property を1つ選びます。パスワードはこちらに保存しません（Google の画面で許可するだけです）。",
        "en": "Sign in with Google and choose one Property. We never store your password—you only approve access on Google’s screen.",
        "ko": "Google 계정으로 로그인해 분석할 Property를 하나 고릅니다. 비밀번호는 저장하지 않으며 Google 화면에서 허용만 하면 됩니다.",
    },
    "connect.btn.google": {
        "ja": "Google で接続",
        "en": "Connect with Google",
        "ko": "Google로 연결",
    },
    "connect.btn.demo": {
        "ja": "デモデータで試す",
        "en": "Try with demo data",
        "ko": "데모 데이터로 시도",
    },
    "connect.hint.demo_oauth": {
        "ja": "Google 接続はまだ設定されていないため、いまはデモ接続で始まります。",
        "en": "Google sign-in isn't set up yet, so this starts a demo connection for now.",
        "ko": "Google 연결이 아직 설정되지 않아, 지금은 데모 연결로 시작합니다.",
    },
    "connect.badge.on": {"ja": "接続中", "en": "Connected", "ko": "연결됨"},
    "connect.badge.demo": {"ja": "デモ", "en": "Demo", "ko": "데모"},
    "connect.badge.google_ok": {
        "ja": "Google 連携済み",
        "en": "Google linked",
        "ko": "Google 연동됨",
    },
    "connect.pick_property": {
        "ja": "使う Property を1つ選んでください",
        "en": "Choose one Property to use",
        "ko": "사용할 Property를 하나 고르세요",
    },
    "connect.pick_property_meta": {
        "ja": "読み取り専用です。あとから切り替えることもできます。",
        "en": "Read-only. You can switch later.",
        "ko": "읽기 전용입니다. 나중에 바꿀 수 있습니다.",
    },
    "connect.property_list": {
        "ja": "Property を選択（{n}）",
        "en": "Select a Property ({n})",
        "ko": "Property 선택（{n}）",
    },
    "connect.use_property": {
        "ja": "この Property を使う",
        "en": "Use this Property",
        "ko": "이 Property 사용",
    },
    "connect.no_property": {
        "ja": "Property が見つかりません",
        "en": "No Property found",
        "ko": "Property를 찾을 수 없음",
    },
    "connect.no_property_meta": {
        "ja": "この Google アカウントに閲覧できる GA4 Property がありません。権限を確認してください。",
        "en": "This Google account has no GA4 Property you can view. Check permissions.",
        "ko": "이 Google 계정에서 볼 수 있는 GA4 Property가 없습니다. 권한을 확인하세요.",
    },
    "connect.disconnect": {"ja": "切断する", "en": "Disconnect", "ko": "연결 해제"},
    "connect.live_board": {
        "ja": "ライブボードを見る",
        "en": "Open live board",
        "ko": "라이브 보드 보기",
    },
    "connect.open_builder": {
        "ja": "ダッシュボードを作る",
        "en": "Build a dashboard",
        "ko": "대시보드 만들기",
    },
    "connect.open_samples": {
        "ja": "サンプルパックを見る",
        "en": "Browse sample packs",
        "ko": "샘플 팩 보기",
    },
    "connect.pack.title": {
        "ja": "業界パック（業界目安）",
        "en": "Industry pack (benchmarks)",
        "ko": "업계 팩（업계 기준）",
    },
    "connect.pack.selected": {
        "ja": "選択中の業界目安: ",
        "en": "Selected benchmark pack: ",
        "ko": "선택된 업계 기준: ",
    },
    "connect.pack.pick": {
        "ja": "ライブボードの業界目安・目安差に使うパックを選んでください（DEMO売上は使いません）。",
        "en": "Pick a pack for live-board 業界目安 / gaps (sample DEMO revenue is not used).",
        "ko": "라이브 보드의 업계 기준·차이에 쓸 팩을 고르세요(DEMO 매출은 쓰지 않습니다).",
    },
    "connect.pack.submit": {
        "ja": "この業界目安を使う",
        "en": "Use this benchmark pack",
        "ko": "이 업계 기준 사용",
    },
    "connect.preview": {
        "ja": "接続プレビュー",
        "en": "Connection preview",
        "ko": "연결 미리보기",
    },
    "connect.dev.summary": {
        "ja": "管理者向け: Google 接続のセットアップ",
        "en": "For admins: set up Google sign-in",
        "ko": "관리자용: Google 연결 설정",
    },
    "connect.dev.ok": {
        "ja": "OAuth クライアント設定済み · API パッケージ OK",
        "en": "OAuth client configured · API packages OK",
        "ko": "OAuth 클라이언트 설정됨 · API 패키지 OK",
    },
    "connect.dev.unset": {
        "ja": "未設定: Google 接続ボタンはデモへフォールバックします。",
        "en": "Not configured: the Google button falls back to demo.",
        "ko": "미설정: Google 연결 버튼은 데모로 대체됩니다.",
    },
    "connect.dev.pkgs": {
        "ja": "パッケージ不足: pip install -r requirements.txt",
        "en": "Missing packages: pip install -r requirements.txt",
        "ko": "패키지 부족: pip install -r requirements.txt",
    },
    "connect.err.oauth_state": {
        "ja": "Google 接続を確認できませんでした（期限切れ、または別のブラウザ・別のアドレスから開始された可能性があります）。もう一度「Google で接続」からやり直してください。",
        "en": "Couldn't verify the Google sign-in (it expired, or was started from a different browser or address). Please start again from “Connect with Google”.",
        "ko": "Google 연결을 확인하지 못했습니다(만료되었거나 다른 브라우저·주소에서 시작되었을 수 있습니다). 「Google로 연결」부터 다시 시도해 주세요.",
    },
    "connect.err.oauth_denied": {
        "ja": "Google 側で接続がキャンセルされました。必要なら、もう一度「Google で接続」から許可してください。",
        "en": "The Google connection was cancelled. Start again from “Connect with Google” if you want to allow access.",
        "ko": "Google에서 연결이 취소되었습니다. 필요하면 「Google로 연결」에서 다시 허용해 주세요.",
    },
    "connect.err.token": {
        "ja": "トークン取得に失敗しました: {exc}",
        "en": "Failed to obtain a token: {exc}",
        "ko": "토큰을 가져오지 못했습니다: {exc}",
    },
    "connect.err.list_props": {
        "ja": "Property 一覧の取得に失敗しました: {exc}",
        "en": "Failed to list Properties: {exc}",
        "ko": "Property 목록을 가져오지 못했습니다: {exc}",
    },
    "connect.err.preview": {
        "ja": "プレビュー取得に失敗しました: {exc}",
        "en": "Failed to load preview: {exc}",
        "ko": "미리보기를 가져오지 못했습니다: {exc}",
    },
    "live.note.ok": {
        "ja": "GA4 ライブ · 業界目安: {pack}",
        "en": "GA4 live · benchmarks: {pack}",
        "ko": "GA4 라이브 · 업계 기준: {pack}",
    },
    "live.note.demo": {
        "ja": "GA4 接続（デモ数値フォールバック）· 業界目安: {pack}",
        "en": "GA4 connected (demo numbers fallback) · benchmarks: {pack}",
        "ko": "GA4 연결(데모 수치 폴백) · 업계 기준: {pack}",
    },
    "live.note.demo_mode": {
        "ja": "デモ接続 · 見本数値（実データではありません）· 業界目安: {pack}",
        "en": "Demo connection · sample numbers (not real data) · benchmarks: {pack}",
        "ko": "데모 연결 · 샘플 수치(실데이터 아님) · 업계 기준: {pack}",
    },
    "live.note.err": {
        "ja": "GA4 取得失敗 · サンプル数値 · 業界目安: {pack}",
        "en": "GA4 fetch failed · sample numbers · benchmarks: {pack}",
        "ko": "GA4 조회 실패 · 샘플 수치 · 업계 기준: {pack}",
    },
    # Builder chrome
    "builder.title": {
        "ja": "カスタムビルダー",
        "en": "Custom builder",
        "ko": "커스텀 빌더",
    },
    "builder.nav.connect": {"ja": "GA4接続", "en": "Connect GA4", "ko": "GA4 연결"},
    "builder.status.unsaved": {"ja": "未保存", "en": "Unsaved", "ko": "미저장"},
    "builder.btn.clear": {"ja": "クリア", "en": "Clear", "ko": "지우기"},
    "builder.btn.save": {"ja": "保存", "en": "Save", "ko": "저장"},
    "builder.palette": {"ja": "項目パレット", "en": "Widget palette", "ko": "항목 팔레트"},
    "builder.palette_sub": {
        "ja": "GA4接続時は指標・イベントがPropertyから入ります。検索で絞り込み。",
        "en": "When GA4 is connected, metrics and events come from the Property. Search to filter.",
        "ko": "GA4 연결 시 지표·이벤트가 Property에서 들어옵니다. 검색으로 필터하세요.",
    },
    "builder.search_ph": {
        "ja": "検索（例: sessions, purchase, エンゲージ）",
        "en": "Search (e.g. sessions, purchase)",
        "ko": "검색(예: sessions, purchase)",
    },
    "builder.search_empty": {
        "ja": "該当する項目がありません",
        "en": "No matching items",
        "ko": "맞는 항목이 없습니다",
    },
    "builder.filter_valued": {
        "ja": "値ありだけ",
        "en": "With values only",
        "ko": "값 있는 것만",
    },
    "builder.expand_all": {"ja": "すべて開く", "en": "Expand all", "ko": "모두 열기"},
    "builder.collapse_all": {
        "ja": "すべて閉じる",
        "en": "Collapse all",
        "ko": "모두 닫기",
    },
    "builder.canvas": {
        "ja": "マイダッシュボード",
        "en": "My dashboard",
        "ko": "내 대시보드",
    },
    "builder.canvas_help": {
        "ja": "見出し名・色はカード上で直接変更。ブラウザに保存されます。",
        "en": "Edit titles and colors on the cards. Saved in this browser.",
        "ko": "카드에서 제목·색을 바로 바꿉니다. 이 브라우저에 저장됩니다.",
    },
    "builder.live_on": {
        "ja": "GA4 接続中: {name} · 指標 {n_digital} / イベント {n_event} · 業務KPIは未連携",
        "en": "GA4 connected: {name} · metrics {n_digital} / events {n_event} · business KPIs unlinked",
        "ko": "GA4 연결됨: {name} · 지표 {n_digital} / 이벤트 {n_event} · 업무 KPI 미연동",
    },
    "builder.live_err": {
        "ja": "GA4取得エラー: {err}",
        "en": "GA4 error: {err}",
        "ko": "GA4 오류: {err}",
    },
    "builder.live_hint": {
        "ja": "GA4接続すると、パレットに Property の指標・イベントがすべて入ります。",
        "en": "Connect GA4 to fill the palette with the Property’s metrics and events.",
        "ko": "GA4를 연결하면 Property의 지표·이벤트가 팔레트에 모두 들어옵니다.",
    },
    "builder.biz_hint": {
        "ja": "未連携 · 業務DB（サンプル）",
        "en": "Unlinked · business DB (sample)",
        "ko": "미연동 · 업무 DB(샘플)",
    },
}
