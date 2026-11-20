"""更新情報 (/updates) copy: docs/plan s12 · screens/12-updates.dc.html.

One entry per release, newest first. The version matches the GitHub release (docs/releases/vX.Y.Z.md);
the text here is for people using SiteKPI, the GitHub notes are for developers.
"""

from __future__ import annotations

from typing import Any

RELEASES_URL = "https://github.com/starful/sitekpi/releases"

# (anchor, date, version, link to try it or "")
_ENTRIES = [
    ("v0-7-3", "2026-11-20", "v0.7.3", "/ec"),
    ("v0-7-2", "2026-11-19", "v0.7.2", ""),
    ("v0-7-1", "2026-11-19", "v0.7.1", ""),
    ("v0-7-0", "2026-11-18", "v0.7.0", ""),
]

_TEXT: dict[str, dict[str, Any]] = {
    "ja": {
        "title": "更新情報", "lead": "SiteKPI に加わった機能と、直したところ。新しい順です。",
        "meta_desc": "SiteKPI の更新情報。新しくできること・使いやすくなったこと・直した不具合を、新しい順にまとめています。",
        "toc_k": "このページの中", "new": "NEW", "try": "見本ボードで見る →",
        "kinds": {"new": "新機能", "better": "改善", "fix": "修正"},
        "legend": "新しくできること · 使いやすくなったこと · 直した不具合",
        "dev": "開発者向けのくわしい記録（変更したコードの一覧）は {link} にあります。",
        "entries": [
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
        "toc_k": "On this page", "new": "NEW", "try": "See it on a sample board →",
        "kinds": {"new": "New", "better": "Better", "fix": "Fixed"},
        "legend": "Something new you can do · easier to use · a bug fixed",
        "dev": "The detailed record for developers (every code change) is on {link}.",
        "entries": [
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
        "toc_k": "이 페이지 안", "new": "NEW", "try": "견본 보드에서 보기 →",
        "kinds": {"new": "새 기능", "better": "개선", "fix": "수정"},
        "legend": "새로 할 수 있는 것 · 쓰기 편해진 것 · 고친 문제",
        "dev": "개발자용 자세한 기록(바뀐 코드 목록)은 {link}에 있어요.",
        "entries": [
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
