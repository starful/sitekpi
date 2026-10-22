"""Fetch GA4 pack metrics for industry pages / builder (session OAuth)."""

from __future__ import annotations

from typing import Any

from sitekpi.ga4.oauth import (
    HAS_DATA,
    HAS_GOOGLE_AUTH,
    creds_from_session,
)

try:
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import (
        DateRange,
        Dimension,
        Filter,
        FilterExpression,
        FilterExpressionList,
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
    info = connection_info(session)
    if not info or not HAS_DATA or not HAS_GOOGLE_AUTH:
        return [], None
    ranges = PERIOD_RANGE.get(period) or PERIOD_RANGE["28d"]
    cur_start, cur_end = ranges[0], ranges[1]
    property_id = info["property_id"]
    try:
        creds = creds_from_session(session)
        if not creds:
            return [], "GA4 認証が無効です。再接続してください。"
        client = BetaAnalyticsDataClient(credentials=creds)
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
    info = connection_info(session)
    if not info or not HAS_DATA or not HAS_GOOGLE_AUTH:
        return None, None

    ranges = PERIOD_RANGE.get(period) or PERIOD_RANGE["28d"]
    cur_start, cur_end, prev_start, prev_end, label = ranges
    property_id = info["property_id"]

    try:
        creds = creds_from_session(session)
        if not creds:
            return None, "GA4 認証が無効です。再接続してください。"
        client = BetaAnalyticsDataClient(credentials=creds)

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
        cur = _run(client, property_id, cur_start, cur_end, totals_metrics)
        prev = _run(client, property_id, prev_start, prev_end, totals_metrics)
        cur_t = _totals(_vals(cur.rows[0]) if cur.rows else ["0"] * 8)
        prev_t = _totals(_vals(prev.rows[0]) if prev.rows else ["0"] * 8)
        uu, sessions = cur_t["uu"], cur_t["sessions"]
        uu_prev, sess_prev = prev_t["uu"], prev_t["sessions"]
        uu_delta = round(100 * (uu - uu_prev) / uu_prev, 1) if uu_prev else 0.0
        sessions_delta = (
            round(100 * (sessions - sess_prev) / sess_prev, 1) if sess_prev else 0.0
        )

        # Events
        event_counts: dict[str, int] = {e: 0 for e in event_names}
        event_counts_prev: dict[str, int] = {}
        if event_names:
            filt = FilterExpression(
                or_group=FilterExpressionList(
                    expressions=[
                        FilterExpression(
                            filter=Filter(
                                field_name="eventName",
                                string_filter=Filter.StringFilter(
                                    value=name,
                                    match_type=Filter.StringFilter.MatchType.EXACT,
                                ),
                            )
                        )
                        for name in event_names
                    ]
                )
            )
            ev = _run(
                client,
                property_id,
                cur_start,
                cur_end,
                ["eventCount"],
                dimensions=["eventName"],
                dimension_filter=filt,
                limit=max(len(event_names), 10),
            )
            for row in ev.rows or []:
                name = row.dimension_values[0].value
                event_counts[name] = _i(_vals(row)[0])
            # Same events, previous period → real 前期比 per event
            ev_prev = _run(
                client,
                property_id,
                prev_start,
                prev_end,
                ["eventCount"],
                dimensions=["eventName"],
                dimension_filter=filt,
                limit=max(len(event_names), 10),
            )
            for row in ev_prev.rows or []:
                event_counts_prev[row.dimension_values[0].value] = _i(_vals(row)[0])

        # Channels (top by sessions)
        ch = _run(
            client,
            property_id,
            cur_start,
            cur_end,
            ["sessions"],
            dimensions=["sessionDefaultChannelGroup"],
            limit=10,
        )
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


def _channel_widget_id(name: str) -> str:
    safe = "".join(c if c.isalnum() else "_" for c in name).strip("_").lower()
    return f"ch_{safe or 'other'}"


def _fmt_metric_value(raw: str, metric_type: str, api_name: str = "") -> str:
    t = (metric_type or "").upper()
    api = api_name or ""
    try:
        n = float(raw) if raw not in (None, "") else 0.0
    except ValueError:
        return str(raw or "—")
    if "SECOND" in t:
        if n >= 3600:
            return f"{n / 3600:.1f} h"
        if n >= 120:
            return f"{int(n // 60)} 分"
        return _fmt_avg_time(n)
    if "PERCENT" in t or api.endswith("Rate") or api.endswith("rate"):
        pct = n * 100 if 0 <= n <= 1 else n
        return f"{round(pct, 1)}%"
    if "CURRENCY" in t:
        return f"{n:,.0f}" if abs(n - round(n)) < 1e-9 else f"{n:,.2f}"
    if abs(n - round(n)) < 1e-9:
        return f"{int(round(n)):,}"
    return f"{n:,.2f}"


def fetch_metric_catalog(
    session: dict[str, Any],
) -> tuple[list[dict[str, Any]], str | None]:
    """Return GA4 metrics metadata: [{api_name, ui_name, category, type}, ...]."""
    info = connection_info(session)
    if not info or not HAS_DATA or not HAS_GOOGLE_AUTH:
        return [], None
    try:
        creds = creds_from_session(session)
        if not creds:
            return [], "GA4 認証が無効です。再接続してください。"
        client = BetaAnalyticsDataClient(credentials=creds)
        meta = client.get_metadata(name=f"properties/{info['property_id']}/metadata")
        out: list[dict[str, Any]] = []
        for m in meta.metrics or []:
            api = str(m.api_name or "").strip()
            if not api:
                continue
            t = getattr(m, "type_", None)
            type_str = t.name if hasattr(t, "name") else str(t or "")
            out.append(
                {
                    "api_name": api,
                    "ui_name": str(m.ui_name or api),
                    "category": str(m.category or "Other"),
                    "type": type_str,
                    "custom": bool(getattr(m, "custom_definition", False)),
                }
            )
        # Stable sort: custom last, then category, then ui name
        out.sort(key=lambda x: (x["custom"], x["category"], x["ui_name"].lower()))
        return out, None
    except Exception as exc:  # noqa: BLE001
        return [], str(exc)


def fetch_metric_values(
    session: dict[str, Any],
    api_names: list[str],
    *,
    period: str = "28d",
    batch_size: int = 8,
) -> dict[str, str]:
    """Fetch display values for metric api names (batched; failures → skipped)."""
    info = connection_info(session)
    if not info or not HAS_DATA or not HAS_GOOGLE_AUTH or not api_names:
        return {}
    ranges = PERIOD_RANGE.get(period) or PERIOD_RANGE["28d"]
    cur_start, cur_end = ranges[0], ranges[1]
    property_id = info["property_id"]
    # Build type map from a lightweight re-fetch is expensive; callers pass via catalog
    values: dict[str, str] = {}
    try:
        creds = creds_from_session(session)
        if not creds:
            return {}
        client = BetaAnalyticsDataClient(credentials=creds)
    except Exception:  # noqa: BLE001
        return {}

    names = [n for n in api_names if n]
    i = 0
    while i < len(names):
        chunk = names[i : i + batch_size]
        i += batch_size
        try:
            resp = _run(client, property_id, cur_start, cur_end, chunk)
            if not resp.rows:
                for n in chunk:
                    values.setdefault(n, "—")
                continue
            raws = _vals(resp.rows[0])
            for j, n in enumerate(chunk):
                values[n] = raws[j] if j < len(raws) else "—"
        except Exception:  # noqa: BLE001
            # Incompatible set — try one-by-one
            for n in chunk:
                if n in values:
                    continue
                try:
                    resp = _run(client, property_id, cur_start, cur_end, [n])
                    if resp.rows:
                        values[n] = _vals(resp.rows[0])[0]
                    else:
                        values[n] = "—"
                except Exception:  # noqa: BLE001
                    values[n] = "—"
    return values


def build_live_builder_widgets(
    session: dict[str, Any],
    *,
    period: str = "28d",
) -> tuple[list[dict[str, Any]], str, str | None]:
    """
    Build palette widgets from connected GA4: all metrics + all events + channels.
    Business sample widgets kept with — values.
    Returns (widgets, property_name, error).
    """
    from sitekpi.views.builder import WIDGETS  # local import avoids cycle at module load

    info = connection_info(session)
    if not info:
        return [], "", None

    prop_name = info["property_name"]
    errors: list[str] = []

    metrics, m_err = fetch_metric_catalog(session)
    if m_err:
        errors.append(m_err)
    events, e_err = discover_event_names(session, period=period, limit=200)
    if e_err:
        errors.append(e_err)

    # Prefetch metric raw values (cap to keep first load reasonable)
    # Prefer custom + common engagement metrics first
    priority = {
        "activeUsers",
        "sessions",
        "screenPageViews",
        "engagementRate",
        "bounceRate",
        "averageSessionDuration",
        "userEngagementDuration",
        "newUsers",
        "sessionsPerUser",
        "screenPageViewsPerSession",
        "eventCount",
        "conversions",
        "totalRevenue",
        "purchaseRevenue",
    }
    ordered = sorted(
        metrics,
        key=lambda m: (0 if m["api_name"] in priority else 1, m["category"], m["ui_name"]),
    )
    # Fetch values for up to 64 metrics; rest show —
    to_fetch = [m["api_name"] for m in ordered[:64]]
    raw_vals = fetch_metric_values(session, to_fetch, period=period) if to_fetch else {}
    type_map = {m["api_name"]: m["type"] for m in metrics}

    widgets: list[dict[str, Any]] = []

    # Business: keep sample definitions, blank values (not in GA4)
    for w in WIDGETS:
        if w.get("group") == "business":
            widgets.append(
                {
                    **w,
                    "value": "—",
                    "hint": "未連携 · 業務DB（サンプル項目）",
                }
            )

    # Digital: full metric catalog
    for m in ordered:
        api = m["api_name"]
        raw = raw_vals.get(api)
        if raw is None:
            display = "—"
            hint = f"{m['category']} · {api}"
        else:
            display = _fmt_metric_value(raw, type_map.get(api, ""), api_name=api)
            hint = f"{m['category']} · {api} · GA4"
        prefix = "★ " if m["custom"] else ""
        widgets.append(
            {
                "id": f"m_{api}",
                "group": "digital",
                "label": f"{prefix}{m['ui_name']}",
                "value": display,
                "hint": hint,
            }
        )

    # Events: all discovered
    for ev in events:
        name = ev["name"]
        widgets.append(
            {
                "id": f"ev_{name}",
                "group": "event",
                "label": name,
                "value": f"{int(ev.get('count') or 0):,}",
                "hint": "eventCount · GA4",
            }
        )

    # Traffic channels from a light overlay-style report
    channel_widgets: list[dict[str, Any]] = []
    try:
        creds = creds_from_session(session)
        if creds and HAS_DATA:
            client = BetaAnalyticsDataClient(credentials=creds)
            ranges = PERIOD_RANGE.get(period) or PERIOD_RANGE["28d"]
            ch = _run(
                client,
                info["property_id"],
                ranges[0],
                ranges[1],
                ["sessions"],
                dimensions=["sessionDefaultChannelGroup"],
                limit=20,
            )
            rows: list[tuple[str, int]] = []
            total = 0
            for row in ch.rows or []:
                nm = row.dimension_values[0].value or "Other"
                n = _i(_vals(row)[0])
                rows.append((nm, n))
                total += n
            for nm, n in rows:
                pct = round(100 * n / total) if total else 0
                channel_widgets.append(
                    {
                        "id": _channel_widget_id(nm),
                        "group": "traffic",
                        "label": nm,
                        "value": f"{pct}%",
                        "hint": f"sessions {n:,} · GA4",
                    }
                )
    except Exception as exc:  # noqa: BLE001
        errors.append(str(exc))

    if not channel_widgets:
        for w in WIDGETS:
            if w.get("group") == "traffic":
                channel_widgets.append({**w, "value": "—", "hint": "GA4未取得"})
    widgets.extend(channel_widgets)

    err = " / ".join(errors) if errors else None
    return widgets, prop_name, err


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
    info = connection_info(session)
    if not info or not HAS_DATA or not HAS_GOOGLE_AUTH:
        return None, None
    ranges = PERIOD_RANGE.get(period) or PERIOD_RANGE["28d"]
    start, end = ranges[0], ranges[1]
    pid = info["property_id"]
    try:
        creds = creds_from_session(session)
        if not creds:
            return None, "GA4 認証が無効です。再接続してください。"
        client = BetaAnalyticsDataClient(credentials=creds)
        ch_dim = "sessionDefaultChannelGroup"
        total = _run(client, pid, start, end, ["totalUsers"])
        entry = _i(_vals(total.rows[0])[0]) if total.rows else 0
        by_ch_entry = _run(client, pid, start, end, ["totalUsers"], dimensions=[ch_dim], limit=25)
        entry_by = {(r.dimension_values[0].value or "Other"): _i(_vals(r)[0]) for r in by_ch_entry.rows or []}
        totals: dict[str, int] = {e: 0 for e in events}
        by_channel: dict[str, dict[str, int]] = {c: {} for c in entry_by}
        if events:
            filt = FilterExpression(
                filter=Filter(field_name="eventName", in_list_filter=Filter.InListFilter(values=list(events)))
            )
            ev = _run(client, pid, start, end, ["totalUsers"], dimensions=["eventName"],
                      dimension_filter=filt, limit=len(events) + 5)
            for r in ev.rows or []:
                totals[r.dimension_values[0].value] = _i(_vals(r)[0])
            ev_ch = _run(client, pid, start, end, ["totalUsers"], dimensions=[ch_dim, "eventName"],
                         dimension_filter=filt, limit=500)
            for r in ev_ch.rows or []:
                ch = r.dimension_values[0].value or "Other"
                by_channel.setdefault(ch, {})[r.dimension_values[1].value] = _i(_vals(r)[0])
        return {"entry": entry, "entry_by": entry_by, "totals": totals, "by_channel": by_channel, "sample": False}, None
    except Exception as exc:  # noqa: BLE001
        return None, str(exc)
