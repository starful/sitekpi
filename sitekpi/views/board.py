"""KPI board page (dense hierarchy + 説明 popups).

Python here only shapes data: numbers, 業界目安 positions, chart points.
All markup lives in templates/board.html + templates/board/_macros.html,
styles in static/css/board.css, behaviour in static/js/board.js.
"""

from __future__ import annotations

from contextvars import ContextVar
from typing import Any

from sitekpi.board.data import build_dense_board
from sitekpi.i18n import normalize_locale, t
from sitekpi.templating import render
from sitekpi.views.layout import rail_context

_KIND_KEYS = {
    "digital": "kind.digital",
    "event": "kind.event",
    "traffic": "kind.traffic",
    "business": "kind.business",
}
# Fallback labels when a kind has no i18n key
KINDS = {
    "digital": "デジタル",
    "event": "イベント",
    "traffic": "流入",
    "business": "業務",
}

# Active pack benches / locale for the render in progress. ContextVars (not
# module globals) so concurrent requests rendering different packs can't mix 業界目安.
_ACTIVE_BENCH: ContextVar[dict[str, dict[str, Any]]] = ContextVar("_ACTIVE_BENCH", default={})
_ACTIVE_LOCALE: ContextVar[str] = ContextVar("_ACTIVE_LOCALE", default="ja")

EVENT_PREVIEW = 10
_UNLINKED = (None, "", "—", "–")


def _kind_label(kind: str, locale: str) -> str:
    key = _KIND_KEYS.get(kind)
    return t(key, locale) if key else KINDS.get(kind, kind)


# --- numbers -------------------------------------------------------------

def _fmt_num(n: float, unit: str) -> str:
    if abs(n - round(n)) < 1e-9:
        body = f"{int(round(n))}"
    elif abs(n) >= 10:
        body = f"{n:.1f}".rstrip("0").rstrip(".")
    else:
        body = f"{n:.2f}".rstrip("0").rstrip(".")
    return f"{body}{unit}"


def _fmt_gap(gap: float, gap_unit: str) -> str:
    sign = "+" if gap > 0 else ""
    if gap_unit == "pt":
        return f"{sign}{gap:.1f}pt"
    if gap_unit == "%":
        return f"{sign}{gap:.1f}%"
    if abs(gap) >= 1:
        return f"{sign}{gap:.1f}"
    return f"{sign}{gap:.2f}"


def _source_text(spec: dict[str, Any], locale: str) -> str:
    if spec.get("custom"):
        return t("bench_src.custom", locale)
    src = spec.get("source") or {}
    if src.get("kind") == "blend":
        return t("bench_src.blend", locale, label=src.get("label", ""))
    if src.get("kind") == "cited":
        text = t("bench_src.cited", locale, label=src.get("label", ""))
        kind, _, n = str(src.get("rule") or "").partition(":")
        if kind == "pt":
            text += " · " + t("bench_rule.pt", locale, n=n)
        elif kind == "rel":
            text += " · " + t("bench_rule.rel", locale, n=f"{float(n) * 100:g}")
        return text
    return t("bench_src.provisional", locale)


def _bench_info(value: float | None, bench_key: str | None) -> dict[str, Any] | None:
    if not bench_key:
        return None
    spec = _ACTIVE_BENCH.get().get(bench_key)
    if not spec:
        return None
    low = float(spec["low"])
    high = float(spec["high"])
    mid = (low + high) / 2
    unit = str(spec["unit"])
    hib = bool(spec["hib"])
    gap_unit = str(spec.get("gap_unit") or unit)
    band = f"{low:g}–{high:g}{unit}"
    avg = _fmt_num(mid, unit)
    loc = _ACTIVE_LOCALE.get()
    custom = bool(spec.get("custom"))
    kind = (spec.get("source") or {}).get("kind")
    key = ("bench_title_custom" if custom else "bench_title_cited" if kind == "cited"
           else "bench_title_blend" if kind == "blend" else "bench_title")
    title = t(key, loc, band=band, avg=avg)
    title += " · " + _source_text(spec, loc)
    # 基準なし: no published figure and no target of the user's own → nothing to compare with
    none = not custom and kind not in ("cited", "blend")
    if none:
        avg, band, title = t("bench_none", loc), "", t("bench_none_title", loc)
    base: dict[str, Any] = {
        "key": bench_key,
        "none": none,
        "custom": custom,
        "band": band,
        "avg": avg,
        "title": title,
        "low": low,
        "high": high,
        "mid": mid,
        "unit": unit,
    }
    if value is None or none:
        return {
            **base,
            "gap": "—",
            "tone": "na",
            "arrow": "",
            "value": None,
        }
    gap = value - mid
    if low <= value <= high:
        arrow, tone = "●", "mid"
    elif value > high:
        arrow, tone = ("▲", "up") if hib else ("▼", "down")
    else:
        arrow, tone = ("▼", "down") if hib else ("▲", "up")
    return {
        **base,
        "gap": _fmt_gap(gap, gap_unit),
        "tone": tone,
        "arrow": arrow,
        "value": value,
    }


