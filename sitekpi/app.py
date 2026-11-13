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

from contextlib import asynccontextmanager  # noqa: E402

from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.gzip import GZipMiddleware  # noqa: E402

from sitekpi.routes.benchmarks import router as benchmarks_router  # noqa: E402
from sitekpi.routes.billing import router as billing_router  # noqa: E402
from sitekpi.routes.connect import router as connect_router  # noqa: E402
from sitekpi.routes.flow import router as flow_router  # noqa: E402
from sitekpi.routes.setup import router as setup_router  # noqa: E402
from sitekpi.routes.pages import router as pages_router  # noqa: E402
from sitekpi.static_files import CachedStaticFiles  # noqa: E402
from sitekpi.stickers import router as stickers_router  # noqa: E402
from sitekpi.feedback import router as feedback_router  # noqa: E402
from sitekpi.onboarding import router as onboarding_router  # noqa: E402
from sitekpi.routes.legal import router as legal_router  # noqa: E402
from sitekpi.firestore_store import FirestoreSessionStore, enabled as firestore_enabled  # noqa: E402
from sitekpi.session import (  # noqa: E402
    ServerSessionMiddleware,
    SQLiteSessionStore,
    session_settings,
)
from sitekpi.views.branding import BRAND_NAME  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

SESSION_MAX_AGE = 14 * 24 * 60 * 60
_session = session_settings()


@asynccontextmanager
async def _lifespan(_app: FastAPI):
    from sitekpi.views.seo import ping_search_console

    ping_search_console()  # best-effort GSC sitemap ping, once per deploy (new revision)
    yield


app = FastAPI(title=BRAND_NAME, lifespan=_lifespan)
app.add_middleware(GZipMiddleware, minimum_size=1024)
app.add_middleware(
    ServerSessionMiddleware,
    store=(FirestoreSessionStore(_session["secret"], SESSION_MAX_AGE) if firestore_enabled()
           else SQLiteSessionStore(_session["db_path"], _session["secret"], SESSION_MAX_AGE)),
    cookie_name="sitekpi_sid",
    https_only=_session["https_only"],
    same_site="lax",
    legacy_cookies=("kpistarter_session",),  # old signed-cookie sessions: expire them
)
app.mount("/static", CachedStaticFiles(directory=str(ROOT / "static")), name="static")
app.include_router(connect_router)
app.include_router(benchmarks_router)
app.include_router(billing_router)
app.include_router(flow_router)
app.include_router(setup_router)
app.include_router(stickers_router)
app.include_router(feedback_router)
app.include_router(onboarding_router)
app.include_router(legal_router)
# pages last: it owns the catch-all /{slug}
app.include_router(pages_router)
