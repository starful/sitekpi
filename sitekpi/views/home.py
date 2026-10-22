"""Home page."""

from __future__ import annotations

from sitekpi.packs import INDUSTRIES
from sitekpi.templating import render


def render_home() -> str:
    packs = [
        {"slug": slug, "label": meta["label"], "blurb": meta["blurb"]}
        for slug, meta in INDUSTRIES.items()
    ]
    # Home is Japanese-only for now (redesign is step 11)
    return render("home.html", loc="ja", packs=packs)
