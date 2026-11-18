"""Story v7 chapters around the issue (docs/plan s03): うまくいっていること (0), なぜ変わった？ (1),
誰が買っている？ (2), どこで起きている？ · いつから？ (4), and 直したら効いた？ (6).

Python only shapes numbers and chart geometry here; markup is templates/board/story_more.html.
Inputs: the board rows, the flow context (stages · channels), and story_x (board/story_x.py).
"""

from __future__ import annotations

import math
from datetime import date, timedelta
from typing import Any

from sitekpi.board.story_x import DEVICES, WINDOW, _sample_release, today_jst
from sitekpi.format import fmt_int
from sitekpi.i18n.story_l10n import STORY

GOOD_MAX = 3
MIN_BASE = 30  # fewer people than this at the start of a step → the rate is only a reference


def _s(loc: str, key: str, **kw: Any) -> str:
    text = STORY.get(loc, STORY["ja"]).get(key) or STORY["ja"][key]
    return text.format(**kw) if kw else text


def _pct(v: float | None) -> str:
    if v is None:
        return "—"
    return f"{v:.2f}%" if 0 < abs(v) < 1 else f"{v:.1f}%"


def _pt(d: float) -> str:
    if abs(d) < 0.05:
        return "±0.0pt"
    return f"{d:+.1f}pt".replace("-", "−")


def _rel(d: float) -> str:
    if abs(d) < 0.05:
        return "±0.0%"
    return f"{d:+.1f}%".replace("-", "−")


def _money(n: float) -> str:
    return f"¥{n:,.0f}"


def _rate(a: float, b: float) -> float | None:
    return min(100.0 * b / a, 100.0) if a > 0 and b >= 0 else None


# ---------------------------------------------------------------- 0 うまくいっていること

def goods(board: dict[str, Any], watch: list[dict[str, Any]], loc: str) -> list[dict[str, str]]:
    """Up to three metrics that got better than last period and are not 要注意."""
    off = {w["bench_key"] for w in watch if w.get("tone") == "down"}
    seen: set[str] = set()
    out: list[tuple[float, dict[str, str]]] = []
    for r in board.get("summary", []) + board.get("funnel", []) + board.get("engage", []) + board.get("audience", []):
        if r.get("tone") != "up" or r.get("bench") in off or r["label"] in seen:
            continue
        txt = str(r.get("delta") or "")
        try:
            mag = abs(float(txt.replace("−", "-").replace("%", "").replace("pt", "")))
        except ValueError:
            continue
        seen.add(r["label"])
        out.append((mag, {"label": r["label"], "delta": txt, "value": str(r.get("value") or "")}))
    out.sort(key=lambda x: -x[0])
    return [x for _, x in out[:GOOD_MAX]]


# ---------------------------------------------------------------- 1 なぜ変わった？

