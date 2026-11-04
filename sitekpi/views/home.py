"""Start page (/) when nothing is connected: connect · demo · sample, and what the board shows."""

from __future__ import annotations

from typing import Any

from sitekpi.templating import render


def render_home(*, locale: str = "ja", rail: dict[str, Any] | None = None) -> str:
    return render("home.html", loc=locale, rail=rail)
