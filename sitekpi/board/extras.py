"""詳しい数字の追加分 — 8週の推移, デバイス, 売上, and a few more site totals.

Same shape for sample / demo boards (``sample_extras``, deterministic) and live GA4
(``live_extras``). The board view (views/board.py) only reads this shape:

    weeks:   {series key: [8 numbers, oldest first]}   keys: uu, sessions, engaged, pv,
             new_users, avg_session, revenue, tx, "ev:<event name>"
    cur/prev: {avg_session (s), events_per_session, key_events, scrolled, dau, wau, mau,
               dau_mau (%), revenue, tx, aov, item_revenue}   (missing → absent)
    has_revenue: bool
    devices: [{id, sessions, prev_sessions, users, conv_users}]
"""

from __future__ import annotations

from typing import Any

from sitekpi.board.prev import _jitter, _mmss

WEEKS = 8
DEVICES = ("mobile", "desktop", "tablet")
_SALE_EVENTS = ("purchase",)


def _series(tag: str, prev_total: float, cur_total: float, *, rate: bool = False) -> list[float]:
    """8 weekly points: 4 from the previous period, 4 from this one (sums match the totals)."""
    out = []
    for i in range(WEEKS):
        base = prev_total if i < WEEKS // 2 else cur_total
        j = _jitter(f"{tag}|w{i}", 0.94, 1.06)
        out.append(round(base * j, 2) if rate else round(base / (WEEKS // 2) * j))
    return out


def sample_extras(slug: str, data: dict[str, Any], prev: dict[str, Any] | None) -> dict[str, Any]:
    """Deterministic extras for 見本 / デモ boards, consistent with the pack's DEMO numbers."""
    tag = f"x|{slug}|"
    prev = prev or data
    uu, sessions = int(data.get("uu") or 0), int(data.get("sessions") or 0)
    p_uu, p_sessions = int(prev.get("uu") or uu), int(prev.get("sessions") or sessions)
    counts = {str(k): int(v) for k, v in (data.get("event_counts") or {}).items()}
    p_counts = {str(k): int(v) for k, v in (prev.get("event_counts") or {}).items()}
    events_total = max(sum(counts.values()), int(sessions * 7.4))
    p_events_total = max(sum(p_counts.values()), int(p_sessions * 7.2))
    avg_eng = _mmss(data.get("avg_time")) or 90
    p_avg_eng = _mmss(prev.get("avg_time")) or avg_eng

    def totals(u: int, s: int, ev: int, eng_s: int, c: dict[str, int], t: str, key_events: int) -> dict[str, Any]:
        mau = round(u * _jitter(t + "mau", 0.86, 0.92))
        dau = round(mau * _jitter(t + "dau", 0.045, 0.055))
        out: dict[str, Any] = {
            "avg_session": round(eng_s * _jitter(t + "ses", 1.25, 1.45)),
            "events_per_session": round(ev / s, 1) if s else 0.0,
            "key_events": key_events,
            "scrolled": int(c.get("scroll") or round(u * _jitter(tag + "scr", 0.28, 0.36))),
            "dau": dau,
            "wau": round(mau * _jitter(t + "wau", 0.26, 0.30)),
            "mau": mau,
            "dau_mau": round(100 * dau / mau, 1) if mau else 0.0,
        }
        tx = int(c.get("purchase") or 0)
        if tx:
            aov = round(6480 * _jitter(t + "aov", 0.97, 1.03))
            out.update({"tx": tx, "aov": aov, "revenue": tx * aov,
                        "item_revenue": round(tx * aov * _jitter(t + "item", 0.92, 0.95))})
        return out

    cur = totals(uu, sessions, events_total, avg_eng, counts, tag + "c|", int(data.get("signups") or 0))
    prv = totals(p_uu, p_sessions, p_events_total, p_avg_eng, p_counts, tag + "p|", int(prev.get("signups") or 0))
    weeks: dict[str, list[float]] = {
        "uu": _series(tag + "uu", p_uu, uu),
        "sessions": _series(tag + "ses", p_sessions, sessions),
        "engaged": _series(tag + "eng", float(prev.get("engaged_rate") or 0), float(data.get("engaged_rate") or 0), rate=True),
        "pv": _series(tag + "pv", int(prev.get("pageviews") or 0), int(data.get("pageviews") or 0)),
        "new_users": _series(tag + "new", int(prev.get("new_users") or 0), int(data.get("new_users") or 0)),
        "avg_session": _series(tag + "as", prv["avg_session"], cur["avg_session"], rate=True),
    }
    for name, n in counts.items():
        weeks["ev:" + name] = _series(tag + "ev" + name, p_counts.get(name, n), n)
    if cur.get("tx"):
        weeks["tx"] = weeks["ev:purchase"]
        weeks["revenue"] = _series(tag + "rev", prv.get("revenue") or cur["revenue"], cur["revenue"])
    share = {"mobile": 0.68, "desktop": 0.29, "tablet": 0.03}
    conv_rate = {"mobile": 0.62, "desktop": 1.48, "tablet": 0.9}  # × the site's CVR
    primary_users = int(data.get("signups") or 0)
    site_cvr = primary_users / uu if uu else 0.0
    devices = []
    for d in DEVICES:
        s = round(sessions * share[d] * _jitter(tag + "dv" + d, 0.97, 1.03))
        u = round(uu * share[d])
        devices.append({
            "id": d, "sessions": s, "users": u,
            "prev_sessions": round(p_sessions * share[d] * _jitter(tag + "dvp" + d, 0.95, 1.05)),
            "conv_users": round(u * site_cvr * conv_rate[d]),
        })
    return {"weeks": weeks, "cur": cur, "prev": prv, "has_revenue": bool(cur.get("tx")), "devices": devices}


def live_extras(session: dict[str, Any], *, period: str, events: list[str],
                primary: str) -> tuple[dict[str, Any] | None, str | None]:
    """The same shape from GA4 (3 batched round trips). (None, error) when GA4 says no."""
    from sitekpi.ga4 import data as g

    info = g.connection_info(session)
    if not info or not g.HAS_DATA or not g.HAS_GOOGLE_AUTH:
        return None, None
    cur_start, cur_end, prev_start, prev_end, _label = g.PERIOD_RANGE.get(period) or g.PERIOD_RANGE["28d"]
    try:
        creds = g.creds_from_session(session)
        if not creds:
            return None, "auth"
        client = g.BetaAnalyticsDataClient(credentials=creds)
        week_metrics = ["activeUsers", "sessions", "engagementRate", "screenPageViews", "newUsers",
                        "averageSessionDuration", "purchaseRevenue", "transactions"]
        tot_metrics = ["averageSessionDuration", "eventCount", "sessions", "keyEvents", "scrolledUsers",
                       "purchaseRevenue", "transactions", "averagePurchaseRevenue"]
        ev = [e for e in dict.fromkeys(events + ["purchase", "file_download"]) if e]
        reqs = [
            g._req("55daysAgo", "yesterday", week_metrics, ["nthWeek"], limit=20),
            g._req("55daysAgo", "yesterday", ["eventCount"], ["nthWeek", "eventName"], g._event_filter(ev), 400),
            g._req(cur_start, cur_end, tot_metrics),
            g._req(prev_start, prev_end, tot_metrics),
            g._req("yesterday", "yesterday", ["active1DayUsers", "active7DayUsers", "active28DayUsers"]),
            g._req(cur_start, cur_end, ["sessions", "activeUsers"], ["deviceCategory"], limit=10),
            g._req(prev_start, prev_end, ["sessions"], ["deviceCategory"], limit=10),
        ]
        if primary:
            reqs.append(g._req(cur_start, cur_end, ["totalUsers"], ["deviceCategory"],
                               g._event_filter([primary]), 10))
        rep = g._batch(client, info["property_id"], reqs)
    except Exception as exc:  # noqa: BLE001
        return None, str(exc)

    def vals(r: Any) -> list[str]:
        return g._vals(r)

    weeks: dict[str, list[float]] = {k: [0.0] * WEEKS for k in
                                     ("uu", "sessions", "engaged", "pv", "new_users", "avg_session", "revenue", "tx")}
    for r in rep[0].rows or []:
        i = g._i(r.dimension_values[0].value)
        if 0 <= i < WEEKS:
            v = vals(r)
            for k, j in (("uu", 0), ("sessions", 1), ("pv", 3), ("new_users", 4), ("revenue", 6), ("tx", 7)):
                weeks[k][i] = g._f(v[j])
            weeks["engaged"][i] = round(g._f(v[2]) * 100, 1)
            weeks["avg_session"][i] = round(g._f(v[5]))
    for r in rep[1].rows or []:
        i = g._i(r.dimension_values[0].value)
        name = r.dimension_values[1].value
        if 0 <= i < WEEKS:
            weeks.setdefault("ev:" + name, [0.0] * WEEKS)[i] = g._f(vals(r)[0])

    def totals(r: Any) -> dict[str, Any]:
        v = vals(r.rows[0]) if r.rows else ["0"] * len(tot_metrics)
        s = g._i(v[2])
        out: dict[str, Any] = {
            "avg_session": round(g._f(v[0])),
            "events_per_session": round(g._f(v[1]) / s, 1) if s else 0.0,
            "key_events": g._i(v[3]),
            "scrolled": g._i(v[4]),
        }
        if g._f(v[5]) > 0 or g._i(v[6]) > 0:
            out.update({"revenue": g._f(v[5]), "tx": g._i(v[6]), "aov": g._f(v[7])})
        return out

    cur, prv = totals(rep[2]), totals(rep[3])
    a = vals(rep[4].rows[0]) if rep[4].rows else ["0", "0", "0"]
    dau, wau, mau = g._i(a[0]), g._i(a[1]), g._i(a[2])
    cur.update({"dau": dau, "wau": wau, "mau": mau, "dau_mau": round(100 * dau / mau, 1) if mau else 0.0})
    prev_sess = {r.dimension_values[0].value: g._i(vals(r)[0]) for r in rep[6].rows or []}
    conv = {r.dimension_values[0].value: g._i(vals(r)[0]) for r in (rep[7].rows if len(rep) > 7 else []) or []}
    devices = []
    for r in rep[5].rows or []:
        d = r.dimension_values[0].value
        if d not in DEVICES:
            continue
        v = vals(r)
        devices.append({"id": d, "sessions": g._i(v[0]), "users": g._i(v[1]),
                        "prev_sessions": prev_sess.get(d, 0), "conv_users": conv.get(d, 0)})
    devices.sort(key=lambda x: DEVICES.index(x["id"]))
    return {"weeks": weeks, "cur": cur, "prev": prv, "has_revenue": "revenue" in cur, "devices": devices}, None
