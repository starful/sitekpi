"""Shared board render context for one HTML response.

_ACTIVE_BENCH / _ACTIVE_LOCALE are ContextVars so concurrent sync workers
(thread pool) do not leak another request's 業界目安 or locale into this board.
Set/reset only in views.board.render_sample_dense.
"""

from __future__ import annotations

from contextvars import ContextVar
from typing import Any

from sitekpi.i18n import t

_KIND_KEYS = {
    "digital": "kind.digital",
    "event": "kind.event",
    "traffic": "kind.traffic",
    "business": "kind.business",
}
# JA fallbacks when t() has no key (should not happen after i18n coverage).
KINDS = {
    "digital": "デジタル",
    "event": "イベント",
    "traffic": "流入",
    "business": "業務",
}

_ACTIVE_BENCH: ContextVar[dict[str, dict[str, Any]]] = ContextVar("_ACTIVE_BENCH", default={})
_ACTIVE_LOCALE: ContextVar[str] = ContextVar("_ACTIVE_LOCALE", default="ja")

EVENT_PREVIEW = 10  # L2 イベント table shows this many + 「ほか n 件」
_UNLINKED = (None, "", "—", "–")  # business KPI empty glyphs — never invent a number


def kind_label(kind: str, locale: str) -> str:
    key = _KIND_KEYS.get(kind)
    return t(key, locale) if key else KINDS.get(kind, kind)


# Back-compat for in-package callers
_kind_label = kind_label
