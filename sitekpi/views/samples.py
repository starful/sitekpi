"""見本ボード — goal list on the left, a live preview of that board on the right.

The preview is the board's own いまの状態 (sentence + 3 tiles) and 行動フロー, computed from the
behaviour's demo numbers and the chosen industry's 業界目安 — the same code the board uses.
"""

from __future__ import annotations

from typing import Any

from sitekpi.i18n import normalize_locale, t
from sitekpi.i18n.pack_l10n import pack_text
from sitekpi.templating import render


def _href(cat: str, ind: str = "") -> str:
    return f"/samples?b={cat}" + (f"&i={ind}" if ind else "")


def resolve(cat: str | None, ind: str | None) -> tuple[str, str]:
    """Valid (behaviour, industry) — unknown values fall back to the first goal / its first industry."""
    from sitekpi.packs import INDUSTRIES
    from sitekpi.packs.behaviors import BEHAVIORS, slug_of

    if cat not in BEHAVIORS:
        cat = next(iter(BEHAVIORS))
    members = list(INDUSTRIES[slug_of(cat)].get("members") or [])
    if ind not in members:
        ind = members[0] if members else ""
    return cat, ind


def preview(cat: str, ind: str, locale: str) -> dict[str, Any]:
    from sitekpi.board.prev import sample_prev
    from sitekpi.flow import resolved_steps, sample_flow
    from sitekpi.packs import BENCHMARKS, DEMO, INDUSTRIES
    from sitekpi.packs.behaviors import behavior_hint, behavior_label, slug_of
    from sitekpi.selection import compose_benchmarks
    from sitekpi.views.board import verdict_scene
    from sitekpi.views.flow import flow_context

    loc = normalize_locale(locale)
    pack = slug_of(cat)
    data = DEMO[pack]["28d"]
    benches = compose_benchmarks(cat, ind) if ind else BENCHMARKS[pack]
    flow = flow_context(pack=pack, flow=sample_flow(pack, data), steps=resolved_steps(pack, {}),
                        locale=loc, live=False)
    verdict = verdict_scene(industry=pack, data=data, benches_raw=benches, flow=flow, locale=loc,
                            prev=sample_prev(pack, "28d", data))

    stages = (flow or {}).get("stages") or []
    entry = int(stages[0].get("users") or 0) if stages else 0
    bars = []
    for i, st in enumerate(stages):
        before = stages[i - 1].get("link") if i else None
        users = int(st.get("users") or 0)
        bars.append({
            "label": st.get("label") or "",
            "users": (st.get("users_fmt") or {}).get("all") or f"{users:,}",
            "height": max(3.0, round(users / entry * 100, 1)) if entry else 3.0,
            "go": (before or {}).get("go", {}).get("all") if before else "",
            "worst": bool(before and before.get("worst")),
            "last": i == len(stages) - 1,
        })

    members = list(INDUSTRIES[pack].get("members") or [])
    ind_label = pack_text(ind, "label", loc, str(INDUSTRIES[ind]["label"])) if ind else t("samplesx.all_ind", loc)
    return {
        "cat": cat,
        "label": behavior_label(cat, loc),
        "hint": behavior_hint(cat, loc),
        "ind": ind,
        "ind_label": ind_label,
        "inds": [{"slug": m, "label": pack_text(m, "label", loc, str(INDUSTRIES[m]["label"])),
                  "selected": m == ind, "href": _href(cat, m)} for m in members],
        "open_href": f"/{ind}" if ind else f"/{pack}",
        "verdict": verdict,
        "bars": bars,
    }


def render_samples(*, locale: str, rail: dict[str, Any], cat: str | None = None, ind: str | None = None,
                   fragment: bool = False) -> str:
    from sitekpi.packs import INDUSTRIES
    from sitekpi.packs.behaviors import BEHAVIORS, GROUPS, behavior_label, slug_of

    loc = normalize_locale(locale)
    cat, ind = resolve(cat, ind)
    cur = preview(cat, ind, loc)
    if fragment:
        return render("samples/_preview.html", loc=loc, cur=cur)

    groups = []
    for gid, lab in GROUPS.items():
        items = []
        for c, beh in BEHAVIORS.items():
            if beh["group"] != gid:
                continue
            n = len(INDUSTRIES[slug_of(c)].get("members") or [])
            items.append({
                "cat": c, "label": behavior_label(c, loc), "selected": c == cat, "href": _href(c),
                "count": t("samplesx.n_ind", loc, n=n) if n else t("samplesx.all_ind", loc),
            })
        if items:
            groups.append({"label": lab.get(loc) or lab["ja"], "goals": items})
    return render("samples.html", loc=loc, rail=rail, groups=groups, cur=cur)
