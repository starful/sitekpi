"""自社目安 via the board's bottom sheet: edit / validate / reset, scoped per property or browser."""

from __future__ import annotations

import pytest
from bs4 import BeautifulSoup
from fastapi.testclient import TestClient

from main import app
from sitekpi.packs import BENCHMARKS

JSON = {"Accept": "application/json"}


def _client() -> TestClient:
    return TestClient(app, base_url="http://127.0.0.1:8766", follow_redirects=False)


def _form(pack: str, board: str = "sample", **ranges: tuple[str, str]) -> dict[str, str]:
    data = {"pack": pack, "board": board}
    for key, spec in BENCHMARKS[pack].items():
        lo, hi = ranges.get(key, (f"{spec['low']:g}", f"{spec['high']:g}"))
        data[f"low_{key}"], data[f"high_{key}"] = lo, hi
    return data


def _sheet(html: str):
    return BeautifulSoup(html, "html.parser").select_one("dialog#bench-sheet")


def _funnel_row(html: str, label: str):
    for tr in BeautifulSoup(html, "html.parser").select("#panel-funnel tr"):
        if label in tr.get_text():
            return tr
    raise AssertionError(label)


def test_board_has_sheet_and_every_benchmark_value_opens_it():
    html = _client().get("/hr").text
    sheet = _sheet(html)
    assert sheet is not None and sheet.select_one("form[action='/benchmarks']")
    keys = {li["data-bench-row"] for li in sheet.select("[data-bench-row]")}
    assert keys == set(BENCHMARKS["hr"])
    s = BeautifulSoup(html, "html.parser")
    openers = {b["data-bench-open"] for b in s.select("button.bench-open")}
    assert openers and openers <= keys
    assert s.select_one("button.adjust-link[data-bench-open='']")
    assert 'href="/benchmarks"' not in html  # no separate page / rail item


def test_save_applies_to_board_watch_and_tooltip():
    c = _client()
    r = c.post("/benchmarks", data=_form("hr", pay_cvr=("30", "40")), headers=JSON)
    assert r.status_code == 200 and r.json() == {"ok": True, "saved": ["pay_cvr"], "reset": [
        k for k in sorted(BENCHMARKS["hr"]) if k != "pay_cvr"]}
    html = c.get("/hr").text
    row = _funnel_row(html, "開始→完了率")
    assert "35%" in row.get_text() and "自社" in row.get_text()
    assert "自社目安" in row.select_one("td.bench-cell")["title"]
    assert "開始→完了率が目安より低い" not in html
    sheet = _sheet(html)
    assert "is-custom" in sheet.select_one("[data-bench-row=pay_cvr]")["class"]
    assert sheet.select_one("#low_pay_cvr")["value"] == "30"


def test_no_js_post_redirects_back_to_board():
    r = _client().post("/benchmarks", data=_form("hr", pay_cvr=("30", "40")))
    assert r.status_code == 303 and r.headers["location"] == "/hr"


def test_validation_returns_errors_and_saves_nothing():
    c = _client()
    r = c.post("/benchmarks", headers=JSON, data=_form(
        "hr", engaged_rate=("70", "50"), bounce_rate=("x", "40"), signup_rate=("1", "150")))
    assert r.status_code == 400
    errors = r.json()["errors"]
    assert errors == {
        "engaged_rate": "下限は上限より小さくしてください",
        "bounce_rate": "数字を入れてください",
        "signup_rate": "0〜100 の範囲で入れてください",
    }
    assert "自社" not in str(_funnel_row(c.get("/hr").text, "応募CVR"))


def test_reset_one_and_all():
    c = _client()
    c.post("/benchmarks", headers=JSON, data=_form("hr", pay_cvr=("30", "40"), engaged_rate=("40", "50")))
    c.post("/benchmarks/reset", headers=JSON, data={"pack": "hr", "board": "sample", "metric": "pay_cvr"})
    custom = [li["data-bench-row"] for li in _sheet(c.get("/hr").text).select(".sheet-row.is-custom")]
    assert custom == ["engaged_rate"]
    c.post("/benchmarks/reset", headers=JSON, data={"pack": "hr", "board": "sample", "metric": ""})
    assert not _sheet(c.get("/hr").text).select(".sheet-row.is-custom")


def test_sample_targets_are_per_browser():
    a, b = _client(), _client()
    a.post("/benchmarks", headers=JSON, data=_form("hr", pay_cvr=("30", "40")))
    assert "自社" in _funnel_row(a.get("/hr").text, "開始→完了率").get_text()
    assert "自社" not in _funnel_row(b.get("/hr").text, "開始→完了率").get_text()


def test_viewing_samples_does_not_create_sessions():
    r = _client().get("/hr")
    assert "sitekpi_sid" not in r.headers.get("set-cookie", "")


def test_old_page_links_go_to_the_board():
    r = _client().get("/benchmarks?pack=ec&board=sample")
    assert r.status_code == 302 and r.headers["location"] == "/ec#bench"


@pytest.fixture
def connected(monkeypatch):
    """Browsers connected to the same GA4 property (live scope = property)."""
    import sitekpi.routes.connect as connect_routes
    import sitekpi.routes.pages as pages
    from google_auth_oauthlib.flow import Flow
    from urllib.parse import parse_qs, urlsplit

    from sitekpi.packs import DEMO

    class Creds:
        def to_json(self):
            return '{"token": "t", "refresh_token": "r", "client_id": "c", "client_secret": "s"}'

    props = [{"id": "777", "name": "Shop", "account": "Acc"}]
    monkeypatch.setattr(Flow, "fetch_token", lambda self, **kw: {"access_token": "t"})
    monkeypatch.setattr(Flow, "credentials", property(lambda self: Creds()))
    monkeypatch.setattr(connect_routes, "creds_from_session", lambda session: object())
    monkeypatch.setattr(connect_routes, "list_properties", lambda creds: props)
    monkeypatch.setattr(connect_routes, "fetch_preview", lambda creds, pid: None)
    monkeypatch.setattr(pages, "discover_event_names", lambda s, period, limit: ([], None))
    monkeypatch.setattr(pages, "fetch_pack_overlay", lambda s, **kw: (dict(DEMO["hr"]["28d"]), None))
    pages._LIVE_PACK_CACHE._data.clear()

    def login() -> TestClient:
        c = _client()
        state = parse_qs(urlsplit(c.get("/connect/google").headers["location"]).query)["state"][0]
        c.get(f"/connect/callback?state={state}&code=x")
        c.post("/connect/property", data={"property_id": "777"})
        c.post("/connect/pack", data={"pack_slug": "hr"})
        return c

    return login


def test_live_targets_are_shared_per_property_and_separate_from_samples(connected):
    a, b = connected(), connected()
    live_sheet = _sheet(a.get("/live").text)
    assert "接続中のプロパティ「Shop」" in live_sheet.get_text()
    assert live_sheet.select_one("input[name=board]")["value"] == "live"
    r = a.post("/benchmarks", headers=JSON, data=_form("hr", board="live", engaged_rate=("20", "30")))
    assert r.json()["ok"]
    assert _sheet(b.get("/live").text).select_one("#low_engaged_rate")["value"] == "20"
    assert _sheet(a.get("/hr").text).select_one("#low_engaged_rate")["value"] != "20"


def test_default_source_label_is_shown():
    html = _client().get("/hr").text
    sheet = _sheet(html)
    assert "SiteKPI 初期値" in sheet.get_text() or sheet.select("a[href^='http']")
