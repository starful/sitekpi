"""Shared metric help catalog (説明 / 指標辞典 / ビルダー).

Single source of truth: add metrics here; glossary, builder palette, and
board popovers (via aliases) pick them up. Optional fields:
  ga4_api   — GA4 Data API metric name (builder live fetch)
  ga4_event — GA4 eventName (builder event count)
  sample    — demo display value for offline builder
  hint      — one-line palette hint (defaults to first meaning line)
"""

from __future__ import annotations

from typing import Any

PERIODS: dict[str, str] = {"7d": "直近7日", "28d": "直近28日"}

KINDS: dict[str, dict[str, str]] = {
    "digital": {
        "label": "デジタルKPI",
        "short": "デジタル",
        "desc": "GA4など、サイトやアプリが自動で記録する数字です。"
        "「人」ではなく、だいたい同じブラウザ単位で数えます。",
    },
    "traffic": {
        "label": "流入チャネル",
        "short": "流入",
        "desc": "どこから来たか（検索・広告・直接など）の内訳です。"
        "チャネル名は GA4 の表記のままです。",
    },
    "event": {
        "label": "イベント",
        "short": "イベント",
        "desc": "サイト上の具体的な行動の回数です。"
        "自動収集・拡張計測・推奨イベントを中心に載せています。",
    },
    "business": {
        "label": "業務KPI",
        "short": "業務",
        "desc": "会員DB・売上など、会社の業務システム側の数字です。"
        "GA の数字とズレるのは普通で、ズレ自体がチェックポイントです。",
    },
    "meta": {
        "label": "見方・ボード",
        "short": "見方",
        "desc": "ボード全体の読み方や、デジタルと業務の違いなど。"
        "数値カードではなく、判断の前提です。",
    },
}

# Board / shared_help keys that map onto HELP ids
ALIASES: dict[str, str] = {
    "bounce_like": "bounce_rate",
    "pv": "pageviews",
    "pv_uu": "pages_per_uu",
    "engaged_title": "engaged",
}


def _h(
    kind: str,
    title: str,
    meaning: str,
    formula: str,
    tip: str,
    *,
    ga4_api: str | None = None,
    ga4_event: str | None = None,
    sample: str | None = None,
    hint: str | None = None,
    palette: bool = True,
) -> dict[str, Any]:
    out: dict[str, Any] = {
        "kind": kind,
        "title": title,
        "meaning": meaning,
        "formula": formula,
        "tip": tip,
        "palette": palette,
    }
    if ga4_api:
        out["ga4_api"] = ga4_api
    if ga4_event:
        out["ga4_event"] = ga4_event
    if sample is not None:
        out["sample"] = sample
    if hint:
        out["hint"] = hint
    return out


