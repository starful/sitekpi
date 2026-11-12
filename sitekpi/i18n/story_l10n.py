"""The board's story (docs/plan s03 「ストーリー」): 0 総評 → 1 どこで？ → 2 どこがおかしい？ → 3 どうする？

ACTIONS is the 対策カタログ: for each kind of step (the issue's last step decides the kind), a headline for ①
and three actions — what to try, the usual reason, and how to check it in GA4. They are common causes,
not a diagnosis: the board always says so. Used by views/story.py; the AI prompt is built from the same text.
"""

from __future__ import annotations

# --- step kinds -------------------------------------------------------------------------------------

KINDS = ("engage", "browse", "cart", "checkout", "form_start", "form_submit", "signup", "click", "download",
         "video", "overall")


def kind_of_event(event: str) -> str:
    """Which catalog entry a flow step belongs to, from its event name (works for custom keys too)."""
    e = (event or "").lower()
    if "engagement" in e:
        return "engage"
    if "video" in e:
        return "video"
    if "cart" in e:
        return "cart"
    if "checkout" in e or "purchase" in e or e.startswith("pay") or "_pay" in e:
        return "checkout"
    if "download" in e:
        return "download"
    if ("form" in e or "apply" in e or "booking" in e or "reserve" in e or "quote" in e) and "start" in e:
        return "form_start"
    if "submit" in e or "complete" in e or "lead" in e or "contact" in e:
        return "form_submit"
    if "sign_up" in e or "signup" in e or "login" in e or "trial" in e or "register" in e:
        return "signup"
    if "click" in e or "tel" in e or "line" in e:
        return "click"
    return "browse"


# --- fixed copy -------------------------------------------------------------------------------------

