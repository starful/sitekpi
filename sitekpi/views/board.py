"""KPI board page (dense hierarchy + 説明 popups).

Python here only shapes data: numbers, 業界目安 positions, chart points.
All markup lives in templates/board.html + templates/board/_macros.html,
styles in static/css/board.css, behaviour in static/js/board.js.

Helpers live in board_ctx / board_bench / board_verdict / board_details.
"""

from __future__ import annotations

from typing import Any

from sitekpi.board.data import build_dense_board
from sitekpi.i18n import normalize_locale, t
from sitekpi.templating import render
from sitekpi.views.board_bench import _bench_info, _bench_view
from sitekpi.views.board_ctx import _ACTIVE_BENCH, _ACTIVE_LOCALE
from sitekpi.views.board_details import _details_view, _dialog_v3, _gl_key
from sitekpi.views.board_verdict import _verdict, _watch_items, _worst_link
from sitekpi.views.layout import rail_context

def render_sample_dense(*args: Any, **kwargs: Any) -> str:
    """Render the dense board; 業界目安 for this render are scoped to it."""
    token = _ACTIVE_BENCH.set({})
    loc_token = _ACTIVE_LOCALE.set(normalize_locale(kwargs.get("locale") or "ja"))
    try:
        return _render_sample_dense(*args, **kwargs)
    finally:
        _ACTIVE_LOCALE.reset(loc_token)
        _ACTIVE_BENCH.reset(token)


def _render_sample_dense(
    *,
    industry: str = "hr",
    period: str = "28d",
    property_name: str = "",
    industry_label: str = "",
    industry_note: str = "",
    data: dict[str, Any] | None = None,
    ind: dict[str, Any] | None = None,
    benches_raw: dict[str, dict[str, Any]] | None = None,
    pack_links: list[tuple[str, str]] | list[tuple[str, str, str]] | None = None,
    pack_groups: list[tuple[str, str, list[tuple[str, str, str]]]] | None = None,
    nav_active: str = "",
    connected: dict[str, str] | None = None,
    locale: str = "ja",
    board_kind: str = "sample",
    bench: dict[str, Any] | None = None,
    flow: dict[str, Any] | None = None,
    prev: dict[str, Any] | None = None,
    notice: dict[str, str] | None = None,
    extras: dict[str, Any] | None = None,
    details_src: str = "",
    fragment: bool = False,
    editor: dict[str, Any] | None = None,
    industry_drawer: dict[str, Any] | None = None,
    ind_name: str = "",
    meta_short: str = "",
    auto_open: str = "",
    onb_first_view: bool = False,
) -> str:
    loc = normalize_locale(locale)
    if data is None or ind is None or benches_raw is None:
        from sitekpi.packs import BENCHMARKS, DEMO, INDUSTRIES

        ind = ind or INDUSTRIES[industry]
        data = data or DEMO[industry][period]
        benches_raw = benches_raw or BENCHMARKS[industry]
    if pack_groups is None and pack_links is None:
        from sitekpi.packs import packs_by_category

        pack_groups = packs_by_category()
    nav_active = nav_active or f"pack:{industry}"

    board = build_dense_board(
        industry=industry, period=period, ind=ind, data=data, benches_raw=benches_raw, locale=loc,
        prev=prev,
    )
    _ACTIVE_BENCH.set(board["benches"])
    is_sample = board_kind != "live"

    industry_label = industry_label or board["industry_label"]
    industry_note = industry_note or board["industry_note"]
    if industry_note in ("", "業界パック見本"):
        industry_note = t("sample_meta", loc)
    prop = property_name or board["property_name"]
    period_label = t("period.28d" if period == "28d" else "period.7d", loc)
    # Live boards pass a custom industry_note; avoid a double "(sample)"
    page_title = (
        f"SiteKPI · {industry_label}"
        if industry_note and industry_note != t("sample_meta", loc)
        else f"SiteKPI · {industry_label}{t('sample_title_suffix', loc)}"
    )

    # 詳しい数字 (L2): inline, or loaded after the page by board.js (details_src) when GA4 is slow
    details = None if details_src else _details_view(board, extras, flow, loc)
    if fragment:
        return render("board/details.html", loc=loc, details=details)

    watch = _watch_items(board, loc)
    help_items = board["summary"] + board["funnel"] + board["engage"] + board["audience"]
    seen: set[str] = set()
    dialogs = []
    for r in help_items:
        if r["id"] in seen or not r.get("help"):
            continue
        seen.add(r["id"])
        dialogs.append(_dialog_v3({"id": r["id"], "label": r["label"], "help": r["help"], "gl": _gl_key(r["id"]),
                                   "bench": _bench_view(_bench_info(r.get("value_num"), r.get("bench")))}, loc))
    verdict = _verdict(board, watch, flow, loc)
    story = _story(board, watch, verdict, flow, loc, industry=industry, site=property_name or "",
                   ind_label=ind_name or industry_label, period_label=period_label)
    worst = _worst_link(flow)
    return render(
        "board.html",
        loc=loc,
        rail=rail_context(
            nav_active=nav_active, locale=loc, connected=connected,
            pack_groups=pack_groups, pack_links=pack_links, industry=industry,
        ),
        page_title=page_title,
        industry_label=industry_label,
        pack_meta=f"{industry_note} · {prop} · {period_label}",
        period=period,
        verdict=verdict,
        story=story,
        watch=watch,
        worst=worst,
        details=details,
        details_src=details_src,
        editor=editor,
        industry_drawer=industry_drawer,
        ind_name=ind_name,
        meta_short=meta_short,
        is_sample=is_sample,
        onb_first_view=onb_first_view and board_kind == "live",
        notice=notice,
        bench=bench,
        flow=flow,
        dialogs=dialogs,
        board_data={
            "close": t("close", loc),
            "details_src": details_src,
            "auto_open": auto_open if (editor or industry_drawer) else "",
            "open_tpl": t("detail.open", loc, n="__N__"),
            "close_label": t("detail.close", loc),
            "load_error": t("detail.load_error", loc),
            "retry": t("detail.retry", loc),
        },
    )


