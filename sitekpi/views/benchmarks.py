"""業界目安 popovers (on the board) — view model."""

from __future__ import annotations

from typing import Any

from sitekpi.board.data import build_dense_board
from sitekpi.i18n import t
from sitekpi.i18n.pack_l10n import pack_text
from sitekpi.packs import BENCHMARKS, DEMO, INDUSTRIES

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


def bench_context(
    *,
    pack: str,
    board: str,
    effective: dict[str, dict[str, Any]],
    locale: str,
    property_name: str = "",
    labels_from: str = "",
) -> dict[str, Any]:
    labels = metric_labels(labels_from or pack, locale)  # metric names as the board words them
    groups: dict[str, list[dict[str, Any]]] = {"ga4": [], "biz": []}
    for key, spec in effective.items():
        unit = spec.get("unit", "")
        groups["biz" if key in BIZ_KEYS else "ga4"].append(
            {
                "key": key,
                "label": labels.get(key, key),
                "unit": unit,
                "higher": bool(spec["higher_is_better"]),
                "default": f"{_fmt(spec['default_low'])}–{_fmt(spec['default_high'])}{unit}",
                "source": spec.get("source") or {"kind": "provisional", "label": "", "url": ""},
                "low": _fmt(spec["low"]),
                "high": _fmt(spec["high"]),
                "custom": bool(spec.get("custom")),
            }
        )
    return {
        "pack": pack,
        "board": board,
        "pack_label": pack_text(pack, "label", locale, str(INDUSTRIES[pack]["label"])),
        "property_name": property_name,
        "groups": [
            g for g in (
                {"title": t("bench_edit.group_ga4", locale), "rows": groups["ga4"]},
                {"title": t("bench_edit.group_biz", locale), "rows": groups["biz"]},
            ) if g["rows"]
        ],
    }
