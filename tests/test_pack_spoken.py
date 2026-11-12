"""Spoken pack labels: pack_l10n JA is the runtime source (registry overlays it)."""

from __future__ import annotations

from sitekpi.i18n.pack_l10n import PACK_L10N
from sitekpi.packs import INDUSTRIES, PACK_COPY, PACK_MODULES


def test_base_packs_have_spoken_l10n():
    missing = [s for s in PACK_MODULES if s not in PACK_L10N]
    assert not missing, f"PACK_L10N missing for {missing}"


def test_registry_overlays_spoken_ja_from_l10n():
    for slug in PACK_MODULES:
        loc = PACK_L10N[slug]
        meta = INDUSTRIES[slug]
        copy = PACK_COPY[slug]
        for field in ("label", "hint", "signup_label"):
            row = loc.get(field)
            ja = row.get("ja") if isinstance(row, dict) else None
            if ja:
                assert meta.get(field) == ja, f"{slug}.{field}: registry {meta.get(field)!r} != l10n {ja!r}"
        for field in ("cvr_label", "mid_label", "bottom_label", "rate_a_label", "rate_b_label", "property"):
            row = loc.get(field)
            ja = row.get("ja") if isinstance(row, dict) else None
            if ja:
                assert copy.get(field) == ja, f"{slug}.copy.{field}: registry {copy.get(field)!r} != l10n {ja!r}"