def _story(board: dict[str, Any], watch: list[dict[str, Any]], verdict: dict[str, Any],
           flow: dict[str, Any] | None, loc: str, *, industry: str, site: str, ind_label: str,
           period_label: str) -> dict[str, Any] | None:
    """0 総評 → 1 どこで？ → 2 どこがおかしい？ → 3 どうする？ (views/story.py)."""
    from sitekpi.packs import INDUSTRIES
    from sitekpi.packs.behaviors import BEHAVIORS, behavior_label
    from sitekpi.views.story import build_story

    cat = str((INDUSTRIES.get(industry) or {}).get("category") or "")
    beh = behavior_label(cat, loc) if cat in BEHAVIORS else ""
    return build_story(board=board, watch=watch, verdict=verdict, flow=flow, locale=loc, bench_info=_bench_info,
                       site=site, industry_label=ind_label, behavior_label=beh, period_label=period_label)


def verdict_scene(*, industry: str, data: dict[str, Any], benches_raw: dict[str, dict[str, Any]],
                  flow: dict[str, Any] | None, locale: str, prev: dict[str, Any] | None = None) -> dict[str, Any]:
    """The board's 総評 (sentence + 3 tiles, same story as the board) without the page — for the 見本ボード preview.

    It also marks the story's issue in ``flow`` (stage ``in_issue`` and link ``worst``)."""
    from sitekpi.packs import INDUSTRIES

    loc = normalize_locale(locale)
    token = _ACTIVE_BENCH.set({})
    loc_token = _ACTIVE_LOCALE.set(loc)
    try:
        board = build_dense_board(industry=industry, period="28d", ind=INDUSTRIES[industry], data=data,
                                  benches_raw=benches_raw, locale=loc, prev=prev)
        _ACTIVE_BENCH.set(board["benches"])
        watch = _watch_items(board, loc)
        verdict = _verdict(board, watch, flow, loc)
        # the same story as the board: its 総評 sentence, and the issue's stretch marked in the flow
        story = _story(board, watch, verdict, flow, loc, industry=industry, site="", ind_label="", period_label="")
        verdict["story_s1"] = story["s1"] if story else None
        verdict["story_q0"] = story["q"]["q0"] if story else ""
        return verdict
    finally:
        _ACTIVE_LOCALE.reset(loc_token)
        _ACTIVE_BENCH.reset(token)


