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


def save_selection(session: MutableMapping[str, Any], behavior: str, industry: str) -> None:
    session[BEHAVIOR_KEY] = behavior
    session[INDUSTRY_KEY] = industry
    session.pop("benchmark_pack", None)


def clear_selection(session: MutableMapping[str, Any]) -> None:
    for k in (BEHAVIOR_KEY, INDUSTRY_KEY, "benchmark_pack"):
        session.pop(k, None)


def flow_pack(sel: dict[str, str]) -> str:
    return slug_of(sel["behavior"]) if sel.get("behavior") else ""


def is_ready(sel: dict[str, str]) -> bool:
    return bool(sel.get("behavior") and sel.get("industry"))


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
