"""SiteKPI — FastAPI app: session middleware, static files, routers."""

from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # pragma: no cover
    pass

# Allow OAuth token exchange on local http:// (dev only)
_redirect = (os.getenv("GOOGLE_REDIRECT_URI") or os.getenv("APP_BASE_URL") or "").lower()
if _redirect.startswith("http://") and not os.getenv("OAUTHLIB_INSECURE_TRANSPORT"):
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

from fastapi import FastAPI  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402
from starlette.middleware.sessions import SessionMiddleware  # noqa: E402

from sitekpi.routes.connect import router as connect_router  # noqa: E402
from sitekpi.routes.pages import router as pages_router  # noqa: E402
from sitekpi.views.branding import BRAND_NAME  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

app = FastAPI(title=BRAND_NAME)
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET", "kpistarter-dev-secret-change-me"),
    session_cookie="kpistarter_session",
    same_site="lax",
    https_only=False,
    max_age=14 * 24 * 60 * 60,
)
app.mount("/static", StaticFiles(directory=str(ROOT / "static")), name="static")
app.include_router(connect_router)
# pages last: it owns the catch-all /{slug}
app.include_router(pages_router)
