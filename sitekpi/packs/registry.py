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
        meta.update({"slug": vslug, "label": beh["label"]["ja"], "hint": beh["hint"]["ja"],
                     "virtual": True, "rep": rep, "members": members, "logic_as": rep})
        industries[vslug] = meta
        demo[vslug] = demo[rep]
        pack_copy[vslug] = pack_copy[rep]
        benchmarks[vslug] = blended_benchmarks(
            members, benchmarks, [str(industries[m]["label"]) for m in members])

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