HELP: dict[str, dict[str, Any]] = {
    # ── Audience / volume ──────────────────────────────────────────
    "uu": _h(
        "digital",
        "UU（ユニークユーザー）",
        "選んだ期間にサイトを開いた「ブラウザ」の数です。\n"
        "同じブラウザなら、期間中に何度来てもだいたい1と数えます。\n"
        "厳密な人数ではありません。同じ人がスマホとPCで来ると2になることがあります。",
        "GA4: activeUsers（期間）",
        "UUが増えても登録や売上が伸びないときは、「来ただけで動かない」状態です。流入チャネルや最初の画面を疑います。",
        ga4_api="activeUsers",
        sample="38,920",
        hint="ブラウザ単位",
    ),
    "total_users": _h(
        "digital",
        "総ユーザー数",
        "期間中にサイトやアプリを使ったユーザーの合計です。\n"
        "GA4 の totalUsers。新規・再訪の区別なしの延べ人数イメージです。",
        "GA4: totalUsers",
        "UU（activeUsers）と近いことが多いですが、定義が少し違います。比較するときは同じ指標で揃えます。",
        ga4_api="totalUsers",
        sample="39,100",
        hint="totalUsers",
    ),
    "new_users": _h(
        "digital",
        "新規ユーザー",
        "このプロパティで初めて計測されたユーザー（ブラウザ）の数です。\n"
        "期間中の「初めての訪問」に近い数字です。",
        "GA4: newUsers",
        "広告やSEOの効果を見るときに使います。新規だけ増えてCVRが下がる週は流入の質を疑います。",
        ga4_api="newUsers",
        sample="15,210",
        hint="初めての訪問",
    ),
    "returning_users": _h(
        "digital",
        "再訪ユーザー",
        "以前にも来たことがあるユーザーの目安です。\n"
        "このパックでは「UU − 新規」のイメージで読みます（厳密な GA4 指標名とは別です）。",
        "だいたい UU − 新規ユーザー",
        "再訪が多いほど定着が進んでいます。会員サービスでは再訪の質もセットで見ます。",
        sample="23,710",
        hint="定着の目安",
    ),
    "sessions": _h(
        "digital",
        "セッション",
        "訪問の回数です。1回サイトを開いて見る流れを1セッションと数えます。\n"
        "同じブラウザでも、別のタイミングでまた来たらセッションは増えます。",
        "GA4: sessions（期間合計）",
        "UUよりセッションが大きいほど、同じ人が何度も来ています。逆にセッション≒UUなら、ほぼ一度きり訪問です。",
        ga4_api="sessions",
        sample="54,210",
        hint="訪問回数",
    ),
    "engaged_sessions": _h(
        "digital",
        "エンゲージメント セッション",
        "ある程度見た（エンゲージした）セッションの件数です。\n"
        "率ではなく件数で規模を見たいときに使います。",
        "GA4: engagedSessions",
        "件数だけ増えて率が下がるときは、薄い訪問が増えているサインです。",
        ga4_api="engagedSessions",
        sample="31,760",
        hint="見た訪問の件数",
    ),
    "sessions_per_uu": _h(
        "digital",
        "セッション / UU",
        "1ブラウザあたり、期間中に何回訪れたかの平均です。\n例: 1.4 なら「平均して1人が期間中に1.4回来た」イメージです。",
        "セッション ÷ UU（または GA4: sessionsPerUser）",
        "1に近いと一度きり、1.5以上だと再訪が効いているサインです。業種で目安は変わります。",
        ga4_api="sessionsPerUser",
        sample="1.39",
        hint="再訪の目安",
    ),
    "pageviews": _h(
        "digital",
        "ページビュー（PV）",
        "ページや画面が表示された回数の合計です。\n同じ人が3ページ見たらPVは3です。人の数ではなく「表示回数」です。",
        "GA4: screenPageViews / views",
        "PVだけ増えて登録が増えないときは、回遊はしていてもゴールに届いていません。",
        ga4_api="screenPageViews",
        sample="140,946",
        hint="表示回数",
    ),
    "pages_per_uu": _h(
        "digital",
        "PV / UU",
        "1ブラウザあたり、期間中に何ページ見たかの平均です。\nセッションあたりページ数より「期間全体での深さ」を見ます。",
        "PV ÷ UU",
        "高いほど回遊が深いです。登録CVRとセットで見ると、深さの質が分かります。",
        sample="3.6",
        hint="閲覧の深さ",
    ),
    "pages_session": _h(
        "digital",
        "セッションあたりページ数",
        "1回の訪問で、平均何ページ見たかです。\n例: 2.4 なら「1訪問あたりだいたい2〜3ページ見ている」イメージです。",
        "PV ÷ セッション（または GA4: screenPageViewsPerSession）",
        "メディアでは高いほど回遊が良いことが多いです。会員サービスでは高すぎると、迷ってクリックしている可能性もあります。",
        ga4_api="screenPageViewsPerSession",
        sample="2.6",
        hint="1訪問のページ数",
    ),
    "views_per_user": _h(
        "digital",
        "ユーザーあたりビュー",
        "1ユーザーあたりの画面表示回数です。\nアプリ・Web 両方で使われる GA4 の viewsPerUser に相当します。",
        "GA4: viewsPerUser",
        "PV / UU と近い読み方です。プロパティの定義に合わせてどちらか一方で揃えます。",
        ga4_api="viewsPerUser",
        sample="3.5",
        hint="viewsPerUser",
    ),
    "new_return": _h(
        "digital",
        "新規 / 再訪",
        "期間中のUUを、初めて来たブラウザ（新規）と、以前にも来たブラウザ（再訪）に分けた割合です。\n"
        "ここでも単位はだいたいブラウザです。本当の「初めての人」と完全一致しません。",
        "新規% = 新規ユーザー ÷ UU × 100\n再訪% = 100 − 新規%",
        "新規ばかり高い = 広告やSEOで集客頼み。再訪が高い = 定着・習慣化が進んでいる、と読みます。",
        sample="39.1% / 60.9%",
        hint="UUの内訳",
    ),
    # ── Engagement ─────────────────────────────────────────────────
    "engaged": _h(
        "digital",
        "エンゲージメント率",
        "「ただ開いてすぐ閉じた」ではなく、ある程度見た訪問の割合です。\n"
        "GA4では、一定時間滞在・キーイベント・複数ページ閲覧などの条件を満たしたセッションです。",
        "エンゲージのあったセッション ÷ 全セッション × 100（GA4: engagementRate）",
        "低いときは、流入の質（期待と違う）か、最初の画面が分かりにくい可能性が高いです。",
        ga4_api="engagementRate",
        sample="58.6%",
        hint="見た訪問の割合",
    ),
    "bounce_rate": _h(
        "digital",
        "すぐ離脱に近い率",
        "あまり見ずに終わった訪問の割合の目安です。\n"
        "このパックでは分かりやすく「100% − エンゲージメント率」で示します（厳密な旧・直帰率とは別物です）。",
        "100 − エンゲージメント率（または GA4: bounceRate）",
        "高いほど「来てすぐ帰った」訪問が多いです。LPや記事の冒頭・読み込みを疑います。",
        ga4_api="bounceRate",
        sample="41.4%",
        hint="100−Engaged",
    ),
    "avg_time": _h(
        "digital",
        "平均エンゲージメント時間",
        "ユーザーがサイトに意識を向けていた平均時間です（分:秒）。\nタブを開いたまま放置した時間は、あまり入りません。",
        "GA4: averageSessionDuration / userEngagementDuration 系",
        "長い＝必ず良い、ではありません。登録までの時間やCVRとセットで見ます。",
        ga4_api="averageSessionDuration",
        sample="1:52",
        hint="分:秒",
    ),
    "user_engagement_duration": _h(
        "digital",
        "ユーザーエンゲージメント時間（合計）",
        "期間中にユーザーがサイトに意識を向けていた時間の合計です（秒）。\n平均ではなく総量で規模を見ます。",
        "GA4: userEngagementDuration",
        "セッション数やUUと並べて、深さの総量を読みます。",
        ga4_api="userEngagementDuration",
        sample="—",
        hint="合計秒",
    ),
    "engaged_sessions_per_user": _h(
        "digital",
        "ユーザーあたりエンゲージ セッション",
        "1ユーザーあたり、エンゲージしたセッションが何回あったかの平均です。",
        "GA4: engagedSessionsPerUser",
        "再訪かつ中身を見ているかを見るときに使います。",
        ga4_api="engagedSessionsPerUser",
        sample="0.82",
        hint="深さ×再訪",
    ),
    "events_per_session": _h(
        "digital",
        "セッションあたりイベント数",
        "1回の訪問で、平均何回イベントが発火したかです。\nクリックやスクロールなども含みます。",
        "GA4: eventsPerSession",
        "高いほど操作が多いです。ただし計測が細かいと自然に高くなります。",
        ga4_api="eventsPerSession",
        sample="8.4",
        hint="操作の多さ",
    ),
    "event_count": _h(
        "digital",
        "イベント数（合計）",
        "期間中に発生した全イベントの件数です。\n種類を問わない総量です。",
        "GA4: eventCount",
        "急増は計測追加のこともあります。主転換イベントと分けて見ます。",
        ga4_api="eventCount",
        sample="—",
        hint="全イベント合計",
    ),
    "conversions": _h(
        "digital",
        "コンバージョン数",
        "GA4 でキーイベント（旧コンバージョン）に指定したイベントの合計です。\n"
        "プロパティ設定に依存します。",
        "GA4: conversions / keyEvents",
        "主転換と一致しているか、設定を確認してから読みます。",
        ga4_api="conversions",
        sample="1,486",
        hint="キーイベント合計",
    ),
    "key_events": _h(
        "digital",
        "キーイベント数",
        "重要な行動としてマークしたイベントの発生回数です。\n"
        "コンバージョン数と同系統の指標です（プロパティの表記に合わせます）。",
        "GA4: keyEvents",
        "何をキーにしたかで意味が変わります。説明と設定をセットで見ます。",
        ga4_api="keyEvents",
        sample="1,486",
        hint="重要イベント",
    ),
    "dau": _h(
        "digital",
        "DAU（1日あたりアクティブ）",
        "1日あたりのアクティブユーザー数のイメージです。\n"
        "期間レポートでは日次系列や平均で見ることが多いです。",
        "GA4: active1DayUsers（日次）",
        "週次・月次のUUと並べて、毎日どれだけ来ているかを見ます。",
        ga4_api="active1DayUsers",
        sample="—",
        hint="日次アクティブ",
    ),
    "wau": _h(
        "digital",
        "WAU（7日アクティブ）",
        "直近7日でアクティブだったユーザー数です。",
        "GA4: active7DayUsers",
        "DAU / WAU 比で習慣化をざっくり見ます。",
        ga4_api="active7DayUsers",
        sample="—",
        hint="週次アクティブ",
    ),
    "mau": _h(
        "digital",
        "MAU（28日アクティブ）",
        "直近28日でアクティブだったユーザー数です。",
        "GA4: active28DayUsers",
        "会員サービスやアプリの「動いている母数」の目安です。",
        ga4_api="active28DayUsers",
        sample="—",
        hint="月次アクティブ",
    ),
    "dau_mau": _h(
        "digital",
        "DAU / MAU",
        "月間アクティブのうち、どれだけが「毎日級」に動いているかの目安です。\n"
        "高いほど習慣利用が進んでいます。",
        "DAU ÷ MAU（概算）",
        "コンテンツや会員サービスで定着を見るときに使います。",
        sample="—",
        hint="習慣化の目安",
    ),
    "scrolled_users": _h(
        "digital",
        "スクロールしたユーザー",
        "ページをある程度スクロールしたユーザーの目安です。\n"
        "拡張計測の scroll イベントに基づきます。",
        "scroll イベントのユーザー数",
        "LPで低いときは、冒頭の期待値ズレや読み込みを疑います。",
        sample="—",
        hint="scroll",
    ),
    "file_downloads": _h(
        "digital",
        "ファイルダウンロード",
        "PDFなどのダウンロード回数です。\n拡張計測の file_download に相当します。",
        "file_download イベント数",
        "資料請求型サイトでは主転換の手前指標になります。",
        sample="—",
        hint="file_download",
    ),
    # ── Commerce / revenue (GA4) ───────────────────────────────────
    "total_revenue": _h(
        "digital",
        "総収益（GA4）",
        "GA4 が計測した収益の合計です。\n業務DBの売上とは返金・税・計上タイミングでズレます。",
        "GA4: totalRevenue",
        "業務の売上と並べて、計測と実計上の差を確認します。",
        ga4_api="totalRevenue",
        sample="—",
        hint="GA4収益",
    ),
    "purchase_revenue": _h(
        "digital",
        "購入収益（GA4）",
        "購入イベントに紐づく収益です。\nEC の purchase 計測が前提です。",
        "GA4: purchaseRevenue",
        "purchase 件数と単価をセットで見ます。",
        ga4_api="purchaseRevenue",
        sample="—",
        hint="purchase収益",
    ),
    "ecommerce_purchases": _h(
        "digital",
        "購入件数（GA4）",
        "購入（purchase）として計測された件数です。",
        "GA4: ecommercePurchases",
        "業務の注文件数とズレたら、二重計測や未送信を疑います。",
        ga4_api="ecommercePurchases",
        sample="—",
        hint="purchase件数",
    ),
    "item_revenue": _h(
        "digital",
        "アイテム収益",
        "商品・アイテム単位の収益です。",
        "GA4: itemRevenue",
        "商品別の貢献を見るときに使います。",
        ga4_api="itemRevenue",
        sample="—",
        hint="商品収益",
    ),
    "add_to_carts": _h(
        "digital",
        "カート追加",
        "カートに入れた回数です（add_to_cart）。",
        "GA4: addToCarts",
        "商品閲覧は多いのにここが少ないと、価格・在庫・導線を疑います。",
        ga4_api="addToCarts",
        sample="—",
        hint="add_to_cart",
    ),
    "checkouts": _h(
        "digital",
        "チェックアウト開始",
        "決済フローに入った回数です（begin_checkout）。",
        "GA4: checkouts",
        "カート追加から大きく落ちるなら、送料・会員必須・入力の多さを疑います。",
        ga4_api="checkouts",
        sample="—",
        hint="begin_checkout",
    ),
    "cart_to_view_rate": _h(
        "digital",
        "閲覧→カート率",
        "商品を見た人のうち、カートに入れた割合の目安です。",
        "GA4: cartToViewRate など",
        "低いときは商品ページの説得力や価格表示を疑います。",
        ga4_api="cartToViewRate",
        sample="—",
        hint="ECファネル",
    ),
    "purchase_to_view_rate": _h(
        "digital",
        "閲覧→購入率",
        "商品閲覧から購入まで進んだ割合の目安です。",
        "GA4: purchaseToViewRate",
        "全体CVRより商品単位の効きを見るときに使います。",
        ga4_api="purchaseToViewRate",
        sample="—",
        hint="商品CVR",
    ),
    "average_purchase_revenue": _h(
        "digital",
        "平均購入金額（GA4）",
        "1購入あたりの平均金額です。",
        "GA4: averagePurchaseRevenue",
        "アップセルやセット販売の効きを見るときに使います。",
        ga4_api="averagePurchaseRevenue",
        sample="—",
        hint="客単価イメージ",
    ),
    "transactions": _h(
        "digital",
        "トランザクション",
        "取引（購入）の件数です。ecommercePurchases と同系統です。",
        "GA4: transactions",
        "収益と並べて単価を確認します。",
        ga4_api="transactions",
        sample="—",
        hint="取引件数",
    ),
    # ── Conversion / funnel (pack) ─────────────────────────────────
    "signups": _h(
        "digital",
        "主転換（登録など）",
        "この業界パックで「いちばん大事」と決めた行動の回数です。\n"
        "B2Cなら会員登録、コンテンツならメルマガ登録など。サイト側のイベント計測です。",
        "期間中の主転換イベント数",
        "業務DBの会員増加とズレたら、計測漏れ・二重計測・承認待ちなどを疑います。",
        sample="1,486",
        hint="主転換件数",
    ),
    "signup_cvr": _h(
        "digital",
        "登録CVR",
        "訪れたブラウザのうち、主転換（登録など）まで進んだ割合です。\n"
        "「100人来たら何人が登録したか」に近い感覚の数字です。",
        "主転換数 ÷ UU × 100",
        "UUが増えてCVRが下がる週は、安い流入が増えたか、導線が弱くなったサインです。",
        sample="3.8%",
        hint="登録 ÷ UU",
    ),
    "session_cvr": _h(
        "digital",
        "セッションCVR",
        "セッションあたりの主転換率です。\nUUベースのCVRより「訪問のたびに取る力」を見ます。",
        "主転換数 ÷ セッション × 100",
        "再訪が多いサイトでは UU CVR と差が出ます。両方見ると解釈が安定します。",
        sample="2.7%",
        hint="登録 ÷ セッション",
    ),
    "pay_start": _h(
        "digital",
        "有料開始クリック",
        "有料プランや決済に進もうとした回数です。\nまだ支払い完了ではありません。「買おうとした」回数です。",
        "期間中の pay_start イベント数",
        "登録は多いのにここが少ないと、料金ページへの導線や価値説明が弱いです。",
        sample="702",
        hint="決済に進む",
    ),
    "signup_to_pay": _h(
        "digital",
        "登録→有料開始率",
        "主転換（登録など）したあと、有料開始まで進んだ割合の目安です。",
        "pay_start ÷ 主転換数 × 100",
        "低いときは料金への導線・トライアル・プラン説明を疑います。",
        sample="47.2%",
        hint="pay_start ÷ 登録",
    ),
    "pay_success": _h(
        "digital",
        "有料完了 / 決済CVR",
        "支払いまで完了した回数です。\n決済CVRは「決済に進んだ人のうち、完了した割合」です。",
        "pay_success 件数\n決済CVR = pay_success ÷ pay_start × 100",
        "pay_start から大きく落ちるなら、価格・決済UI・入力項目を疑います。",
        sample="341 · 48.6%",
        hint="完了と決済率",
    ),
    "lead_cvr": _h(
        "digital",
        "問い合わせCVR",
        "訪れた人のうち、問い合わせ・申し込み完了まで進んだ割合です。\nリード獲得型サイトの主転換率です。",
        "問い合わせ完了 ÷ UU × 100",
        "流入チャネル別に見ると、広告の質の差が出やすいです。",
        sample="—",
        hint="リード系",
    ),
    "apply_cvr": _h(
        "digital",
        "申込CVR",
        "応募・申し込み完了までの割合です。\n採用・講座・コンテストなどで使います。",
        "申込完了 ÷ UU × 100",
        "応募開始は多いのに完了が少ないときは、フォームの長さを疑います。",
        sample="—",
        hint="申込系",
    ),
    "booking_cvr": _h(
        "digital",
        "予約CVR",
        "来店・面談・体験などの予約完了率です。",
        "予約完了 ÷ UU × 100",
        "カレンダー空きや予約UIの摩擦を疑うときに使います。",
        sample="—",
        hint="予約系",
    ),
    "purchase_cvr": _h(
        "digital",
        "購入CVR",
        "訪れた人のうち購入まで進んだ割合です（EC）。",
        "purchase ÷ UU × 100",
        "カート追加率・チェックアウト率とセットでボトルネックを特定します。",
        sample="—",
        hint="EC購入率",
    ),
    "form_start_rate": _h(
        "digital",
        "フォーム開始率",
        "訪れた人のうち、フォーム入力を始めた割合です。",
        "form_start ÷ UU × 100",
        "低いときはCTAの位置や「誰向けか」の説明不足を疑います。",
        sample="—",
        hint="form_start",
    ),
    "form_complete_rate": _h(
        "digital",
        "フォーム完了率",
        "フォームを始めた人のうち、送信まで完了した割合です。",
        "form_submit ÷ form_start × 100",
        "開始は多いのに完了が少ない＝項目数・必須・エラー表示を疑います。",
        sample="—",
        hint="開始→送信",
    ),
    # ── Traffic channels ───────────────────────────────────────────
    "channels": _h(
        "traffic",
        "流入チャネル（全体）",
        "ユーザーがどこから来たか（検索、広告、直接入力など）の内訳です。\n"
        "棒グラフは構成比（%）で、合計がだいたい100%になるよう並べています。",
        "各チャネルの割合 ÷ 全体 × 100（上位〜Other）",
        "細かいキャンペーン名より、大きなチャネルの増減を先に見ます。Paid急増時はCVRもセットで。",
        sample="—",
        hint="構成比",
        palette=False,
    ),
    "ch_organic_search": _h(
        "traffic",
        "Organic Search",
        "自然検索からの流入です。Google などの検索結果（広告以外）から来た訪問です。",
        "sessionDefaultChannelGroup = Organic Search",
        "安定した獲得源になりやすいです。急減は検索順位や需要の変化を疑います。",
        sample="26%",
        hint="自然検索",
    ),
    "ch_direct": _h(
        "traffic",
        "Direct",
        "参照元が取れない流入です。URL直接入力・ブックマーク・計測切れも含みます。",
        "sessionDefaultChannelGroup = Direct",
        "増えても「ブランド想起」とは限りません。計測漏れも疑います。",
        sample="16%",
        hint="直接・不明",
    ),
    "ch_paid_search": _h(
        "traffic",
        "Paid Search",
        "検索連動型広告からの流入です。",
        "sessionDefaultChannelGroup = Paid Search",
        "費用対効果はCVR・CPAとセットで見ます。割合だけ見ないこと。",
        sample="15%",
        hint="検索広告",
    ),
    "ch_paid_social": _h(
        "traffic",
        "Paid Social",
        "SNS広告からの流入です。",
        "sessionDefaultChannelGroup = Paid Social",
        "リーチは取りやすい一方、CVRが低くなりがちです。クリエイティブとLPの一致を見ます。",
        sample="13%",
        hint="SNS広告",
    ),
    "ch_organic_social": _h(
        "traffic",
        "Organic Social",
        "SNSの自然投稿・シェアからの流入です。",
        "sessionDefaultChannelGroup = Organic Social",
        "話題化のあと急増しやすいです。定着するかは再訪とセットで。",
        sample="9%",
        hint="SNS自然",
    ),
    "ch_referral": _h(
        "traffic",
        "Referral",
        "他サイトのリンクからの流入です。",
        "sessionDefaultChannelGroup = Referral",
        "提携・記事・比較サイトなど。参照元ドメイン別に掘ると原因が分かります。",
        sample="—",
        hint="参照サイト",
    ),
    "ch_email": _h(
        "traffic",
        "Email",
        "メール経由の流入です。",
        "sessionDefaultChannelGroup = Email",
        "既存顧客・会員へのリーチです。開封だけでなく着地後のCVRも見ます。",
        sample="—",
        hint="メール",
    ),
    "ch_affiliates": _h(
        "traffic",
        "Affiliates",
        "アフィリエイト経由の流入です。",
        "sessionDefaultChannelGroup = Affiliates",
        "成果報酬型。CVRと承認率をセットで見ます。",
        sample="—",
        hint="アフィリエイト",
    ),
    "ch_display": _h(
        "traffic",
        "Display",
        "ディスプレイ広告（バナー等）からの流入です。",
        "sessionDefaultChannelGroup = Display",
        "認知向き。直接CVRは低くてもアシストを疑う余地があります。",
        sample="—",
        hint="ディスプレイ",
    ),
    "ch_cross_network": _h(
        "traffic",
        "Cross-network",
        "複数ネットワークにまたがる広告流入などです。",
        "sessionDefaultChannelGroup = Cross-network",
        "内訳が粗いので、キャンペーン単位の確認が必要なことがあります。",
        sample="—",
        hint="クロスネットワーク",
    ),
    "ch_unassigned": _h(
        "traffic",
        "Unassigned",
        "チャネルに分類できなかった流入です。",
        "sessionDefaultChannelGroup = Unassigned",
        "UTMや計測の欠けが多いサインです。タグ設定を疑います。",
        sample="—",
        hint="未分類",
    ),
    # ── Events (recommended / auto) ────────────────────────────────
    "ev_session_start": _h(
        "event",
        "session_start",
        "セッションが始まったときに自動で送られるイベントです。\nサイトを開いた回数に近いです。",
        "GA4 自動収集: session_start",
        "セッション数と大きくズレたら計測環境を疑います。",
        ga4_event="session_start",
        sample="—",
        hint="セッション開始",
    ),
    "ev_first_visit": _h(
        "event",
        "first_visit",
        "そのブラウザが初めてサイトを訪れたときのイベントです。",
        "GA4 自動収集: first_visit",
        "新規ユーザーと近い動きをします。",
        ga4_event="first_visit",
        sample="—",
        hint="初回訪問",
    ),
    "ev_page_view": _h(
        "event",
        "page_view",
        "ページが表示されたときのイベントです。",
        "GA4 自動収集: page_view",
        "PVの内訳をイベントで見るときに使います。",
        ga4_event="page_view",
        sample="—",
        hint="ページ表示",
    ),
    "ev_user_engagement": _h(
        "event",
        "user_engagement",
        "一定時間以上サイトを見ていたときに送られるイベントです。\n"
        "行動フローの「しっかり見た」に使います。",
        "GA4 自動収集: user_engagement",
        "エンゲージメント率とセットで読みます。",
        ga4_event="user_engagement",
        sample="—",
        hint="しっかり見た",
    ),
    "ev_scroll": _h(
        "event",
        "scroll",
        "ページの一定割合までスクロールしたときのイベントです（拡張計測）。",
        "GA4 拡張計測: scroll",
        "LPの読了感を見るときに使います。",
        ga4_event="scroll",
        sample="—",
        hint="スクロール",
    ),
    "ev_click": _h(
        "event",
        "click",
        "外部リンクなどのクリック（拡張計測）です。",
        "GA4 拡張計測: click",
        "離脱クリックが多いページは導線を見直します。",
        ga4_event="click",
        sample="—",
        hint="クリック",
    ),
    "ev_view_search_results": _h(
        "event",
        "view_search_results",
        "サイト内検索結果を表示したときのイベントです。",
        "GA4 拡張計測: view_search_results",
        "検索クエリ分析の入口です。見つからないワードが多いとIAのヒントになります。",
        ga4_event="view_search_results",
        sample="—",
        hint="サイト内検索",
    ),
    "ev_file_download": _h(
        "event",
        "file_download",
        "ファイルをダウンロードしたときのイベントです。",
        "GA4 拡張計測: file_download",
        "資料請求の手前指標になります。",
        ga4_event="file_download",
        sample="—",
        hint="ダウンロード",
    ),
    "ev_form_start": _h(
        "event",
        "form_start",
        "フォームの入力を始めたときのイベントです。",
        "GA4 推奨/拡張: form_start",
        "CTAの効きを見る入口です。",
        ga4_event="form_start",
        sample="—",
        hint="フォーム開始",
    ),
    "ev_form_submit": _h(
        "event",
        "form_submit",
        "フォームを送信したときのイベントです。",
        "GA4 推奨/拡張: form_submit",
        "form_start との差が離脱ポイントです。",
        ga4_event="form_submit",
        sample="—",
        hint="フォーム送信",
    ),
    "ev_view_item": _h(
        "event",
        "view_item",
        "商品・アイテム詳細を見たときのイベントです（EC）。",
        "GA4 推奨: view_item",
        "一覧→詳細の興味を見ます。",
        ga4_event="view_item",
        sample="—",
        hint="商品閲覧",
    ),
    "ev_view_item_list": _h(
        "event",
        "view_item_list",
        "商品一覧を見たときのイベントです。",
        "GA4 推奨: view_item_list",
        "カテゴリや検索結果の効きを見るときに使います。",
        ga4_event="view_item_list",
        sample="—",
        hint="一覧閲覧",
    ),
    "ev_select_item": _h(
        "event",
        "select_item",
        "一覧から商品を選んだときのイベントです。",
        "GA4 推奨: select_item",
        "一覧のクリック率を見るときに使います。",
        ga4_event="select_item",
        sample="—",
        hint="商品選択",
    ),
    "ev_add_to_cart": _h(
        "event",
        "add_to_cart",
        "カートに追加したときのイベントです。",
        "GA4 推奨: add_to_cart",
        "購入ファネルの中間指標です。",
        ga4_event="add_to_cart",
        sample="—",
        hint="カート追加",
    ),
    "ev_remove_from_cart": _h(
        "event",
        "remove_from_cart",
        "カートから削除したときのイベントです。",
        "GA4 推奨: remove_from_cart",
        "追加との比で迷い・価格ショックを疑います。",
        ga4_event="remove_from_cart",
        sample="—",
        hint="カート削除",
    ),
    "ev_begin_checkout": _h(
        "event",
        "begin_checkout",
        "チェックアウト（決済）を開始したときのイベントです。",
        "GA4 推奨: begin_checkout",
        "カート→決済の落ちを見る要所です。",
        ga4_event="begin_checkout",
        sample="—",
        hint="決済開始",
    ),
    "ev_add_payment_info": _h(
        "event",
        "add_payment_info",
        "支払い情報を入力したときのイベントです。",
        "GA4 推奨: add_payment_info",
        "決済直前の離脱を見るときに使います。",
        ga4_event="add_payment_info",
        sample="—",
        hint="支払情報",
    ),
    "ev_add_shipping_info": _h(
        "event",
        "add_shipping_info",
        "配送情報を入力したときのイベントです。",
        "GA4 推奨: add_shipping_info",
        "送料表示のショックがここで出ることがあります。",
        ga4_event="add_shipping_info",
        sample="—",
        hint="配送情報",
    ),
    "ev_purchase": _h(
        "event",
        "purchase",
        "購入が完了したときのイベントです。",
        "GA4 推奨: purchase",
        "ECの主転換。業務の注文件数と突き合わせます。",
        ga4_event="purchase",
        sample="—",
        hint="購入完了",
    ),
    "ev_refund": _h(
        "event",
        "refund",
        "返金が発生したときのイベントです。",
        "GA4 推奨: refund",
        "売上とネット収益の差を見るときに使います。",
        ga4_event="refund",
        sample="—",
        hint="返金",
    ),
    "ev_view_cart": _h(
        "event",
        "view_cart",
        "カート画面を見たときのイベントです。",
        "GA4 推奨: view_cart",
        "カート追加後に見ない／見るの差で次の一手が変わります。",
        ga4_event="view_cart",
        sample="—",
        hint="カート表示",
    ),
    "ev_sign_up": _h(
        "event",
        "sign_up",
        "会員登録が完了したときのイベントです。",
        "GA4 推奨: sign_up",
        "会員系サイトの主転換になりやすいです。",
        ga4_event="sign_up",
        sample="1,486",
        hint="会員登録完了",
    ),
    "ev_login": _h(
        "event",
        "login",
        "ログインに成功したときのイベントです。",
        "GA4 推奨: login",
        "既存会員の利用頻度の目安です。",
        ga4_event="login",
        sample="24,880",
        hint="ログイン成功",
    ),
    "ev_search": _h(
        "event",
        "search",
        "サイト内検索を実行したときのイベントです（実装依存）。",
        "カスタム / 推奨: search",
        "view_search_results と併用されることがあります。",
        ga4_event="search",
        sample="—",
        hint="検索実行",
    ),
    "ev_share": _h(
        "event",
        "share",
        "コンテンツをシェアしたときのイベントです。",
        "GA4 推奨: share",
        "拡散の兆しを見るときに使います。",
        ga4_event="share",
        sample="—",
        hint="シェア",
    ),
    "ev_generate_lead": _h(
        "event",
        "generate_lead",
        "リード（見込み客）を獲得したときのイベントです。",
        "GA4 推奨: generate_lead",
        "問い合わせ・資料請求の完了に使うことが多いです。",
        ga4_event="generate_lead",
        sample="—",
        hint="リード獲得",
    ),
    "ev_view_promotion": _h(
        "event",
        "view_promotion",
        "プロモーション枠を表示したときのイベントです。",
        "GA4 推奨: view_promotion",
        "バナーの露出量を見るときに使います。",
        ga4_event="view_promotion",
        sample="—",
        hint="プロモ表示",
    ),
    "ev_select_promotion": _h(
        "event",
        "select_promotion",
        "プロモーション枠をクリックしたときのイベントです。",
        "GA4 推奨: select_promotion",
        "表示に対するクリック率で枠の効きを見ます。",
        ga4_event="select_promotion",
        sample="—",
        hint="プロモクリック",
    ),
    "ev_view_pricing": _h(
        "event",
        "view_pricing",
        "料金ページを見たときのイベントです（サイト実装）。",
        "カスタム: view_pricing",
        "登録→有料の間の興味を見るときに使います。",
        ga4_event="view_pricing",
        sample="3,420",
        hint="料金ページ",
    ),
    "ev_trial_start": _h(
        "event",
        "trial_start",
        "トライアルを開始したときのイベントです（サイト実装）。",
        "カスタム: trial_start",
        "有料化ファネルの中間です。",
        ga4_event="trial_start",
        sample="780",
        hint="トライアル開始",
    ),
    "ev_pay_start": _h(
        "event",
        "pay_start",
        "決済・有料開始に進んだときのイベントです（サイト実装）。",
        "カスタム: pay_start",
        "登録→課金の意欲を見ます。",
        ga4_event="pay_start",
        sample="702",
        hint="決済開始",
    ),
    "ev_pay_success": _h(
        "event",
        "pay_success",
        "支払いが完了したときのイベントです（サイト実装）。",
        "カスタム: pay_success",
        "業務の新規有料と突き合わせます。",
        ga4_event="pay_success",
        sample="341",
        hint="支払い完了",
    ),
    "ev_apply_complete": _h(
        "event",
        "apply_complete",
        "申し込み・応募が完了したときのイベントです（サイト実装）。",
        "カスタム: apply_complete",
        "採用・講座などの主転換に使います。",
        ga4_event="apply_complete",
        sample="—",
        hint="申込完了",
    ),
    "ev_contact": _h(
        "event",
        "contact",
        "問い合わせ送信などのイベントです（サイト実装）。",
        "カスタム: contact",
        "リード系の主転換候補です。",
        ga4_event="contact",
        sample="—",
        hint="問い合わせ",
    ),
    "ev_book_appointment": _h(
        "event",
        "book_appointment",
        "予約が完了したときのイベントです（サイト実装）。",
        "カスタム / 推奨寄り: book_appointment",
        "来店・面談型の主転換です。",
        ga4_event="book_appointment",
        sample="—",
        hint="予約完了",
    ),
    # ── Business ───────────────────────────────────────────────────
    "members_db": _h(
        "business",
        "会員数（DB）",
        "会社の会員データベース上で、いま有効な会員の累計です。\n"
        "GAのUUや登録イベントとは別物です。ログインできるアカウント数に近いイメージです。",
        "業務DB: COUNT(有効会員)",
        "GAの新規登録合計と大きくズレたら、計測漏れ・退会反映・テストアカウントを疑います。",
        sample="41,934",
        hint="有効会員の累計",
    ),
    "paid_members": _h(
        "business",
        "有料会員数（DB）",
        "いま有料プランに入っている会員数です。\n無料会員は含みません。収益の土台になる人数です。",
        "業務DB: COUNT(有料かつ有効な会員)",
        "総会員が増えても有料が横ばいなら、獲得はできても収益化が追いついていません。",
        sample="3,280",
        hint="有料プラン中",
    ),
    "free_members": _h(
        "business",
        "無料会員数（DB）",
        "有料ではない会員の人数です。\n会員数から有料会員を引いた残り、というイメージです。",
        "会員数（DB） − 有料会員数（DB）",
        "無料だけ増えて有料化率が下がるときは、無料範囲が広すぎるか有料の魅力が弱い可能性があります。",
        sample="38,654",
        hint="会員 − 有料",
    ),
    "paid_rate": _h(
        "business",
        "有料化率",
        "全会員のうち、有料会員がどれだけかを示す割合です。\n「会員の何%がお金を払っているか」です。",
        "有料会員数 ÷ 会員数 × 100",
        "低いときは料金設計・無料範囲・有料の価値訴求を見直します。",
        sample="7.8%",
        hint="有料 ÷ 会員",
    ),
    "new_paid": _h(
        "business",
        "新規有料（期間）",
        "この期間に、初めて有料になった会員の人数です。\n"
        "サイトの pay_success イベント件数と近いこともありますが、返金・手動登録でズレます。",
        "業務DB: COUNT(期間中に初回課金した会員)",
        "デジタルの有料完了と並べて、計測と実契約のズレを確認します。",
        sample="312",
        hint="初回課金",
    ),
    "churn": _h(
        "business",
        "退会数 / 解約",
        "期間中に退会・解約した人数です（件数）。\n割合で見るときは「解約率」カードを使います。",
        "業務DB: COUNT(期間中に退会/解約した会員)",
        "新規登録より退会が多い週は、集客より定着・解約理由の確認を優先します。",
        sample="168",
        hint="期間中件数",
    ),
    "churn_rate": _h(
        "business",
        "解約率",
        "いまの会員規模に対して、期間中にどれだけ解約したかの目安です。\n"
        "このパックでは簡易に「退会数 ÷ 期末会員数 × 100」で示します。",
        "退会数 ÷ 会員数（DB） × 100",
        "件数だけ見ると会員が多いほど大きく見えるので、率もセットで見ます。高いほど流出がきついです。",
        sample="0.40%",
        hint="退会 ÷ 会員",
    ),
    "revenue": _h(
        "business",
        "売上（期間）",
        "期間中の課金売上です。会計や決済システムの数字を使います。\n"
        "GAのイベント金額とは別で、返金・税・計上タイミングで差が出ます。",
        "業務DB/課金: SUM(期間中の売上)",
        "有料完了イベントと売上がズレるなら、返金・未計上・手動請求を確認します。",
        sample="¥7,240,000",
        hint="課金売上",
    ),
    "arpu": _h(
        "business",
        "ARPU",
        "会員1人あたりの期間売上です（Average Revenue Per User）。\n無料会員も含めた「全体平均」です。",
        "売上 ÷ 会員数（DB）",
        "有料化率や単価が上がると伸びます。会員だけ増えて売上が弱いと下がります。",
        sample="¥173",
        hint="売上 ÷ 全会員",
    ),
    "arppu": _h(
        "business",
        "ARPPU",
        "有料会員1人あたりの期間売上です（Average Revenue Per Paying User）。\n払っている人だけの平均単価イメージです。",
        "売上 ÷ 有料会員数",
        "プラン単価・アップセルの効きを見るときに使います。ARPUより高くなるのが普通です。",
        sample="¥2,207",
        hint="売上 ÷ 有料",
    ),
    "mrr": _h(
        "business",
        "MRR",
        "月次経常収益（Monthly Recurring Revenue）です。\nサブスクの「毎月入ってくる」売上のイメージです。",
        "業務DB: 有効な定期課金の月額合計",
        "新規MRR・解約MRR・拡大MRRに分解すると改善点がはっきりします。",
        sample="—",
        hint="月次経常",
    ),
    "arr": _h(
        "business",
        "ARR",
        "年次経常収益（Annual Recurring Revenue）です。\nだいたい MRR × 12 のイメージです。",
        "MRR × 12（または年契約の年額換算）",
        "B2Bや年払いが多いときに使います。",
        sample="—",
        hint="年次経常",
    ),
    "ltv": _h(
        "business",
        "LTV",
        "顧客生涯価値の目安です。\n1人の顧客が取引期間全体でもたらす利益・売上のイメージです。",
        "例: ARPU ÷ 解約率（簡易）など ※定義は会社ごと",
        "獲得単価（CAC）と比較して、取りにいけるかを判断します。",
        sample="—",
        hint="生涯価値",
    ),
    "cac": _h(
        "business",
        "CAC",
        "顧客獲得単価です。\n新規1人を獲得するのにかかった費用の目安です。",
        "期間の獲得費用 ÷ 新規顧客数",
        "LTV / CAC が健全かセットで見ます。",
        sample="—",
        hint="獲得単価",
    ),
    "nrr": _h(
        "business",
        "NRR",
        "売上維持率（Net Revenue Retention）の目安です。\n既存顧客からの売上の増減を見ます。",
        "（期末既存売上）÷（期初既存売上）など ※定義は会社ごと",
        "100%超はアップセルが解約を上回っているサインです。",
        sample="—",
        hint="売上維持",
    ),
    "orders_db": _h(
        "business",
        "注文件数（DB）",
        "業務・受注システム上の注文件数です。\nGAの purchase とは別物です。",
        "業務DB: COUNT(期間中の注文)",
        "GA購入件数とズレたら計測と実注文の差を確認します。",
        sample="—",
        hint="実注文",
    ),
    "aov_db": _h(
        "business",
        "平均注文単価（DB）",
        "1注文あたりの平均金額です（業務データ）。",
        "売上 ÷ 注文件数",
        "アップセル・セット販売の効きを見るときに使います。",
        sample="—",
        hint="客単価",
    ),
    "leads_db": _h(
        "business",
        "リード数（DB）",
        "CRM上の新規リード件数です。\nフォーム送信イベントとは承認・名寄せでズレます。",
        "業務DB/CRM: COUNT(期間中の新規リード)",
        "デジタルの問い合わせ完了と並べて品質を見ます。",
        sample="—",
        hint="CRMリード",
    ),
    "sql_rate": _h(
        "business",
        "SQL化率",
        "リードのうち、営業が追う案件（SQL）になった割合です。",
        "SQL数 ÷ リード数 × 100",
        "低いときは流入の質か、リード定義の甘さを疑います。",
        sample="—",
        hint="リード→SQL",
    ),
    "win_rate": _h(
        "business",
        "受注率",
        "提案・商談のうち受注した割合です。",
        "受注数 ÷ 商談数 × 100",
        "サイトCVRの先にある「営業の転換」です。",
        sample="—",
        hint="商談→受注",
    ),
    # ── Meta / board chrome ────────────────────────────────────────
    "data_kinds": _h(
        "meta",
        "デジタルデータと業務データ",
        "同じ「会員」でも、見る場所が違うと数字が違います。\n"
        "デジタルはブラウザ計測、業務は契約・DBです。両方を並べるのはズレを見つけるためです。",
        "デジタル = GA4等\n業務 = 会員DB・売上など",
        "どちらか一方だけ信じるより、差が出た週に原因を探す使い方がおすすめです。",
        palette=False,
    ),
    "benchmark": _h(
        "meta",
        "業界目安と矢印",
        "この業界パックで決めた「だいたいこのあたり」の目安帯です。\n"
        "公開統計の厳密な平均ではなく、パック標準の目安です。",
        "▼ 目安より下\n● 目安の範囲内\n▲ 目安より上\nカード内「業界目安」= パック標準帯の数値",
        "矢印は位置の目印です。最終判断は目安数値と、自社の前期間比較をセットで見ます。",
        palette=False,
    ),
    "events_section": _h(
        "meta",
        "イベント（説明と件数）",
        "サイト上の具体的な行動（登録・決済開始など）の説明と、期間中の発生回数です。\n"
        "CVRや業界目安は上のKPIカード側で見ます。ここは「何が何回起きたか」の明細です。",
        "イベント説明（パック固定）\n件数 = 期間中の発生回数",
        "カテゴリ（主転換・利用・課金など）ごとに見ます。主転換マークが、このパックの成功定義です。",
        palette=False,
    ),
    "prev_period": _h(
        "meta",
        "自社の前期比",
        "同じ長さの直前期間と比べた増減です。\n業界目安とは別の「自社の勢い」の物差しです。",
        "今期 − 前期（率は pt、件数は %）",
        "目安内でも前期より悪化していれば、先に原因を見ます。",
        palette=False,
    ),
    "watch_now": _h(
        "meta",
        "今見るべきこと",
        "業界目安からいちばん外れている指標を最大3つ出します。\n"
        "外れていなければ「今は大きく外れている指標はありません」と出します。",
        "目安差の大きい順（悪化優先）",
        "埋め草で埋めません。何もなければそれで安心材料です。",
        palette=False,
    ),
    "behavior_flow": _h(
        "meta",
        "行動フロー",
        "サイトに来た人から主転換までのステップを、人数と次へ進む割合でつなぎます。\n"
        "いちばん落ちている矢印がボトルネックの候補です。",
        "各ステップのユーザー数 / 来た人の % / 次へ・離脱 %",
        "チャネルを切り替えると、流入ごとの落ち方が見えます。",
        palette=False,
    ),
}