def changed(board: dict[str, Any], data: dict[str, Any], prev: dict[str, Any] | None,
            sx: dict[str, Any] | None, loc: str, nums: dict[str, str]) -> dict[str, Any] | None:
    """成果 = 来た人 × 成果率 (× 1 件あたりの売上): which factor moved the outcome."""
    by_id = {r["id"]: r for r in board.get("summary", [])}
    conv_row, rate_row = by_id.get("primary"), by_id.get("signup_cvr")
    if not prev or not conv_row or not rate_row:
        return None
    uu, p_uu = float(data.get("uu") or 0), float(prev.get("uu") or 0)
    conv, p_conv = float(conv_row.get("value_num") or 0), float(conv_row.get("prev_num") or 0)
    if min(uu, p_uu, conv, p_conv) <= 0:
        return None
    rate, p_rate = conv / uu, p_conv / p_uu
    money = (sx or {}).get("money") or None
    rev = float(((money or {}).get("cur") or {}).get("revenue") or 0)
    p_rev = float(((money or {}).get("prev") or {}).get("revenue") or 0)
    has_money = rev > 0 and p_rev > 0
    per, p_per = (rev / conv, p_rev / p_conv) if has_money else (0.0, 0.0)
    out, p_out = (rev, p_rev) if has_money else (conv, p_conv)

    v_lab, r_lab = _s(loc, "x_visitors"), rate_row["label"]
    p_lab = _s(loc, "x_per")
    o_lab = _s(loc, "x_revenue") if has_money else conv_row["label"]
    d_uu, d_rate_pt, d_out = 100 * (uu / p_uu - 1), 100 * (rate - p_rate), 100 * (out / p_out - 1)
    d_per = 100 * (per / p_per - 1) if has_money else 0.0

    def tone(d: float, flat: float = 0.5) -> str:
        return "mid" if abs(d) < flat else ("up" if d > 0 else "down")

    terms = [{"label": v_lab, "value": fmt_int(uu), "unit": _s(loc, "x_people"), "delta": _rel(d_uu), "tone": tone(d_uu)},
             {"label": r_lab, "value": _pct(rate * 100), "unit": "", "delta": _pt(d_rate_pt), "tone": tone(d_rate_pt, 0.05)}]
    if has_money:
        terms.append({"label": p_lab, "value": _money(per), "unit": "", "delta": _rel(d_per), "tone": tone(d_per)})
    result = {"label": o_lab, "value": _money(out) if has_money else fmt_int(out), "delta": _rel(d_out), "tone": tone(d_out)}

    logs = [("uu", v_lab, math.log(uu / p_uu)), ("rate", r_lab, math.log(rate / p_rate))]
    if has_money:
        logs.append(("per", p_lab, math.log(per / p_per)))
    total = sum(x[2] for x in logs)
    diff = out - p_out
    parts = []
    if abs(total) > 1e-9:
        for key, lab, lg in logs:
            amt = diff * lg / total
            parts.append({"key": key, "label": lab, "amount": amt})
    fmt_amt = (lambda a: ("+" if a >= 0 else "−") + _money(abs(a))) if has_money else \
        (lambda a: ("+" if a >= 0 else "−") + fmt_int(abs(a)))
    flat_keys = {k for k, t_ in (("uu", tone(d_uu)), ("rate", tone(d_rate_pt, 0.05)), ("per", tone(d_per))) if t_ == "mid"}
    kept = [p for p in parts if p["key"] not in flat_keys]
    k_logs = {k: lg for k, _, lg in logs if k not in flat_keys}
    k_sum = sum(k_logs.values())
    if kept and abs(k_sum) > 1e-9:  # the shown parts add up to the whole change
        for p in kept:
            p["amount"] = diff * k_logs[p["key"]] / k_sum
    seg_total = sum(abs(p["amount"]) for p in kept) or 1.0
    segs = [{"label": p["label"], "amount": fmt_amt(p["amount"]), "flex": round(100 * abs(p["amount"]) / seg_total, 1),
             "tone": "up" if p["amount"] >= 0 else "down", "key": p["key"]} for p in kept]
    flat_parts = [p["label"] for p in parts if p["key"] in flat_keys]

    rate_rel = rate / p_rate - 1
    out_up = d_out > 0
    if abs(d_out) < 0.5:
        head = _s(loc, "x_ch_h_flat", out=o_lab)
    else:
        main = max(logs, key=lambda x: abs(x[2]))
        up = main[2] > 0
        verb = _s(loc, ("x_up_rate" if up else "x_down_rate") if main[0] == "rate" else ("x_up" if up else "x_down"))
        d_main = {"uu": _rel(d_uu), "rate": _pt(d_rate_pt), "per": _rel(d_per)}[main[0]]
        head = _s(loc, "x_ch_h", out=o_lab, dir=_s(loc, "x_up" if out_up else "x_down"), factor=main[1], fdir=verb, d=d_main)
    if abs(rate_rel) < 0.02 and abs(d_out) >= 0.5:
        head += _s(loc, "x_ch_h_rate_flat", rate=r_lab)
    take = (_s(loc, "x_ch_take", rate=r_lab, span=nums["span"]) if rate_rel < 0.02
            else _s(loc, "x_ch_take_up", rate=r_lab, d=_pt(d_rate_pt), where=nums["where"]))
    return {
        "head": head,
        "formula": _s(loc, "x_ch_formula_money" if has_money else "x_ch_formula", out=o_lab, rate=r_lab, per=p_lab),
        "terms": terms, "result": result,
        "bar_k": _s(loc, "x_ch_bar", out=o_lab, d=fmt_amt(diff)),
        "segs": segs, "flat": _s(loc, "x_ch_flat", names="・".join(flat_parts)) if flat_parts else "",
        "take": take, "take_tone": "mid" if rate_rel < 0.02 else "up",
    }


# ---------------------------------------------------------------- 2 誰が買っている？

def _target(stages: list[dict[str, Any]]) -> int | None:
    """The deepest step that enough people reached — a rate over 10 people says nothing."""
    for k in range(len(stages) - 1, 0, -1):
        if float(stages[k].get("users") or 0) >= MIN_BASE:
            return k
    return None


