"""Jinja2 environment for every page.

- Autoescape is on for .html templates: values are escaped unless explicitly
  marked safe (Markup), so a missed escape() can no longer become XSS.
- `static_url("css/board.css")` appends a content hash (?v=…) so browsers can
  cache static files for a year and still pick up every change.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape
from markupsafe import Markup, escape

from sitekpi.i18n import html_lang, t
from sitekpi.views.branding import BRAND_NAME

ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = ROOT / "static"
TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"

_hash_cache: dict[str, tuple[float, str]] = {}


def static_url(path: str) -> str:
    """URL for a file under /static with a content-hash cache buster."""
    file = STATIC_DIR / path
    try:
        mtime = file.stat().st_mtime
    except FileNotFoundError:
        return f"/static/{path}"
    hit = _hash_cache.get(path)
    if not hit or hit[0] != mtime:
        digest = hashlib.sha256(file.read_bytes()).hexdigest()[:12]
        hit = (mtime, digest)
        _hash_cache[path] = hit
    return f"/static/{path}?v={hit[1]}"


def _nl2br(text: Any) -> Markup:
    return Markup("<br>").join(escape(line) for line in str(text).split("\n"))


def _num(value: Any) -> str:
    return f"{int(value):,}"


env = Environment(
    loader=FileSystemLoader(str(TEMPLATE_DIR)),
    autoescape=select_autoescape(("html",)),
    undefined=StrictUndefined,
    trim_blocks=True,
    lstrip_blocks=True,
    auto_reload=True,
)
env.globals.update(t=t, html_lang=html_lang, static_url=static_url, brand_name=BRAND_NAME)
env.filters["nl2br"] = _nl2br
env.filters["num"] = _num


def render(template: str, **context: Any) -> str:
    return env.get_template(template).render(**context)
