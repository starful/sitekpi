"""Every page shares the same rail + mobile menu; connected property shows everywhere."""

from __future__ import annotations

import re

import pytest
from fastapi.testclient import TestClient

from main import app

PAGES = {"/ec": "pack:ec", "/builder": "builder", "/connect": "connect", "/settings": "settings"}


@pytest.fixture
def client():
    return TestClient(app, base_url="http://127.0.0.1:8766", follow_redirects=False)


@pytest.mark.parametrize("path", list(PAGES))
def test_page_has_shared_rail_and_mobile_menu(client, path):
    html = client.get(path).text
    assert html.count('<aside class="rail" id="rail"') == 1
    assert "data-rail-toggle" in html and "__sitekpiRail" in html
    assert 'class="mobile-bar"' in html
    # no legacy top nav / dead links
    assert 'href="/b2c">B2C<' not in html and 'href="/content">Content<' not in html
    assert '<a class="nav"' not in html


@pytest.mark.parametrize("path,label", [("/builder", "ビルダー"), ("/connect", "GA4 接続"), ("/settings", "設定")])
def test_active_item_is_marked(client, path, label):
    html = client.get(path).text
    assert re.search(rf'<a href="{path}" class="is-on">{label}</a>', html)


def test_connected_property_appears_on_every_page(client):
    client.get("/connect/demo")
    client.post("/connect/property", data={"property_id": "123456789"})
    client.post("/connect/pack", data={"pack_slug": "ec"})
    for path in PAGES:
        assert "Demo Shop JP（デモ）" in client.get(path).text, path