def _place_labels(pts: list[dict[str, Any]], W: float, top: float, bottom: float) -> None:
    """Put each name next to its bubble without two names on top of each other (greedy, by size)."""
    boxes: list[tuple[float, float, float, float]] = []
    for p in sorted(pts, key=lambda q: -q["r"]):
        w = 7.5 * len(p["label"]) + 4
        p["anchor"] = "end" if p["cx"] + p["r"] + 5 + w > W else "start"
        x0 = p["cx"] - p["r"] - 5 - w if p["anchor"] == "end" else p["cx"] + p["r"] + 5
        y = p["cy"]
        for step in (0, 16, -16, 32, -32, 48, -48, 64, -64):
            yy = min(max(p["cy"] + step, top + 10), bottom - 4)
            if all(x0 + w < bx0 or x0 > bx1 or yy - 12 > by1 or yy + 2 < by0 for bx0, by0, bx1, by1 in boxes):
                y = yy
                break
        boxes.append((x0, y - 12, x0 + w, y + 2))
        p["tx"] = round(p["cx"] - p["r"] - 5 if p["anchor"] == "end" else p["cx"] + p["r"] + 5, 1)
        p["ty"] = round(y + 4, 1)


def buyers(flow: dict[str, Any] | None, sx: dict[str, Any] | None, loc: str) -> dict[str, Any] | None:
    stages = (flow or {}).get("stages") or []
    k = _target(stages) if len(stages) >= 2 else None
    if k is None:
        return None
    step_label = stages[k]["label"]
    chans = [c for c in (flow or {}).get("channels") or [] if c.get("entry")]
    total = sum(c["entry"] for c in chans)
    overall = _rate(float(stages[0].get("users") or 0), float(stages[k].get("users") or 0))

    chmap = None
    named = [c for c in chans if c["id"] != "fco"]  # 「その他」 is a bucket, not a channel to act on
    shown = [c for c in named if total and 100.0 * c["entry"] / total >= 3 and c["entry"] >= MIN_BASE]
    small = [c["name"] for c in named if c not in shown]
    if len(shown) >= 2 and overall:
        shares = sorted(100.0 * c["entry"] / total for c in shown)
        mid = shares[len(shares) // 2] if len(shares) % 2 else (shares[len(shares) // 2 - 1] + shares[len(shares) // 2]) / 2
        pts = []
        for c in shown:
            share = 100.0 * c["entry"] / total
            r = _rate(float(c["entry"]), float((stages[k].get("ch_users") or {}).get(c["id"], 0)))
            if r is None:
                continue
            if share >= mid and r < overall * 0.85:
                q = "fix"
            elif share < mid and r >= overall * 1.15:
                q = "grow"
            elif r >= overall:
                q = "core"
            else:
                q = "watch"
            pts.append({"name": c["name"], "share": share, "rate": r, "q": q})
        if len(pts) >= 2:
            xmax = max(10.0, math.ceil(max(p["share"] for p in pts) / 10) * 10)
            ymax = max(max(p["rate"] for p in pts), overall) * 1.15
            ystep = _nice_step(ymax)
            ymax = math.ceil(ymax / ystep) * ystep
            W, H, L, R, T, B = 620, 320, 48, 16, 16, 36
            X = lambda v: L + v / xmax * (W - L - R)
            Y = lambda v: T + (ymax - v) / ymax * (H - T - B)
            for p in pts:
                p["cx"], p["cy"] = round(X(p["share"]), 1), round(Y(p["rate"]), 1)
                p["r"] = round(6 + min(p["share"], 60) / 5, 1)
                p["label"] = f"{p['name']} {_pct(p['rate'])}"
                p["share_fmt"] = f"{p['share']:.0f}%"
                p["rate_fmt"] = _pct(p["rate"])
                p["q_label"] = _s(loc, "x_q_" + p["q"])
            _place_labels(pts, W - R, T, H - B)
            xs = [0, xmax / 3, 2 * xmax / 3, xmax]
            chmap = {
                "w": W, "h": H, "l": L, "r": W - R, "t": T, "b": H - B,
                "mx": round(X(mid), 1), "my": round(Y(overall), 1),
                "xt": [{"x": round(X(v), 1), "t": f"{v:.0f}%"} for v in xs],
                "yt": [{"y": round(Y(v), 1), "t": f"{v:g}%"} for v in _ticks(ymax, ystep)],
                "pts": sorted(pts, key=lambda p: -p["share"]),
                "avg": _s(loc, "x_who_avg", rate=_pct(overall)),
                "q": {q: _s(loc, "x_q_" + q) for q in ("grow", "core", "fix", "watch")},
                "x_k": _s(loc, "x_who_x"), "size_k": _s(loc, "x_who_size"), "list_k": _s(loc, "x_who_list_k", rate=_pct(overall)),
                "col_share": _s(loc, "x_who_col_share"), "col_rate": _s(loc, "x_who_col_rate", step=step_label),
                "small": _s(loc, "x_who_small", names="・".join(small)) if small else "",
            }
            notes = []
            grow = sorted([p for p in pts if p["q"] == "grow"], key=lambda p: -p["rate"])[:2]
            fix = sorted([p for p in pts if p["q"] == "fix"], key=lambda p: -p["share"])[:1]
            core = [p for p in pts if p["q"] == "core"][:2]
            if grow:
                notes.append({"q": "grow", "k": _s(loc, "x_q_grow"), "t": _s(loc, "x_who_grow", names="・".join(
                    f"{p['name']}（{p['rate_fmt']}）" for p in grow))})
            if fix:
                f = fix[0]
                notes.append({"q": "fix", "k": _s(loc, "x_q_fix"), "t": _s(loc, "x_who_fix", name=f["name"], share=f["share_fmt"],
                                                                         rate=f["rate_fmt"], avg=_pct(overall))})
            if core:
                notes.append({"q": "core", "k": _s(loc, "x_q_core"), "t": _s(loc, "x_who_core", names="・".join(p["name"] for p in core))})
            chmap["notes"] = notes
            chmap["fix"] = fix[0]["name"] if fix else ""

    nvr = None
    raw = (sx or {}).get("nvr") or None
    ev_k = stages[k].get("event") or ""
    if raw and raw["new"]["users"] and raw["returning"]["users"]:
        nu, ru = raw["new"]["users"], raw["returning"]["users"]
        nc, rc = int((raw["new"].get("ev") or {}).get(ev_k, 0)), int((raw["returning"].get("ev") or {}).get(ev_k, 0))
        u_ret = 100 * ru / (nu + ru)
        c_ret = 100 * rc / (nc + rc) if (nc + rc) >= MIN_BASE else None
        pr = raw.get("prev_returning") or 0
        d_ret = 100 * (ru / pr - 1) if pr else None

        def bar(new: float, n: str) -> dict[str, Any]:
            ret = round(100 - new, 1)
            return {"new": round(new, 1), "ret": ret, "n": n, "narrow_new": new < 18, "narrow_ret": ret < 18}

        nvr = {
            "users": bar(100 - u_ret, fmt_int(nu + ru)),
            "conv": bar(100 - c_ret, fmt_int(nc + rc)) if c_ret is not None else None,
            "cards": [
                {"k": _s(loc, "x_nvr_rate_new"), "v": _pct(_rate(nu, nc)) if c_ret is not None else "—", "d": "", "tone": "mid"},
                {"k": _s(loc, "x_nvr_rate_ret"), "v": _pct(_rate(ru, rc)) if c_ret is not None else "—", "d": "", "tone": "mid"},
                {"k": _s(loc, "x_nvr_ret_users"), "v": fmt_int(ru) + _s(loc, "x_people_sfx"),
                 "d": _s(loc, "x_prev", d=_rel(d_ret)) if d_ret is not None else "",
                 "tone": "mid" if d_ret is None or abs(d_ret) < 1 else ("up" if d_ret > 0 else "down")},
            ],
            "k_users": _s(loc, "x_nvr_users"), "k_conv": _s(loc, "x_nvr_conv", step=step_label),
            "new_k": _s(loc, "x_nvr_new"), "ret_k": _s(loc, "x_nvr_ret"),
        }
        lead = _s(loc, "x_nvr_lead", step=step_label, ret=_pct(c_ret)) if c_ret is not None else ""
        if d_ret is not None and d_ret <= -1:
            lead += _s(loc, "x_nvr_lead_down", d=_rel(d_ret))
        nvr["lead"] = lead
        nvr["note"] = _s(loc, "x_nvr_note") if d_ret is not None and d_ret <= -1 else ""
        nvr["c_ret"] = c_ret
    if not chmap and not nvr:
        return None
    parts = []
    if nvr and nvr.get("c_ret") is not None:
        c = nvr["c_ret"]
        parts.append(_s(loc, "x_who_h_ret" if c >= 50 else "x_who_h_new", step=step_label, pct=_pct(c if c >= 50 else 100 - c)))
    if chmap and chmap.get("fix"):
        parts.append(_s(loc, "x_who_h_fix", name=chmap["fix"], step=step_label))
    head = "".join(parts) or _s(loc, "x_who_h_none", step=step_label)
    return {"head": head, "map": chmap, "nvr": nvr, "map_k": _s(loc, "x_who_map_k"), "nvr_k": _s(loc, "x_who_nvr_k")}


def _nice_step(top: float) -> float:
    raw = top / 4 if top > 0 else 1
    mag = 10 ** math.floor(math.log10(raw))
    for m in (1, 2, 2.5, 5, 10):
        if raw <= m * mag:
            return m * mag
    return 10 * mag


def _ticks(top: float, step: float) -> list[float]:
    out, v = [], step
    while v <= top + 1e-9:
        out.append(round(v, 4))
        v += step
    return out


# ---------------------------------------------------------------- 4 どこで起きている？ · いつから？

def _stretch(issue: dict[str, Any], stages: list[dict[str, Any]], entry: float, ev: dict[str, float]) -> tuple[float, float]:
    a = entry if issue["i"] == 0 else float(ev.get(stages[issue["i"]]["event"], 0))
    b = float(ev.get(stages[issue["j"]]["event"], 0))
    return a, b


def where_when(issue: dict[str, Any], stages: list[dict[str, Any]], flow: dict[str, Any], sx: dict[str, Any] | None,
               info: dict[str, Any] | None, loc: str, metric_label: str = "") -> dict[str, Any]:
    """The issue's rate per device / channel (same ruler as the 業界目安), and its last 8 weeks."""
    A, B = stages[issue["i"]]["label"], stages[issue["j"]]["label"]
    a_all, b_all = float(stages[issue["i"]].get("users") or 0), float(stages[issue["j"]].get("users") or 0)
    overall = _rate(a_all, b_all)
    band = None
    if info and not info.get("none") and str(info.get("unit")) == "%":
        lo, hi = float(info["low"]), float(info["high"])
        # a lower-is-better rate (すぐ離脱に近い率) is the other side of the share that went on
        band = (lo, hi) if info.get("hib") else (round(100 - hi, 1), round(100 - lo, 1))
    out: dict[str, Any] = {"a": A, "b": B, "overall": _pct(overall), "band": None}

    def row(name: str, a: float, b: float) -> dict[str, Any] | None:
        r = _rate(a, b)
        if r is None:
            return None
        low = r < band[0] if band else (overall is not None and r < overall * 0.85)
        return {"name": name, "rate": r, "rate_fmt": _pct(r), "base": fmt_int(a), "low": low, "few": a < MIN_BASE}

    dev_rows = []
    for d in DEVICES:
        g = ((sx or {}).get("devices") or {}).get(d) or {}
        a, b = _stretch(issue, stages, float(g.get("entry") or 0), g.get("ev") or {})
        r = row(_s(loc, "x_dev_" + d), a, b) if a else None
        if r:
            dev_rows.append(r)
    ch_rows = []
    for c in flow.get("channels") or []:
        a = float(c.get("entry") or 0) if issue["i"] == 0 else float((stages[issue["i"]].get("ch_users") or {}).get(c["id"], 0))
        b = float((stages[issue["j"]].get("ch_users") or {}).get(c["id"], 0))
        r = row(c["name"], a, b) if a else None
        if r:
            ch_rows.append(r)
    rows = dev_rows + ch_rows
    if rows:
        top = max([r["rate"] for r in rows] + ([band[1]] if band else []) + ([overall] if overall else []))
        top = top * 1.08 or 1.0
        for r in rows:
            r["w"] = round(100 * r["rate"] / top, 1)
        if band:
            bk = (_s(loc, "x_band_k", band=f"{band[0]:g}–{band[1]:g}%") if info.get("hib") else
                  _s(loc, "x_band_inv_k", band=f"{band[0]:g}–{band[1]:g}%", label=metric_label,
                     orig=f"{round(float(info['low']), 1):g}–{round(float(info['high']), 1):g}%"))
            out["band"] = {"l": round(100 * band[0] / top, 1), "w": round(100 * (band[1] - band[0]) / top, 1), "k": bk}
        else:
            out["ref"] = {"l": round(100 * (overall or 0) / top, 1), "k": _s(loc, "x_ref_k", rate=_pct(overall))}
        lows = [r for r in rows if r["low"] and not r["few"]]
        worst_dev = min((r for r in dev_rows if r["low"] and not r["few"]), key=lambda r: r["rate"], default=None)
        worst_ch = min((r for r in ch_rows if r["low"] and not r["few"]), key=lambda r: r["rate"], default=None)
        named = [r for r in (worst_dev, worst_ch) if r]
        if named:
            head = _s(loc, "x_where_h", names=_s(loc, "x_and").join(f"{r['name']}（{r['rate_fmt']}）" for r in named))
            oks = [r for r in rows if not r["low"] and not r["few"]][:2]
            if oks and band:
                head += _s(loc, "x_where_ok", names=_s(loc, "x_and").join(f"{r['name']}（{r['rate_fmt']}）" for r in oks))
        elif lows:
            head = _s(loc, "x_where_h", names=_s(loc, "x_and").join(f"{r['name']}（{r['rate_fmt']}）" for r in lows[:2]))
        else:
            head = _s(loc, "x_where_even")
        out.update({"head": head, "devs": dev_rows, "chs": ch_rows, "focus": [r["name"] for r in named],
                    "dev_k": _s(loc, "x_dev_k"), "ch_k": _s(loc, "x_ch_k"), "low_k": _s(loc, "x_low_k"),
                    "base_k": _s(loc, "x_base_k", a=A), "few_k": _s(loc, "x_few_k")})
    out["when"] = _when(issue, stages, sx, band, loc)
    return out


def _when(issue: dict[str, Any], stages: list[dict[str, Any]], sx: dict[str, Any] | None,
          band: tuple[float, float] | None, loc: str) -> dict[str, Any] | None:
    wk = (sx or {}).get("weeks") or {}
    ev = wk.get("ev") or {}
    entry = wk.get("entry") or []
    if len(entry) < 8:
        return None
    series: list[float | None] = []
    for i in range(8):
        a, b = _stretch(issue, stages, float(entry[i] or 0), {k: float(v[i] or 0) for k, v in ev.items() if len(v) > i})
        series.append(_rate(a, b) if a >= MIN_BASE else None)
    vals = [v for v in series if v is not None]
    if len(vals) < 6:
        return None
    try:
        w0 = date.fromisoformat(str((sx or {}).get("week0")))
    except ValueError:
        return None
    days = [(w0 + timedelta(days=7 * i)) for i in range(8)]
    dl = [f"{d.month}/{d.day}" for d in days]
    first = [v for v in series[:4] if v is not None]
    second = [v for v in series[4:] if v is not None]
    p_avg, c_avg = sum(first) / len(first), sum(second) / len(second)
    moves = [(series[i] - series[i - 1], i) for i in range(4, 8) if series[i] is not None and series[i - 1] is not None]
    big = min(moves, default=None) if c_avg < p_avg else max(moves, default=None)
    below = band is not None and all(v < band[0] for v in vals)
    trend = "down" if c_avg < p_avg - 0.3 else ("up" if c_avg > p_avg + 0.3 else "flat")
    n_ago = 8 - big[1] if big else 0
    if trend == "down":
        head = _s(loc, "x_when_below_down" if below else "x_when_down", n=n_ago)
    elif trend == "up":
        head = _s(loc, "x_when_up", n=n_ago)
    else:
        head = _s(loc, "x_when_below_flat" if below else "x_when_flat")
    side = []
    if below:
        side.append({"k": _s(loc, "x_when_always_k"), "t": _s(loc, "x_when_always", low=f"{band[0]:g}%"), "tone": "mid"})
    if big and trend != "flat":
        i = big[1]
        side.append({"k": _s(loc, "x_when_more_k" if below else "x_when_move_k"),
                     "t": _s(loc, "x_when_move", d=dl[i], a=_pct(series[i - 1]), b=_pct(series[i])),
                     "tone": "down" if trend == "down" else "up"})
        if trend == "down":
            side.append({"k": _s(loc, "x_when_check_k"), "t": _s(loc, "x_when_check", d=dl[i]), "tone": "box"})

    def geo(W: int, H: int, L: int) -> dict[str, Any]:
        R, T, Bm = 12, 16, 28
        lo = min(vals + ([band[0]] if band else []))
        hi = max(vals + ([band[0]] if band else []))
        span = max(hi - lo, 1.0)
        y0, y1 = max(0.0, lo - span * 0.6), hi + span * 0.35
        X = lambda k: L + k * (W - L - R) / 7
        Y = lambda v: T + (y1 - v) / (y1 - y0) * (H - T - Bm)
        pts = [{"x": round(X(k), 1), "y": round(Y(v), 1), "cur": k >= 4, "d": dl[k]} for k, v in enumerate(series) if v is not None]
        step = _nice_step(y1 - y0)
        ticks = [v for v in _ticks(y1, step) if v >= y0]
        g = {"w": W, "h": H, "l": L, "r": W - R, "t": T, "b": H - Bm,
             "line": " ".join(f"{p['x']},{p['y']}" for p in pts), "pts": pts,
             "xl": [{"x": round(X(k), 1), "t": dl[k]} for k in range(8)],
             "yt": [{"y": round(Y(v), 1), "t": f"{v:g}%"} for v in ticks],
             "mid": round((X(3) + X(4)) / 2, 1),
             "last": {"x": pts[-1]["x"], "y": pts[-1]["y"], "t": _pct(vals[-1])}, "band": None, "marks": []}
        if band:
            g["band"] = {"y": T, "h": round(max(Y(band[0]) - T, 0), 1), "ly": round(Y(band[0]), 1),
                         "t": _s(loc, "x_when_band", low=f"{band[0]:g}%")}
        return g

    return {"head": head, "side": side, "pc": geo(640, 200, 44), "sp": geo(326, 190, 36),
            "w0": w0.isoformat(), "prev_avg": _s(loc, "x_when_prev", r=_pct(p_avg)), "cur_avg": _s(loc, "x_when_cur", r=_pct(c_avg)),
            "aria": _s(loc, "x_when_aria", a=stages[issue["i"]]["label"], b=stages[issue["j"]]["label"])}


# ---------------------------------------------------------------- 6 直したら効いた？

def effect(issue: dict[str, Any], stages: list[dict[str, Any]], sx: dict[str, Any] | None,
           releases: list[dict[str, Any]], acts: list[dict[str, Any]], loc: str, *, sample: bool,
           nums: dict[str, str], today: date | None = None) -> dict[str, Any]:
    today = today or today_jst()
    opts = [{"v": str(x["n"]), "t": f"{x['n']}. {x['title']}"} for x in acts]
    out: dict[str, Any] = {"opts": opts, "today": today.isoformat(), "sample": sample, "releases": [], "result": None,
                           "recorded": [],
                           "lead": _s(loc, "x_eff_lead", n=WINDOW, do=nums["do"])}
    rel = (sx or {}).get("release")
    shown = None
    if sample:
        day = today - timedelta(days=WINDOW + 1)
        title = acts[0]["title"] if acts else ""
        shown = {"date": day.isoformat(), "act": "1", "title": title}
        events = {st["event"]: float(st.get("users") or 0) for st in stages[1:] if st.get("event")}
        rel = _sample_release("story|", {"date": day.isoformat(), "focus": issue["j"]}, int(stages[0].get("users") or 0),
                              {k: int(v) for k, v in events.items()}, list(events), today=today)
        out["releases"] = [{"label": _rel_label(shown, loc), "idx": 0}]
        out["recorded"] = [{"act": "1", "md": _md(day), "date": day.isoformat(), "title": title}]
    elif releases:
        shown = releases[-1]
        out["releases"] = [{"label": _rel_label(r, loc), "idx": n} for n, r in enumerate(releases)]
        out["recorded"] = [{"act": str(r.get("act") or ""), "md": _md(date.fromisoformat(str(r["date"]))),
                            "date": str(r["date"]), "title": str(r.get("title") or "")} for r in releases]
    if not shown:
        return out
    name = f"「{shown['title']}」" if shown.get("title") else _rel_label(shown, loc)
    if not rel or not rel.get("before") or not rel.get("after"):
        left = max(WINDOW + 1 - (today - date.fromisoformat(shown["date"])).days, 1)
        out["result"] = {"wait": _s(loc, "x_eff_wait", n=left, name=name)}
        return out
    bf, af = rel["before"], rel["after"]

    def r_of(side: dict[str, Any], i: int, j: int) -> float | None:
        ev = side.get("ev") or {}
        a = float(side.get("entry") or 0) if i == 0 else float(ev.get(stages[i]["event"], 0))
        b = float(ev.get(stages[j]["event"], 0))
        return _rate(a, b)

    pairs = []
    if issue["j"] - issue["i"] > 1:
        pairs += [(n, n + 1) for n in range(issue["i"], issue["j"])]
    else:
        nxt = issue["j"] + 1 if issue["j"] + 1 < len(stages) else None
        pairs.append((issue["i"], issue["j"]))
        if nxt is not None:
            pairs.append((issue["j"], nxt))
    stretch = (issue["i"], issue["j"] if issue["j"] - issue["i"] > 1 else (issue["j"] + 1 if issue["j"] + 1 < len(stages) else issue["j"]))
    if stretch not in pairs:
        pairs.append(stretch)
    last_i = len(stages) - 1
    if (0, last_i) not in pairs:
        pairs.append((0, last_i))
    rows = []
    for i, j in pairs:
        x, y = r_of(bf, i, j), r_of(af, i, j)
        if x is None or y is None:
            continue
        d = y - x
        tone = "mid" if abs(d) < 0.5 else ("up" if d > 0 else "down")
        ref = (i, j) == (0, last_i)
        rows.append({"name": _s(loc, "x_eff_ref", a=stages[i]["label"], b=stages[j]["label"]) if ref
                     else f"{stages[i]['label']} → {stages[j]['label']}",
                     "before": _pct(x), "after": _pct(y), "d": _pt(d), "tone": tone, "x": x, "y": y, "ref": ref,
                     "stretch": (i, j) == stretch, "i": i, "j": j})
    if not rows:
        out["result"] = {"wait": _s(loc, "x_eff_none", name=name)}
        return out
    top = max(max(r["x"], r["y"]) for r in rows) * 1.1 or 1
    for r in rows:
        r["wx"], r["wy"] = round(100 * r["x"] / top, 1), round(100 * r["y"] / top, 1)
    steps = [r for r in rows if not r["ref"] and not r["stretch"]] or [r for r in rows if not r["ref"]]
    best = max(steps, key=lambda r: r["y"] - r["x"])
    worst = min(steps, key=lambda r: r["y"] - r["x"])
    st = next((r for r in rows if r["stretch"]), rows[0])
    if best["tone"] == "up" and st["tone"] == "mid" and worst["tone"] == "down":
        head = _s(loc, "x_eff_mixed", name=name, best=best["name"], bd=best["d"], worst=worst["name"], st=st["name"])
        nxt = _s(loc, "x_eff_next", step=worst["name"])
    elif st["tone"] == "up" or (best["tone"] == "up" and worst["tone"] != "down"):
        r = st if st["tone"] == "up" else best
        head, nxt = _s(loc, "x_eff_up", name=name, step=r["name"], d=r["d"]), _s(loc, "x_eff_keep")
    elif st["tone"] == "down":
        head, nxt = _s(loc, "x_eff_down", name=name, step=st["name"], d=st["d"]), _s(loc, "x_eff_back")
    else:
        head, nxt = _s(loc, "x_eff_flat", name=name, step=st["name"], d=st["d"]), _s(loc, "x_eff_more")
    d0 = date.fromisoformat(shown["date"])
    out["result"] = {
        "head": head, "next": nxt, "rows": rows,
        "k": _s(loc, "x_eff_res_k", d=_md(d0), title=shown.get("title") or "", n=WINDOW),
        "before_k": _s(loc, "x_eff_before", n=WINDOW), "after_k": _s(loc, "x_eff_after", n=WINDOW),
        "before_d": f"{_md(d0 - timedelta(days=WINDOW))}–{_md(d0 - timedelta(days=1))}",
        "after_d": f"{_md(d0)}–{_md(d0 + timedelta(days=WINDOW - 1))}",
        "note": _s(loc, "x_eff_note"),
    }
    return out


def _md(d: date) -> str:
    return f"{d.month}/{d.day}"


def _rel_label(r: dict[str, Any], loc: str) -> str:
    try:
        d = _md(date.fromisoformat(str(r["date"])))
    except ValueError:
        d = str(r.get("date") or "")
    title = str(r.get("title") or "").strip()
    return f"{d} {title}" if title else d


def mark_releases(ww: dict[str, Any], eff: dict[str, Any], loc: str) -> None:
    """A dashed line on いつから？ for each recorded fix inside the 8 weeks."""
    when = ww.get("when")
    if not when:
        return
    w0 = date.fromisoformat(when["w0"])
    for g in (when["pc"], when["sp"]):
        g["marks"] = []
        for n, r in enumerate(eff.get("recorded") or []):
            k = (date.fromisoformat(r["date"]) - w0).days / 7
            if 0 <= k <= 7.99:
                x = round(g["l"] + min(k, 7) * (g["r"] - g["l"]) / 7, 1)
                label = _s(loc, "x_mark", n=_circ(r.get("act")), d=r["md"])
                g["marks"].append({"x": x, "t": label, "y": g["t"] + 12 + 14 * (n % 2)})


def _circ(act: Any) -> str:
    s = str(act or "")
    return "⓪①②③④⑤⑥⑦⑧⑨"[int(s)] if s.isdigit() and int(s) < 10 else "✓"


def summary(loc: str, *, a: str, b: str, head_now: str, metric: dict[str, Any] | None, ww: dict[str, Any],
            first: dict[str, Any] | None, gain: str, eff: dict[str, Any], do: str) -> dict[str, Any]:
    """まとめ: the board in four lines, before 詳しい数字 (and as text for a report)."""
    band = _s(loc, "x_sum_band", band=metric["band"]) if metric and metric.get("band") and metric["band"] != "—" else ""
    issue = _s(loc, "x_sum_issue", a=a, b=b, rate=metric["value"] if metric else "", band=band)
    if ww.get("focus"):
        issue += _s(loc, "x_sum_focus", names=_s(loc, "x_and").join(ww["focus"]))
    if (ww.get("when") or {}).get("head"):
        issue += ww["when"]["head"]
    first_t = ""
    if first:
        first_t = f"① {first['title']}" + (f" — {gain}" if gain else "")
    res = eff.get("result") or {}
    nxt = res.get("head") if res.get("head") else _s(loc, "x_sum_next", do=do)
    rows = [{"k": _s(loc, "x_sum_now_k"), "v": head_now}, {"k": _s(loc, "x_sum_issue_k"), "v": issue}]
    if first_t:
        rows.append({"k": _s(loc, "x_sum_first_k"), "v": first_t})
    rows.append({"k": _s(loc, "x_sum_next_k"), "v": nxt})
    head = _s(loc, "x_sum_h", a=a, b=b)
    text = head + "\n" + "\n".join(f"・{r['k']}: {r['v']}" for r in rows)
    return {"head": head, "rows": rows, "text": text}
