"""Site KPI board page (dense hierarchy + 説明 popups)."""

from __future__ import annotations

import math
from html import escape
from typing import Any

from sitekpi.views.branding import brand_head_links, brand_logo_css, brand_logo_html
from sitekpi.board.data import build_dense_board
from sitekpi.i18n import html_lang, normalize_locale, t
from sitekpi.i18n.pack_l10n import pack_text


def _help(
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


_KIND_KEYS = {
    "digital": "kind.digital",
    "event": "kind.event",
    "traffic": "kind.traffic",
    "business": "kind.business",
}

# Legacy alias used by dialogs (locale-aware via _kind_label)
KINDS = {
    "digital": "デジタル",
    "event": "イベント",
    "traffic": "流入",
    "business": "業務",
}


def _kind_label(kind: str, locale: str) -> str:
    key = _KIND_KEYS.get(kind)
    if key:
        return t(key, locale)
    return KINDS.get(kind, kind)

# Active pack benches (set per render from DEMO BENCHMARKS)
_ACTIVE_BENCH: dict[str, dict[str, Any]] = {}


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


def _bench_info(value: float | None, bench_key: str | None) -> dict[str, Any] | None:
    if not bench_key:
        return None
    spec = _ACTIVE_BENCH.get(bench_key)
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
    title = f"パック標準帯 {band}（平均目安 {avg}）"
    scale = _viz_scale(low, high, value, unit)
    base: dict[str, Any] = {
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


def _viz_band_gauge(info: dict[str, Any] | None, *, kind: str = "band") -> str:
    """Horizontal band (or dial) gauge: pack zone + current marker."""
    empty = info is None or info.get("p_low") is None
    if empty:
        return (
            f'<div class="bench-gauge is-empty kind-{escape(kind)}" aria-hidden="true">'
            f'<div class="bench-gauge-track"></div></div>'
        )
    assert info is not None
    p_low = float(info["p_low"])
    p_high = float(info["p_high"])
    p_mid = float(info["p_mid"])
    p_val = info.get("p_val")
    tone = escape(str(info.get("tone") or "na"))
    zone_w = max(0.0, p_high - p_low)
    marker = ""
    if p_val is not None:
        marker = (
            f'<i class="bench-gauge-val tone-{tone}" '
            f'style="left:{float(p_val):.2f}%"></i>'
        )
    return (
        f'<div class="bench-gauge kind-{escape(kind)}" title="{escape(str(info.get("title") or ""))}">'
        f'<div class="bench-gauge-track">'
        f'<i class="bench-gauge-zone" style="left:{p_low:.2f}%;width:{zone_w:.2f}%"></i>'
        f'<i class="bench-gauge-mid" style="left:{p_mid:.2f}%"></i>'
        f"{marker}"
        f"</div></div>"
    )


def _viz_gap_bar(info: dict[str, Any] | None) -> str:
    """Summary mini bar: fill between 目安 mid and current value."""
    if not info or info.get("p_mid") is None or info.get("p_val") is None:
        return '<div class="gap-bar is-empty" aria-hidden="true"><div class="gap-bar-track"></div></div>'
    a = float(info["p_mid"])
    b = float(info["p_val"])
    left, width = (a, b - a) if b >= a else (b, a - b)
    tone = escape(str(info.get("tone") or "na"))
    return (
        f'<div class="gap-bar" title="{escape(str(info.get("title") or ""))}">'
        f'<div class="gap-bar-track">'
        f'<i class="gap-bar-fill tone-{tone}" style="left:{left:.2f}%;width:{max(width, 1.2):.2f}%"></i>'
        f'<i class="gap-bar-mid" style="left:{a:.2f}%"></i>'
        f'<i class="gap-bar-val tone-{tone}" style="left:{b:.2f}%"></i>'
        f"</div></div>"
    )


def _bench_block(
    info: dict[str, Any] | None,
    locale: str = "ja",
    *,
    viz: str = "band",
) -> str:
    # Always reserve the same slot so cards/rows don't change height.
    empty = info is None
    b = info or _empty_bench(locale)
    if empty:
        b = {**b, "title": t("bench_empty", locale)}
    band = (
        f'<span class="bench-band">{escape(b["band"])}</span>'
        if b.get("band")
        else ""
    )
    empty_cls = " is-empty" if empty else ""
    if viz == "gap":
        gauge = _viz_gap_bar(None if empty else info)
    elif viz == "dial":
        gauge = _viz_band_gauge(None if empty else info, kind="dial")
    elif viz == "none":
        gauge = ""
    else:
        gauge = _viz_band_gauge(None if empty else info, kind="band")
    return (
        f'<div class="bench-line{empty_cls}" title="{escape(b["title"])}">'
        f"{gauge}"
        f'<div class="bench-row"><span class="bench-k">{escape(t("bench", locale))}</span>'
        f'<span class="bench-v">{escape(b["avg"])}</span>{band}</div>'
        f'<div class="bench-row"><span class="bench-k">{escape(t("bench_gap", locale))}</span>'
        f'<span class="bench-gap tone-{escape(b["tone"])}">'
        f'{escape(b["gap"])}'
        f'{" " + escape(b["arrow"]) if b["arrow"] else ""}'
        f"</span></div></div>"
    )


def _bench_cells(
    info: dict[str, Any] | None,
    locale: str = "ja",
    *,
    viz: str = "band",
) -> str:
    if not info:
        gauge = (
            _viz_band_gauge(None, kind="dial")
            if viz == "dial"
            else _viz_band_gauge(None, kind="band")
            if viz != "none"
            else ""
        )
        return (
            f'<td class="num muted bench-cell is-empty" title="{escape(t("bench_empty_short", locale))}">'
            f"{gauge}—</td>"
            '<td class="num muted bench-gap tone-na">—</td>'
        )
    band = (
        f'<span class="bench-band">{escape(info["band"])}</span>'
        if info.get("band")
        else ""
    )
    if viz == "dial":
        gauge = _viz_band_gauge(info, kind="dial")
    elif viz == "none":
        gauge = ""
    else:
        gauge = _viz_band_gauge(info, kind="band")
    return (
        f'<td class="num bench-cell" title="{escape(info["title"])}">'
        f"{gauge}"
        f'<span class="bench-v">{escape(info["avg"])}</span>{band}</td>'
        f'<td class="num bench-gap tone-{escape(info["tone"])}">'
        f'{escape(info["gap"])}'
        f'{" " + escape(info["arrow"]) if info["arrow"] else ""}'
        f"</td>"
    )


def _help_btn(help_id: str, title: str, locale: str = "ja") -> str:
    return (
        f'<button type="button" class="help-btn" data-help="{escape(help_id)}" '
        f'aria-label="{escape(t("help_of", locale, title=title))}">{escape(t("help", locale))}</button>'
    )


def _section_view_switch(section: str, modes: list[str], locale: str = "ja") -> str:
    labels = {
        "list": t("view.list", locale),
        "card": t("view.card", locale),
        "bar": t("view.bar", locale),
        "compare": t("view.compare", locale),
        "trend": t("view.trend", locale),
        "stack": t("view.stack", locale),
    }
    btns = "".join(
        f'<button type="button" class="view-btn" data-section="{escape(section)}" '
        f'data-mode="{escape(m)}">{escape(labels[m])}</button>'
        for m in modes
    )
    return (
        f'<div class="view-switch" data-section-switch="{escape(section)}" '
        f'role="group" aria-label="{escape(t("view.switch", locale))}">{btns}</div>'
    )


def _dialogs_from_items(items: list[dict[str, Any]], locale: str = "ja") -> str:
    blocks: list[str] = []
    for item in items:
        h = item["help"]
        hid = item["id"]
        kind = _kind_label(h["kind"], locale)
        formula_html = "<br>".join(escape(line) for line in h["formula"].split("\n"))
        meaning_html = "<br>".join(escape(line) for line in h["meaning"].split("\n"))
        blocks.append(
            f"""
            <dialog class="help-dialog" id="help-{escape(hid)}" data-help-dialog>
              <form method="dialog" class="help-sheet">
                <header>
                  <div>
                    <p class="help-kind">{escape(kind)}</p>
                    <h3>{escape(h["title"])}</h3>
                  </div>
                  <button type="submit" class="help-close" aria-label="{escape(t("close", locale))}">×</button>
                </header>
                <section>
                  <h4>{escape(t("meaning", locale))}</h4>
                  <p>{meaning_html}</p>
                </section>
                <section>
                  <h4>{escape(t("formula", locale))}</h4>
                  <p class="formula">{formula_html}</p>
                </section>
                <section>
                  <h4>{escape(t("tip", locale))}</h4>
                  <p>{escape(h["tip"])}</p>
                </section>
              </form>
            </dialog>
            """
        )
    return "\n".join(blocks)


def _metric_table_parts(
    rows: list[dict[str, Any]],
    *,
    preview: int | None = None,
    locale: str = "ja",
) -> dict[str, Any]:
    """Build list/card HTML (numbers only; gauges live in separate view modes)."""
    n = len(rows)
    show_more = preview is not None and n > preview
    cut = preview if show_more else n
    focus = escape(t("focus", locale))

    def row_cls(i: int, r: dict[str, Any], *, as_attr: bool = False) -> str:
        bits = []
        if show_more and i >= cut:
            bits.append("is-more")
        if r.get("focus"):
            bits.append("is-focus")
        if not bits:
            return ""
        joined = " ".join(bits)
        return f" class='{joined}'" if as_attr else f" {joined}"

    table_rows = "".join(
        f"""
        <tr{row_cls(i, r, as_attr=True)}>
          <td class="help-cell">{_help_btn(r["id"], r["label"], locale)}</td>
          <td class="name-cell"><span class="row-name">{escape(r["label"])}</span>
            {f" <span class='focus-tag'>{focus}</span>" if r.get("focus") else ""}</td>
          <td class="num">{escape(r["value"])}</td>
          {_bench_cells(_bench_info(r.get("value_num"), r.get("bench")), locale, viz="none")}
        </tr>
        """
        for i, r in enumerate(rows)
    )
    cards = "".join(
        f"""
        <article class="metric-card{row_cls(i, r)}">
          <div class="metric-card-head">
            {_help_btn(r["id"], r["label"], locale)}
            <span class="metric-card-name">{escape(r["label"])}</span>
            {f"<span class='focus-tag'>{focus}</span>" if r.get("focus") else ""}
          </div>
          <div class="metric-card-value">{escape(r["value"])}</div>
          {_bench_block(_bench_info(r.get("value_num"), r.get("bench")), locale, viz="none")}
        </article>
        """
        for i, r in enumerate(rows)
    )
    more_n = max(0, n - cut) if show_more else 0
    sub = (
        t("count_more", locale, shown=cut, more=more_n)
        if more_n
        else t("count_n", locale, n=n)
    )
    return {
        "rows": table_rows,
        "cards": cards,
        "more_n": more_n,
        "preview": cut,
        "total": n,
        "sub": sub,
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


def _viz_trend_svg(
    current: list[float] | None,
    compare: list[float] | None = None,
) -> str:
    """GA4-style mini line chart: solid current, dashed prior/目安."""
    if not current:
        return (
            '<div class="trend-chart is-empty" aria-hidden="true">'
            '<svg viewBox="0 0 140 40" preserveAspectRatio="none"></svg></div>'
        )
    w, h, pad = 140.0, 40.0, 3.0
    vals = list(current) + list(compare or [])
    ymin, ymax = min(vals), max(vals)
    if abs(ymax - ymin) < 1e-9:
        ymin -= 1.0
        ymax += 1.0
    # pad range a bit
    span = ymax - ymin
    ymin -= span * 0.08
    ymax += span * 0.08
    n = len(current)

    def pt(i: int, v: float, length: int) -> str:
        x = pad + (i / max(length - 1, 1)) * (w - 2 * pad)
        y = h - pad - ((v - ymin) / (ymax - ymin)) * (h - 2 * pad)
        return f"{x:.2f},{y:.2f}"

    grid = "".join(
        f'<line class="trend-grid" x1="{pad}" x2="{w - pad}" '
        f'y1="{y:.1f}" y2="{y:.1f}"/>'
        for y in (pad + 2, h / 2, h - pad - 2)
    )
    cur_path = " ".join(pt(i, v, n) for i, v in enumerate(current))
    cmp_path = ""
    if compare and len(compare) >= 2:
        cpts = " ".join(pt(i, v, len(compare)) for i, v in enumerate(compare))
        cmp_path = (
            f'<polyline class="trend-line is-cmp" fill="none" points="{cpts}"/>'
        )
    return (
        f'<div class="trend-chart" role="img">'
        f'<svg viewBox="0 0 {w:.0f} {h:.0f}" preserveAspectRatio="none">'
        f"{grid}{cmp_path}"
        f'<polyline class="trend-line is-cur" fill="none" points="{cur_path}"/>'
        f"</svg></div>"
    )


def _viz_period_bars(series: list[float] | None) -> str:
    """Mini vertical bars for period points (GA4 exploration-like)."""
    if not series:
        return '<div class="period-bars is-empty" aria-hidden="true"></div>'
    peak = max(abs(v) for v in series) or 1.0
    floor = min(series)
    # Shift so shortest bar still shows when all positive
    base = min(0.0, floor) if floor < 0 else 0.0
    span = peak - base or 1.0
    cells = []
    for i, v in enumerate(series):
        ht = max(8.0, 100.0 * (v - base) / span)
        cls = "is-last" if i == len(series) - 1 else ""
        cells.append(f'<i class="period-bar {cls}" style="height:{ht:.1f}%"></i>')
    return f'<div class="period-bars">{"".join(cells)}</div>'


def _viz_compare_bars(
    *,
    current: float | None,
    compare: float | None,
    cur_label: str,
    cmp_label: str,
    unit: str = "",
) -> str:
    """GA4-like dual horizontal bars: current vs prior (or vs 目安)."""
    vals = [v for v in (current, compare) if v is not None]
    peak = max((abs(v) for v in vals), default=1.0) or 1.0
    if unit == "%" and peak <= 120:
        peak = 100.0

    def bar(v: float | None, cls: str, lab: str) -> str:
        if v is None:
            return (
                f'<div class="compare-row">'
                f'<span class="compare-k">{escape(lab)}</span>'
                f'<div class="compare-track"><i class="compare-fill {cls}" style="width:0"></i></div>'
                f'<span class="compare-n">—</span></div>'
            )
        w = max(2.0, min(100.0, 100.0 * abs(v) / peak))
        if unit:
            shown = _fmt_num(v, unit)
        elif abs(v - round(v)) < 1e-9:
            shown = f"{int(round(v)):,}"
        else:
            shown = f"{v:g}"
        return (
            f'<div class="compare-row">'
            f'<span class="compare-k">{escape(lab)}</span>'
            f'<div class="compare-track"><i class="compare-fill {cls}" style="width:{w:.1f}%"></i></div>'
            f'<span class="compare-n">{escape(shown)}</span></div>'
        )

    empty_cls = " is-empty" if not vals else ""
    return (
        f'<div class="compare-bars{empty_cls}">'
        f'{bar(current, "is-cur", cur_label)}'
        f'{bar(compare, "is-cmp", cmp_label)}'
        f"</div>"
    )


def _viz_row_meta(
    r: dict[str, Any],
    info: dict[str, Any] | None,
    *,
    prefer_delta: bool = False,
) -> str:
    if prefer_delta and r.get("delta"):
        return f'<span class="viz-meta">{escape(str(r["delta"]))}</span>'
    if info and info.get("gap") and info["gap"] != "—":
        return (
            f'<span class="bench-gap tone-{escape(info["tone"])}">'
            f'{escape(info["gap"])}'
            f'{" " + escape(info["arrow"]) if info.get("arrow") else ""}'
            f"</span>"
        )
    if r.get("delta"):
        return f'<span class="viz-meta">{escape(str(r["delta"]))}</span>'
    return '<span class="bench-gap tone-na">—</span>'


def _viz_rows_html(
    rows: list[dict[str, Any]],
    *,
    locale: str,
    mode: str,
) -> str:
    """Shared rows for gauge / compare / trend / bar view modes."""
    focus = escape(t("focus", locale))
    out: list[str] = []
    for r in rows:
        label = escape(str(r.get("label") or r.get("name") or ""))
        value = escape(str(r.get("value") or ""))
        cur = _row_value_num(r)
        bench_val = r.get("value_num") if r.get("value_num") is not None else cur
        info = _bench_info(bench_val if r.get("bench") else None, r.get("bench"))
        prior = _prior_from_delta(cur, r.get("delta"))
        mid = float(info["mid"]) if info and info.get("mid") is not None else None
        unit = str((info or {}).get("unit") or "")

        if mode == "compare":
            if prior is not None:
                viz = _viz_compare_bars(
                    current=cur,
                    compare=prior,
                    cur_label=t("compare.current", locale),
                    cmp_label=t("compare.prior", locale),
                    unit=unit,
                )
            elif mid is not None and cur is not None:
                viz = _viz_compare_bars(
                    current=cur,
                    compare=mid,
                    cur_label=t("compare.current", locale),
                    cmp_label=t("compare.bench", locale),
                    unit=unit,
                )
            else:
                viz = _viz_compare_bars(
                    current=cur,
                    compare=None,
                    cur_label=t("compare.current", locale),
                    cmp_label=t("compare.prior", locale),
                    unit=unit,
                )
            meta = _viz_row_meta(r, info, prefer_delta=True)
        elif mode == "trend":
            if cur is None:
                viz = _viz_trend_svg(None)
            else:
                series, cmp_s = _synthetic_series(
                    cur, prior=prior, mid=mid, seed=str(r.get("id") or label)
                )
                viz = _viz_trend_svg(series, cmp_s)
            meta = _viz_row_meta(r, info, prefer_delta=True)
        elif mode == "bar":
            if cur is None:
                viz = _viz_period_bars(None)
            else:
                series, _ = _synthetic_series(
                    cur, prior=prior, mid=mid, seed=str(r.get("id") or label)
                )
                viz = _viz_period_bars(series)
            meta = _viz_row_meta(r, info, prefer_delta=True)
        else:
            viz = _viz_band_gauge(info, kind="dial" if mode == "gauge" else "band")
            meta = _viz_row_meta(r, info)

        out.append(
            f'<div class="viz-row{" is-focus" if r.get("focus") else ""}">'
            f'{_help_btn(str(r["id"]), str(r.get("label") or r.get("name") or ""), locale)}'
            f'<span class="viz-name">{label}'
            f'{f" <span class=\'focus-tag\'>{focus}</span>" if r.get("focus") else ""}'
            f"</span>"
            f'<span class="viz-value">{value}</span>'
            f'<div class="viz-plot">{viz}</div>'
            f"{meta}"
            f"</div>"
        )
    return "".join(out)


def _dense_metric_table(*, body_rows: str, locale: str) -> str:
    return f"""
                <table class="dense">
                  <thead>
                    <tr>
                      <th class="help-col">{escape(t("col.help", locale))}</th>
                      <th>{escape(t("col.metric", locale))}</th>
                      <th style="text-align:right">{escape(t("col.value", locale))}</th>
                      <th style="text-align:right">{escape(t("col.bench", locale))}</th>
                      <th style="text-align:right">{escape(t("col.gap", locale))}</th>
                    </tr>
                  </thead>
                  <tbody>{body_rows}</tbody>
                </table>
    """


def _metric_panel_html(
    *,
    section_id: str,
    title: str,
    sub: str,
    switch: str,
    parts: dict[str, Any],
    foot: str = "",
    locale: str = "ja",
    extra_panes: str = "",
) -> str:
    return f"""
          <section class="panel" id="panel-{escape(section_id)}">
            <div class="panel-head">
              <div class="panel-head-left">
                <h2>{escape(title)}</h2>
                <span class="sub" data-count-sub="{escape(section_id)}">{escape(sub)}</span>
              </div>
              {switch}
            </div>
            <div class="panel-body" data-section-body="{escape(section_id)}" data-view-mode="list">
              <div class="mode-pane mode-list">
                {_dense_metric_table(body_rows=parts["rows"], locale=locale)}
              </div>
              <div class="mode-pane mode-card">{parts["cards"]}</div>
              {extra_panes}
            </div>
            <div class="panel-foot">{foot}</div>
          </section>
    """


def _channel_stack_html(channels: list[dict[str, Any]], locale: str) -> str:
    """Share stack for inflow mix."""
    segs = "".join(
        f'<i class="chan-stack-seg" style="width:{c["pct"]}%;background:{escape(c["color"])}" '
        f'title="{escape(c["name"])} {c["pct"]}%"></i>'
        for c in channels
        if c.get("pct")
    )
    if not segs:
        return ""
    return (
        f'<div class="chan-stack" role="img" aria-label="{escape(t("panel.channels", locale))}">'
        f"{segs}</div>"
    )


def _rail_nav_html(
    *,
    industry: str,
    pack_links: list[tuple[str, str]] | list[tuple[str, str, str]] | None = None,
    nav_active: str,
    connected: dict[str, str] | None = None,
    pack_groups: list[tuple[str, str, list[tuple[str, str, str]]]] | None = None,
    locale: str = "ja",
) -> str:
    """サンプルパック（カテゴリ内訳）/ 接続済み / アプリ — separate categories."""

    def _pack_link(slug: str, label: str, hint: str) -> str:
        on = "is-on" if nav_active == f"pack:{slug}" else ""
        shown_label = pack_text(slug, "label", locale, label)
        shown_hint = pack_text(slug, "hint", locale, hint) if hint else ""
        hint_html = (
            f'<span class="pack-hint">{escape(shown_hint)}</span>' if shown_hint else ""
        )
        q = f"{shown_label} {shown_hint} {slug}".strip().lower()
        return (
            f'<a href="/{escape(slug)}" class="{on}" data-pack-q="{escape(q)}">'
            f'<span class="pack-name">{escape(shown_label)}</span>{hint_html}</a>'
        )

    if pack_groups is None:
        from sitekpi.packs import packs_by_category

        pack_groups = packs_by_category()
    elif not pack_groups and pack_links:
        items: list[tuple[str, str, str]] = []
        for item in pack_links:
            if len(item) >= 3:
                items.append((item[0], item[1], item[2]))
            else:
                items.append((item[0], item[1], ""))
        pack_groups = [("all", t("cat.all", locale), items)]

    active_slug = ""
    if nav_active.startswith("pack:"):
        active_slug = nav_active.removeprefix("pack:")

    pack_nav_parts: list[str] = []
    for cid, cat_label, items in pack_groups:
        links = "".join(_pack_link(s, lab, h) for s, lab, h in items)
        is_open = active_slug and any(s == active_slug for s, _, _ in items)
        open_attr = " open" if is_open else ""
        shown = t(f"cat.{cid}", locale) if cid != "all" else cat_label
        if shown.startswith("cat."):
            shown = cat_label
        pack_nav_parts.append(
            f'<details class="pack-cat"{open_attr}>'
            f'<summary><span class="pack-cat-label">{escape(shown)}</span></summary>'
            f'<div class="pack-cat-body">{links}</div></details>'
        )
    pack_nav = "".join(pack_nav_parts)

    if connected:
        live_cls = "is-on" if nav_active == "live" else ""
        connected_nav = (
            f'<a href="/live" class="{live_cls}" title="{escape(connected.get("email") or "")}">'
            f'{escape(connected.get("name") or t("nav.property", locale))}</a>'
            f'<a href="/connect" class="nav-add">{escape(t("nav.change_property", locale))}</a>'
        )
    else:
        connected_nav = (
            f'<a href="/connect" class="nav-muted">{escape(t("nav.disconnected", locale))}</a>'
            f'<a href="/connect" class="nav-add">{escape(t("nav.add_ga4", locale))}</a>'
        )

    search = f"""
        <div class="pack-search-wrap">
          <label class="visually-hidden" for="pack-search">{escape(t("nav.pack_search", locale))}</label>
          <input type="search" id="pack-search" class="pack-search"
            placeholder="{escape(t("nav.pack_search_ph", locale))}"
            autocomplete="off" data-pack-search />
          <p class="pack-search-empty" data-pack-search-empty hidden>
            {escape(t("nav.pack_search_empty", locale))}
          </p>
        </div>
    """
    return f"""
        <div class="nav-group">{escape(t("nav.samples", locale))}</div>
        {search}
        <div class="nav-sub" role="navigation" aria-label="{escape(t("nav.packs_aria", locale))}" data-pack-nav>{pack_nav}</div>
        <div class="nav-group">{escape(t("nav.connected", locale))}</div>
        <div class="nav-sub" role="navigation" aria-label="{escape(t("nav.ga4_aria", locale))}">{connected_nav}</div>
        <div class="nav-group">{escape(t("nav.app", locale))}</div>
        <a href="/builder" class="{"is-on" if nav_active == "builder" else ""}">{escape(t("nav.builder", locale))}</a>
        <a href="/connect" class="{"is-on" if nav_active == "connect" else ""}">{escape(t("nav.connect", locale))}</a>
        <a href="/settings" class="{"is-on" if nav_active == "settings" else ""}">{escape(t("nav.settings", locale))}</a>
        <script>
        (function () {{
          if (window.__sitekpiPackSearch) return;
          window.__sitekpiPackSearch = true;
          const input = document.querySelector("[data-pack-search]");
          const empty = document.querySelector("[data-pack-search-empty]");
          const nav = document.querySelector("[data-pack-nav]");
          if (!input || !nav) return;
          const cats = () => Array.from(nav.querySelectorAll(".pack-cat"));
          input.addEventListener("input", () => {{
            const q = (input.value || "").trim().toLowerCase();
            let any = false;
            cats().forEach((cat) => {{
              let hit = false;
              cat.querySelectorAll(".pack-cat-body a").forEach((a) => {{
                const hay = (a.getAttribute("data-pack-q") || a.textContent || "").toLowerCase();
                const show = !q || hay.includes(q);
                a.hidden = !show;
                if (show) hit = true;
              }});
              cat.hidden = Boolean(q) && !hit;
              if (q && hit) cat.open = true;
              if (hit) any = true;
            }});
            if (empty) empty.hidden = !(q && !any);
          }});
        }})();
        </script>
    """


def render_sample_dense(
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
) -> str:
    global _ACTIVE_BENCH
    loc = normalize_locale(locale)

    # Prefer caller-supplied pack data (route) — avoid importing main on every request
    if data is None or ind is None or benches_raw is None:
        from sitekpi.packs import BENCHMARKS, DEMO, INDUSTRIES

        ind = ind or INDUSTRIES[industry]
        data = data or DEMO[industry][period]
        benches_raw = benches_raw or BENCHMARKS[industry]
    if pack_groups is None and pack_links is None:
        from sitekpi.packs import pack_links as _pack_links, packs_by_category

        pack_links = _pack_links()
        pack_groups = packs_by_category()

    if not nav_active:
        nav_active = f"pack:{industry}"

    rail_nav = _rail_nav_html(
        industry=industry,
        pack_links=pack_links,
        pack_groups=pack_groups,
        nav_active=nav_active,
        connected=connected,
        locale=loc,
    )

    board = build_dense_board(
        industry=industry,
        period=period,
        ind=ind,
        data=data,
        benches_raw=benches_raw,
        locale=loc,
    )
    _ACTIVE_BENCH = board["benches"]
    SUMMARY = board["summary"]
    FUNNEL_ROWS = board["funnel"]
    ENGAGE_ROWS = board["engage"]
    AUDIENCE_ROWS = board["audience"]
    EVENTS = board["events"]
    CHANNELS = board["channels"]
    BUSINESS = board["business"]
    NEXT_WATCH = board["next_watch"]
    industry_label = industry_label or board["industry_label"]
    industry_note = industry_note or board["industry_note"]
    if industry_note in ("", "業界パック見本"):
        industry_note = t("sample_meta", loc)
    prop = property_name or board["property_name"]
    period_label = t("period.28d" if period == "28d" else "period.7d", loc)
    pack_meta = f"{industry_note} · {prop} · {period_label}"
    focus_line = board.get("focus_line") or ""
    focus_tag = escape(t("focus", loc))
    primary_tag = escape(t("primary_tag", loc))

    summary_html = "".join(
        f"""
        <div class="sum-item{" is-focus" if k.get("focus") else ""}">
          <div class="sum-head">
            {_help_btn(k["id"], k["label"], loc)}
            <div class="sum-label" title="{escape(k["label"])}">{escape(k["label"])}</div>
            {f"<span class='focus-tag'>{focus_tag}</span>" if k.get("focus") else ""}
          </div>
          <div class="sum-value">{escape(k["value"])}</div>
          <div class="sum-delta tone-{escape(k["tone"])}">{escape(k["delta"])} <span class="vs">{escape(t("vs_prev", loc))}</span></div>
          {_bench_block(_bench_info(k.get("value_num"), k.get("bench")), loc, viz="gap")}
        </div>
        """
        for k in SUMMARY
    )
    funnel = _metric_table_parts(FUNNEL_ROWS, locale=loc)
    engage = _metric_table_parts(ENGAGE_ROWS, locale=loc)
    audience = _metric_table_parts(AUDIENCE_ROWS, locale=loc)
    channel_stack = _channel_stack_html(CHANNELS, loc)
    is_sample = board_kind != "live"
    series_note = (
        f'<p class="series-note">{escape(t("series.sample_note", loc))}</p>'
        if is_sample
        else ""
    )
    audience_compare = _viz_rows_html(AUDIENCE_ROWS, locale=loc, mode="compare")
    audience_trend = (
        _viz_rows_html(AUDIENCE_ROWS, locale=loc, mode="trend") if is_sample else ""
    )
    audience_bars = (
        _viz_rows_html(AUDIENCE_ROWS, locale=loc, mode="bar") if is_sample else ""
    )
    engage_compare = _viz_rows_html(ENGAGE_ROWS, locale=loc, mode="compare")
    engage_trend = (
        _viz_rows_html(ENGAGE_ROWS, locale=loc, mode="trend") if is_sample else ""
    )
    engage_bars = (
        _viz_rows_html(ENGAGE_ROWS, locale=loc, mode="bar") if is_sample else ""
    )
    funnel_compare = _viz_rows_html(FUNNEL_ROWS, locale=loc, mode="compare")
    event_preview = 6
    event_rows = "".join(
        f"""
        <tr{" class='" + " ".join(x for x in ("is-more" if i >= event_preview else "", "is-focus" if e.get("focus") else "") if x) + "'" if (i >= event_preview or e.get("focus")) else ""}>
          <td class="help-cell">{_help_btn(e["id"], e["name"], loc)}</td>
          <td class="name-cell"><code>{escape(e["name"])}</code>{f" <span class='focus-tag'>{primary_tag}</span>" if e.get("focus") else ""}</td>
          <td class="num">{e["count"]:,}</td>
          <td class="num muted">{escape(e["delta"])}</td>
        </tr>
        """
        for i, e in enumerate(EVENTS)
    )
    event_cards = "".join(
        f"""
        <article class="metric-card{" is-more" if i >= event_preview else ""}{" is-focus" if e.get("focus") else ""}">
          <div class="metric-card-head">
            {_help_btn(e["id"], e["name"], loc)}
            <code class="metric-card-name">{escape(e["name"])}</code>
            {f"<span class='focus-tag'>{primary_tag}</span>" if e.get("focus") else ""}
          </div>
          <div class="metric-card-value">{e["count"]:,}</div>
          <div class="metric-card-delta">{escape(e["delta"])}</div>
        </article>
        """
        for i, e in enumerate(EVENTS)
    )
    event_max = max((e["count"] for e in EVENTS), default=1) or 1
    event_bars = "".join(
        f"""
        <div class="bar-row{" is-more" if i >= event_preview else ""}{" is-focus" if e.get("focus") else ""}">
          <div class="bar-meta">
            {_help_btn(e["id"], e["name"], loc)}
            <code class="compact-name">{escape(e["name"])}</code>
            {f"<span class='focus-tag'>{primary_tag}</span>" if e.get("focus") else ""}
            <span class="compact-value">{e["count"]:,}</span>
          </div>
          <div class="rank-bar"><i style="width:{max(2, round(100 * e["count"] / event_max))}%"></i></div>
        </div>
        """
        for i, e in enumerate(EVENTS)
    )
    event_more_n = max(0, len(EVENTS) - event_preview)
    channel_list = "".join(
        f"""
        <div class="chan">
          <div class="chan-meta">
            {_help_btn(c["id"], c["name"], loc)}
            <span class="row-name">{escape(c["name"])}</span>
            <strong>{c["pct"]}%</strong>
          </div>
          <div class="chan-bar"><i style="width:{c["pct"]}%;background:{escape(c["color"])}"></i></div>
        </div>
        """
        for c in CHANNELS
    )
    channel_stack_mode = (
        f"{channel_stack}"
        + "".join(
            f"""
        <div class="chan">
          <div class="chan-meta">
            {_help_btn(c["id"], c["name"], loc)}
            <span class="row-name">{escape(c["name"])}</span>
            <strong>{c["pct"]}%</strong>
          </div>
        </div>
        """
            for c in CHANNELS
        )
    )
    channel_cards = "".join(
        f"""
        <article class="metric-card">
          <div class="metric-card-head">
            {_help_btn(c["id"], c["name"], loc)}
            <span class="metric-card-name">{escape(c["name"])}</span>
          </div>
          <div class="metric-card-value">{c["pct"]}%</div>
          <div class="chan-bar"><i style="width:{c["pct"]}%;background:{escape(c["color"])}"></i></div>
        </article>
        """
        for c in CHANNELS
    )
    channel_bars = "".join(
        f"""
        <div class="bar-row">
          <div class="bar-meta">
            {_help_btn(c["id"], c["name"], loc)}
            <span class="compact-name">{escape(c["name"])}</span>
            <span class="compact-value">{c["pct"]}%</span>
          </div>
          <div class="rank-bar"><i style="width:{c["pct"]}%;background:{escape(c["color"])}"></i></div>
        </div>
        """
        for c in CHANNELS
    )
    def _biz_status(b: dict[str, Any]) -> str:
        linked = b.get("value") not in (None, "", "—", "–")
        if linked:
            return f'<span class="biz-status is-linked">{escape(t("biz.linked", loc))}</span>'
        return f'<span class="biz-status is-unlinked">{escape(t("biz.unlinked", loc))}</span>'

    biz_rows = "".join(
        f"""
        <tr>
          <td class="help-cell">{_help_btn(b["id"], b["label"], loc)}</td>
          <td class="name-cell"><span class="row-name">{escape(b["label"])}</span>
            {_biz_status(b)}</td>
          <td class="num na">{escape(b["value"])}</td>
          {_bench_cells(
              _bench_info(b.get("value_num"), b.get("bench"))
              if b.get("value") not in (None, "", "—", "–")
              else None,
              loc,
              viz="none",
          )}
        </tr>
        """
        for b in BUSINESS
    )
    biz_cards = "".join(
        f"""
        <article class="metric-card">
          <div class="metric-card-head">
            {_help_btn(b["id"], b["label"], loc)}
            <span class="metric-card-name">{escape(b["label"])}</span>
            {_biz_status(b)}
          </div>
          <div class="metric-card-value na">{escape(b["value"])}</div>
          {_bench_block(
              _bench_info(b.get("value_num"), b.get("bench"))
              if b.get("value") not in (None, "", "—", "–")
              else None,
              loc,
              viz="none",
          )}
        </article>
        """
        for b in BUSINESS
    )
    # Settled modes; sample-only trend/period-bar (synthetic series)
    events_switch = _section_view_switch("events", ["list", "card", "bar"], loc)
    channels_switch = _section_view_switch(
        "channels", ["list", "card", "bar", "stack"], loc
    )
    funnel_switch = _section_view_switch(
        "funnel", ["list", "card", "compare"], loc
    )
    engage_modes = (
        ["list", "card", "bar", "compare", "trend"]
        if is_sample
        else ["list", "card", "compare"]
    )
    audience_modes = (
        ["list", "card", "bar", "compare", "trend"]
        if is_sample
        else ["list", "card", "compare"]
    )
    engage_switch = _section_view_switch("engage", engage_modes, loc)
    audience_switch = _section_view_switch("audience", audience_modes, loc)
    biz_switch = _section_view_switch("biz", ["list", "card"], loc)
    next_html = "".join(
        f"""
        <li>
          <strong>{escape(title)}</strong>
          <span>{escape(body)}</span>
        </li>
        """
        for title, body in NEXT_WATCH
    )
    close_label = t("close", loc)
    event_sub_open = t("count_n", loc, n=len(EVENTS))
    event_sub_closed = (
        t("count_more", loc, shown=event_preview, more=event_more_n)
        if event_more_n
        else event_sub_open
    )

    def _more_footer(section: str, more_n: int) -> str:
        if more_n <= 0:
            return ""
        return f"""
        <div class="more-wrap" data-more-wrap="{escape(section)}">
          <div class="more-fade" aria-hidden="true"></div>
          <button type="button" class="more-chip" data-more="{escape(section)}">
            {escape(t("more_n", loc, n=more_n))}
          </button>
        </div>
        """

    event_toggle = _more_footer("events", event_more_n)
    event_sub = event_sub_closed
    funnel_panel = _metric_panel_html(
        section_id="funnel",
        title=t("panel.funnel", loc),
        sub=funnel["sub"],
        switch=funnel_switch,
        parts=funnel,
        locale=loc,
        extra_panes=(
            f'<div class="mode-pane mode-compare">{funnel_compare}</div>'
        ),
    )
    engage_panel = _metric_panel_html(
        section_id="engage",
        title=t("panel.engage", loc),
        sub=engage["sub"],
        switch=engage_switch,
        parts=engage,
        locale=loc,
        extra_panes=(
            (
                f'<div class="mode-pane mode-bar">{series_note}{engage_bars}</div>'
                f'<div class="mode-pane mode-trend">{series_note}{engage_trend}</div>'
                if is_sample
                else ""
            )
            + f'<div class="mode-pane mode-compare">{engage_compare}</div>'
        ),
    )
    audience_panel = _metric_panel_html(
        section_id="audience",
        title=t("panel.audience", loc),
        sub=audience["sub"],
        switch=audience_switch,
        parts=audience,
        locale=loc,
        extra_panes=(
            (
                f'<div class="mode-pane mode-bar">{series_note}{audience_bars}</div>'
                f'<div class="mode-pane mode-trend">{series_note}{audience_trend}</div>'
                if is_sample
                else ""
            )
            + f'<div class="mode-pane mode-compare">{audience_compare}</div>'
        ),
    )

    all_help_items = (
        SUMMARY
        + FUNNEL_ROWS
        + ENGAGE_ROWS
        + AUDIENCE_ROWS
        + EVENTS
        + CHANNELS
        + BUSINESS
    )
    dialogs = _dialogs_from_items(all_help_items, locale=loc)
    title_suffix = t("sample_title_suffix", loc)
    # Live boards pass a custom industry_note; avoid double "(sample)"
    page_title = (
        f"SiteKPI · {escape(industry_label)}"
        if industry_note and industry_note != t("sample_meta", loc)
        else f"SiteKPI · {escape(industry_label)}{escape(title_suffix)}"
    )

    return f"""<!doctype html>
<html lang="{escape(html_lang(loc))}">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{page_title}</title>
  {brand_head_links()}
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,500;600;700;800&family=IBM+Plex+Sans+JP:wght@400;500;600;700&family=Noto+Sans+JP:wght@400;500;700;800&display=swap" rel="stylesheet" />
  <style>
    {brand_logo_css()}
    :root {{
      --ink: #152033;
      --muted: #6b7788;
      --line: #e5eaf1;
      --bg: #f4f6fa;
      --panel: #ffffff;
      --accent: #2f6fed;
      --up: #0f766e;
      --down: #b45309;
      --font-ui: "IBM Plex Sans JP", "Noto Sans JP", sans-serif;
      --font-num: "DM Sans", "IBM Plex Sans JP", sans-serif;
      --rail-w: 268px;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0; min-height: 100vh; color: var(--ink);
      font-family: var(--font-ui);
      background: var(--bg);
    }}
    .shell {{
      display: grid;
      grid-template-columns: var(--rail-w) 1fr;
      min-height: 100vh;
    }}
    @media (max-width: 900px) {{
      .shell {{ grid-template-columns: 1fr; }}
      .rail {{ display: none; }}
    }}
    .rail {{
      background: #fff; color: var(--ink);
      border-right: 1px solid var(--line);
      padding: 18px 12px 20px; position: sticky; top: 0; height: 100vh;
      display: flex; flex-direction: column; min-height: 0;
      box-sizing: border-box;
      font-family: var(--font-ui);
    }}
    .rail .logo {{
      margin: 0 8px 18px; flex-shrink: 0;
    }}
    .rail nav {{
      flex: 1 1 auto; min-height: 0; overflow-y: auto; overflow-x: hidden;
      padding-right: 2px; overscroll-behavior: contain;
      scrollbar-width: thin; scrollbar-color: #cbd5e1 transparent;
    }}
    .rail nav::-webkit-scrollbar {{ width: 5px; }}
    .rail nav::-webkit-scrollbar-thumb {{
      background: #cbd5e1; border-radius: 999px;
    }}
    .rail nav a {{
      display: block; padding: 7px 10px; border-radius: 6px;
      color: #3d4a5c; text-decoration: none; font-size: 0.9rem; font-weight: 600;
      margin-bottom: 1px;
    }}
    .rail nav a:hover {{ background: #f3f6fa; color: var(--ink); }}
    .rail nav a.is-on {{ background: #eef4ff; color: var(--accent); }}
    .rail .nav-group {{
      margin: 16px 0 6px; padding: 0 10px;
      font-size: 0.66rem; font-weight: 700; letter-spacing: 0.04em;
      color: #8b97a8; text-transform: none;
    }}
    .rail .nav-group:first-child {{ margin-top: 0; }}
    .rail .pack-search-wrap {{ padding: 0 10px 8px; }}
    .rail .pack-search {{
      width: 100%; box-sizing: border-box;
      border: 1px solid var(--line); border-radius: 8px;
      padding: 7px 10px; font: inherit; font-size: 0.78rem;
      background: #fff; color: var(--ink);
    }}
    .rail .pack-search:focus {{
      outline: none; border-color: #bfd2f8; box-shadow: 0 0 0 2px #eaf1ff;
    }}
    .rail .pack-search-empty {{
      margin: 6px 0 0; font-size: 0.72rem; color: #94a3b8; font-weight: 600;
    }}
    .visually-hidden {{
      position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px;
      overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap; border: 0;
    }}
    .series-note {{
      margin: 0 0 8px; padding: 6px 10px;
      border-radius: 6px; background: #f8fafc; border: 1px solid #e8edf4;
      color: #64748b; font-size: 0.72rem; font-weight: 600; line-height: 1.4;
    }}
    .rail .nav-sub {{
      margin: 0 0 4px; padding: 0; background: transparent;
    }}
    .rail .nav-sub a {{
      font-size: 0.9rem; font-weight: 600; padding: 9px 10px;
    }}
    .rail .nav-sub a .pack-name {{
      display: block; line-height: 1.35; color: inherit; font-weight: 600;
    }}
    .rail .nav-sub a .pack-hint {{
      display: none; margin-top: 3px;
      font-size: 0.66rem; font-weight: 500; color: #8b97a8; line-height: 1.3;
    }}
    .rail .nav-sub a.is-on .pack-hint {{ display: block; color: #6b8fd4; }}
    /* Findy-like: category = Noto + chevron; packs = Plex */
    .rail .pack-cat {{ margin: 0 0 8px; border: none; background: transparent; }}
    .rail .pack-cat summary {{
      list-style: none; cursor: pointer; user-select: none;
      display: flex; align-items: center; gap: 4px;
      padding: 8px 10px; border-radius: 4px;
      font-family: "Noto Sans JP", sans-serif;
      font-size: 0.9rem; font-weight: 700; letter-spacing: 0.02em;
      color: #8b97a8; background: transparent;
    }}
    .rail .pack-cat[open] summary {{ color: #6b7788; }}
    .rail .pack-cat summary:hover {{ color: #5a6575; background: transparent; }}
    .rail .pack-cat summary::-webkit-details-marker {{ display: none; }}
    .rail .pack-cat summary::before {{
      content: "▸"; flex: 0 0 auto; width: 0.75em;
      color: #a8b2c1; font-size: 0.8rem; line-height: 1;
    }}
    .rail .pack-cat[open] summary::before {{ content: "▾"; }}
    .rail .pack-cat-label {{ flex: 1 1 auto; min-width: 0; }}
    .rail .pack-cat-body {{
      padding: 2px 0 8px; margin: 0; border: none;
    }}
    .rail .pack-cat-body a {{
      margin: 0 0 2px; padding: 9px 10px 9px 26px;
      border-radius: 6px; background: transparent;
    }}
    .rail .pack-cat-body a:hover {{ background: transparent; color: inherit; }}
    .rail .pack-cat-body a.is-on {{ background: #eef4ff; color: var(--accent); }}
    .rail .pack-cat-body a.is-on:hover {{ background: #eef4ff; color: var(--accent); }}
    .rail .pack-cat-body a .pack-name {{
      font-family: var(--font-ui);
      font-size: 0.9rem; font-weight: 600;
    }}
    .rail .nav-muted {{ color: #8b97a8 !important; font-weight: 500 !important; }}
    .rail .nav-add {{
      color: var(--accent) !important; font-size: 0.75rem !important; font-weight: 600 !important;
    }}
    .main {{ min-width: 0; }}
    .top {{
      background: var(--panel); border-bottom: 1px solid var(--line);
      padding: 14px 24px; display: flex; justify-content: space-between;
      align-items: center; gap: 12px; flex-wrap: wrap;
      position: sticky; top: 0; z-index: 10;
    }}
    .top h1 {{
      margin: 0; font-size: 1.05rem; font-weight: 800;
      font-family: var(--font-num);
    }}
    .top .meta {{ color: var(--muted); font-size: 0.82rem; font-weight: 600; }}
    .sr-only {{
      position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px;
      overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap; border: 0;
    }}
    .top-right {{
      display: flex; align-items: center; gap: 10px; flex-wrap: wrap;
    }}
    .view-switch {{
      display: inline-flex; flex-wrap: wrap; gap: 0;
      border: 1px solid var(--line); border-radius: 8px;
      overflow: hidden; background: #fff; max-width: 100%;
      justify-content: flex-end;
    }}
    .view-btn {{
      font: inherit; font-size: 0.7rem; font-weight: 700;
      padding: 5px 7px; border: none; background: transparent;
      color: var(--muted); cursor: pointer;
    }}
    .view-btn + .view-btn {{ border-left: 1px solid var(--line); }}
    .view-btn.is-on {{ background: #eaf1ff; color: #1d4ed8; }}
    .panel-head .view-switch {{ flex-shrink: 1; min-width: 0; }}
    .period select {{
      font: inherit; font-size: 0.82rem; font-weight: 700;
      padding: 7px 10px; border-radius: 8px; border: 1px solid var(--line);
      background: #fff; color: var(--ink);
    }}
    .mode-pane {{ display: none; }}
    .panel-body[data-view-mode="list"] .mode-list,
    .biz-body[data-view-mode="list"] .mode-list {{ display: block; }}
    .panel-body[data-view-mode="card"] .mode-card,
    .biz-body[data-view-mode="card"] .mode-card {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 8px;
    }}
    .panel-body[data-view-mode="bar"] .mode-bar,
    .panel-body[data-view-mode="stack"] .mode-stack,
    .panel-body[data-view-mode="compare"] .mode-compare,
    .panel-body[data-view-mode="trend"] .mode-trend {{ display: block; }}
    @media (min-width: 1400px) {{
      .panel-body[data-view-mode="card"] .mode-card,
      .biz-body[data-view-mode="card"] .mode-card {{
        grid-template-columns: repeat(3, minmax(0, 1fr));
      }}
    }}
    /* Equal row height within a section view */
    table.dense tbody tr {{
      height: 48px;
    }}
    table.dense tbody td {{
      vertical-align: middle;
    }}
    .viz-row {{
      display: grid;
      grid-template-columns: auto minmax(0, 1fr) max-content minmax(7rem, 1fr) max-content;
      gap: 8px 12px; align-items: center;
      padding: 8px 4px; border-bottom: 1px solid #f0f3f7;
      min-height: 56px; height: 56px; box-sizing: border-box;
    }}
    .viz-row:last-child {{ border-bottom: none; }}
    .viz-row.is-focus {{ background: #f5f8ff; border-radius: 6px; }}
    .viz-name {{ font-size: 0.84rem; font-weight: 700; min-width: 0; line-height: 1.25; }}
    .viz-value {{
      font-family: var(--font-num); font-weight: 800; font-size: 0.9rem;
      font-variant-numeric: tabular-nums; white-space: nowrap; line-height: 1.25;
    }}
    .viz-plot {{
      min-width: 0; height: 40px;
      display: flex; align-items: center;
    }}
    .viz-plot .bench-gauge,
    .viz-plot .gap-bar,
    .viz-plot .compare-bars,
    .viz-plot .trend-chart,
    .viz-plot .period-bars {{ max-width: none; width: 100%; }}
    .viz-meta,
    .viz-row .bench-gap {{
      font-size: 0.75rem; font-weight: 700; color: #64748b;
      font-variant-numeric: tabular-nums; white-space: nowrap;
      min-width: 4rem; text-align: right;
    }}
    .compare-bars {{
      display: flex; flex-direction: column; justify-content: center;
      gap: 4px; min-width: 0; height: 40px; width: 100%;
    }}
    .compare-bars.is-empty {{ opacity: 0.55; }}
    .compare-row {{
      display: grid;
      grid-template-columns: 2.8rem minmax(0, 1fr) max-content;
      gap: 6px; align-items: center; min-height: 16px;
    }}
    .compare-k {{
      font-size: 0.65rem; font-weight: 700; color: #94a3b8;
      letter-spacing: 0.02em;
    }}
    .compare-track {{
      height: 8px; background: #eef2f7; border-radius: 999px; overflow: hidden;
    }}
    .compare-fill {{
      display: block; height: 100%; border-radius: 999px;
    }}
    .compare-fill.is-cur {{ background: var(--accent); }}
    .compare-fill.is-cmp {{ background: #94a3b8; opacity: 0.75; }}
    .compare-n {{
      font-family: var(--font-num); font-size: 0.72rem; font-weight: 700;
      font-variant-numeric: tabular-nums; color: #475569; min-width: 3.2rem;
      text-align: right;
    }}
    .trend-chart {{
      width: 100%; height: 40px;
    }}
    .trend-chart svg {{
      display: block; width: 100%; height: 100%;
    }}
    .trend-chart.is-empty {{ opacity: 0.4; }}
    .trend-grid {{
      stroke: #e8edf4; stroke-width: 1;
    }}
    .trend-line {{
      stroke: var(--accent); stroke-width: 1.75; stroke-linejoin: round;
      stroke-linecap: round; vector-effect: non-scaling-stroke;
    }}
    .trend-line.is-cmp {{
      stroke-dasharray: 4 3; opacity: 0.85;
    }}
    .period-bars {{
      display: flex; align-items: flex-end; gap: 3px;
      width: 100%; height: 40px;
    }}
    .period-bars.is-empty {{
      opacity: 0.35; background: repeating-linear-gradient(
        to right, #eef2f7 0 8px, transparent 8px 11px
      );
      border-radius: 4px;
    }}
    .period-bar {{
      flex: 1; min-width: 0; border-radius: 2px 2px 0 0;
      background: #bfd2f8; align-self: flex-end;
    }}
    .period-bar.is-last {{ background: var(--accent); }}
    .metric-card {{
      display: flex; flex-direction: column; gap: 6px;
      padding: 10px 12px; border: 1px solid var(--line); border-radius: 10px;
      background: #fafbfd; min-height: 136px; height: 100%; box-sizing: border-box;
    }}
    .metric-card-head {{
      display: flex; align-items: center; gap: 6px; min-width: 0;
    }}
    .metric-card-name {{
      font-size: 0.82rem; font-weight: 800; min-width: 0;
      overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
    }}
    .metric-card-value {{
      font-family: var(--font-num);
      font-size: 1.25rem; font-weight: 800; font-variant-numeric: tabular-nums;
      margin-top: auto;
    }}
    .metric-card-value.na {{ color: #94a3b8; }}
    .metric-card-delta {{
      font-size: 0.75rem; font-weight: 600; color: #94a3b8;
    }}
    .metric-card .chan-bar {{ margin-top: 2px; }}
    /* Compact = same table as list, tighter chrome (bar view still uses .compact-*) */
    .compact-name {{
      font-size: 0.84rem; font-weight: 700; min-width: 0;
    }}
    .compact-value {{
      font-family: var(--font-num);
      font-size: 0.9rem; font-weight: 800; font-variant-numeric: tabular-nums;
      white-space: nowrap; justify-self: end;
    }}
    .compact-value.na {{ color: #94a3b8; }}
    .compact-delta {{
      font-size: 0.75rem; font-weight: 600; color: #94a3b8;
      justify-self: end; min-width: 4rem; text-align: right;
    }}
    .bar-row {{
      margin-bottom: 0; padding: 8px 0;
      min-height: 48px; box-sizing: border-box;
      border-bottom: 1px solid #f0f3f7;
    }}
    .bar-row:last-child {{ border-bottom: none; }}
    .bar-meta {{
      display: grid;
      grid-template-columns: auto minmax(0, 1fr) auto;
      gap: 8px; align-items: center; margin-bottom: 4px;
    }}
    .rank-bar {{
      height: 8px; background: #eef2f7; border-radius: 999px; overflow: hidden;
    }}
    .rank-bar i {{
      display: block; height: 100%; border-radius: 999px; background: var(--accent);
    }}
    .content {{
      padding: 20px 28px 48px;
      width: 100%;
      max-width: none;
      box-sizing: border-box;
    }}
    @media (min-width: 1400px) {{
      .content {{ padding-left: 32px; padding-right: 32px; }}
      .sum-value {{ font-size: 1.75rem; }}
    }}

    .summary {{
      display: grid;
      grid-template-columns: repeat(6, minmax(0, 1fr));
      gap: 10px;
      margin-bottom: 16px;
      align-items: stretch;
    }}
    @media (max-width: 1200px) {{
      .summary {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
    }}
    @media (max-width: 640px) {{
      .summary {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    }}
    .focus-banner {{
      margin: 0 0 10px; padding: 8px 12px;
      border-radius: 8px; border: 1px solid #bfd2f8;
      background: #eaf1ff; color: #1e3a8a;
      font-size: 0.8rem; font-weight: 700;
    }}
    .focus-tag {{
      font-size: 0.65rem; font-weight: 800;
      padding: 1px 6px; border-radius: 4px;
      background: #1d4ed8; color: #fff;
      letter-spacing: 0.02em; flex-shrink: 0;
    }}
    .sum-item {{
      display: flex;
      flex-direction: column;
      min-height: 168px;
      padding: 12px 12px 12px;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 10px;
      box-shadow: 0 1px 0 rgba(21,32,51,0.03);
    }}
    .sum-item.is-focus {{
      border-color: #93b4f5;
      background: linear-gradient(180deg, #f5f8ff 0%, #fff 55%);
      box-shadow: 0 0 0 1px rgba(47,111,237,0.12), 0 4px 14px rgba(47,111,237,0.08);
    }}
    tr.is-focus td,
    .metric-card.is-focus,
    .bar-row.is-focus {{
      background: #f5f8ff;
    }}
    .metric-card.is-focus {{
      border-color: #93b4f5;
    }}
    .bench-line {{
      margin-top: 8px; padding-top: 8px;
      border-top: 1px solid var(--line);
      display: flex; flex-direction: column; gap: 4px;
      min-height: 3.2em;
    }}
    .bench-line.is-empty .bench-v,
    .bench-line.is-empty .bench-gap {{
      color: #94a3b8; font-weight: 700;
    }}
    .bench-row {{
      display: flex; align-items: baseline; gap: 6px;
      font-size: 0.7rem; line-height: 1.3; flex-wrap: wrap;
    }}
    .bench-k {{
      color: var(--muted); font-weight: 700; flex-shrink: 0;
      width: 3.6em;
    }}
    .bench-v {{
      font-weight: 800; color: #1e40af; font-variant-numeric: tabular-nums;
    }}
    .bench-band {{
      color: #94a3b8; font-weight: 600; font-variant-numeric: tabular-nums;
    }}
    .bench-band::before {{ content: "帯 "; font-weight: 600; }}
    .bench-gap {{ font-weight: 800; font-variant-numeric: tabular-nums; }}
    .bench-gap.tone-up {{ color: var(--up); }}
    .bench-gap.tone-down {{ color: var(--down); }}
    .bench-gap.tone-mid {{ color: #475569; }}
    .bench-gap.tone-na {{ color: #94a3b8; }}
    td.bench-cell {{
      text-align: right; font-size: 0.78rem; line-height: 1.25;
      min-width: 6.2rem; vertical-align: middle;
    }}
    td.bench-cell .bench-gauge {{ margin: 0 0 4px; max-width: none; }}
    td.bench-cell .bench-v {{ display: block; }}
    td.bench-cell .bench-band {{ display: block; font-size: 0.68rem; }}
    td.bench-cell .bench-band::before {{ content: ""; }}
    td.bench-cell.is-empty {{ color: #94a3b8; }}
    td.bench-gap {{ font-weight: 800; white-space: nowrap; min-width: 4.2rem; }}
    .metric-card .bench-line {{
      margin-top: 4px; padding-top: 6px; min-height: 3.2em;
    }}
    .bench-gauge, .gap-bar {{ width: 100%; max-width: 11rem; }}
    .bench-gauge-track, .gap-bar-track {{
      position: relative; height: 8px; border-radius: 999px;
      background: #eef2f7; overflow: visible;
    }}
    .bench-gauge.kind-dial .bench-gauge-track {{ height: 12px; }}
    .bench-gauge.is-empty .bench-gauge-track,
    .gap-bar.is-empty .gap-bar-track {{ opacity: 0.45; }}
    .bench-gauge-zone {{
      position: absolute; top: 0; bottom: 0;
      background: #cfe0ff; border-radius: 999px;
    }}
    .bench-gauge-mid {{
      position: absolute; top: -2px; bottom: -2px; width: 2px;
      margin-left: -1px; background: #64748b; border-radius: 1px;
    }}
    .bench-gauge-val {{
      position: absolute; top: 50%; width: 10px; height: 10px;
      margin: -5px 0 0 -5px; border-radius: 50%;
      background: var(--accent); box-shadow: 0 0 0 2px #fff;
    }}
    .bench-gauge.kind-dial .bench-gauge-val {{
      width: 12px; height: 12px; margin: -6px 0 0 -6px;
    }}
    .bench-gauge-val.tone-up {{ background: var(--up); }}
    .bench-gauge-val.tone-down {{ background: var(--down); }}
    .bench-gauge-val.tone-mid {{ background: #64748b; }}
    .bench-gauge-val.tone-na {{ background: #94a3b8; }}
    .gap-bar {{ margin-bottom: 2px; max-width: none; }}
    .gap-bar-fill {{
      position: absolute; top: 0; bottom: 0; border-radius: 999px;
      background: #bfd2f8; opacity: 0.9;
    }}
    .gap-bar-fill.tone-up {{ background: rgba(15, 118, 110, 0.35); }}
    .gap-bar-fill.tone-down {{ background: rgba(185, 28, 28, 0.28); }}
    .gap-bar-fill.tone-mid {{ background: rgba(100, 116, 139, 0.3); }}
    .gap-bar-mid {{
      position: absolute; top: -3px; bottom: -3px; width: 2px;
      margin-left: -1px; background: #64748b;
    }}
    .gap-bar-val {{
      position: absolute; top: 50%; width: 9px; height: 9px;
      margin: -4.5px 0 0 -4.5px; border-radius: 50%;
      background: var(--accent); box-shadow: 0 0 0 2px #fff;
    }}
    .gap-bar-val.tone-up {{ background: var(--up); }}
    .gap-bar-val.tone-down {{ background: var(--down); }}
    .gap-bar-val.tone-mid {{ background: #64748b; }}
    .chan-stack {{
      display: flex; height: 12px; border-radius: 999px; overflow: hidden;
      background: #eef2f7; margin: 0 0 14px;
    }}
    .chan-stack-seg {{ display: block; height: 100%; min-width: 2px; }}
    .biz-status {{
      display: inline-block; margin-left: 6px; padding: 1px 6px;
      border-radius: 4px; font-size: 0.65rem; font-weight: 700;
      vertical-align: middle; letter-spacing: 0.02em;
    }}
    .biz-status.is-unlinked {{
      background: #f1f5f9; color: #94a3b8; border: 1px solid #e2e8f0;
    }}
    .biz-status.is-linked {{
      background: #ecfdf5; color: #0f766e; border: 1px solid #a7f3d0;
    }}
    .bar-row.is-focus .rank-bar i {{
      box-shadow: inset 0 0 0 1px rgba(47,111,237,0.35);
    }}
    .bar-row.is-focus .compact-name {{ color: var(--accent); }}
    .sum-head {{
      display: grid;
      grid-template-columns: auto 1fr auto;
      align-items: center;
      gap: 6px;
      min-height: 1.5em;
      margin-bottom: 10px;
    }}
    .sum-label {{
      font-size: 0.76rem; font-weight: 800; color: var(--ink);
      line-height: 1.25;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      min-width: 0;
    }}
    .sum-value {{
      font-family: var(--font-num);
      font-size: 1.55rem; font-weight: 800; letter-spacing: -0.02em;
      line-height: 1.1; color: #0b1b33;
      font-variant-numeric: tabular-nums;
      margin-top: auto;
    }}
    .sum-delta {{
      margin-top: 6px; font-size: 0.75rem; font-weight: 700;
      min-height: 1.2em;
    }}
    .sum-delta .vs {{ color: var(--muted); font-weight: 600; margin-left: 2px; }}
    .tone-up {{ color: var(--up); }}
    .tone-down {{ color: var(--down); }}

    .insights {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 14px 16px 16px;
      margin-bottom: 14px;
    }}
    .insights h2 {{
      margin: 0 0 10px; font-size: 0.95rem; font-weight: 800;
    }}
    .insights ol {{
      list-style: none; margin: 0; padding: 0;
      display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px;
    }}
    @media (max-width: 900px) {{
      .insights ol {{ grid-template-columns: 1fr; }}
    }}
    .insights li {{
      padding: 10px 12px; border-left: 3px solid var(--accent);
      background: #f8fafc; border-radius: 0 8px 8px 0;
    }}
    .insights strong {{ display: block; font-size: 0.86rem; margin-bottom: 4px; }}
    .insights span {{ font-size: 0.8rem; color: var(--muted); line-height: 1.5; }}

    .grid-2 {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 14px;
      margin-bottom: 14px;
      align-items: stretch;
    }}
    @media (min-width: 1600px) {{
      .grid-2 {{ gap: 18px; }}
    }}
    @media (max-width: 1100px) {{ .grid-2 {{ grid-template-columns: 1fr; }} }}

    .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 14px 16px 14px;
      display: flex;
      flex-direction: column;
      min-height: 0;
    }}
    .panel-head {{
      display: flex; justify-content: space-between; align-items: center;
      gap: 10px; margin-bottom: 10px; flex-shrink: 0; flex-wrap: wrap;
    }}
    .panel-head-left {{
      display: flex; align-items: baseline; gap: 8px; min-width: 0;
    }}
    .panel-head h2 {{ margin: 0; font-size: 0.95rem; font-weight: 800; }}
    .panel-head .sub {{ font-size: 0.75rem; color: var(--muted); font-weight: 600; }}
    .panel-body {{ flex: 1; min-height: 0; }}
    .panel-foot {{
      margin-top: 0; flex-shrink: 0; position: relative;
    }}
    .more-wrap {{
      position: relative;
      display: flex; justify-content: center;
      padding: 4px 0 2px;
    }}
    .more-fade {{
      position: absolute; left: 0; right: 0; bottom: 100%;
      height: 36px;
      background: linear-gradient(to bottom, rgba(255,255,255,0), #fff 85%);
      pointer-events: none;
    }}
    .more-chip {{
      position: relative; z-index: 1;
      font: inherit; font-size: 0.8rem; font-weight: 800;
      padding: 8px 14px; border-radius: 999px;
      border: 1px solid #bfd2f8; background: #eaf1ff; color: #1d4ed8;
      cursor: pointer; box-shadow: 0 4px 12px rgba(47,111,237,0.12);
    }}
    .more-chip:hover {{ background: #dbe7ff; }}
    .panel.is-expanded .more-fade {{ display: none; }}
    .panel.is-expanded .more-chip {{
      background: #fff; border-color: var(--line); color: var(--muted);
      box-shadow: none; font-weight: 700;
    }}
    .is-more {{ display: none !important; }}
    .panel.is-expanded tr.is-more {{ display: table-row !important; }}
    .panel.is-expanded .metric-card.is-more {{ display: flex !important; }}
    .panel.is-expanded .bar-row.is-more {{ display: block !important; }}
    .row-name {{ font-size: 0.9rem; font-weight: 800; line-height: 1.35; }}
    .help-btn {{
      font: inherit; font-size: 0.72rem; font-weight: 700;
      padding: 2px 7px; border-radius: 6px; border: 1px solid var(--line);
      background: #fff; color: var(--muted); cursor: pointer; flex-shrink: 0;
      line-height: 1.2; white-space: nowrap;
    }}
    .help-btn:hover {{ border-color: #bfd2f8; color: var(--accent); background: #eaf1ff; }}

    /* Full width; 説明 fixed, 指標 ~1/3, remaining cols share leftover evenly */
    table.dense {{
      width: 100%; border-collapse: collapse; font-size: 0.84rem;
      table-layout: fixed;
    }}
    table.dense th {{
      text-align: left; font-size: 0.7rem; font-weight: 700;
      color: var(--muted); letter-spacing: 0.04em;
      padding: 6px 8px; border-bottom: 1px solid var(--line);
      white-space: nowrap;
    }}
    table.dense th.help-col,
    table.dense td.help-cell {{
      width: 4.5rem; text-align: left; white-space: nowrap;
    }}
    table.dense td {{
      padding: 11px 8px; border-bottom: 1px solid #f0f3f7;
      vertical-align: middle;
    }}
    table.dense td.num.muted {{
      color: #94a3b8; font-weight: 600; font-size: 0.82rem;
    }}
    table.dense th:nth-child(2),
    table.dense td.name-cell {{
      width: 32%; padding-right: 14px;
      overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
    }}
    table.dense tr:last-child td {{ border-bottom: none; }}
    table.dense td.num {{
      font-family: var(--font-num);
      font-weight: 800; font-variant-numeric: tabular-nums;
      text-align: right; white-space: nowrap;
      font-size: 0.95rem;
      padding-left: 10px;
    }}
    table.dense td.muted {{ color: var(--muted); font-weight: 600; }}
    table.dense td.na {{ color: #94a3b8; }}
    code {{
      font-size: 0.92em; background: #f1f5f9; padding: 2px 6px;
      border-radius: 4px; font-weight: 800;
    }}
    .chan {{
      margin-bottom: 0; padding: 10px 0;
      min-height: 48px; box-sizing: border-box;
      border-bottom: 1px solid #f0f3f7;
    }}
    .chan:last-child {{ border-bottom: none; }}
    .chan-meta {{
      display: grid;
      grid-template-columns: auto minmax(0, 1fr) auto;
      gap: 8px;
      align-items: center; margin-bottom: 5px;
    }}
    .chan-meta .row-name {{
      min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
    }}
    .chan-meta strong {{
      font-family: var(--font-num);
      font-size: 0.95rem; font-weight: 800;
      width: 2.8rem; text-align: right;
    }}
    .chan-bar {{
      height: 6px; background: #eef2f7; border-radius: 999px; overflow: hidden;
    }}
    .chan-bar i {{ display: block; height: 100%; border-radius: 999px; }}

    .help-dialog {{
      border: 1px solid var(--line); border-radius: 14px; padding: 0;
      width: min(440px, calc(100vw - 32px));
      box-shadow: 0 18px 48px rgba(21,32,51,0.18);
    }}
    .help-dialog::backdrop {{ background: rgba(21,32,51,0.28); }}
    .help-sheet {{ margin: 0; padding: 18px; }}
    .help-sheet header {{
      display: flex; justify-content: space-between; gap: 12px;
      align-items: flex-start; margin-bottom: 12px;
    }}
    .help-sheet h3 {{
      margin: 0; font-size: 1.15rem; font-weight: 800;
      font-family: var(--font-num);
    }}
    .help-kind {{
      margin: 0 0 4px; font-size: 0.72rem; font-weight: 800; color: var(--accent);
    }}
    .help-close {{
      width: 32px; height: 32px; border-radius: 8px; border: 1px solid var(--line);
      background: #fff; font-size: 1.1rem; cursor: pointer; color: var(--muted);
    }}
    .help-sheet section {{ margin-top: 12px; }}
    .help-sheet h4 {{
      margin: 0 0 4px; font-size: 0.75rem; font-weight: 800; color: var(--muted);
    }}
    .help-sheet p {{ margin: 0; line-height: 1.65; font-size: 0.92rem; }}
    .help-sheet .formula {{
      font-family: var(--font-num);
      font-weight: 700; background: #f8fafc; border: 1px solid var(--line);
      border-radius: 8px; padding: 10px 12px; font-size: 0.88rem;
    }}

  </style>
</head>
<body>
  <div class="shell">
    <aside class="rail">
      {brand_logo_html()}
      <nav>
        {rail_nav}
      </nav>
    </aside>
    <div class="main">
      <header class="top">
        <div>
          <h1>{escape(industry_label)}</h1>
          <div class="meta">{escape(pack_meta)}</div>
        </div>
        <div class="top-right">
          <label class="period">
            <span class="sr-only">{escape(t("period.label", loc))}</span>
            <select disabled aria-label="{escape(t("period.label", loc))}">
              <option{" selected" if period == "28d" else ""}>{escape(t("period.28d", loc))}</option>
              <option{" selected" if period == "7d" else ""}>{escape(t("period.7d", loc))}</option>
            </select>
          </label>
        </div>
      </header>
      <div class="content">
        <div class="focus-banner" role="status">{escape(focus_line)}</div>
        <section class="summary" aria-label="{escape(t("summary_aria", loc))}">
          {summary_html}
        </section>

        <section class="insights" aria-label="{escape(t("next_watch", loc))}">
          <h2>{escape(t("next_watch", loc))}</h2>
          <ol>{next_html}</ol>
        </section>

        <!-- Reading order: who → where from → depth → convert → evidence → business -->
        <div class="grid-2">
          {audience_panel}
          <section class="panel" id="panel-channels">
            <div class="panel-head">
              <div class="panel-head-left">
                <h2>{escape(t("panel.channels", loc))}</h2>
                <span class="sub">{escape(t("panel.channels_sub", loc))}</span>
              </div>
              {channels_switch}
            </div>
            <div class="panel-body" data-section-body="channels" data-view-mode="list">
              <div class="mode-pane mode-list">{channel_list}</div>
              <div class="mode-pane mode-card">{channel_cards}</div>
              <div class="mode-pane mode-bar">{channel_bars}</div>
              <div class="mode-pane mode-stack">{channel_stack_mode}</div>
            </div>
          </section>
        </div>

        <div class="grid-2">
          {engage_panel}
          {funnel_panel}
        </div>

        <div class="grid-2">
          <section class="panel" id="panel-events">
            <div class="panel-head">
              <div class="panel-head-left">
                <h2>{escape(t("panel.events", loc))}</h2>
                <span class="sub" data-count-sub="events">{escape(event_sub)}</span>
              </div>
              {events_switch}
            </div>
            <div class="panel-body" data-section-body="events" data-view-mode="bar">
              <div class="mode-pane mode-list">
                <table class="dense">
                  <thead>
                    <tr>
                      <th class="help-col">{escape(t("col.help", loc))}</th>
                      <th>{escape(t("col.event", loc))}</th>
                      <th style="text-align:right">{escape(t("col.count", loc))}</th>
                      <th style="text-align:right">{escape(t("col.delta", loc))}</th>
                    </tr>
                  </thead>
                  <tbody>{event_rows}</tbody>
                </table>
              </div>
              <div class="mode-pane mode-card">{event_cards}</div>
              <div class="mode-pane mode-bar">{event_bars}</div>
            </div>
            <div class="panel-foot">{event_toggle}</div>
          </section>
          <section class="panel" id="panel-biz">
            <div class="panel-head">
              <div class="panel-head-left">
                <h2>{escape(t("panel.biz", loc))}</h2>
                <span class="sub">{escape(t("panel.biz_sub", loc))}</span>
              </div>
              {biz_switch}
            </div>
            <div class="panel-body" data-section-body="biz" data-view-mode="list">
              <div class="mode-pane mode-list">
                {_dense_metric_table(body_rows=biz_rows, locale=loc)}
              </div>
              <div class="mode-pane mode-card">{biz_cards}</div>
            </div>
          </section>
        </div>
      </div>
    </div>
  </div>
  {dialogs}
  <script>
    const I18N_CLOSE = {escape(close_label)!r};
    const I18N_MORE = (n) => {escape(t("more_n", loc, n="__N__"))!r}.replace("__N__", String(n));
    const I18N_EVENT_SUB_OPEN = {escape(event_sub_open)!r};
    const I18N_EVENT_SUB_CLOSED = {escape(event_sub_closed)!r};
    document.querySelectorAll(".help-btn").forEach((btn) => {{
      btn.addEventListener("click", (e) => {{
        e.stopPropagation();
        const id = btn.getAttribute("data-help");
        const dialog = document.getElementById("help-" + id);
        if (dialog) dialog.showModal();
      }});
    }});
    document.querySelectorAll("[data-help-dialog]").forEach((dialog) => {{
      dialog.addEventListener("click", (e) => {{
        if (e.target === dialog) dialog.close();
      }});
    }});
    document.querySelectorAll(".more-chip").forEach((btn) => {{
      btn.addEventListener("click", () => {{
        const key = btn.getAttribute("data-more");
        const panel = document.getElementById("panel-" + key);
        if (!panel) return;
        const open = panel.classList.toggle("is-expanded");
        const n = panel.querySelectorAll(".mode-list .is-more").length;
        btn.textContent = open ? I18N_CLOSE : I18N_MORE(n);
        const sub = panel.querySelector('[data-count-sub="' + key + '"]');
        if (sub && key === "events") {{
          sub.textContent = open ? I18N_EVENT_SUB_OPEN : I18N_EVENT_SUB_CLOSED;
        }}
      }});
    }});

    const VIEW_PREFIX = "kpistarter.sample.sectionView.";
    const allowed = {{
      funnel: ["list", "card", "compare"],
      events: ["list", "card", "bar"],
      channels: ["list", "card", "bar", "stack"],
      engage: {engage_modes!r},
      audience: {audience_modes!r},
      biz: ["list", "card"],
    }};
    function setSectionView(section, mode) {{
      const modes = allowed[section] || ["list"];
      /* legacy → settled set */
      if (mode === "gap") mode = "compare";
      if (mode === "gauge" || mode === "compact" || mode === "funnel") mode = "list";
      if ((mode === "trend" || mode === "bar") && section !== "events" && section !== "channels" && !modes.includes(mode)) mode = "list";
      if (!modes.includes(mode)) mode = "list";
      const body = document.querySelector('[data-section-body="' + section + '"]');
      if (body) body.setAttribute("data-view-mode", mode);
      document.querySelectorAll('.view-btn[data-section="' + section + '"]').forEach((b) => {{
        b.classList.toggle("is-on", b.dataset.mode === mode);
      }});
      localStorage.setItem(VIEW_PREFIX + section, mode);
    }}
    const defaults = {{ events: "bar", channels: "stack", funnel: "list" }};
    Object.keys(allowed).forEach((section) => {{
      const saved = localStorage.getItem(VIEW_PREFIX + section);
      setSectionView(section, saved || defaults[section] || "list");
    }});
    document.querySelectorAll(".view-btn[data-section]").forEach((btn) => {{
      btn.addEventListener("click", (e) => {{
        e.preventDefault();
        e.stopPropagation();
        setSectionView(btn.dataset.section, btn.dataset.mode);
      }});
    }});
  </script>
</body>
</html>"""
