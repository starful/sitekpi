"""業界目安 helpers and metric/channel row view models for the board.

Judge chips (良好 / 目安内 / 要注意 / 基準なし) come from effective benches
(load_effective = pack defaults + sources + 自社目安 overrides). Never invent a
band when sources say there is none — show 基準なし and explain why in the popover.
"""

from __future__ import annotations

from typing import Any

from sitekpi.i18n import t
from sitekpi.views.board_ctx import _ACTIVE_BENCH, _ACTIVE_LOCALE

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


def _range_gap(value: float, low: float, high: float, hib: bool, gap_unit: str) -> dict[str, Any]:
    """今 · 業界(range) · あと(range): how far the value is from the 業界目安 range.

    short → "+5.2" "〜+25.2pt" (to the near edge, then to the far edge); in → 0; over → beyond the good edge.
    pos_* place the range and the value on a small bar (0–100%)."""
    def f(x: float) -> str:
        x = abs(x)
        return f"{x:.2f}" if 0 < x < 1 and gap_unit not in ("pt", "%") else f"{x:.1f}"

    def sign(x: float) -> str:
        return ("+" if x > 0 else "−" if x < 0 else "±") + f(x)

    u = gap_unit
    if low <= value <= high:
        state, main, rest = "in", "", ""
    elif (hib and value < low) or (not hib and value > high):
        near, far = (low - value, high - value) if hib else (high - value, low - value)
        state, main, rest = "short", sign(near), "〜" + sign(far) + u
    else:
        beyond = value - high if hib else low - value
        state, main, rest = "over", "+" + f(beyond), u
    width = (high - low) or abs(high) or 1.0
    lo_end = min(low, value) - width * 0.35
    hi_end = max(high, value) + width * 0.35

    def pos(x: float) -> float:
        return round((x - lo_end) / (hi_end - lo_end) * 100, 1)

    return {"state": state, "main": main, "rest": rest,
            "pos_lo": pos(low), "pos_w": round(pos(high) - pos(low), 1), "pos_v": pos(value)}


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
    band = f"{round(low, 1):g}–{round(high, 1):g}{unit}"
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
        "hib": hib,
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
        "rg": _range_gap(value, low, high, hib, gap_unit),
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
                "judge": "", "custom": False, "none": False, "rg": None}
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
        "rg": None if none else info.get("rg"),
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


