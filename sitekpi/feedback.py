"""「メモ・ご意見」: a free note (+ optional 👍 / 👎) from the right-side panel → POST /feedback.

The panel sends the part of the page on screen (section). The landing's 「ご意見」 dialog uses the same endpoint.

Stored without IP or account data: screen, path, vote, comment, locale, whether a GA4
property was connected (demo / live / none), time. Firestore on Cloud Run, a JSONL file locally.
"""

from __future__ import annotations

import json
import threading
import time
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from sitekpi import firestore_store
from sitekpi.i18n import get_locale

router = APIRouter()

ROOT = Path(__file__).resolve().parents[1]
COMMENT_MAX = 500
DAILY_MAX = 30  # per browser session
_lock = threading.Lock()


def _save(row: dict[str, Any]) -> None:
    if firestore_store.enabled():
        firestore_store.FirestoreFeedbackStore().add(row)
        return
    path = ROOT / ".data" / "feedback.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with _lock, path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


@router.post("/feedback")
async def feedback(request: Request) -> JSONResponse:
    try:
        body = await request.json()
    except ValueError:
        return JSONResponse({"ok": False}, status_code=400)
    if not isinstance(body, dict):
        return JSONResponse({"ok": False}, status_code=400)
    vote = str(body.get("vote") or "")
    comment = str(body.get("comment") or "").strip()[:COMMENT_MAX]
    if vote not in ("up", "down", "") or (not vote and not comment):
        return JSONResponse({"ok": False}, status_code=400)
    if str(body.get("website") or ""):  # honeypot
        return JSONResponse({"ok": True})

    session = request.session
    day = time.strftime("%Y-%m-%d")
    sent = session.get("feedback_sent") if isinstance(session.get("feedback_sent"), dict) else {}
    if sent.get("day") != day:
        sent = {"day": day, "n": 0}
    if int(sent.get("n") or 0) >= DAILY_MAX:
        return JSONResponse({"ok": False, "error": "limit"}, status_code=429)

    connected = "demo" if session.get("ga4_demo") else ("live" if session.get("ga4_credentials") else "none")
    _save({
        "screen": str(body.get("screen") or "")[:40],
        "section": str(body.get("section") or "")[:60],
        "path": str(body.get("path") or "")[:200],
        "vote": vote,
        "comment": comment,
        "locale": get_locale(session),
        "connected": connected,
        "at": int(time.time()),
    })
    session["feedback_sent"] = {"day": day, "n": int(sent.get("n") or 0) + 1}
    return JSONResponse({"ok": True})
