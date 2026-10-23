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
        assert steps[:2] == ["session_start", "user_engagement"]  # worldwide GA4 start: opened, really looked
        assert 5 <= len(steps) <= 6
        assert all(s in ("session_start", "user_engagement") or s in INDUSTRIES[slug]["events"] for s in steps)
        assert all(s in STEP_LABELS for s in steps)
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
    assert [s.select_one(".flow-label").get_text() for s in stages] == ["サイトに来た", "サイトを開いた", "しっかり見た（10秒以上）", "商品を見た", "カートに追加", "購入手続きへ", "購入"]
    assert stages[0].select_one(".flow-users strong").get_text() == "68,500"
    assert "流入元: Organic Search 25%" in stages[0].get_text()  # where visitors came from
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
         "totals": {"session_start": 990, "user_engagement": 700, "job_view": 500, "apply_start": 0, "apply_submit": 40, "entry_complete": 10},
         "by_channel": {"Direct": {"job_view": 300, "apply_submit": 10, "entry_complete": 2},
                        "Email": {"job_view": 200, "apply_submit": 30, "entry_complete": 8}}}
    steps = [{"step": s, "event": s} for s in FLOW_STEPS["hr"]]
    ctx = flow_context(pack="hr", flow=f, steps=steps, locale="ja", live=True)
    assert [s["missing"] for s in ctx["stages"]] == [False, False, False, False, True, False, False]
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


SITE_COUNTS = {"session_start": 21000, "user_engagement": 14000, "page_view": 40000, "view_search_results": 7000, "view_item": 9000, "form_start": 800,
               "submit_application": 260, "apply_mobile": 500}
SITE_USERS = {"session_start": 19800, "user_engagement": 12000, "page_view": 19000, "view_search_results": 6000, "view_item": 5000, "form_start": 600,
              "submit_application": 200, "apply_mobile": 400}


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
    from sitekpi.flow import get_mapping_store

    with get_mapping_store()._connect() as db:  # each test starts from the standard flows
        for table in ("event_mappings", "flow_branches", "flow_custom"):
            db.execute(f"DELETE FROM {table} WHERE scope = 'prop:4242'")

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
    labels = [n.get_text() for n in _soup(html).select("#flow .flow-node .flow-label")]
    assert labels == ["サイトに来た", "サイトを開いた", "しっかり見た（10秒以上）", "求人を検索", "求人を見た", "応募を開始", "応募を送信"]
    assert "is-missing" in _stage(html, "応募を送信")["class"]  # site sends submit_application
    assert "見本" not in _soup(html).select_one("#flow h2").get_text()
    form = _template(html, "pop-flow-form_submit").select_one("form[action='/flow/mapping']")
    options = [o["value"] for o in form.select("select[name=event] option")]
    assert options[0] == "" and "submit_application" in options

    r = a.post("/flow/mapping", headers=JSON, data={"pack": "type-recruit", "step": "form_submit", "event": "submit_application"})
    assert r.status_code == 200 and r.json() == {"ok": True, "step": "form_submit", "event": "submit_application"}

    html = b.get("/live").text  # same property, another browser
    st = _stage(html, "応募を送信")
    assert "is-missing" not in st["class"]
    assert st.select_one("code.flow-event.is-mapped").get_text() == "submit_application"
    assert st.select_one(".flow-users strong").get_text() == "200"
    assert live.calls["flow"][-1] == ["session_start", "user_engagement", "view_search_results", "view_item", "form_start", "submit_application"]
    assert "submit_application" in live.calls["overlay"][-1]
    # イベント: the flow's event stands in for the site's event (no duplicate row)
    events = html.split('id="panel-events"', 1)[1].split('id="panel-biz"', 1)[0]
    assert "← submit_application" in events
    assert '<code>submit_application</code>' not in events
    # 主転換 (応募完了 = form_submit) now counts the site's event
    assert "260" in _soup(html).select_one(".summary").get_text()

    a.post("/flow/mapping", headers=JSON, data={"pack": "type-recruit", "step": "form_submit", "event": ""})
    assert "is-missing" in _stage(a.get("/live").text, "応募を送信")["class"]


