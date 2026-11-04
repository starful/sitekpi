"""Numbers first: start page → board in one step; the flow is guessed until the user fits it."""

from __future__ import annotations

import pytest
from bs4 import BeautifulSoup
from fastapi.testclient import TestClient

from main import app
from sitekpi.selection import guess_behavior


@pytest.fixture
def client():
    return TestClient(app, base_url="http://127.0.0.1:8766", follow_redirects=False)


@pytest.mark.parametrize("events,want", [
    ({"purchase": 3, "view_item": 9, "add_to_cart": 4}, ("commerce", "purchase")),
    ({"purchase": 1, "sign_up": 5, "login": 9}, ("commerce", "purchase")),  # a sale beats a sign-up
    ({"form_submit": 3, "form_start": 4, "view_item": 1, "view_search_results": 2}, ("recruit", "form_submit")),
    ({"form_submit": 3}, ("lead", "form_submit")),  # plain form → 問い合わせる
    ({"sign_up": 2, "login": 3}, ("free_trial", "sign_up")),
    ({"click": 4, "scroll": 3}, ("blog", "click")),
    ({"page_view": 10, "custom_thing": 2}, ("blog", "")),  # nothing to convert yet
])
def test_guess_behaviour_from_the_sites_events(events, want):
    assert guess_behavior(events) == want


def test_demo_guess_follows_the_demo_property():
    assert guess_behavior(None, "Demo Shop JP") == ("commerce", "demo")
    assert guess_behavior(None, "Demo Media") == ("content", "demo")


def test_start_page_offers_connect_demo_sample(client):
    html = client.get("/").text
    s = BeautifulSoup(html, "html.parser")
    hrefs = [a["href"] for a in s.select(".home-actions a")]
    assert hrefs == ["/connect", "/connect/demo?start=1", "/ec"]
    assert len(s.select(".home-steps li")) == 3
    assert s.select_one('aside.rail')  # same menu as every page


def test_demo_is_one_click_to_a_board_with_a_guess_notice(client):
    r = client.get("/connect/demo?start=1")
    assert r.headers["location"] == "/live"
    s = BeautifulSoup(client.get("/live").text, "html.parser")
    items = [i.get_text(" ", strip=True) for i in s.select(".notice .notice-item")]
    assert len(items) == 2 and "買う" in items[0] and "EC・小売" in items[1]  # both guesses, each fixable
    assert s.select_one(".notice form[action='/setup/keep']") and s.select_one(".notice [data-edit-open]")
    assert s.select_one(".notice [data-drawer-open='industry']")
    # 上のバー: 比べる業種 sits with 期間; 目安を調整 moved into the 業種 drawer
    assert s.select_one(".top-right .ind-chip") and not s.select_one(".top-right .adjust-link")
    assert s.select_one("#drawer-industry .drawer-adjust [data-ind-adjust]") and s.select_one("template#pop-bench-all")
    assert s.select_one(".where-title .where-edit")  # 流れを直す beside the title and 説明
    assert "デモ接続の見本" in str(s.select_one("template#pop-flow-help"))  # not 「GA4 を接続すると」
    assert client.get("/").headers["location"] == "/live"  # connected → straight to the board


def test_board_period_switch_and_edit_numbers_match_the_flow(client):
    import json

    client.get("/connect/demo?start=1")
    for period in ("28d", "7d"):
        s = BeautifulSoup(client.get(f"/live?period={period}").text, "html.parser")
        sel = s.select_one(".top-right form[data-period] select[name=period]")
        assert sel and not sel.has_attr("disabled")
        assert sel.select_one("option[selected]")["value"] == period
        assert s.select_one("[data-details]") is not None
        # 編集モード shows the same people as the flow it replaces (this period too)
        data = json.loads(s.select_one("#setup-data").get_text())
        nodes = s.select("#flow .flow-node")
        shown = [n.select_one(".flow-users strong").get_text() for n in nodes]
        assert f"{data['entry']:,}" == shown[0]
        for st, txt in zip(data["steps"], shown[1:]):
            assert f"{data['counts'][st['event']]:,}" == txt, (period, st)
    # the 段 drawer can save (the drawer covers the 編集中 bar)
    assert s.select_one("#drawer-step button[type=submit][form=edit-form]") and s.select_one("form#edit-form")