STORY: dict[str, dict[str, str]] = {
    "ja": {
        "q0": "総評", "q1": "大丈夫？", "q2": "どこで離れている？", "q3": "どこがおかしい？", "q4": "どうする？",
        "ref": "参考", "ref_k": "ぜんぶの数字",
        "strip": "このボードの読み方",
        "a1_ok": "大きな問題なし", "a1_issue": "伸びしろは「{a} → {b}」",
        "a3_n": "目安から外れた {n} つ", "a3_none": "目安から大きく外れた指標なし",
        "a4_gain": "{n} つの手 · {gain}", "a4": "{n} つの手",
        "but": "ただ、",
        # Top 総評 (boss-repeatable). Stretch + rate + how many are off — not four mini Q&A answers.
        "lede_core": "いちばんの課題は「{a} → {b}」（{rate}）",
        "lede_off": "。目安から外れた指標が {n} つあります。",
        "lede_end": "です。",
        "lede_ok": "大きな問題はありません。",
        "toc": "このボードの読み方",

        "where_h": "「{a} → {b}」で止まっています。{a} {na} 人のうち、{b}まで進んだのは {nb} 人（{rate}）。",
        "where_note": "人数がいちばん減るのは「{a} → {b}」（−{n} 人）。ただ、業界の目安と比べていちばん離れているのは上の段です。",
        "next2": "① {a} のあと、どの段で止まっているか",
        "next3": "② なぜそこで止まっているのか、数字を確かめる",
        "next4": "③ では、何から手をつけるか",

        "why_h_bench": "{label}が業界の目安（{band}）を下回っています。",
        "why_h_flow": "「{a} → {b}」に進む人の割合が、この流れの中でいちばん低い段です。",
        "why_h_none": "業界の目安から大きく外れた指標はありません。流れの中で人数が大きく減る段を見ます。",
        "why_step": "{a} → {b}",
        "others": "ほかにも目安から外れている:",
        "others_more": "詳しい数字で見る ↓",
        "do_h_gain": "{label}が目安の下限 {low} まで上がると、{target}は {gain} 増える見込みです。",
        "do_h": "まず「{a} → {b}」から手をつけます。",
        "do_calc": "計算: {base} 人 × {low} − {now} 人",
        "gain": "+約 {n} 人",
        "why": "なぜ", "check": "確かめ方",
        "do_note": "よくある原因と確かめ方の例です。サイトに合うかを確かめてから進めてください。直したあとは、このボードで前期と比べて効果を見られます。",
        "go_edit": "✎ 流れに段を足す", "go_ch": "流入別に見る ▾", "go_gl": "指標辞典で見る",
        # AI prompt
        "ai_btn": "✦ 自分の AI に聞く（プロンプトを作る）",
        "ai_lead": "ChatGPT・Claude・Gemini など、お使いの AI に貼り付けて深掘りできます。",
        "ai_ask_k": "何を聞く？",
        "ai_cause": "原因を深掘りする", "ai_ideas": "施策のアイデアを増やす", "ai_report": "報告用の文章にする",
        "ai_anon": "サイト名を入れない（おすすめ）", "ai_detail": "詳しい数字（転換ファネル）も入れる",
        "ai_copy": "コピー", "ai_copied": "✓ コピーしました", "ai_copy_fail": "コピーできませんでした。文章を選んでコピーしてください。",
        "ai_note": "SiteKPI から AI には何も送りません。コピーした文章を、あなたが使っている AI に貼り付けてください。貼り付ける前に、社外に出してよい数字か確かめてください。",
        "p_role": "あなたはウェブ解析とサイト改善の専門家です。",
        "p_site_anon": "次は、あるサイト（業種: {ind}、目的: {beh}）の GA4 の数字です。期間は {period}、前期はその前の同じ長さです。",
        "p_site_named": "次は、サイト「{site}」（業種: {ind}、目的: {beh}）の GA4 の数字です。期間は {period}、前期はその前の同じ長さです。",
        "p_s1": "■ 大丈夫か", "p_s2": "■ どこで離れているか（人数）", "p_s3": "■ いちばんの課題: {a} → {b}",
        "p_s4": "■ SiteKPI の対策案", "p_s5": "■ 詳しい数字（転換ファネル）", "p_ask": "■ お願い",
        "p_cause": "「{a} → {b}」で止まっている原因の仮説を、可能性が高い順に 5 つ挙げてください。それぞれ、GA4 のどのレポート・イベントで確かめられるかも書いてください。",
        "p_ideas": "「{a} → {b}」を上げる施策を、すぐできるもの・1 か月かかるものに分けて 6 つ挙げてください。それぞれ、効果を GA4 でどう測るかも書いてください。",
        "p_report": "上の内容を、上司に送る週次報告（300 字以内・箇条書き 3 つ）にまとめてください。数字は変えないでください。",
        "p_tail": "業界目安は公開データの一般的な値です。断定せず、確かめ方とセットで答えてください。",
        "p_prev": "前期 {d}", "p_band": "業界目安 {band}", "p_gain": "目安の下限まで上がると {gain}",
    },
    "en": {
        "q0": "Overview", "q1": "Is it OK?", "q2": "Where do people leave?", "q3": "What is off?", "q4": "What to do?",
        "ref": "Reference", "ref_k": "Every number",
        "strip": "How to read this board",
        "a1_ok": "No big problem", "a1_issue": "Room to grow: {a} → {b}",
        "a3_n": "{n} off the standard", "a3_none": "Nothing far off the standard",
        "a4_gain": "{n} things to try · {gain}", "a4": "{n} things to try",
        "but": "But ",
        "lede_core": "the main issue is “{a} → {b}” ({rate})",
        "lede_off": ". {n} metrics are off the standard.",
        "lede_end": ".",
        "lede_ok": "Nothing big is wrong.",
        "toc": "How to read this board",

        "where_h": "People stall at “{a} → {b}”. Of {na} who reached {a}, {nb} reached {b} ({rate}).",
        "where_note": "The biggest drop in people is “{a} → {b}” (−{n}). Against the industry standard, though, the step above is further off.",
        "next2": "① After {a}, which step do people stall at",
        "next3": "② Check the numbers behind it",
        "next4": "③ So where to start",

        "why_h_bench": "{label} is below the industry standard ({band}).",
        "why_h_flow": "“{a} → {b}” has the lowest share of people moving on in this flow.",
        "why_h_none": "Nothing is far off the industry standard. Look at where the flow loses the most people.",
        "why_step": "{a} → {b}",
        "others": "Also off the standard:",
        "others_more": "See every number ↓",
        "do_h_gain": "If {label} reached the low end of the standard ({low}), {target} would grow by {gain}.",
        "do_h": "Start with “{a} → {b}”.",
        "do_calc": "Calculation: {base} × {low} − {now}",
        "gain": "about +{n} people",
        "why": "Why", "check": "How to check",
        "do_note": "These are common causes and checks, not a diagnosis. Make sure they fit your site first. After a change, compare with the prior period here.",
        "go_edit": "✎ Add a step to the flow", "go_ch": "By traffic source ▾", "go_gl": "Open in the glossary",
        "ai_btn": "✦ Ask your own AI (make a prompt)",
        "ai_lead": "Paste it into the AI you use — ChatGPT, Claude, Gemini — to dig deeper.",
        "ai_ask_k": "Ask for",
        "ai_cause": "Causes", "ai_ideas": "More ideas", "ai_report": "A short report",
        "ai_anon": "Leave out the site name (recommended)", "ai_detail": "Include the detailed funnel numbers",
        "ai_copy": "Copy", "ai_copied": "✓ Copied", "ai_copy_fail": "Could not copy. Select the text and copy it.",
        "ai_note": "SiteKPI sends nothing to any AI. Paste the copied text into the AI you use. Check that these numbers may leave your company first.",
        "p_role": "You are an expert in web analytics and website improvement.",
        "p_site_anon": "Below are GA4 numbers for a website (industry: {ind}, goal: {beh}). Period: {period}; the prior period is the same length just before it.",
        "p_site_named": "Below are GA4 numbers for the website “{site}” (industry: {ind}, goal: {beh}). Period: {period}; the prior period is the same length just before it.",
        "p_s1": "■ Is it OK?", "p_s2": "■ Where do people leave (people)", "p_s3": "■ Biggest issue: {a} → {b}",
        "p_s4": "■ SiteKPI's suggestions", "p_s5": "■ Detailed numbers (conversion funnel)", "p_ask": "■ Request",
        "p_cause": "List 5 hypotheses for why people stall at “{a} → {b}”, most likely first. For each, say which GA4 report or event would confirm it.",
        "p_ideas": "List 6 ideas to improve “{a} → {b}”, split into quick wins and one-month projects. For each, say how to measure the effect in GA4.",
        "p_report": "Summarise the above as a weekly report for my manager (under 120 words, 3 bullet points). Do not change the numbers.",
        "p_tail": "Industry standards are general values from public data. Do not state things as certain; pair each answer with how to check it.",
        "p_prev": "prior {d}", "p_band": "industry standard {band}", "p_gain": "at the low end of the standard: {gain}",
    },
    "ko": {
        "q0": "총평", "q1": "괜찮은가?", "q2": "어디서 이탈하는가?", "q3": "어디가 이상한가?", "q4": "어떻게 할까?",
        "ref": "참고", "ref_k": "모든 숫자",
        "strip": "이 보드를 읽는 순서",
        "a1_ok": "큰 문제 없음", "a1_issue": "개선 여지는 「{a} → {b}」",
        "a3_n": "기준을 벗어난 {n}개", "a3_none": "기준에서 크게 벗어난 지표 없음",
        "a4_gain": "{n}가지 방법 · {gain}", "a4": "{n}가지 방법",
        "but": "다만 ",
        "lede_core": "가장 큰 과제는 「{a} → {b}」({rate})",
        "lede_off": ". 기준을 벗어난 지표가 {n}개 있습니다.",
        "lede_end": "입니다.",
        "lede_ok": "큰 문제는 없습니다.",
        "toc": "이 보드를 읽는 순서",

        "where_h": "「{a} → {b}」에서 멈추고 있어요. {a} {na}명 중 {b}까지 간 사람은 {nb}명({rate}).",
        "where_note": "인원이 가장 많이 줄어드는 곳은 「{a} → {b}」(−{n}명). 다만 업계 기준과 비교해 가장 벗어난 곳은 위의 단계예요.",
        "next2": "① {a} 다음, 어느 단계에서 멈추는가",
        "next3": "② 왜 거기서 멈추는지 숫자로 확인",
        "next4": "③ 그럼 무엇부터 할까",

        "why_h_bench": "{label}이(가) 업계 기준({band})보다 낮아요.",
        "why_h_flow": "「{a} → {b}」로 넘어가는 비율이 이 흐름에서 가장 낮아요.",
        "why_h_none": "업계 기준에서 크게 벗어난 지표는 없어요. 흐름에서 인원이 크게 줄어드는 단계를 봐요.",
        "why_step": "{a} → {b}",
        "others": "그 밖에 기준을 벗어난 것:",
        "others_more": "자세한 숫자에서 보기 ↓",
        "do_h_gain": "{label}이(가) 기준 하한 {low}까지 오르면 {target}은(는) {gain} 늘어날 전망이에요.",
        "do_h": "먼저 「{a} → {b}」부터 손대요.",
        "do_calc": "계산: {base}명 × {low} − {now}명",
        "gain": "+약 {n}명",
        "why": "이유", "check": "확인 방법",
        "do_note": "흔한 원인과 확인 방법의 예예요. 내 사이트에 맞는지 먼저 확인하세요. 고친 뒤에는 이 보드에서 전기와 비교해 효과를 볼 수 있어요.",
        "go_edit": "✎ 흐름에 단계 추가", "go_ch": "유입별로 보기 ▾", "go_gl": "지표 사전에서 보기",
        "ai_btn": "✦ 내 AI에게 묻기 (프롬프트 만들기)",
        "ai_lead": "ChatGPT·Claude·Gemini 등 쓰고 있는 AI에 붙여 넣어 더 깊이 볼 수 있어요.",
        "ai_ask_k": "무엇을 물을까?",
        "ai_cause": "원인 파고들기", "ai_ideas": "개선 아이디어 늘리기", "ai_report": "보고용 문장 만들기",
        "ai_anon": "사이트 이름 넣지 않기 (추천)", "ai_detail": "자세한 숫자(전환 퍼널)도 넣기",
        "ai_copy": "복사", "ai_copied": "✓ 복사했어요", "ai_copy_fail": "복사하지 못했어요. 글을 선택해서 복사해 주세요.",
        "ai_note": "SiteKPI는 AI에 아무것도 보내지 않아요. 복사한 글을 쓰고 있는 AI에 붙여 넣으세요. 붙여 넣기 전에 회사 밖으로 내보내도 되는 숫자인지 확인하세요.",
        "p_role": "당신은 웹 분석과 사이트 개선 전문가입니다.",
        "p_site_anon": "다음은 어떤 사이트(업종: {ind}, 목적: {beh})의 GA4 숫자입니다. 기간은 {period}, 전기는 그 직전 같은 길이입니다.",
        "p_site_named": "다음은 사이트 「{site}」(업종: {ind}, 목적: {beh})의 GA4 숫자입니다. 기간은 {period}, 전기는 그 직전 같은 길이입니다.",
        "p_s1": "■ 괜찮은가", "p_s2": "■ 어디서 이탈하는가 (인원)", "p_s3": "■ 가장 큰 과제: {a} → {b}",
        "p_s4": "■ SiteKPI의 대책안", "p_s5": "■ 자세한 숫자 (전환 퍼널)", "p_ask": "■ 부탁",
        "p_cause": "「{a} → {b}」에서 멈추는 원인의 가설을 가능성이 높은 순서로 5개 들어 주세요. 각각 GA4의 어떤 보고서·이벤트로 확인할 수 있는지도 써 주세요.",
        "p_ideas": "「{a} → {b}」를 높일 방법을 바로 할 수 있는 것과 한 달 걸리는 것으로 나눠 6개 들어 주세요. 각각 GA4에서 효과를 어떻게 잴지도 써 주세요.",
        "p_report": "위 내용을 상사에게 보낼 주간 보고(300자 이내, 글머리표 3개)로 정리해 주세요. 숫자는 바꾸지 마세요.",
        "p_tail": "업계 기준은 공개 데이터의 일반적인 값입니다. 단정하지 말고 확인 방법과 함께 답해 주세요.",
        "p_prev": "전기 {d}", "p_band": "업계 기준 {band}", "p_gain": "기준 하한까지 오르면 {gain}",
    },
}

