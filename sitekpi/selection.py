"""What the connected board shows: 訪問者の行動 (flow) × 業種 (standards).

- behaviour (category id, e.g. ``commerce``) decides the flow, the events and the
  board's funnel wording — its pack is ``type-<behaviour>``.
- industry (pack slug, e.g. ``apparel``) decides the 業界目安. Metrics that mean
  the same everywhere always use the industry's standard; funnel-step rates use
  it only when the industry's funnel is defined like the behaviour's.
"""

from __future__ import annotations

from typing import Any, MutableMapping

from sitekpi.i18n import t
from sitekpi.i18n.pack_l10n import pack_text
from sitekpi.packs import BENCHMARKS, INDUSTRIES
from sitekpi.packs.behaviors import BEHAVIORS, SHARED_METRICS, behavior_label, category_of, is_behavior, slug_of

BEHAVIOR_KEY = "flow_behavior"
INDUSTRY_KEY = "industry"


def selection(session: MutableMapping[str, Any]) -> dict[str, str]:
    behavior = str(session.get(BEHAVIOR_KEY) or "")
    industry = str(session.get(INDUSTRY_KEY) or "")
    legacy = str(session.get("benchmark_pack") or "")  # before the split
    if legacy and not behavior and not industry:
        if is_behavior(legacy):
            behavior = category_of(legacy)
        elif legacy in INDUSTRIES:
            industry = legacy
            behavior = str(INDUSTRIES[legacy].get("category") or "")
    if behavior not in BEHAVIORS:
        behavior = ""
    if industry not in INDUSTRIES or INDUSTRIES[industry].get("virtual"):
        industry = ""
    return {"behavior": behavior, "industry": industry}


AUTO_KEY = "auto_selection"  # set while the flow is only our first guess (cleared once the user chooses)


def save_selection(session: MutableMapping[str, Any], behavior: str, industry: str) -> None:
    session[BEHAVIOR_KEY] = behavior
    session[INDUSTRY_KEY] = industry
    session.pop("benchmark_pack", None)
    session.pop(AUTO_KEY, None)  # the user chose → no more 仮 notice


# 主転換 events from the most to the least specific: a site that records purchase is a shop
# even if it also records click; one with only form_submit is an inquiry site, etc.
_PRIMARY_RANK = {"purchase": 5, "sign_up": 4, "form_submit": 3, "video_complete": 2, "click": 1}
FALLBACK_BEHAVIOR = "blog"  # no conversion event yet: reading is what every site has


def guess_behavior(event_counts: dict[str, int] | None, property_name: str = "") -> tuple[str, str]:
    """First guess of 訪問者の行動 so the board can open before any setup.

    Returns (behaviour, reason) — reason is the event that decided it, "demo", or "".
    Picks the behaviour whose 主転換 event the site records, preferring specific
    conversions and flows whose steps the site also records."""
    if event_counts is None:  # demo: no GA4 — go by the demo property's name
        name = property_name.lower()
        return ("content" if "media" in name else "commerce"), "demo"
    seen = {e for e, n in event_counts.items() if n}
    best: tuple[float, int, str] | None = None
    for i, (cat, beh) in enumerate(BEHAVIORS.items()):
        primary = str(beh.get("primary") or "")
        if primary not in seen:
            continue
        steps = [s for s in beh.get("steps") or [] if s != primary]  # the way there, not the goal
        hits = sum(1 for s in steps if s in seen)
        score = _PRIMARY_RANK.get(primary, 0) * 10 + hits / max(len(steps), 1) * 9 + hits * 0.1
        score += 0.05 if cat == FALLBACK_BEHAVIOR else 0  # generic click/scroll sites read, not phone
        if best is None or score > best[0] or (score == best[0] and i < best[1]):
            best = (score, i, cat)
    if best:
        cat = best[2]
        return cat, str(BEHAVIORS[cat].get("primary") or "")
    return FALLBACK_BEHAVIOR, ""


