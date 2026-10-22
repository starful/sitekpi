"""Sample-pack categories (nav grouping). UI may consume this later."""

from __future__ import annotations

from typing import Any

# id -> label (JP). Order = nav order when grouped.
CATEGORIES: dict[str, dict[str, Any]] = {
    "membership": {"label": "会員・継続", "order": 10},
    "content": {"label": "コンテンツ", "order": 20},
    "recruit": {"label": "採用", "order": 30},
    "lead": {"label": "問い合わせ・リード", "order": 40},
    "commerce": {"label": "コマース", "order": 50},
    "education": {"label": "教育・申込", "order": 60},
    "booking": {"label": "予約", "order": 70},
}
