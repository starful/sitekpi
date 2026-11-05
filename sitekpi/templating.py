"""Jinja2 environment for every page.

- Autoescape is on for .html templates: values are escaped unless explicitly
  marked safe (Markup), so a missed escape() can no longer become XSS.
- `static_url("css/board.css")` appends a content hash (?v=…) so browsers can
  cache static files for a year and still pick up every change.
"""

from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape
from markupsafe import Markup, escape

from sitekpi.i18n import html_lang, t
from sitekpi.i18n.landing_l10n import CONTACT_URL
from sitekpi.views.branding import BRAND_NAME

ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = ROOT / "static"
TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"

_hash_cache: dict[str, tuple[tuple[int, int], str]] = {}


def static_url(path: str) -> str:
    """URL for a file under /static with a content-hash cache buster."""
    file = STATIC_DIR / path
    try:
        st = file.stat()
    except FileNotFoundError:
        return f"/static/{path}"
    stamp = (st.st_mtime_ns, st.st_size)
    hit = _hash_cache.get(path)
    if not hit or hit[0] != stamp:
        # Content + write time: a file rewritten in place always gets a new URL, so a browser
        # that cached a half-written copy (responses are immutable for a year) never reuses it.
        h = hashlib.sha256(file.read_bytes())
        h.update(f"{st.st_mtime_ns}:{st.st_size}".encode())
        hit = (stamp, h.hexdigest()[:12])
        _hash_cache[path] = hit
    return f"/static/{path}?v={hit[1]}"


_GTM_ID = re.compile(r"GTM-[A-Z0-9]{4,12}")


def gtm_id() -> str:
    """Google Tag Manager container from env GTM_ID (set on Cloud Run only, so local runs send nothing)."""
    value = (os.getenv("GTM_ID") or "").strip().upper()
    return value if _GTM_ID.fullmatch(value) else ""


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
env.globals.update(t=t, html_lang=html_lang, static_url=static_url, brand_name=BRAND_NAME, gtm_id=gtm_id,
                   contact_url=lambda: CONTACT_URL)
env.filters["nl2br"] = _nl2br
env.filters["num"] = _num


def render(template: str, **context: Any) -> str:
    return env.get_template(template).render(**context)
