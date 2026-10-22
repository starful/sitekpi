"""In-app Settings — display language (session)."""

from __future__ import annotations

from sitekpi.i18n import locale_options, normalize_locale
from sitekpi.templating import render
from sitekpi.views.layout import rail_context


def render_settings_page(
    *,
    locale: str = "ja",
    saved: bool = False,
    pack_links: list | None = None,
    pack_groups: list | None = None,
    connected: dict[str, str] | None = None,
    back_href: str = "/hr",
) -> str:
    loc = normalize_locale(locale)
    rail = rail_context(
        nav_active="settings",
        locale=loc,
        connected=connected,
        pack_groups=pack_groups,
        pack_links=pack_links,
    )
    return render(
        "settings.html",
        loc=loc,
        rail=rail,
        saved=saved,
        locales=locale_options(),
        back_href=back_href,
    )
