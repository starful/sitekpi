"""/policy and /terms (ja/en/ko) on the public layout. ?lang= picks the language (e.g. /policy?lang=en)."""

from __future__ import annotations

import os

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, Response

from sitekpi.i18n import get_locale, normalize_locale, set_locale, t
from sitekpi.i18n.landing_l10n import CONTACT_URL, LANDING
from sitekpi.templating import render
from sitekpi.views.seo import seo_context

router = APIRouter()

_DESC = {
    "policy": {
        "ja": "SiteKPI が集める情報（GA4 は読み取りのみ）、使い方、保存するもの、削除の方法。",
        "en": "What SiteKPI collects (read-only GA4 access), how it is used, what is stored and how to remove it.",
        "ko": "SiteKPI가 수집하는 정보(GA4는 읽기 전용), 이용 방법, 저장하는 것, 삭제 방법.",
    },
    "terms": {
        "ja": "SiteKPI の利用規約。無料・現状のまま提供、業界目安は参考値、禁止事項など。",
        "en": "SiteKPI terms of use: free and provided as is, benchmarks are references, acceptable use.",
        "ko": "SiteKPI 이용약관. 무료·현 상태 제공, 업계 기준은 참고값, 금지 사항 등.",
    },
}


_OP_DEFAULT = {
    "name": {"ja": "SiteKPI 運営者", "en": "the SiteKPI operator", "ko": "SiteKPI 운영자"},
    "address": {"ja": "ご請求があれば遅滞なく開示します", "en": "disclosed without delay on request",
                "ko": "청구가 있으면 지체 없이 공개합니다"},
    "court": {"ja": "運営者の住所地を管轄する地方裁判所", "en": "the district court having jurisdiction over the operator's address",
              "ko": "운영자의 주소지를 관할하는 지방법원"},
}


def operator(loc: str) -> dict[str, str]:
    """Who runs the service (env OPERATOR_NAME / OPERATOR_ADDRESS / LEGAL_COURT; neutral wording until set)."""
    def pick(key: str, env: str) -> str:
        return (os.getenv(env) or "").strip() or _OP_DEFAULT[key][loc]
    court = pick("court", "LEGAL_COURT")
    return {"name": pick("name", "OPERATOR_NAME"), "address": pick("address", "OPERATOR_ADDRESS"),
            "court": court, "court_en": court, "court_ko": court}


def _page(request: Request, kind: str, lang: str) -> HTMLResponse:
    if lang:
        set_locale(request.session, lang)
    loc = get_locale(request.session)
    title = f"{t(f'legal.{kind}', loc)} | SiteKPI"
    return HTMLResponse(render(
        "legal.html",
        loc=loc, c=LANDING[loc], page=kind, connected=bool(request.session.get("ga4_credentials") or request.session.get("ga4_demo")), path=f"/{kind}", lq="" if loc == "ja" else f"?lang={loc}",
        body=f"legal/{kind}_{loc}.html",
        op=operator(loc), contact_url=CONTACT_URL,
        seo=seo_context(path=f"/{kind}", loc=loc, title=title, description=_DESC[kind][loc]),
    ))


@router.get("/policy", response_class=HTMLResponse)
def policy(request: Request, lang: str = Query(default="")):
    return _page(request, "policy", lang)


@router.get("/terms", response_class=HTMLResponse)
def terms(request: Request, lang: str = Query(default="")):
    return _page(request, "terms", lang)


@router.get("/robots.txt", include_in_schema=False)
def robots() -> PlainTextResponse:
    from sitekpi.views.seo import base_url

    return PlainTextResponse(
        "User-agent: *\n"
        "Allow: /$\nAllow: /policy\nAllow: /terms\nAllow: /static/\n"
        "Disallow: /live\nDisallow: /connect\nDisallow: /setup\nDisallow: /builder\n"
        "Disallow: /feedback\nDisallow: /settings\n"
        f"\nSitemap: {base_url()}/sitemap.xml\n"
    )


@router.get("/sitemap.xml", include_in_schema=False)
def sitemap() -> Response:
    from sitekpi.views.seo import LANGS, lang_url

    urls = []
    for path in ("/", "/help", "/policy", "/terms"):
        links = "".join(f'<xhtml:link rel="alternate" hreflang="{lg}" href="{lang_url(path, lg)}"/>' for lg in LANGS)
        for lg in LANGS:
            urls.append(f"<url><loc>{lang_url(path, lg)}</loc>{links}</url>")
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">'
           + "".join(urls) + "</urlset>")
    return Response(xml, media_type="application/xml")
