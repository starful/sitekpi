"""/policy and /terms (ja/en/ko). ?lang= overrides the UI language (e.g. /policy?lang=en for reviewers)."""

from __future__ import annotations

import os

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse

from sitekpi.i18n import get_locale, normalize_locale, t
from sitekpi.routes.nav import nav_rail_context
from sitekpi.templating import render

router = APIRouter()


def _page(request: Request, kind: str, lang: str) -> HTMLResponse:
    loc = normalize_locale(lang) if lang else get_locale(request.session)
    return HTMLResponse(render(
        "legal.html",
        loc=loc,
        rail=nav_rail_context(request, kind),
        title=t(f"legal.{kind}", loc),
        body=f"legal/{kind}_{loc}.html",
        contact=(os.getenv("CONTACT_EMAIL") or "").strip(),
        kind=kind,
    ))


@router.get("/policy", response_class=HTMLResponse)
def policy(request: Request, lang: str = Query(default="")):
    return _page(request, "policy", lang)


@router.get("/terms", response_class=HTMLResponse)
def terms(request: Request, lang: str = Query(default="")):
    return _page(request, "terms", lang)
