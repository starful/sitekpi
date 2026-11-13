"""Stripe webhook: signature check, then created → payment_failed (retries) → payment_succeeded."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import time

from fastapi.testclient import TestClient

from main import app
from sitekpi.billing import FREE_SITE_LIMIT, MAX_PAYMENT_RETRIES, check_site_limit, get_store

SECRET = "whsec_test_secret"


def _client() -> TestClient:
    return TestClient(app, base_url="http://127.0.0.1:8766", follow_redirects=False)


def _signed(monkeypatch, body: dict) -> tuple[bytes, dict[str, str]]:
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", SECRET)
    payload = json.dumps(body).encode()
    ts = str(int(time.time()))
    sig = hmac.new(SECRET.encode(), f"{ts}.".encode() + payload, hashlib.sha256).hexdigest()
    return payload, {"stripe-signature": f"t={ts},v1={sig}", "content-type": "application/json"}


def _event(event_type: str, obj: dict) -> dict:
    return {"type": event_type, "data": {"object": obj}}


def test_bad_signature_is_rejected(monkeypatch):
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", SECRET)
    resp = _client().post(
        "/billing/webhook",
        content=b"{}",
        headers={"stripe-signature": "t=1,v1=deadbeef", "content-type": "application/json"},
    )
    assert resp.status_code == 400


def test_subscription_lifecycle(monkeypatch):
    user_id = "cus_test_123"
    body = _event("customer.subscription.created", {
        "id": "sub_1", "customer": user_id, "status": "active",
        "current_period_end": 1234567890,
        "items": {"data": [{"price": {"lookup_key": "pro_monthly"}}]},
    })
    payload, headers = _signed(monkeypatch, body)
    assert _client().post("/billing/webhook", content=payload, headers=headers).status_code == 200

    row = get_store().get(user_id)
    assert row and row["plan"] == "pro_monthly" and row["status"] == "active"

    for _ in range(MAX_PAYMENT_RETRIES - 1):
        payload, headers = _signed(monkeypatch, _event("invoice.payment_failed", {"customer": user_id}))
        assert _client().post("/billing/webhook", content=payload, headers=headers).status_code == 200
    assert get_store().get(user_id)["status"] == "past_due"

    payload, headers = _signed(monkeypatch, _event("invoice.payment_failed", {"customer": user_id}))
    _client().post("/billing/webhook", content=payload, headers=headers)
    assert get_store().get(user_id)["status"] == "canceled"

    payload, headers = _signed(monkeypatch, _event("invoice.payment_succeeded", {
        "customer": user_id, "period_end": 1234699999,
    }))
    _client().post("/billing/webhook", content=payload, headers=headers)
    row = get_store().get(user_id)
    assert row["status"] == "active" and row["retry_count"] == 0 and row["renewed_at"] == 1234699999


def test_new_subscriber_defaults_to_free_site_limit(monkeypatch):
    """subscriptions.site_limit is new; a freshly-created row still starts at the free limit."""
    user_id = "cus_test_site_limit"
    body = _event("customer.subscription.created", {
        "id": "sub_2", "customer": user_id, "status": "active",
        "current_period_end": 1234567890,
        "items": {"data": [{"price": {"lookup_key": "pro_monthly"}}]},
    })
    payload, headers = _signed(monkeypatch, body)
    _client().post("/billing/webhook", content=payload, headers=headers)
    assert get_store().get(user_id)["site_limit"] == FREE_SITE_LIMIT


def test_check_site_limit_blocks_once_at_the_limit():
    assert check_site_limit(None, FREE_SITE_LIMIT - 1) is None  # still under the limit
    blocked = check_site_limit(None, FREE_SITE_LIMIT)
    assert blocked and blocked["blocked"] is True and blocked["limit"] == FREE_SITE_LIMIT
    assert blocked["modal"]["title_key"]


def test_check_site_limit_allows_more_once_the_stored_limit_is_raised():
    import sqlite3

    user_id = "cus_test_raised_limit"
    get_store().upsert(user_id, plan="team_monthly", status="active")
    # Per-plan site_limit values aren't decided yet (pricing TBD), so there is no route
    # that sets this above the free default — write it by hand to exercise the check.
    with sqlite3.connect(os.environ["APP_DB_PATH"]) as db:
        db.execute("UPDATE subscriptions SET site_limit = 5 WHERE user_id = ?", (user_id,))
    assert check_site_limit(user_id, 1) is None
    assert check_site_limit(user_id, 5) is not None