# --- view models (what the templates render) -----------------------------


def _judge(info: dict[str, Any] | None) -> str:
    """'up' (better than the band) / 'mid' (inside) / 'down' (worse) — '' when no 目安."""
    tone = str((info or {}).get("tone") or "")
    return tone if tone in ("up", "mid", "down") else ""


def _first_line(text: str) -> str:
    """One short sentence of 意味 for the opened row (full text stays in 説明)."""
    text = str(text or "").strip()
    for sep in ("\n", "。", ". "):
        if sep in text:
            head = text.split(sep, 1)[0].strip()
            return head + ("。" if sep == "。" else "." if sep == ". " else "")
    return text


def _bench_view(info: dict[str, Any] | None) -> dict[str, Any]:
    """業界目安 for one metric: the judge chip in the row, the numbers when the row opens.

    kind: "judge" (a cited / blended / own target → 良好・目安内・要注意),
          "none"  (基準なし — a popover says why), "na" (counts etc.: nothing to compare)."""
    if not info:
        return {"kind": "na", "key": "", "avg": "—", "gap": "—", "tone": "na", "title": "", "band": "",
                "judge": "", "custom": False, "none": False}
    none = bool(info.get("none"))
    return {
        "kind": "none" if none else "judge",
        "key": str(info.get("key") or ""),
        "avg": info["avg"],
        "gap": info["gap"],
        "tone": info["tone"],
        "title": info["title"],
        "band": info.get("band") or "",
        "judge": "" if none else _judge(info),
        "custom": bool(info.get("custom")),
        "none": none,
    }


def _metric_row(r: dict[str, Any], locale: str) -> dict[str, Any]:
    info = _bench_info(r.get("value_num"), r.get("bench"))
    return {
        "id": r["id"],
        "label": r["label"],
        # "59.6% / 40.4%" may wrap after the slash, never leave "/" alone on a line
        "value": str(r["value"]).replace(" / ", "\u00a0/ "),
        "focus": bool(r.get("focus")),
        "bench": _bench_view(info),
        "delta": str(r.get("delta") or "—"),
        "delta_tone": str(r.get("tone") or "na"),
        "meaning": _first_line((r.get("help") or {}).get("meaning") or ""),
    }


CHANNEL_TOP_N = 5
OTHER_COLOR = "#94a3b8"


def _group_channels(channels: list[dict[str, Any]], locale: str) -> list[dict[str, Any]]:
    """Top 5 channels by share + one 'その他（n）' row, so beginners scan 6 rows, not 10+."""
    if len(channels) <= CHANNEL_TOP_N + 1:
        return channels
    ranked = sorted(channels, key=lambda c: -int(c.get("pct") or 0))
    top, rest = ranked[:CHANNEL_TOP_N], ranked[CHANNEL_TOP_N:]
    names = ", ".join(str(c["name"]) for c in rest)
    label = t("channels.other", locale, n=len(rest))
    other = {
        "id": "ch_others",
        "name": label,
        "pct": sum(int(c.get("pct") or 0) for c in rest),
        "color": OTHER_COLOR,
        "help": {
            "title": label,
            "kind": "traffic",
            "meaning": t("channels.other_meaning", locale, names=names),
            "formula": t("channels.other_formula", locale),
            "tip": t("channels.other_tip", locale),
        },
    }
    return top + [other]


# --- 今見るべきこと (rule-based until step 10) -------------------------------

WATCH_MAX = 3


def _trend(r: dict[str, Any], locale: str) -> dict[str, str] | None:
    """自社の前期比 next to the 業界目安 judgement: 改善 / 悪化 / 横ばい."""
    delta, tone = str(r.get("delta") or "—"), str(r.get("tone") or "na")
    if delta == "—" or tone == "na":
        return None
    word = {"up": "trend.better", "down": "trend.worse"}.get(tone, "trend.flat")
    return {"text": delta, "tone": tone, "word": t(word, locale)}


