"""自社目安: edit / validate / reset, scoped per property (live) or per browser (samples)."""

from __future__ import annotations

import re

import pytest
from bs4 import BeautifulSoup
from fastapi.testclient import TestClient

from main import app
from sitekpi.packs import BENCHMARKS


def _client() -> TestClient:
    return TestClient(app, base_url="http://127.0.0.1:8766", follow_redirects=False)


def _form(pack: str, board: str = "sample", **ranges: tuple[str, str]) -> dict[str, str]:
    data = {"pack": pack, "board": board}
    for key, spec in BENCHMARKS[pack].items():
        lo, hi = ranges.get(key, (f"{spec['low']:g}", f"{spec['high']:g}"))
        data[f"low_{key}"], data[f"high_{key}"] = lo, hi
    return data


def _funnel_cell(html: str, label: str) -> BeautifulSoup:
    s = BeautifulSoup(html, "html.parser")
    for tr in s.select("#panel-funnel tr"):
        if label in tr.get_text():
            return tr
    raise AssertionError(label)


def test_page_explains_default_source_honestly():
    html = _client().get("/benchmarks?pack=hr").text
    assert "公開統計や調査にもとづく値ではありません（出典なし）" in html
    assert "40–65%" in html  # default shown next to the inputs


def test_save_applies_to_board_watch_and_tooltip():
    c = _client()
    r = c.post("/benchmarks", data=_form("hr", pay_cvr=("30", "40")))
    assert r.status_code == 303 and "saved=1" in r.headers["location"]
    html = c.get("/hr").text
    row = _funnel_cell(html, "開始→完了率")
    assert "35%" in row.get_text() and "自社" in row.get_text()
    assert "自社目安" in row.select_one("td.bench-cell")["title"]
    # 34.2% is now inside 30–40 → no longer flagged in 今見るべきこと
    assert "開始→完了率が目安より低い" not in html
    # other metrics keep the honest default label
    assert "SiteKPI 初期値（仮・出典なし）" in html


def test_saving_the_default_values_stores_nothing():
    c = _client()
    c.post("/benchmarks", data=_form("ec"))
    page = c.get("/benchmarks?pack=ec").text
    assert "is-custom" not in page


def test_validation_keeps_input_and_saves_nothing():
    c = _client()
    r = c.post("/benchmarks", data=_form("hr", engaged_rate=("70", "50"), bounce_rate=("x", "40"),
                                         signup_rate=("1", "150")))
    assert r.status_code == 400
    s = BeautifulSoup(r.text, "html.parser")
    errors = {tr.select_one(".metric").get_text(): tr.select_one(".row-error").get_text()
              for tr in s.select("tr.has-error")}
    assert errors["エンゲージ率"] == "下限は上限より小さくしてください"
    assert errors["すぐ離脱に近い率"] == "数字を入れてください"
    assert any(v == "0〜100 の範囲で入れてください" for v in errors.values())
    assert s.select_one("#low_engaged_rate")["value"] == "70"  # input kept
    assert "自社" not in c.get("/hr").text.split('id="panel-funnel"')[1].split("</section>")[0]


def test_reset_one_and_all():
    c = _client()
    c.post("/benchmarks", data=_form("hr", signup_to_pay=("30", "40"), engaged_rate=("40", "50")))
    c.post("/benchmarks/reset", data={"pack": "hr", "board": "sample", "metric": "signup_to_pay"})
    page = BeautifulSoup(c.get("/benchmarks?pack=hr").text, "html.parser")
    custom = [tr.select_one(".metric").get_text() for tr in page.select("tr.is-custom")]
    assert custom == ["エンゲージ率"]
    c.post("/benchmarks/reset", data={"pack": "hr", "board": "sample", "metric": ""})
    assert "is-custom" not in c.get("/benchmarks?pack=hr").text


def test_sample_targets_are_per_browser():
    a, b = _client(), _client()
    a.post("/benchmarks", data=_form("hr", pay_cvr=("30", "40")))
    assert "自社" in _funnel_cell(a.get("/hr").text, "開始→完了率").get_text()
    assert "自社" not in _funnel_cell(b.get("/hr").text, "開始→完了率").get_text()


def test_viewing_samples_does_not_create_sessions():
    c = _client()
    r = c.get("/hr")
    assert "sitekpi_sid" not in r.headers.get("set-cookie", "")


@pytest.fixture
def connected(monkeypatch):
    """Two browsers connected to the same GA4 property (live scope = property)."""
    import sitekpi.routes.connect as connect_routes
    from google_auth_oauthlib.flow import Flow
    from urllib.parse import parse_qs, urlsplit

    class Creds:
        def to_json(self):
            return '{"token": "t", "refresh_token": "r", "client_id": "c", "client_secret": "s"}'

    props = [{"id": "777", "name": "Shop", "account": "Acc"}]
    monkeypatch.setattr(Flow, "fetch_token", lambda self, **kw: {"access_token": "t"})
    monkeypatch.setattr(Flow, "credentials", property(lambda self: Creds()))
    monkeypatch.setattr(connect_routes, "creds_from_session", lambda session: object())
    monkeypatch.setattr(connect_routes, "list_properties", lambda creds: props)
    monkeypatch.setattr(connect_routes, "fetch_preview", lambda creds, pid: None)

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
    r = a.post("/benchmarks", data=_form("hr", board="live", engaged_rate=("20", "30")))
    assert r.status_code == 303 and "board=live" in r.headers["location"]
    def low(page: str) -> str:
        return BeautifulSoup(page, "html.parser").select_one("#low_engaged_rate")["value"]

    page_b = b.get("/benchmarks?board=live").text
    assert "接続中のプロパティ「Shop」" in page_b and low(page_b) == "20"
    # the sample /hr board of the same browser is not affected
    assert low(a.get("/benchmarks?pack=hr&board=sample").text) != "20"


def test_live_board_falls_back_to_sample_scope_when_not_connected():
    page = _client().get("/benchmarks?board=live&pack=ec").text
    assert "見本ボード用の目安" in page
    assert re.search(r'<option value="ec" selected>', page)
