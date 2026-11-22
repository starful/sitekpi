"""Subscription billing (Stripe webhooks) — first step of the paid-plan backend.

Stores one row per subscriber: who they are (``user_id`` — today this is the
Stripe customer id, since SiteKPI has no login yet; a real account id can
replace it once one exists), which plan, its status, and when it last renewed.
Local SQLite only for now (see ``sitekpi/firestore_store.py`` for the Firestore
pattern this would need on Cloud Run before going live).

No ``stripe`` package is used: webhook signatures are verified by hand with
``hmac`` (the scheme Stripe documents for ``Stripe-Signature``), so this adds
no new dependency.
"""

from __future__ import annotations

import os
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

# invoice.payment_failed events before we give up and mark the subscription canceled.
# Stripe's own Smart Retries already re-attempts the charge; this just bounds how long
# we keep a subscriber in "past_due" before treating the plan as lapsed.
MAX_PAYMENT_RETRIES = 3

STATUS_ACTIVE = "active"
STATUS_PAST_DUE = "past_due"
STATUS_CANCELED = "canceled"

# How many sites a free (no active paid subscription) workspace may connect at once.
# Paid plans can be given a higher per-row site_limit once pricing is final (not yet
# decided — see docs/plan); until then every row defaults to the free limit.
FREE_SITE_LIMIT = 1

# Plan tiers for feature gating. There is no ORM "Site.plan" — the workspace plan
# lives in ``subscriptions`` (and is ``free`` when there is no active row).
PLAN_FREE = "free"
PLAN_PRO = "pro"

# Stripe lookup_key / stored plan strings that count as Pro while status is active.
_PRO_PLAN_KEYS = frozenset({
    PLAN_PRO, "pro_monthly", "pro_yearly", "team_monthly", "team_yearly",
})

# Features that need an active paid plan. Do NOT put board / connect / disconnect /
# setup here — free users must keep the current live path (HQ verify regressions).
PRO_FEATURES = frozenset({
    "advanced_report",  # future: GA4 advanced / export packs
    # "site_compare" (/sites: other sites' summaries) is free for now (2026-11-22 decision);
    # add it back here to put it behind Pro once paid plans can be bought.
})


class SubscriptionStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._lock = threading.Lock()
        from sitekpi.sqlite_util import connect, init_wal

        init_wal(path)
        with connect(path) as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS subscriptions ("
                " user_id TEXT PRIMARY KEY, plan TEXT NOT NULL, status TEXT NOT NULL,"
                " stripe_customer_id TEXT, stripe_subscription_id TEXT,"
                " renewed_at INTEGER, retry_count INTEGER NOT NULL DEFAULT 0,"
                f" site_limit INTEGER NOT NULL DEFAULT {FREE_SITE_LIMIT},"
                " updated_at INTEGER NOT NULL)"
            )
            # Migration for subscriptions.sqlite3 files that predate site_limit.
            cols = {row[1] for row in db.execute("PRAGMA table_info(subscriptions)").fetchall()}
            if "site_limit" not in cols:
                db.execute(
                    f"ALTER TABLE subscriptions ADD COLUMN site_limit INTEGER"
                    f" NOT NULL DEFAULT {FREE_SITE_LIMIT}"
                )

    def _connect(self) -> sqlite3.Connection:
        from sitekpi.sqlite_util import connect

        return connect(self.path)

    def get(self, user_id: str) -> dict[str, Any] | None:
        with self._connect() as db:
            row = db.execute(
                "SELECT user_id, plan, status, stripe_customer_id, stripe_subscription_id,"
                " renewed_at, retry_count, site_limit, updated_at FROM subscriptions WHERE user_id = ?",
                (user_id,),
            ).fetchone()
        if not row:
            return None
        keys = ("user_id", "plan", "status", "stripe_customer_id", "stripe_subscription_id",
                "renewed_at", "retry_count", "site_limit", "updated_at")
        return dict(zip(keys, row))

    def site_limit(self, user_id: str | None) -> int:
        """How many sites this workspace may keep connected right now.

        No row (never subscribed) or a lapsed subscription (past_due/canceled) both fall
        back to the free limit; an active row uses its own site_limit."""
        row = self.get(user_id) if user_id else None
        if not row or row["status"] != STATUS_ACTIVE:
            return FREE_SITE_LIMIT
        return int(row["site_limit"] or FREE_SITE_LIMIT)

    def upsert(
        self,
        user_id: str,
        *,
        plan: str,
        status: str,
        stripe_customer_id: str | None = None,
        stripe_subscription_id: str | None = None,
        renewed_at: int | None = None,
        retry_count: int = 0,
    ) -> None:
        """Subscription created/updated/renewed — current state replaces the row."""
        now = int(time.time())
        with self._lock, self._connect() as db:
            db.execute(
                "INSERT INTO subscriptions (user_id, plan, status, stripe_customer_id,"
                " stripe_subscription_id, renewed_at, retry_count, updated_at)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
                " ON CONFLICT(user_id) DO UPDATE SET plan = excluded.plan,"
                " status = excluded.status,"
                " stripe_customer_id = COALESCE(excluded.stripe_customer_id, subscriptions.stripe_customer_id),"
                " stripe_subscription_id = COALESCE(excluded.stripe_subscription_id, subscriptions.stripe_subscription_id),"
                " renewed_at = COALESCE(excluded.renewed_at, subscriptions.renewed_at),"
                " retry_count = excluded.retry_count, updated_at = excluded.updated_at",
                (user_id, plan, status, stripe_customer_id, stripe_subscription_id,
                 renewed_at, retry_count, now),
            )

    def mark_payment_failed(self, user_id: str) -> int:
        """invoice.payment_failed: bump the retry count; cancel past the limit. Returns the new count."""
        with self._lock, self._connect() as db:
            row = db.execute(
                "SELECT retry_count FROM subscriptions WHERE user_id = ?", (user_id,)
            ).fetchone()
            retry_count = int(row[0]) + 1 if row else 1
            status = STATUS_CANCELED if retry_count >= MAX_PAYMENT_RETRIES else STATUS_PAST_DUE
            db.execute(
                "UPDATE subscriptions SET retry_count = ?, status = ?, updated_at = ?"
                " WHERE user_id = ?",
                (retry_count, status, int(time.time()), user_id),
            )
        return retry_count

    def mark_payment_succeeded(self, user_id: str, renewed_at: int) -> None:
        """invoice.payment_succeeded: back to active, retry count clears."""
        with self._lock, self._connect() as db:
            db.execute(
                "UPDATE subscriptions SET status = ?, retry_count = 0, renewed_at = ?,"
                " updated_at = ? WHERE user_id = ?",
                (STATUS_ACTIVE, renewed_at, int(time.time()), user_id),
            )

    def cancel(self, user_id: str) -> None:
        with self._lock, self._connect() as db:
            db.execute(
                "UPDATE subscriptions SET status = ?, updated_at = ? WHERE user_id = ?",
                (STATUS_CANCELED, int(time.time()), user_id),
            )