def _watch_items(board: dict[str, Any], locale: str) -> list[dict[str, Any]]:
    """Metrics furthest outside their 業界目安: worse ones first, then better ones."""
    seen: set[str] = set()
    scored: list[tuple[int, float, dict[str, Any]]] = []
    for r in board["summary"] + board["funnel"] + board["engage"] + board["audience"]:
        key = str(r.get("bench") or "")
        if not key or key in seen:
            continue
        info = _bench_info(r.get("value_num"), key)
        if not info or info.get("value") is None or info["tone"] not in ("up", "down"):
            continue
        seen.add(key)
        v, low, high = float(info["value"]), float(info["low"]), float(info["high"])
        outside = (low - v) if v < low else (v - high)
        severity = outside / max(high - low, 1e-9)
        bad = info["tone"] == "down"
        if bad:
            title = t("watch.bad", locale, label=r["label"],
                      dir=t("watch.dir_high" if v > high else "watch.dir_low", locale))
            tip = str((r.get("help") or {}).get("tip") or "")
        else:
            title = t("watch.good", locale, label=r["label"])
            tip = t("watch.keep", locale)
        scored.append(
            (
                0 if bad else 1,
                -severity,
                {
                    "id": r["id"],
                    "label": r["label"],
                    "value": r["value"],
                    "value_num": r.get("value_num"),
                    "bench_key": key,
                    "delta": str(r.get("delta") or "—"),
                    "delta_tone": str(r.get("tone") or "na"),
                    "tone": info["tone"],
                    "title": title,
                    "avg": info["avg"],
                    "numbers": t("watch.numbers", locale, value=r["value"], avg=info["avg"],
                                 band=info["band"], gap=info["gap"]),
                    "trend": _trend(r, locale),
                    "tip": tip,
                    # far outside the band (more than its own width) → maybe the wrong 比べる業種
                    "far": severity >= 1.0,
                },
            )
        )
    scored.sort(key=lambda x: (x[0], x[1]))
    return [item for _, _, item in scored[:WATCH_MAX]]


# --- いまの状態 (L0): one sentence + three numbers ---------------------------


def _prev_view(delta: str, tone: str, locale: str) -> dict[str, str]:
    """自社の前期比 in words (改善 / 悪化 / 横ばい) with the number beside it."""
    delta = str(delta or "—")
    if delta == "—":
        return {"word": t("verdict.prev_none", locale), "text": "", "tone": "na"}
    word = {"up": "trend.better", "down": "trend.worse"}.get(tone, "trend.flat")
    return {"word": t(word, locale), "text": delta, "tone": tone if tone in ("up", "down") else "mid"}


def _tile(*, label: str, tag: str, value: str, delta: str, tone: str,
          info: dict[str, Any] | None, locale: str, note: str = "", help_id: str = "",
          issue: bool = False) -> dict[str, Any]:
    return {
        "label": label, "tag": tag, "value": value, "help_id": help_id, "issue": issue,
        "prev": _prev_view(delta, tone, locale),
        "bench": _bench_view(info),
        "note": note,
    }


def _worst_link(flow: dict[str, Any] | None) -> dict[str, Any] | None:
    for st in (flow or {}).get("stages") or []:
        link = st.get("link")
        if link and link.get("worst"):
            return link
    return None


def _verdict(board: dict[str, Any], watch: list[dict[str, Any]],
             flow: dict[str, Any] | None, locale: str) -> dict[str, Any]:
    """L0: 主転換の件数 · 主転換率 · 一番の課題 — each with 前期 and 業界 in words."""
    by_id = {r["id"]: r for r in board["summary"]}
    lines: list[str] = []
    short: list[str] = []
    tiles: list[dict[str, Any]] = []

    count = by_id.get("primary")
    if count:
        delta, tone = str(count.get("delta") or "—"), str(count.get("tone") or "na")
        key = ("verdict.count_na" if delta == "—"
               else {"up": "verdict.count_up", "down": "verdict.count_down"}.get(tone, "verdict.count_flat"))
        lines.append(t(key, locale, label=count["label"], value=count["value"], delta=delta))
        short.append(t("bx." + key.split(".", 1)[1], locale, label=count["label"], value=count["value"]))
        tiles.append(_tile(label=count["label"], tag=t("primary_tag", locale), value=count["value"],
                           delta=delta, tone=tone, info=None, locale=locale, help_id=count["id"],
                           note=t("verdict.count_note", locale)))

    rate = by_id.get("signup_cvr")
    if rate:
        info = _bench_info(rate.get("value_num"), rate.get("bench"))
        view = _bench_view(info)
        key = (f"verdict.rate_{view['judge']}" if view["kind"] == "judge" and view["judge"]
               else "verdict.rate_none")
        lines.append(t(key, locale, label=rate["label"], value=rate["value"], avg=view["avg"]))
        tiles.append(_tile(label=rate["label"], tag="", value=rate["value"],
                           delta=str(rate.get("delta") or "—"), tone=str(rate.get("tone") or "na"),
                           info=info, locale=locale, help_id=rate["id"]))

    # 一番の課題: the worst metric outside its 目安 — not the rate already shown in tile 2
    rate_key = str((rate or {}).get("bench") or "")
    bad = next((w for w in watch if w["tone"] == "down" and w["bench_key"] != rate_key), None)
    link = _worst_link(flow)
    if bad:
        info = _bench_info(bad.get("value_num"), bad["bench_key"])
        lines.append(t("verdict.issue_bench", locale, label=bad["label"], value=bad["value"],
                       avg=(info or {}).get("avg", "—")))
        short.append(t("bx.issue", locale, label=bad["label"], value=bad["value"], avg=(info or {}).get("avg", "—")))
        tiles.append(_tile(label=bad["label"], tag=t("verdict.issue_k", locale), value=bad["value"],
                           delta=bad["delta"], tone=bad["delta_tone"], info=info, locale=locale,
                           help_id=bad["id"], issue=True))
    elif link and link.get("drop_num") is not None:
        lines.append(t("verdict.issue_flow", locale, a=link["from"], b=link["to"], drop=link["drop"]))
        short.append(t("bx.issue_flow", locale, a=link["from"], b=link["to"], drop=link["drop"]))
        tiles.append(_tile(label=t("verdict.link", locale, a=link["from"], b=link["to"]),
                           tag=t("verdict.issue_k", locale), value=link["go"]["all"],
                           delta="—", tone="na", info=None, locale=locale, issue=True,
                           note=t("verdict.issue_flow_note", locale, drop=link["drop"])))
    else:
        lines.append(t("verdict.issue_none", locale))
        short.append(t("bx.issue_none", locale))
        eng = by_id.get("engaged")
        if eng:
            tiles.append(_tile(label=eng["label"], tag="", value=eng["value"],
                               delta=str(eng.get("delta") or "—"), tone=str(eng.get("tone") or "na"),
                               info=_bench_info(eng.get("value_num"), eng.get("bench")),
                               locale=locale, help_id=eng["id"]))
    joiner = "" if locale == "ja" else " "
    sep = t("bx.sep", locale)
    return {"text": joiner.join(lines), "short": (short[0] + sep + short[1]) if len(short) > 1 else "".join(short),
            "tiles": tiles}


