"""行動フロー: sample flow, live flow with per-property event mapping."""

from __future__ import annotations

from urllib.parse import parse_qs, urlsplit

import pytest
from bs4 import BeautifulSoup
from fastapi.testclient import TestClient

from main import app
from sitekpi.flow import sample_flow
from sitekpi.packs import DEMO, INDUSTRIES
from sitekpi.packs.flows import FLOW_STEPS, STEP_LABELS
from sitekpi.views.flow import flow_context

JSON = {"Accept": "application/json"}


def _client() -> TestClient:
    return TestClient(app, base_url="http://127.0.0.1:8766", follow_redirects=False)


def _soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


def _template(html: str, tid: str) -> BeautifulSoup:
    raw = str(_soup(html).select_one(f"template#{tid}"))
    return _soup(raw.replace("<template", "<section").replace("</template>", "</section>"))


def test_every_pack_has_a_flow_of_its_own_events():
    assert set(FLOW_STEPS) == set(INDUSTRIES)
    for slug, steps in FLOW_STEPS.items():
        assert 3 <= len(steps) <= 4
        assert all(s in INDUSTRIES[slug]["events"] and s in STEP_LABELS for s in steps)
        for label in (STEP_LABELS[s] for s in steps):
            assert label["ja"] and label["en"] and label["ko"]


@pytest.mark.parametrize("slug", list(FLOW_STEPS))
def test_sample_flow_only_narrows(slug):
    f = sample_flow(slug, DEMO[slug]["28d"])
    prev = f["entry"]
    for s in FLOW_STEPS[slug]:
        assert 0 < f["totals"][s] <= prev
        prev = f["totals"][s]
        for ch, steps in f["by_channel"].items():
            assert steps[s] <= f["entry_by"][ch]


def test_sample_board_shows_flow_with_worst_step_and_no_mapping_form():
    html = _client().get("/ec").text
    flow = _soup(html).select_one("section#flow")
    assert flow and "見本" in flow.select_one("h2").get_text()
    stages = flow.select(".flow-stage")
    assert [s.select_one(".flow-label").get_text() for s in stages] == ["サイトに来た", "商品を見た", "カートに追加", "購入手続きへ", "購入"]
    assert stages[0].select_one(".flow-users strong").get_text() == "68,500"
    assert len(flow.select(".flow-link.is-worst")) == 1
    assert "一番の詰まりどころ" in flow.select_one(".flow-insights").get_text()
    # channel switch carries every channel's numbers
    chs = [b["data-flow-ch"] for b in flow.select("[data-flow-ch]")]
    assert chs[0] == "all" and len(chs) == 6
    strong = stages[1].select_one(".flow-users strong")
    assert all(strong.has_attr(f"data-v-{c}") for c in chs)
    pop = _template(html, "pop-flow-add_to_cart")
    assert not pop.select("form") and pop.select_one("a[href='/connect']")
    # the flow sits right after 今見るべきこと
    assert html.index('class="watch"') < html.index('id="flow"') < html.index('class="grid-2"')


@pytest.mark.parametrize("loc,label", [("en", "Arrived"), ("ko", "사이트 방문")])
def test_flow_is_localised(loc, label):
    c = _client()
    c.post("/settings", data={"locale": loc})
    html = c.get("/hr").text
    assert _soup(html).select_one("#flow .flow-label").get_text() == label


def test_view_model_marks_untracked_steps():
    f = {"entry": 1000, "entry_by": {"Direct": 600, "Email": 400}, "sample": False,
         "totals": {"job_view": 500, "apply_start": 0, "apply_submit": 40, "entry_complete": 10},
         "by_channel": {"Direct": {"job_view": 300, "apply_submit": 10, "entry_complete": 2},
                        "Email": {"job_view": 200, "apply_submit": 30, "entry_complete": 8}}}
    steps = [{"step": s, "event": s} for s in FLOW_STEPS["hr"]]
    ctx = flow_context(pack="hr", flow=f, steps=steps, locale="ja", live=True)
    assert [s["missing"] for s in ctx["stages"]] == [False, False, True, False, False]
    assert any("応募を開始" in i and "クリック" in i for i in ctx["insights"])
    rows = {r["name"]: r for r in ctx["ch_rows"]}
    assert rows["Email"]["best"] and rows["Direct"]["low"]
    assert rows["Email"]["rate_fmt"] == "2.0%"
    # near-ties are not called best / lowest
    f["by_channel"]["Email"]["entry_complete"] = 2
    f["by_channel"]["Direct"]["entry_complete"] = 3
    ctx = flow_context(pack="hr", flow=f, steps=steps, locale="ja", live=True)
    assert not any(r["best"] or r["low"] for r in ctx["ch_rows"])
    assert not any("最も高く" in i for i in ctx["insights"])


