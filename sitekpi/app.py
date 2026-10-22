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
# If Google returns extra previously-granted scopes, don't fail the token exchange
os.environ.setdefault("OAUTHLIB_RELAX_TOKEN_SCOPE", "1")

from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.gzip import GZipMiddleware  # noqa: E402

from sitekpi.routes.benchmarks import router as benchmarks_router  # noqa: E402
from sitekpi.routes.connect import router as connect_router  # noqa: E402
from sitekpi.routes.flow import router as flow_router  # noqa: E402
from sitekpi.routes.pages import router as pages_router  # noqa: E402
from sitekpi.static_files import CachedStaticFiles  # noqa: E402
from sitekpi.session import (  # noqa: E402
    ServerSessionMiddleware,
    SQLiteSessionStore,
    session_settings,
)
from sitekpi.views.branding import BRAND_NAME  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

SESSION_MAX_AGE = 14 * 24 * 60 * 60
_session = session_settings()

app = FastAPI(title=BRAND_NAME)
app.add_middleware(GZipMiddleware, minimum_size=1024)
app.add_middleware(
    ServerSessionMiddleware,
    store=SQLiteSessionStore(_session["db_path"], _session["secret"], SESSION_MAX_AGE),
    cookie_name="sitekpi_sid",
    https_only=_session["https_only"],
    same_site="lax",
    legacy_cookies=("kpistarter_session",),  # old signed-cookie sessions: expire them
)
app.mount("/static", CachedStaticFiles(directory=str(ROOT / "static")), name="static")
app.include_router(connect_router)
app.include_router(benchmarks_router)
app.include_router(flow_router)
# pages last: it owns the catch-all /{slug}
app.include_router(pages_router)
