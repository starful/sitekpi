"""The board's story: 0 総評 → 1 どこで？ → 2 どこがおかしい？ → 3 どうする？ (docs/plan s03; 「大丈夫？」は総評に吸収).

One issue runs through all four cards. The rule (pick_issue):
  1. いまの状態's issue tile — the metric furthest outside its 業界目安 (not the CVR tile) — if its rate maps
     to a stretch of the flow (board rows carry "seg": (from event, to event); engagement → 開いた → しっかり見た);
  2. otherwise the flow step with the lowest share moving on (the board's worst link).
④ comes from the 対策カタログ (i18n/story_l10n.ACTIONS) for the kind of the issue's last step, with the
expected gain when the rate has a 業界目安: base × target low − now. The AI prompt (copy only, never sent)
is built here from the same numbers.
"""

from __future__ import annotations

from typing import Any

from markupsafe import Markup, escape

from sitekpi.format import fmt_int as _fmt_int
from sitekpi.i18n.story_l10n import ACTIONS, STORY, kind_of_event

ENGAGE_KEYS = ("engaged_rate", "bounce_rate")


def _s(loc: str, key: str, **kw: Any) -> str:
    text = STORY.get(loc, STORY["ja"]).get(key) or STORY["ja"][key]
    return text.format(**kw) if kw else text


def _stage_index(stages: list[dict[str, Any]], event: str) -> int:
    for i, st in enumerate(stages):
        if event and event in (st.get("key"), st.get("step")):
            return i
    return -1


