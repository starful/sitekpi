"""v2 pages from the design canvas: 見本ボード, 指標辞典, ダッシュボードを作る, GA4 をつなぐ, 設定."""

from __future__ import annotations

import json

import pytest
from bs4 import BeautifulSoup
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    return TestClient(app, base_url="http://127.0.0.1:8766", follow_redirects=False)


def _soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


def test_samples_goal_list_and_preview(client):
    soup = _soup(client.get("/samples?b=commerce&i=apparel").text)
    on = soup.select(".sp-goal.is-on")
    assert len(on) == 1 and on[0]["href"] == "/samples?b=commerce"
    pane = soup.select_one("[data-preview]")
    assert "買う × アパレル・ファッション" in pane.select_one("h2").get_text()
    assert pane.select_one(".sp-ind.is-on")["href"] == "/samples?b=commerce&i=apparel"
    assert pane.select_one("a.sp-btn-primary")["href"] == "/apparel"
    # the board's own いまの状態: a sentence and three numbers
    assert pane.select_one(".sp-verdict").get_text().strip() and len(pane.select(".sp-tile")) == 3
    bars = pane.select(".sp-bars li")
    assert bars[0].select_one(".sp-bar-label").get_text() == "サイトに来た" and len(pane.select(".sp-bars li.is-worst")) == 1


def test_samples_unknown_values_fall_back(client):
    soup = _soup(client.get("/samples?b=nope&i=nope").text)
    assert soup.select_one(".sp-goal.is-on") and soup.select_one(".sp-ind.is-on")
    frag = client.get("/samples/preview?b=blog").text
    assert "<html" not in frag and "全業種" in frag and 'href="/type-blog"' in frag


def test_glossary_open_cards(client):
    soup = _soup(client.get("/glossary").text)
    cards = soup.select("details.gl-card")
    assert len(cards) > 100 and all(c.select_one("summary .gl-title") for c in cards)
    eng = soup.select_one("details#engaged")
    assert eng.select_one(".gl-formula .mono").get_text() and eng.select_one(".gl-tip")
    assert eng.select_one(".gl-bench.is-on")  # judged against 業界目安 on the board
    assert not soup.select_one("details#uu .gl-bench.is-on")  # a count — not compared
    assert soup.select_one(".gl-kind[data-kind='traffic']")


def test_builder_templates_and_catalog(client):
    soup = _soup(client.get("/builder").text)
    assert [b["data-tpl"] for b in soup.select("[data-tpl]")] == ["weekly", "ads", "funnel", "seo", "blank"]
    data = json.loads(soup.select_one("#builder-data").get_text())
    ids = {i for secs in data["templates"].values() for s in secs for i in s["ids"]}
    assert ids <= set(data["catalog"])
    # sample mode: every template metric shows a number before GA4 is connected
    assert all(data["catalog"][i]["value"] not in ("", "—") for i in ids if not i.startswith("ch_display"))
    assert data["order"][0] == "uu" and soup.select_one("#drawer[hidden]")


def test_connect_reassures_before_login(client):
    soup = _soup(client.get("/connect").text)
    safe = soup.select(".cx-safe li")
    assert len(safe) == 3 and "読み取りだけ" in safe[0].get_text()
    assert soup.select_one("a.cx-demo")["href"] == "/samples"  # v5: samples, not a demo connection


def test_settings_language_cards_and_site(client):
    soup = _soup(client.get("/settings").text)
    radios = soup.select(".st-lang input[name=locale]")
    assert [r["value"] for r in radios] == ["ja", "en", "ko"] and radios[0].has_attr("checked")
    assert soup.select_one(".st-site a[href='/connect']")
    client.get("/connect/demo?start=1")
    soup = _soup(client.get("/settings").text)
    assert "Demo Shop JP" in soup.select_one(".st-site").get_text()
    assert soup.select_one(".st-site a[href='/live?edit=1#flow']") and soup.select_one("a.st-back")["href"] == "/live"
    r = client.post("/settings", data={"locale": "en"})
    assert r.headers["location"] == "/settings?saved=1"
    soup = _soup(client.get("/settings?saved=1").text)
    assert soup.select_one(".st-lang input[value=en]").has_attr("checked") and soup.select_one(".st-saved")


