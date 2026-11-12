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
    from sitekpi.board.data import build_dense_board
    from sitekpi.i18n.pack_l10n import PACK_L10N
    from sitekpi.packs import BENCHMARKS, DEMO, INDUSTRIES
    from sitekpi.packs.catalog import CATEGORIES
    from sitekpi.packs.registry import PACK_MODULES
    from sitekpi.packs.derived import DERIVED
    from sitekpi.packs.schema import (
        BENCH_CORE_KEYS,
        DEMO_NESTED_KEYS,
        DEMO_SCALAR_KEYS,
        META_KEYS,
        SPOKEN_COPY_FIELDS,
        SPOKEN_META_FIELDS,
    )
    from sitekpi.views.board import render_sample_dense

    # 行動タイプ packs (type-*) are not sample boards; tests/test_flow.py covers them
    INDUSTRIES = {k: v for k, v in INDUSTRIES.items() if not v.get("virtual")}

    errors: list[str] = []

    if set(PACK_MODULES) | set(DERIVED) != set(INDUSTRIES):
        errors.append(
            f"PACK_MODULES ≠ INDUSTRIES: "
            f"only_modules={set(PACK_MODULES) - set(INDUSTRIES)} "
            f"only_industries={set(INDUSTRIES) - set(PACK_MODULES)}"
        )

    for slug in INDUSTRIES:
        if slug in DERIVED:
            row = {f: DERIVED[slug][f] for f in ("label", "hint")}  # wording beyond label/hint: base pack
        elif slug not in PACK_L10N:
            errors.append(f"{slug}: missing PACK_L10N entry")
            continue
        else:
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
        missing_meta = META_KEYS - set(INDUSTRIES[slug])
        if missing_meta:
            errors.append(f"{slug}: meta missing {sorted(missing_meta)}")
        for period, row in (DEMO.get(slug) or {}).items():
            miss = DEMO_SCALAR_KEYS - set(row)
            if miss:
                errors.append(f"{slug} DEMO[{period}]: missing scalars {sorted(miss)}")
            for nk in DEMO_NESTED_KEYS:
                if nk not in row:
                    errors.append(f"{slug} DEMO[{period}]: missing {nk}")
        miss_b = BENCH_CORE_KEYS - set(BENCHMARKS.get(slug) or {})
        if miss_b:
            errors.append(f"{slug}: benchmarks missing core {sorted(miss_b)}")
        # Spoken fields must exist in PACK_L10N (registry overlays JA from there)
        if slug not in DERIVED:
            loc_row = PACK_L10N.get(slug) or {}
            for field in (*SPOKEN_META_FIELDS, *SPOKEN_COPY_FIELDS):
                cell = loc_row.get(field)
                if not isinstance(cell, dict) or not str(cell.get("ja") or "").strip():
                    errors.append(f"{slug}: PACK_L10N.{field}.ja required (spoken source)")

    for cid in CATEGORIES:
        # cat.* keys live in strings; render path uses t(f"cat.{cid}")
        pass

    # 見本ボード must reach every registered industry (goal → industry chip → open the board)
    from sitekpi.packs import INDUSTRIES as ALL_PACKS
    from sitekpi.packs.behaviors import BEHAVIORS, slug_of
    from sitekpi.views.samples import render_samples

    reached = ""
    for cat in BEHAVIORS:
        members = ALL_PACKS[slug_of(cat)].get("members") or [""]
        for m in members:
            reached += render_samples(locale="ja", rail={}, cat=cat, ind=m or None, fragment=True)
    for slug in INDUSTRIES:
        if f'href="/{slug}"' not in reached:
            errors.append(f"/samples missing link /{slug}")

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
            if 'href="/samples"' not in html:
                errors.append(f"render {slug}/{locale}: menu missing 見本ボード一覧")

    # Markup lives in templates; views must not build HTML strings again
    for rel in ("sitekpi/views/board.py", "sitekpi/views/settings.py",
                "sitekpi/views/builder.py", "sitekpi/views/connect.py",
                "sitekpi/views/layout.py"):
        src = (ROOT / rel).read_text(encoding="utf-8")
        if "<!doctype" in src.lower() or "<style" in src or ".rail .pack-cat" in src:
            errors.append(f"{rel}: inline HTML/CSS — use sitekpi/templates + static/")

    if errors:
        print(f"FAIL ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"ok: {len(INDUSTRIES)} packs × 3 locales, rail + dense board")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
