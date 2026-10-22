# Industry packs

One file per vertical. Demo numbers, 業界目安 bands, board copy, and event labels live together.

## Add a pack

1. Copy an existing file (e.g. `ec.py`) to `packs/{slug}.py`.
2. Edit `PACK`: `meta` (incl. `category`), `benchmarks`, `demo`, `copy`, `event_desc`.
3. Append `"{slug}"` to `PACK_MODULES` in [`registry.py`](registry.py).
4. Add `PACK_L10N["{slug}"]` in [`../i18n/pack_l10n.py`](../i18n/pack_l10n.py) (`label` / `hint` at least, `ja`/`en`/`ko`).
5. Run `python scripts/smoke_packs.py` then restart the server — `/{slug}` is available.

Categories are defined in [`catalog.py`](catalog.py). Structure conventions for agents: `.cursor/rules/kpi-starter-structure.mdc`.

## Shared metrics help

説明テキスト for common KPI ids lives in [`../metrics/help.py`](../metrics/help.py), not per pack.