# Preferred glossary / narrative order within kinds
_ORDER_DIGITAL = [
    "uu", "total_users", "new_users", "returning_users", "sessions", "engaged_sessions",
    "sessions_per_uu", "pageviews", "pages_per_uu", "pages_session", "views_per_user",
    "new_return", "engaged", "bounce_rate", "avg_time", "user_engagement_duration",
    "engaged_sessions_per_user", "events_per_session", "event_count", "conversions",
    "key_events", "dau", "wau", "mau", "dau_mau", "scrolled_users", "file_downloads",
    "total_revenue", "purchase_revenue", "ecommerce_purchases", "item_revenue",
    "add_to_carts", "checkouts", "cart_to_view_rate", "purchase_to_view_rate",
    "average_purchase_revenue", "transactions",
    "signups", "signup_cvr", "session_cvr", "pay_start", "signup_to_pay", "pay_success",
    "lead_cvr", "apply_cvr", "booking_cvr", "purchase_cvr", "form_start_rate",
    "form_complete_rate",
]
_ORDER_TRAFFIC = [
    "channels", "ch_organic_search", "ch_direct", "ch_paid_search", "ch_paid_social",
    "ch_organic_social", "ch_referral", "ch_email", "ch_affiliates", "ch_display",
    "ch_cross_network", "ch_unassigned",
]
_ORDER_EVENT = [
    "ev_session_start", "ev_first_visit", "ev_page_view", "ev_user_engagement",
    "ev_scroll", "ev_click", "ev_view_search_results", "ev_file_download",
    "ev_form_start", "ev_form_submit", "ev_view_item", "ev_view_item_list",
    "ev_select_item", "ev_add_to_cart", "ev_remove_from_cart", "ev_view_cart",
    "ev_begin_checkout", "ev_add_shipping_info", "ev_add_payment_info",
    "ev_purchase", "ev_refund", "ev_sign_up", "ev_login", "ev_search", "ev_share",
    "ev_generate_lead", "ev_view_promotion", "ev_select_promotion",
    "ev_view_pricing", "ev_trial_start", "ev_pay_start", "ev_pay_success",
    "ev_apply_complete", "ev_contact", "ev_book_appointment",
]
_ORDER_BUSINESS = [
    "members_db", "paid_members", "free_members", "paid_rate", "new_paid",
    "churn", "churn_rate", "revenue", "arpu", "arppu", "mrr", "arr", "ltv", "cac",
    "nrr", "orders_db", "aov_db", "leads_db", "sql_rate", "win_rate",
]
_ORDER_META = [
    "data_kinds", "benchmark", "prev_period", "watch_now", "behavior_flow",
    "events_section",
]

