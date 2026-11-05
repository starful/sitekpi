"""サイトの設定 on the board — view models (no pages of their own any more).

flow_editor_context : the board's 編集モード of 「どこで離れているか」 (board/edit_bar.html + board_edit.js)
industry_context    : the 比べる業種 drawer (board/drawer_industry.html)
"""

from __future__ import annotations

from typing import Any

from sitekpi.i18n import normalize_locale, t
from sitekpi.i18n.pack_l10n import pack_text
from sitekpi.packs.flows import FLOW_STEPS, step_label

EVENT_LIST_MAX = 40


def _templates(loc: str) -> list[dict[str, Any]]:
    """Every behaviour's standard flow — the 「ひな形から始める」 choices."""
    from sitekpi.packs.behaviors import BEHAVIORS, GROUPS, behavior_label, slug_of

    out = []
    for cat, beh in BEHAVIORS.items():
        pack = slug_of(cat)
        g = GROUPS.get(beh["group"]) or {}
        out.append({
            "id": cat,
            "label": behavior_label(cat, loc),
            "group": g.get(loc) or g.get("ja") or "",
            "steps": [{"key": k, "event": k, "label": step_label(k, loc, pack)} for k in FLOW_STEPS[pack]],
        })
    return out


def flow_editor_context(
    *,
    locale: str,
    behavior: str,
    industry: str,
    steps: list[dict[str, str]],
    counts: dict[str, int],
    entry: int,
    is_demo: bool,
    max_steps: int,
    step_counts: dict[str, int] | None = None,
) -> dict[str, Any]:
    """The board's 編集モード: template groups + the data island board_edit.js reads.

    step_counts: people per event as the board's flow shows them (this period) — the steps use
    these; the event list keeps the site's own event counts."""
    from sitekpi.packs import INDUSTRIES

    loc = normalize_locale(locale)
    templates = _templates(loc)
    events = sorted(counts.items(), key=lambda kv: -kv[1])[:EVENT_LIST_MAX]
    ind_label = pack_text(industry, "label", loc, str(INDUSTRIES[industry]["label"])) if industry in INDUSTRIES else ""
    groups: list[dict[str, Any]] = []
    for tpl in templates:
        if not groups or groups[-1]["label"] != tpl["group"]:
            groups.append({"label": tpl["group"], "opts": []})
        groups[-1]["opts"].append({"id": tpl["id"], "label": tpl["label"], "selected": tpl["id"] == behavior})
    data = {
        "behavior": behavior,
        "steps": [{"key": s["key"], "event": s["event"], "label": s["label"]} for s in steps],
        "templates": {tpl["id"]: tpl["steps"] for tpl in templates},
        "counts": {**counts, **(step_counts or {})},
        "events": [{"name": n, "count": c} for n, c in events],
        "entry": entry,
        "max": max_steps,
        "i18n": {
            "entry": t("flow.entry", loc),
            "people": t("setupx.unit", loc),
            "none": t("setup.adjust.none", loc),
            "pick": t("setupx.pick_event", loc),
            "no_event": t("setupx.no_event", loc),
            "from_prev": t("setupx.from_prev", loc),
            "primary": t("primary_tag", loc),
            "step_n": t("setupx.step_n", loc),
            "step_last": t("setupx.step_last", loc),
            "new_step": t("setupx.new_step", loc),
            "all_ok": t("setupx.all_ok", loc),
            "missing": t("setupx.missing", loc),
            "worst": t("setupx.worst", loc),
            "add_here": t("setupx.add_here", loc),
            "too_many": t("setupx.too_many", loc, n=max_steps),
            "min_one": t("setupx.min_one", loc),
            "remove_step": t("setupx.remove_step", loc),
            "removed": t("setupx.removed", loc),
            "undo": t("setupx.undo", loc),
            "more": t("setupx.more_events", loc),
            "fewer": t("setupx.fewer_events", loc),
        },
    }
    return {"data": data, "groups": groups, "industry_label": ind_label, "is_demo": is_demo}


