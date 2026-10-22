#!/usr/bin/env python3
"""Smoke: registry ↔ pack_l10n ↔ categories ↔ dense board render.

Run from repo root:
  .venv/bin/python scripts/smoke_packs.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> int:
    from dense_packs import build_dense_board
    from i18n.pack_l10n import PACK_L10N
    from packs import BENCHMARKS, DEMO, INDUSTRIES
    from packs.catalog import CATEGORIES
    from packs.registry import PACK_MODULES
    from sample_dense import _rail_nav_html, render_sample_dense

    errors: list[str] = []

    if set(PACK_MODULES) != set(INDUSTRIES):
        errors.append(
            f"PACK_MODULES ≠ INDUSTRIES: "
            f"only_modules={set(PACK_MODULES) - set(INDUSTRIES)} "
            f"only_industries={set(INDUSTRIES) - set(PACK_MODULES)}"
        )

    for slug in INDUSTRIES:
        if slug not in PACK_L10N:
            errors.append(f"{slug}: missing PACK_L10N entry")
            continue
        row = PACK_L10N[slug]
        for field in ("label", "hint"):
            loc = row.get(field) or {}
            for locale in ("ja", "en", "ko"):
                if not str(loc.get(locale) or "").strip():
                    errors.append(f"{slug}: PACK_L10N.{field}.{locale} empty")
        cat = str(INDUSTRIES[slug].get("category") or "")
        if cat not in CATEGORIES:
            errors.append(f"{slug}: unknown category {cat!r}")
        if slug not in DEMO or "28d" not in DEMO[slug]:
            errors.append(f"{slug}: missing DEMO['28d']")
        if slug not in BENCHMARKS:
            errors.append(f"{slug}: missing BENCHMARKS")

    for cid in CATEGORIES:
        # cat.* keys live in strings; render path uses t(f"cat.{cid}")
        pass

    # Rail must include every registered pack link
    rail = _rail_nav_html(
        industry="hr",
        nav_active="pack:hr",
        pack_groups=None,
        locale="ja",
    )
    for slug in INDUSTRIES:
        if f'href="/{slug}"' not in rail:
            errors.append(f"rail missing link /{slug}")

    # Dense board + full sample HTML for each slug × locale
    for slug, ind in INDUSTRIES.items():
        data = DEMO[slug]["28d"]
        benches = BENCHMARKS[slug]
        for locale in ("ja", "en", "ko"):
            try:
                build_dense_board(
                    industry=slug,
                    period="28d",
                    ind=ind,
                    data=data,
                    benches_raw=benches,
                    locale=locale,
                )
                html = render_sample_dense(
                    industry=slug,
                    period="28d",
                    data=data,
                    ind=ind,
                    benches_raw=benches,
                    locale=locale,
                )
            except Exception as exc:  # noqa: BLE001 — smoke reports any failure
                errors.append(f"render {slug}/{locale}: {exc}")
                continue
            if "pack-cat" not in html:
                errors.append(f"render {slug}/{locale}: missing pack-cat nav")

    # Soft reminder: rail CSS still duplicated (do not fail until extracted)
    sample_css = (ROOT / "sample_dense.py").read_text(encoding="utf-8")
    settings_css = (ROOT / "settings_page.py").read_text(encoding="utf-8")
    marker = ".rail .pack-cat summary"
    if marker in sample_css and marker in settings_css:
        print(
            "note: rail pack-cat CSS is still duplicated in "
            "sample_dense.py and settings_page.py — keep them in sync "
            "or extract a shared helper."
        )

    if errors:
        print(f"FAIL ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"ok: {len(INDUSTRIES)} packs × 3 locales, rail + dense board")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