# 詳しい数字 v3: rows that came with the 8週の推移 / デバイス additions
HELP.update({
    "avg_session_duration": _h(
        "digital",
        "平均セッション時間",
        "1回の訪問（セッション）の長さの平均です。\n"
        "「平均エンゲージメント時間」と違い、画面が裏にあった時間も入ります。",
        "GA4: averageSessionDuration",
        "長いほど良いとは限りません。迷って長くなっていないか、ページ / セッションとセットで見ます。",
        ga4_api="averageSessionDuration",
        sample="2:47",
        hint="1回の訪問の長さ",
    ),
    "device_mobile": _h(
        "digital",
        "モバイル",
        "スマホからの訪問です。値は全セッションに占める割合、下に セッション数 と CVR を出します。",
        "GA4: deviceCategory = mobile のセッション ÷ 全セッション × 100",
        "モバイルの CVR が PC の半分以下なら、スマホの入力フォームや購入手続きを疑います。",
        palette=False,
    ),
    "device_desktop": _h(
        "digital",
        "PC",
        "パソコンからの訪問です。値は全セッションに占める割合です。",
        "GA4: deviceCategory = desktop のセッション ÷ 全セッション × 100",
        "B2B や高単価の商品では PC の比率と CVR が高くなりがちです。モバイルと並べて差を見ます。",
        palette=False,
    ),
    "device_tablet": _h(
        "digital",
        "タブレット",
        "タブレットからの訪問です。値は全セッションに占める割合です。",
        "GA4: deviceCategory = tablet のセッション ÷ 全セッション × 100",
        "割合が小さいうちは CVR の上下が大きく出ます。件数とセットで見ます。",
        palette=False,
    ),
    "trend_8w": _h(
        "meta",
        "8週の推移",
        "直近8週の週ごとの値を線にしたものです。右端がいちばん新しい週です。",
        "GA4: 直近56日を週ごと（nthWeek）に集計",
        "前期比だけでは1回の上下か、続いている向きかが分かりません。線の向きが続いているかを先に見ます。",
        palette=False,
    ),
})

