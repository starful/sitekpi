"""Numbers the story chapters need beyond the board and the flow (docs/plan s03, v7).

Same shape for 見本 / demo boards (``sample_story_x``, deterministic) and live GA4
(``sitekpi.ga4.story.fetch_story_x``). views/story_more.py only reads this shape:

    week0:   ISO date of the first day of week 0 (8 weeks, oldest first, 7 days each)
    weeks:   {"entry": [8 users], "ev": {event: [8 users]}}          users who fired the event that week
    devices: {mobile|desktop|tablet: {"entry": users, "ev": {event: users}}}
    money:   {"cur": {"revenue": n}, "prev": {"revenue": n}} | None   (sites that sell)
    nvr:     {"new": {"users", "conv"}, "returning": {"users", "conv"}, "prev_returning": users} | None
             conv = users who reached the last step of the flow
    release: {"date", "days_after", "before": {"entry", "ev"}, "after": {"entry", "ev"}} | None
             14 days before the release date vs the 14 days from it (only when 14 days have passed)
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any

from sitekpi.board.prev import _jitter

WEEKS = 8
JST = timezone(timedelta(hours=9))  # fixed offset: slim images have no tz database
DEVICES = ("mobile", "desktop", "tablet")
WINDOW = 14  # days compared before / after a release
_STEP_IN = (0, 0, 0, 0, 0.15, 1, 1, 1)  # sample: when the weekly drift kicks in
_DEV_SHARE = {"mobile": 0.66, "desktop": 0.31, "tablet": 0.03}
# how much better / worse each device carries people through a step (sample only)
_DEV_LIFT = {"mobile": 0.78, "desktop": 1.45, "tablet": 1.0}


def today_jst() -> date:
    """GA4 dates ("yesterday", nthWeek) follow the property's time zone; SiteKPI's users are in Japan."""
    return datetime.now(JST).date()


def week0(today: date | None = None) -> date:
    """GA4 nthWeek 0 for the range 55daysAgo → yesterday."""
    return (today or today_jst()) - timedelta(days=55)


def _scaled(n: float, f: float) -> int:
    return max(0, round(n * f))


def sample_story_x(slug: str, data: dict[str, Any], prev: dict[str, Any] | None,
                   flow_raw: dict[str, Any] | None, *, release: dict[str, Any] | None = None,
                   today: date | None = None) -> dict[str, Any]:
    """Deterministic numbers consistent with the pack's DEMO and its sample flow (flow.sample_flow)."""
    tag = f"sx|{slug}|"
    prev = prev or data
    fr = flow_raw or {}
    entry = int(fr.get("entry") or data.get("uu") or 0)
    totals = {str(k): int(v) for k, v in (fr.get("totals") or {}).items()}
    events = list(totals)
    last = next((e for e in reversed(events) if totals.get(e)), "")

    # 8 weeks: weekly users ≈ a quarter of the period's users; the rate drifts down in the last weeks
    p_entry = int(prev.get("uu") or entry)
    wk_entry = [_scaled((p_entry if i < 4 else entry) / 4, _jitter(f"{tag}we{i}", 0.95, 1.05)) for i in range(WEEKS)]
    wk_ev: dict[str, list[int]] = {}
    for n, ev in enumerate(events):
        share = totals[ev] / entry if entry else 0.0
        series = []
        for i in range(WEEKS):
            drift = 1.0 - 0.03 * (n + 1) * _STEP_IN[i]  # every step loses a little from week 5 on
            series.append(_scaled(wk_entry[i] * share, drift * _jitter(f"{tag}w{ev}{i}", 0.985, 1.015)))
        wk_ev[ev] = series

    # devices: shares of each step, mobile carrying people a little less far than desktop
    devices: dict[str, Any] = {}
    for d in DEVICES:
        d_entry = _scaled(entry, _DEV_SHARE[d])
        evs: dict[str, int] = {}
        before = d_entry
        for n, ev in enumerate(events, start=1):
            depth = n / max(len(events), 1)
            raw = totals[ev] * _DEV_SHARE[d] * (_DEV_LIFT[d] ** depth)
            evs[ev] = min(before, _scaled(raw, 1.0))
            before = evs[ev] or before
        devices[d] = {"entry": d_entry, "ev": evs}
    # keep device sums equal to the totals
    for ev in events:
        s = sum(devices[d]["ev"][ev] for d in DEVICES)
        if s:
            for d in DEVICES:
                devices[d]["ev"][ev] = round(devices[d]["ev"][ev] * totals[ev] / s)

    money = None
    from sitekpi.board.extras import sample_extras

    ex = sample_extras(slug, data, prev)  # the same revenue as 詳しい数字 › 売上
    if ex.get("has_revenue") and ex["cur"].get("revenue") and ex["prev"].get("revenue"):
        money = {"cur": {"revenue": float(ex["cur"]["revenue"])}, "prev": {"revenue": float(ex["prev"]["revenue"])}}

    nvr = None
    new_u, ret_u = int(data.get("new_users") or 0), int(data.get("returning_users") or 0)
    if new_u and ret_u and last:
        conv = totals[last]
        ret_conv = min(ret_u, round(conv * _jitter(tag + "rc", 0.58, 0.66)))
        nvr = {"new": {"users": new_u, "conv": conv - ret_conv}, "returning": {"users": ret_u, "conv": ret_conv},
               "prev_returning": round(ret_u * _jitter(tag + "pr", 1.02, 1.05))}

    rel = None
    if release and release.get("date"):
        rel = _sample_release(tag, release, entry, totals, events, today=today)
    return {"week0": week0(today).isoformat(), "weeks": {"entry": wk_entry, "ev": wk_ev}, "devices": devices,
            "money": money, "nvr": nvr, "release": rel}


def _sample_release(tag: str, release: dict[str, Any], entry: int, totals: dict[str, int], events: list[str],
                    *, today: date | None = None) -> dict[str, Any]:
    """Before / after a release: the step right after the release gets better, the next one a little worse."""
    d = date.fromisoformat(str(release["date"]))
    days_after = ((today or today_jst()) - d).days
    half = entry * WINDOW / 28
    before = {"entry": round(half), "ev": {e: round(totals[e] * WINDOW / 28) for e in events}}
    after_ev: dict[str, int] = {}
    focus = int(release.get("focus") or 1)  # flow stage that got better (stage n = events[n - 1])
    for n, e in enumerate(events, start=1):
        f = 1.0
        if n >= focus:
            f = 1.11  # more people got past the improved step …
        if n >= focus + 1:
            f = 1.11 * 0.97  # … but a few more of them stop at the next one
        after_ev[e] = round(before["ev"][e] * f * _jitter(f"{tag}ra{e}", 0.998, 1.002))
    after = {"entry": before["entry"], "ev": after_ev}
    return {"date": d.isoformat(), "days_after": days_after, "before": before, "after": after}
