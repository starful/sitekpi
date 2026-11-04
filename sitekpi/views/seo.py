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
