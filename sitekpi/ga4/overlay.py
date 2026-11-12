"""GA4 → DEMO-shaped overlay for the connected /live board.

Business KPI fields are intentionally omitted (stay — / 業務DB until linked).

Client / auth flags are read from sitekpi.ga4.data at call time so tests can
monkeypatch the facade (BetaAnalyticsDataClient, HAS_DATA, connection_info, …).
"""

from __future__ import annotations

from typing import Any

from sitekpi.ga4.report import (
    PERIOD_RANGE,
    _batch,
    _conversions,
    _event_filter,
    _i,
    _req,
    _totals,
    _vals,
)


def fetch_pack_overlay(
    session: dict[str, Any],
    *,
    period: str,
    event_names: list[str],
    primary_event: str | None = None,
) -> tuple[dict[str, Any] | None, str | None]:
    """
    Return partial DEMO-shaped dict (digital/events/channels) or (None, error).
    Business fields are intentionally omitted (stay demo / separate).
    """
    from sitekpi.ga4 import data as g

    info = g.connection_info(session)
    if not info or not g.HAS_DATA or not g.HAS_GOOGLE_AUTH:
        return None, None

    ranges = PERIOD_RANGE.get(period) or PERIOD_RANGE["28d"]
    cur_start, cur_end, prev_start, prev_end, label = ranges
    property_id = info["property_id"]

    try:
        creds = g.creds_from_session(session)
        if not creds:
            return None, "GA4 認証が無効です。再接続してください。"
        client = g.BetaAnalyticsDataClient(credentials=creds)

        totals_metrics = [
            "activeUsers",
            "sessions",
            "screenPageViews",
            "engagementRate",
            "newUsers",
            "screenPageViewsPerSession",
            "averageSessionDuration",
            "userEngagementDuration",
        ]
        # One round trip: totals now / before, events now / before, channels
        reqs = [
            _req(cur_start, cur_end, totals_metrics),
            _req(prev_start, prev_end, totals_metrics),
            _req(cur_start, cur_end, ["sessions"], dimensions=["sessionDefaultChannelGroup"], limit=10),
        ]
        if event_names:
            filt = _event_filter(event_names)
            lim = max(len(event_names), 10)
            reqs += [
                _req(cur_start, cur_end, ["eventCount"], ["eventName"], filt, lim),
                _req(prev_start, prev_end, ["eventCount"], ["eventName"], filt, lim),
            ]
        reports = _batch(client, property_id, reqs)
        cur, prev, ch = reports[0], reports[1], reports[2]
        cur_t = _totals(_vals(cur.rows[0]) if cur.rows else ["0"] * 8)
        prev_t = _totals(_vals(prev.rows[0]) if prev.rows else ["0"] * 8)
        uu, sessions = cur_t["uu"], cur_t["sessions"]
        uu_prev, sess_prev = prev_t["uu"], prev_t["sessions"]
        uu_delta = round(100 * (uu - uu_prev) / uu_prev, 1) if uu_prev else 0.0
        sessions_delta = (
            round(100 * (sessions - sess_prev) / sess_prev, 1) if sess_prev else 0.0
        )

        event_counts: dict[str, int] = {e: 0 for e in event_names}
        event_counts_prev: dict[str, int] = {}
        if event_names:
            for row in reports[3].rows or []:
                event_counts[row.dimension_values[0].value] = _i(_vals(row)[0])
            for row in reports[4].rows or []:
                event_counts_prev[row.dimension_values[0].value] = _i(_vals(row)[0])

        ch_rows = []
        ch_total = 0
        for row in ch.rows or []:
            name = row.dimension_values[0].value or "Other"
            n = _i(_vals(row)[0])
            ch_rows.append((name, n))
            ch_total += n
        channels: list[tuple[str, int]] = []
        if ch_total > 0:
            for name, n in ch_rows:
                channels.append((name, max(1, round(100 * n / ch_total)) if n else 0))
            # Fix rounding to ~100
            s = sum(p for _, p in channels)
            if channels and s != 100:
                name0, p0 = channels[0]
                channels[0] = (name0, max(0, p0 + (100 - s)))
        else:
            channels = [("Other", 100)]

        primary = (primary_event or "").strip() or (event_names[0] if event_names else "")
        overlay: dict[str, Any] = {
            **cur_t,
            **_conversions(event_counts, primary, uu),
            "uu_delta": uu_delta,
            "sessions_delta": sessions_delta,
            "event_counts": event_counts,
            "event_counts_prev": event_counts_prev,
            "channels": channels,
            "_ga4_label": label,
            "_ga4_property": info["property_name"],
            "_ga4_property_id": property_id,
        }
        prev_counts = {e: event_counts_prev.get(e, 0) for e in event_counts}
        overlay["_prev"] = {
            **prev_t,
            **_conversions(prev_counts, primary, uu_prev),
            "uu_delta": 0.0,
            "sessions_delta": 0.0,
            "event_counts": prev_counts,
            "channels": channels,
        } if uu_prev else None
        # Persist refreshed token if any
        if session.get("ga4_credentials"):
            # creds_from_session may have refreshed
            pass
        return overlay, None
    except Exception as exc:  # noqa: BLE001
        return None, str(exc)