def test_details_new_numbers_on_a_sample_board(client):
    soup = _soup(client.get("/ec").text)

    def names(g):
        return [r.select_one(".row-name").get_text() for r in soup.select(f"#g-{g} .dt-row:not(.dt-head)")]

    assert names("revenue")[:2] == ["購入収益（GA4）", "トランザクション"]
    assert names("device") == ["モバイル", "PC", "タブレット"]
    mobile = soup.select("#g-device .dt-row:not(.dt-head)")[0]
    assert "CVR" in mobile.select_one(".dt-sub").get_text() and "is-warn" in mobile.select_one(".dt-sub")["class"]
    assert "DAU" in names("audience") and "WAU" in soup.select_one("#g-audience").get_text()
    assert {"キーイベント数", "セッションCVR"} <= set(names("funnel"))
    assert "平均セッション時間" in names("engage")
    # every row's 説明 is a card; the new ones link to their 指標辞典 entry
    assert soup.select_one("dialog#help-x_dev_mobile a[href='/glossary#device_mobile']")
    assert soup.select("#g-engage svg.spark")


def test_live_extras_reads_ga4_reports(monkeypatch):
    """The GA4 side of 8週の推移 / デバイス / 売上, with the reports faked."""
    from types import SimpleNamespace as NS

    import sitekpi.ga4.data as g
    from sitekpi.board.extras import live_extras

    def row(dims, vals):
        return NS(dimension_values=[NS(value=d) for d in dims], metric_values=[NS(value=str(v)) for v in vals])

    weeks = NS(rows=[row([str(i)], [100 + i, 150, 0.55, 400, 40, 120, 1000 * i, 10]) for i in range(8)])
    evw = NS(rows=[row([str(i), "purchase"], [10 + i]) for i in range(8)])
    tot = NS(rows=[row([], [130, 9000, 1200, 80, 300, 50000, 20, 2500])])
    act = NS(rows=[row([], [50, 300, 900])])
    dev = NS(rows=[row(["mobile"], [800, 600]), row(["desktop"], [400, 300])])
    devp = NS(rows=[row(["mobile"], [700]), row(["desktop"], [500])])
    conv = NS(rows=[row(["mobile"], [6]), row(["desktop"], [9])])
    monkeypatch.setattr(g, "connection_info", lambda s: {"property_id": "1", "property_name": "P"})
    monkeypatch.setattr(g, "HAS_DATA", True)
    monkeypatch.setattr(g, "HAS_GOOGLE_AUTH", True)
    monkeypatch.setattr(g, "creds_from_session", lambda s: object())
    monkeypatch.setattr(g, "BetaAnalyticsDataClient", lambda credentials: object())
    monkeypatch.setattr(g, "_req", lambda *a, **k: None)
    monkeypatch.setattr(g, "_event_filter", lambda names: None)
    monkeypatch.setattr(g, "_batch", lambda client, pid, reqs: [weeks, evw, tot, tot, act, dev, devp, conv][:len(reqs)])
    x, err = live_extras({}, period="28d", events=["purchase"], primary="purchase")
    assert err is None
    assert x["weeks"]["uu"] == [100.0 + i for i in range(8)] and x["weeks"]["ev:purchase"][7] == 17.0
    assert x["cur"]["events_per_session"] == 7.5 and x["cur"]["dau_mau"] == round(100 * 50 / 900, 1)
    assert x["has_revenue"] and x["cur"]["tx"] == 20
    assert [d["id"] for d in x["devices"]] == ["mobile", "desktop"] and x["devices"][0]["conv_users"] == 6


def test_glossary_stickers_use_opaque_urls(client):
    """Blockers drop images named like analytics (pageviews.gif): stickers load from /stk/<hash>."""
    s = _soup(client.get("/glossary").text)
    imgs = s.select(".gl-sticker")
    assert imgs and all(i["src"].startswith("/stk/") for i in imgs)
    pv = s.select_one("#pageviews .gl-sticker")["src"]
    assert "page" not in pv
    r = client.get(pv)
    assert r.status_code == 200 and r.headers["content-type"] == "image/gif"
    assert client.get("/stk/0000000000000000.gif").status_code == 404