def ensure_selection(session: MutableMapping[str, Any], event_counts: dict[str, int] | None,
                     property_name: str = "") -> dict[str, str]:
    """Numbers first: a connected property always gets a board. If nothing is chosen yet,
    guess the behaviour (and its usual industry) and remember that it is only a guess."""
    sel = selection(session)
    if is_ready(sel):
        return sel
    behavior = sel["behavior"]
    reason = ""
    if not behavior:
        behavior, reason = guess_behavior(event_counts, property_name)
    industry = sel["industry"] or default_industry(behavior)
    save_selection(session, behavior, industry)
    if not sel["behavior"]:
        session[AUTO_KEY] = {"behavior": behavior, "reason": reason}
    return selection(session)


def auto_notice(session: MutableMapping[str, Any], locale: str) -> dict[str, str] | None:
    """The 仮 notice on the board while the flow is our guess."""
    auto = session.get(AUTO_KEY)
    if not isinstance(auto, dict) or not auto.get("behavior"):
        return None
    reason = str(auto.get("reason") or "")
    why = (t("notice.why_demo", locale) if reason == "demo"
           else t("notice.why_event", locale, event=reason) if reason
           else t("notice.why_default", locale))
    flow = behavior_label(str(auto["behavior"]), locale)
    ind = str(session.get(INDUSTRY_KEY) or "")
    if ind in INDUSTRIES:
        from sitekpi.i18n.pack_l10n import pack_text

        name = pack_text(ind, "label", locale, str(INDUSTRIES[ind]["label"]))
        # both guesses are listed under the lead, each with its own fix button (board.html)
        return {"text": t("notice.lead", locale, why=why), "flow": flow, "ind": name, "why": why}
    return {"text": t("notice.auto", locale, behavior=flow, why=why), "flow": "", "ind": ""}


def clear_selection(session: MutableMapping[str, Any]) -> None:
    for k in (BEHAVIOR_KEY, INDUSTRY_KEY, "benchmark_pack"):
        session.pop(k, None)


def flow_pack(sel: dict[str, str]) -> str:
    return slug_of(sel["behavior"]) if sel.get("behavior") else ""


def is_ready(sel: dict[str, str]) -> bool:
    return bool(sel.get("behavior") and sel.get("industry"))


def default_industry(behavior: str) -> str:
    """Pick a usable industry pack so the board can load without a separate industry step."""
    if behavior not in BEHAVIORS:
        return ""
    beh = BEHAVIORS[behavior]
    for s in list(beh.get("industries") or []):
        if s in INDUSTRIES and not INDUSTRIES[s].get("virtual"):
            return s
    for s, m in INDUSTRIES.items():
        if m.get("category") == behavior and not m.get("virtual"):
            return s
    rep = str(beh.get("rep") or "")
    if rep in INDUSTRIES and not INDUSTRIES[rep].get("virtual"):
        return rep
    for s, m in INDUSTRIES.items():
        if not m.get("virtual"):
            return s
    return ""


def same_funnel(behavior: str, industry: str) -> bool:
    """Do the industry's funnel-step rates mean the same as the behaviour's?"""
    logic = lambda s: str(INDUSTRIES[s].get("logic_as") or s)  # noqa: E731
    return logic(industry) == logic(slug_of(behavior))


# Same meaning whatever the visitors are asked to do (主転換CVR is not: purchase ≠ inquiry)
SITE_METRICS = tuple(k for k in SHARED_METRICS if k != "signup_rate")


def compose_benchmarks(behavior: str, industry: str) -> dict[str, dict[str, Any]]:
    """業界目安 for a behaviour × industry board."""
    src = BENCHMARKS[industry]
    same_goal = INDUSTRIES[industry].get("category") == behavior  # 主転換 means the same thing
    keep_all = same_goal and same_funnel(behavior, industry)       # step rates computed the same way
    # 主転換CVR: always the chosen industry's figure — CVR levels differ by industry
    keep = set(SITE_METRICS) | {"signup_rate"}
    return {k: dict(v) for k, v in src.items() if keep_all or k in keep}


def selection_label(sel: dict[str, str], locale: str) -> str:
    parts = []
    if sel.get("behavior"):
        parts.append(behavior_label(sel["behavior"], locale))
    if sel.get("industry"):
        ind = sel["industry"]
        parts.append(pack_text(ind, "label", locale, str(INDUSTRIES[ind]["label"])))
    return t("selection.join", locale).join(parts)
