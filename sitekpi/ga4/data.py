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
        BatchRunReportsRequest,
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
    batch_size: int = 10,
) -> dict[str, str]:
    """Fetch display values for metric api names (batched in parallel; failures → —)."""
    from concurrent.futures import ThreadPoolExecutor, as_completed

    info = connection_info(session)
    if not info or not HAS_DATA or not HAS_GOOGLE_AUTH or not api_names:
        return {}
    ranges = PERIOD_RANGE.get(period) or PERIOD_RANGE["28d"]
    cur_start, cur_end = ranges[0], ranges[1]
    property_id = info["property_id"]
    values: dict[str, str] = {}
    try:
        creds = creds_from_session(session)
        if not creds:
            return {}
        client = BetaAnalyticsDataClient(credentials=creds)
    except Exception:  # noqa: BLE001
        return {}

    names = [n for n in api_names if n]
    chunks = [names[i : i + batch_size] for i in range(0, len(names), batch_size)]

    def _one_chunk(chunk: list[str]) -> dict[str, str]:
        out: dict[str, str] = {}
        try:
            resp = _run(client, property_id, cur_start, cur_end, chunk)
            if not resp.rows:
                return {n: "—" for n in chunk}
            raws = _vals(resp.rows[0])
            for j, n in enumerate(chunk):
                out[n] = raws[j] if j < len(raws) else "—"
            return out
        except Exception:  # noqa: BLE001
            # Incompatible metric mix — split once, not one-by-one
            if len(chunk) == 1:
                return {chunk[0]: "—"}
            mid = max(1, len(chunk) // 2)
            out.update(_one_chunk(chunk[:mid]))
            out.update(_one_chunk(chunk[mid:]))
            return out

    workers = min(4, max(1, len(chunks)))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futs = [pool.submit(_one_chunk, c) for c in chunks]
        for fut in as_completed(futs):
            values.update(fut.result())
    return values

def build_live_builder_widgets(
    session: dict[str, Any],
    *,
    period: str = "28d",
    cache: Any = None,
    locale: str = "ja",
) -> tuple[list[dict[str, Any]], str, str | None]:
    """
    Build palette from HELP catalog only (same ids as 指標辞典).
    Fetches GA4 values for mapped metrics / known events / channels — no full catalog crawl.
    Returns (widgets, property_name, error).
    """
    from concurrent.futures import ThreadPoolExecutor

    from sitekpi.i18n import normalize_locale
    from sitekpi.metrics.help import (
        CHANNEL_IDS,
        HELP,
        ga4_apis_for_palette,
        ga4_events_for_palette,
        palette_widgets,
    )

    loc = normalize_locale(locale)
    info = connection_info(session)
    if not info:
        return [], "", None

    prop_name = info["property_name"]
    cache_key = f"builder|help|{info.get('property_id')}|{period}|{loc}"
    if cache is not None:
        hit = cache.get(cache_key)
        if hit is not None:
            widgets, err = hit
            return widgets, prop_name, err

    errors: list[str] = []
    apis = ga4_apis_for_palette()
    event_names = ga4_events_for_palette()

    def _fetch_events() -> tuple[dict[str, int], str | None]:
        if not event_names or not HAS_DATA or not HAS_GOOGLE_AUTH:
            return {}, None
        ranges = PERIOD_RANGE.get(period) or PERIOD_RANGE["28d"]
        try:
            creds = creds_from_session(session)
            if not creds:
                return {}, "GA4 認証が無効です。再接続してください。"
            client = BetaAnalyticsDataClient(credentials=creds)
            resp = _run(
                client,
                info["property_id"],
                ranges[0],
                ranges[1],
                ["eventCount"],
                dimensions=["eventName"],
                dimension_filter=_event_filter(event_names),
                limit=len(event_names) + 5,
            )
            out: dict[str, int] = {e: 0 for e in event_names}
            for row in resp.rows or []:
                name = row.dimension_values[0].value
                if name in out:
                    out[name] = _i(_vals(row)[0])
            return out, None
        except Exception as exc:  # noqa: BLE001
            return {}, str(exc)

    def _fetch_channels() -> tuple[dict[str, tuple[str, int]], str | None]:
        """HELP channel id → (pct display, sessions)."""
        if not HAS_DATA or not HAS_GOOGLE_AUTH:
            return {}, None
        ranges = PERIOD_RANGE.get(period) or PERIOD_RANGE["28d"]
        try:
            creds = creds_from_session(session)
            if not creds:
                return {}, None
            client = BetaAnalyticsDataClient(credentials=creds)
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
            out: dict[str, tuple[str, int]] = {}
            for nm, n in rows:
                hid = CHANNEL_IDS.get(nm)
                if not hid:
                    continue
                pct = round(100 * n / total) if total else 0
                out[hid] = (f"{pct}%", n)
            return out, None
        except Exception as exc:  # noqa: BLE001
            return {}, str(exc)

    with ThreadPoolExecutor(max_workers=3) as pool:
        fut_v = pool.submit(fetch_metric_values, session, apis, period=period)
        fut_e = pool.submit(_fetch_events)
        fut_c = pool.submit(_fetch_channels)
        raw_vals = fut_v.result()
        event_counts, e_err = fut_e.result()
        channel_vals, c_err = fut_c.result()
    if e_err:
        errors.append(e_err)
    if c_err:
        errors.append(c_err)

    # Format helpers: fetch_metric_values already returns display strings
    widgets: list[dict[str, Any]] = []
    for w in palette_widgets(sample=False, locale=loc):
        wid = w["id"]
        h = HELP.get(wid) or {}
        group = w["group"]
        if group == "business":
            widgets.append({**w, "value": "—", "hint": "未連携 · 業務DB"})
            continue
        if group == "digital":
            api = h.get("ga4_api")
            if api and api in raw_vals and raw_vals[api] not in ("", None, "—"):
                display = _fmt_metric_value(raw_vals[api], "", api_name=str(api))
                widgets.append({**w, "value": display, "hint": f"{api} · GA4"})
            elif api:
                widgets.append({**w, "value": "—", "hint": f"{api} · 未取得"})
            else:
                widgets.append({**w, "value": "—", "hint": w.get("hint") or ""})
            continue
        if group == "event":
            ev = h.get("ga4_event")
            if ev and ev in event_counts:
                widgets.append(
                    {
                        **w,
                        "value": f"{event_counts[ev]:,}",
                        "hint": f"{ev} · GA4",
                    }
                )
            else:
                widgets.append({**w, "value": "—", "hint": f"{ev or wid} · 未計測"})
            continue
        if group == "traffic":
            if wid in channel_vals:
                pct, n = channel_vals[wid]
                widgets.append({**w, "value": pct, "hint": f"sessions {n:,} · GA4"})
            else:
                widgets.append({**w, "value": "—", "hint": "GA4未取得"})
            continue
        widgets.append(w)

    err = " / ".join(errors) if errors else None
    if cache is not None:
        cache.set(cache_key, (widgets, err))
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
    info = connection_info(session)
    if not info or not HAS_DATA or not HAS_GOOGLE_AUTH:
        return None
    ranges = PERIOD_RANGE.get(period) or PERIOD_RANGE["28d"]
    try:
        creds = creds_from_session(session)
        if not creds:
            return None
        client = BetaAnalyticsDataClient(credentials=creds)
        r = _run(client, info["property_id"], ranges[0], ranges[1], ["activeUsers", "engagementRate", "sessions"])
        if not r.rows:
            return None
        v = _vals(r.rows[0])
        return {"uu": _i(v[0]), "engaged_rate": round(_f(v[1]) * 100, 1), "sessions": _i(v[2])}
    except Exception:  # noqa: BLE001
        return None
