"""KPI board page (dense hierarchy + 説明 popups).

Python here only shapes data: numbers, 業界目安 positions, chart points.
All markup lives in templates/board.html + templates/board/_macros.html,
styles in static/css/board.css, behaviour in static/js/board.js.
"""

from __future__ import annotations

import math
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

EVENT_PREVIEW = 6
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


def _viz_scale(
    low: float, high: float, value: float | None, unit: str
) -> dict[str, float | None]:
    """Map bench band + value onto 0–100% track positions."""
    span = max(high - low, 1e-9)
    if unit == "%":
        smin, smax = 0.0, 100.0
        if value is not None:
            smin = min(smin, float(value), low)
            smax = max(smax, float(value), high)
    else:
        pad = span * 0.75
        smin, smax = low - pad, high + pad
        if value is not None:
            smin = min(smin, float(value))
            smax = max(smax, float(value))
    if smax <= smin:
        smax = smin + 1.0

    def pct(x: float) -> float:
        return max(0.0, min(100.0, 100.0 * (x - smin) / (smax - smin)))

    mid = (low + high) / 2
    return {
        "p_low": pct(low),
        "p_high": pct(high),
        "p_mid": pct(mid),
        "p_val": pct(float(value)) if value is not None else None,
    }


def _source_text(spec: dict[str, Any], locale: str) -> str:
    if spec.get("custom"):
        return t("bench_src.custom", locale)
    src = spec.get("source") or {}
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
    cited = (spec.get("source") or {}).get("kind") == "cited"
    key = "bench_title_custom" if custom else "bench_title_cited" if cited else "bench_title"
    title = t(key, loc, band=band, avg=avg)
    title += " · " + _source_text(spec, loc)
    scale = _viz_scale(low, high, value, unit)
    base: dict[str, Any] = {
        "key": bench_key,
        "custom": custom,
        "band": band,
        "avg": avg,
        "title": title,
        "low": low,
        "high": high,
        "mid": mid,
        "unit": unit,
        **scale,
    }
    if value is None:
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


def _empty_bench(locale: str) -> dict[str, Any]:
    return {
        "band": "",
        "avg": "—",
        "gap": "—",
        "tone": "na",
        "arrow": "",
        "title": t("bench_empty", locale),
        "p_low": None,
        "p_high": None,
        "p_mid": None,
        "p_val": None,
    }


def _prior_from_delta(value: float | None, delta: str | None) -> float | None:
    """Estimate prior-period value from a delta string (GA4-style compare)."""
    if value is None or not delta:
        return None
    raw = (
        str(delta)
        .replace("−", "-")
        .replace("＋", "+")
        .replace(",", "")
        .strip()
    )
    if not raw or raw == "—":
        return None
    try:
        if raw.endswith("%"):
            pct = float(raw[:-1])
            denom = 1.0 + pct / 100.0
            return value / denom if abs(denom) > 1e-9 else None
        if raw.endswith("pt"):
            pts = float(raw[:-2])
            return value - pts
        return value - float(raw)
    except ValueError:
        return None


def _row_value_num(r: dict[str, Any]) -> float | None:
    cur = r.get("value_num")
    if isinstance(cur, (int, float)):
        return float(cur)
    raw_v = r.get("value")
    if isinstance(raw_v, (int, float)):
        return float(raw_v)
    if not isinstance(raw_v, str):
        return None
    s = raw_v.strip()
    if ":" in s and s.count(":") <= 2:
        parts = s.split(":")
        try:
            nums = [int(p) for p in parts]
        except ValueError:
            return None
        if len(nums) == 2:
            return float(nums[0] * 60 + nums[1])
        if len(nums) == 3:
            return float(nums[0] * 3600 + nums[1] * 60 + nums[2])
    try:
        return float(s.replace(",", "").replace("%", "").strip())
    except ValueError:
        return None


def _seed_u32(text: str) -> int:
    h = 2166136261
    for ch in text:
        h ^= ord(ch)
        h = (h * 16777619) & 0xFFFFFFFF
    return h or 1


