"""App locale (in-app setting → session)."""

from __future__ import annotations

from typing import Any, MutableMapping

from i18n.strings import LOCALES, UI

DEFAULT_LOCALE = "ja"
SESSION_KEY = "locale"


def normalize_locale(value: str | None) -> str:
    if value and value in LOCALES:
        return value
    return DEFAULT_LOCALE


def get_locale(session: MutableMapping[str, Any] | None) -> str:
    if not session:
        return DEFAULT_LOCALE
    return normalize_locale(str(session.get(SESSION_KEY) or ""))


def set_locale(session: MutableMapping[str, Any], locale: str) -> str:
    loc = normalize_locale(locale)
    session[SESSION_KEY] = loc
    return loc


def t(key: str, locale: str | None = None, **kwargs: Any) -> str:
    """Translate UI chrome key. Falls back to ja, then key."""
    loc = normalize_locale(locale)
    row = UI.get(key) or {}
    text = row.get(loc) or row.get(DEFAULT_LOCALE) or key
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, ValueError):
            return text
    return text


def html_lang(locale: str | None = None) -> str:
    loc = normalize_locale(locale)
    return str(LOCALES[loc]["html_lang"])


def locale_options() -> list[tuple[str, str]]:
    return [(code, meta["label"]) for code, meta in LOCALES.items()]
