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
    assert "data-rail-toggle" in html
    src = re.search(r'<script src="(/static/js/rail\.js\?v=[0-9a-f]+)" defer>', html)
    assert src, "rail.js must be loaded"
    assert "__sitekpiRail" in client.get(src.group(1)).text
    assert 'class="mobile-bar"' in html
    # no legacy top nav / dead links
    assert 'href="/b2c">B2C<' not in html and 'href="/content">Content<' not in html
    assert '<a class="nav"' not in html


@pytest.mark.parametrize("path,label", [("/builder", "ダッシュボードを作る"), ("/samples", "見本ボード一覧"),
                                        ("/settings", "設定")])
def test_active_item_is_marked(client, path, label):
    html = client.get(path).text
    assert re.search(rf'<a href="{path}" class="is-on">{label}</a>', html)


def test_menu_sections_and_no_pack_search(client):
    html = client.get("/ec").text
    rail = html.split('<aside class="rail"', 1)[1].split("</aside>", 1)[0]
    groups = re.findall(r'<div class="nav-group">([^<]+)</div>', rail)
    assert groups == ["マイサイト", "ツール", "見本"]
    assert "pack-search" not in rail and "pack-cat" not in rail
    assert 'href="/connect" class="nav-cta' in rail  # not connected → connect CTA
    assert re.search(r'<a href="/ec" class="nav-indent is-on">EC・小売</a>', rail)  # current sample


def test_samples_gallery_links_every_industry(client):
    from sitekpi.packs import INDUSTRIES

    html = client.get("/samples").text
    for slug in INDUSTRIES:  # every industry + every behaviour's own sample
        assert f'href="/{slug}"' in html, slug


def test_connected_property_appears_on_every_page(client):
    client.get("/connect/demo")
    client.post("/connect/property", data={"property_id": "123456789"})
    client.post("/connect/pack", data={"pack_slug": "ec"})
    for path in PAGES:
        html = client.get(path).text
        assert "Demo Shop JP（デモ）" in html, path
        assert "買う × EC・小売" in html, path  # 行動 × 業種 under the property
