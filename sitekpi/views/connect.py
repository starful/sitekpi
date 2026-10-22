"""GA4 connect page: Google → property (then サイトの設定: /setup)."""

from __future__ import annotations

from typing import Any

from sitekpi.ga4.oauth import base_url, redirect_uri
from sitekpi.i18n import normalize_locale
from sitekpi.templating import render


def render_connect_page(
    *,
    configured: bool,
    connected: bool,
    demo: bool,
    email: str,
    properties: list[dict[str, str]],
    selected: dict[str, str] | None,
    error: str | None,
    libs_ok: bool,
    setup: dict[str, Any] | None = None,
    locale: str = "ja",
    rail: dict[str, Any] | None = None,
) -> str:
    loc = normalize_locale(locale)
    return render(
        "connect.html",
        loc=loc,
        rail=rail,
        configured=configured,
        oauth_ready=configured and libs_ok,
        connected=connected,
        demo=demo,
        email=email,
        properties=properties,
        selected=selected,
        error=error,
        setup=setup,
        ready=bool(setup and setup["ready"]),
        redirect_uri=redirect_uri(),
        base_url=base_url(),
    )