def verify_stripe_signature(payload: bytes, sig_header: str, secret: str, tolerance: int = 300) -> bool:
    """Check a ``Stripe-Signature`` header by hand (Stripe's documented v1 scheme).

    Avoids depending on the ``stripe`` package just to verify a webhook.
    """
    import hmac
    import hashlib

    ts = v1 = ""
    for part in sig_header.split(","):
        key, _, value = part.partition("=")
        if key == "t":
            ts = value
        elif key == "v1":
            v1 = value
    if not ts or not v1:
        return False
    try:
        if abs(time.time() - int(ts)) > tolerance:
            return False
    except ValueError:
        return False
    expected = hmac.new(secret.encode(), f"{ts}.".encode() + payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, v1)


_store: SubscriptionStore | None = None
_store_lock = threading.Lock()


def get_store() -> SubscriptionStore:
    global _store
    with _store_lock:
        if not isinstance(_store, SubscriptionStore):
            path = Path(os.getenv("APP_DB_PATH") or (ROOT / ".data" / "app.sqlite3"))
            _store = SubscriptionStore(path)
        return _store


def check_site_limit(user_id: str | None, current_site_count: int) -> dict[str, Any] | None:
    """Would connecting one more site put this workspace over its plan's site_limit?

    Call this right before a *new* site gets linked (``current_site_count`` = sites
    already connected, not counting the new one). Returns an upgrade-prompt payload
    to block the connection with, or ``None`` to let it through. No login/workspace
    id exists yet (see module docstring), so ``user_id`` may be ``None`` — that's
    just treated as a free workspace.
    """
    limit = get_store().site_limit(user_id)
    if current_site_count < limit:
        return None
    return {
        "blocked": True,
        "reason": "site_limit",
        "limit": limit,
        "modal": {
            "title_key": "billing.site_limit_modal.title",
            "body_key": "billing.site_limit_modal.body",
            "cta_key": "billing.site_limit_modal.cta",
        },
    }


def normalize_plan(plan: str | None) -> str:
    """Map a stored Stripe lookup_key / plan id to ``free`` or ``pro``."""
    if not plan:
        return PLAN_FREE
    key = str(plan).strip().lower()
    if key in _PRO_PLAN_KEYS or key.startswith("pro_") or key.startswith("team_"):
        return PLAN_PRO
    return PLAN_FREE


def effective_plan(user_id: str | None) -> str:
    """Workspace plan right now: ``pro`` only with an *active* subscription row."""
    if not user_id:
        return PLAN_FREE
    row = get_store().get(user_id)
    if not row or row.get("status") != STATUS_ACTIVE:
        return PLAN_FREE
    return normalize_plan(row.get("plan"))


def plan_allows(user_id: str | None, feature: str) -> bool:
    """True if this workspace may use ``feature``.

    Unknown / free features always return True so accidental checks never lock the
    board. Only names in ``PRO_FEATURES`` require an active Pro plan.
    """
    if feature not in PRO_FEATURES:
        return True
    return effective_plan(user_id) == PLAN_PRO


def check_feature_access(user_id: str | None, feature: str) -> dict[str, Any] | None:
    """None = allowed; otherwise an upgrade payload (same shape family as site_limit)."""
    if plan_allows(user_id, feature):
        return None
    return {
        "blocked": True,
        "reason": "plan",
        "need": PLAN_PRO,
        "feature": feature,
        "plan": effective_plan(user_id),
        "modal": {
            "title_key": "billing.plan_gate_modal.title",
            "body_key": "billing.plan_gate_modal.body",
            "cta_key": "billing.plan_gate_modal.cta",
        },
    }


def require_plan(feature: str):
    """FastAPI dependency factory: block with HTTP 402 when ``feature`` needs Pro.

    Use only on future Pro routes. Never wrap ``/live``, ``/connect*``, or setup —
    those must stay open for free (and for the demo session used in tests).
    """
    from fastapi import HTTPException, Request

    def _dep(request: Request) -> None:
        # Prefer an explicit billing id when login exists; until then demos stay free.
        session = request.session
        user_id = session.get("billing_user_id") or session.get("stripe_customer_id")
        if isinstance(user_id, str):
            uid: str | None = user_id
        else:
            uid = None
        blocked = check_feature_access(uid, feature)
        if blocked:
            raise HTTPException(status_code=402, detail=blocked)

    return _dep