def _synthetic_series(
    end: float,
    *,
    prior: float | None = None,
    mid: float | None = None,
    seed: str = "",
    n: int = 8,
) -> tuple[list[float], list[float] | None]:
    """Demo period series (sample packs): solid ends at current, dashed = prior/目安."""
    h = _seed_u32(seed)
    start = prior if prior is not None else end * (0.86 + (h % 12) / 100.0)
    amp = max(abs(end) * 0.05, abs(end - start) * 0.25, 0.08)
    cur: list[float] = []
    for i in range(n):
        t = i / max(n - 1, 1)
        # W-shaped wobble that flattens into the final value (GA4-like)
        phase = (i * 1.7 + (h % 9)) * 0.9
        wobble = math.sin(phase) * amp * (0.35 + 0.65 * (1 - t))
        if i == n - 1:
            cur.append(float(end))
        elif i >= n - 2:
            cur.append(float(end) + wobble * 0.15)
        else:
            cur.append(float(start + (end - start) * (t**0.85) + wobble))
    cmp: list[float] | None
    if prior is not None:
        p0 = prior * (0.92 + (h % 5) / 100.0)
        cmp = [float(p0 + (prior - p0) * (i / max(n - 1, 1))) for i in range(n)]
    elif mid is not None:
        cmp = [float(mid)] * n
    else:
        cmp = None
    return cur, cmp


# --- view models (what the templates render) -----------------------------


def _gap_bar(info: dict[str, Any] | None) -> dict[str, Any]:
    """Summary mini bar: fill between 目安 mid and current value."""
    if not info or info.get("p_mid") is None or info.get("p_val") is None:
        return {"empty": True}
    a = float(info["p_mid"])
    b = float(info["p_val"])
    left, width = (a, b - a) if b >= a else (b, a - b)
    return {
        "empty": False,
        "title": str(info.get("title") or ""),
        "tone": str(info.get("tone") or "na"),
        "fill_style": f"left:{left:.2f}%;width:{max(width, 1.2):.2f}%",
        "mid_style": f"left:{a:.2f}%",
        "val_style": f"left:{b:.2f}%",
    }


def _judge(info: dict[str, Any] | None) -> str:
    """'up' (better than the band) / 'mid' (inside) / 'down' (worse) — '' when no 目安."""
    tone = str((info or {}).get("tone") or "")
    return tone if tone in ("up", "mid", "down") else ""


def _bench_block(info: dict[str, Any] | None, locale: str, *, gap_bar: bool = False) -> dict[str, Any]:
    """業界目安 + 目安差 slot (always reserved, '—' when there is no standard)."""
    empty = info is None
    b = info or _empty_bench(locale)
    return {
        "empty": empty,
        "title": t("bench_empty", locale) if empty else b["title"],
        "avg": b["avg"],
        "band": b.get("band") or "",
        "tone": b["tone"],
        "gap": b["gap"],
        "judge": _judge(None if empty else info),
        "custom": bool((info or {}).get("custom")),
        "key": str((info or {}).get("key") or ""),
        "gapbar": _gap_bar(None if empty else info) if gap_bar else None,
    }


def _bench_cells(info: dict[str, Any] | None) -> dict[str, Any]:
    if not info:
        return {"empty": True}
    return {
        "empty": False,
        "title": info["title"],
        "avg": info["avg"],
        "band": info.get("band") or "",
        "tone": info["tone"],
        "gap": info["gap"],
        "judge": _judge(info),
        "custom": bool(info.get("custom")),
        "key": str(info.get("key") or ""),
    }


def _metric_row(r: dict[str, Any], locale: str) -> dict[str, Any]:
    info = _bench_info(r.get("value_num"), r.get("bench"))
    return {
        "id": r["id"],
        "label": r["label"],
        # "59.6% / 40.4%" may wrap after the slash, never leave "/" alone on a line
        "value": str(r["value"]).replace(" / ", "\u00a0/ "),
        "focus": bool(r.get("focus")),
        "cells": _bench_cells(info),
        "block": _bench_block(info, locale),
        "delta": str(r.get("delta") or "—"),
        "delta_tone": str(r.get("tone") or "na"),
    }


def _compare_plot(
    *, current: float | None, compare: float | None, cur_label: str, cmp_label: str, unit: str = ""
) -> dict[str, Any]:
    """GA4-like dual horizontal bars: current vs prior (or vs 目安)."""
    vals = [v for v in (current, compare) if v is not None]
    peak = max((abs(v) for v in vals), default=1.0) or 1.0
    if unit == "%" and peak <= 120:
        peak = 100.0

    def bar(v: float | None, cls: str, label: str) -> dict[str, str]:
        if v is None:
            return {"label": label, "cls": cls, "style": "width:0", "shown": "—"}
        w = max(2.0, min(100.0, 100.0 * abs(v) / peak))
        if unit:
            shown = _fmt_num(v, unit)
        elif abs(v - round(v)) < 1e-9:
            shown = f"{int(round(v)):,}"
        else:
            shown = f"{v:g}"
        return {"label": label, "cls": cls, "style": f"width:{w:.1f}%", "shown": shown}

    return {
        "kind": "compare",
        "empty": not vals,
        "bars": [bar(current, "is-cur", cur_label), bar(compare, "is-cmp", cmp_label)],
    }


