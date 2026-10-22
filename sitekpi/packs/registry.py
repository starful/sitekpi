"""Aggregate pack modules into INDUSTRIES / DEMO / BENCHMARKS / PACK_COPY / EVENT_DESC.

Add a new industry:
  1. Create packs/{slug}.py with PACK = {...}
  2. Append slug to PACK_MODULES below
  3. Restart — /{slug} works automatically
"""

from __future__ import annotations

from importlib import import_module
from typing import Any

from sitekpi.packs.sources import apply_sources

# Registration order = sample nav order (within category UI later).
PACK_MODULES: list[str] = [
    "b2c",
    "saas",
    "community",
    "content",
    "news",
    "creator",
    "hr",
    "parttime",
    "agency",
    "construction",
    "ec",
    "marketplace",
    "d2c",
    "b2b",
    "edu",
    "clinic",
    "beauty",
    "finance",
    "travel",
    "realestate",
    "food",
    "gov",
]


def _load_pack(slug: str) -> dict[str, Any]:
    mod = import_module(f"sitekpi.packs.{slug}")
    pack = getattr(mod, "PACK")
    if not isinstance(pack, dict):
        raise TypeError(f"packs.{slug}.PACK must be a dict")
    return pack


def _behavior_demo(base: dict[str, dict[str, Any]], flow: list[str]) -> dict[str, dict[str, Any]]:
    """Sample counts for a behaviour's own flow: narrowing from page views to the main conversion."""
    out: dict[str, dict[str, Any]] = {}
    for period, data in base.items():
        d = dict(data)
        counts = dict(data.get("event_counts") or {})
        uu = int(data.get("uu") or 0)
        known = {"page_view": uu * 0.97, "user_engagement": uu * float(data.get("engaged_rate") or 50) / 100}
        values: list[float | None] = [
            float(counts[ev]) if ev in counts and ev != "page_view" else known.get(ev) for ev in flow
        ]
        if values[-1] is None:
            values[-1] = float(max(int(data.get("signups") or 0), 1))
        # fill the gaps geometrically between the known neighbours
        i = 0
        while i < len(values):
            if values[i] is None:
                j = i
                while values[j] is None:
                    j += 1
                a = values[i - 1] if i else uu * 0.97
                b = values[j]
                for k in range(i, j):
                    values[k] = a * (b / a) ** ((k - i + 1) / (j - i + 1)) if a else 0.0
                i = j
            i += 1
        for ev, v in zip(flow, values):
            if ev not in counts or ev == "page_view":
                counts[ev] = round(v or 0)
        d["event_counts"] = counts
        out[period] = d
    return out


