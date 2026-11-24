"""Board share links: UTM params so visits from a shared board link are attributable."""

from __future__ import annotations

SHARE_UTM: dict[str, str] = {
    "utm_source": "sitekpi_share",
    "utm_medium": "share",
    "utm_campaign": "board_share",
}
