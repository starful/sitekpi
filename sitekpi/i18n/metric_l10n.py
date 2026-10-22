"""Shared metric labels + help templates (ja / en / ko). Pack-specific → pack_l10n."""

from __future__ import annotations

from typing import Any

from sitekpi.i18n import normalize_locale

# Shared spoken labels (audience / engage / summary commons)
SHARED_LABELS: dict[str, dict[str, str]] = {
    "uu": {"ja": "期間 UU", "en": "Active users", "ko": "기간 UU"},
    "sessions": {"ja": "セッション", "en": "Sessions", "ko": "세션"},
    "engaged": {"ja": "エンゲージ率", "en": "Engagement rate", "ko": "참여율"},
    "engaged_title": {
        "ja": "エンゲージメント率",
        "en": "Engagement rate",
        "ko": "참여율",
    },
    "bounce_like": {
        "ja": "すぐ離脱に近い率",
        "en": "Near-bounce rate",
        "ko": "이탈에 가까운 율",
    },
    "pages_session": {
        "ja": "ページ / セッション",
        "en": "Pages / session",
        "ko": "페이지 / 세션",
    },
    "pv_uu": {"ja": "PV / UU", "en": "PV / UU", "ko": "PV / UU"},
    "pv": {"ja": "PV", "en": "PV", "ko": "PV"},
    "avg_time": {
        "ja": "平均エンゲージ時間",
        "en": "Avg. engagement time",
        "ko": "평균 참여 시간",
    },
    "new_return": {
        "ja": "新規 / 再訪",
        "en": "New / returning",
        "ko": "신규 / 재방문",
    },
    "sessions_per_uu": {
        "ja": "セッション / UU",
        "en": "Sessions / UU",
        "ko": "세션 / UU",
    },
}

