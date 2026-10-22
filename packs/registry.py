"""Aggregate pack modules into INDUSTRIES / DEMO / BENCHMARKS / PACK_COPY / EVENT_DESC.

Add a new industry:
  1. Create packs/{slug}.py with PACK = {...}
  2. Append slug to PACK_MODULES below
  3. Restart — /{slug} works automatically
"""

from __future__ import annotations

from importlib import import_module
from typing import Any

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
    mod = import_module(f"packs.{slug}")
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
        benchmarks[slug] = pack["benchmarks"]
        pack_copy[slug] = pack["copy"]
        for k, v in (pack.get("event_desc") or {}).items():
            event_desc[str(k)] = str(v)

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
    """Return raw PACK dict for a slug."""
    return _load_pack(slug)


def pack_links() -> list[tuple[str, str, str]]:
    return [
        (s, str(m["label"]), str(m.get("hint") or ""))
        for s, m in INDUSTRIES.items()
    ]


def packs_by_category() -> list[tuple[str, str, list[tuple[str, str, str]]]]:
    """Return [(category_id, category_label, [(slug, label, hint), ...]), ...] ordered."""
    from packs.catalog import CATEGORIES

    buckets: dict[str, list[tuple[str, str, str]]] = {}
    for slug, meta in INDUSTRIES.items():
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
