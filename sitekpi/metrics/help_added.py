"""When each glossary word was added (not shown; drives the NEW badge on 指標辞典, docs/plan s04).

Words that were there from the start have no date. Add a line here with every new batch.
"""

from __future__ import annotations

from datetime import date, timedelta

NEW_DAYS = 30  # a card shows NEW for this many days after it was added

_BATCHES: dict[str, list[str]] = {
    "2026-11-04": [
        "exit_rate", "cart_abandonment", "repeat_purchase", "refund_rate", "landing_cvr", "micro_conversion",
        "roas", "cpc", "cpm", "ctr", "cpa", "reach", "frequency", "activation", "retention", "ltv_cac",
        "payback", "nps", "assisted_conv", "utm",
    ],
    "2026-11-20": [
        "checkout_abandonment", "site_search_rate", "zero_result_rate", "lcp", "inp", "cls", "return_interval",
        "search_impressions", "search_ctr", "avg_position", "email_open_rate", "email_ctr", "unsubscribe_rate",
        "cpl", "view_through_conv", "gross_margin", "csat", "time_to_value", "cohort", "ab_test",
    ],
    "2026-11-27": [
        "brand_search", "ttfb", "impression_share", "conversion_lag", "f2_rate", "reactivation_rate", "mql",
        "gmv", "attribution", "backlinks",
    ],
}

ADDED: dict[str, date] = {k: date.fromisoformat(d) for d, keys in _BATCHES.items() for k in keys}


def recent(today: date) -> tuple[set[str], list[tuple[date, int]]]:
    """(keys still NEW today, [(batch date, how many)] newest first)."""
    since = today - timedelta(days=NEW_DAYS)
    keys = {k for k, d in ADDED.items() if since < d <= today}
    batches: dict[date, int] = {}
    for k in keys:
        batches[ADDED[k]] = batches.get(ADDED[k], 0) + 1
    return keys, sorted(batches.items(), reverse=True)
