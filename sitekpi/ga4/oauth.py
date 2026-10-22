"""GA4 OAuth helpers — client config, session credentials, property list, preview."""

from __future__ import annotations

import json
import os
from typing import Any

# Optional Google libs — page still works in setup/demo mode without them installed
try:
    from google.auth.exceptions import RefreshError, TransportError
    from google.auth.transport.requests import Request as GoogleAuthRequest
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import Flow

    HAS_GOOGLE_AUTH = True
except ImportError:  # pragma: no cover
    HAS_GOOGLE_AUTH = False
    Flow = None  # type: ignore[misc, assignment]
    Credentials = None  # type: ignore[misc, assignment]
    GoogleAuthRequest = None  # type: ignore[misc, assignment]
    RefreshError = TransportError = Exception  # type: ignore[misc, assignment]

try:
    from google.analytics.admin_v1beta import AnalyticsAdminServiceClient
    from google.analytics.admin_v1beta.types import ListAccountSummariesRequest

    HAS_ADMIN = True
except ImportError:  # pragma: no cover
    HAS_ADMIN = False
    AnalyticsAdminServiceClient = None  # type: ignore[misc, assignment]

try:
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import DateRange, Metric, RunReportRequest

    HAS_DATA = True
except ImportError:  # pragma: no cover
    HAS_DATA = False
    BetaAnalyticsDataClient = None  # type: ignore[misc, assignment]

SCOPES = ["https://www.googleapis.com/auth/analytics.readonly"]

DEMO_PROPERTIES = [
    {
        "id": "123456789",
        "name": "Demo Shop JP",
        "account": "Demo Account",
    },
    {
        "id": "987654321",
        "name": "Demo Media",
        "account": "Demo Account",
    },
]


def _env(name: str, default: str = "") -> str:
    return (os.getenv(name) or default).strip()


def oauth_configured() -> bool:
    return bool(_env("GOOGLE_CLIENT_ID") and _env("GOOGLE_CLIENT_SECRET"))


def redirect_uri() -> str:
    return _env(
        "GOOGLE_REDIRECT_URI",
        "http://127.0.0.1:8766/connect/callback",
    )


def base_url() -> str:
    return _env("APP_BASE_URL", "http://127.0.0.1:8766")


def client_config() -> dict[str, Any]:
    return {
        "web": {
            "client_id": _env("GOOGLE_CLIENT_ID"),
            "client_secret": _env("GOOGLE_CLIENT_SECRET"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [redirect_uri()],
        }
    }


def creds_from_session(session: dict[str, Any]) -> Any | None:
    if not HAS_GOOGLE_AUTH:
        return None
    info = session.get("ga4_credentials")
    if not info:
        return None
    creds = Credentials.from_authorized_user_info(info, SCOPES)
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(GoogleAuthRequest())
        except RefreshError:
            # Revoked / expired grant: forget it so /connect can start over
            # instead of failing on every request.
            for key in ("ga4_credentials", "ga4_property", "ga4_email"):
                session.pop(key, None)
            return None
        except TransportError:
            return None  # network hiccup — keep the grant, try again next request
        session["ga4_credentials"] = json.loads(creds.to_json())
    return creds


def list_properties(creds: Any) -> list[dict[str, str]]:
    if not HAS_ADMIN:
        return []
    client = AnalyticsAdminServiceClient(credentials=creds)
    out: list[dict[str, str]] = []
    for summary in client.list_account_summaries(request=ListAccountSummariesRequest()):
        account_name = summary.display_name or summary.name
        for ps in summary.property_summaries:
            # property resource name: properties/123456
            pid = ps.property.split("/")[-1] if ps.property else ""
            if not pid:
                continue
            out.append(
                {
                    "id": pid,
                    "name": ps.display_name or pid,
                    "account": account_name,
                }
            )
    return out


def fetch_preview(creds: Any, property_id: str) -> dict[str, Any] | None:
    if not HAS_DATA:
        return None
    client = BetaAnalyticsDataClient(credentials=creds)
    req = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date="28daysAgo", end_date="yesterday")],
        metrics=[
            Metric(name="activeUsers"),
            Metric(name="sessions"),
            Metric(name="screenPageViews"),
            Metric(name="engagementRate"),
        ],
    )
    resp = client.run_report(req)
    if not resp.rows:
        return {
            "activeUsers": "0",
            "sessions": "0",
            "screenPageViews": "0",
            "engagementRate": "0%",
            "period": "直近28日",
        }
    row = resp.rows[0]
    values = [v.value for v in row.metric_values]
    eng = values[3] if len(values) > 3 else "0"
    try:
        eng_pct = f"{float(eng) * 100:.1f}%"
    except ValueError:
        eng_pct = eng
    return {
        "activeUsers": values[0] if values else "0",
        "sessions": values[1] if len(values) > 1 else "0",
        "screenPageViews": values[2] if len(values) > 2 else "0",
        "engagementRate": eng_pct,
        "period": "直近28日",
    }


def demo_preview(property_id: str) -> dict[str, Any]:
    if property_id == "987654321":
        return {
            "activeUsers": "86,400",
            "sessions": "112,000",
            "screenPageViews": "212,800",
            "engagementRate": "51.4%",
            "period": "直近28日（デモ）",
        }
    return {
        "activeUsers": "38,920",
        "sessions": "54,210",
        "screenPageViews": "140,946",
        "engagementRate": "58.6%",
        "period": "直近28日（デモ）",
    }
