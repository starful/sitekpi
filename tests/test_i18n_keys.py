"""UI string catalog must not redefine the same key (later silent wins confuse editors)."""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

STRINGS = Path(__file__).resolve().parents[1] / "sitekpi" / "i18n" / "strings.py"


def test_ui_string_keys_are_unique():
    text = STRINGS.read_text(encoding="utf-8")
    keys = re.findall(r'^    "([^"]+)":', text, re.M)
    dups = sorted(k for k, n in Counter(keys).items() if n > 1)
    assert not dups, f"duplicate UI keys: {dups}"