SITE_COUNTS = {"job_view": 9000, "apply_start": 800, "submit_application": 260, "page_view": 40000, "apply_mobile": 500}
SITE_USERS = {"job_view": 5000, "apply_start": 600, "submit_application": 200, "apply_mobile": 400}


@pytest.fixture
def live(monkeypatch):
    import sitekpi.routes.connect as connect_routes
    import sitekpi.routes.flow as flow_routes
    import sitekpi.routes.pages as pages
    from google_auth_oauthlib.flow import Flow

    class Creds:
        def to_json(self):
            return '{"token": "t", "refresh_token": "r", "client_id": "c", "client_secret": "s"}'

    calls: dict[str, list] = {"overlay": [], "flow": []}
    monkeypatch.setattr(Flow, "fetch_token", lambda self, **kw: {"access_token": "t"})
    monkeypatch.setattr(Flow, "credentials", property(lambda self: Creds()))
    monkeypatch.setattr(connect_routes, "creds_from_session", lambda session: object())
    monkeypatch.setattr(connect_routes, "list_properties",
                        lambda creds: [{"id": "4242", "name": "Jobs", "account": "A"}])
    monkeypatch.setattr(connect_routes, "fetch_preview", lambda creds, pid: None)
    discovered = ([{"name": n, "count": c} for n, c in SITE_COUNTS.items()], None)
    monkeypatch.setattr(pages, "discover_event_names", lambda s, period, limit: discovered)
    monkeypatch.setattr(flow_routes, "discover_event_names", lambda s, period, limit: discovered)

    def overlay(session, *, period, event_names, primary_event):
        calls["overlay"].append(list(event_names))
        o = dict(DEMO["hr"][period])
        o.update({"event_counts": {n: SITE_COUNTS.get(n, 0) for n in event_names}, "event_counts_prev": {},
                  "signups": 0, "signup_rate": 0.0, "_ga4_property": "Jobs"})
        return o, None

    def flow(session, *, period, events):
        calls["flow"].append(list(events))
        totals = {e: SITE_USERS.get(e, 0) for e in events}
        return {"entry": 20000, "entry_by": {"Organic Search": 12000, "Direct": 8000}, "totals": totals,
                "by_channel": {"Organic Search": {e: v * 6 // 10 for e, v in totals.items()},
                               "Direct": {e: v * 4 // 10 for e, v in totals.items()}},
                "sample": False}, None

    monkeypatch.setattr(pages, "fetch_pack_overlay", overlay)
    monkeypatch.setattr(flow_routes, "fetch_flow", flow)
    pages._LIVE_PACK_CACHE._data.clear()
    flow_routes._FLOW_CACHE._data.clear()
    flow_routes._EVENTS_CACHE._data.clear()

    def login() -> TestClient:
        c = _client()
        state = parse_qs(urlsplit(c.get("/connect/google").headers["location"]).query)["state"][0]
        c.get(f"/connect/callback?state={state}&code=x")
        c.post("/connect/property", data={"property_id": "4242"})
        c.post("/connect/pack", data={"pack_slug": "hr"})
        return c

    login.calls = calls  # type: ignore[attr-defined]
    return login


def _stage(html: str, label: str):
    for st in _soup(html).select("#flow .flow-stage"):
        if st.select_one(".flow-label").get_text() == label:
            return st
    raise AssertionError(label)


def test_live_flow_maps_a_step_to_the_sites_own_event(live):
    a, b = live(), live()
    html = a.get("/live").text
    assert "is-missing" in _stage(html, "応募を送信")["class"]
    assert "見本" not in _soup(html).select_one("#flow h2").get_text()
    form = _template(html, "pop-flow-apply_submit").select_one("form[action='/flow/mapping']")
    options = [o["value"] for o in form.select("select[name=event] option")]
    assert options[0] == "" and "submit_application" in options

    r = a.post("/flow/mapping", headers=JSON, data={"pack": "hr", "step": "apply_submit", "event": "submit_application"})
    assert r.status_code == 200 and r.json() == {"ok": True, "step": "apply_submit", "event": "submit_application"}

    html = b.get("/live").text  # same property, another browser
    st = _stage(html, "応募を送信")
    assert "is-missing" not in st["class"]
    assert st.select_one("code.flow-event.is-mapped").get_text() == "submit_application"
    assert st.select_one(".flow-users strong").get_text() == "200"
    assert live.calls["flow"][-1] == ["job_view", "apply_start", "submit_application", "entry_complete"]
    assert "submit_application" in live.calls["overlay"][-1]
    # イベント: the pack event stands in for the site's event (no duplicate row)
    events = html.split('id="panel-events"', 1)[1].split('id="panel-biz"', 1)[0]
    assert "← submit_application" in events
    assert '<code>submit_application</code>' not in events
    # 主転換 (apply_submit) now counts the site's event
    assert "260" in _soup(html).select_one(".summary").get_text()

    a.post("/flow/mapping", headers=JSON, data={"pack": "hr", "step": "apply_submit", "event": ""})
    assert "is-missing" in _stage(a.get("/live").text, "応募を送信")["class"]


def test_mapping_is_validated(live):
    c = live()
    bad = c.post("/flow/mapping", headers=JSON, data={"pack": "hr", "step": "apply_submit", "event": "x y;"})
    assert bad.status_code == 400 and bad.json()["ok"] is False
    other = c.post("/flow/mapping", headers=JSON, data={"pack": "hr", "step": "purchase", "event": "buy"})
    assert other.status_code == 400
    wrong_pack = c.post("/flow/mapping", headers=JSON, data={"pack": "ec", "step": "purchase", "event": "buy"})
    assert wrong_pack.status_code == 403


def test_sample_visitors_cannot_map():
    r = _client().post("/flow/mapping", headers=JSON, data={"pack": "hr", "step": "apply_submit", "event": "x"})
    assert r.status_code == 403


def test_connect_page_picks_behaviour_first_industry_optional(live):
    c = live()
    soup = _soup(c.get("/connect").text)
    behaviours = soup.select("[data-behavior]")
    names = [b.select_one(".behavior-opt strong").get_text() for b in behaviours]
    assert names == ["買う", "会員になって使い続ける", "問い合わせる", "予約する", "申し込む", "応募する", "読む・見る"]
    rec = soup.select_one("input[value=type-recruit]").find_parent("div", class_="behavior")
    # the site records job_view + apply_start → 応募する is the closest behaviour
    assert "is-rec" in rec["class"] and "記録あり 2/4" in rec.select_one(".behavior-opt").get_text()
    assert [s["title"] for s in rec.select(".behavior-opt .mf-step.is-found")] == ["job_view", "apply_start"]
    # industries are optional, inside the behaviour, each with its own flow
    inds = [i["value"] for i in rec.select(".industries input[name=pack_slug]")]
    assert inds == ["hr", "parttime", "agency"]
    assert rec.select_one(".industries input[value=hr]").find_parent("label").select(".mf-step")
    # a behaviour alone is a valid choice → the board uses behaviour-level standards
    r = c.post("/connect/pack", data={"pack_slug": "type-commerce"})
    assert r.status_code == 302 and r.headers["location"] == "/live"
    soup = _soup(c.get("/connect").text)
    assert soup.select_one("input[value=type-commerce]").has_attr("checked")
    assert "is-selected" in soup.select_one("input[value=type-commerce]").find_parent("div", class_="behavior")["class"]


def test_behaviour_only_uses_industry_median_for_shared_metrics_only():
    from sitekpi.packs import BENCHMARKS, INDUSTRIES
    from sitekpi.packs.behaviors import SHARED_METRICS

    b = BENCHMARKS["type-commerce"]
    assert set(b) <= set(SHARED_METRICS) and "signup_to_pay" not in b and "pay_cvr" not in b
    lows = sorted(BENCHMARKS[m]["engaged_rate"]["low"] for m in ("ec", "marketplace", "d2c"))
    assert b["engaged_rate"]["low"] == lows[1]  # median
    assert b["engaged_rate"]["source"]["kind"] == "blend"
    assert INDUSTRIES["type-commerce"]["members"] == ["ec", "marketplace", "d2c"]
    # behaviour packs never show up as sample boards in the menu
    from sitekpi.packs import packs_by_category
    assert not any(s.startswith("type-") for _, _, items in packs_by_category() for s, _, _ in items)

def _labels(html: str) -> list[str]:
    return [n.get_text() for n in _soup(html).select("#flow .flow-node .flow-label")]


def _branches(html: str, step: str, pos: str) -> list[str]:
    """Labels of the other behaviours drawn above / below a step (same grid column)."""
    soup = _soup(html)
    node = soup.select_one(f"#flow .flow-node[data-pop-open='flow-{step}']")
    box = node.find_previous_sibling("div", class_="flow-up") if pos == "above" else \
        node.find_next_sibling("div", class_="flow-down")
    return [b.select_one(".flow-label").get_text() for b in box.select(".flow-branch")]


def test_live_flow_shows_other_behaviours_above_and_below_a_step(live):
    a, b = live(), live()
    html = a.get("/live").text
    soup = _soup(html)
    assert soup.select_one("#flow .flow-add[data-pop-open='flow-add-apply_start-above']")
    assert soup.select_one("#flow .flow-add[data-pop-open='flow-add-apply_start-below']")
    assert not soup.select("#flow .flow-add[data-pop-open^='flow-add-entry-']")
    add = _template(html, "pop-flow-add-apply_start-below").select_one("form[action='/flow/branch']")
    assert add.select_one("input[name=pos]")["value"] == "below"

    def post(**data):
        return a.post("/flow/branch", headers=JSON, data={"pack": "hr", **data})

    r = post(action="add", at="apply_start", pos="below", event="apply_mobile", label="スマホで応募開始")
    assert r.status_code == 200 and r.json()["ok"]
    first = r.json()["id"]
    html = b.get("/live").text  # same property → same flow
    # the main path is unchanged — the branch sits under its step
    assert _labels(html) == ["サイトに来た", "求人を見た", "応募を開始", "応募を送信", "エントリー完了"]
    assert _branches(html, "apply_start", "below") == ["スマホで応募開始"]
    br = _soup(html).select_one("#flow .flow-branch")
    assert br.select_one(".flow-users strong").get_text() == "400"
    assert "「求人を見た」から" in br.get_text() and "8.0%" in br.get_text()  # 400 / 5,000
    assert "apply_mobile" in live.calls["flow"][-1]
    edit = _template(html, f"pop-flow-b{first}")
    assert "「応募を開始」の 66.7%" in edit.get_text()
    assert edit.select_one("input[name=action][value=update]") and edit.select_one("input[name=action][value=delete]")

    assert post(action="add", at="apply_start", pos="above", event="page_view", label="PV").json()["ok"]
    assert post(action="add", at="job_view", pos="below", event="page_view").json()["ok"]
    html = a.get("/live").text
    assert _branches(html, "apply_start", "above") == ["PV"]
    assert _branches(html, "job_view", "below") == ["page_view"]
    full = post(action="add", at="entry_complete", pos="below", event="page_view")
    assert full.status_code == 400 and "3 つ" in full.json()["error"]
    assert not _soup(html).select("#flow .flow-add")

    assert post(action="update", id=first, event="apply_mobile", label="スマホ").json()["ok"]
    assert post(action="delete", id=first).json()["ok"]
    html = a.get("/live").text
    assert _branches(html, "apply_start", "below") == [] and _branches(html, "apply_start", "above") == ["PV"]
    assert post(action="update", id="nope", event="x").status_code == 404


def test_branches_are_validated(live):
    c = live()
    post = lambda **d: c.post("/flow/branch", headers=JSON, data={"pack": "hr", **d})  # noqa: E731
    assert post(action="add", at="apply_start", pos="below", event="bad name!").status_code == 400
    assert post(action="add", at="entry", pos="below", event="x").status_code == 400
    assert post(action="add", at="apply_start", pos="left", event="x").status_code == 400
    assert _client().post("/flow/branch", headers=JSON, data={
        "pack": "hr", "action": "add", "at": "apply_start", "pos": "below", "event": "x"}).status_code == 403
    assert post(action="add", at="apply_start", pos="below", event="ok_event",
                label="  a   very long label that keeps going on  ").json()["ok"]
    assert "a very long label that k" in _branches(c.get("/live").text, "apply_start", "below")


def test_live_board_with_behaviour_only(live):
    c = live()
    c.post("/connect/pack", data={"pack_slug": "type-recruit"})
    html = c.get("/live").text
    soup = _soup(html)
    assert "応募する" in soup.select_one("header.top .meta").get_text()
    pop = _template(html, "pop-bench-engaged_rate")
    assert pop.select_one(".src-blend").get_text() == "業種の中央値"
    assert "人事・採用 / アルバイト・シフト / 人材紹介・エージェント" in pop.select_one(".src-blend")["title"]
    assert not soup.select("template#pop-bench-pay_cvr")  # funnel-step rate: no standard without an industry
    assert [n.get_text() for n in soup.select("#flow .flow-node .flow-label")][:2] == ["サイトに来た", "求人を見た"]
    # mapping / branches work for a behaviour pack too
    r = c.post("/flow/mapping", headers=JSON, data={"pack": "type-recruit", "step": "apply_submit", "event": "submit_application"})
    assert r.json()["ok"]
