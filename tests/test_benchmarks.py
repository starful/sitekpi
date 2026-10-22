"""自社目安 via popovers anchored on the board's values: edit / validate / reset, scoped per property or browser."""

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


def _pops(html: str):
    """All benchmark popover templates (per metric + list) as one soup.
    (bs4 hides <template> text from get_text, so they are re-read as <section>s.)"""
    soup = BeautifulSoup(html, "html.parser")
    assert soup.select_one("#pop[hidden]") is not None
    raw = "".join(str(t) for t in soup.select("template[id^=pop-bench-]"))
    return BeautifulSoup(raw.replace("<template", "<section").replace("</template>", "</section>"), "html.parser")


def _pop(html: str, key: str):
    return _pops(html).select_one(f"section#pop-bench-{key}")


def _funnel_row(html: str, label: str):
    for tr in BeautifulSoup(html, "html.parser").select("#panel-funnel tr"):
        if label in tr.get_text():
            return tr
    raise AssertionError(label)


def test_every_benchmark_value_opens_its_own_popover():
    html = _client().get("/hr").text
    pops = _pops(html)
    keys = {t["id"].removeprefix("pop-bench-") for t in pops.select("section")} - {"all"}
    assert keys == set(BENCHMARKS["hr"])
    for k in keys:
        form = _pop(html, k).select_one("form[action='/benchmarks'][data-bench-form]")
        assert form.select_one(f"input[name=low_{k}]") and form.select_one(f"input[name=high_{k}]")
        assert not form.select(f"input[name^=low_]:not([name=low_{k}])")  # only its own metric
    s = BeautifulSoup(html, "html.parser")
    openers = {b["data-pop-open"].removeprefix("bench-") for b in s.select("button.bench-open")}
    assert openers and openers <= keys
    assert s.select_one("button.adjust-link[data-pop-open='bench-all']")
    rows = {b["data-pop-open"].removeprefix("bench-") for b in _pop(html, "all").select(".pop-row")}
    assert rows == keys
    assert 'href="/benchmarks"' not in html  # no separate page / rail item
    assert "bench-sheet" not in html


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
    assert _pop(html, "pay_cvr").select_one("#pop-low-pay_cvr")["value"] == "30"
    assert _pop(html, "pay_cvr").select_one("[data-bench-reset=pay_cvr]")
    assert "is-custom" in _pop(html, "all").select_one("[data-pop-open=bench-pay_cvr]")["class"]


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
    custom = [b["data-pop-open"] for b in _pop(c.get("/hr").text, "all").select(".pop-row.is-custom")]
    assert custom == ["bench-engaged_rate"]
    c.post("/benchmarks/reset", headers=JSON, data={"pack": "hr", "board": "sample", "metric": ""})
    assert not _pop(c.get("/hr").text, "all").select(".pop-row.is-custom")


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
    monkeypatch.setattr(pages, "discover_event_names", lambda s, period, limit: ([], None))
    monkeypatch.setattr(pages, "fetch_pack_overlay", lambda s, **kw: (dict(DEMO["hr"]["28d"]), None))
    import sitekpi.routes.flow as flow_routes
    monkeypatch.setattr(flow_routes, "fetch_flow", lambda s, **kw: (None, None))
    monkeypatch.setattr(flow_routes, "discover_event_names", lambda s, period, limit: ([], None))
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
    live = a.get("/live").text
    assert "接続中のプロパティ「Shop」" in _pop(live, "all").get_text()
    assert _pop(live, "engaged_rate").select_one("input[name=board]")["value"] == "live"
    r = a.post("/benchmarks", headers=JSON, data=_form("hr", board="live", engaged_rate=("20", "30")))
    assert r.json()["ok"]
    assert _pop(b.get("/live").text, "engaged_rate").select_one("#pop-low-engaged_rate")["value"] == "20"
    assert _pop(a.get("/hr").text, "engaged_rate").select_one("#pop-low-engaged_rate")["value"] != "20"


def test_source_is_a_button_not_a_full_url():
    html = _client().get("/ec").text
    cited = _pop(html, "engaged_rate").select_one("a.src-btn")
    assert cited and cited.get_text(strip=True) == "出典" and cited["href"].startswith("https://")
    assert cited["target"] == "_blank" and "noopener" in cited["rel"]
    assert cited["title"]  # publisher name on hover, not printed
    # no published figure → 基準なし, and the popover explains why instead of citing a source
    none = [t for t in _pops(html).select("section") if t.select_one(".pop-why")]
    assert none and "基準なし" in none[0].get_text() and not none[0].select_one("a.src-btn")


def test_added_industries_cite_their_own_published_figures():
    from sitekpi.packs.derived import DERIVED

    def cited(slug, key):
        src = BENCHMARKS[slug][key].get("source") or {}
        return src.get("label", "")

    assert "Apparel & Footwear: 60.23%" in cited("apparel", "engaged_rate")
    assert "Automotive: 41.06%" in cited("auto", "bounce_rate")
    assert "Industrials & Manufacturing" in cited("manufacturing", "engaged_rate")
    assert "Manufacturing: 2.2%" in cited("manufacturing", "signup_rate")
    assert "Legal Services: 7.4%" in cited("legal", "signup_rate")
    assert "HVAC Services: 3.1%" in cited("home_service", "signup_rate")
    assert "Financial Services: 1.9%" in cited("finance", "signup_rate")
    assert "Food & Beverage: 4.9%" in cited("food_ec", "signup_rate")
    assert "Home & Furniture: 1.4%" in cited("furniture_ec", "signup_rate")
    # a derived pack never inherits its base pack's citation
    assert "B2B SaaS" not in cited("legal", "signup_rate") and "Construction" not in cited("legal", "signup_rate")
    for slug in DERIVED:
        r = _client().get(f"/{slug}")
        assert r.status_code == 200 and DERIVED[slug]["label"]["ja"] in r.text