def build_registry() -> dict[str, Any]:
    industries: dict[str, dict[str, Any]] = {}
    demo: dict[str, dict[str, dict[str, Any]]] = {}
    benchmarks: dict[str, dict[str, dict[str, Any]]] = {}
    pack_copy: dict[str, dict[str, Any]] = {}
    event_desc: dict[str, str] = {}

    for slug in PACK_MODULES:
        pack = _load_pack(slug)
        meta = dict(pack["meta"])
        meta.setdefault("slug", slug)
        industries[slug] = meta
        demo[slug] = pack["demo"]
        # cited 業界目安 (packs/sources.py) replace SiteKPI defaults where a source matches
        benchmarks[slug] = apply_sources(slug, pack["benchmarks"])
        pack_copy[slug] = pack["copy"]
        for k, v in (pack.get("event_desc") or {}).items():
            event_desc[str(k)] = str(v)

    # Packs derived from a base pack for industries with a published benchmark
    from sitekpi.packs.derived import DERIVED, scaled_demo

    for dslug, spec in DERIVED.items():
        base = spec["base"]
        meta = dict(industries[base])
        meta.update({"slug": dslug, "label": spec["label"]["ja"], "hint": spec["hint"]["ja"],
                     "category": spec["category"], "derived": True, "logic_as": base})
        industries[dslug] = meta
        demo[dslug] = scaled_demo(demo[base], float(spec.get("scale") or 1.0))
        bcopy = dict(pack_copy[base])
        bcopy["property"] = f"{spec['label']['ja']} Demo"
        pack_copy[dslug] = bcopy
        benchmarks[dslug] = apply_sources(dslug, _load_pack(base)["benchmarks"])

    # 行動タイプ packs (type-<category>): behaviour chosen, industry skipped
    from sitekpi.packs.behaviors import BEHAVIORS, blended_benchmarks, slug_of

    for cat, beh in BEHAVIORS.items():
        members = [s for s, m in industries.items() if m.get("category") == cat and not m.get("virtual")]
        rep = beh["rep"]
        vslug = slug_of(cat)
        meta = dict(industries[rep])
        flow = list(beh["flow"])
        board = beh.get("board")
        meta.update({"slug": vslug, "label": beh["label"]["ja"], "hint": beh["hint"]["ja"],
                     "virtual": True, "rep": rep, "members": members,
                     "logic_as": "edu" if board else rep,  # edu = primary ÷ mid, primary ÷ bottom
                     "events": flow + [e for e in meta.get("events") or [] if e not in flow]})
        bcopy = dict(pack_copy[rep])
        if board:
            meta["primary_event"] = board["primary"]
            meta["signup_label"] = board["signup_label"]["ja"]
            bcopy.update({"mid_event": board["mid"], "bottom_event": board["bottom"],
                          **{k: board[k]["ja"] for k in ("cvr_label", "mid_label", "bottom_label",
                                                         "rate_a_label", "rate_b_label")}})
        industries[vslug] = meta
        demo[vslug] = _behavior_demo(demo[rep], flow)
        pack_copy[vslug] = bcopy
        if members:
            benchmarks[vslug] = blended_benchmarks(
                members, benchmarks, [str(industries[m]["label"]) for m in members])
        else:  # a behaviour no industry pack belongs to (e.g. blog): site-wide standards only
            from sitekpi.packs.behaviors import SHARED_METRICS

            benchmarks[vslug] = {k: dict(v) for k, v in benchmarks[rep].items()
                                 if k in SHARED_METRICS and k != "signup_rate"}

    return {
        "INDUSTRIES": industries,
        "DEMO": demo,
        "BENCHMARKS": benchmarks,
        "PACK_COPY": pack_copy,
        "EVENT_DESC": event_desc,
    }


_REG = build_registry()
INDUSTRIES: dict[str, dict[str, Any]] = _REG["INDUSTRIES"]
DEMO: dict[str, dict[str, dict[str, Any]]] = _REG["DEMO"]
BENCHMARKS: dict[str, dict[str, dict[str, Any]]] = _REG["BENCHMARKS"]
PACK_COPY: dict[str, dict[str, Any]] = _REG["PACK_COPY"]
EVENT_DESC: dict[str, str] = _REG["EVENT_DESC"]


def get_pack(slug: str) -> dict[str, Any]:
    """Return raw PACK dict for a slug (a derived pack returns its base)."""
    from sitekpi.packs.derived import base_of

    return _load_pack(base_of(slug))


def pack_links() -> list[tuple[str, str, str]]:
    return [
        (s, str(m["label"]), str(m.get("hint") or ""))
        for s, m in INDUSTRIES.items()
        if not m.get("virtual")
    ]


def packs_by_category() -> list[tuple[str, str, list[tuple[str, str, str]]]]:
    """Return [(category_id, category_label, [(slug, label, hint), ...]), ...] ordered."""
    from sitekpi.packs.catalog import CATEGORIES

    buckets: dict[str, list[tuple[str, str, str]]] = {}
    for slug, meta in INDUSTRIES.items():
        if meta.get("virtual"):
            continue
        cat = str(meta.get("category") or "lead")
        buckets.setdefault(cat, []).append(
            (slug, str(meta["label"]), str(meta.get("hint") or ""))
        )

    ordered_cats = sorted(
        CATEGORIES.items(),
        key=lambda kv: int(kv[1].get("order") or 999),
    )
    out: list[tuple[str, str, list[tuple[str, str, str]]]] = []
    for cid, cmeta in ordered_cats:
        items = buckets.pop(cid, [])
        if items:
            out.append((cid, str(cmeta.get("label") or cid), items))
    # Any unknown category ids last
    for cid, items in buckets.items():
        out.append((cid, cid, items))
    return out