# Help bodies keyed by metric id → field → locale
SHARED_HELP: dict[str, dict[str, dict[str, str]]] = {
    "uu": {
        "meaning": {
            "ja": "期間中にサイトを訪れた人の数（ブラウザ単位）です。",
            "en": "People who visited the site in the period (browser-based).",
            "ko": "기간 중 사이트를 방문한 사람 수(브라우저 단위)입니다.",
        },
        "formula": {
            "ja": "GA4: activeUsers（期間）",
            "en": "GA4: activeUsers (period)",
            "ko": "GA4: activeUsers(기간)",
        },
        "tip": {
            "ja": "増えても{cvr_label}が弱いときは、集客の質を疑います。",
            "en": "If this rises but {cvr_label} stays weak, question traffic quality.",
            "ko": "늘어도 {cvr_label}이 약하면 유입 질을 의심하세요.",
        },
    },
    "sessions": {
        "meaning": {
            "ja": "サイトを開いた回数です。同じ人が何度来ても加算されます。",
            "en": "Visits to the site. The same person can add multiple sessions.",
            "ko": "사이트를 연 횟수입니다. 같은 사람이 여러 번 와도 합산됩니다.",
        },
        "formula": {
            "ja": "GA4: sessions",
            "en": "GA4: sessions",
            "ko": "GA4: sessions",
        },
        "tip": {
            "ja": "UUとの比（セッション / UU）で再訪の多さを見ます。",
            "en": "Use sessions / UU to gauge return frequency.",
            "ko": "UU와의 비(세션 / UU)로 재방문 정도를 봅니다.",
        },
    },
    "engaged": {
        "meaning": {
            "ja": "すぐ閉じずに内容を見た訪問の割合です。",
            "en": "Share of visits that engaged instead of leaving immediately.",
            "ko": "바로 닫지 않고 내용을 본 방문 비율입니다.",
        },
        "formula": {
            "ja": "GA4: engagementRate（×100）",
            "en": "GA4: engagementRate (×100)",
            "ko": "GA4: engagementRate(×100)",
        },
        "tip": {
            "ja": "流入チャネル別に見ると、広告の質の差が出やすいです。",
            "en": "By channel, ad quality differences show up clearly.",
            "ko": "유입 채널별로 보면 광고 질 차이가 잘 드러납니다.",
        },
    },
    "bounce_like": {
        "meaning": {
            "ja": "エンゲージメントしなかった訪問のイメージです。",
            "en": "Rough share of visits that did not engage.",
            "ko": "참여하지 않은 방문의 대략적인 비율입니다.",
        },
        "formula": {
            "ja": "100 − エンゲージメント率",
            "en": "100 − engagement rate",
            "ko": "100 − 참여율",
        },
        "tip": {
            "ja": "低いほど良い、という読み方で足ります。",
            "en": "Lower is better — that reading is enough.",
            "ko": "낮을수록 좋다는 읽기면 충분합니다.",
        },
    },
    "pages_session": {
        "meaning": {
            "ja": "1回の訪問で見るページ数です。",
            "en": "Pages viewed per visit.",
            "ko": "한 번 방문에서 보는 페이지 수입니다.",
        },
        "formula": {
            "ja": "screenPageViewsPerSession",
            "en": "screenPageViewsPerSession",
            "ko": "screenPageViewsPerSession",
        },
        "tip": {
            "ja": "低いとランディングで終わっている可能性。",
            "en": "Low values often mean visits end on the landing page.",
            "ko": "낮으면 랜딩에서 끝나는 경우가 많습니다.",
        },
    },
    "pv_uu": {
        "meaning": {
            "ja": "1人あたり何ページ見たか。",
            "en": "Pages viewed per person.",
            "ko": "1인당 몇 페이지를 봤는지.",
        },
        "formula": {
            "ja": "PV ÷ UU",
            "en": "PV ÷ UU",
            "ko": "PV ÷ UU",
        },
        "tip": {
            "ja": "深さと主転換の矛盾を見つけるのに使います。",
            "en": "Use it to spot depth vs primary-conversion mismatches.",
            "ko": "깊이와 주전환의 모순을 찾는 데 씁니다.",
        },
    },
    "pv": {
        "meaning": {
            "ja": "ページが表示された回数です。",
            "en": "How many times pages were viewed.",
            "ko": "페이지가 표시된 횟수입니다.",
        },
        "formula": {
            "ja": "screenPageViews",
            "en": "screenPageViews",
            "ko": "screenPageViews",
        },
        "tip": {
            "ja": "PVだけ見て判断せず、UU・エンゲージとセットで。",
            "en": "Don’t judge on PV alone — pair with UU and engagement.",
            "ko": "PV만 보고 판단하지 말고 UU·참여와 함께 보세요.",
        },
    },
    "avg_time": {
        "meaning": {
            "ja": "意識を向けていた時間の目安です。",
            "en": "Rough time users actually paid attention.",
            "ko": "실제로 주의를 기울인 시간의 대략치입니다.",
        },
        "formula": {
            "ja": "エンゲージ時間 ÷ UU（概算）",
            "en": "Engagement time ÷ UU (approx.)",
            "ko": "참여 시간 ÷ UU(대략)",
        },
        "tip": {
            "ja": "業種で水準が違います。CVRとセットで見ます。",
            "en": "Benchmarks differ by industry — pair with CVR.",
            "ko": "업종마다 수준이 다릅니다. CVR과 함께 보세요.",
        },
    },
    "new_return": {
        "meaning": {
            "ja": "期間UUのうち新規と再訪の割合です。業界目安は新規%側です。",
            "en": "New vs returning share of period UU. Industry std. uses new %.",
            "ko": "기간 UU 중 신규와 재방문 비율입니다. 업계 기준은 신규% 쪽입니다.",
        },
        "formula": {
            "ja": "新規% = newUsers ÷ UU × 100",
            "en": "New % = newUsers ÷ UU × 100",
            "ko": "신규% = newUsers ÷ UU × 100",
        },
        "tip": {
            "ja": "新規ばかり増えて再訪が落ちるときは定着を疑います。",
            "en": "If new rises while returning falls, question retention.",
            "ko": "신규만 늘고 재방문이 떨어지면 정착을 의심하세요.",
        },
    },
    "sessions_per_uu": {
        "meaning": {
            "ja": "1人あたり何回訪れたか。",
            "en": "Visits per person.",
            "ko": "1인당 몇 번 방문했는지.",
        },
        "formula": {
            "ja": "セッション ÷ UU",
            "en": "Sessions ÷ UU",
            "ko": "세션 ÷ UU",
        },
        "tip": {
            "ja": "高いほど再訪が多い傾向です。",
            "en": "Higher usually means more return visits.",
            "ko": "높을수록 재방문이 많은 경향입니다.",
        },
    },
}

