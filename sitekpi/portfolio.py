"""マイサイト一覧 (/sites): every GA4 property the signed-in Google account can read, one row each.

For consultants and agencies (docs/plan 「목적과 대상」): the same 総評 sentence and three tiles as each
board, side by side. Rows for properties other than the open one use a first guess of 訪問者の行動
(selection.guess_behavior → its usual industry), labelled 仮 — the same rule as a first board.

Plan gate (billing.PRO_FEATURES "site_compare"): the list itself is free, and so is the open site's
summary; the other sites' summaries need Pro. Demo sessions (dev / tests) see everything.

GA4: two reports per property (event names, board overlay), run side by side for at most MAX_SITES
properties, cached 5 min per property · period · language. Errors become a row note, never a page error.
"""

from __future__ import annotations

import copy
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from sitekpi.cache import TTLCache

MAX_SITES = 12
_ROW_CACHE = TTLCache(maxsize=512, ttl=300.0)


def _sub_session(session: dict[str, Any], prop: dict[str, str]) -> dict[str, Any]:
    """A session-shaped dict for one property, sharing the sign-in (ga4/* read ga4_property from it)."""
    return {"ga4_credentials": session.get("ga4_credentials"), "ga4_property": dict(prop),
            "ga4_email": session.get("ga4_email")}


def _scene(pack: str, industry: str, behavior: str, data: dict[str, Any], prev: dict[str, Any] | None,
           sub: dict[str, Any] | None, locale: str) -> dict[str, Any]:
    from sitekpi.benchmarks import load_effective
    from sitekpi.selection import compose_benchmarks
    from sitekpi.views.board import verdict_scene

    benches = compose_benchmarks(behavior, industry)
    if sub is not None:  # live: the property's own 自社目安 apply (scope prop:{id})
        benches = {k: dict(v) for k, v in benches.items()}
        eff = load_effective(sub, pack, benches, live=True)
        for k, spec in eff.items():
            if spec.get("custom"):
                benches[k]["low"], benches[k]["high"] = spec["low"], spec["high"]
    return verdict_scene(industry=pack, data=data, benches_raw=benches, flow=None, locale=locale, prev=prev)


def _issue(verdict: dict[str, Any]) -> str:
    """Row colour: down when a tile is judged 要注意, up when every judged tile is 良好 / 目安内."""
    judges = [str(((k.get("bench") or {}).get("judge")) or "") for k in verdict.get("tiles") or []]
    judged = [j for j in judges if j]
    if "down" in judged:
        return "down"
    return "up" if judged else "neutral"


def demo_row(prop: dict[str, str], *, period: str, locale: str) -> dict[str, Any]:
    from sitekpi.board.prev import sample_prev
    from sitekpi.packs import DEMO
    from sitekpi.packs.behaviors import slug_of
    from sitekpi.selection import default_industry, guess_behavior

    behavior, _ = guess_behavior(None, prop.get("name", ""))
    pack, industry = slug_of(behavior), default_industry(behavior)
    data = DEMO[pack][period]
    verdict = _scene(pack, industry, behavior, data, sample_prev(pack, period, data), None, locale)
    return {"behavior": behavior, "industry": industry, "verdict": verdict, "error": ""}


def live_row(session: dict[str, Any], prop: dict[str, str], *, period: str, locale: str,
             selection: dict[str, str] | None = None) -> dict[str, Any]:
    """One property's 総評. ``selection`` = the open site's chosen 行動 × 業種 (others are guessed)."""
    from sitekpi.ga4.data import discover_event_names, fetch_pack_overlay
    from sitekpi.packs import DEMO, INDUSTRIES
    from sitekpi.packs.behaviors import slug_of
    from sitekpi.selection import default_industry, guess_behavior

    key = f"{prop['id']}|{period}|{locale}|{(selection or {}).get('behavior', '')}|{(selection or {}).get('industry', '')}"
    hit = _ROW_CACHE.get(key)
    if hit is not None:
        return copy.deepcopy(hit)
    sub = _sub_session(session, prop)
    found, err = discover_event_names(sub, period=period, limit=200)
    if err and not found:
        return {"behavior": "", "industry": "", "verdict": None, "error": "ga4"}
    counts = {e["name"]: int(e.get("count") or 0) for e in found}
    if selection and selection.get("behavior") and selection.get("industry"):
        behavior, industry, guessed = selection["behavior"], selection["industry"], False
    else:
        behavior, _ = guess_behavior(counts, prop.get("name", ""))
        industry, guessed = default_industry(behavior), True
    pack = slug_of(behavior)
    events = [e["name"] for e in found] or list(INDUSTRIES[pack].get("events") or [])
    primary = str(INDUSTRIES[pack].get("primary_event") or (events[0] if events else ""))
    overlay, err = fetch_pack_overlay(sub, period=period, event_names=events, primary_event=primary)
    if not overlay:
        return {"behavior": behavior, "industry": industry, "verdict": None, "error": "ga4"}
    data = dict(DEMO[pack][period])
    for k in ("_ga4_property", "_ga4_label", "_ga4_property_id"):
        overlay.pop(k, None)
    prev = overlay.pop("_prev", None)
    data.update(overlay)
    out = {"behavior": behavior, "industry": industry, "guessed": guessed,
           "verdict": _scene(pack, industry, behavior, data, prev, sub, locale), "error": ""}
    if sub.get("ga4_credentials") != session.get("ga4_credentials"):  # token refreshed on the way
        session["ga4_credentials"] = sub["ga4_credentials"]
    _ROW_CACHE.set(key, copy.deepcopy(out))
    return out


def site_rows(session: dict[str, Any], props: list[dict[str, str]], *, period: str, locale: str,
              current_id: str, selection: dict[str, str] | None, full: bool, demo: bool) -> list[dict[str, Any]]:
    """Rows for /sites. ``full`` = every site's summary (Pro / demo); otherwise only the open one's."""
    from sitekpi.packs.behaviors import behavior_label
    from sitekpi.packs.registry import INDUSTRIES
    from sitekpi.i18n.pack_l10n import pack_text

    props = props[:MAX_SITES]

    def one(p: dict[str, str]) -> dict[str, Any] | None:
        is_cur = p["id"] == current_id
        if not (full or is_cur):
            return None
        try:
            if demo:
                return demo_row(p, period=period, locale=locale)
            return live_row(session, p, period=period, locale=locale, selection=selection if is_cur else None)
        except Exception:  # noqa: BLE001 — one property must not break the list
            return {"behavior": "", "industry": "", "verdict": None, "error": "ga4"}

    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(one, props))
    rows = []
    for p, r in zip(props, results):
        row: dict[str, Any] = {"id": p["id"], "name": p.get("name") or p["id"], "account": p.get("account") or "",
                               "current": p["id"] == current_id, "locked": r is None}
        if r:
            ind = r.get("industry") or ""
            row.update({
                "error": r.get("error") or "",
                "guessed": bool(r.get("guessed", demo)) and p["id"] != current_id,
                "behavior_label": behavior_label(r["behavior"], locale) if r.get("behavior") else "",
                "industry_label": pack_text(ind, "label", locale, str(INDUSTRIES[ind]["label"])) if ind in INDUSTRIES else "",
                "verdict": r.get("verdict"),
                "tone": _issue(r["verdict"]) if r.get("verdict") else "neutral",
            })
        rows.append(row)
    return rows