ORDER_BY_KIND: dict[str, list[str]] = {
    "digital": _ORDER_DIGITAL,
    "traffic": _ORDER_TRAFFIC,
    "event": _ORDER_EVENT,
    "business": _ORDER_BUSINESS,
    "meta": _ORDER_META,
}


def resolve_id(key: str) -> str:
    return ALIASES.get(key, key)


def get_help(key: str, locale: str = "ja") -> dict[str, Any] | None:
    """Return HELP entry with title/meaning/formula/tip/hint for locale (ja/en/ko)."""
    from sitekpi.i18n import normalize_locale
    from sitekpi.i18n.help_l10n import localize_entry

    base = HELP.get(resolve_id(key))
    if not base:
        return None
    return localize_entry(resolve_id(key), base, normalize_locale(locale))


def localized_kinds(locale: str = "ja") -> dict[str, dict[str, str]]:
    from sitekpi.i18n import normalize_locale
    from sitekpi.i18n.help_l10n import localize_kinds

    return localize_kinds(KINDS, normalize_locale(locale))


def ordered_keys(kind: str | None = None) -> list[str]:
    if kind:
        preferred = ORDER_BY_KIND.get(kind, [])
        rest = [k for k, h in HELP.items() if h.get("kind") == kind and k not in preferred]
        return [k for k in preferred if k in HELP] + rest
    keys: list[str] = []
    seen: set[str] = set()
    for k in KINDS:
        for key in ordered_keys(k):
            if key not in seen:
                keys.append(key)
                seen.add(key)
    for key in HELP:
        if key not in seen:
            keys.append(key)
    return keys