def test_mapping_is_validated(live):
    c = live()
    bad = c.post("/flow/mapping", headers=JSON, data={"pack": "type-recruit", "step": "form_submit", "event": "x y;"})
    assert bad.status_code == 400 and bad.json()["ok"] is False
    other = c.post("/flow/mapping", headers=JSON, data={"pack": "type-recruit", "step": "purchase", "event": "buy"})
    assert other.status_code == 400
    wrong_pack = c.post("/flow/mapping", headers=JSON, data={"pack": "ec", "step": "purchase", "event": "buy"})
    assert wrong_pack.status_code == 403


def test_sample_visitors_cannot_map():
    r = _client().post("/flow/mapping", headers=JSON, data={"pack": "hr", "step": "apply_submit", "event": "x"})
    assert r.status_code == 403


def test_setup_is_three_short_steps(live):
    c = live()
    # choosing a property leads into the wizard when nothing is set yet
    c.post("/connect/property/change")
    r = c.post("/connect/property", data={"property_id": "4242"})
    assert r.headers["location"] == "/setup"
    assert c.get("/setup").headers["location"] == "/setup/flow"
    # ① flow: one question, closest flow first
    soup = _soup(c.get("/setup/flow").text)
    assert soup.select_one("h1").get_text() == "あなたのサイトに近い流れは？"
    first = soup.select("button.choice")[0]
    assert first["value"] == "recruit" and first.find_parent("section", class_="flow-closest")
    # the shared start is drawn once; cards only show what differs
    assert [s["title"] for s in soup.select(".flow-common .mf-step[title]")] == ["session_start", "user_engagement"]
    assert [s["title"] for s in first.select(".mf-step.is-found")] == ["view_search_results", "view_item", "form_start"]
    assert len(first.select(".pack-hits, .pack-rec, .pack-now")) <= 1  # one badge at most
    assert soup.select("details.flow-group") and not any(d.has_attr("open") for d in soup.select("details.flow-group"))
    names = [b.select_one("strong").get_text() for b in soup.select("button[name=behavior]")]
    assert len(set(names)) == 18 and "ブログ・記事を読んでもらう" in names
    assert c.get("/setup/adjust").headers["location"] == "/setup/flow"  # can't skip ahead
    r = c.post("/setup/flow", data={"behavior": "recruit"})
    assert r.headers["location"] == "/setup/industry"
    # ② industry: the flow's industries as big choices, the rest folded away
    soup = _soup(c.get("/setup/industry").text)
    assert [b["value"] for b in soup.select(".choice-grid button")] == ["hr", "parttime", "agency"]
    assert "出典つきの目安" in soup.select_one(".choice-grid button").get_text()
    assert "legal" in [b["value"] for b in soup.select(".more-inds button")]
    r = c.post("/setup/industry", data={"industry": "hr"})
    assert r.headers["location"] == "/setup/adjust"
    # ③ adjust: steps the site doesn't record are flagged
    soup = _soup(c.get("/setup/adjust").text)
    rows = soup.select("ol.adj-steps > [data-step]")
    assert [r.select_one("[name=label]")["value"] for r in rows] == [
        "サイトを開いた", "しっかり見た（10秒以上）", "求人を検索", "求人を見た", "応募を開始", "応募を送信"]
    assert ["is-missing" in r["class"] for r in rows] == [False, False, False, False, False, True]
    assert "1 段のイベントが GA4 に見つかりません" in soup.get_text()
    assert "submit_application" in [o["value"] for o in rows[5].select("select[name=event] option")]
    # connect page now just summarises, with links to change each step
    soup = _soup(c.get("/connect").text)
    assert [a["href"] for a in soup.select(".setup-sum .sum-rows a")] == ["/setup/flow", "/setup/industry", "/setup/adjust"]
    assert not soup.select("form[action='/connect/selection']")


def _form_lists(pairs):
    out: dict[str, list[str]] = {}
    for k, v in pairs:
        out.setdefault(k, []).append(v)
    return out


