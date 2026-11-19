"""v7.3 page-level numbers for the story (docs/plan s03): ② 入口ページ別, ④ どのページで？, 詳しい数字 › ページ別.

Reads ``story_x["pages"]`` (board/story_pages.py documents the shape) and the flow stages.
"""

from __future__ import annotations

from typing import Any

from sitekpi.format import fmt_int
from sitekpi.views.story_more import MIN_BASE, _pct, _rate, _s, _target

SHOW = 6       # pages drawn in ② / ④
TABLE = 10     # rows in the table before 「もっと見る」
TABLE_MAX = 30


def _title(t: Any, loc: str) -> str:
    if isinstance(t, dict):
        return str(t.get(loc) or t.get("ja") or "")
    return str(t or "")


def _pages(sx: dict[str, Any] | None) -> dict[str, Any] | None:
    pg = (sx or {}).get("pages")
    return pg if pg and (pg.get("entry") or pg.get("views")) else None


def _quad(share: float, rate: float, mid: float, overall: float) -> str:
    """Same split as the traffic map in ②: volume vs its median, rate vs the overall ±15%."""
    if share >= mid:
        return "core" if rate >= overall * 0.85 else "fix"
    return "grow" if rate >= overall * 1.15 else "watch"


def entry_pages(flow: dict[str, Any] | None, sx: dict[str, Any] | None, loc: str) -> dict[str, Any] | None:
    """② Which landing pages carry people to the deepest step enough people reach."""
    pg = _pages(sx)
    stages = (flow or {}).get("stages") or []
    k = _target(stages) if len(stages) >= 2 else None
    if not pg or k is None:
        return None
    ev, step = stages[k].get("event") or "", stages[k]["label"]
    entry = [e for e in pg.get("entry") or [] if e.get("users")]
    total = sum(e["users"] for e in entry)
    overall = _rate(float(stages[0].get("users") or 0), float(stages[k].get("users") or 0))
    shown = [e for e in entry if e["users"] >= MIN_BASE][:SHOW]
    if len(shown) < 2 or not total or not overall:
        return None
    shares = sorted(100.0 * e["users"] / total for e in shown)
    mid = shares[len(shares) // 2] if len(shares) % 2 else (shares[len(shares) // 2 - 1] + shares[len(shares) // 2]) / 2
    top_share = max(shares)
    rows = []
    for e in shown:
        share = 100.0 * e["users"] / total
        r = _rate(float(e["users"]), float((e.get("ev") or {}).get(ev, 0))) or 0.0
        q = _quad(share, r, mid, overall)
        rows.append({"title": _title(e.get("title"), loc) or e["path"], "path": e["path"], "url": e.get("url") or "", "users": fmt_int(e["users"]),
                     "share": f"{share:.0f}%", "w": round(100 * share / top_share, 1), "rate": _pct(r), "r": r,
                     "q": q, "q_label": _s(loc, "x_q_" + q), "low": q == "fix"})
    rest = [e for e in entry if e not in shown]
    fix = max((r for r in rows if r["q"] == "fix"), key=lambda r: float(r["share"][:-1]), default=None)
    grow = sorted((r for r in rows if r["q"] == "grow"), key=lambda r: -r["r"])[:2]
    watch = [r for r in rows if r["q"] == "watch"][:2]
    avg = _pct(overall)
    if fix:
        head = _s(loc, "x_pg_h_fix", name=fix["title"], share=fix["share"], step=step, rate=fix["rate"], avg=avg)
    elif grow:
        head = _s(loc, "x_pg_h_grow", name=grow[0]["title"], step=step, rate=grow[0]["rate"], avg=avg)
    else:
        head = _s(loc, "x_pg_h_even", avg=avg)
    notes = []
    if fix:
        notes.append({"q": "fix", "k": _s(loc, "x_q_fix"), "t": _s(loc, "x_pg_fix_t", name=fix["title"], share=fix["share"], rate=fix["rate"], avg=avg)})
    if grow:
        notes.append({"q": "grow", "k": _s(loc, "x_q_grow"), "t": _s(loc, "x_pg_grow_t", names="・".join(f"「{r['title']}」" for r in grow))})
    if watch:
        notes.append({"q": "watch", "k": _s(loc, "x_q_watch"), "t": _s(loc, "x_pg_watch_t", names="・".join(f"「{r['title']}」" for r in watch))})
    n_rest = max(len(rest), int(pg.get("n_pages") or 0) - len(shown)) if rest else 0
    return {
        "k": _s(loc, "x_pg_k", step=step), "sub": _s(loc, "x_pg_sub"), "head": head, "rows": rows, "notes": notes,
        "col_page": _s(loc, "x_pg_col_page"), "col_share": _s(loc, "x_pg_col_share"), "col_rate": _s(loc, "x_who_col_rate", step=step),
        "foot": _s(loc, "x_pg_rest", n=fmt_int(n_rest), people=fmt_int(sum(e["users"] for e in rest)) + _s(loc, "x_people_sfx"), step=step)
        if rest else _s(loc, "x_pg_rest0", step=step),
    }


def issue_rows(issue: dict[str, Any], stages: list[dict[str, Any]], sx: dict[str, Any] | None,
               row: Any, loc: str) -> list[dict[str, Any]]:
    """④ The issue's rate per landing page (rows built by where_when's ``row`` so the ruler is the same)."""
    pg = _pages(sx)
    if not pg:
        return []
    a_ev = stages[issue["i"]].get("event") if issue["i"] else None
    b_ev = stages[issue["j"]].get("event") or ""
    out: list[dict[str, Any]] = []
    rest_a = rest_b = 0.0
    rest_n = 0
    for e in pg.get("entry") or []:
        evs = e.get("ev") or {}
        a = float(e.get("users") or 0) if a_ev is None else float(evs.get(a_ev, 0))
        b = float(evs.get(b_ev, 0))
        if not a:
            continue
        if len(out) < SHOW and a >= MIN_BASE:
            r = row(_title(e.get("title"), loc) or e["path"], a, b)
            if r:
                r["path"], r["url"] = e["path"], e.get("url") or ""
                out.append(r)
                continue
        rest_a, rest_b, rest_n = rest_a + a, rest_b + b, rest_n + 1
    out.sort(key=lambda r: -float(r["base"].replace(",", "")))
    if out and rest_a:
        r = row(_s(loc, "x_pgw_other", n=fmt_int(rest_n)), rest_a, rest_b)
        if r:
            r["path"], r["url"], r["rest"] = "", "", True
            out.append(r)
    return out if len([r for r in out if not r.get("rest")]) >= 2 else []


def issue_head(rows: list[dict[str, Any]], A: str, B: str, loc: str) -> dict[str, str] | None:
    named = [r for r in rows if not r.get("rest") and not r["few"]]
    if len(named) < 2:
        return None
    worst = min(named, key=lambda r: r["rate"])
    others = [r for r in named if r is not worst]
    lo, hi = min(r["rate"] for r in others), max(r["rate"] for r in others)
    if not worst["low"] or worst["rate"] > lo * 0.8:  # no page stands out
        return {"head": _s(loc, "x_pgw_h_even"), "name": "", "t": ""}
    return {"head": _s(loc, "x_pgw_h", name=worst["name"], a=A, rate=worst["rate_fmt"], lo=_pct(lo), hi=_pct(hi)),
            "name": worst["name"],
            "t": _s(loc, "x_pgw_t", name=worst["name"], a=A, b=B, rate=worst["rate_fmt"]), "check": _s(loc, "x_pgw_check")}


def table(flow: dict[str, Any] | None, sx: dict[str, Any] | None, loc: str) -> dict[str, Any] | None:
    """詳しい数字 › ページ別: most viewed pages with what the visits that started there did."""
    pg = _pages(sx)
    if not pg or not pg.get("views"):
        return None
    stages = (flow or {}).get("stages") or []
    k = _target(stages) if len(stages) >= 2 else None
    ev = stages[k].get("event") if k is not None else None
    step = stages[k]["label"] if k is not None else ""
    entry = {e["path"]: e for e in pg.get("entry") or []}
    rows = []
    for v in pg["views"][:TABLE_MAX]:
        e = entry.get(v["path"]) or {}
        u = int(e.get("users") or 0)
        c = int((e.get("ev") or {}).get(ev, 0)) if ev and e else None
        r = _rate(float(u), float(c)) if u >= MIN_BASE and c is not None else None
        rows.append({"title": _title(v.get("title"), loc) or v["path"], "path": v["path"], "url": v.get("url") or "",
                     "views": fmt_int(v["views"]), "views_n": v["views"],
                     "entry": fmt_int(u) if u else "—", "entry_n": u,
                     "eng": _pct(e.get("eng")) if e.get("eng") is not None and u else "—", "eng_n": e.get("eng") if u else -1,
                     "conv": fmt_int(c) if c is not None and u else "—", "conv_n": c if c is not None and u else -1,
                     "rate": _pct(r) if r is not None else "—", "rate_n": r if r is not None else -1})
    n = int(pg.get("n_pages") or len(pg["views"]))
    return {
        "k": _s(loc, "x_pt_k"), "n": _s(loc, "x_pt_n", n=fmt_int(n)), "lead": _s(loc, "x_pt_lead") + (_s(loc, "x_pt_open") if any(r["url"] for r in rows) else ""), "sort": _s(loc, "x_pt_sort"),
        "cols": [("title", _s(loc, "x_pt_page"), "text"), ("views", _s(loc, "x_pt_views"), "num"),
                 ("entry", _s(loc, "x_pt_entry"), "num"), ("eng", _s(loc, "x_pt_eng"), "num")]
        + ([("conv", step, "num"), ("rate", _s(loc, "x_who_col_rate", step=step), "num")] if ev else []),
        "rows": rows[:TABLE], "more": rows[TABLE:],
        "more_k": _s(loc, "x_pt_more", n=len(rows) - TABLE) if len(rows) > TABLE else "",
        "note": _s(loc, "x_pt_note", step=step or "—"),
    }
