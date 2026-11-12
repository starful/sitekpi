"""Required keys for industry pack DEMO / meta / 業界目安.

Used by smoke_packs (and tests) so a new pack fails early when a scalar
the board always reads is missing. Nested structures (event_counts, channels)
are checked for presence, not for a fixed event vocabulary — that varies by pack.
"""

from __future__ import annotations

# Scalars every DEMO period row must carry (board + GA4 overlay merge onto these).
DEMO_SCALAR_KEYS: frozenset[str] = frozenset(
    {
        "uu",
        "uu_delta",
        "sessions",
        "sessions_delta",
        "new_users",
        "returning_users",
        "engaged_rate",
        "avg_time",
        "pages_session",
        "pageviews",
        "signups",
        "signup_rate",
        "pay_start",
        "pay_success",
        "pay_cvr",
        "revenue",
        "revenue_delta",
        "members_db",
        "members_delta",
        "paid_members",
        "paid_delta",
        "new_paid",
        "churn",
    }
)

# Nested DEMO fields (shape differs per pack; must exist).
DEMO_NESTED_KEYS: frozenset[str] = frozenset({"event_counts", "channels"})

# meta keys after registry load (slug is injected if missing).
META_KEYS: frozenset[str] = frozenset(
    {
        "slug",
        "label",
        "hint",
        "blurb",
        "events",
        "event_categories",
        "primary_event",
        "signup_label",
        "notes",
        "category",
    }
)

# Spoken labels owned by pack_l10n (registry overlays JA from there).
SPOKEN_META_FIELDS: tuple[str, ...] = ("label", "hint", "signup_label")
SPOKEN_COPY_FIELDS: tuple[str, ...] = (
    "cvr_label",
    "mid_label",
    "bottom_label",
    "rate_a_label",
    "rate_b_label",
    "property",
)

# Every pack must define at least these 業界目安 bands (more are pack-specific).
BENCH_CORE_KEYS: frozenset[str] = frozenset(
    {
        "engaged_rate",
        "bounce_rate",
        "pages_session",
        "sessions_per_uu",
        "pages_per_uu",
        "new_pct",
    }
)
