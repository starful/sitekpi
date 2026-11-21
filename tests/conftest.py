import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Deterministic test config (never touches the real .env values)
import tempfile

os.environ["SESSION_SECRET"] = "test-secret-" + "x" * 32
_tmp = Path(tempfile.mkdtemp())
os.environ["SESSION_DB_PATH"] = str(_tmp / "sessions.sqlite3")
os.environ["APP_DB_PATH"] = str(_tmp / "app.sqlite3")
os.environ["GOOGLE_CLIENT_ID"] = "test-client-id.apps.googleusercontent.com"
os.environ["GOOGLE_CLIENT_SECRET"] = "test-client-secret"
os.environ["GOOGLE_REDIRECT_URI"] = "http://127.0.0.1:8766/connect/callback"
os.environ["APP_BASE_URL"] = "http://127.0.0.1:8766"
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
os.environ["DEMO_CONNECT"] = "1"  # the demo connection is a test-only mode


import pytest
from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials


@pytest.fixture(autouse=True)
def _google_rejects_test_tokens(monkeypatch):
    """Like Cloud Build (which has network): Google rejects the fake test tokens. Without this, a GA4
    call a test forgot to fake passes here (no network → TransportError) but disconnects there."""
    def rejected(self, request):
        raise RefreshError("invalid_grant (test token)")
    monkeypatch.setattr(Credentials, "refresh", rejected)


@pytest.fixture(autouse=True)
def _no_story_ga4(monkeypatch):
    """The story's extra GA4 reports (ga4/story.py) are faked per test (tests/test_story_v7.py)."""
    from sitekpi.routes import live_board

    monkeypatch.setattr(live_board, "live_story_x", lambda *a, **k: None)


@pytest.fixture(autouse=True)
def _fresh_details_cache():
    """live_extras caches per property; tests fake different GA4 answers for the same id."""
    from sitekpi.board import extras

    extras._EXTRAS_CACHE._data.clear()