def _dialog(item: dict[str, Any], locale: str) -> dict[str, str]:
    h = item["help"]
    return {
        "id": item["id"],
        "kind": _kind_label(h["kind"], locale),
        "title": h["title"],
        "meaning": h["meaning"],
        "formula": h["formula"],
        "tip": h["tip"],
    }


# --- page -----------------------------------------------------------------


def render_sample_dense(*args: Any, **kwargs: Any) -> str:
    """Render the dense board; 業界目安 for this render are scoped to it."""
    token = _ACTIVE_BENCH.set({})
    loc_token = _ACTIVE_LOCALE.set(normalize_locale(kwargs.get("locale") or "ja"))
    try:
        return _render_sample_dense(*args, **kwargs)
    finally:
        _ACTIVE_LOCALE.reset(loc_token)
        _ACTIVE_BENCH.reset(token)


def _render_sample_dense(
    *,
    industry: str = "hr",
    period: str = "28d",
    property_name: str = "",
    industry_label: str = "",
    industry_note: str = "",
    data: dict[str, Any] | None = None,
    ind: dict[str, Any] | None = None,
    benches_raw: dict[str, dict[str, Any]] | None = None,
    pack_links: list[tuple[str, str]] | list[tuple[str, str, str]] | None = None,
    pack_groups: list[tuple[str, str, list[tuple[str, str, str]]]] | None = None,
    nav_active: str = "",
    connected: dict[str, str] | None = None,
    locale: str = "ja",
    board_kind: str = "sample",
    bench: dict[str, Any] | None = None,
    flow: dict[str, Any] | None = None,
    prev: dict[str, Any] | None = None,
    notice: dict[str, str] | None = None,
    extras: dict[str, Any] | None = None,
    details_src: str = "",
    fragment: bool = False,
    editor: dict[str, Any] | None = None,
    industry_drawer: dict[str, Any] | None = None,
    ind_name: str = "",
    meta_short: str = "",
    auto_open: str = "",
) -> str:
    loc = normalize_locale(locale)
    if data is None or ind is None or benches_raw is None:
        from sitekpi.packs import BENCHMARKS, DEMO, INDUSTRIES

        ind = ind or INDUSTRIES[industry]
        data = data or DEMO[industry][period]
        benches_raw = benches_raw or BENCHMARKS[industry]
    if pack_groups is None and pack_links is None:
        from sitekpi.packs import packs_by_category

        pack_groups = packs_by_category()
    nav_active = nav_active or f"pack:{industry}"

    board = build_dense_board(
        industry=industry, period=period, ind=ind, data=data, benches_raw=benches_raw, locale=loc,
        prev=prev,
    )
    _ACTIVE_BENCH.set(board["benches"])
    is_sample = board_kind != "live"

    industry_label = industry_label or board["industry_label"]
    industry_note = industry_note or board["industry_note"]
    if industry_note in ("", "業界パック見本"):
        industry_note = t("sample_meta", loc)
    prop = property_name or board["property_name"]
    period_label = t("period.28d" if period == "28d" else "period.7d", loc)
    # Live boards pass a custom industry_note; avoid a double "(sample)"
    page_title = (
        f"SiteKPI · {industry_label}"
        if industry_note and industry_note != t("sample_meta", loc)
        else f"SiteKPI · {industry_label}{t('sample_title_suffix', loc)}"
    )

    # 詳しい数字 (L2): inline, or loaded after the page by board.js (details_src) when GA4 is slow
    details = None if details_src else _details_view(board, extras, flow, loc)
    if fragment:
        return render("board/details.html", loc=loc, details=details)

    watch = _watch_items(board, loc)
    help_items = board["summary"] + board["funnel"] + board["engage"] + board["audience"]
    seen: set[str] = set()
    dialogs = []
    for r in help_items:
        if r["id"] in seen or not r.get("help"):
            continue
        seen.add(r["id"])
        dialogs.append(_dialog_v3({"id": r["id"], "label": r["label"], "help": r["help"], "gl": _gl_key(r["id"]),
                                   "bench": _bench_view(_bench_info(r.get("value_num"), r.get("bench")))}, loc))
    worst = _worst_link(flow)
    return render(
        "board.html",
        loc=loc,
        rail=rail_context(
            nav_active=nav_active, locale=loc, connected=connected,
            pack_groups=pack_groups, pack_links=pack_links, industry=industry,
        ),
        page_title=page_title,
        industry_label=industry_label,
        pack_meta=f"{industry_note} · {prop} · {period_label}",
        period=period,
        verdict=_verdict(board, watch, flow, loc),
        watch=watch,
        worst=worst,
        details=details,
        details_src=details_src,
        editor=editor,
        industry_drawer=industry_drawer,
        ind_name=ind_name,
        meta_short=meta_short,
        is_sample=is_sample,
        notice=notice,
        bench=bench,
        flow=flow,
        dialogs=dialogs,
        board_data={
            "close": t("close", loc),
            "details_src": details_src,
            "auto_open": auto_open if (editor or industry_drawer) else "",
            "open_tpl": t("detail.open", loc, n="__N__"),
            "close_label": t("detail.close", loc),
            "load_error": t("detail.load_error", loc),
            "retry": t("detail.retry", loc),
        },
    )


