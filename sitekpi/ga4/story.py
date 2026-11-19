"""GA4 fetch for the story chapters (board/story_x.py documents the shape).

Up to 14 small reports, sent as batches of 5 side by side, so the page waits for about one round trip.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from typing import Any

from sitekpi.board.story_x import DEVICES, WEEKS, WINDOW, today_jst, week0
from sitekpi.ga4.report import PERIOD_RANGE, _event_filter, _f, _i, _req, _vals

PAGES = 60  # landing / viewed pages asked for (the board shows the top ones, the table up to 30)


def _req2(ranges: list[tuple[str, str]], metrics: list[str], dimensions: list[str] | None = None,
          dimension_filter: Any | None = None, limit: int | None = None) -> Any:
    """A report over several date ranges (GA4 adds a dateRange dimension to each row)."""
    from sitekpi.ga4.report import DateRange

    req = _req(ranges[0][0], ranges[0][1], metrics, dimensions, dimension_filter, limit)
    del req.date_ranges[:]
    for n, (a, b) in enumerate(ranges):
        req.date_ranges.append(DateRange(start_date=a, end_date=b, name=f"r{n}"))
    return req


def _ordered(req: Any, metric: str) -> Any:
    """Biggest first (GA4 does not promise an order otherwise, and the list is cut at the limit)."""
    from sitekpi.ga4.report import OrderBy

    req.order_bys.append(OrderBy(metric=OrderBy.MetricOrderBy(metric_name=metric), desc=True))
    return req


def release_ranges(day: date, today: date | None = None) -> tuple[tuple[str, str], tuple[str, str]] | None:
    """14 days before the release and the 14 days from it — None until those 14 days are over."""
    today = today or today_jst()
    if (today - day).days < WINDOW + 1:  # the last day must be yesterday or earlier
        return None
    before = (day - timedelta(days=WINDOW), day - timedelta(days=1))
    after = (day, day + timedelta(days=WINDOW - 1))
    return (before[0].isoformat(), before[1].isoformat()), (after[0].isoformat(), after[1].isoformat())


def fetch_story_x(session: dict[str, Any], *, period: str, events: list[str], last: str,
                  release: dict[str, Any] | None = None) -> tuple[dict[str, Any] | None, str | None]:
    from sitekpi.ga4 import data as g

    info = g.connection_info(session)
    if not info or not g.HAS_DATA or not g.HAS_GOOGLE_AUTH or not events:
        return None, None
    cur_start, cur_end, prev_start, prev_end, _label = PERIOD_RANGE.get(period) or PERIOD_RANGE["28d"]
    filt = _event_filter(events)
    n_ev = len(events) + 5
    reqs = [
        _req(cur_start, cur_end, ["totalUsers"], ["deviceCategory"], limit=10),
        _req(cur_start, cur_end, ["totalUsers"], ["deviceCategory", "eventName"], filt, 10 * n_ev),
        _req("55daysAgo", "yesterday", ["totalUsers"], ["nthWeek"], limit=20),
        _req("55daysAgo", "yesterday", ["totalUsers"], ["nthWeek", "eventName"], filt, 20 * n_ev),
        _req(cur_start, cur_end, ["activeUsers", "purchaseRevenue"]),
        _req(prev_start, prev_end, ["activeUsers", "purchaseRevenue"]),
        _req(cur_start, cur_end, ["totalUsers"], ["newVsReturning"], limit=5),
        _req(prev_start, prev_end, ["totalUsers"], ["newVsReturning"], limit=5),
    ]
    reqs.append(_req(cur_start, cur_end, ["totalUsers"], ["newVsReturning", "eventName"], filt, 3 * n_ev))
    # v7.3 pages: where visits start (and how far they get), and the most viewed pages
    reqs.append(_ordered(_req(cur_start, cur_end, ["totalUsers", "engagementRate"], ["landingPage"], limit=PAGES), "totalUsers"))
    reqs.append(_ordered(_req(cur_start, cur_end, ["totalUsers"], ["landingPage", "eventName"], filt, 10000), "totalUsers"))
    reqs.append(_ordered(_req(cur_start, cur_end, ["screenPageViews"], ["pagePath", "pageTitle", "hostName"], limit=PAGES), "screenPageViews"))
    rel_day = None
    rel_ranges = None
    if release and release.get("date"):
        try:
            rel_day = date.fromisoformat(str(release["date"]))
        except ValueError:
            rel_day = None
        rel_ranges = release_ranges(rel_day) if rel_day else None
    n_base = len(reqs)
    if rel_ranges:
        reqs += [_req2(list(rel_ranges), ["totalUsers"], limit=5),
                 _req2(list(rel_ranges), ["totalUsers"], ["eventName"], filt, 2 * n_ev)]
    try:
        creds = g.creds_from_session(session)
        if not creds:
            return None, "auth"
        client = g.BetaAnalyticsDataClient(credentials=creds)
        from sitekpi.ga4.report import BatchRunReportsRequest

        chunks = [reqs[i:i + 5] for i in range(0, len(reqs), 5)]
        pid = info["property_id"]

        def run(chunk: list[Any]) -> list[Any]:
            return list(client.batch_run_reports(
                BatchRunReportsRequest(property=f"properties/{pid}", requests=chunk)).reports)

        with ThreadPoolExecutor(max_workers=len(chunks)) as pool:
            rep = [r for part in pool.map(run, chunks) for r in part]
    except Exception as exc:  # noqa: BLE001
        return None, str(exc)

    devices: dict[str, Any] = {d: {"entry": 0, "ev": {}} for d in DEVICES}
    for r in rep[0].rows or []:
        d = r.dimension_values[0].value
        if d in devices:
            devices[d]["entry"] = _i(_vals(r)[0])
    for r in rep[1].rows or []:
        d = r.dimension_values[0].value
        if d in devices:
            devices[d]["ev"][r.dimension_values[1].value] = _i(_vals(r)[0])
    wk_entry = [0] * WEEKS
    for r in rep[2].rows or []:
        i = _i(r.dimension_values[0].value, -1)
        if 0 <= i < WEEKS:
            wk_entry[i] = _i(_vals(r)[0])
    wk_ev: dict[str, list[int]] = {e: [0] * WEEKS for e in events}
    for r in rep[3].rows or []:
        i = _i(r.dimension_values[0].value, -1)
        name = r.dimension_values[1].value
        if 0 <= i < WEEKS and name in wk_ev:
            wk_ev[name][i] = _i(_vals(r)[0])

    def one(r: Any, k: int) -> float:
        return _f(_vals(r.rows[0])[k]) if r.rows else 0.0

    money = None
    if one(rep[4], 1) > 0 or one(rep[5], 1) > 0:
        money = {"cur": {"revenue": one(rep[4], 1)}, "prev": {"revenue": one(rep[5], 1)}}

    def nvr_map(r: Any) -> dict[str, int]:
        return {row.dimension_values[0].value: _i(_vals(row)[0]) for row in r.rows or []}

    users, p_users = nvr_map(rep[6]), nvr_map(rep[7])
    by_ev: dict[str, dict[str, int]] = {"new": {}, "returning": {}}
    for row in rep[8].rows or []:
        side = row.dimension_values[0].value
        if side in by_ev:
            by_ev[side][row.dimension_values[1].value] = _i(_vals(row)[0])
    nvr = None
    if users.get("new") and users.get("returning"):
        nvr = {"new": {"users": users["new"], "ev": by_ev["new"]},
               "returning": {"users": users["returning"], "ev": by_ev["returning"]},
               "prev_returning": p_users.get("returning", 0)}

    pages = None
    try:
        from sitekpi.board.story_pages import from_ga4

        pages = from_ga4(
            [(r.dimension_values[0].value, _i(_vals(r)[0]), round(100 * _f(_vals(r)[1]), 1)) for r in rep[9].rows or []],
            [(r.dimension_values[0].value, r.dimension_values[1].value, _i(_vals(r)[0])) for r in rep[10].rows or []],
            [(r.dimension_values[0].value, r.dimension_values[1].value, _i(_vals(r)[0]), r.dimension_values[2].value)
             for r in rep[11].rows or []],
            int(getattr(rep[11], "row_count", 0) or 0), events)
    except (IndexError, ValueError):
        pages = None

    rel = None
    if rel_day:
        rel = {"date": rel_day.isoformat(), "days_after": (today_jst() - rel_day).days, "before": None, "after": None}
        if rel_ranges:
            sides: dict[str, dict[str, Any]] = {"r0": {"entry": 0, "ev": {}}, "r1": {"entry": 0, "ev": {}}}
            for r in rep[n_base].rows or []:
                k = r.dimension_values[-1].value
                if k in sides:
                    sides[k]["entry"] = _i(_vals(r)[0])
            for r in rep[n_base + 1].rows or []:
                k = r.dimension_values[-1].value
                if k in sides:
                    sides[k]["ev"][r.dimension_values[0].value] = _i(_vals(r)[0])
            rel["before"], rel["after"] = sides["r0"], sides["r1"]
    return {"week0": week0().isoformat(), "weeks": {"entry": wk_entry, "ev": wk_ev}, "devices": devices,
            "money": money, "nvr": nvr, "release": rel, "pages": pages}, None
