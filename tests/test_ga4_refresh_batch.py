"""Daily GA4 token refresh batch + its failure-list API (sitekpi/ga4/refresh_batch.py)."""

from __future__ import annotations

import json

from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from google.oauth2.credentials import Credentials

from sitekpi import visitlog
from sitekpi.app import app
from sitekpi.ga4 import refresh_batch
from sitekpi.session import SQLiteSessionStore


def _info(expiry: datetime | None) -> dict:
    info = {"token": "AT", "refresh_token": "RT", "client_id": "c", "client_secret": "s"}
    if expiry is not None:
        info["expiry"] = expiry.strftime("%Y-%m-%dT%H:%M:%SZ")
    return info


@pytest.fixture
def store(tmp_path, monkeypatch):
    s = SQLiteSessionStore(tmp_path / "sessions.sqlite3", "k" * 40, 14 * 24 * 60 * 60)
    monkeypatch.setattr(refresh_batch, "_session_store", lambda: s)
    monkeypatch.setattr(refresh_batch, "_FAILURES_PATH", tmp_path / "ga4_refresh_failures.json")
    return s


def test_refreshes_a_grant_close_to_expiry(store, monkeypatch):
    store.save("sid-1", {"ga4_credentials": _info(None), "ga4_email": "a@example.com"})  # no expiry = already due

    def ok_refresh(self, request):
        self.token = "AT-new"
        self.expiry = datetime.now(timezone.utc) + timedelta(hours=1)

    monkeypatch.setattr(Credentials, "refresh", ok_refresh)
    counts = refresh_batch.refresh_all()
    assert counts == {"checked": 1, "refreshed": 1, "failed": 0}
    assert store.load("sid-1")[0]["ga4_credentials"]["token"] == "AT-new"
    assert refresh_batch.list_failures() == []


def test_leaves_a_fresh_grant_alone(store, monkeypatch):
    store.save("sid-1", {"ga4_credentials": _info(datetime.now(timezone.utc) + timedelta(days=10))})
    called = []
    monkeypatch.setattr(Credentials, "refresh", lambda self, request: called.append(1))
    counts = refresh_batch.refresh_all()
    assert counts == {"checked": 1, "refreshed": 0, "failed": 0}
    assert not called


def test_failed_refresh_is_recorded_and_listed_by_the_api(store):
    # conftest's autouse fixture makes Credentials.refresh raise RefreshError for every test token
    store.save("sid-1", {"ga4_credentials": _info(None), "ga4_email": "a@example.com"})
    counts = refresh_batch.refresh_all()
    assert counts == {"checked": 1, "refreshed": 0, "failed": 1}
    failures = refresh_batch.list_failures()
    assert "error" in failures[0] and failures[0]["site"]
    assert "a@example.com" not in json.dumps(failures)   # no personal data in the unencrypted store

    client = TestClient(app)
    r = client.get("/hq/api/ga4-refresh-failures",
                    headers={"Authorization": "Bearer " + visitlog.hq_token()})
    assert r.status_code == 200
    assert r.json()["failures"][0]["site"] == failures[0]["site"]


def test_a_later_successful_refresh_clears_the_failure(store, monkeypatch):
    store.save("sid-1", {"ga4_credentials": _info(None)})
    refresh_batch.refresh_all()  # fails (autouse fixture rejects test tokens)
    assert refresh_batch.list_failures()

    def ok_refresh(self, request):
        self.token = "AT-new"
        self.expiry = datetime.now(timezone.utc) + timedelta(hours=1)

    monkeypatch.setattr(Credentials, "refresh", ok_refresh)
    counts = refresh_batch.refresh_all()
    assert counts["refreshed"] == 1
    assert refresh_batch.list_failures() == []