def _trend_plot(current: list[float] | None, compare: list[float] | None = None) -> dict[str, Any]:
    """GA4-style mini line chart: solid current, dashed prior/目安."""
    if not current:
        return {"kind": "trend", "empty": True}
    w, h, pad = 140.0, 40.0, 3.0
    vals = list(current) + list(compare or [])
    ymin, ymax = min(vals), max(vals)
    if abs(ymax - ymin) < 1e-9:
        ymin -= 1.0
        ymax += 1.0
    span = ymax - ymin
    ymin -= span * 0.08
    ymax += span * 0.08

    def pt(i: int, v: float, length: int) -> str:
        x = pad + (i / max(length - 1, 1)) * (w - 2 * pad)
        y = h - pad - ((v - ymin) / (ymax - ymin)) * (h - 2 * pad)
        return f"{x:.2f},{y:.2f}"

    return {
        "kind": "trend",
        "empty": False,
        "grid": [{"x1": f"{pad}", "x2": f"{w - pad}", "y": f"{y:.1f}"} for y in (pad + 2, h / 2, h - pad - 2)],
        "cmp": (
            " ".join(pt(i, v, len(compare)) for i, v in enumerate(compare))
            if compare and len(compare) >= 2
            else ""
        ),
        "cur": " ".join(pt(i, v, len(current)) for i, v in enumerate(current)),
    }


def _bars_plot(series: list[float] | None) -> dict[str, Any]:
    """Mini vertical bars for period points (GA4 exploration-like)."""
    if not series:
        return {"kind": "bars", "empty": True}
    peak = max(abs(v) for v in series) or 1.0
    floor = min(series)
    base = min(0.0, floor) if floor < 0 else 0.0
    span = peak - base or 1.0
    bars = []
    for i, v in enumerate(series):
        ht = max(8.0, 100.0 * (v - base) / span)
        bars.append({"cls": "is-last" if i == len(series) - 1 else "", "style": f"height:{ht:.1f}%"})
    return {"kind": "bars", "empty": False, "bars": bars}


def _viz_meta(r: dict[str, Any], info: dict[str, Any] | None, *, prefer_delta: bool = False) -> dict[str, str]:
    if prefer_delta and r.get("delta"):
        return {"kind": "delta", "text": str(r["delta"])}
    if info and info.get("gap") and info["gap"] != "—":
        text = info["gap"] + (" " + info["arrow"] if info.get("arrow") else "")
        return {"kind": "gap", "tone": info["tone"], "text": text}
    if r.get("delta"):
        return {"kind": "delta", "text": str(r["delta"])}
    return {"kind": "na"}


def _viz_rows(rows: list[dict[str, Any]], *, locale: str, mode: str) -> list[dict[str, Any]]:
    """Rows for the compare / trend / bar view modes."""
    out: list[dict[str, Any]] = []
    for r in rows:
        label = str(r.get("label") or r.get("name") or "")
        cur = _row_value_num(r)
        bench_val = r.get("value_num") if r.get("value_num") is not None else cur
        info = _bench_info(bench_val if r.get("bench") else None, r.get("bench"))
        prior = r.get("prev_num") if r.get("prev_num") is not None else _prior_from_delta(cur, r.get("delta"))
        mid = float(info["mid"]) if info and info.get("mid") is not None else None
        unit = str((info or {}).get("unit") or "")
        seed = str(r.get("id") or label)
        if mode == "compare":
            if prior is not None:
                cmp_val, cmp_label = prior, t("compare.prior", locale)
            elif mid is not None and cur is not None:
                cmp_val, cmp_label = mid, t("compare.bench", locale)
            else:
                cmp_val, cmp_label = None, t("compare.prior", locale)
            plot = _compare_plot(
                current=cur, compare=cmp_val,
                cur_label=t("compare.current", locale), cmp_label=cmp_label, unit=unit,
            )
        elif mode == "trend":
            if cur is None:
                plot = _trend_plot(None)
            else:
                series, cmp_s = _synthetic_series(cur, prior=prior, mid=mid, seed=seed)
                plot = _trend_plot(series, cmp_s)
        else:  # "bar"
            if cur is None:
                plot = _bars_plot(None)
            else:
                series, _ = _synthetic_series(cur, prior=prior, mid=mid, seed=seed)
                plot = _bars_plot(series)
        out.append(
            {
                "id": str(r["id"]),
                "label": label,
                "value": str(r.get("value") or ""),
                "focus": bool(r.get("focus")),
                "plot": plot,
                "meta": _viz_meta(r, info, prefer_delta=True),
            }
        )
    return out


