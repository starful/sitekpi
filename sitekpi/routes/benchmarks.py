"""自社目安 — save / reset from the board's popover (JSON for fetch, redirect otherwise)."""

from __future__ import annotations

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse, RedirectResponse, Response

from sitekpi.benchmarks import get_store, parse_range, scope_for
from sitekpi.i18n import get_locale, t
from sitekpi.packs import BENCHMARKS, INDUSTRIES

router = APIRouter(tags=["benchmarks"])


def resolve(session, pack: str, board: str) -> tuple[str, str]:
    """Live edits are only for the connected property's pack; everything else is sample scope."""
    live_ok = bool(session.get("ga4_credentials") and session.get("ga4_property"))
    live_pack = str(session.get("benchmark_pack") or "")
    if board == "live" and live_ok and live_pack in INDUSTRIES:
        return live_pack, "live"
    if pack not in INDUSTRIES:
        pack = live_pack if live_pack in INDUSTRIES else "hr"
    return pack, "sample"


def _board_url(pack: str, board: str) -> str:
    return "/live" if board == "live" else f"/{pack}"


def _wants_json(request: Request) -> bool:
    return "application/json" in (request.headers.get("accept") or "")


@router.get("/benchmarks")
def benchmarks_legacy(pack: str = Query(default=""), board: str = Query(default="sample")):
    """The page became a popover on the board — send old links there."""
    if pack not in INDUSTRIES:
        pack = "hr"
    return RedirectResponse(_board_url(pack, board) + "#bench", status_code=302)


@router.post("/benchmarks")
async def benchmarks_save(request: Request) -> Response:
    form = await request.form()
    pack, board = resolve(request.session, str(form.get("pack") or ""), str(form.get("board") or "sample"))
    loc = get_locale(request.session)
    defaults = BENCHMARKS[pack]
    values: dict[str, tuple[float, float]] = {}
    to_default: list[str] = []
    errors: dict[str, str] = {}
    for key, spec in defaults.items():
        lo, hi = form.get(f"low_{key}"), form.get(f"high_{key}")
        if lo is None and hi is None:
            continue  # field not sent → leave as is
        parsed = parse_range(str(lo or ""), str(hi or ""), str(spec.get("unit", "")))
        if isinstance(parsed, str):
            errors[key] = t(parsed, loc)
        elif parsed == (float(spec["low"]), float(spec["high"])):
            to_default.append(key)  # same as default → no override
        else:
            values[key] = parsed
    if errors:
        if _wants_json(request):
            return JSONResponse({"ok": False, "errors": errors}, status_code=400)
        return RedirectResponse(_board_url(pack, board) + "#bench", status_code=303)
    scope = scope_for(request.session, live=board == "live", create=True)
    store = get_store()
    if values:
        store.set_many(scope, pack, values)
    for key in to_default:
        store.reset(scope, pack, key)
    if _wants_json(request):
        return JSONResponse({"ok": True, "saved": sorted(values), "reset": sorted(to_default)})
    return RedirectResponse(_board_url(pack, board), status_code=303)


@router.post("/benchmarks/reset")
async def benchmarks_reset(request: Request) -> Response:
    form = await request.form()
    pack, board = resolve(request.session, str(form.get("pack") or ""), str(form.get("board") or "sample"))
    metric = str(form.get("metric") or "")
    scope = scope_for(request.session, live=board == "live")
    if scope:
        get_store().reset(scope, pack, metric if metric in BENCHMARKS[pack] else None)
    if _wants_json(request):
        return JSONResponse({"ok": True})
    return RedirectResponse(_board_url(pack, board), status_code=303)