def verdict_scene(*, industry: str, data: dict[str, Any], benches_raw: dict[str, dict[str, Any]],
                  flow: dict[str, Any] | None, locale: str, prev: dict[str, Any] | None = None) -> dict[str, Any]:
    """The board's いまの状態 (sentence + 3 tiles) without the page — used by the 見本ボード preview."""
    from sitekpi.packs import INDUSTRIES

    loc = normalize_locale(locale)
    token = _ACTIVE_BENCH.set({})
    loc_token = _ACTIVE_LOCALE.set(loc)
    try:
        board = build_dense_board(industry=industry, period="28d", ind=INDUSTRIES[industry], data=data,
                                  benches_raw=benches_raw, locale=loc, prev=prev)
        _ACTIVE_BENCH.set(board["benches"])
        return _verdict(board, _watch_items(board, loc), flow, loc)
    finally:
        _ACTIVE_LOCALE.reset(loc_token)
        _ACTIVE_BENCH.reset(token)


# --- 詳しい数字 (L2) v3: every category stacked, 8週の推移, extras ----------------

# board row id → 指標辞典 key (the 説明 card links to the same entry)
_GL = {
    "signup_cvr": "signup_cvr", "funnel_cvr": "signup_cvr", "uu": "uu", "aud_uu": "uu",
    "sessions": "sessions", "aud_sessions": "sessions", "engaged": "engaged", "engage_rate_row": "engaged",
    "bounce_like": "bounce_rate", "pages_session": "pages_session", "pv_uu": "pages_per_uu",
    "pv": "pageviews", "avg_time": "avg_time", "new_return": "new_return", "sessions_per_uu": "sessions_per_uu",
    "pay_start": "pay_start", "funnel_rate_a": "signup_to_pay",
}
SPARK_W, SPARK_H = 76, 26
_COLLAPSED = ("audience", "events")


def _gl_key(row_id: str, name: str = "") -> str:
    from sitekpi.metrics.help import HELP, resolve_id

    for cand in (_GL.get(row_id, ""), row_id, resolve_id(name) if name else ""):
        if cand and resolve_id(cand) in HELP:
            return resolve_id(cand)
    return ""


def _spark(points: list[float] | None, tone: str) -> dict[str, str] | None:
    """SVG polyline points for a 76×26 sparkline (oldest left). None when there is no series."""
    vals = [float(v) for v in (points or []) if v is not None]
    if len(vals) < 2 or not any(vals):
        return None
    lo, hi = min(vals), max(vals)
    span = hi - lo or 1.0
    step = (SPARK_W - 4) / (len(vals) - 1)
    pts = [(2 + i * step, SPARK_H - 3 - (v - lo) / span * (SPARK_H - 6) if hi != lo else SPARK_H / 2)
           for i, v in enumerate(vals)]
    return {"points": " ".join(f"{x:.1f},{y:.1f}" for x, y in pts),
            "x": f"{pts[-1][0]:.1f}", "y": f"{pts[-1][1]:.1f}",
            "tone": tone if tone in ("up", "down") else "flat"}


