"""GA4 Data API report primitives (period ranges, run/batch, parsers).

Internal helpers shared by overlay / builder / flow fetches.
Callers import public names from sitekpi.ga4.data (stable facade) — do not
import this module from routes/views unless you are extending the GA4 layer.

PERIOD_RANGE tuples: (cur_start, cur_end, prev_start, prev_end, JA label).
_batch chunks at 5 (GA4 batch_run_reports limit). Business KPIs are never
fetched here — overlay omits them so /live shows — until 業務DB is linked.
"""

from __future__ import annotations

from typing import Any

try:
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import (
        BatchRunReportsRequest,
        DateRange,
        Dimension,
        Filter,
        FilterExpression,
        Metric,
        RunReportRequest,
    )
except ImportError:  # pragma: no cover
    BetaAnalyticsDataClient = None  # type: ignore[misc, assignment]

PERIOD_RANGE = {
    "7d": ("7daysAgo", "yesterday", "14daysAgo", "8daysAgo", "直近7日"),
    "28d": ("28daysAgo", "yesterday", "56daysAgo", "29daysAgo", "直近28日"),
}


def saved_events(session: dict[str, Any]) -> dict[str, Any] | None:
    """User-selected events: {{events: [...], primary: str}}."""
    cfg = session.get("ga4_selected_events")
    if not isinstance(cfg, dict):
        return None
    events = [str(e).strip() for e in (cfg.get("events") or []) if str(e).strip()]
    if not events:
        return None
    primary = str(cfg.get("primary") or events[0]).strip()
    if primary not in events:
        primary = events[0]
    return {"events": events, "primary": primary}


def discover_event_names(
    session: dict[str, Any],
    *,
    period: str = "28d",
    limit: int = 200,
) -> tuple[list[dict[str, Any]], str | None]:
    """Return [{name, count}, ...] from GA4 for the connected property."""
    from sitekpi.ga4 import data as g

    info = g.connection_info(session)
    if not info or not g.HAS_DATA or not g.HAS_GOOGLE_AUTH:
        return [], None
    ranges = PERIOD_RANGE.get(period) or PERIOD_RANGE["28d"]
    cur_start, cur_end = ranges[0], ranges[1]
    property_id = info["property_id"]
    try:
        creds = g.creds_from_session(session)
        if not creds:
            return [], "GA4 認証が無効です。再接続してください。"
        client = g.BetaAnalyticsDataClient(credentials=creds)
        resp = _run(
            client,
            property_id,
            cur_start,
            cur_end,
            ["eventCount"],
            dimensions=["eventName"],
            limit=limit,
        )
        out: list[dict[str, Any]] = []
        for row in resp.rows or []:
            name = row.dimension_values[0].value
            if not name:
                continue
            out.append({"name": name, "count": _i(_vals(row)[0])})
        return out, None
    except Exception as exc:  # noqa: BLE001
        return [], str(exc)


def connection_info(session: dict[str, Any]) -> dict[str, Any] | None:
    if session.get("ga4_demo"):
        return None
    prop = session.get("ga4_property")
    if not prop or not session.get("ga4_credentials"):
        return None
    return {
        "property_id": str(prop.get("id", "")),
        "property_name": str(prop.get("name", "")),
        "account": str(prop.get("account", "")),
        "email": str(session.get("ga4_email") or ""),
    }


def _vals(row: Any) -> list[str]:
    return [m.value for m in row.metric_values]


def _f(v: str | None, default: float = 0.0) -> float:
    try:
        return float(v) if v is not None else default
    except ValueError:
        return default


def _i(v: str | None, default: int = 0) -> int:
    try:
        return int(float(v)) if v is not None else default
    except ValueError:
        return default


def _fmt_avg_time(seconds: float) -> str:
    if seconds < 0:
        seconds = 0
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m}:{s:02d}"


def _run(
    client: Any,
    property_id: str,
    start: str,
    end: str,
    metrics: list[str],
    dimensions: list[str] | None = None,
    dimension_filter: Any | None = None,
    limit: int | None = None,
) -> Any:
    req = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=start, end_date=end)],
        metrics=[Metric(name=m) for m in metrics],
        dimensions=[Dimension(name=d) for d in (dimensions or [])],
    )
    if dimension_filter is not None:
        req.dimension_filter = dimension_filter
    if limit is not None:
        req.limit = limit
    return client.run_report(req)


def _req(
    start: str,
    end: str,
    metrics: list[str],
    dimensions: list[str] | None = None,
    dimension_filter: Any | None = None,
    limit: int | None = None,
) -> Any:
    req = RunReportRequest(
        date_ranges=[DateRange(start_date=start, end_date=end)],
        metrics=[Metric(name=m) for m in metrics],
        dimensions=[Dimension(name=d) for d in (dimensions or [])],
    )
    if dimension_filter is not None:
        req.dimension_filter = dimension_filter
    if limit is not None:
        req.limit = limit
    return req


def _batch(client: Any, property_id: str, reqs: list[Any]) -> list[Any]:
    """Several reports in one round trip (GA4 allows 5 per batch)."""
    out: list[Any] = []
    for i in range(0, len(reqs), 5):
        resp = client.batch_run_reports(
            BatchRunReportsRequest(property=f"properties/{property_id}", requests=reqs[i:i + 5])
        )
        out.extend(resp.reports)
    return out


def _event_filter(names: list[str]) -> Any:
    return FilterExpression(
        filter=Filter(field_name="eventName", in_list_filter=Filter.InListFilter(values=list(names)))
    )


def _totals(cv: list[str]) -> dict[str, Any]:
    """Site totals from the 8 totals metrics (same order as the request)."""
    uu = _i(cv[0])
    new_users = _i(cv[4])
    eng_total = _f(cv[7])
    return {
        "uu": uu,
        "sessions": _i(cv[1]),
        "pageviews": _i(cv[2]),
        "engaged_rate": round(_f(cv[3]) * 100, 1),
        "new_users": new_users,
        "returning_users": max(uu - new_users, 0),
        "pages_session": round(_f(cv[5]), 1),
        # userEngagementDuration is total seconds; per-user average if possible
        "avg_time": _fmt_avg_time(eng_total / uu if uu else _f(cv[6])),
    }


def _conversions(event_counts: dict[str, int], primary: str, uu: int) -> dict[str, Any]:
    """Map pack / user events to signup / pay fields."""
    signups = event_counts.get(primary, 0) if primary else 0
    if not signups:
        for key in ("sign_up", "newsletter_signup", "purchase", "generate_lead"):
            if event_counts.get(key):
                signups = event_counts[key]
                break
    pay_start = event_counts.get("pay_start", 0) or event_counts.get("begin_checkout", 0)
    pay_success = event_counts.get("pay_success", 0) or event_counts.get("purchase", 0)
    return {
        "signups": signups,
        "signup_rate": round(100 * signups / uu, 1) if uu else 0.0,
        "pay_start": pay_start,
        "pay_success": pay_success,
        "pay_cvr": round(100 * pay_success / pay_start, 1) if pay_start else 0.0,
    }