# --- 対策カタログ ------------------------------------------------------------------------------------
# kind → {"head": ① の後半, "acts": [(title, why, check, link)]}  link: edit · ch · gl · ""

ACTIONS: dict[str, dict[str, dict]] = {
    "ja": {
        "engage": {"head": "来た人の多くが、すぐに離れています", "acts": [
            ("最初の画面で「何のサイトか」と次の一歩を見せる", "すぐ離れる人は、最初の数秒で目的のものが見つからないことが多い。", "流入別に「しっかり見た」率を比べ、低い流入元の着地ページを見る", "ch"),
            ("広告・検索の言葉と、着地ページの中身をそろえる", "期待と違うページに着くと、読まずに戻る。", "参照元・キャンペーン別のエンゲージ率を比べる", "ch"),
            ("ページの表示速度を確かめる（特にスマホ）", "表示が遅いと、内容を見る前に離れる。", "デバイス別のエンゲージ率と、PageSpeed Insights の結果を見る", "gl")]},
        "browse": {"head": "見に来た人が次のページに進めていません", "acts": [
            ("次に見てほしいページへのリンクを、目に入る位置に置く", "読み終えたあとの行き先がないと、そこで終わる。", "ページ別の離脱数（探索レポート）で、止まっているページを見る", "edit"),
            ("一覧・検索から詳細ページに入りやすくする", "一覧で比べにくいと、詳細まで進まない。", "検索結果ページの数と、そこからの詳細ページ閲覧を比べる", "edit"),
            ("流入元ごとに、入口のページを分けて考える", "流入元によって、知りたいことが違う。", "流入別に、この段に進む割合を比べる", "ch")]},
        "cart": {"head": "商品を見た人がカートに入れていません", "acts": [
            ("価格・在庫・送料・届く日を、商品ページの上の方で見せる", "買うかどうかの判断材料が足りないと、カートに入れない。", "商品ページの滞在時間と、カート追加率を商品別に比べる", "gl"),
            ("写真・レビュー・サイズ表など、迷いを減らす情報を足す", "不安が残ると、いったん離れて比べに行く。", "レビューのある商品とない商品で、カート追加率を比べる", ""),
            ("「カートに入れる」ボタンを、スマホでも見つけやすくする", "スマホではボタンが画面の外にあることが多い。", "デバイス別のカート追加率を比べる", "ch")]},
        "checkout": {"head": "カートに入れた人が買い切れていません", "acts": [
            ("送料・手数料・届く日を、カートより前に見せる", "カートで止まる理由でいちばん多いのは「思っていなかった追加費用」（Baymard の調査）。", "送料無料ラインの前後で「カート → 購入手続き」を比べる", "ch"),
            ("購入手続きの入力と決済手段を見直す", "入力が多い・使いたい決済がないと、途中でやめる。", "配送先・支払い情報（add_shipping_info / add_payment_info）を流れに足して、どこで止まるかを見る", "edit"),
            ("カートに入れたまま離れた人を呼び戻す", "カートに入れた人の多くは、その場では買わずに比べに行く。", "メール・リターゲティングから戻った人の購入率を流入別で見る", "ch")]},
        "form_start": {"head": "見た人がフォームの入力を始めていません", "acts": [
            ("申し込み・問い合わせの入口を、各ページの目に入る位置に置く", "入口が見つからないと、始めようがない。", "ボタンのクリック数（click イベント）と、フォーム開始を比べる", "edit"),
            ("始める前の不安（費用・連絡の有無・所要時間）に答える", "何が起きるか分からないと、入力を始めない。", "よくある質問・料金ページを見た人のフォーム開始率を比べる", ""),
            ("電話・LINE など、フォーム以外の手段も用意する", "フォームが面倒な人は、別の手段なら連絡する。", "電話・LINE のクリックを「分かれ道」として流れに足す", "edit")]},
        "form_submit": {"head": "入力を始めた人が送信まで進めていません", "acts": [
            ("入力項目を減らし、必須だけにする", "項目が多いほど、途中でやめる人が増える。", "フォーム開始 → 送信の割合を、項目を減らす前後で比べる", ""),
            ("エラーの出方を見直す（どこが違うかをその場で示す）", "送信後にまとめてエラーが出ると、やり直さずに離れる。", "送信ボタンのクリック数と、送信完了の差を見る", "edit"),
            ("スマホで入力しやすくする（キーボード・自動入力）", "スマホは入力の手間が大きい。", "デバイス別の「開始 → 送信」を比べる", "ch")]},
        "signup": {"head": "見た人が登録まで進めていません", "acts": [
            ("登録すると何ができるかを、登録ボタンの近くで見せる", "得られるものが分からないと、登録しない。", "登録ページを見た人の登録率を、流入別に比べる", "ch"),
            ("登録の手順を短くする（Google ログインなど）", "パスワードやメール確認で止まる人が多い。", "sign_up の開始と完了を分けて流れに足す", "edit"),
            ("登録しなくても試せる範囲を作る", "試す前に登録を求めると離れる。", "無料で見られるページの閲覧者の登録率を比べる", "")]},
        "click": {"head": "見た人が次の行動（クリック）に進んでいません", "acts": [
            ("押してほしいリンク・ボタンを 1 つに絞り、目に入る位置に置く", "選択肢が多いと、どれも押されない。", "クリックされたリンク先（link_url）を見て、押されている場所を確かめる", "gl"),
            ("リンクの文言を「押すと何が起きるか」が分かるものにする", "行き先が分からないリンクは押されない。", "文言を変える前後で、クリック率を比べる", ""),
            ("読み終えた位置（ページの下）にも同じボタンを置く", "最後まで読んだ人ほど、次の行動を探している。", "スクロール 90% の人のクリック率を見る", "edit")]},
        "download": {"head": "見た人が資料のダウンロードまで進めていません", "acts": [
            ("資料の中身（目次・ページ数）を見せてから案内する", "中身が分からない資料は取られない。", "資料ページを見た人のダウンロード率を比べる", ""),
            ("ダウンロード前の入力を減らす", "入力が多いと、資料を諦める。", "フォーム開始と file_download の差を見る", "edit"),
            ("関連する記事・ページの最後から資料に案内する", "興味が高いのは、関連する内容を読み終えたとき。", "流入別・ページ別のダウンロード率を比べる", "ch")]},
        "video": {"head": "動画を見始めた人が最後まで見ていません", "acts": [
            ("最初の 10 秒で、動画の中身と長さを伝える", "何の動画か分からないと、すぐに止める。", "video_progress（10%・25%）で止まる位置を見る", "gl"),
            ("長い動画を短く分ける・章をつける", "長いほど、途中で離れる。", "動画の長さ別に完了率を比べる", ""),
            ("見てほしい人が来る流入元から案内する", "興味のない人は最後まで見ない。", "流入別の完了率を比べる", "ch")]},
        "overall": {"head": "来た人のうち、成果まで進む人が少なめです", "acts": [
            ("流れの中で人数が大きく減る段から順に見る", "全体の率は、どこか一つの段の弱さで下がることが多い。", "「どこで離れている？」で人数がいちばん減る段を確かめる", "edit"),
            ("成果につながりやすい流入元を増やす", "流入元によって、成果まで進む割合が大きく違う。", "流入別に成果の率を比べる", "ch"),
            ("比べる業種が合っているかを確かめる", "業種が違うと、目安そのものがずれる。", "比べる業種を変えて、目安の範囲を見比べる", "")]},
    },
    "en": {
        "engage": {"head": "many visitors leave right away", "acts": [
            ("Show what the site is and the next step on the first screen", "People who leave fast often can't find what they came for in the first seconds.", "Compare the engaged share by traffic source and check landing pages of weak ones", "ch"),
            ("Match the landing page to the ad or search words", "Landing on a page that differs from what they expected sends people back.", "Compare engagement rate by source and campaign", "ch"),
            ("Check page speed, especially on phones", "Slow pages lose people before they read anything.", "Compare engagement by device and check PageSpeed Insights", "gl")]},
        "browse": {"head": "visitors don't move on to the next page", "acts": [
            ("Put links to the pages you want read next where they're seen", "With nowhere to go after reading, the visit ends there.", "Find where people stop with page-level exits (exploration report)", "edit"),
            ("Make it easier to go from lists and search to detail pages", "Hard-to-compare lists stop people before the detail page.", "Compare search result views with detail views after them", "edit"),
            ("Think about the entry page per traffic source", "People from different sources want different things.", "Compare the share reaching this step by source", "ch")]},
        "cart": {"head": "people who view products don't add them to the cart", "acts": [
            ("Show price, stock, shipping and delivery date high on the product page", "Without what they need to decide, people don't add to cart.", "Compare time on product page and add-to-cart rate by product", "gl"),
            ("Add photos, reviews and size charts that remove doubts", "Lingering doubts send people off to compare elsewhere.", "Compare add-to-cart rate for products with and without reviews", ""),
            ("Make the add-to-cart button easy to find on phones", "On phones the button is often below the screen.", "Compare add-to-cart rate by device", "ch")]},
        "checkout": {"head": "people who add to cart don't finish buying", "acts": [
            ("Show shipping, fees and delivery date before the cart", "The top reason for leaving at the cart is unexpected extra costs (Baymard research).", "Compare cart → checkout around the free-shipping threshold", "ch"),
            ("Review checkout fields and payment methods", "Long forms or a missing payment method make people give up.", "Add add_shipping_info / add_payment_info to the flow to see where people stop", "edit"),
            ("Bring back people who left items in the cart", "Many who add to cart leave to compare and don't buy right away.", "Compare the purchase rate of people returning from email or retargeting", "ch")]},
        "form_start": {"head": "people who view don't start the form", "acts": [
            ("Put the entry to apply or contact where it's seen on every page", "If they can't find the entry, they can't start.", "Compare button clicks (click event) with form starts", "edit"),
            ("Answer worries before the form (cost, follow-up calls, time)", "Not knowing what happens next stops people from starting.", "Compare form start rate of people who saw the FAQ or pricing page", ""),
            ("Offer other ways too, such as phone or chat", "People who find forms tedious may still call or message.", "Add phone or chat clicks to the flow as side paths", "edit")]},
        "form_submit": {"head": "people who start the form don't submit it", "acts": [
            ("Cut the form to required fields only", "The more fields, the more people give up midway.", "Compare start → submit before and after removing fields", ""),
            ("Show errors right where they happen", "A list of errors after submitting makes people leave instead of retrying.", "Compare submit-button clicks with completed submissions", "edit"),
            ("Make typing easy on phones (keyboards, autofill)", "Typing costs more on phones.", "Compare start → submit by device", "ch")]},
        "signup": {"head": "people who view don't sign up", "acts": [
            ("Show what signing up gives right next to the button", "If the benefit isn't clear, people don't sign up.", "Compare the sign-up rate of sign-up page viewers by source", "ch"),
            ("Shorten sign-up (Google sign-in and similar)", "Passwords and email checks stop many people.", "Add sign-up start and finish as separate steps to the flow", "edit"),
            ("Let people try something before signing up", "Asking to sign up before trying makes people leave.", "Compare the sign-up rate of people who viewed free pages", "")]},
        "click": {"head": "people who view don't take the next step (click)", "acts": [
            ("Narrow to one link or button and put it where it's seen", "With many choices, none get clicked.", "Check where people click (link_url)", "gl"),
            ("Word links so people know what happens when they click", "Links with an unclear destination don't get clicked.", "Compare click rate before and after changing the wording", ""),
            ("Repeat the button where reading ends (page bottom)", "People who read to the end are looking for the next step.", "Look at the click rate of people who scrolled 90%", "edit")]},
        "download": {"head": "people who view don't download the document", "acts": [
            ("Show what's inside (contents, page count) before asking", "People don't take a document they can't picture.", "Compare download rate of people who saw the document page", ""),
            ("Ask for less before the download", "Long forms make people give up the document.", "Compare form starts with file_download", "edit"),
            ("Offer the document at the end of related articles", "Interest peaks right after reading related content.", "Compare download rate by source and page", "ch")]},
        "video": {"head": "people who start the video don't finish it", "acts": [
            ("Say what the video is and how long in the first 10 seconds", "If it's unclear, people stop right away.", "Look at where people stop with video_progress (10% · 25%)", "gl"),
            ("Split long videos or add chapters", "The longer the video, the more people leave.", "Compare completion rate by video length", ""),
            ("Promote it where interested people come from", "People who aren't interested won't watch to the end.", "Compare completion rate by source", "ch")]},
        "overall": {"head": "few visitors reach the goal", "acts": [
            ("Look at the steps that lose the most people first", "The overall rate is often dragged down by one weak step.", "Check the biggest drop in “Where do people leave?”", "edit"),
            ("Grow the traffic sources that convert well", "The share reaching the goal varies a lot by source.", "Compare the goal rate by source", "ch"),
            ("Check that the compared industry fits", "With the wrong industry, the standard itself is off.", "Change the industry and compare the ranges", "")]},
    },
    "ko": {
        "engage": {"head": "들어온 사람 대부분이 바로 나가고 있어요", "acts": [
            ("첫 화면에서 「무슨 사이트인지」와 다음 행동을 보여 주기", "바로 나가는 사람은 처음 몇 초 안에 원하는 것을 못 찾는 경우가 많아요.", "유입별 「제대로 봤다」 비율을 비교하고, 낮은 유입의 착지 페이지를 보기", "ch"),
            ("광고·검색어와 착지 페이지 내용을 맞추기", "기대와 다른 페이지에 오면 읽지 않고 돌아가요.", "참조·캠페인별 참여율을 비교하기", "ch"),
            ("페이지 표시 속도 확인하기 (특히 휴대폰)", "느리면 내용을 보기 전에 나가요.", "기기별 참여율과 PageSpeed Insights 결과를 보기", "gl")]},
        "browse": {"head": "보러 온 사람이 다음 페이지로 넘어가지 않고 있어요", "acts": [
            ("다음에 보여 주고 싶은 페이지 링크를 눈에 띄는 곳에 두기", "다 읽은 뒤 갈 곳이 없으면 거기서 끝나요.", "페이지별 이탈(탐색 보고서)로 멈추는 페이지를 보기", "edit"),
            ("목록·검색에서 상세 페이지로 들어가기 쉽게 하기", "목록에서 비교하기 어려우면 상세까지 가지 않아요.", "검색 결과 페이지 수와 그 뒤 상세 페이지 열람을 비교하기", "edit"),
            ("유입별로 입구 페이지를 나눠 생각하기", "유입에 따라 알고 싶은 것이 달라요.", "유입별로 이 단계까지 가는 비율을 비교하기", "ch")]},
        "cart": {"head": "상품을 본 사람이 장바구니에 담지 않고 있어요", "acts": [
            ("가격·재고·배송비·도착일을 상품 페이지 위쪽에 보여 주기", "판단할 정보가 부족하면 담지 않아요.", "상품별 체류 시간과 장바구니 추가율을 비교하기", "gl"),
            ("사진·리뷰·사이즈표 등 망설임을 줄이는 정보 추가하기", "불안이 남으면 일단 나가서 비교해요.", "리뷰가 있는 상품과 없는 상품의 장바구니 추가율을 비교하기", ""),
            ("「장바구니 담기」 버튼을 휴대폰에서도 찾기 쉽게 하기", "휴대폰에서는 버튼이 화면 밖에 있는 경우가 많아요.", "기기별 장바구니 추가율을 비교하기", "ch")]},
        "checkout": {"head": "장바구니에 담은 사람이 끝까지 사지 않고 있어요", "acts": [
            ("배송비·수수료·도착일을 장바구니보다 먼저 보여 주기", "장바구니에서 멈추는 가장 흔한 이유는 「예상 못 한 추가 비용」이에요(Baymard 조사).", "무료 배송 기준 전후로 「장바구니 → 결제 시작」을 비교하기", "ch"),
            ("결제 단계의 입력 항목과 결제 수단 다시 보기", "입력이 많거나 원하는 결제 수단이 없으면 중간에 그만둬요.", "배송지·결제 정보(add_shipping_info / add_payment_info)를 흐름에 추가해 어디서 멈추는지 보기", "edit"),
            ("장바구니에 담은 채 떠난 사람 다시 부르기", "담은 사람 상당수는 바로 사지 않고 비교하러 가요.", "메일·리타기팅으로 돌아온 사람의 구매율을 유입별로 보기", "ch")]},
        "form_start": {"head": "본 사람이 폼 입력을 시작하지 않고 있어요", "acts": [
            ("신청·문의 입구를 각 페이지의 눈에 띄는 곳에 두기", "입구를 못 찾으면 시작할 수 없어요.", "버튼 클릭(click 이벤트)과 폼 시작을 비교하기", "edit"),
            ("시작 전 불안(비용·연락 여부·소요 시간)에 답하기", "무슨 일이 생길지 모르면 입력을 시작하지 않아요.", "FAQ·요금 페이지를 본 사람의 폼 시작률을 비교하기", ""),
            ("전화·LINE 등 폼 외의 수단도 준비하기", "폼이 귀찮은 사람도 다른 수단이면 연락해요.", "전화·LINE 클릭을 「갈림길」로 흐름에 추가하기", "edit")]},
        "form_submit": {"head": "입력을 시작한 사람이 전송까지 가지 않고 있어요", "acts": [
            ("입력 항목을 줄여 필수만 남기기", "항목이 많을수록 중간에 그만두는 사람이 늘어요.", "항목을 줄이기 전후로 「시작 → 전송」 비율을 비교하기", ""),
            ("오류 표시 방식 다시 보기 (그 자리에서 알려 주기)", "전송 후에 오류가 한꺼번에 나오면 다시 하지 않고 떠나요.", "전송 버튼 클릭 수와 전송 완료의 차이를 보기", "edit"),
            ("휴대폰에서 입력하기 쉽게 하기 (키보드·자동 입력)", "휴대폰은 입력 부담이 커요.", "기기별 「시작 → 전송」을 비교하기", "ch")]},
        "signup": {"head": "본 사람이 가입까지 가지 않고 있어요", "acts": [
            ("가입하면 무엇을 할 수 있는지 가입 버튼 근처에서 보여 주기", "얻는 것이 분명하지 않으면 가입하지 않아요.", "가입 페이지를 본 사람의 가입률을 유입별로 비교하기", "ch"),
            ("가입 절차 줄이기 (Google 로그인 등)", "비밀번호·메일 인증에서 멈추는 사람이 많아요.", "가입 시작과 완료를 나눠 흐름에 추가하기", "edit"),
            ("가입하지 않아도 써 볼 수 있는 범위 만들기", "써 보기 전에 가입을 요구하면 떠나요.", "무료로 볼 수 있는 페이지를 본 사람의 가입률을 비교하기", "")]},
        "click": {"head": "본 사람이 다음 행동(클릭)으로 넘어가지 않고 있어요", "acts": [
            ("눌렀으면 하는 링크·버튼을 하나로 줄이고 눈에 띄는 곳에 두기", "선택지가 많으면 아무것도 눌리지 않아요.", "클릭된 링크(link_url)를 보고 눌리는 위치를 확인하기", "gl"),
            ("링크 문구를 「누르면 무엇이 되는지」 알 수 있게 바꾸기", "어디로 가는지 모르는 링크는 눌리지 않아요.", "문구를 바꾸기 전후로 클릭률을 비교하기", ""),
            ("다 읽은 위치(페이지 아래)에도 같은 버튼 두기", "끝까지 읽은 사람일수록 다음 행동을 찾고 있어요.", "90% 스크롤한 사람의 클릭률을 보기", "edit")]},
        "download": {"head": "본 사람이 자료 다운로드까지 가지 않고 있어요", "acts": [
            ("자료 내용(목차·페이지 수)을 보여 주고 안내하기", "내용을 모르는 자료는 받지 않아요.", "자료 페이지를 본 사람의 다운로드율을 비교하기", ""),
            ("다운로드 전 입력 줄이기", "입력이 많으면 자료를 포기해요.", "폼 시작과 file_download의 차이를 보기", "edit"),
            ("관련 글·페이지 끝에서 자료로 안내하기", "관심이 가장 높을 때는 관련 내용을 다 읽었을 때예요.", "유입별·페이지별 다운로드율을 비교하기", "ch")]},
        "video": {"head": "동영상을 보기 시작한 사람이 끝까지 보지 않고 있어요", "acts": [
            ("처음 10초 안에 동영상 내용과 길이 알려 주기", "무슨 영상인지 모르면 바로 멈춰요.", "video_progress(10%·25%)로 멈추는 위치를 보기", "gl"),
            ("긴 영상을 나누거나 챕터 달기", "길수록 중간에 나가요.", "영상 길이별 완료율을 비교하기", ""),
            ("보여 주고 싶은 사람이 오는 유입에서 안내하기", "관심 없는 사람은 끝까지 보지 않아요.", "유입별 완료율을 비교하기", "ch")]},
        "overall": {"head": "들어온 사람 중 성과까지 가는 사람이 적은 편이에요", "acts": [
            ("흐름에서 인원이 크게 줄어드는 단계부터 보기", "전체 비율은 어느 한 단계의 약점 때문에 떨어지는 경우가 많아요.", "「어디서 이탈하는가?」에서 가장 많이 줄어드는 단계를 확인하기", "edit"),
            ("성과로 이어지기 쉬운 유입 늘리기", "유입에 따라 성과까지 가는 비율이 크게 달라요.", "유입별 성과 비율을 비교하기", "ch"),
            ("비교 업종이 맞는지 확인하기", "업종이 다르면 기준 자체가 어긋나요.", "비교 업종을 바꿔 기준 범위를 비교하기", "")]},
    },
}
