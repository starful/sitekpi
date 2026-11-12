"""Public GA4 Data API facade.

Split internals live in report / overlay / builder / flow. Import from here so
call sites stay stable when those modules move.

Also re-exports report helpers (_req, _batch, …) and oauth flags that
board.extras and tests monkeypatch on this module.
"""

from __future__ import annotations

from sitekpi.ga4.builder import (
    build_live_builder_widgets,
    fetch_metric_catalog,
    fetch_metric_values,
)
from sitekpi.ga4.flow import fetch_flow, fetch_site_basics
from sitekpi.ga4.oauth import HAS_DATA, HAS_GOOGLE_AUTH, creds_from_session
from sitekpi.ga4.overlay import fetch_pack_overlay
from sitekpi.ga4.report import (
    PERIOD_RANGE,
    BetaAnalyticsDataClient,
    _batch,
    _conversions,
    _event_filter,
    _f,
    _fmt_avg_time,
    _i,
    _req,
    _run,
    _totals,
    _vals,
    connection_info,
    discover_event_names,
    saved_events,
)

__all__ = [
    "HAS_DATA",
    "HAS_GOOGLE_AUTH",
    "PERIOD_RANGE",
    "BetaAnalyticsDataClient",
    "build_live_builder_widgets",
    "connection_info",
    "creds_from_session",
    "discover_event_names",
    "fetch_flow",
    "fetch_metric_catalog",
    "fetch_metric_values",
    "fetch_pack_overlay",
    "fetch_site_basics",
    "saved_events",
    "_batch",
    "_conversions",
    "_event_filter",
    "_f",
    "_fmt_avg_time",
    "_i",
    "_req",
    "_run",
    "_totals",
    "_vals",
]