# --- /setup/industry -----------------------------------------------------------------

PREVIEW_KEYS = ("signup_rate", "engaged_rate", "bounce_rate", "signup_to_pay")


def _source_kind(spec: dict[str, Any]) -> str:
    src = spec.get("source") or {}
    if spec.get("custom"):
        return "custom"
    if src.get("url"):
        return "cited"
    if src.get("kind") == "blend":
        return "blend"
    return "none"


def _preview(behavior: str, industry: str, mine: dict[str, float | None], labels: dict[str, str],
             loc: str) -> list[dict[str, Any]]:
    """業界目安 this industry would give the board, next to the site's own numbers where known."""
    from sitekpi.selection import compose_benchmarks

    bench = compose_benchmarks(behavior, industry)
    rows = []
    for key in PREVIEW_KEYS:
        spec = bench.get(key)
        if not spec:
            continue
        low, high = float(spec["low"]), float(spec["high"])
        mid = (low + high) / 2
        kind = _source_kind(spec)
        you = mine.get(key)
        judge = ""
        if kind != "none" and you is not None:
            hib = bool(spec.get("higher_is_better", spec.get("hib", True)))
            if low <= you <= high:
                judge = "mid"
            elif (you > high) == hib:
                judge = "up"
            else:
                judge = "down"
        rows.append({
            "label": labels.get(key, key),
            "bench": t("bench_none", loc) if kind == "none" else f"{mid:.1f}%".replace(".0%", "%"),
            "you": "—" if you is None else f"{you:.1f}%",
            "gap": "" if (you is None or kind == "none") else f"{you - mid:+.1f}pt",
            "judge": judge,
            "none": kind == "none",
        })
    return rows


def industry_context(
    *,
    locale: str,
    behavior: str,
    industry: str,
    mine: dict[str, float | None],
    labels: dict[str, str],
) -> dict[str, Any]:
    from sitekpi.packs import BENCHMARKS, INDUSTRIES, packs_by_category
    from sitekpi.packs.behaviors import behavior_label
    from sitekpi.packs.industry_about import industry_about

    loc = normalize_locale(locale)

    def item(slug: str, label: str) -> dict[str, Any]:
        return {
            "slug": slug,
            "label": pack_text(slug, "label", loc, label),
            "about": industry_about(slug, loc) or pack_text(slug, "hint", loc, str(INDUSTRIES[slug].get("hint") or "")),
            "cited": sum(1 for spec in BENCHMARKS[slug].values() if (spec.get("source") or {}).get("url")),
            "selected": industry == slug,
        }

    main: list[dict[str, Any]] = []
    others: list[dict[str, Any]] = []
    previews: dict[str, list[dict[str, Any]]] = {}
    for cid, _lab, items in packs_by_category():
        rows = [item(s, lab) for s, lab, _h in items]
        for r in rows:
            previews[r["slug"]] = _preview(behavior, r["slug"], mine, labels, loc)
        if cid == behavior:
            main = rows
        else:
            others.append({"label": behavior_label(cid, loc), "packs": rows})
    current = industry if industry in previews else (main[0]["slug"] if main else "")
    labels_by_slug = {r["slug"]: r["label"] for r in main + [p for g in others for p in g["packs"]]}
    return {
        "behavior_label": behavior_label(behavior, loc), "main": main, "others": others,
        "other_selected": bool(industry) and not any(r["selected"] for r in main),
        "current": current, "current_label": labels_by_slug.get(current, ""),
        "preview": previews.get(current, []),
        "data": {"previews": previews, "labels": labels_by_slug,
                 "judge": {"up": t("judge.up", loc), "mid": t("judge.mid", loc), "down": t("judge.down", loc)},
                 "you": t("setupx.ind_you", loc), "bench": t("setupx.ind_bench", loc), "none": t("bench_none", loc),
                 "title_tpl": t("setupx.ind_preview", loc, name="__N__")},
    }
