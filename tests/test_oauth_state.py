"""OAuth callback must only accept the state issued to *this* browser session."""

from __future__ import annotations

from urllib.parse import parse_qs, urlsplit

import pytest
from fastapi.testclient import TestClient

from main import app

BASE = "http://127.0.0.1:8766"


class _FakeCreds:
    def to_json(self) -> str:
        return '{"token": "t", "refresh_token": "r", "client_id": "c", "client_secret": "s"}'


@pytest.fixture
def fake_token_exchange(monkeypatch):
    """Stub Google's token endpoint; record what the flow sent."""
    calls: list[dict] = []
    from google_auth_oauthlib.flow import Flow

    def fetch_token(self, **kwargs):
        calls.append({"state": self.oauth2session._state, "verifier": self.code_verifier, **kwargs})
        return {"access_token": "t"}

    monkeypatch.setattr(Flow, "fetch_token", fetch_token)
    monkeypatch.setattr(Flow, "credentials", property(lambda self: _FakeCreds()))
    # After a successful connect the page lists GA4 properties — keep it offline
    import sitekpi.routes.connect as connect_routes

    monkeypatch.setattr(connect_routes, "creds_from_session", lambda session: object())
    monkeypatch.setattr(connect_routes, "list_properties", lambda creds: [])
    return calls


def _client() -> TestClient:
    return TestClient(app, base_url=BASE, follow_redirects=False)


def _start(client: TestClient) -> str:
    r = client.get("/connect/google")
    assert r.status_code == 302
    loc = urlsplit(r.headers["location"])
    assert loc.netloc == "accounts.google.com"
    q = parse_qs(loc.query)
    assert q.get("code_challenge_method") == ["S256"]  # PKCE on
    return q["state"][0]


def test_happy_path(fake_token_exchange):
    c = _client()
    state = _start(c)
    r = c.get(f"/connect/callback?state={state}&code=abc")
    assert r.status_code == 302 and r.headers["location"] == "/connect"
    assert len(fake_token_exchange) == 1
    assert fake_token_exchange[0]["verifier"]  # PKCE verifier from this session


def test_callback_from_another_browser_is_rejected(fake_token_exchange):
    """Login CSRF: attacker starts a flow, sends the victim the callback URL."""
    attacker = _client()
    state = _start(attacker)
    victim = _client()  # no oauth_state in this session
    r = victim.get(f"/connect/callback?state={state}&code=attackers-code")
    assert r.status_code == 200
    assert "Google 接続を確認できませんでした" in r.text
    assert fake_token_exchange == []


def test_mismatched_state_is_rejected(fake_token_exchange):
    c = _client()
    _start(c)
    r = c.get("/connect/callback?state=forged&code=abc")
    assert "Google 接続を確認できませんでした" in r.text
    assert fake_token_exchange == []


def test_state_is_single_use(fake_token_exchange):
    c = _client()
    state = _start(c)
    c.get(f"/connect/callback?state={state}&code=abc")
    r = c.get(f"/connect/callback?state={state}&code=abc")
    assert "Google 接続を確認できませんでした" in r.text
    assert len(fake_token_exchange) == 1


def test_missing_state_is_rejected(fake_token_exchange):
    c = _client()
    _start(c)
    r = c.get("/connect/callback?code=abc")
    assert "Google 接続を確認できませんでした" in r.text
    assert fake_token_exchange == []


def test_user_cancel_on_google(fake_token_exchange):
    c = _client()
    state = _start(c)
    r = c.get(f"/connect/callback?state={state}&error=access_denied")
    assert "キャンセルされました" in r.text
    assert fake_token_exchange == []


def test_flow_starts_on_redirect_host():
    """localhost → 127.0.0.1 first, so the session cookie survives Google's redirect."""
    c = TestClient(app, base_url="http://localhost:8766", follow_redirects=False)
    r = c.get("/connect/google")
    assert r.status_code == 302
    assert r.headers["location"] == "http://127.0.0.1:8766/connect/google"


def test_revoked_grant_does_not_break_connect_page(monkeypatch):
    """If Google refuses to refresh (user revoked access), /connect must still render."""
    from google.auth.exceptions import RefreshError
    from google.oauth2.credentials import Credentials

    def refresh(self, request):
        raise RefreshError("invalid_grant: Token has been expired or revoked.")

    monkeypatch.setattr(Credentials, "refresh", refresh)
    monkeypatch.setattr(Credentials, "expired", property(lambda self: True))

    from sitekpi.ga4.oauth import creds_from_session

    session = {
        "ga4_credentials": {"token": "t", "refresh_token": "r", "client_id": "c", "client_secret": "s"},
        "ga4_property": {"id": "1", "name": "P"},
    }
    assert creds_from_session(session) is None
    assert "ga4_credentials" not in session and "ga4_property" not in session
