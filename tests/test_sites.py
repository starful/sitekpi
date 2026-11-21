"""マイサイト一覧 /sites (sitekpi/routes/sites.py · sitekpi/portfolio.py)."""

from __future__ import annotations

from bs4 import BeautifulSoup
from fastapi.testclient import TestClient

from main import app


def _client() -> TestClient:
    return TestClient(app, base_url="http://127.0.0.1:8766", follow_redirects=False)


def _demo(c: TestClient) -> None:
    c.get("/connect/demo")
    c.post("/connect/property", data={"property_id": "123456789"})


def test_sites_needs_a_sign_in():
    assert _client().get("/sites").headers["location"] == "/connect"


def test_demo_lists_every_property_with_a_summary_in_three_languages():
    c = _client()
    _demo(c)
    for lang, title in (("ja", "サイト一覧"), ("en", "All sites"), ("ko", "사이트 목록")):
        s = BeautifulSoup(c.get(f"/sites?lang={lang}").text, "html.parser")
        assert s.select_one("h1").get_text() == title
        rows = s.select(".ss-row")
        assert len(rows) == 2
        assert rows[0].select_one(".ss-cur") and not rows[1].select_one(".ss-cur")
        assert all(r.select_one(".ss-verdict").get_text(strip=True) for r in rows)
        assert all(len(r.select(".ss-tile")) == 3 for r in rows)
        assert not s.select(".ss-pro")  # demo sees everything
    rail = c.get("/sites").text.split('<aside class="rail"', 1)[1].split("</aside>", 1)[0]
    assert '<a href="/sites" class="nav-indent is-on">' in rail


def test_open_switches_the_board_to_that_property():
    c = _client()
    _demo(c)
    r = c.post("/sites/open", data={"property_id": "987654321"})
    assert r.status_code == 303 and r.headers["location"] == "/live"
    s = BeautifulSoup(c.get("/sites").text, "html.parser")
    cur = [row.select_one(".ss-name").get_text() for row in s.select(".ss-row") if row.select_one(".ss-cur")]
    assert cur and cur[0].startswith("Demo Media")
    assert c.post("/sites/open", data={"property_id": "nope"}).headers["location"] == "/sites"


def test_free_plan_shows_only_the_open_sites_summary(monkeypatch):
    """Pro gate (billing site_compare): the list is free, other sites' summaries are locked."""
    from starlette.requests import Request

    from sitekpi import portfolio
    from sitekpi.routes import sites

    props = [{"id": "1", "name": "Shop", "account": "A"}, {"id": "2", "name": "Blog", "account": "A"}]
    calls = []

    def fake_live_row(session, prop, **kw):
        calls.append(prop["id"])
        return portfolio.demo_row({"id": prop["id"], "name": "Demo Shop"}, period=kw["period"], locale=kw["locale"])

    monkeypatch.setattr(sites, "_properties", lambda session: (props, True))
    monkeypatch.setattr(portfolio, "live_row", fake_live_row)
    monkeypatch.setattr(sites, "plan_allows", lambda uid, feature: False)
    session = {"ga4_credentials": {"token": "x"}, "ga4_property": props[0], "locale": "ja"}
    req = Request({"type": "http", "method": "GET", "path": "/sites", "headers": [], "query_string": b"",
                   "session": session})
    s = BeautifulSoup(sites.page_sites(req, period="28d").body.decode(), "html.parser")
    rows = s.select(".ss-row")
    assert calls == ["1"]  # GA4 is read only for the open site
    assert rows[0].select_one(".ss-verdict") and "is-locked" in rows[1]["class"]
    assert "1" in s.select_one(".ss-pro").get_text()

    monkeypatch.setattr(sites, "plan_allows", lambda uid, feature: True)  # Pro: every row
    calls.clear()
    s = BeautifulSoup(sites.page_sites(req, period="28d").body.decode(), "html.parser")
    assert sorted(calls) == ["1", "2"] and not s.select(".ss-pro") and not s.select(".is-locked")


def test_live_row_guesses_and_caches(monkeypatch):
    """A property other than the open one: behavior guessed from its events (仮), 5-min cache."""
    from sitekpi import portfolio
    from sitekpi.ga4 import data as g
    from sitekpi.packs import DEMO

    portfolio._ROW_CACHE._data.clear()
    hits = []
    monkeypatch.setattr(g, "discover_event_names",
                        lambda sub, **k: (hits.append(sub["ga4_property"]["id"]) or [{"name": "purchase", "count": 40},
                                                                                     {"name": "add_to_cart", "count": 90}], None))
    monkeypatch.setattr(g, "fetch_pack_overlay", lambda sub, **k: ({**DEMO["type-commerce"]["28d"]}, None))
    session = {"ga4_credentials": {"token": "x"}}
    a = portfolio.live_row(session, {"id": "7", "name": "Shop"}, period="28d", locale="en")
    b = portfolio.live_row(session, {"id": "7", "name": "Shop"}, period="28d", locale="en")
    assert a["behavior"] == "commerce" and a["guessed"] and a["verdict"]["tiles"]
    assert hits == ["7"] and b == a
    monkeypatch.setattr(g, "discover_event_names", lambda sub, **k: ([], "quota"))
    assert portfolio.live_row(session, {"id": "8", "name": "X"}, period="28d", locale="en")["error"] == "ga4"