# Dynamic help templates (format kwargs)
HELP_TMPL: dict[str, dict[str, dict[str, str]]] = {
    "signup_cvr": {
        "meaning": {
            "ja": "期間UUのうち、{signup_label}（{primary}）まで進んだ割合です。",
            "en": "Share of period UU that reached {signup_label} ({primary}).",
            "ko": "기간 UU 중 {signup_label}({primary})까지 간 비율입니다.",
        },
        "formula": {
            "ja": "{cvr_label} = {primary} ÷ UU × 100",
            "en": "{cvr_label} = {primary} ÷ UU × 100",
            "ko": "{cvr_label} = {primary} ÷ UU × 100",
        },
        "tip": {
            "ja": "低いときはファネル上流の離脱をイベントで追います。",
            "en": "When low, chase upstream drop-offs in events.",
            "ko": "낮을 때는 퍼널 상류 이탈을 이벤트로 추적하세요.",
        },
    },
    "primary": {
        "meaning": {
            "ja": "この業界パックの主転換です。イベント名は {primary} です。",
            "en": "Primary conversion for this pack. Event id: {primary}.",
            "ko": "이 업계 팩의 주전환입니다. 이벤트명: {primary}.",
        },
        "formula": {
            "ja": "eventCount（{primary}）",
            "en": "eventCount ({primary})",
            "ko": "eventCount({primary})",
        },
        "tip": {
            "ja": "チームで成功の定義をこの指標名にそろえます。",
            "en": "Align the team’s success definition on this metric name.",
            "ko": "팀의 성공 정의를 이 지표명에 맞추세요.",
        },
    },
    "pay_start": {
        "meaning": {
            "ja": "{mid_label}の回数です。イベント名は {mid_event} です。",
            "en": "Count of {mid_label}. Event id: {mid_event}.",
            "ko": "{mid_label} 횟수입니다. 이벤트명: {mid_event}.",
        },
        "formula": {
            "ja": "eventCount（{mid_event}）",
            "en": "eventCount ({mid_event})",
            "ko": "eventCount({mid_event})",
        },
        "tip": {
            "ja": "開始は多いのに完了が少ないときはフォーム・導線を疑います。",
            "en": "Many starts, few completes → check forms and paths.",
            "ko": "시작은 많은데 완료가 적으면 폼·동선을 의심하세요.",
        },
    },
    "rate_a": {
        "meaning": {
            "ja": "{signup_label}のあとに次ステップへ進んだ割合です。",
            "en": "Share that moved to the next step after {signup_label}.",
            "ko": "{signup_label} 이후 다음 단계로 간 비율입니다.",
        },
        "tip": {
            "ja": "オンボーディングや次導線の健康度を見ます。",
            "en": "Watch onboarding / next-step path health.",
            "ko": "온보딩·다음 동선 건강도를 봅니다.",
        },
    },
    "rate_b": {
        "meaning": {
            "ja": "開始から完了までの歩留まりです。",
            "en": "Yield from start to complete.",
            "ko": "시작부터 완료까지의 수율입니다.",
        },
        "tip": {
            "ja": "低いときはフォーム・決済・必須項目を疑います。",
            "en": "When low, check forms, payment, and required fields.",
            "ko": "낮을 때는 폼·결제·필수 항목을 의심하세요.",
        },
    },
    "bottom": {
        "meaning": {
            "ja": "{bottom_label}の件数です（{bottom_event}）。",
            "en": "Count of {bottom_label} ({bottom_event}).",
            "ko": "{bottom_label} 건수입니다({bottom_event}).",
        },
        "formula": {
            "ja": "eventCount（{bottom_event}）",
            "en": "eventCount ({bottom_event})",
            "ko": "eventCount({bottom_event})",
        },
        "tip": {
            "ja": "業務DBの対応指標と並べてズレを確認します。",
            "en": "Compare with the matching business-DB metric for gaps.",
            "ko": "업무 DB 대응 지표와 나란히 보고 차이를 확인하세요.",
        },
    },
    "event": {
        "meaning": {
            "ja": "イベント {name} の発生回数です。",
            "en": "How many times event {name} fired.",
            "ko": "이벤트 {name} 발생 횟수입니다.",
        },
        "meaning_primary": {
            "ja": "イベント {name} の発生回数です。 この業界の主転換（{signup_label}）です。",
            "en": "How many times event {name} fired. Primary conversion ({signup_label}) for this pack.",
            "ko": "이벤트 {name} 발생 횟수입니다. 이 업계의 주전환({signup_label})입니다.",
        },
        "formula": {
            "ja": "GA4 eventName = {name}",
            "en": "GA4 eventName = {name}",
            "ko": "GA4 eventName = {name}",
        },
        "tip": {
            "ja": "件数の前後関係でファネルの落ちを見ます。",
            "en": "Use count order to spot funnel drops.",
            "ko": "건수 전후 관계로 퍼널 낙차를 봅니다.",
        },
    },
    "channel": {
        "meaning": {
            "ja": "流入チャネル {name} のセッション構成比です。",
            "en": "Session mix for channel {name}.",
            "ko": "유입 채널 {name}의 세션 구성비입니다.",
        },
        "formula": {
            "ja": "sessionDefaultChannelGroup の構成比",
            "en": "sessionDefaultChannelGroup mix",
            "ko": "sessionDefaultChannelGroup 구성비",
        },
        "tip": {
            "ja": "主転換・エンゲージ率とセットで質を見ます。",
            "en": "Pair with primary conversion and engagement for quality.",
            "ko": "주전환·참여율과 함께 질을 봅니다.",
        },
    },
    "biz_suffix": {
        "ja": " 未連携時はデモ数字で埋めません。",
        "en": " When unlinked, we do not fill with demo numbers.",
        "ko": " 미연동 시 데모 숫자로 채우지 않습니다.",
    },
    "biz_tip": {
        "ja": "GA4の主転換と並べてズレを確認します。",
        "en": "Compare with the GA4 primary conversion for gaps.",
        "ko": "GA4 주전환과 나란히 보고 차이를 확인하세요.",
    },
}

