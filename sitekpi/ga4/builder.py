"""GA4 fetches for the KPI builder palette (HELP catalog ids only).

Auth / client symbols resolve via sitekpi.ga4.data so tests can monkeypatch the facade.
"""

from __future__ import annotations

from typing import Any

from sitekpi.ga4.report import (
    PERIOD_RANGE,
    _event_filter,
    _fmt_avg_time,
    _i,
    _run,
    _vals,
)

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
    from sitekpi.ga4 import data as g
    info = g.connection_info(session)
    if not info or not g.HAS_DATA or not g.HAS_GOOGLE_AUTH:
        return [], None
    try:
        creds = g.creds_from_session(session)
        if not creds:
            return [], "GA4 認証が無効です。再接続してください。"
        client = g.BetaAnalyticsDataClient(credentials=creds)
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
    from sitekpi.ga4 import data as g
    from concurrent.futures import ThreadPoolExecutor, as_completed

    info = g.connection_info(session)
    if not info or not g.HAS_DATA or not g.HAS_GOOGLE_AUTH or not api_names:
        return {}
    ranges = PERIOD_RANGE.get(period) or PERIOD_RANGE["28d"]
    cur_start, cur_end = ranges[0], ranges[1]
    property_id = info["property_id"]
    values: dict[str, str] = {}
    try:
        creds = g.creds_from_session(session)
        if not creds:
            return {}
        client = g.BetaAnalyticsDataClient(credentials=creds)
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
    from sitekpi.ga4 import data as g
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
    info = g.connection_info(session)
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
        if not event_names or not g.HAS_DATA or not g.HAS_GOOGLE_AUTH:
            return {}, None
        ranges = PERIOD_RANGE.get(period) or PERIOD_RANGE["28d"]
        try:
            creds = g.creds_from_session(session)
            if not creds:
                return {}, "GA4 認証が無効です。再接続してください。"
            client = g.BetaAnalyticsDataClient(credentials=creds)
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
        if not g.HAS_DATA or not g.HAS_GOOGLE_AUTH:
            return {}, None
        ranges = PERIOD_RANGE.get(period) or PERIOD_RANGE["28d"]
        try:
            creds = g.creds_from_session(session)
            if not creds:
                return {}, None
            client = g.BetaAnalyticsDataClient(credentials=creds)
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
