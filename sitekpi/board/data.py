"""Build dense site-KPI board payloads from industry DEMO / BENCHMARKS / copy."""

from __future__ import annotations

from typing import Any

from sitekpi.i18n import normalize_locale
from sitekpi.i18n.metric_l10n import (
    board_tmpl,
    help_dict,
    shared_help,
    shared_label,
    tmpl,
)
from sitekpi.i18n.pack_l10n import pack_biz_rows, pack_notes, pack_text
from sitekpi.packs import PACK_COPY

CHANNEL_COLORS: dict[str, str] = {
    "Organic Search": "#2f6fed",
    "Direct": "#64748b",
    "Paid Search": "#0ea5e9",
    "Paid Social": "#8b5cf6",
    "Organic Social": "#14b8a6",
    "Referral": "#f59e0b",
    "Email": "#ef4444",
    "Display": "#a855f7",
    "Affiliates": "#84cc16",
    "Other": "#94a3b8",
    "Social": "#14b8a6",
}


def _help(title: str, *, kind: str, meaning: str, formula: str, tip: str) -> dict[str, str]:
    return help_dict(title, kind=kind, meaning=meaning, formula=formula, tip=tip)


def _fmt_int(n: int | float) -> str:
    return f"{int(round(n)):,}"


def _fmt_pct(n: float, digits: int = 1) -> str:
    return f"{n:.{digits}f}%"


def _fmt_delta_pct(v: float) -> tuple[str, str]:
    sign = "+" if v > 0 else ""
    tone = "up" if v >= 0 else "down"
    return f"{sign}{v:.1f}%", tone


def _mmss_to_seconds(raw: Any) -> float | None:
    """Parse 'm:ss' / 'h:mm:ss' demo strings into seconds for charts."""
    if raw is None or raw in ("", "—", "–"):
        return None
    if isinstance(raw, (int, float)):
        return float(raw)
    parts = str(raw).strip().split(":")
    try:
        nums = [int(p) for p in parts]
    except ValueError:
        return None
    if len(nums) == 2:
        return float(nums[0] * 60 + nums[1])
    if len(nums) == 3:
        return float(nums[0] * 3600 + nums[1] * 60 + nums[2])
    return None


