"""Optional metric stickers: static/stickers/{help_id}.{gif|webp|png}.

Missing files = no sticker (layout unchanged). Language-agnostic assets.
Directory listing is re-read when files change (no stale process cache).

Pages load them from an opaque URL (/stk/<hash>.gif), not /static/stickers/<help_id>.gif:
ad/tracker blockers drop image requests whose path looks like analytics ("pageviews.gif",
"page_view.gif" …), which left those cards blank. The hash also changes when a file is rewritten.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse, Response

router = APIRouter()

_ROOT = Path(__file__).resolve().parents[1] / "static" / "stickers"

_cache_key: tuple[tuple[str, int], ...] | None = None
_cache_index: dict[str, dict[str, str]] = {}
_by_token: dict[str, Path] = {}  # "<hash>.gif" → file


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


def _token(path: Path) -> str:
    st = path.stat()
    raw = f"{path.name}:{st.st_mtime_ns}:{st.st_size}".encode()
    return hashlib.sha256(raw).hexdigest()[:16] + path.suffix.lower()


def _index() -> dict[str, dict[str, str]]:
    """help_id → {anim?, still?} opaque URLs (/stk/<hash>.<ext>)."""
    global _cache_key, _cache_index, _by_token
    key = _dir_key()
    if key == _cache_key:
        return _cache_index
    out: dict[str, dict[str, str]] = {}
    tokens: dict[str, Path] = {}
    if _ROOT.is_dir():
        for path in _ROOT.iterdir():
            if not path.is_file() or path.name.startswith("."):
                continue
            stem = path.stem
            if stem.endswith("-base") or stem.startswith("mascot"):
                continue
            suf = path.suffix.lower()
            if suf not in (".gif", ".webp", ".png", ".jpg", ".jpeg"):
                continue
            try:
                tok = _token(path)
            except OSError:
                continue
            tokens[tok] = path
            url = f"/stk/{tok}"
            slot = out.setdefault(stem, {})
            if suf == ".gif":
                slot["anim"] = url
            else:
                slot.setdefault("still", url)
    _cache_key = key
    _cache_index = out
    _by_token = tokens
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
    out: dict[str, str] = {"url": primary}
    if still:
        out["still_url"] = still
    return out


def clear_sticker_cache() -> None:
    global _cache_key, _cache_index, _by_token
    _cache_key = None
    _cache_index = {}
    _by_token = {}


@router.get("/stk/{token}")
def sticker_file(token: str) -> Response:
    _index()
    path = _by_token.get(token)
    if path is None or not path.is_file():
        return Response(status_code=404)
    # the token changes whenever the file does, so the response never goes stale
    return FileResponse(path, headers={"Cache-Control": "public, max-age=31536000, immutable"})
