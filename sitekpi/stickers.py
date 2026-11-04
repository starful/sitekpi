"""Optional metric stickers: static/stickers/{help_id}.{gif|webp|png}.

Missing files = no sticker (layout unchanged). Language-agnostic assets.
Directory listing is re-read when files change (no stale process cache).
"""

from __future__ import annotations

from pathlib import Path

from sitekpi.templating import static_url

_ROOT = Path(__file__).resolve().parents[1] / "static" / "stickers"

_cache_key: tuple[tuple[str, int], ...] | None = None
_cache_index: dict[str, dict[str, str]] = {}


def _dir_key() -> tuple[tuple[str, int], ...]:
    if not _ROOT.is_dir():
        return ()
    rows: list[tuple[str, int]] = []
    for path in _ROOT.iterdir():
        if path.is_file() and not path.name.startswith("."):
            try:
                rows.append((path.name, path.stat().st_mtime_ns))
            except OSError:
                continue
    return tuple(sorted(rows))


def _index() -> dict[str, dict[str, str]]:
    """help_id → {anim?, still?} relative static paths."""
    global _cache_key, _cache_index
    key = _dir_key()
    if key == _cache_key:
        return _cache_index
    out: dict[str, dict[str, str]] = {}
    if _ROOT.is_dir():
        for path in _ROOT.iterdir():
            if not path.is_file() or path.name.startswith("."):
                continue
            stem = path.stem
            if stem.endswith("-base") or stem.startswith("mascot"):
                continue
            rel = f"stickers/{path.name}"
            slot = out.setdefault(stem, {})
            suf = path.suffix.lower()
            if suf == ".gif":
                slot["anim"] = rel
            elif suf in (".webp", ".png", ".jpg", ".jpeg"):
                slot.setdefault("still", rel)
    _cache_key = key
    _cache_index = out
    return out


def sticker_for(help_id: str) -> dict[str, str] | None:
    """Return {url, still_url?} for template, or None."""
    slot = _index().get(help_id)
    if not slot:
        return None
    anim = slot.get("anim")
    still = slot.get("still")
    if not anim and not still:
        return None
    primary = anim or still
    assert primary
    out: dict[str, str] = {"url": static_url(primary)}
    if still:
        out["still_url"] = static_url(still)
    return out


def clear_sticker_cache() -> None:
    global _cache_key, _cache_index
    _cache_key = None
    _cache_index = {}