BOARD_TMPL: dict[str, dict[str, str]] = {
    "focus_line": {
        "ja": "重点 · {names}（主転換: {signup}）",
        "en": "Focus · {names} (Primary: {signup})",
        "ko": "중점 · {names} (주전환: {signup})",
    },
    "focus_line_simple": {
        "ja": "主転換: {signup}",
        "en": "Primary: {signup}",
        "ko": "주전환: {signup}",
    },
    "point_n": {
        "ja": "ポイント {n}",
        "en": "Point {n}",
        "ko": "포인트 {n}",
    },
    "biz_unlinked_title": {
        "ja": "業務KPIは未連携",
        "en": "Business KPIs unlinked",
        "ko": "업무 KPI 미연동",
    },
    "biz_unlinked_body": {
        "ja": "業務DBをつなぐと、主転換イベントと実数のズレが見えます。",
        "en": "Link a business DB to see gaps vs the primary conversion event.",
        "ko": "업무 DB를 연결하면 주전환 이벤트와 실수 차이를 볼 수 있습니다.",
    },
}


def _pick(row: dict[str, str] | None, locale: str, fallback: str = "") -> str:
    if not row:
        return fallback
    loc = normalize_locale(locale)
    return str(row.get(loc) or row.get("ja") or fallback)


def shared_label(key: str, locale: str) -> str:
    return _pick(SHARED_LABELS.get(key), locale, key)


def shared_help(
    key: str, locale: str, *, title: str | None = None, **fmt: Any
) -> dict[str, str]:
    loc = normalize_locale(locale)
    block = SHARED_HELP.get(key) or {}
    out_title = title or shared_label(key, loc)
    meaning = _pick(block.get("meaning"), loc)
    formula = _pick(block.get("formula"), loc)
    tip = _pick(block.get("tip"), loc)
    if fmt:
        try:
            meaning = meaning.format(**fmt)
            formula = formula.format(**fmt)
            tip = tip.format(**fmt)
        except (KeyError, ValueError):
            pass
    return {
        "title": out_title,
        "kind": "digital",
        "meaning": meaning,
        "formula": formula,
        "tip": tip,
    }


def tmpl(group: str, field: str, locale: str, **fmt: Any) -> str:
    loc = normalize_locale(locale)
    block = HELP_TMPL.get(group) or {}
    raw = block.get(field)
    if isinstance(raw, dict):
        text = _pick(raw, loc)
    else:
        text = ""
    if fmt and text:
        try:
            return text.format(**fmt)
        except (KeyError, ValueError):
            return text
    return text


def board_tmpl(key: str, locale: str, **fmt: Any) -> str:
    loc = normalize_locale(locale)
    text = _pick(BOARD_TMPL.get(key), loc)
    if fmt and text:
        try:
            return text.format(**fmt)
        except (KeyError, ValueError):
            return text
    return text


def help_dict(
    title: str,
    *,
    kind: str,
    meaning: str,
    formula: str,
    tip: str,
) -> dict[str, str]:
    return {
        "title": title,
        "kind": kind,
        "meaning": meaning,
        "formula": formula,
        "tip": tip,
    }
