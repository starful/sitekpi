"""見本ボード一覧 — every behaviour's flow with the industries that use it."""

from __future__ import annotations

from typing import Any

from sitekpi.i18n import normalize_locale
from sitekpi.i18n.pack_l10n import pack_text
from sitekpi.packs.flows import FLOW_STEPS, step_label
from sitekpi.templating import render


def render_samples(*, locale: str, rail: dict[str, Any]) -> str:
    from sitekpi.packs import BENCHMARKS, INDUSTRIES
    from sitekpi.packs.behaviors import BEHAVIORS, GROUPS, behavior_hint, behavior_label, slug_of

    loc = normalize_locale(locale)
    behaviors = []
    for cat in BEHAVIORS:
        pack = slug_of(cat)
        behaviors.append({
            "cat": cat,
            "group": BEHAVIORS[cat]["group"],
            "slug": pack,
            "label": behavior_label(cat, loc),
            "hint": behavior_hint(cat, loc),
            "steps": [{"label": step_label(s, loc, pack), "event": s, "found": None} for s in FLOW_STEPS[pack]],
            "industries": [
                {"slug": m, "label": pack_text(m, "label", loc, str(INDUSTRIES[m]["label"])),
                 "cited": sum(1 for spec in BENCHMARKS[m].values() if (spec.get("source") or {}).get("url"))}
                for m in INDUSTRIES[pack]["members"]
            ],
        })
    groups = [{"label": lab.get(loc) or lab["ja"], "behaviors": [b for b in behaviors if b["group"] == g]}
              for g, lab in GROUPS.items()]
    return render("samples.html", loc=loc, rail=rail, groups=[g for g in groups if g["behaviors"]])
