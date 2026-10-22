"""目安を調整 — view / save / reset 自社目安 for a pack."""

from __future__ import annotations

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from sitekpi.benchmarks import effective_benchmarks, get_store, load_effective, parse_range, scope_for
from sitekpi.i18n import get_locale
from sitekpi.packs import BENCHMARKS, INDUSTRIES
from sitekpi.routes.nav import nav_rail_context
from sitekpi.views.benchmarks import render_benchmarks_page

router = APIRouter(tags=["benchmarks"])


def _resolve(request: Request, pack: str, board: str) -> tuple[str, str]:
    """Live edits are only for the connected property's pack; everything else is sample scope."""
    session = request.session
    live_ok = bool(session.get("ga4_credentials") and session.get("ga4_property"))
    live_pack = str(session.get("benchmark_pack") or "")
    if board == "live" and live_ok and live_pack in INDUSTRIES:
        return live_pack, "live"
    if pack not in INDUSTRIES:
        pack = live_pack if live_pack in INDUSTRIES else "hr"
    return pack, "sample"


def _page(request: Request, pack: str, board: str, **kw) -> str:
    prop = request.session.get("ga4_property") or {}
    return render_benchmarks_page(
        pack=pack,
        board=board,
        effective=kw.pop("effective", None)
        or load_effective(request.session, pack, BENCHMARKS[pack], live=board == "live"),
        locale=get_locale(request.session),
        rail=nav_rail_context(request, "benchmarks"),
        property_name=str(prop.get("name") or "") if board == "live" else "",
        **kw,
    )


@router.get("/benchmarks", response_class=HTMLResponse)
def benchmarks_page(
    request: Request,
    pack: str = Query(default=""),
    board: str = Query(default="sample"),
    saved: int = Query(default=0),
    reset: int = Query(default=0),
):
    pack, board = _resolve(request, pack, board)
    flash = "bench_edit.saved" if saved else "bench_edit.was_reset" if reset else ""
    return HTMLResponse(_page(request, pack, board, flash=flash))


@router.post("/benchmarks")
async def benchmarks_save(request: Request):
    form = await request.form()
    pack, board = _resolve(request, str(form.get("pack") or ""), str(form.get("board") or "sample"))
    defaults = BENCHMARKS[pack]
    values: dict[str, tuple[float, float]] = {}
    to_default: list[str] = []
    errors: dict[str, str] = {}
    raw: dict[str, tuple[str, str]] = {}
    for key, spec in defaults.items():
        lo, hi = str(form.get(f"low_{key}", "")), str(form.get(f"high_{key}", ""))
        raw[key] = (lo, hi)
        parsed = parse_range(lo, hi, str(spec.get("unit", "")))
        if isinstance(parsed, str):
            errors[key] = parsed
        elif parsed == (float(spec["low"]), float(spec["high"])):
            to_default.append(key)  # same as default → no override
        else:
            values[key] = parsed
    if errors:
        scope = scope_for(request.session, live=board == "live")
        current = get_store().get(scope, pack) if scope else {}
        html = _page(
            request, pack, board, errors=errors, form=raw,
            effective=effective_benchmarks(defaults, current),
        )
        return HTMLResponse(html, status_code=400)
    scope = scope_for(request.session, live=board == "live", create=True)
    store = get_store()
    if values:
        store.set_many(scope, pack, values)
    for key in to_default:
        store.reset(scope, pack, key)
    return RedirectResponse(f"/benchmarks?pack={pack}&board={board}&saved=1", status_code=303)


@router.post("/benchmarks/reset")
async def benchmarks_reset(request: Request):
    form = await request.form()
    pack, board = _resolve(request, str(form.get("pack") or ""), str(form.get("board") or "sample"))
    metric = str(form.get("metric") or "")
    scope = scope_for(request.session, live=board == "live")
    if scope:
        get_store().reset(scope, pack, metric if metric in BENCHMARKS[pack] else None)
    return RedirectResponse(f"/benchmarks?pack={pack}&board={board}&reset=1", status_code=303)