def test_adjust_the_flow_to_the_site(live):
    c = live()
    data = []
    for key, ev, label in [("session_start", "session_start", "サイトを開いた"), ("", "apply_mobile", "スマホ応募"),
                           ("form_submit", "submit_application", "応募を送信")]:
        data += [("key", key), ("event", ev), ("label", label)]
    r = c.post("/setup/adjust", data=_form_lists(data))
    assert r.status_code == 303 and r.headers["location"] == "/live"
    html = c.get("/live").text
    labels = [n.get_text() for n in _soup(html).select("#flow .flow-node .flow-label")]
    assert labels == ["サイトに来た", "サイトを開いた", "スマホ応募", "応募を送信"]
    assert live.calls["flow"][-1] == ["session_start", "apply_mobile", "submit_application"]
    assert "260" in _soup(html).select_one(".summary").get_text()  # last step = 主転換
    rows = _soup(c.get("/setup/adjust").text).select("ol.adj-steps > [data-step]")
    assert [r.select_one("[name=label]")["value"] for r in rows] == ["サイトを開いた", "スマホ応募", "応募を送信"]
    bad = [("key", ""), ("event", "bad name"), ("label", "")]
    assert "イベント名" in c.post("/setup/adjust", data=_form_lists(bad)).text
    many = [x for n in range(9) for x in (("key", ""), ("event", f"e{n}"), ("label", ""))]
    assert "8 つまで" in c.post("/setup/adjust", data=_form_lists(many)).text
    std = [x for k in ("session_start", "user_engagement", "view_search_results", "view_item", "form_start", "form_submit")
           for x in (("key", k), ("event", k), ("label", ""))]
    c.post("/setup/adjust", data=_form_lists(std))
    labels = [n.get_text() for n in _soup(c.get("/live").text).select("#flow .flow-node .flow-label")]
    assert labels == ["サイトに来た", "サイトを開いた", "しっかり見た（10秒以上）", "求人を検索", "求人を見た", "応募を開始", "応募を送信"]


def test_industry_of_another_kind_uses_site_wide_standards_only(live):
    c = live()
    c.post("/setup/flow", data={"behavior": "commerce"})
    c.post("/setup/industry", data={"industry": "legal"})
    html = c.get("/live").text
    soup = _soup(html)
    assert "買う × 士業・法律事務所" in soup.select_one("header.top .meta").get_text()
    assert "Consulting & Professional Services" in _template(html, "pop-bench-engaged_rate").select_one("a.src-btn")["title"]
    # CVR standards always follow the chosen industry, whatever the flow
    assert _template(html, "pop-bench-signup_rate").select_one("a.src-btn, .pop-why")
    c.post("/setup/industry", data={"industry": "apparel"})
    assert "Baymard" in _template(c.get("/live").text, "pop-bench-signup_to_pay").select_one("a.src-btn")["title"]

def test_behaviour_only_uses_industry_median_for_shared_metrics_only():
    from sitekpi.packs import BENCHMARKS, INDUSTRIES
    from sitekpi.packs.behaviors import SHARED_METRICS

    b = BENCHMARKS["type-commerce"]
    assert set(b) <= set(SHARED_METRICS) and "signup_to_pay" not in b and "pay_cvr" not in b
    from statistics import median
    members = INDUSTRIES["type-commerce"]["members"]
    assert b["engaged_rate"]["low"] == round(median(BENCHMARKS[m]["engaged_rate"]["low"] for m in members), 2)
    assert b["engaged_rate"]["source"]["kind"] == "blend"
    assert INDUSTRIES["type-commerce"]["members"][:3] == ["ec", "marketplace", "d2c"]
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
    assert soup.select_one("#flow .flow-add[data-pop-open='flow-add-form_start-above']")
    assert soup.select_one("#flow .flow-add[data-pop-open='flow-add-form_start-below']")
    assert not soup.select("#flow .flow-add[data-pop-open^='flow-add-entry-']")
    add = _template(html, "pop-flow-add-form_start-below").select_one("form[action='/flow/branch']")
    assert add.select_one("input[name=pos]")["value"] == "below"

    def post(**data):
        return a.post("/flow/branch", headers=JSON, data={"pack": "type-recruit", **data})

    r = post(action="add", at="form_start", pos="below", event="apply_mobile", label="スマホで応募開始")
    assert r.status_code == 200 and r.json()["ok"]
    first = r.json()["id"]
    html = b.get("/live").text  # same property → same flow
    # the main path is unchanged — the branch sits under its step
    assert _labels(html) == ["サイトに来た", "サイトを開いた", "しっかり見た（10秒以上）", "求人を検索", "求人を見た", "応募を開始", "応募を送信"]
    assert _branches(html, "form_start", "below") == ["スマホで応募開始"]
    br = _soup(html).select_one("#flow .flow-branch")
    assert br.select_one(".flow-users strong").get_text() == "400"
    assert "「求人を見た」から" in br.get_text() and "8.0%" in br.get_text()  # 400 / 5,000 (view_item)
    assert "apply_mobile" in live.calls["flow"][-1]
    edit = _template(html, f"pop-flow-b{first}")
    assert "「応募を開始」の 66.7%" in edit.get_text()
    assert edit.select_one("input[name=action][value=update]") and edit.select_one("input[name=action][value=delete]")

    assert post(action="add", at="form_start", pos="above", event="page_view", label="PV").json()["ok"]
    assert post(action="add", at="view_item", pos="below", event="page_view").json()["ok"]
    html = a.get("/live").text
    assert _branches(html, "form_start", "above") == ["PV"]
    assert _branches(html, "view_item", "below") == ["page_view"]
    full = post(action="add", at="form_submit", pos="below", event="page_view")
    assert full.status_code == 400 and "3 つ" in full.json()["error"]
    assert not _soup(html).select("#flow .flow-add")

    assert post(action="update", id=first, event="apply_mobile", label="スマホ").json()["ok"]
    assert post(action="delete", id=first).json()["ok"]
    html = a.get("/live").text
    assert _branches(html, "form_start", "below") == [] and _branches(html, "form_start", "above") == ["PV"]
    assert post(action="update", id="nope", event="x").status_code == 404