def _benches_for_sample(raw: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for key, spec in raw.items():
        unit = str(spec.get("unit", ""))
        out[key] = {
            "low": float(spec["low"]),
            "high": float(spec["high"]),
            "unit": unit,
            "hib": bool(spec["higher_is_better"]),
            "gap_unit": "pt" if unit == "%" else unit,
            # 自社目安 (user override) vs pack default, and where the default came from
            "custom": bool(spec.get("custom")),
            "source": spec.get("source") or {"kind": "provisional", "label": "", "url": ""},
        }
    return out


# GA4 automatically collected / enhanced-measurement events (listed after the
# pack's and the site's own events).
GA4_AUTO_EVENTS = frozenset(
    {
        "page_view", "session_start", "first_visit", "user_engagement", "scroll",
        "click", "view_search_results", "file_download", "form_start", "form_submit",
        "video_start", "video_progress", "video_complete", "first_open", "screen_view",
        "app_remove", "app_update", "os_update", "notification_receive",
        "notification_open", "notification_dismiss",
    }
)


def build_dense_board(
    *,
    industry: str,
    period: str,
    ind: dict[str, Any],
    data: dict[str, Any],
    benches_raw: dict[str, dict[str, Any]],
    locale: str = "ja",
) -> dict[str, Any]:
    """Return all lists + meta for render_sample_dense."""
    loc = normalize_locale(locale)
    copy = PACK_COPY.get(industry) or PACK_COPY["b2c"]
    benches = _benches_for_sample(benches_raw)
    primary = str(ind.get("primary_event") or "")
    signup_label = pack_text(
        industry, "signup_label", loc, str(ind.get("signup_label") or primary)
    )
    cvr_label = pack_text(industry, "cvr_label", loc, str(copy["cvr_label"]))
    mid_label = pack_text(industry, "mid_label", loc, str(copy["mid_label"]))
    bottom_label = pack_text(industry, "bottom_label", loc, str(copy["bottom_label"]))
    rate_a_label = pack_text(industry, "rate_a_label", loc, str(copy["rate_a_label"]))
    rate_b_label = pack_text(industry, "rate_b_label", loc, str(copy["rate_b_label"]))
    industry_label = pack_text(industry, "label", loc, str(ind["label"]))
    property_name = pack_text(industry, "property", loc, str(copy["property"]))

    focus_ids = set(copy.get("focus_ids") or [])
    events_order: list[str] = list(ind.get("events") or [])
    counts: dict[str, int] = {
        str(k): int(v) for k, v in (data.get("event_counts") or {}).items()
    }
    cat_of: dict[str, str] = {}
    for block in ind.get("event_categories") or []:
        label = str(block.get("label") or "")
        for ev in block.get("events") or []:
            cat_of[str(ev)] = label

    uu = int(data["uu"])
    sessions = int(data["sessions"])
    signups = int(data["signups"])
    signup_rate = float(data["signup_rate"])
    engaged = float(data["engaged_rate"])
    pages_session = float(data["pages_session"])
    pageviews = int(data["pageviews"])
    new_users = int(data["new_users"])
    pay_start = int(data["pay_start"])
    pay_success = int(data["pay_success"])
    pay_cvr = float(data["pay_cvr"])

    mid_event = str(copy["mid_event"])
    bottom_event = str(copy["bottom_event"])
    mid_count = int(counts.get(mid_event, pay_start))
    bottom_count = int(counts.get(bottom_event, pay_success))
    primary_count = int(counts.get(primary, signups))

    rate_a = (bottom_count / primary_count * 100) if primary_count else 0.0
    rate_b = (primary_count / mid_count * 100) if mid_count else pay_cvr
    # content: mid is click_cta; start→complete uses pay fields differently
    if industry in ("content", "news", "creator") and mid_count:
        rate_b = primary_count / mid_count * 100 if mid_count else 0.0
    if industry in ("b2c", "saas", "community"):
        rate_a = (pay_start / signups * 100) if signups else 0.0
        rate_b = pay_cvr
        mid_count = pay_start
        bottom_count = pay_success
    elif industry in ("ec", "travel", "marketplace", "d2c"):
        # mid→primary / bottom→primary（purchase 系）
        cart = int(counts.get(mid_event, mid_count))
        checkout = int(counts.get(bottom_event, bottom_count))
        rate_a = (primary_count / cart * 100) if cart else 0.0
        rate_b = (primary_count / checkout * 100) if checkout else 0.0
        mid_count = cart
        bottom_count = checkout
    elif industry in ("edu", "finance", "gov"):
        # 開始→完了 / 上流完了→主転換
        start = int(counts.get(mid_event, mid_count))
        upstream = int(counts.get(bottom_event, bottom_count))
        rate_a = (primary_count / start * 100) if start else 0.0
        rate_b = (primary_count / upstream * 100) if upstream else 0.0
        mid_count = start
        bottom_count = upstream

    new_pct = (new_users / uu * 100) if uu else 0.0
    ret_pct = 100.0 - new_pct
    sessions_per_uu = sessions / uu if uu else 0.0
    pv_uu = pageviews / uu if uu else 0.0
    bounce = 100.0 - engaged

    uu_delta, uu_tone = _fmt_delta_pct(float(data["uu_delta"]))
    ses_delta, ses_tone = _fmt_delta_pct(float(data["sessions_delta"]))

    fmt_common = {
        "signup_label": signup_label,
        "primary": primary,
        "cvr_label": cvr_label,
        "mid_label": mid_label,
        "mid_event": mid_event,
        "bottom_label": bottom_label,
        "bottom_event": bottom_event,
    }

    by_id: dict[str, dict[str, Any]] = {
        "signup_cvr": {
            "id": "signup_cvr",
            "label": cvr_label,
            "value": _fmt_pct(signup_rate),
            "value_num": signup_rate,
            "bench": "signup_rate",
            "delta": "+0.1pt",
            "tone": "up",
            "help": _help(
                cvr_label,
                kind="digital",
                meaning=tmpl("signup_cvr", "meaning", loc, **fmt_common),
                formula=tmpl("signup_cvr", "formula", loc, **fmt_common),
                tip=tmpl("signup_cvr", "tip", loc),
            ),
        },
        "primary": {
            "id": "primary",
            "label": signup_label,
            "value": _fmt_int(primary_count),
            "delta": "+8.0%",
            "tone": "up",
            "help": _help(
                signup_label,
                kind="event",
                meaning=tmpl("primary", "meaning", loc, **fmt_common),
                formula=tmpl("primary", "formula", loc, **fmt_common),
                tip=tmpl("primary", "tip", loc),
            ),
        },
        "pay_start": {
            "id": "pay_start",
            "label": mid_label,
            "value": _fmt_int(mid_count),
            "delta": "+3.2%",
            "tone": "up",
            "help": _help(
                mid_label,
                kind="event",
                meaning=tmpl("pay_start", "meaning", loc, **fmt_common),
                formula=tmpl("pay_start", "formula", loc, **fmt_common),
                tip=tmpl("pay_start", "tip", loc),
            ),
        },
        "uu": {
            "id": "uu",
            "label": shared_label("uu", loc),
            "value": _fmt_int(uu),
            "delta": uu_delta,
            "tone": uu_tone,
            "help": shared_help("uu", loc, cvr_label=cvr_label),
        },
        "sessions": {
            "id": "sessions",
            "label": shared_label("sessions", loc),
            "value": _fmt_int(sessions),
            "delta": ses_delta,
            "tone": ses_tone,
            "help": shared_help("sessions", loc),
        },
        "engaged": {
            "id": "engaged",
            "label": shared_label("engaged", loc),
            "value": _fmt_pct(engaged),
            "value_num": engaged,
            "bench": "engaged_rate",
            "delta": "−0.6pt",
            "tone": "down",
            "help": shared_help(
                "engaged", loc, title=shared_label("engaged_title", loc)
            ),
        },
    }
    for kid, row in by_id.items():
        row["focus"] = kid in focus_ids

    # Focus KPIs first so industry differences pop in the summary band
    order = [i for i in copy.get("focus_ids") or [] if i in by_id]
    order += [
        i
        for i in ("signup_cvr", "primary", "pay_start", "uu", "sessions", "engaged")
        if i not in order
    ]
    summary = [by_id[i] for i in order if i in by_id]

    focus_names = [by_id[i]["label"] for i in (copy.get("focus_ids") or []) if i in by_id]
    focus_line = (
        board_tmpl(
            "focus_line",
            loc,
            names=" · ".join(focus_names),
            signup=signup_label,
        )
        if focus_names
        else board_tmpl("focus_line_simple", loc, signup=signup_label)
    )

    funnel = [
        {
            "id": "funnel_cvr",
            "label": cvr_label,
            "value": _fmt_pct(signup_rate),
            "value_num": signup_rate,
            "bench": "signup_rate",
            "focus": True,
            "help": by_id["signup_cvr"]["help"],
        },
        {
            "id": "funnel_rate_a",
            "label": rate_a_label,
            "value": _fmt_pct(rate_a),
            "value_num": rate_a,
            "bench": "signup_to_pay",
            "help": _help(
                rate_a_label,
                kind="digital",
                meaning=tmpl("rate_a", "meaning", loc, **fmt_common),
                formula=rate_a_label,
                tip=tmpl("rate_a", "tip", loc),
            ),
        },
        {
            "id": "funnel_rate_b",
            "label": rate_b_label,
            "value": _fmt_pct(rate_b),
            "value_num": rate_b,
            "bench": "pay_cvr",
            "help": _help(
                rate_b_label,
                kind="digital",
                meaning=tmpl("rate_b", "meaning", loc),
                formula=rate_b_label,
                tip=tmpl("rate_b", "tip", loc),
            ),
        },
        {
            "id": "funnel_bottom",
            "label": bottom_label,
            "value": _fmt_int(bottom_count),
            "value_num": float(bottom_count),
            "help": _help(
                bottom_label,
                kind="event",
                meaning=tmpl("bottom", "meaning", loc, **fmt_common),
                formula=tmpl("bottom", "formula", loc, **fmt_common),
                tip=tmpl("bottom", "tip", loc),
            ),
        },
        {
            "id": "funnel_mid",
            "label": mid_label,
            "value": _fmt_int(mid_count),
            "value_num": float(mid_count),
            "help": by_id["pay_start"]["help"],
        },
        {
            "id": "funnel_primary",
            "label": signup_label,
            "value": _fmt_int(primary_count),
            "value_num": float(primary_count),
            "focus": True,
            "help": by_id["primary"]["help"],
        },
    ]

    engage = [
        {
            "id": "engage_rate_row",
            "label": shared_label("engaged", loc),
            "value": _fmt_pct(engaged),
            "value_num": engaged,
            "bench": "engaged_rate",
            "help": by_id["engaged"]["help"],
        },
        {
            "id": "bounce_like",
            "label": shared_label("bounce_like", loc),
            "value": _fmt_pct(bounce),
            "value_num": bounce,
            "bench": "bounce_rate",
            "help": shared_help("bounce_like", loc),
        },
        {
            "id": "pages_session",
            "label": shared_label("pages_session", loc),
            "value": f"{pages_session:.1f}",
            "value_num": pages_session,
            "bench": "pages_session",
            "help": shared_help("pages_session", loc),
        },
        {
            "id": "pv_uu",
            "label": shared_label("pv_uu", loc),
            "value": f"{pv_uu:.1f}",
            "value_num": pv_uu,
            "bench": "pages_per_uu",
            "help": shared_help("pv_uu", loc),
        },
        {
            "id": "pv",
            "label": shared_label("pv", loc),
            "value": _fmt_int(pageviews),
            "value_num": float(pageviews),
            "delta": ses_delta,
            "help": shared_help("pv", loc),
        },
        {
            "id": "avg_time",
            "label": shared_label("avg_time", loc),
            "value": str(data.get("avg_time") or "—"),
            "value_num": _mmss_to_seconds(data.get("avg_time")),
            "delta": "+4.2%",
            "help": shared_help("avg_time", loc),
        },
    ]

    audience = [
        {
            "id": "new_return",
            "label": shared_label("new_return", loc),
            "value": f"{new_pct:.1f}% / {ret_pct:.1f}%",
            "value_num": new_pct,
            "bench": "new_pct",
            "help": shared_help("new_return", loc),
        },
        {
            "id": "sessions_per_uu",
            "label": shared_label("sessions_per_uu", loc),
            "value": f"{sessions_per_uu:.2f}",
            "value_num": sessions_per_uu,
            "bench": "sessions_per_uu",
            "help": shared_help("sessions_per_uu", loc),
        },
        {
            "id": "aud_uu",
            "label": shared_label("uu", loc),
            "value": _fmt_int(uu),
            "value_num": float(uu),
            "delta": uu_delta,
            "help": by_id["uu"]["help"],
        },
        {
            "id": "aud_sessions",
            "label": shared_label("sessions", loc),
            "value": _fmt_int(sessions),
            "value_num": float(sessions),
            "delta": ses_delta,
            "help": by_id["sessions"]["help"],
        },
    ]

    # イベント: show what the site actually records. Pack events keep their
    # funnel order; then the site's own events, then GA4 auto-collected ones.
    # Pack events with 0 hits are listed separately as "not tracked".
    pack_events = list(events_order)
    is_live = "_live_events" in data
    prev_counts: dict[str, int] = {
        str(k): int(v) for k, v in (data.get("event_counts_prev") or {}).items()
    }
    sample_deltas = ["+8%", "+5%", "+3%", "+2%", "+11%", "+4%", "+6%", "+1%", "+9%", "+7%"]

    def _bucket(name: str) -> int:
        if name in pack_events:
            return 0
        return 2 if name in GA4_AUTO_EVENTS else 1

    candidates = pack_events + [n for n in counts if n not in pack_events]
    shown = [n for n in candidates if counts.get(n, 0) > 0]
    shown.sort(
        key=lambda n: (
            _bucket(n),
            pack_events.index(n) if n in pack_events else -counts.get(n, 0),
        )
    )
    events_missing = [n for n in pack_events if counts.get(n, 0) <= 0]

    def _event_delta(name: str, i: int) -> str:
        if not is_live:
            return sample_deltas[i % len(sample_deltas)]  # sample board only
        prev = prev_counts.get(name, 0)
        if prev <= 0:
            return "—"
        return f"{100 * (counts.get(name, 0) - prev) / prev:+.0f}%"

    events: list[dict[str, Any]] = []
    for i, name in enumerate(shown):
        is_primary = name == primary
        meaning_key = "meaning_primary" if is_primary else "meaning"
        events.append(
            {
                "id": f"ev_{name}",
                "name": name,
                "cat": cat_of.get(name, ""),
                "count": int(counts.get(name, 0)),
                "delta": _event_delta(name, pack_events.index(name) if name in pack_events else i),
                "focus": is_primary,
                "help": _help(
                    name,
                    kind="event",
                    meaning=tmpl(
                        "event",
                        meaning_key,
                        loc,
                        name=name,
                        signup_label=signup_label,
                    ),
                    formula=tmpl("event", "formula", loc, name=name),
                    tip=tmpl("event", "tip", loc),
                ),
            }
        )

    channels: list[dict[str, Any]] = []
    for i, row in enumerate(data.get("channels") or []):
        name, pct = row[0], int(row[1])
        channels.append(
            {
                "id": f"ch_{i}",
                "name": name,
                "pct": pct,
                "color": CHANNEL_COLORS.get(name, "#94a3b8"),
                "help": _help(
                    name,
                    kind="traffic",
                    meaning=tmpl("channel", "meaning", loc, name=name),
                    formula=tmpl("channel", "formula", loc),
                    tip=tmpl("channel", "tip", loc),
                ),
            }
        )

    from sitekpi.i18n.metric_l10n import HELP_TMPL

    def _flat(key: str) -> str:
        row = HELP_TMPL.get(key) or {}
        return str(row.get(loc) or row.get("ja") or "")

    biz_suffix = _flat("biz_suffix")
    biz_tip = _flat("biz_tip")

    business: list[dict[str, Any]] = []
    for bid, label, meaning, formula in pack_biz_rows(
        industry, loc, list(copy["biz"])
    ):
        row: dict[str, Any] = {
            "id": bid,
            "label": label,
            "value": "—",
            "help": _help(
                label,
                kind="business",
                meaning=meaning + biz_suffix,
                formula=formula,
                tip=biz_tip,
            ),
        }
        if bid in ("paid_rate", "churn_rate"):
            row["value_num"] = None
            row["bench"] = bid
        business.append(row)

    ja_notes = list((ind.get("notes") or {}).get(period) or [])
    notes = pack_notes(industry, period, loc, ja_notes)
    next_watch = [
        (board_tmpl("point_n", loc, n=i + 1), note) for i, note in enumerate(notes[:3])
    ]
    if len(next_watch) < 3:
        next_watch.append(
            (
                board_tmpl("biz_unlinked_title", loc),
                board_tmpl("biz_unlinked_body", loc),
            )
        )

    return {
        "industry": industry,
        "industry_label": industry_label,
        "industry_note": "業界パック見本",  # overridden by render via t("sample_meta")
        "property_name": property_name,
        "period_label": "直近28日" if period == "28d" else "直近7日",
        "focus_line": focus_line,
        "benches": benches,
        "summary": summary,
        "funnel": funnel,
        "engage": engage,
        "audience": audience,
        "events": events,
        "events_missing": events_missing,
        "channels": channels,
        "business": business,
        "next_watch": next_watch,
    }
