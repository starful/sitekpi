"""Server-side session: cookie holds only an id; data is encrypted at rest."""

from __future__ import annotations

import os
import sqlite3
from urllib.parse import parse_qs, urlsplit

import pytest
from fastapi.testclient import TestClient

from main import app

BASE = "http://127.0.0.1:8766"
DB = os.environ["SESSION_DB_PATH"]


def _client() -> TestClient:
    return TestClient(app, base_url=BASE, follow_redirects=False)


def _rows() -> list[bytes]:
    with sqlite3.connect(DB) as db:
        return [r[0] for r in db.execute("SELECT data FROM sessions")]


@pytest.fixture
def signed_in(monkeypatch):
    """A client that completed the Google flow (token endpoint stubbed)."""
    from google_auth_oauthlib.flow import Flow

    import sitekpi.routes.connect as connect_routes

    class Creds:
        def to_json(self):
            return '{"token": "AT-secret", "refresh_token": "RT-very-secret", "client_id": "c", "client_secret": "s"}'

    monkeypatch.setattr(Flow, "fetch_token", lambda self, **kw: {"access_token": "t"})
    monkeypatch.setattr(Flow, "credentials", property(lambda self: Creds()))
    monkeypatch.setattr(connect_routes, "creds_from_session", lambda session: object())
    monkeypatch.setattr(connect_routes, "list_properties", lambda creds: [])

    c = _client()
    r = c.get("/connect/google")
    state = parse_qs(urlsplit(r.headers["location"]).query)["state"][0]
    sid_before = c.cookies.get("sitekpi_sid")
    r = c.get(f"/connect/callback?state={state}&code=abc")
    assert r.status_code == 302
    return c, sid_before


def test_cookie_holds_only_an_id(signed_in):
    c, _ = signed_in
    cookie = c.cookies.get("sitekpi_sid")
    assert cookie and len(cookie) >= 40
    assert "RT-very-secret" not in cookie and "ga4" not in cookie
    assert "kpistarter_session" not in c.cookies


def test_grant_is_encrypted_at_rest(signed_in):
    blobs = b"".join(_rows())
    assert blobs, "session should be stored server-side"
    assert b"RT-very-secret" not in blobs and b"ga4_credentials" not in blobs


def test_session_id_rotates_on_sign_in(signed_in):
    c, sid_before = signed_in
    sid_after = c.cookies.get("sitekpi_sid")
    assert sid_before and sid_after and sid_before != sid_after
    # the pre-login id no longer carries the signed-in session
    from sitekpi.session import SQLiteSessionStore

    store = next(m.kwargs["store"] for m in app.user_middleware if "store" in m.kwargs)
    assert isinstance(store, SQLiteSessionStore)
    assert store.load(sid_before) is None
    assert "ga4_credentials" in store.load(sid_after)[0]


def test_forged_cookie_starts_fresh_session():
    c = _client()
    c.cookies.set("sitekpi_sid", "forged-value")
    r = c.get("/connect")
    assert r.status_code == 200
    assert c.cookies.get("sitekpi_sid") in (None, "forged-value")  # not adopted as a session


def test_disconnect_deletes_server_row(signed_in):
    c, _ = signed_in
    sid = c.cookies.get("sitekpi_sid")
    store = next(m.kwargs["store"] for m in app.user_middleware if "store" in m.kwargs)
    assert store.load(sid) is not None
    r = c.post("/connect/disconnect")
    assert r.status_code == 302
    assert store.load(sid) is None
    assert "Max-Age=0" in r.headers.get("set-cookie", "")


def test_settings_persist_across_requests():
    c = _client()
    c.post("/settings", data={"locale": "ko"})
    assert 'lang="ko"' in c.get("/settings").text


def test_legacy_cookie_is_expired():
    c = _client()
    c.cookies.set("kpistarter_session", "old-signed-cookie")
    r = c.get("/connect")
    assert "kpistarter_session=; Path=/; Max-Age=0" in r.headers.get("set-cookie", "")


def test_https_requires_real_secret(monkeypatch):
    from sitekpi.session import session_settings

    monkeypatch.setenv("APP_BASE_URL", "https://sitekpi.example")
    monkeypatch.setenv("SESSION_SECRET", "change-me-to-a-long-random-string")
    with pytest.raises(RuntimeError):
        session_settings()
    monkeypatch.setenv("SESSION_SECRET", "a" * 48)
    assert session_settings()["https_only"] is True