def test_branches_are_validated(live):
    c = live()
    post = lambda **d: c.post("/flow/branch", headers=JSON, data={"pack": "type-recruit", **d})  # noqa: E731
    assert post(action="add", at="form_start", pos="below", event="bad name!").status_code == 400
    assert post(action="add", at="entry", pos="below", event="x").status_code == 400
    assert post(action="add", at="form_start", pos="left", event="x").status_code == 400
    assert _client().post("/flow/branch", headers=JSON, data={
        "pack": "hr", "action": "add", "at": "form_start", "pos": "below", "event": "x"}).status_code == 403
    assert post(action="add", at="form_start", pos="below", event="ok_event",
                label="  a   very long label that keeps going on  ").json()["ok"]
    assert "a very long label that k" in _branches(c.get("/live").text, "form_start", "below")


@pytest.mark.parametrize("cat", list(__import__("sitekpi.packs.behaviors", fromlist=["BEHAVIORS"]).BEHAVIORS))
def test_every_behaviour_has_a_sample_board_built_on_ga4_basics(cat):
    from sitekpi.packs.behaviors import BEHAVIORS

    for loc in ("ja", "en", "ko"):
        c = _client()
        c.post("/settings", data={"locale": loc})
        html = c.get(f"/type-{cat}").text
        nodes = _soup(html).select("#flow .flow-node")
        assert len(nodes) == 1 + len(BEHAVIORS[cat]["flow"])  # サイトに来た + the flow
        assert [n.select_one("code").get_text() for n in nodes[1:]] == BEHAVIORS[cat]["flow"]
        assert not any(n.select_one(".flow-missing") for n in nodes)  # the sample records every step


def test_blog_flow_takes_any_industry(live):
    c = live()
    c.post("/setup/flow", data={"behavior": "blog"})
    soup = _soup(c.get("/setup/industry").text)
    assert not soup.select(".choice-grid button") and soup.select_one("details.more-inds").has_attr("open")
    assert "業種を問いません" in soup.get_text()
    c.post("/setup/industry", data={"industry": "news"})
    html = c.get("/live").text
    assert "ブログ・記事を読んでもらう × ニュース・購読" in _soup(html).select_one("header.top .meta").get_text()
    assert _template(html, "pop-bench-engaged_rate")  # site-wide standards still apply


def test_industry_step_compares_the_site_with_each_industry(live, monkeypatch):
    import sitekpi.routes.setup as setup_routes

    monkeypatch.setattr(setup_routes, "fetch_site_basics", lambda session, period="28d": {"uu": 19000, "engaged_rate": 48.0, "sessions": 21000})
    setup_routes._BASICS_CACHE._data.clear()
    c = live()
    c.post("/setup/flow", data={"behavior": "recruit"})
    soup = _soup(c.get("/setup/industry").text)
    assert "48.0%" in soup.select_one(".setup-context .ctx-num").get_text()  # your number, once
    assert "人事・採用" in soup.select_one(".setup-context").get_text() or soup.select_one(".setup-context a[href='/setup/flow']")
    card = soup.select_one(".choice-grid button")
    assert "56.2%" in card.select_one(".choice-compare").get_text() and card.select_one(".ind-foot .choice-meta")
    assert "パック" not in card.get_text()
