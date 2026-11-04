"""指標辞典 — HELP catalog as open cards: compact grid, one card opens to a full row."""

from __future__ import annotations

from typing import Any

from sitekpi.i18n import normalize_locale, t
from sitekpi.metrics.help import get_help, localized_kinds, ordered_keys
from sitekpi.stickers import sticker_for
from sitekpi.templating import render

# help ids whose number the board judges against an 業界目安 (the rest are counts / mixes)
BENCHED = frozenset({
    "signup_cvr", "session_cvr", "purchase_cvr", "lead_cvr", "apply_cvr", "booking_cvr",
    "engaged", "bounce_rate", "pages_session", "pages_per_uu", "new_return", "sessions_per_uu",
    "signup_to_pay", "paid_rate", "churn_rate",
})


def render_glossary(*, locale: str, rail: dict[str, Any]) -> str:
    loc = normalize_locale(locale)
    kinds = localized_kinds(loc)
    by_kind: dict[str, list[dict[str, Any]]] = {k: [] for k in kinds}
    for key in ordered_keys():
        h = get_help(key, loc)
        if not h:
            continue
        kind = str(h.get("kind") or "digital")
        hint = str(h.get("hint") or "").strip()
        if not hint:
            hint = str(h.get("meaning") or "").split("\n", 1)[0].strip()
        entry: dict[str, Any] = {
            "id": key,
            "title": h["title"],
            "meaning": h["meaning"],
            "formula": h["formula"],
            "tip": h["tip"],
            "hint": hint,
            "sticker": sticker_for(key),
            "bench": key in BENCHED,
            "kind": kind,
        }
        by_kind.setdefault(kind, []).append(entry)
    groups = []
    total = 0
    for kind, meta in kinds.items():
        items = by_kind.get(kind) or []
        if not items:
            continue
        total += len(items)
        groups.append({
            "id": kind,
            "label": meta["label"],
            "short": meta.get("short") or meta["label"],
            "desc": meta["desc"],
            "entries": items,
            "count": len(items),
        })
    return render(
        "glossary.html",
        loc=loc,
        rail=rail,
        groups=groups,
        total=total,
        title=t("glossary.title", loc),
        kicker=t("glossary.kicker", loc),
        lead=t("glossary.lead", loc),
        k_meaning=t("glossary.meaning", loc),
        k_formula=t("glossary.formula", loc),
        k_tip=t("glossary.tip", loc),
        search_ph=t("glossary.search_ph", loc),
        search_empty=t("glossary.search_empty", loc),
        filter_all=t("glossary.filter_all", loc),
        filter_label=t("glossary.filter_label", loc),
        bench_yes=t("glossary.bench_yes", loc),
        bench_no=t("glossary.bench_no", loc),
        to_board=t("glossary.to_board", loc),
    )
