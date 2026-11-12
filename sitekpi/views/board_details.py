"""L2 詳しい数字 view model (stacked categories + 説明 cards; no HTML).

Category order tells the story: funnel → engage → channels → audience → events → business.
Rows open for 業界目安 / 目安差 / 意味; 帯 stays in the tooltip, not the closed row.
"""

from __future__ import annotations

from typing import Any

from sitekpi.i18n import t
from sitekpi.views.board_bench import _bench_info, _bench_view, _group_channels
from sitekpi.views.board_ctx import _UNLINKED, _kind_label

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


def _outside_score(r: dict[str, Any]) -> float:
    """How far past the 業界目安 band (0 if unknown) — used to pick the furthest 要注意."""
    rg = (r.get("bench") or {}).get("rg") or {}
    if rg.get("state") != "short":
        return 0.0
    raw = str(rg.get("main") or "0").replace("+", "").replace("−", "-").replace(",", "")
    try:
        return abs(float(raw))
    except ValueError:
        return 0.0


def _group_lede(rows: list[dict[str, Any]], loc: str) -> str:
    """One line: why open this category — furthest 要注意, or 「目安内」 when judged rows are fine.

    Skip when nothing is comparable (events / share-only channels) — no filler.
    """
    judged = [
        r for r in rows
        if (r.get("bench") or {}).get("kind") == "judge" and (r.get("bench") or {}).get("judge")
    ]
    if not judged:
        return ""
    bad = [r for r in judged if r["bench"]["judge"] == "down"]
    if not bad:
        return t("detail.lede_ok", loc)
    worst = max(bad, key=_outside_score)
    return t(
        "detail.lede_warn",
        loc,
        label=worst["label"],
        value=worst["value"],
        # the same 「あと」 as the table (to the near edge of the range, then the far edge), not 目安差 (vs. the middle)
        left=((worst["bench"].get("rg") or {}).get("main") or "") + ((worst["bench"].get("rg") or {}).get("rest") or ""),
    )


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
            # v5: the first three categories (転換ファネル · 売上 · エンゲージ) start open, the rest closed
            "collapsed": bool(rows) and len(groups) >= 3,
            # Why open this block: furthest 要注意, or 目安内 (empty when nothing is judged)
            "lede": _group_lede(rows, loc) if rows else "",
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

