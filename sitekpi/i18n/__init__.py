"""App locale (in-app setting → session)."""

from __future__ import annotations

from collections.abc import MutableMapping
from typing import Any

from sitekpi.i18n.strings import LOCALES, UI

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


_BOT = ("bot", "crawler", "spider", "slurp", "preview", "lighthouse", "headless")


def browser_locale(accept_language: str) -> str | None:
    """The first of ja / en / ko in the browser's Accept-Language (q order), or None.
    'en-US,en;q=0.9,ja;q=0.8' → 'en'; 'zh-TW,ko;q=0.7' → 'ko'; 'fr' → None."""
    prefs: list[tuple[float, int, str]] = []
    for i, part in enumerate((accept_language or "").split(",")[:12]):
        tag, _, params = part.strip().partition(";")
        q = 1.0
        if params.strip().startswith("q="):
            try:
                q = float(params.strip()[2:])
            except ValueError:
                q = 0.0
        lang = tag.strip().lower().split("-")[0]
        if lang in LOCALES and q > 0:
            prefs.append((-q, i, lang))
    return min(prefs)[2] if prefs else None


class BrowserLocaleMiddleware:
    """First visit with no language chosen yet: use the browser's language (Accept-Language) — not IP.
    Only en / ko are stored; ja (the default) needs nothing. ?lang= and the in-app switch always win.
    Crawlers are left on the default so search engines index the ja page (en/ko have ?lang= hreflang URLs)."""

    def __init__(self, app: Any) -> None:
        self.app = app

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        if scope.get("type") == "http" and scope.get("method") == "GET" and "session" in scope:
            session = scope["session"]
            qs = scope.get("query_string", b"").decode("latin-1")
            if not session.get(SESSION_KEY) and "lang=" not in qs and not scope.get("path", "").startswith(("/static", "/stk", "/events")):
                headers = {k.decode("latin-1").lower(): v.decode("latin-1") for k, v in scope.get("headers", [])}
                ua = headers.get("user-agent", "").lower()
                if ua and not any(b in ua for b in _BOT):
                    loc = browser_locale(headers.get("accept-language", ""))
                    if loc and loc != DEFAULT_LOCALE:
                        session[SESSION_KEY] = loc
        await self.app(scope, receive, send)
