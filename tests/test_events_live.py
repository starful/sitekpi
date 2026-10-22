"""/live イベント: show recorded events, list 0-hit pack events separately, real 前期比."""

from __future__ import annotations

import re

import pytest
from fastapi.testclient import TestClient

from main import app
from sitekpi.packs import DEMO

COUNTS = {
    # b2c pack events (sign_up not implemented on this site)
    "sign_up": 0, "pay_start": 0, "pay_success": 0,
    # the site's own + GA4 auto events
    "contact_submit": 120, "page_view": 9000, "session_start": 3000, "scroll": 2500,
}
PREV = {"contact_submit": 100, "page_view": 10000, "session_start": 3000}


@pytest.fixture
def live_client(monkeypatch):
    import sitekpi.routes.pages as pages

    info = {"property_id": "1", "property_name": "Site", "account": "", "email": "a@b"}
    monkeypatch.setattr(pages, "connection_info", lambda session: info)
    monkeypatch.setattr(pages, "saved_events", lambda session: None)
    monkeypatch.setattr(
        pages, "discover_event_names",
        lambda session, period, limit: ([{"name": n, "count": c} for n, c in COUNTS.items() if c], None),
    )

    def overlay(session, *, period, event_names, primary_event):
        o = dict(DEMO["b2c"][period])
        o.update({"event_counts": dict(COUNTS), "event_counts_prev": dict(PREV), "_ga4_property": "Site"})
        return o, None

    monkeypatch.setattr(pages, "fetch_pack_overlay", overlay)
    pages._LIVE_PACK_CACHE._data.clear()
    c = TestClient(app, base_url="http://127.0.0.1:8766", follow_redirects=False)
    c.get("/connect/demo")
    c.post("/connect/property", data={"property_id": "123456789"})
    c.post("/connect/pack", data={"pack_slug": "b2c"})
    return c


def _events_panel(html: str) -> str:
    return html.split('id="panel-events"', 1)[1].split('id="panel-biz"', 1)[0]


def _list_rows(panel: str) -> list[str]:
    tbody = panel.split("<tbody>", 1)[1].split("</tbody>", 1)[0]
    return re.findall(r'<td class="name-cell"><code>([^<]+)</code>', tbody)


def test_only_recorded_events_are_rows(live_client):
    panel = _events_panel(live_client.get("/live").text)
    rows = _list_rows(panel)
    assert "sign_up" not in rows and "pay_start" not in rows
    # the flow's events first (session_start opens every flow), then the site's own, then GA4 auto ones
    assert rows == ["session_start", "contact_submit", "page_view", "scroll"]


def test_zero_hit_pack_events_listed_as_not_tracked(live_client):
    panel = _events_panel(live_client.get("/live").text)
    foot = panel.split('class="ev-missing"', 1)[1]
    assert "<code>sign_up</code>" in foot and "<code>pay_start</code>" in foot
    assert "未計測" in foot


def test_live_deltas_are_real(live_client):
    panel = _events_panel(live_client.get("/live").text)
    tbody = panel.split("<tbody>", 1)[1]
    def delta(name):
        row = tbody.split(f"<code>{name}</code>", 1)[1].split("</tr>", 1)[0]
        return re.findall(r'<td class="num muted">([^<]*)</td>', row)[0]
    assert delta("contact_submit") == "+20%"
    assert delta("page_view") == "-10%"
    assert delta("session_start") == "+0%"
    assert delta("scroll") == "—"  # no previous-period data


def test_live_board_has_watch_without_sample_note(live_client):
    html = live_client.get("/live").text
    assert 'class="watch"' in html
    assert "watch-sample" not in html
