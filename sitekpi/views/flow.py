"""行動フロー panel — view model (stages, step conversion, channel split)."""

from __future__ import annotations

from typing import Any

from sitekpi.board.data import CHANNEL_COLORS
from sitekpi.i18n import t
from sitekpi.packs.flows import step_label

TOP_CHANNELS = 4
OTHER_COLOR = "#cbd5e1"


def _int(n: float) -> str:
    return f"{int(round(n)):,}"


def _pct(part: float, whole: float) -> float | None:
    return 100.0 * part / whole if whole else None


def _fmt_pct(v: float | None) -> str:
    if v is None:
        return "—"
    if v and v < 1:
        return f"{v:.2f}%"
    return f"{v:.1f}%"


def _group_channels(flow: dict[str, Any], loc: str) -> list[dict[str, Any]]:
    """Top channels by arrivals + one 「その他」 bucket."""
    entry_by: dict[str, int] = flow.get("entry_by") or {}
    by_ch: dict[str, dict[str, int]] = flow.get("by_channel") or {}
    names = sorted(entry_by, key=lambda n: -entry_by[n])
    top, rest = names[:TOP_CHANNELS], names[TOP_CHANNELS:]
    groups = [
        {"id": f"fc{i}", "name": n, "color": CHANNEL_COLORS.get(n, "#94a3b8"),
         "entry": entry_by[n], "steps": dict(by_ch.get(n) or {})}
        for i, n in enumerate(top)
    ]
    if rest:
        steps: dict[str, int] = {}
        for n in rest:
            for ev, v in (by_ch.get(n) or {}).items():
                steps[ev] = steps.get(ev, 0) + v
        groups.append({"id": "fco", "name": t("flow.other", loc, n=len(rest)), "color": OTHER_COLOR,
                       "entry": sum(entry_by[n] for n in rest), "steps": steps})
    return groups


