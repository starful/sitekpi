"""Stripe webhook receiver — subscription created/renewed/canceled, payment retry.

POST /billing/webhook is the one endpoint Stripe calls for all of this; there is
no separate "create" or "cancel" route because Stripe itself owns the checkout
and portal UI and just notifies us of the result here.
"""

from __future__ import annotations

import logging
import os

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from sitekpi.billing import get_store, verify_stripe_signature

router = APIRouter(tags=["billing"])
log = logging.getLogger("sitekpi.billing")


def _user_id(obj: dict) -> str | None:
    """No login yet, so the Stripe customer id is the join key (see billing.py)."""
    metadata = obj.get("metadata") or {}
    return str(metadata.get("user_id") or obj.get("customer") or "") or None


def _plan(obj: dict) -> str:
    items = ((obj.get("items") or {}).get("data") or [])
    if items:
        price = (items[0].get("price") or {})
        return str(price.get("lookup_key") or price.get("id") or "")
    return ""


@router.post("/billing/webhook")
async def stripe_webhook(request: Request) -> JSONResponse:
    secret = (os.getenv("STRIPE_WEBHOOK_SECRET") or "").strip()
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature") or ""
    if not secret or not verify_stripe_signature(payload, sig_header, secret):
        return JSONResponse({"ok": False, "error": "bad_signature"}, status_code=400)

    try:
        event = await request.json()
    except ValueError:
        return JSONResponse({"ok": False, "error": "bad_json"}, status_code=400)
    if not isinstance(event, dict):
        return JSONResponse({"ok": False, "error": "bad_json"}, status_code=400)

    event_type = str(event.get("type") or "")
    obj = ((event.get("data") or {}).get("object") or {})
    store = get_store()

    if event_type in ("customer.subscription.created", "customer.subscription.updated"):
        user_id = _user_id(obj)
        if user_id:
            store.upsert(
                user_id,
                plan=_plan(obj),
                status=str(obj.get("status") or "active"),
                stripe_customer_id=str(obj.get("customer") or "") or None,
                stripe_subscription_id=str(obj.get("id") or "") or None,
                renewed_at=obj.get("current_period_end"),
            )
    elif event_type == "customer.subscription.deleted":
        user_id = _user_id(obj)
        if user_id:
            store.cancel(user_id)
    elif event_type == "invoice.payment_failed":
        user_id = _user_id(obj)
        if user_id:
            retries = store.mark_payment_failed(user_id)
            log.warning("billing: payment failed for %s (retry %d)", user_id, retries)
    elif event_type == "invoice.payment_succeeded":
        user_id = _user_id(obj)
        renewed_at = obj.get("period_end") or obj.get("created")
        if user_id and renewed_at:
            store.mark_payment_succeeded(user_id, int(renewed_at))
    else:
        log.info("billing: unhandled event type %s", event_type)

    return JSONResponse({"ok": True})
