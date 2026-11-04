"""ダッシュボードを作る — purpose templates → sections of metric cards → add drawer (localStorage).

Catalog = HELP palette (same ids as 指標辞典). Live values filled by ga4.data (/builder/values).
"""

from __future__ import annotations

from typing import Any

from sitekpi.i18n import normalize_locale, t
from sitekpi.metrics.help import palette_widgets
from sitekpi.templating import render

# Sample offline palette (HELP-derived, ja). Kept as WIDGETS for tests / offline.
WIDGETS: list[dict[str, Any]] = palette_widgets(sample=True, locale="ja")

_GROUP_TONES = {
    "layout": "lay",
    "business": "biz",
    "digital": "dig",
    "event": "evt",
    "traffic": "trf",
}

# 目的のひな形: (id, [(section title key, [metric ids])])
TEMPLATES: list[tuple[str, list[tuple[str, list[str]]]]] = [
    ("weekly", [("reach", ["uu", "sessions", "ch_organic_search"]),
                ("results", ["key_events", "session_cvr", "engaged"])]),
    ("ads", [("ads", ["ch_paid_search", "ch_paid_social", "ch_display"]),
             ("results", ["key_events", "session_cvr", "bounce_rate"])]),
    ("funnel", [("funnel", ["ev_view_item", "ev_add_to_cart", "ev_begin_checkout", "ev_purchase",
                            "purchase_cvr", "cart_to_view_rate"])]),
    ("seo", [("search", ["ch_organic_search", "engaged", "pages_session", "avg_time", "bounce_rate"])]),
    ("blank", [("new", [])]),
]
KINDS = ("digital", "event", "traffic", "business")


def fill_sample_values(widgets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Sample mode: events the sample palette leaves at — get the demo packs' counts (EC first),
    so every purpose template shows numbers before GA4 is connected."""
    from sitekpi.packs import DEMO

    counts: dict[str, int] = {}
    for slug, periods in DEMO.items():
        if slug.startswith("type-"):
            for k, v in (periods["28d"].get("event_counts") or {}).items():
                counts.setdefault(k, int(v))
    ec = DEMO.get("type-commerce", {}).get("28d") or {}
    counts.update({k: int(v) for k, v in (ec.get("event_counts") or {}).items()})
    uu = int(ec.get("uu") or 0)
    rates = {}
    if uu and counts.get("purchase"):
        rates["purchase_cvr"] = f"{counts['purchase'] / uu * 100:.1f}%"
    if counts.get("view_item") and counts.get("add_to_cart"):
        rates["cart_to_view_rate"] = f"{counts['add_to_cart'] / counts['view_item'] * 100:.1f}%"
    if counts.get("view_item") and counts.get("purchase"):
        rates["purchase_to_view_rate"] = f"{counts['purchase'] / counts['view_item'] * 100:.1f}%"
    for w in widgets:
        if not _value_is_empty(w.get("value")):
            continue
        ev = w.get("ga4_event")
        if ev and counts.get(ev):
            w["value"] = f"{counts[ev]:,}"
        elif w["id"] in rates:
            w["value"] = rates[w["id"]]
    return widgets


def _templates(loc: str) -> list[dict[str, Any]]:
    return [{
        "id": tid,
        "name": t(f"builderx.tpl.{tid}", loc),
        "desc": t(f"builderx.tpl.{tid}_d", loc),
        "sections": [{"title": t(f"builderx.sec.{key}", loc), "ids": ids} for key, ids in secs],
    } for tid, secs in TEMPLATES]


_COLOR_IDS = ("default", "sky", "blue", "teal", "amber", "rose", "indigo", "slate")


def _value_is_empty(val: Any) -> bool:
    s = str(val if val is not None else "").strip()
    return s in ("", "—", "-", "–", "N/A", "n/a")


def _palette(widgets: list[dict[str, Any]], loc: str) -> list[dict[str, Any]]:
    """Palette groups (layout tools first, then each widget group, collapsed)."""
    groups: list[dict[str, Any]] = [
        {
            "id": "layout",
            "label": t("builder.group.layout", loc),
            "tone": "lay",
            "count": 1,
            "collapsed": False,
            "widgets": [],
        }
    ]
    for gid, tone in _GROUP_TONES.items():
        if gid == "layout":
            continue
        items = [w for w in widgets if w["group"] == gid]
        groups.append(
            {
                "id": gid,
                "label": t(f"builder.group.{gid}", loc),
                "tone": tone,
                "count": len(items),
                "collapsed": True,
                "widgets": [
                    {
                        "id": w["id"],
                        "group": w["group"],
                        "label": w["label"],
                        "hint": w.get("hint") or "",
                        "empty": _value_is_empty(w.get("value")),
                        "display": "—" if _value_is_empty(w.get("value")) else str(w.get("value")),
                    }
                    for w in items
                ],
            }
        )
    return groups


def render_builder(
    *,
    live_values: dict[str, str] | None = None,
    property_name: str = "",
    live_error: str | None = None,
    live_loading: bool = False,
    live_fetch: bool = False,
    widgets: list[dict[str, Any]] | None = None,
    locale: str = "ja",
    rail: dict[str, Any] | None = None,
) -> str:
    loc = normalize_locale(locale)
    source = widgets if widgets is not None else palette_widgets(sample=True, locale=loc)
    catalog: dict[str, Any] = {w["id"]: dict(w) for w in source}
    # Keep legacy sample ids so older localStorage boards still resolve
    for w in WIDGETS:
        catalog.setdefault(w["id"], dict(w))
    if live_values:
        for wid, val in live_values.items():
            if wid in catalog:
                catalog[wid]["value"] = val
                hint = catalog[wid].get("hint") or ""
                if "GA4" not in hint:
                    catalog[wid]["hint"] = (hint + " · GA4").strip(" ·")
    if property_name:
        for meta in catalog.values():
            if meta.get("group") == "business":
                meta["value"] = "—"
                meta["hint"] = t("builder.biz_hint", loc)
    colors = [{"id": cid, "label": t(f"builder.color.{cid}", loc)} for cid in _COLOR_IDS]
    templates = _templates(loc)
    i18n_keys = ("saved", "unsaved", "n_metrics", "add_metric", "heading", "remove", "remove_section",
                 "drawer", "add_x", "no_match", "empty", "sec.new")
    return render(
        "builder.html",
        loc=loc,
        rail=rail,
        property_name=property_name,
        live_error=live_error,
        live_loading=live_loading,
        n_digital=sum(1 for w in source if w.get("group") == "digital"),
        n_event=sum(1 for w in source if w.get("group") == "event"),
        palette=_palette(source, loc),
        templates=templates,
        kinds=[{"id": k, "label": t(f"builder.group.{k}", loc)} for k in KINDS],
        is_sample=not (property_name or live_fetch or live_error),
        builder_data={
            "templates": {tp["id"]: tp["sections"] for tp in templates},
            "order": [w["id"] for w in source],  # tojson sorts keys; the drawer lists in this order
            "i18n": {k.replace("sec.", ""): t(f"builderx.{k}", loc) for k in i18n_keys},
            "catalog": catalog,
            "colors": colors,
            "liveFetch": bool(live_fetch),
            "loadingMsg": t("builder.live_loading", loc),
            "loadedMsg": t("builder.live_loaded", loc),
        },
    )
