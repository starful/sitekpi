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


@pytest.mark.parametrize("path,label", [("/builder", "ダッシュボードを作る"),
                                        ("/glossary", "指標辞典"),
                                        ("/samples", "見本ボード一覧"),
                                        ("/settings", "設定")])
def test_active_item_is_marked(client, path, label):
    html = client.get(path).text
    assert re.search(rf'<a href="{path}" class="is-on">{label}</a>', html)


def test_connected_menu_has_connect_manage(client):
    client.get("/connect/demo")
    client.post("/connect/property", data={"property_id": "123456789"})
    # /live may redirect until setup is ready — any shelled page is enough
    html = client.get("/ec").text
    rail = html.split('<aside class="rail"', 1)[1].split("</aside>", 1)[0]
    assert 'href="/connect"' in rail and "接続・切断" in rail
    assert 'href="/glossary"' in rail and "指標辞典" in rail


def test_glossary_lists_help_metrics(client):
    from sitekpi.metrics.help import HELP

    html = client.get("/glossary").text
    assert "指標辞典" in html
    assert "エンゲージメント率" in html
    for key in ("uu", "engaged", "signup_cvr", "ev_purchase", "ch_organic_search", "mrr"):
        assert f'id="{key}"' in html
    assert len(HELP) >= 80
    assert "gl-list" in html  # 3-col grid container


def test_glossary_switches_locale(client):
    from sitekpi.metrics.help import get_help

    client.post("/settings", data={"locale": "en"})
    html = client.get("/glossary").text
    assert "Metric glossary" in html
    assert get_help("uu", "en")["title"] in html
    assert "Engagement rate" in html

    client.post("/settings", data={"locale": "ko"})
    html = client.get("/glossary").text
    assert "지표 사전" in html
    assert get_help("uu", "ko")["title"] in html


def test_beginner_scene_has_three_metrics_and_cta(client):
    """/beginner stays reachable by URL; it is not a 見本 rail item."""
    html = client.get("/beginner").text
    assert "はじめての5分" in html
    assert "問い合わせ完了" in html
    assert "問い合わせ率" in html
    assert "しっかり見た人の割合" in html
    assert 'href="/connect"' in html
    assert html.count('class="beg-metric ') == 3
    rail = html.split('<aside class="rail"', 1)[1].split("</aside>", 1)[0]
    assert 'href="/beginner"' not in rail


def test_menu_sections_and_no_pack_search(client):
    html = client.get("/ec").text
    rail = html.split('<aside class="rail"', 1)[1].split("</aside>", 1)[0]
    groups = re.findall(r'<div class="nav-group">([^<]+)</div>', rail)
    assert groups == ["マイサイト", "見本（例の数字）", "ツール"]  # v5: samples right under マイサイト
    assert "pack-search" not in rail and "pack-cat" not in rail
    assert 'href="/connect" class="nav-cta' in rail  # not connected → connect CTA
    assert 'href="/samples"' in rail and 'href="/glossary"' in rail and 'href="/builder"' in rail
    assert 'href="/beginner"' not in rail  # not a menu item
    assert re.search(r'<a href="/ec" class="nav-sample is-on"><span class="nav-ex" aria-hidden="true">例</span>EC・小売</a>', rail)  # current sample, marked 例
    assert "data-feedback-open" not in rail  # v5: the メモ panel replaced 「ご意見を送る」


def test_connected_rail_has_live_setup_connect(client):
    client.get("/connect/demo")
    client.post("/connect/property", data={"property_id": "123456789"})
    html = client.get("/ec").text
    rail = html.split('<aside class="rail"', 1)[1].split("</aside>", 1)[0]
    assert 'href="/live"' in rail
    assert 'href="/live?edit=1#flow"' in rail and "サイトの設定" in rail
    assert 'href="/connect"' in rail and "接続・切断" in rail
    assert 'href="/beginner"' not in rail


def test_samples_gallery_links_every_industry(client):
    from sitekpi.packs import INDUSTRIES

    from sitekpi.packs.behaviors import BEHAVIORS, slug_of

    html = client.get("/samples").text
    for cat in BEHAVIORS:  # the goal list: one entry per behaviour
        assert f'href="/samples?b={cat}"' in html, cat
    reach: set[str] = set()
    for cat in BEHAVIORS:  # each goal's preview offers its industries and opens a real board
        members = INDUSTRIES[slug_of(cat)]["members"]
        for m in members:
            page = client.get(f"/samples/preview?b={cat}&i={m}").text
            assert f'href="/{m}"' in page and f'href="/samples?b={cat}&amp;i={m}"' in page, (cat, m)
            reach.add(m)
        if not members:
            assert f'href="/{slug_of(cat)}"' in client.get(f"/samples/preview?b={cat}").text
    assert {s for s in INDUSTRIES if not s.startswith("type-")} <= reach


def test_connected_property_appears_on_every_page(client):
    client.get("/connect/demo")
    client.post("/connect/property", data={"property_id": "123456789"})
    client.post("/connect/pack", data={"pack_slug": "ec"})
    for path in PAGES:
        html = client.get(path).text
        assert "Demo Shop JP（デモ）" in html, path
        assert "買う × EC・小売" in html, path  # 行動 × 業種 under the property