def _rows_by_bench(board: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for r in board.get("summary", []) + board.get("funnel", []) + board.get("engage", []):
        if r.get("bench") and r["bench"] not in out:
            out[r["bench"]] = r
    return out


def pick_issue(board: dict[str, Any], watch: list[dict[str, Any]], verdict: dict[str, Any],
               flow: dict[str, Any] | None) -> dict[str, Any] | None:
    """The one issue: stage indices (i → j) in the flow, and the metric behind it when there is one."""
    stages = (flow or {}).get("stages") or []
    if len(stages) < 3:
        return None
    rows = _rows_by_bench(board)
    tile = next((k for k in verdict.get("tiles", []) if k.get("issue")), None)
    key = (tile or {}).get("bench", {}).get("key") or ""
    metric = next((w for w in watch if w.get("bench_key") == key), None) if key else None
    i = j = -1
    if metric:
        if key in ENGAGE_KEYS:
            i, j = _stage_index(stages, "session_start"), _stage_index(stages, "user_engagement")
        elif key == "signup_rate":
            i, j = 0, len(stages) - 1
        else:
            seg = rows.get(key, {}).get("seg")
            if seg:
                i, j = _stage_index(stages, seg[0]), _stage_index(stages, seg[1])
    if not (0 <= i < j):
        metric = None
        worst = next((n for n, st in enumerate(stages[:-1]) if (st.get("link") or {}).get("worst")), -1)
        if worst < 0:
            return None
        i, j = worst, worst + 1
    last = stages[j]
    kind = "overall" if (metric and key == "signup_rate") else \
        "engage" if (metric and key in ENGAGE_KEYS) else kind_of_event(str(last.get("step") or last.get("key") or ""))
    return {"i": i, "j": j, "metric": metric, "kind": kind, "from_tile": bool(tile and metric)}


def _gain(issue: dict[str, Any], stages: list[dict[str, Any]], info: dict[str, Any] | None) -> dict[str, Any] | None:
    """Expected gain when the rate reaches the low end of its 業界目安 (rates measured between two steps)."""
    if not info or info.get("none") or not info.get("hib") or str(info.get("unit")) != "%":
        return None
    a, b = stages[issue["i"]], stages[issue["j"]]
    base, now = float(a.get("users") or 0), float(b.get("users") or 0)
    low = float(info["low"])
    extra = base * low / 100 - now
    if base <= 0 or extra < 1:
        return None
    return {"n": _fmt_int(extra), "base": _fmt_int(base), "now": _fmt_int(now), "low": f"{round(low, 1):g}%",
            "pct": f"+{extra / now * 100:.0f}%" if now else ""}


def build_story(*, board: dict[str, Any], watch: list[dict[str, Any]], verdict: dict[str, Any],
                flow: dict[str, Any] | None, locale: str, bench_info: Any, site: str = "",
                industry_label: str = "", behavior_label: str = "", period_label: str = "") -> dict[str, Any] | None:
    """Everything the four cards and the AI prompt need. bench_info: views/board._bench_info."""
    loc = locale if locale in STORY else "ja"
    issue = pick_issue(board, watch, verdict, flow)
    if not issue:
        return None
    stages = flow["stages"]
    a, b = stages[issue["i"]], stages[issue["j"]]
    na, nb = float(a.get("users") or 0), float(b.get("users") or 0)
    rate = f"{nb / na * 100:.1f}%" if na else "—"
    metric = issue["metric"]
    info = bench_info(metric.get("value_num"), metric["bench_key"]) if metric else None
    gain = _gain(issue, stages, info) if metric else None
    cat = ACTIONS.get(loc, ACTIONS["ja"]).get(issue["kind"]) or ACTIONS["ja"]["overall"]
    A, B = a["label"], b["label"]

    # the issue's stretch of the flow in orange (replaces the biggest-drop highlight)
    biggest = next((n for n, st in enumerate(stages[:-1]) if (st.get("link") or {}).get("worst")), -1)
    for n, st in enumerate(stages[:-1]):
        if st.get("link"):
            st["link"]["worst"] = issue["i"] <= n < issue["j"]
    for st in stages:
        st["in_issue"] = False
    for n in range(issue["i"], issue["j"] + 1):
        stages[n]["in_issue"] = True

    # 0 総評: one boss-repeatable sentence + the three tiles (「大丈夫？」は総評に吸収).
    # verdict.lead already ends with bx.sep — strip it so we don't get "…요. . 다만".
    lead = str(verdict.get("lead") or "").rstrip()
    while lead and lead[-1] in "。.!?！？":
        lead = lead[:-1].rstrip()
    has_issue = any(k.get("issue") for k in verdict.get("tiles", [])) and not verdict.get("no_issue")
    n_off = len([w for w in watch if w["tone"] == "down"])
    stop = "。" if loc == "ja" else ". "
    if has_issue:
        core = _s(loc, "lede_core", a=A, b=B, rate=rate)
        tail = _s(loc, "lede_off", n=n_off) if n_off else _s(loc, "lede_end")
        s1 = Markup(
            f"{escape(lead)}{escape(stop)}{escape(_s(loc, 'but'))}"
            f'<span class="v-issue">{escape(core)}</span>{escape(tail)}'
        )
    else:
        s1 = Markup(f"{escape(lead)}{escape(stop)}{escape(_s(loc, 'lede_ok'))}")

    # ②
    s2 = Markup(escape(_s(loc, "where_h", a=A, b=B, na=_fmt_int(na), nb=_fmt_int(nb), rate=rate))
                .replace(escape(f"「{A} → {B}」" if loc != "en" else f"“{A} → {B}”"),
                         Markup('<span class="v-issue">') + escape(f"「{A} → {B}」" if loc != "en" else f"“{A} → {B}”")
                         + Markup("</span>"), 1))
    note = ""
    if biggest >= 0 and not (issue["i"] <= biggest < issue["j"]) and metric:
        lk = stages[biggest]["link"]
        note = _s(loc, "where_note", a=lk["from"], b=lk["to"], n=(lk.get("lost") or {}).get("all", "—"))

    # ③: the metric (業界目安) and every step inside the stretch
    rows: list[dict[str, Any]] = []
    if metric:
        rows.append({"name": metric["label"], "step": _s(loc, "why_step", a=A, b=B), "now": metric["value"],
                     "prev": metric.get("delta") or "—", "prev_tone": metric.get("delta_tone") or "na",
                     "band": metric.get("band") or "—", "rg": metric.get("rg"), "bench_key": metric["bench_key"]})
    for n in range(issue["i"], issue["j"]):
        st, nx = stages[n], stages[n + 1]
        if not st.get("link") or (metric and issue["j"] - issue["i"] == 1):
            continue
        rows.append({"name": _s(loc, "why_step", a=st["label"], b=nx["label"]), "step": "",
                     "now": st["link"]["go"]["all"], "prev": "—", "prev_tone": "na", "band": "—", "rg": None,
                     "bench_key": ""})
    if metric:
        h3 = _s(loc, "why_h_bench", label=metric["label"], band=metric.get("band") or "—")
    elif has_issue:
        h3 = _s(loc, "why_h_flow", a=A, b=B)
    else:
        h3 = _s(loc, "why_h_none")
    others = [w for w in watch if w["tone"] == "down" and (not metric or w["bench_key"] != metric["bench_key"])]
    if not metric:  # a flow step without 業界目安: the metrics that are off become the evidence rows
        rows += [{"name": w["label"], "step": "", "now": w["value"], "prev": w.get("delta") or "—",
                  "prev_tone": w.get("delta_tone") or "na", "band": w.get("band") or "—", "rg": w.get("rg"),
                  "bench_key": w["bench_key"]} for w in others]
        others = []
    none_off = not any(w["tone"] == "down" for w in watch)

    # ④
    acts = [{"n": n + 1, "title": t_, "why": w_, "check": c_, "link": l_} for n, (t_, w_, c_, l_) in enumerate(cat["acts"])]
    gain_txt = _s(loc, "gain", n=gain["n"]) if gain else ""
    if gain:
        h4 = _s(loc, "do_h_gain", label=metric["label"], low=gain["low"], target=B, gain=gain_txt)
        calc = _s(loc, "do_calc", base=gain["base"], low=gain["low"], now=gain["now"])
    else:
        h4, calc = _s(loc, "do_h", a=A, b=B), ""

    # 0 総評 (sentence + tiles). 1〜3 = where / why / do. 「大丈夫？」was absorbed into 0.
    toc = [
        {"n": 0, "q": _s(loc, "q0"), "href": "#q0"},
        {"n": 1, "q": _s(loc, "q2"), "href": "#q2"},
        {"n": 2, "q": _s(loc, "q3"), "href": "#q3"},
        {"n": 3, "q": _s(loc, "q4"), "href": "#q4"},
    ]

    prompt = _prompt(loc=loc, site=site, ind=industry_label, beh=behavior_label, period=period_label,
                     verdict=verdict, stages=stages, a=A, b=B, rows=rows, gain=gain_txt, acts=acts, board=board,
                     bench_info=bench_info)
    return {
        "q": {k: _s(loc, k) for k in ("q0", "q2", "q3", "q4", "ref", "ref_k", "toc", "why", "check",
                                       "others", "others_more", "do_note", "go_edit", "go_ch", "go_gl")},
        "toc": toc,
        "s1": s1, "s2": s2, "note": note, "h3": h3, "rows": rows, "others": others, "none_off": none_off,
        "h4": h4, "calc": calc, "acts": acts, "kind": issue["kind"],
        "next2": _s(loc, "next2", a=A), "next3": _s(loc, "next3"), "next4": _s(loc, "next4"),
        # Display numbers on section headers (anchors stay #q2/#q3/#q4 for stable deep links)
        "n_where": 1, "n_why": 2, "n_do": 3,
        "ai": {k: _s(loc, k) for k in ("ai_btn", "ai_lead", "ai_ask_k", "ai_cause", "ai_ideas", "ai_report",
                                        "ai_anon", "ai_detail", "ai_copy", "ai_copied", "ai_copy_fail", "ai_note")},
        "prompt": prompt,
    }


def _prompt(*, loc: str, site: str, ind: str, beh: str, period: str, verdict: dict[str, Any],
            stages: list[dict[str, Any]], a: str, b: str, rows: list[dict[str, Any]], gain: str,
            acts: list[dict[str, Any]], board: dict[str, Any], bench_info: Any) -> dict[str, Any]:
    """Pieces of the prompt; static/js/story.js joins them (site name and details are the viewer's choice)."""
    sep = "、" if loc == "ja" else ", "

    def paren(parts: list[str]) -> str:
        parts = [p for p in parts if p]
        if not parts:
            return ""
        return ("（" + " · ".join(parts) + "）") if loc == "ja" else (" (" + " · ".join(parts) + ")")

    s1 = [_s(loc, "p_s1")]
    for k in verdict.get("tiles", []):
        prev = _s(loc, "p_prev", d=k["prev"]["text"]) if k.get("prev", {}).get("text") else ""
        band = _s(loc, "p_band", band=k["bench"]["band"]) if k.get("bench", {}).get("band") else ""
        s1.append(f"- {k['label']} {k['value']}{paren([prev, band])}")
    s2 = [_s(loc, "p_s2"), " → ".join(f"{st['label']} {_fmt_int(float(st.get('users') or 0))}" for st in stages
                                       if st.get("users") is not None)]
    s3 = [_s(loc, "p_s3", a=a, b=b)]
    for r in rows:
        prev = _s(loc, "p_prev", d=r["prev"]) if r["prev"] not in ("", "—") else ""
        band = _s(loc, "p_band", band=r["band"]) if r["band"] not in ("", "—") else ""
        s3.append(f"- {r['name']} {r['now']}{paren([prev, band])}")
    if gain:
        s3.append("- " + _s(loc, "p_gain", gain=gain))
    s4 = [_s(loc, "p_s4")] + [f"{x['n']}. {x['title']}" for x in acts]
    s5 = [_s(loc, "p_s5")]
    for r in board.get("funnel", []):
        info = bench_info(r.get("value_num"), r.get("bench")) if r.get("bench") else None
        band = _s(loc, "p_band", band=info["band"]) if info and info.get("band") else ""
        s5.append(f"- {r['label']} {r['value']}{paren([band])}")
    return {
        "role": _s(loc, "p_role"),
        "site_anon": _s(loc, "p_site_anon", ind=ind or "—", beh=beh or "—", period=period),
        "site_named": _s(loc, "p_site_named", site=site or "—", ind=ind or "—", beh=beh or "—", period=period),
        "has_site": bool(site),
        "body": "\n\n".join("\n".join(x) for x in (s1, s2, s3, s4)),
        "details": "\n".join(s5),
        "ask_k": _s(loc, "p_ask"),
        "asks": {"cause": _s(loc, "p_cause", a=a, b=b), "ideas": _s(loc, "p_ideas", a=a, b=b),
                 "report": _s(loc, "p_report")},
        "tail": _s(loc, "p_tail"),
        "sep": sep,
    }
