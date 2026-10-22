"""サイトの設定 wizard — view model."""

from __future__ import annotations

from typing import Any

from sitekpi.i18n import normalize_locale
from sitekpi.i18n.pack_l10n import pack_text
from sitekpi.packs.flows import FLOW_STEPS, step_label
from sitekpi.templating import render


def _flow_options(loc: str, sel: dict[str, str], counts: dict[str, int] | None,
                  flows: dict[str, list[dict[str, str]]]) -> list[dict[str, Any]]:
    from sitekpi.packs.behaviors import BEHAVIORS, behavior_hint, behavior_label, slug_of

    out = []
    for cat in BEHAVIORS:
        steps = [{**s, "found": None if counts is None else s["event"] in counts} for s in flows[cat]]
        out.append({
            "cat": cat, "label": behavior_label(cat, loc), "hint": behavior_hint(cat, loc),
            "steps": steps, "hits": sum(1 for s in steps if s["found"]), "selected": sel["behavior"] == cat,
        })
    best = max((b["hits"] for b in out), default=0)
    for b in out:
        b["recommended"] = best > 0 and b["hits"] == best
    # closest to the site first, the rest in their usual order
    return sorted(out, key=lambda b: (not b["recommended"],))


def _industry_options(loc: str, sel: dict[str, str]) -> dict[str, Any]:
    from sitekpi.packs import BENCHMARKS, INDUSTRIES, packs_by_category
    from sitekpi.packs.behaviors import behavior_label

    def item(slug: str, label: str) -> dict[str, Any]:
        return {"slug": slug, "label": pack_text(slug, "label", loc, label),
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
            "other_selected": any(i["selected"] for g in others for i in g["packs"])}


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
) -> str:
    from sitekpi.packs.behaviors import behavior_label, slug_of

    loc = normalize_locale(locale)
    ctx: dict[str, Any] = {"step": step, "sel": sel, "error": error, "can_adjust": can_adjust,
                           "knows_events": counts is not None, "max_steps": max_steps}
    if step == "flow":
        ctx["options"] = _flow_options(loc, sel, counts, flows)
    elif step == "industry":
        ctx["behavior_label"] = behavior_label(sel["behavior"], loc)
        ctx["industries"] = _industry_options(loc, sel)
    else:
        pack = slug_of(sel["behavior"])
        ctx["behavior_label"] = behavior_label(sel["behavior"], loc)
        ctx["rows"] = [{**s, "count": None if counts is None else counts.get(s["event"])} for s in flows[sel["behavior"]]]
        ctx["missing"] = sum(1 for r in ctx["rows"] if counts is not None and not r["count"])
        ctx["events"] = sorted(((n, c) for n, c in (counts or {}).items()), key=lambda x: -x[1])
        ctx["std"] = [{"key": k, "event": k, "label": step_label(k, loc, pack)} for k in FLOW_STEPS[pack]]
        ctx["counts"] = counts or {}
    return render("setup.html", loc=loc, rail=rail, **ctx)
