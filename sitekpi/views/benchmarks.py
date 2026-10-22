"""目安を調整 page — view model."""

from __future__ import annotations

from typing import Any

from sitekpi.board.data import build_dense_board
from sitekpi.i18n import normalize_locale, t
from sitekpi.i18n.pack_l10n import pack_text
from sitekpi.packs import BENCHMARKS, DEMO, INDUSTRIES, packs_by_category
from sitekpi.templating import render

# Benchmarks only used once business data (DB) is linked
BIZ_KEYS = ("paid_rate", "churn_rate")


def _fmt(v: float) -> str:
    return f"{v:g}"


def metric_labels(pack: str, locale: str) -> dict[str, str]:
    """Spoken metric name per benchmark key, as the board shows it for this pack."""
    board = build_dense_board(
        industry=pack, period="28d", ind=INDUSTRIES[pack], data=DEMO[pack]["28d"],
        benches_raw=BENCHMARKS[pack], locale=locale,
    )
    labels: dict[str, str] = {}
    for r in board["summary"] + board["funnel"] + board["engage"] + board["audience"] + board["business"]:
        key = r.get("bench")
        if key and key not in labels:
            labels[key] = str(r["label"])
    return labels


def render_benchmarks_page(
    *,
    pack: str,
    board: str,
    effective: dict[str, dict[str, Any]],
    locale: str,
    rail: dict[str, Any] | None,
    property_name: str = "",
    flash: str = "",
    errors: dict[str, str] | None = None,
    form: dict[str, tuple[str, str]] | None = None,
) -> str:
    loc = normalize_locale(locale)
    labels = metric_labels(pack, loc)
    errors = errors or {}
    form = form or {}
    groups: dict[str, list[dict[str, Any]]] = {"ga4": [], "biz": []}
    for key, spec in effective.items():
        low, high = form.get(key, (_fmt(spec["low"]), _fmt(spec["high"])))
        groups["biz" if key in BIZ_KEYS else "ga4"].append(
            {
                "key": key,
                "label": labels.get(key, key),
                "unit": spec.get("unit", ""),
                "higher": bool(spec["higher_is_better"]),
                "default": f"{_fmt(spec['default_low'])}–{_fmt(spec['default_high'])}{spec.get('unit', '')}",
                "low": low,
                "high": high,
                "custom": bool(spec.get("custom")),
                "error": t(errors[key], loc) if key in errors else "",
            }
        )
    packs = [
        {
            "group": t(f"cat.{cid}", loc) if not t(f"cat.{cid}", loc).startswith("cat.") else label,
            "packs": [{"slug": s, "label": pack_text(s, "label", loc, lab)} for s, lab, _ in items],
        }
        for cid, label, items in packs_by_category()
    ]
    return render(
        "benchmarks.html",
        loc=loc,
        rail=rail,
        pack=pack,
        pack_label=pack_text(pack, "label", loc, str(INDUSTRIES[pack]["label"])),
        packs=packs,
        board=board,
        property_name=property_name,
        groups=[
            {"title": t("bench_edit.group_ga4", loc), "rows": groups["ga4"]},
            {"title": t("bench_edit.group_biz", loc), "rows": groups["biz"]},
        ],
        flash=flash,
        has_errors=bool(errors),
        back_href="/live" if board == "live" else f"/{pack}",
    )