def flow_context(
    *,
    max_branches: int = 0,
    branches: list[dict[str, str]] | None = None,
    pack: str,
    flow: dict[str, Any] | None,
    steps: list[dict[str, str]],
    locale: str,
    live: bool,
    event_options: list[dict[str, Any]] | None = None,
    error: str | None = None,
) -> dict[str, Any] | None:
    if not steps:
        return None
    loc = locale
    flow = flow or {"entry": 0, "entry_by": {}, "totals": {}, "by_channel": {}, "sample": not live}
    entry = int(flow.get("entry") or 0)
    totals: dict[str, int] = flow.get("totals") or {}
    channels = _group_channels(flow, loc)
    ch_total_entry = sum(c["entry"] for c in channels) or 1

    stages: list[dict[str, Any]] = []
    stages.append({
        "key": "entry", "label": t("flow.entry", loc), "event": "", "mapped": False,
        "above": [], "below": [],
        "users": entry, "missing": entry <= 0,
        "users_fmt": {"all": _int(entry), **{c["id"]: _int(c["entry"]) for c in channels}},
        "reach_pct": 100.0, "reach": {"all": "100%", **{c["id"]: "100%" for c in channels}},
        "mix": [{"name": c["name"], "color": c["color"], "pct": round(100 * c["entry"] / ch_total_entry, 1)}
                for c in channels],
    })
    for s in steps:
        ev = s["event"]
        users = int(totals.get(ev, 0))
        ch_users = {c["id"]: int(c["steps"].get(ev, 0)) for c in channels}
        ch_sum = sum(ch_users.values()) or 1
        reach = _pct(users, entry)
        stages.append({
            "key": s["step"], "event": ev, "step": s["step"],
            "label": step_label(s["step"], loc, pack),
            "mapped": ev != s["step"], "users": users, "missing": users <= 0,
            "above": [], "below": [],
            "users_fmt": {"all": _int(users), **{cid: _int(v) for cid, v in ch_users.items()}},
            "reach_pct": reach or 0.0,
            "reach": {"all": _fmt_pct(reach),
                      **{c["id"]: _fmt_pct(_pct(ch_users[c["id"]], c["entry"])) for c in channels}},
            "mix": [{"name": c["name"], "color": c["color"], "pct": round(100 * ch_users[c["id"]] / ch_sum, 1)}
                    for c in channels] if users else [],
            "ch_users": ch_users,
        })

    # 分岐: other behaviours at the same stage — compared with the stage before
    by_key = {st["key"]: i for i, st in enumerate(stages)}
    for b in branches or []:
        i = by_key.get(b["at"])
        if i is None:
            continue
        before = stages[i - 1]
        users = int(totals.get(b["event"], 0))
        from_prev = _pct(users, before["users"]) if before["users"] and users else None
        stages[i][b["pos"]].append({
            "id": b["id"], "event": b["event"], "label": b["label"] or b["event"],
            "custom_label": b["label"], "users": users, "missing": users <= 0,
            "users_fmt": _int(users),
            "reach": _fmt_pct(_pct(users, entry)) if users else "—",
            "from_prev": _fmt_pct(min(from_prev, 100.0)) if from_prev is not None else "—",
            "vs_main": _fmt_pct(_pct(users, stages[i]["users"])) if users and stages[i]["users"] else "—",
            "prev_label": before["label"], "main_label": stages[i]["label"],
        })

    # Links between stages: share that went on to the next step, and the drop-off.
    links: list[dict[str, Any]] = []
    worst: tuple[float, int] | None = None
    for i in range(1, len(stages)):
        a, b = stages[i - 1], stages[i]
        ok = a["users"] > 0 and b["users"] > 0
        go = _pct(b["users"], a["users"]) if ok else None
        go = min(go, 100.0) if go is not None else None
        per: dict[str, str] = {"all": _fmt_pct(go)}
        drops: dict[str, str] = {"all": _fmt_pct(100.0 - go) if go is not None else "—"}
        for c in channels:
            av = c["entry"] if a["key"] == "entry" else a["ch_users"][c["id"]]
            bv = b["ch_users"][c["id"]]
            g = min(_pct(bv, av), 100.0) if av and bv else None
            per[c["id"]] = _fmt_pct(g)
            drops[c["id"]] = _fmt_pct(100.0 - g) if g is not None else "—"
        drop = 100.0 - go if go is not None else None
        links.append({"go": per, "drop": drops["all"], "drops": drops,
                      "drop_num": drop, "worst": False, "from": a["label"], "to": b["label"]})
        if drop is not None and (worst is None or drop > worst[0]):
            worst = (drop, len(links) - 1)
    if worst:
        links[worst[1]]["worst"] = True
    for i, st in enumerate(stages):
        st["link"] = links[i] if i < len(links) else None  # link to the next stage

    # Channel summary: share of arrivals that reached the last measured step.
    last = next((st for st in reversed(stages[1:]) if st["users"] > 0), None)
    ch_rows = []
    if last:
        for c in channels:
            r = _pct(last["ch_users"][c["id"]], c["entry"])
            ch_rows.append({"id": c["id"], "name": c["name"], "color": c["color"],
                            "entry": _int(c["entry"]), "rate": r, "rate_fmt": _fmt_pct(r),
                            "best": False, "low": False})
        rated = [r for r in ch_rows if r["rate"] is not None and r["rate"] > 0]
        if len(rated) >= 2:
            hi_row = max(rated, key=lambda r: r["rate"])
            lo_row = min(rated, key=lambda r: r["rate"])
            if hi_row["rate"] >= lo_row["rate"] * 1.1:  # ignore near-ties
                hi_row["best"], lo_row["low"] = True, True

    insights: list[str] = []
    if worst:
        lk = links[worst[1]]
        insights.append(t("flow.insight_drop", loc, a=lk["from"], b=lk["to"], pct=lk["drop"]))
    best = next((r for r in ch_rows if r.get("best")), None)
    low = next((r for r in ch_rows if r.get("low")), None)
    if best and low and last:
        insights.append(t("flow.insight_channel", loc, step=last["label"], best=best["name"],
                          best_pct=best["rate_fmt"], low=low["name"], low_pct=low["rate_fmt"]))
    missing = [st for st in stages[1:] if st["missing"]]
    if missing:
        insights.append(t("flow.insight_missing_live" if live else "flow.insight_missing", loc,
                          steps="・".join(st["label"] for st in missing)))

    return {
        "pack": pack,
        "live": live,
        "sample": bool(flow.get("sample")),
        "error": error,
        "stages": stages,
        "channels": [{"id": c["id"], "name": c["name"], "color": c["color"]} for c in channels],
        "ch_rows": ch_rows,
        "last_label": last["label"] if last else "",
        "insights": insights,
        "event_options": event_options or [],
        # live boards can show up to max_branches other behaviours above / below a stage
        "can_add": live and len(branches or []) < max_branches,
        "n_branches": len(branches or []),
        "max_branches": max_branches,
    }
