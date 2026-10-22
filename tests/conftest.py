import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Deterministic test config (never touches the real .env values)
os.environ.setdefault("SESSION_SECRET", "test-secret")
os.environ["GOOGLE_CLIENT_ID"] = "test-client-id.apps.googleusercontent.com"
os.environ["GOOGLE_CLIENT_SECRET"] = "test-client-secret"
os.environ["GOOGLE_REDIRECT_URI"] = "http://127.0.0.1:8766/connect/callback"
os.environ["APP_BASE_URL"] = "http://127.0.0.1:8766"
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