def _ratio(a: list[float] | None, b: list[float] | None, scale: float = 100.0) -> list[float] | None:
    if not a or not b:
        return None
    return [(x / y * scale) if y else 0.0 for x, y in zip(a, b)]


def _delta_pct(cur: float | None, prev: float | None) -> tuple[str, str]:
    if cur is None or not prev:
        return "—", "na"
    d = (cur - prev) / prev * 100
    return f"{d:+.1f}%", ("up" if d > 0.05 else "down" if d < -0.05 else "flat")


def _delta_pt(cur: float | None, prev: float | None, *, hib: bool = True) -> tuple[str, str]:
    if cur is None or prev is None:
        return "—", "na"
    d = cur - prev
    good = d > 0.05 if hib else d < -0.05
    bad = d < -0.05 if hib else d > 0.05
    return f"{d:+.1f}pt", ("up" if good else "down" if bad else "flat")


def _fmt_mmss(seconds: float | None) -> str:
    if seconds is None:
        return "—"
    s = int(round(seconds))
    return f"{s // 60}:{s % 60:02d}"


def _yen(n: float | None, loc: str) -> str:
    if n is None:
        return "—"
    return f"¥{n:,.0f}"


def _d_row(*, rid: str, label: str, value: str, delta: str = "—", tone: str = "na", info: Any = None,
           spark: list[float] | None = None, sub: str = "", sub_warn: bool = False, focus: bool = False,
           code: bool = False, gl: str = "", help: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "id": rid, "label": label, "value": str(value).replace(" / ", " / "),
        "delta": delta or "—", "delta_tone": tone or "na",
        "bench": _bench_view(info), "spark": _spark(spark, tone), "sub": sub, "sub_warn": sub_warn,
        "focus": focus, "code": code, "gl": gl, "help": help,
    }


def _from_board(r: dict[str, Any], spark: list[float] | None = None) -> dict[str, Any]:
    info = _bench_info(r.get("value_num"), r.get("bench"))
    return _d_row(rid=r["id"], label=r["label"], value=r["value"], delta=str(r.get("delta") or "—"),
                  tone=str(r.get("tone") or "na"), info=info, spark=spark, focus=bool(r.get("focus")),
                  gl=_gl_key(r["id"]), help=r.get("help"))


def _help_of(key: str, loc: str) -> dict[str, Any] | None:
    from sitekpi.metrics.help import get_help

    h = get_help(key, loc)
    return {k: h.get(k, "") for k in ("kind", "title", "meaning", "formula", "tip")} if h else None


