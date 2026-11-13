"""Public-page SEO: absolute URLs, canonical + hreflang (?lang=), Open Graph, JSON-LD."""

from __future__ import annotations

import json
import os
from typing import Any

from markupsafe import Markup

LANGS = ("ja", "en", "ko")
DEFAULT_LANG = "ja"
OG_LOCALE = {"ja": "ja_JP", "en": "en_US", "ko": "ko_KR"}


def base_url() -> str:
    return (os.getenv("APP_BASE_URL") or "http://127.0.0.1:8766").rstrip("/")


def lang_url(path: str, loc: str) -> str:
    """ja is the default (no ?lang=); en / ko carry ?lang=."""
    return base_url() + path + ("" if loc == DEFAULT_LANG else f"?lang={loc}")


def ping_search_console() -> None:
    """Best-effort: tell Google a new sitemap is live. Fires once per app start (new Cloud Run
    revision = new deploy); skipped in dev/tests since base_url() stays on 127.0.0.1 there.
    Set GSC_PING_ON_DEPLOY=0 to disable. Never raises: network failure must not block startup."""
    if (os.getenv("GSC_PING_ON_DEPLOY") or "1") == "0":
        return
    url = base_url()
    if "127.0.0.1" in url or "localhost" in url:
        return

    def _ping() -> None:
        import urllib.request

        try:
            urllib.request.urlopen(f"https://www.google.com/ping?sitemap={url}/sitemap.xml", timeout=5)
        except Exception:
            pass

    import threading

    threading.Thread(target=_ping, daemon=True).start()


def seo_context(*, path: str, loc: str, title: str, description: str,
                image: str = "/static/img/og.png", jsonld: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return {
        "title": title,
        "description": description,
        "canonical": lang_url(path, loc),
        "alternates": [{"hreflang": lg, "href": lang_url(path, lg)} for lg in LANGS]
        + [{"hreflang": "x-default", "href": lang_url(path, DEFAULT_LANG)}],
        "og_locale": OG_LOCALE.get(loc, "ja_JP"),
        "image": base_url() + image,
        "jsonld": [Markup(json.dumps(j, ensure_ascii=False).replace("</", "<\\/")) for j in (jsonld or [])],
    }
