"""更新情報 (/updates) copy: docs/plan s12 · screens/12-updates.dc.html.

One entry per release, newest first. The version matches the GitHub release (docs/releases/vX.Y.Z.md);
the text here is for people using SiteKPI, the GitHub notes are for developers.
"""

from __future__ import annotations

from typing import Any

RELEASES_URL = "https://github.com/starful/sitekpi/releases"

# (anchor, date, version, link to try it or "")
_ENTRIES = [
    ("v0-8-1", "2026-11-22", "v0.8.1", "/ec"),
    ("v0-8-0", "2026-11-22", "v0.8.0", "/ec"),
    ("v0-7-6", "2026-11-21", "v0.7.6", "/ec"),
    ("v0-7-5", "2026-11-20", "v0.7.5", "/glossary"),
    ("v0-7-4", "2026-11-20", "v0.7.4", "/glossary"),
    ("v0-7-3", "2026-11-20", "v0.7.3", "/ec"),
    ("v0-7-2", "2026-11-19", "v0.7.2", ""),
    ("v0-7-1", "2026-11-19", "v0.7.1", ""),
    ("v0-7-0", "2026-11-18", "v0.7.0", ""),
]

_TEXT: dict[str, dict[str, Any]] = {
    "ja": {
        "title": "更新情報", "lead": "SiteKPI に加わった機能と、直したところ。新しい順です。",
        "meta_desc": "SiteKPI の更新情報。新しくできること・使いやすくなったこと・直した不具合を、新しい順にまとめています。",
        "toc_k": "このページの中", "new": "NEW", "try": "見本ボードで見る →", "try_glossary": "指標辞典を開く →",
        "kinds": {"new": "新機能", "better": "改善", "fix": "修正"},
        "legend": "新しくできること · 使いやすくなったこと · 直した不具合",
        "dev": "開発者向けのくわしい記録（変更したコードの一覧）は {link} にあります。",
        "entries": [
            ("印刷・PDF が 1 ページ 1 カテゴリに", [
                ("better", "「印刷・PDF」で、ボードの各章と詳しい数字の各カテゴリが、それぞれ新しいページから始まります。途中で切れません。1 ページに入らない章は小見出しの区切りで分け、それでも入らないものはそのページに収まるよう縮小します。"),
            ]),
            ("サイト一覧と、印刷・PDF", [
                ("new", "「サイト一覧」: この Google アカウントで見られる GA4 プロパティを並べ、それぞれの総評と 3 つの数字を同じ物差しで表示。代理店・コンサルの方向けです。"),
                ("new", "ボードの上のバーに「印刷・PDF」。印刷画面で「PDF に保存」を選ぶと、メニューやボタンを除いた報告用の PDF になります。"),
                ("better", "「今見るべきこと」の見るポイントを、訪問者の行動（買う · 問い合わせ · 予約 · 登録 · 読む …）ごとの言葉に。"),
                ("better", "業界目安の「出典」の横に、数字を出典ページと照らし合わせた日（確認日）を表示。"),
                ("better", "スクロール · フォーム · 動画などの段が「未計測」のとき、GA4 の拡張計測機能でオンにする場所を案内。"),
                ("better", "期間を切り替えたときの「詳しい数字」が速くなりました。"),
                ("better", "エンゲージ率・すぐ離脱に近い率の業界目安を外しました。出典の利用条件が確認できるまで「基準なし」と表示します。"),
            ]),
            ("AI への質問文をすぐ開けるように", [
                ("better", "ボードの上のバーに「✦ AI に聞く」。押すと、この画面の数字を入れた質問文がポップアップで開きます（スマホは下から）。"),
                ("better", "「どうする？」の AI のカードを目立つ色に。「開いて見る」でも同じポップアップが開きます。"),
                ("fix", "URL に ?lang=en などを付けても、見本ボードや指標辞典が日本語のままだったのを直しました。"),
            ]),
            ("指標辞典で新しい言葉がすぐわかるように", [
                ("better", "追加してから 30 日の言葉に「NEW」。いちばん上に「最近追加した言葉」と「NEW だけ見る」ボタン。"),
            ]),
            ("指標辞典に 20 語を追加", [
                ("new", "表示の速さ（LCP · INP · CLS）、サイト内検索（利用率 · 結果ゼロ率）、購入手続き離脱率、再訪までの日数。"),
                ("new", "Google 検索（表示回数 · クリック率 · 平均掲載順位）、メール（開封率 · クリック率 · 配信停止率）、CPL、ビュースルーコンバージョン。"),
                ("new", "粗利率 · CSAT · 価値を感じるまでの時間 · コホート · A/Bテスト。"),
            ]),
            ("「どのページを直す？」がわかるように", [
                ("new", "「誰が成果を出している？」に、入口ページ別の表。最初に開いたページごとに、来た人と購入まで進んだ割合がわかります。"),
                ("new", "「どこがおかしい？」に「どのページで？」。いちばん離れている段を入口ページ別に並べ、いちばん低いページを枠で囲みます。"),
                ("new", "詳しい数字に「ページ別」。表示回数の多い順で、見出しを押すと並べ替え。ページ名を押すと、そのページが開きます。"),
            ]),
            ("最初は短く、説明は押して読む", [
                ("better", "グラフと数字は開いたまま、説明の文章だけ「説明を読む ▾」にしまいました。"),
                ("better", "「どうする？」の「確かめ方」を、ボタンひとつでまとめて表示。"),
                ("fix", "「いつから？」のグラフで、やった日の印と業界目安の文字が重ならないように。"),
            ]),
            ("まとめと、やった日の記録", [
                ("new", "詳しい数字の前に「まとめ」。結論ひとつと 4 行で、そのままコピーできます。"),
                ("better", "「効いた？」を「どうする？」の中へ。対策の横の「やった日を記録」から始められます。"),
                ("better", "AI に聞くための質問文を、見えるところに置きました。"),
                ("fix", "地図の文字の重なり · 棒グラフの文字切れ · 戻ったときに一番上に戻ってしまう、を直しました。"),
            ]),
            ("ボードが「物語」になりました", [
                ("new", "7 つの章で上から読めます: 総評 · なぜ変わった？ · 誰が成果を出している？ · どこで離れている？ · どこがおかしい？ · どうする？ · まとめ。"),
                ("new", "対策を「やった日」を記録すると、14 日たったところでその前後を比べます。"),
                ("new", "日本語 · 英語 · 韓国語。"),
            ]),
        ],
    },
    "en": {
        "title": "What's new", "lead": "New features and fixes in SiteKPI, newest first.",
        "meta_desc": "What's new in SiteKPI: new features, improvements and fixes, newest first.",
        "toc_k": "On this page", "new": "NEW", "try": "See it on a sample board →", "try_glossary": "Open the metric glossary →",
        "kinds": {"new": "New", "better": "Better", "fix": "Fixed"},
        "legend": "Something new you can do · easier to use · a bug fixed",
        "dev": "The detailed record for developers (every code change) is on {link}.",
        "entries": [
            ("Print / PDF: one category per page", [
                ("better", "“Print / PDF” now starts each board chapter and each detailed-numbers category on a new page, and never cuts one in half. A chapter longer than a page breaks between its sub-questions; anything still too long is scaled to fit its page."),
            ]),
            ("All sites, and Print / PDF", [
                ("new", "“All sites”: every GA4 property this Google account can read, each with its summary and three numbers on the same yardstick. Made for agencies and consultants."),
                ("new", "“Print / PDF” in the board's top bar. Choose “Save as PDF” in the print dialog for a clean report without menus and buttons."),
                ("better", "“What to look at now” tips now speak to your visitor behavior (buy · contact · book · sign up · read …)."),
                ("better", "Next to an industry target's “Source”, the date its figures were last checked against the source page."),
                ("better", "When a scroll, form or video step shows “Not tracked”, the board points to the GA4 enhanced-measurement switch."),
                ("better", "“Detailed numbers” load faster when you switch the period."),
                ("better", "Industry targets for engagement and bounce-like rate are removed until we can confirm the source's terms; they show “No benchmark”."),
            ]),
            ("Open the AI question in one click", [
                ("better", "“✦ Ask AI” in the board's top bar opens the question with this screen's numbers in a popup (a sheet from the bottom on phones)."),
                ("better", "The AI card in “What to do?” now stands out, and “Open” shows the same popup."),
                ("fix", "Sample boards and the glossary now follow ?lang=en / ?lang=ko in the URL (they stayed in Japanese)."),
            ]),
            ("Spot the new words in the glossary", [
                ("better", "Words added in the last 30 days carry “NEW”, with a “recently added” line and a “Show NEW only” button at the top."),
            ]),
            ("20 more words in the metric glossary", [
                ("new", "Page speed (LCP · INP · CLS), site search (usage · zero results), checkout abandonment and days to return."),
                ("new", "Google search (impressions · click rate · average position), email (open · click · unsubscribe rates), CPL and view-through conversions."),
                ("new", "Gross margin · CSAT · time to value · cohorts · A/B tests."),
            ]),
            ("See which page to fix", [
                ("new", "“Who converts?” now has a table by landing page: for each first page of a visit, how many came and how many went on to buy."),
                ("new", "“What is off?” now asks “On which page?”: the step people leave most, split by landing page, with the lowest page outlined."),
                ("new", "“All the numbers” now has “By page”: most viewed first, sort by any heading, and click a page name to open the page."),
            ]),
            ("Short first, explanations on click", [
                ("better", "Charts and numbers stay open; only the explaining text folds under “Read the explanation ▾”."),
                ("better", "One button shows every “how to check” line in “What to do?”."),
                ("fix", "On the “Since when?” chart, the date you recorded no longer sits on the industry label."),
            ]),
            ("Summary, and the day you made a change", [
                ("new", "A “Summary” before “All the numbers”: one conclusion and four lines, ready to copy."),
                ("better", "“Did it work?” moved inside “What to do?” — start from “Record the day you did it” next to each action."),
                ("better", "The question to ask your AI is now in plain view."),
                ("fix", "Fixed overlapping labels on the map, cut-off text in bars, and the page jumping to the top when you came back."),
            ]),
            ("The board now tells a story", [
                ("new", "Seven chapters, top to bottom: Overview · Why did it change? · Who converts? · Where do people leave? · What is off? · What to do? · Summary."),
                ("new", "Record the day you made a change; after 14 days the board compares before and after."),
                ("new", "Japanese · English · Korean."),
            ]),
        ],
    },
    "ko": {
        "title": "업데이트 소식", "lead": "SiteKPI에 새로 생긴 기능과 고친 점. 최신순이에요.",
        "meta_desc": "SiteKPI 업데이트 소식: 새 기능, 개선, 고친 문제를 최신순으로 정리했어요.",
        "toc_k": "이 페이지 안", "new": "NEW", "try": "견본 보드에서 보기 →", "try_glossary": "지표 사전 열기 →",
        "kinds": {"new": "새 기능", "better": "개선", "fix": "수정"},
        "legend": "새로 할 수 있는 것 · 쓰기 편해진 것 · 고친 문제",
        "dev": "개발자용 자세한 기록(바뀐 코드 목록)은 {link}에 있어요.",
        "entries": [
            ("인쇄·PDF가 한 페이지에 한 카테고리로", [
                ("better", "「인쇄·PDF」에서 보드의 각 장과 자세한 숫자의 각 카테고리가 새 페이지에서 시작해요. 중간에서 잘리지 않아요. 한 페이지에 안 들어가는 장은 소제목 단위로 나누고, 그래도 넘치면 그 페이지에 맞게 줄여요."),
            ]),
            ("사이트 목록과 인쇄·PDF", [
                ("new", "「사이트 목록」: 이 Google 계정으로 볼 수 있는 GA4 속성을 나란히, 각각의 총평과 숫자 3개를 같은 잣대로 보여 줘요. 대행사·컨설턴트용이에요."),
                ("new", "보드 위쪽 바에 「인쇄·PDF」. 인쇄 화면에서 「PDF로 저장」을 고르면 메뉴·버튼을 뺀 보고용 PDF가 돼요."),
                ("better", "「지금 볼 것」의 확인할 점을 방문자 행동(구매 · 문의 · 예약 · 가입 · 읽기 …)에 맞는 말로 바꿨어요."),
                ("better", "업계 기준 「출처」 옆에, 숫자를 출처 페이지와 대조한 날(확인일)을 표시해요."),
                ("better", "스크롤·폼·동영상 단계가 「미계측」일 때, GA4 향상된 측정에서 켜는 곳을 안내해요."),
                ("better", "기간을 바꿀 때 「자세한 숫자」가 빨라졌어요."),
                ("better", "참여율·이탈에 가까운 율의 업계 기준을 뺐어요. 출처의 이용 조건을 확인할 때까지 「기준 없음」으로 보여요."),
            ]),
            ("AI 질문문을 바로 열 수 있게", [
                ("better", "보드 위쪽 바에 「✦ AI에게 묻기」. 누르면 이 화면의 숫자를 넣은 질문문이 팝업으로 열려요(스마트폰은 아래에서)."),
                ("better", "「어떻게 할까?」의 AI 카드를 눈에 띄는 색으로. 「열어 보기」로도 같은 팝업이 열려요."),
                ("fix", "URL에 ?lang=en 등을 붙여도 견본 보드와 지표 사전이 일본어로 나오던 문제를 고쳤어요."),
            ]),
            ("지표 사전에서 새 말을 바로 알 수 있게", [
                ("better", "추가한 지 30일 안 된 말에 「NEW」. 맨 위에 「최근 추가한 말」과 「NEW만 보기」 버튼."),
            ]),
            ("지표 사전에 20개 추가", [
                ("new", "표시 속도(LCP · INP · CLS), 사이트 내 검색(이용률 · 결과 0건 비율), 구매 절차 이탈률, 재방문까지의 일수."),
                ("new", "Google 검색(노출 수 · 클릭률 · 평균 게재 순위), 메일(오픈율 · 클릭률 · 수신 거부율), CPL, 뷰스루 전환."),
                ("new", "매출 총이익률 · CSAT · 가치를 느끼기까지의 시간 · 코호트 · A/B 테스트."),
            ]),
            ("「어느 페이지를 고칠까?」를 알 수 있게", [
                ("new", "「누가 성과를 내나?」에 입구 페이지별 표. 처음 연 페이지마다 방문자와 구매까지 간 비율을 알 수 있어요."),
                ("new", "「어디가 이상한가?」에 「어느 페이지에서?」. 가장 많이 빠지는 단계를 입구 페이지별로 나누고, 가장 낮은 페이지에 테두리를 쳐요."),
                ("new", "「자세한 수치」에 「페이지별」. 조회수 많은 순이고, 제목을 누르면 정렬, 페이지 이름을 누르면 그 페이지가 열려요."),
            ]),
            ("처음엔 짧게, 설명은 눌러서", [
                ("better", "그래프와 숫자는 열어 두고, 설명 문장만 「설명 읽기 ▾」 안에 넣었어요."),
                ("better", "「어떻게 할까?」의 「확인 방법」을 버튼 하나로 한꺼번에 보여 줘요."),
                ("fix", "「언제부터?」 그래프에서 기록한 날 표시와 업계 기준 글자가 겹치지 않게."),
            ]),
            ("정리, 그리고 한 날 기록", [
                ("new", "「자세한 수치」 앞에 「정리」. 결론 하나와 4줄, 그대로 복사할 수 있어요."),
                ("better", "「효과가 있었나?」를 「어떻게 할까?」 안으로. 대책 옆 「한 날 기록」에서 시작해요."),
                ("better", "AI에게 물어볼 질문문을 보이는 곳에 두었어요."),
                ("fix", "지도 글자 겹침 · 막대그래프 글자 잘림 · 돌아왔을 때 맨 위로 가 버리는 문제를 고쳤어요."),
            ]),
            ("보드가 「이야기」가 되었어요", [
                ("new", "7장으로 위에서부터 읽어요: 총평 · 왜 바뀌었나? · 누가 성과를 내나? · 어디서 이탈하는가? · 어디가 이상한가? · 어떻게 할까? · 정리."),
                ("new", "대책을 「한 날」로 기록하면, 14일이 지난 뒤 그 전후를 비교해요."),
                ("new", "일본어 · 영어 · 한국어."),
            ]),
        ],
    },
}


def updates(loc: str) -> dict[str, Any]:
    t = _TEXT.get(loc) or _TEXT["ja"]
    entries = []
    for n, ((anchor, date, ver, link), (title, items)) in enumerate(zip(_ENTRIES, t["entries"])):
        entries.append({"id": anchor, "date": date, "ver": ver, "title": title, "new": n == 0,
                        "link": link, "items": [{"k": k, "label": t["kinds"][k], "t": x} for k, x in items]})
    return {**{k: v for k, v in t.items() if k != "entries"}, "entries": entries, "releases_url": RELEASES_URL}
