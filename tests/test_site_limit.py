"""Free plan: 1 connected site. Picking a *different* Property while one is still
connected is a new-site connection request, so it gets the upgrade prompt instead."""

from __future__ import annotations

from fastapi.testclient import TestClient

from main import app

BASE = "http://127.0.0.1:8766"


def _client() -> TestClient:
    c = TestClient(app, base_url=BASE, follow_redirects=False)
    c.get("/connect/demo")
    return c


def test_second_property_is_blocked_with_an_upgrade_prompt():
    c = _client()
    c.post("/connect/property", data={"property_id": "123456789"})
    r = c.post("/connect/property", data={"property_id": "987654321"})
    assert r.status_code == 200
    assert "無料プランは 1 サイトまでです" in r.text


def test_picking_the_same_property_again_is_not_a_new_site():
    c = _client()
    c.post("/connect/property", data={"property_id": "123456789"})
    r = c.post("/connect/property", data={"property_id": "123456789"})
    assert r.status_code == 302 and r.headers["location"] == "/live"


def test_disconnecting_first_allows_a_different_property():
    c = _client()
    c.post("/connect/property", data={"property_id": "123456789"})
    c.post("/connect/property/change")
    r = c.post("/connect/property", data={"property_id": "987654321"})
    assert r.status_code == 302 and r.headers["location"] == "/live"
