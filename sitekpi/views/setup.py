"""サイトの設定 wizard — view model."""

from __future__ import annotations

from typing import Any

from sitekpi.i18n import normalize_locale
from sitekpi.i18n.pack_l10n import pack_text
from sitekpi.packs.flows import FLOW_STEPS, step_label
from sitekpi.templating import render


UNIVERSAL = {"session_start", "user_engagement", "page_view"}


def _flow_options(loc: str, sel: dict[str, str], counts: dict[str, int] | None,
                  flows: dict[str, list[dict[str, str]]]) -> dict[str, Any]:
    """Step ① choices: the closest flows first, then every flow by group."""
    from sitekpi.packs.behaviors import BEHAVIORS, GROUPS, behavior_hint, behavior_label

    out = []
    for cat, beh in BEHAVIORS.items():
        steps = [{**s, "found": None if counts is None else s["event"] in counts} for s in flows[cat]]
        own = [s for s in steps if s["event"] not in UNIVERSAL]
        out.append({
            "cat": cat, "group": beh["group"], "label": behavior_label(cat, loc), "hint": behavior_hint(cat, loc),
            # the universal first steps say nothing about which flow fits
            "steps": steps, "own": own, "hits": sum(1 for s in own if s["found"]), "total": len(own),
            "selected": sel["behavior"] == cat, "recommended": False,
        })
    best = max((b["hits"] for b in out), default=0)
    closest = sorted([b for b in out if best and b["hits"] == best], key=lambda b: -b["hits"] / max(b["total"], 1))[:3]
    for b in closest:
        b["recommended"] = True
    rest = [b for b in out if b not in closest]
    groups = [{"id": g, "label": lab.get(loc) or lab["ja"], "options": [b for b in rest if b["group"] == g]}
              for g, lab in GROUPS.items()]
    for g in groups:  # the group holding the current flow starts open
        g["open"] = any(b["selected"] for b in g["options"])
    # the shared start is drawn once above the list, not on every card
    common = [s for s in out[0]["steps"] if s["event"] in UNIVERSAL] if out else []
    return {"closest": closest, "groups": [g for g in groups if g["options"]], "count": len(out), "common": common}


def _industry_options(loc: str, sel: dict[str, str], site: dict[str, float] | None = None) -> dict[str, Any]:
    from sitekpi.packs import BENCHMARKS, INDUSTRIES, packs_by_category
    from sitekpi.packs.behaviors import behavior_label
    from sitekpi.packs.industry_about import industry_about

    def compare(slug: str) -> dict[str, Any] | None:
        """One number that shows how the site differs: its engagement rate vs this industry's."""
        spec = BENCHMARKS[slug].get("engaged_rate")
        if not site or spec is None or not (spec.get("source") or {}).get("url"):
            return None
        std = (float(spec["low"]) + float(spec["high"])) / 2
        you = float(site["engaged_rate"]) if site.get("engaged_rate") is not None else None
        if you is None:
            return None
        return {"you": f"{you:.1f}%", "std": f"{std:.1f}%", "diff": f"{you - std:+.1f}pt".replace("-", "−"),
                # same rule as the board: inside the band is neutral, outside is good / needs attention
                "tone": "up" if you > float(spec["high"]) else "down" if you < float(spec["low"]) else "ok"}

    def item(slug: str, label: str) -> dict[str, Any]:
        return {"slug": slug, "label": pack_text(slug, "label", loc, label),
                "about": industry_about(slug, loc) or pack_text(slug, "hint", loc, str(INDUSTRIES[slug].get("hint") or "")),
                "compare": compare(slug),
                "hint": pack_text(slug, "hint", loc, str(INDUSTRIES[slug].get("hint") or "")),
                "cited": sum(1 for spec in BENCHMARKS[slug].values() if (spec.get("source") or {}).get("url")),
                "selected": sel["industry"] == slug}

    main, others = [], []
    for cid, _lab, items in packs_by_category():
        rows = [item(s, lab) for s, lab, _h in items]
        if cid == sel["behavior"]:
            main = rows
        else:
            others.append({"label": behavior_label(cid, loc), "packs": rows})
    return {"main": main, "others": others,
            "other_selected": not main or any(i["selected"] for g in others for i in g["packs"])}


def render_setup(
    *,
    step: str,
    sel: dict[str, str],
    locale: str,
    counts: dict[str, int] | None,
    flows: dict[str, list[dict[str, str]]],
    can_adjust: bool,
    max_steps: int,
    rail: dict[str, Any],
    error: str | None = None,
    site: dict[str, float] | None = None,
) -> str:
    from sitekpi.packs.behaviors import behavior_label, slug_of

    loc = normalize_locale(locale)
    ctx: dict[str, Any] = {"step": step, "sel": sel, "error": error, "can_adjust": can_adjust,
                           "knows_events": counts is not None, "max_steps": max_steps}
    if step == "flow":
        ctx["options"] = _flow_options(loc, sel, counts, flows)
    elif step == "industry":
        ctx["behavior_label"] = behavior_label(sel["behavior"], loc)
        from sitekpi.packs.behaviors import BEHAVIORS
        ctx["behavior_group"] = (BEHAVIORS.get(sel["behavior"]) or {}).get("group", "")
        ctx["industries"] = _industry_options(loc, sel, site)
        ctx["site"] = site
    else:
        pack = slug_of(sel["behavior"])
        ctx["behavior_label"] = behavior_label(sel["behavior"], loc)
        ctx["rows"] = [{**s, "count": None if counts is None else counts.get(s["event"])} for s in flows[sel["behavior"]]]
        ctx["missing"] = sum(1 for r in ctx["rows"] if counts is not None and not r["count"])
        ctx["events"] = sorted(((n, c) for n, c in (counts or {}).items()), key=lambda x: -x[1])
        ctx["std"] = [{"key": k, "event": k, "label": step_label(k, loc, pack)} for k in FLOW_STEPS[pack]]
        ctx["counts"] = counts or {}
    return render("setup.html", loc=loc, rail=rail, **ctx)