def _hint_of(h: dict[str, Any]) -> str:
    if h.get("hint"):
        return str(h["hint"])
    meaning = str(h.get("meaning") or "")
    return meaning.split("\n", 1)[0][:80]


def palette_widgets(*, sample: bool = True, locale: str = "ja") -> list[dict[str, Any]]:
    """Builder palette entries derived from HELP (palette≠False)."""
    widgets: list[dict[str, Any]] = []
    for key in ordered_keys():
        raw = HELP[key]
        if raw.get("palette") is False:
            continue
        kind = str(raw.get("kind") or "digital")
        # meta never on palette
        if kind == "meta":
            continue
        h = get_help(key, locale) or raw
        group = {"digital": "digital", "business": "business", "traffic": "traffic", "event": "event"}.get(
            kind, "digital"
        )
        val = raw.get("sample") if sample else "—"
        widgets.append(
            {
                "id": key,
                "group": group,
                "label": h["title"],
                "value": val if val is not None else "—",
                "hint": _hint_of(h),
                "ga4_api": raw.get("ga4_api"),
                "ga4_event": raw.get("ga4_event"),
            }
        )
    return widgets


def ga4_apis_for_palette() -> list[str]:
    """Unique GA4 metric API names used by HELP digital entries."""
    seen: set[str] = set()
    out: list[str] = []
    for key in ordered_keys("digital"):
        api = HELP[key].get("ga4_api")
        if api and api not in seen:
            seen.add(api)
            out.append(str(api))
    return out


def ga4_events_for_palette() -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for key in ordered_keys("event"):
        ev = HELP[key].get("ga4_event")
        if ev and ev not in seen:
            seen.add(ev)
            out.append(str(ev))
    return out


# Channel label (GA4) → HELP id
CHANNEL_IDS: dict[str, str] = {
    "Organic Search": "ch_organic_search",
    "Direct": "ch_direct",
    "Paid Search": "ch_paid_search",
    "Paid Social": "ch_paid_social",
    "Organic Social": "ch_organic_social",
    "Referral": "ch_referral",
    "Email": "ch_email",
    "Affiliates": "ch_affiliates",
    "Display": "ch_display",
    "Cross-network": "ch_cross_network",
    "Unassigned": "ch_unassigned",
}
