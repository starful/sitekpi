"""Cited 業界目安 — where a published benchmark matches a pack metric.

Only figures that were checked against the source page verbatim are listed.
Each cited value becomes the *middle* of the band, so the board's 業界目安 equals
the published figure; the band width is a SiteKPI rule and is labelled as such.
Metrics/packs not listed keep their SiteKPI 初期値 (no external source).

Checked 2026-10-22; First Page Sage Financial/Manufacturing/Legal/HVAC and Dynamic Yield
Food & Beverage / Home & Furniture added 2026-10-23. Databox removed 2026-11-22 (terms).
"""

from __future__ import annotations

from typing import Any

# "checked" (YYYY-MM-DD) is shown next to 出典 on the board. When you re-check a page,
# update its date here (and the figures, if they changed).
SOURCES: dict[str, dict[str, str]] = {
    "fps_b2b": {
        "label": "First Page Sage — B2B Conversion Rates by Industry (visitor-to-lead, Jan 2022–Aug 2025)",
        "url": "https://firstpagesage.com/reports/b2b-conversion-rates-by-industry/",
        "checked": "2026-10-23",  # last time the figures were compared with the page
    },
    "dynamic_yield": {
        "label": "Dynamic Yield 2024 via Smart Insights — ecommerce conversion rate per user",
        "url": "https://www.smartinsights.com/ecommerce/ecommerce-analytics/ecommerce-conversion-rates/",
        "checked": "2026-10-23",  # last time the figures were compared with the page
    },
    "baymard": {
        "label": "Baymard Institute — cart abandonment 70.22% (50 studies, updated Sep 2025); cart→purchase = 100 − 70.22",
        "url": "https://baymard.com/lists/cart-abandonment-rate",
        "checked": "2026-10-22",  # last time the figures were compared with the page
    },
}

# band rules: ("pt", n) → value ± n points;  ("rel", r) → value × (1 ± r)
ENGAGE_RULE = ("pt", 7.5)
CVR_RULE = ("rel", 0.4)
CART_RULE = ("pt", 10.0)

# Databox GA4 benchmarks (engagement · bounce) were removed on 2026-11-22: their terms of service
# prohibit using the site's content (docs/launch/benchmark-sources-terms.md). engaged_rate and
# bounce_rate show 基準なし until a source with clear reuse terms is found.

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
    "finance": ("Financial Services", 1.9),
    "manufacturing": ("Manufacturing", 2.2),
    "it_services": ("IT & Managed Services", 1.5),
    "legal": ("Legal Services", 7.4),
    "home_service": ("HVAC Services", 3.1),
}

CITED: dict[str, dict[str, tuple[str, str, float, tuple[str, float]]]] = {}
for _slug, (_seg, _v) in _FPS.items():
    CITED.setdefault(_slug, {})["signup_rate"] = ("fps_b2b", _seg, _v, CVR_RULE)
# Dynamic Yield purchase CVR per user: industry figure where the article states one in text
_DY = {"food_ec": ("Food & Beverage", 4.9), "furniture_ec": ("Home & Furniture", 1.4)}
for _slug in ("ec", "marketplace", "d2c", "apparel", "food_ec", "furniture_ec"):
    _seg, _v = _DY.get(_slug, ("All retail (overall)", 2.9))
    CITED.setdefault(_slug, {})["signup_rate"] = ("dynamic_yield", _seg, _v, CVR_RULE)
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
            "checked": src.get("checked", ""),
        }
    return out