def _details_view(board: dict[str, Any], extras: dict[str, Any] | None, flow: dict[str, Any] | None,
                  loc: str) -> dict[str, Any]:
    """L2 groups (stacked, one category per block) + the 説明 cards they open."""
    x = extras or {}
    W: dict[str, list[float]] = x.get("weeks") or {}
    cur: dict[str, Any] = x.get("cur") or {}
    prv: dict[str, Any] = x.get("prev") or {}
    by_id = {r["id"]: r for r in board["summary"] + board["funnel"] + board["engage"] + board["audience"]}
    primary_ev = next((e["name"] for e in board["events"] if e.get("focus")), "")
    w_primary = W.get("ev:" + primary_ev) if primary_ev else None
    eng = W.get("engaged")
    series = {
        "signup_cvr": _ratio(w_primary, W.get("uu")), "funnel_cvr": _ratio(w_primary, W.get("uu")),
        "primary": w_primary, "funnel_primary": w_primary,
        "engage_rate_row": eng, "bounce_like": [100 - v for v in eng] if eng else None,
        "pages_session": _ratio(W.get("pv"), W.get("sessions"), 1.0), "pv_uu": _ratio(W.get("pv"), W.get("uu"), 1.0),
        "pv": W.get("pv"), "new_return": _ratio(W.get("new_users"), W.get("uu")),
        "sessions_per_uu": _ratio(W.get("sessions"), W.get("uu"), 1.0),
        "aud_uu": W.get("uu"), "aud_sessions": W.get("sessions"),
    }
    groups: list[dict[str, Any]] = []

    def group(gid: str, rows: list[dict[str, Any]], *, head: str = "", note: str = "",
              missing: list[str] | None = None) -> None:
        if not rows and not note:
            return
        warn = sum(1 for r in rows if r["bench"].get("judge") == "down")
        groups.append({
            "id": gid, "title": t(f"panel.{gid}", loc), "rows": rows, "count": len(rows), "warn": warn,
            "value_head": head or t("col.value", loc), "note": note, "missing": missing or [],
            "collapsed": gid in _COLLAPSED and not warn,
            "summary": " · ".join(f"{r['label']} {r['value']}" for r in rows[:3]) + (" …" if len(rows) > 3 else ""),
        })

    # 転換ファネル (+ キーイベント · セッションCVR)
    funnel = [_from_board(r, series.get(r["id"])) for r in board["funnel"]]
    if cur.get("key_events") is not None:
        d, tn = _delta_pct(cur.get("key_events"), prv.get("key_events"))
        funnel.append(_d_row(rid="x_key_events", label=_help_of("key_events", loc)["title"],
                             value=f"{int(cur['key_events']):,}", delta=d, tone=tn, gl="key_events",
                             help=_help_of("key_events", loc)))
    p_row = by_id.get("primary")
    ses = by_id.get("aud_sessions")
    if p_row and ses and p_row.get("value_num") and ses.get("value_num"):
        v = float(p_row["value_num"]) / float(ses["value_num"]) * 100
        funnel.append(_d_row(rid="x_session_cvr", label=_help_of("session_cvr", loc)["title"], value=f"{v:.1f}%",
                             spark=_ratio(w_primary, W.get("sessions")), gl="session_cvr",
                             help=_help_of("session_cvr", loc)))
    group("funnel", funnel)

    # 売上 (only when the site records purchases)
    if x.get("has_revenue"):
        rev = []
        for rid, key, fmt, wk in (("x_revenue", "purchase_revenue", "yen", "revenue"),
                                  ("x_tx", "transactions", "int", "tx"),
                                  ("x_aov", "average_purchase_revenue", "yen", None),
                                  ("x_item", "item_revenue", "yen", None)):
            ck = {"x_revenue": "revenue", "x_tx": "tx", "x_aov": "aov", "x_item": "item_revenue"}[rid]
            if cur.get(ck) is None:
                continue
            d, tn = _delta_pct(cur.get(ck), prv.get(ck))
            val = _yen(cur[ck], loc) if fmt == "yen" else f"{int(cur[ck]):,}"
            h = _help_of(key, loc)
            rev.append(_d_row(rid=rid, label=h["title"], value=val, delta=d, tone=tn,
                              spark=W.get(wk) if wk else None, gl=key, help=h))
        group("revenue", rev)

    # エンゲージ (+ 平均セッション時間 · イベント/セッション · スクロール · ダウンロード)
    engage = [_from_board(r, series.get(r["id"])) for r in board["engage"]]
    extra_engage = [
        ("x_avg_session", "avg_session_duration", "avg_session", lambda v: _fmt_mmss(v), "avg_session"),
        ("x_eps", "events_per_session", "events_per_session", lambda v: f"{v:.1f}", None),
        ("x_scrolled", "scrolled_users", "scrolled", lambda v: f"{int(v):,}", "ev:scroll"),
    ]
    for rid, key, ck, fmt, wk in extra_engage:
        if cur.get(ck) is None:
            continue
        d, tn = _delta_pct(cur.get(ck), prv.get(ck))
        h = _help_of(key, loc)
        engage.append(_d_row(rid=rid, label=h["title"], value=fmt(cur[ck]), delta=d, tone=tn,
                             spark=W.get(wk) if wk else None, gl=key, help=h))
    dl = next((e for e in board["events"] if e["name"] == "file_download"), None)
    if dl:
        h = _help_of("ev_file_download", loc)
        engage.append(_d_row(rid="x_downloads", label=t("detail.downloads", loc), value=f"{dl['count']:,}",
                             delta=dl["delta"], tone="up" if str(dl["delta"]).startswith("+") else "down"
                             if str(dl["delta"]).startswith("-") else "na",
                             spark=W.get("ev:file_download"), gl="ev_file_download", help=h))
    group("engage", engage)

    # 流入チャネル (+ セッション数 · CVR under each name)
    ch_rows = {str(r.get("name")): r for r in ((flow or {}).get("ch_rows") or [])}
    total_sessions = float((by_id.get("aud_sessions") or {}).get("value_num") or 0)
    chans = []
    for c in _group_channels(board["channels"], loc):
        fr = ch_rows.get(str(c["name"]))
        sub_parts = []
        if total_sessions and c.get("pct"):
            sub_parts.append(t("detail.sessions_n", loc, n=f"{round(total_sessions * c['pct'] / 100):,}"))
        if fr:
            sub_parts.append(f"CVR {fr.get('rate_fmt')}" + (f"（{t('flow.ch_low', loc)}）" if fr.get("low") else ""))
        chans.append(_d_row(rid=c["id"], label=c["name"], value=f"{c['pct']}%", sub=" · ".join(sub_parts),
                            sub_warn=bool(fr and fr.get("low")), gl=_gl_key(c["id"], c["name"]), help=c.get("help")))
    group("channels", chans, head=t("detail.share", loc))

    # デバイス
    devs = x.get("devices") or []
    if devs:
        tot = sum(d["sessions"] for d in devs) or 1
        ptot = sum(d.get("prev_sessions") or 0 for d in devs) or 0
        cvr = {d["id"]: (d["conv_users"] / d["users"] * 100 if d.get("users") else None) for d in devs}
        desk = cvr.get("desktop")
        drows = []
        for d in devs:
            share = d["sessions"] / tot * 100
            pshare = (d.get("prev_sessions") or 0) / ptot * 100 if ptot else None
            delta, tone = _delta_pt(share, pshare)
            c = cvr.get(d["id"])
            low = bool(d["id"] == "mobile" and c is not None and desk and c < desk / 2)
            sub = t("detail.sessions_n", loc, n=f"{d['sessions']:,}") + (f" · CVR {c:.1f}%" if c is not None else "")
            if low:
                sub += t("detail.mobile_low", loc)
            h = _help_of("device_" + d["id"], loc)
            drows.append(_d_row(rid="x_dev_" + d["id"], label=h["title"], value=f"{share:.0f}%", delta=delta,
                                tone="na" if delta == "—" else "flat", sub=sub, sub_warn=low,
                                gl="device_" + d["id"], help=h))
        group("device", drows, head=t("detail.share", loc))

    # オーディエンス (+ 新規 · 再訪 · DAU · DAU/MAU)
    audience = [_from_board(r, series.get(r["id"])) for r in board["audience"]]
    nu = by_id.get("new_return")
    uu_row = by_id.get("aud_uu")
    if nu and uu_row and uu_row.get("value_num"):
        uu_v = float(uu_row["value_num"])
        new_v = round(uu_v * float(nu.get("value_num") or 0) / 100)
        for rid, key, v, wk in (("x_new", "new_users", new_v, W.get("new_users")),
                                ("x_ret", "returning_users", uu_v - new_v,
                                 [a - b for a, b in zip(W.get("uu") or [], W.get("new_users") or [])] or None)):
            h = _help_of(key, loc)
            audience.append(_d_row(rid=rid, label=h["title"], value=f"{int(v):,}", spark=wk, gl=key, help=h))
    if cur.get("dau") is not None:
        h = _help_of("dau", loc)
        audience.append(_d_row(rid="x_dau", label="DAU", value=f"{int(cur['dau']):,}",
                               sub=f"WAU {int(cur.get('wau') or 0):,} · MAU {int(cur.get('mau') or 0):,}",
                               gl="dau", help=h))
        h = _help_of("dau_mau", loc)
        d, tn = _delta_pt(cur.get("dau_mau"), prv.get("dau_mau"))
        audience.append(_d_row(rid="x_dau_mau", label=h["title"], value=f"{cur['dau_mau']:.1f}%", delta=d, tone=tn,
                               gl="dau_mau", help=h))
    group("audience", audience)

    # イベント
    evs = []
    for e in board["events"]:
        dl_ = str(e["delta"])
        tn = "up" if dl_.startswith("+") else "down" if dl_.startswith("-") else "na"
        evs.append(_d_row(rid=e["id"], label=e["name"], value=f"{e['count']:,}", delta=dl_, tone=tn,
                          spark=W.get("ev:" + e["name"]), focus=bool(e.get("focus")), code=True,
                          sub=t("event.alias", loc, name=e["alias"]) if e.get("alias") else "",
                          gl=_gl_key(e["id"]), help=e.get("help")))
    group("events", evs, head=t("col.count", loc), missing=board.get("events_missing") or [])

    # 業務KPI: unlinked → one line
    biz_linked = [b for b in board["business"] if b.get("value") not in _UNLINKED]
    if biz_linked:
        group("biz", [_from_board(b) for b in biz_linked])
    elif board["business"]:
        group("biz", [], note=t("biz.collapsed", loc, n=len(board["business"])))

    dialogs = [_dialog_v3(r, loc) for g in groups for r in g["rows"] if r.get("help")]
    return {"groups": groups, "dialogs": dialogs, "warn": sum(g["warn"] for g in groups)}


def _dialog_v3(r: dict[str, Any], loc: str) -> dict[str, Any]:
    """The 説明 card: the same parts as a 指標辞典 card (kind · title · id · meaning · 計算 · 見るポイント)."""
    h = r["help"]
    return {
        "id": r["id"], "kind": _kind_label(str(h.get("kind") or "digital"), loc), "kind_id": str(h.get("kind") or "digital"),
        "title": h.get("title") or r["label"], "gl": r.get("gl") or "",
        "meaning": h.get("meaning") or "", "formula": h.get("formula") or "", "tip": h.get("tip") or "",
        "bench": r["bench"].get("kind") in ("judge", "none"),
    }
