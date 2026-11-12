"""GA4 fetches for 行動フロー and site basics (industry compare).

Auth / client symbols resolve via sitekpi.ga4.data so tests can monkeypatch the facade.
"""

from __future__ import annotations

from typing import Any

from sitekpi.ga4.report import PERIOD_RANGE, _batch, _event_filter, _f, _i, _req, _run, _vals


def fetch_flow(
    session: dict[str, Any],
    *,
    period: str,
    events: list[str],
) -> tuple[dict[str, Any] | None, str | None]:
    """行動フロー: users who arrived, and users who fired each step event — overall and per channel.

    Users are unique per row (totalUsers); a user who came from two channels is
    counted in both channel rows, so per-channel numbers are shown as shares.
    """
    from sitekpi.ga4 import data as g

    info = g.connection_info(session)
    if not info or not g.HAS_DATA or not g.HAS_GOOGLE_AUTH:
        return None, None
    ranges = PERIOD_RANGE.get(period) or PERIOD_RANGE["28d"]
    start, end = ranges[0], ranges[1]
    pid = info["property_id"]
    try:
        creds = g.creds_from_session(session)
        if not creds:
            return None, "GA4 認証が無効です。再接続してください。"
        client = g.BetaAnalyticsDataClient(credentials=creds)
        ch_dim = "sessionDefaultChannelGroup"
        reqs = [
            _req(start, end, ["totalUsers"]),
            _req(start, end, ["totalUsers"], [ch_dim], limit=25),
        ]
        if events:
            filt = _event_filter(events)
            reqs += [
                _req(start, end, ["totalUsers"], ["eventName"], filt, len(events) + 5),
                _req(start, end, ["totalUsers"], [ch_dim, "eventName"], filt, 500),
            ]
        reports = _batch(client, pid, reqs)  # one round trip
        total, by_ch_entry = reports[0], reports[1]
        entry = _i(_vals(total.rows[0])[0]) if total.rows else 0
        entry_by = {(r.dimension_values[0].value or "Other"): _i(_vals(r)[0]) for r in by_ch_entry.rows or []}
        totals: dict[str, int] = {e: 0 for e in events}
        by_channel: dict[str, dict[str, int]] = {c: {} for c in entry_by}
        if events:
            for r in reports[2].rows or []:
                totals[r.dimension_values[0].value] = _i(_vals(r)[0])
            for r in reports[3].rows or []:
                ch = r.dimension_values[0].value or "Other"
                by_channel.setdefault(ch, {})[r.dimension_values[1].value] = _i(_vals(r)[0])
        return {"entry": entry, "entry_by": entry_by, "totals": totals, "by_channel": by_channel, "sample": False}, None
    except Exception as exc:  # noqa: BLE001
        return None, str(exc)


def fetch_site_basics(session: dict[str, Any], *, period: str = "28d") -> dict[str, float] | None:
    """Users and engagement rate for the property (used to compare with an industry)."""
    from sitekpi.ga4 import data as g

    info = g.connection_info(session)
    if not info or not g.HAS_DATA or not g.HAS_GOOGLE_AUTH:
        return None
    ranges = PERIOD_RANGE.get(period) or PERIOD_RANGE["28d"]
    try:
        creds = g.creds_from_session(session)
        if not creds:
            return None
        client = g.BetaAnalyticsDataClient(credentials=creds)
        r = _run(client, info["property_id"], ranges[0], ranges[1], ["activeUsers", "engagementRate", "sessions"])
        if not r.rows:
            return None
        v = _vals(r.rows[0])
        return {"uu": _i(v[0]), "engaged_rate": round(_f(v[1]) * 100, 1), "sessions": _i(v[2])}
    except Exception:  # noqa: BLE001
        return None
