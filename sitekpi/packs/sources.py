"""Cited 業界目安 — where a published benchmark matches a pack metric.

Only figures that were checked against the source page verbatim are listed.
Each cited value becomes the *middle* of the band, so the board's 業界目安 equals
the published figure; the band width is a SiteKPI rule and is labelled as such.
Metrics/packs not listed keep their SiteKPI 初期値 (no external source).

Checked 2026-10-22.
"""

from __future__ import annotations

from typing import Any

SOURCES: dict[str, dict[str, str]] = {
    "databox_ga4": {
        "label": "Databox — GA4 Industry Benchmarks (Aug 2023, median)",
        "url": "https://databox.com/google-analytics-4-industry-benchmarks",
    },
    "fps_b2b": {
        "label": "First Page Sage — B2B Conversion Rates by Industry (visitor-to-lead, Jan 2022–Aug 2025)",
        "url": "https://firstpagesage.com/reports/b2b-conversion-rates-by-industry/",
    },
    "dynamic_yield": {
        "label": "Dynamic Yield 2024 via Smart Insights — ecommerce conversion rate per user",
        "url": "https://www.smartinsights.com/ecommerce/ecommerce-analytics/ecommerce-conversion-rates/",
    },
    "baymard": {
        "label": "Baymard Institute — cart abandonment 70.22% (50 studies, updated Sep 2025); cart→purchase = 100 − 70.22",
        "url": "https://baymard.com/lists/cart-abandonment-rate",
    },
}

# band rules: ("pt", n) → value ± n points;  ("rel", r) → value × (1 ± r)
ENGAGE_RULE = ("pt", 7.5)
CVR_RULE = ("rel", 0.4)
CART_RULE = ("pt", 10.0)

# Databox GA4 medians (engagement rate, bounce rate), Aug 2023
_DATABOX = {
    "eCommerce & Marketplaces": (63.86, 36.14),
    "Construction": (54.92, 46.27),
    "Real Estate": (54.13, 47.83),
    "Education": (57.19, 42.4),
    "Food": (53.74, 39.38),
    "Health Care": (59.97, 43.38),
    "Health & Wellness": (62.22, 38.65),
    "SaaS": (52.43, 48.24),
    "Consulting & Professional Services": (52.43, 49.47),
    "Travel & Leisure": (61.55, 36.0),
    "All industries": (56.23, 44.82),
}
_DATABOX_SEGMENT = {
    "ec": "eCommerce & Marketplaces",
    "marketplace": "eCommerce & Marketplaces",
    "d2c": "eCommerce & Marketplaces",
    "construction": "Construction",
    "realestate": "Real Estate",
    "edu": "Education",
    "food": "Food",
    "clinic": "Health Care",
    "beauty": "Health & Wellness",
    "saas": "SaaS",
    "b2b": "Consulting & Professional Services",
    "agency": "Consulting & Professional Services",
    "travel": "Travel & Leisure",
    # no matching industry → all-industry median (labelled as such)
    "b2c": "All industries",
    "community": "All industries",
    "content": "All industries",
    "news": "All industries",
    "creator": "All industries",
    "hr": "All industries",
    "parttime": "All industries",
    "finance": "All industries",
    "gov": "All industries",
}

# First Page Sage visitor-to-lead (per unique visitor) → primary CVR (登録/問い合わせ/応募/申込 ÷ UU)
_FPS = {
    "saas": ("B2B SaaS", 1.1),
    "b2b": ("IT & Managed Services", 1.5),
    "construction": ("Construction", 1.9),
    "realestate": ("Real Estate", 2.7),
    "hr": ("Staffing & Recruiting", 2.9),
    "parttime": ("Staffing & Recruiting", 2.9),
    "agency": ("Staffing & Recruiting", 2.9),
    "edu": ("Higher Education & College", 2.8),
}

CITED: dict[str, dict[str, tuple[str, str, float, tuple[str, float]]]] = {}
for _slug, _seg in _DATABOX_SEGMENT.items():
    eng, bounce = _DATABOX[_seg]
    CITED.setdefault(_slug, {})["engaged_rate"] = ("databox_ga4", _seg, eng, ENGAGE_RULE)
    CITED[_slug]["bounce_rate"] = ("databox_ga4", _seg, bounce, ENGAGE_RULE)
for _slug, (_seg, _v) in _FPS.items():
    CITED.setdefault(_slug, {})["signup_rate"] = ("fps_b2b", _seg, _v, CVR_RULE)
for _slug in ("ec", "marketplace", "d2c"):
    CITED[_slug]["signup_rate"] = ("dynamic_yield", "All retail (overall)", 2.9, CVR_RULE)
    CITED[_slug]["signup_to_pay"] = ("baymard", "Average of 50 studies", round(100 - 70.22, 2), CART_RULE)


def _band(value: float, rule: tuple[str, float], unit: str) -> tuple[float, float]:
    kind, n = rule
    if kind == "pt":
        low, high = value - n, value + n
    else:
        low, high = value * (1 - n), value * (1 + n)
    if unit == "%":
        low, high = max(0.0, low), min(100.0, high)
    return round(low, 2), round(high, 2)


def apply_sources(slug: str, benchmarks: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Return the pack's benchmarks with cited values applied (others untouched)."""
    out = {k: dict(v) for k, v in benchmarks.items()}
    for metric, (src_id, segment, value, rule) in CITED.get(slug, {}).items():
        if metric not in out:
            continue
        spec = out[metric]
        spec["low"], spec["high"] = _band(value, rule, str(spec.get("unit", "")))
        src = SOURCES[src_id]
        spec["source"] = {
            "label": f"{src['label']} — {segment}: {value:g}{spec.get('unit', '')}",
            "url": src["url"],
            "rule": f"{rule[0]}:{rule[1]:g}",
        }
    return out