def _metric_panel(
    pid: str, title: str, rows: list[dict[str, Any]], *, modes: list[str], locale: str, sample: bool
) -> dict[str, Any]:
    extra: list[dict[str, Any]] = []
    if sample and "trend" in modes:
        extra.append({"mode": "bar", "note": True, "rows": _viz_rows(rows, locale=locale, mode="bar")})
        extra.append({"mode": "trend", "note": True, "rows": _viz_rows(rows, locale=locale, mode="trend")})
    extra.append({"mode": "compare", "note": False, "rows": _viz_rows(rows, locale=locale, mode="compare")})
    return {
        "id": pid,
        "title": title,
        "sub": t("count_n", locale, n=len(rows)),
        "modes": modes,
        "rows": [_metric_row(r, locale) for r in rows],
        "extra": extra,
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
                    "tone": info["tone"],
                    "title": title,
                    "numbers": t("watch.numbers", locale, value=r["value"], avg=info["avg"],
                                 band=info["band"], gap=info["gap"]),
                    "trend": _trend(r, locale),
                    "tip": tip,
                },
            )
        )
    scored.sort(key=lambda x: (x[0], x[1]))
    return [item for _, _, item in scored[:WATCH_MAX]]


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

    summary = [
        {
            "id": k["id"],
            "label": k["label"],
            "value": k["value"],
            "delta": k["delta"],
            "tone": k["tone"],
            "focus": bool(k.get("focus")),
            "block": _bench_block(_bench_info(k.get("value_num"), k.get("bench")), loc, gap_bar=True),
        }
        for k in board["summary"]
    ]

    trend_modes = ["list", "card", "bar", "compare", "trend"] if is_sample else ["list", "card", "compare"]
    panels = {
        "audience": _metric_panel("audience", t("panel.audience", loc), board["audience"],
                                  modes=trend_modes, locale=loc, sample=is_sample),
        "engage": _metric_panel("engage", t("panel.engage", loc), board["engage"],
                                modes=trend_modes, locale=loc, sample=is_sample),
        "funnel": _metric_panel("funnel", t("panel.funnel", loc), board["funnel"],
                                modes=["list", "card", "compare"], locale=loc, sample=is_sample),
    }

    events_src = board["events"]
    event_max = max((e["count"] for e in events_src), default=1) or 1
    event_rows = []
    for i, e in enumerate(events_src):
        cls = " ".join(
            c for c in ("is-more" if i >= EVENT_PREVIEW else "", "is-focus" if e.get("focus") else "") if c
        )
        event_rows.append(
            {
                "id": e["id"],
                "name": e["name"],
                "alias": e.get("alias", ""),
                "count": e["count"],
                "delta": e["delta"],
                "focus": bool(e.get("focus")),
                "cls": cls,
                "bar_pct": max(2, round(100 * e["count"] / event_max)),
            }
        )
    more_n = max(0, len(events_src) - EVENT_PREVIEW)
    sub_open = t("count_n", loc, n=len(events_src))
    sub_closed = t("count_more", loc, shown=EVENT_PREVIEW, more=more_n) if more_n else sub_open
    events = {
        "rows": event_rows,
        "more_n": more_n,
        "missing": board.get("events_missing") or [],
        "sub_closed": sub_closed,
    }

    business = []
    for b in board["business"]:
        linked = b.get("value") not in _UNLINKED
        info = _bench_info(b.get("value_num"), b.get("bench")) if linked else None
        business.append(
            {
                "id": b["id"],
                "label": b["label"],
                "value": b["value"],
                "linked": linked,
                "cells": _bench_cells(info),
                "block": _bench_block(info, loc),
            }
        )

    channels = _group_channels(board["channels"], loc)
    help_items = (
        board["summary"] + board["funnel"] + board["engage"] + board["audience"]
        + board["events"] + channels + board["business"]
    )

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
        focus_line=board.get("focus_line") or "",
        summary=summary,
        panels=panels,
        channels=channels,
        channels_stack=[c for c in channels if c.get("pct")],
        events=events,
        business=business,
        business_unlinked=bool(business) and not any(b["linked"] for b in business),
        watch=_watch_items(board, loc),
        is_sample=is_sample,
        bench=bench,
        flow=flow,
        dialogs=[_dialog(item, loc) for item in help_items],
        board_data={
            "close": t("close", loc),
            "more_tpl": t("more_n", loc, n="__N__"),
            "event_sub_open": sub_open,
            "event_sub_closed": sub_closed,
            "modes": {"engage": trend_modes, "audience": trend_modes},
        },
    )
