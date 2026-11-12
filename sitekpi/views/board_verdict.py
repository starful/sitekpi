"""L0 いまの状態 and L1 今見るべきこと view models (no HTML).

L0 = one-sentence verdict + 3 tiles (主転換 · 主転換率 · 一番の課題).
今見るべきこと = up to WATCH_MAX metrics furthest outside 業界目安 (worse first);
when none are off, the section says so — do not fill with filler tips.
"""

from __future__ import annotations

from markupsafe import Markup
from typing import Any

from sitekpi.i18n import t
from sitekpi.views.board_bench import _bench_info, _bench_view
from sitekpi.views.board_ctx import _kind_label

# --- 今見るべきこと (rule-based until step 10) -------------------------------

WATCH_MAX = 3


def _trend(r: dict[str, Any], locale: str) -> dict[str, str] | None:
    """自社の前期比 next to the 業界目安 judgement: 改善 / 悪化 / 横ばい."""
    delta, tone = str(r.get("delta") or "—"), str(r.get("tone") or "na")
    if delta == "—" or tone == "na":
        return None
    word = {"up": "trend.better", "down": "trend.worse"}.get(tone, "trend.flat")
    return {"text": delta, "tone": tone, "word": t(word, locale)}


def _watch_items(board: dict[str, Any], locale: str) -> list[dict[str, Any]]:
    """Metrics furthest outside their 業界目安: worse ones first, then better ones."""
    seen: set[str] = set()
    scored: list[tuple[int, float, dict[str, Any]]] = []
    for r in board["summary"] + board["funnel"] + board["engage"] + board["audience"]:
        key = str(r.get("bench") or "")
        if not key or key in seen:
            continue
        info = _bench_info(r.get("value_num"), key)
        if not info or info.get("value") is None or info["tone"] not in ("up", "down"):
            continue
        seen.add(key)
        v, low, high = float(info["value"]), float(info["low"]), float(info["high"])
        outside = (low - v) if v < low else (v - high)
        severity = outside / max(high - low, 1e-9)
        bad = info["tone"] == "down"
        if bad:
            title = t("watch.bad", locale, label=r["label"],
                      dir=t("watch.dir_high" if v > high else "watch.dir_low", locale))
            tip = str((r.get("help") or {}).get("tip") or "")
        else:
            title = t("watch.good", locale, label=r["label"])
            tip = t("watch.keep", locale)
        scored.append(
            (
                0 if bad else 1,
                -severity,
                {
                    "id": r["id"],
                    "label": r["label"],
                    "value": r["value"],
                    "value_num": r.get("value_num"),
                    "bench_key": key,
                    "delta": str(r.get("delta") or "—"),
                    "delta_tone": str(r.get("tone") or "na"),
                    "tone": info["tone"],
                    "title": title,
                    "avg": info["avg"],
                    "band": info["band"],
                    "rg": info.get("rg"),
                    "numbers": t("watch.numbers", locale, value=r["value"], avg=info["avg"],
                                 band=info["band"], gap=info["gap"]),
                    "trend": _trend(r, locale),
                    "tip": tip,
                    # far outside the band (more than its own width) → maybe the wrong 比べる業種
                    "far": severity >= 1.0,
                },
            )
        )
    scored.sort(key=lambda x: (x[0], x[1]))
    return [item for _, _, item in scored[:WATCH_MAX]]


# --- いまの状態 (L0): one sentence + three numbers ---------------------------


def _prev_view(delta: str, tone: str, locale: str) -> dict[str, str]:
    """自社の前期比 in words (改善 / 悪化 / 横ばい) with the number beside it."""
    delta = str(delta or "—")
    if delta == "—":
        return {"word": t("verdict.prev_none", locale), "text": "", "tone": "na"}
    word = {"up": "trend.better", "down": "trend.worse"}.get(tone, "trend.flat")
    return {"word": t(word, locale), "text": delta, "tone": tone if tone in ("up", "down") else "mid"}


def _tile(*, label: str, tag: str, value: str, delta: str, tone: str,
          info: dict[str, Any] | None, locale: str, note: str = "", help_id: str = "",
          issue: bool = False) -> dict[str, Any]:
    return {
        "label": label, "tag": tag, "value": value, "help_id": help_id, "issue": issue,
        "prev": _prev_view(delta, tone, locale),
        "bench": _bench_view(info),
        "note": note,
    }


def _worst_link(flow: dict[str, Any] | None) -> dict[str, Any] | None:
    for st in (flow or {}).get("stages") or []:
        link = st.get("link")
        if link and link.get("worst"):
            return link
    return None


def _verdict(board: dict[str, Any], watch: list[dict[str, Any]],
             flow: dict[str, Any] | None, locale: str) -> dict[str, Any]:
    """L0: 主転換の件数 · 主転換率 · 一番の課題 — each with 前期 and 業界 in words."""
    by_id = {r["id"]: r for r in board["summary"]}
    lines: list[str] = []
    short: list[str] = []
    tiles: list[dict[str, Any]] = []

    count = by_id.get("primary")
    if count:
        delta, tone = str(count.get("delta") or "—"), str(count.get("tone") or "na")
        key = ("verdict.count_na" if delta == "—"
               else {"up": "verdict.count_up", "down": "verdict.count_down"}.get(tone, "verdict.count_flat"))
        lines.append(t(key, locale, label=count["label"], value=count["value"], delta=delta))
        short.append(t("bx." + key.split(".", 1)[1], locale, label=count["label"], value=count["value"]))
        tiles.append(_tile(label=count["label"], tag=t("primary_tag", locale), value=count["value"],
                           delta=delta, tone=tone, info=None, locale=locale, help_id=count["id"],
                           note=t("verdict.count_note", locale)))

    rate = by_id.get("signup_cvr")
    if rate:
        info = _bench_info(rate.get("value_num"), rate.get("bench"))
        view = _bench_view(info)
        key = (f"verdict.rate_{view['judge']}" if view["kind"] == "judge" and view["judge"]
               else "verdict.rate_none")
        lines.append(t(key, locale, label=rate["label"], value=rate["value"], avg=view["avg"]))
        tiles.append(_tile(label=rate["label"], tag="", value=rate["value"],
                           delta=str(rate.get("delta") or "—"), tone=str(rate.get("tone") or "na"),
                           info=info, locale=locale, help_id=rate["id"]))

    # 一番の課題: the worst metric outside its 目安 — not the rate already shown in tile 2
    rate_key = str((rate or {}).get("bench") or "")
    bad = next((w for w in watch if w["tone"] == "down" and w["bench_key"] != rate_key), None)
    link = _worst_link(flow)
    if bad:
        info = _bench_info(bad.get("value_num"), bad["bench_key"])
        lines.append(t("verdict.issue_bench", locale, label=bad["label"], value=bad["value"],
                       avg=(info or {}).get("avg", "—")))
        short.append(t("bx.issue", locale, label=bad["label"], value=bad["value"], avg=(info or {}).get("avg", "—")))
        tiles.append(_tile(label=bad["label"], tag=t("verdict.issue_k", locale), value=bad["value"],
                           delta=bad["delta"], tone=bad["delta_tone"], info=info, locale=locale,
                           help_id=bad["id"], issue=True))
    elif link and link.get("drop_num") is not None:
        lines.append(t("verdict.issue_flow", locale, a=link["from"], b=link["to"], drop=link["drop"]))
        short.append(t("bx.issue_flow", locale, a=link["from"], b=link["to"], drop=link["drop"]))
        tiles.append(_tile(label=t("verdict.link", locale, a=link["from"], b=link["to"]),
                           tag=t("verdict.issue_k", locale), value=link["go"]["all"],
                           delta="—", tone="na", info=None, locale=locale, issue=True,
                           note=t("verdict.issue_flow_note", locale, drop=link["drop"])))
    else:
        lines.append(t("verdict.issue_none", locale))
        short.append(t("bx.issue_none", locale))
        eng = by_id.get("engaged")
        if eng:
            tiles.append(_tile(label=eng["label"], tag="", value=eng["value"],
                               delta=str(eng.get("delta") or "—"), tone=str(eng.get("tone") or "na"),
                               info=_bench_info(eng.get("value_num"), eng.get("bench")),
                               locale=locale, help_id=eng["id"]))
    joiner = "" if locale == "ja" else " "
    sep = t("bx.sep", locale)
    short_text = (short[0] + sep + short[1]) if len(short) > 1 else "".join(short)
    # v5: the issue's name in orange inside the sentence; its tile says （いちばんの課題） in the label
    hl = ""
    for k in tiles:
        if k["issue"]:
            hl = k["label"]
            k["label"] = k["label"] + t("bx.issue_suffix", locale)
    return {"text": joiner.join(lines), "short": short_text, "short_html": _highlight(short_text, hl),
            "tiles": tiles, "lead": (short[0] + sep) if count and short else "", "no_issue": not hl}


def _highlight(text: str, part: str) -> Markup:
    from markupsafe import escape

    safe = escape(text)
    if not part or str(escape(part)) not in str(safe):
        return Markup(safe)
    return Markup(str(safe).replace(str(escape(part)), f'<span class="v-issue">{escape(part)}</span>', 1))


def _dialog(item: dict[str, Any], locale: str) -> dict[str, str]:
    h = item["help"]
    return {
        "id": item["id"],
        "kind": _kind_label(h["kind"], locale),
        "title": h["title"],
        "meaning": h["meaning"],
        "formula": h["formula"],
        "tip": h["tip"],
    }

