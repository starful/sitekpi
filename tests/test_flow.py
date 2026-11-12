"""行動フロー: sample flow, live flow with per-property event mapping."""

from __future__ import annotations

import json
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
    assert flow and _soup(html).select_one(".ex-banner")  # v5: the 例 banner says it is a sample
    stages = flow.select(".flow-stage")
    assert [s.select_one(".flow-label").get_text() for s in stages] == ["サイトに来た", "サイトを開いた", "しっかり見た（10秒以上）", "商品を見た", "カートに追加", "購入手続きへ", "購入"]
    assert stages[0].select_one(".flow-users strong").get_text() == "68,500"
    # v6 story: the one issue (カート → 購入, furthest from its 業界目安) is the orange stretch of the flow
    assert len(flow.select(".flow-link.is-worst")) == 2
    assert [st.select_one(".flow-label").get_text() for st in flow.select(".flow-stage.is-issue")] == ["カートに追加", "購入手続きへ", "購入"]
    assert flow.select_one("h2.where-answer").get_text().startswith("「カートに追加 → 購入」で止まっています。カートに追加 10,800 人のうち")
    # the biggest drop in people is named too, so the two never contradict each other
    assert "人数がいちばん減るのは「商品を見た → カートに追加」（−23,104 人）" in flow.select_one(".q-note").get_text()
    lost = flow.select_one(".flow-lost.is-worst b")
    assert lost and lost.get_text() == "−7,180" and lost.has_attr("data-v-all")
    # every step keeps the same rows: the first one reserves the 「離れた」 line, the channel bar sits under the count
    assert stages[0].select_one(".flow-lost.is-blank")
    node = stages[2].select_one(".flow-node")
    kids = [c["class"][0] for c in node.find_all(recursive=False) if c.name]
    assert kids.index("flow-mix") < kids.index("flow-lost")
    pop = _template(html, "pop-flow-help").get_text()
    assert "流入元" in pop and "view_item → add_to_cart" in pop
    # channel switch carries every channel's numbers
    chs = [b["data-flow-ch"] for b in flow.select("[data-flow-ch]")]
    assert chs[0] == "all" and len(chs) == 6
    strong = stages[1].select_one(".flow-users strong")
    assert all(strong.has_attr(f"data-v-{c}") for c in chs)
    assert not flow.select("[data-pop-open^='flow-add']")
    # v5: 流れを直す can be tried on a sample — the form never posts and 保存 is off
    bar = _soup(html).select_one("[data-edit-bar]")
    assert bar.select_one("form#edit-form[data-try-only] .edit-save[disabled]") and "保存はされません" in bar.get_text()
    # Top → bottom: 0 総評 → 1 どこで離れている？ → 2 どこがおかしい？ → 3 どうする？ → 詳しい数字
    assert html.index('class="verdict card"') < html.index('id="flow"') < html.index('id="q3"') < html.index('id="q4"') < html.index('class="detail card"')


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
    import sitekpi.routes.setup as setup_routes
    monkeypatch.setattr(
        setup_routes, "fetch_site_basics",
        lambda session, period="28d": {"uu": 9000, "engaged_rate": 58.0, "sessions": 12000},
    )
    monkeypatch.setattr(
        setup_routes, "site_event_counts",
        lambda request: dict(SITE_COUNTS),
    )
    pages._LIVE_PACK_CACHE._data.clear()
    flow_routes._FLOW_CACHE._data.clear()
    flow_routes._EVENTS_CACHE._data.clear()
    setup_routes._BASICS_CACHE._data.clear()
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
    # 編集モード offers the site's own events for every step
    data = json.loads(_soup(html).select_one("#setup-data").get_text())
    assert "submit_application" in [e["name"] for e in data["events"]]
    # 記録なし → a hint and 「この段を直す」, which opens that very step in 編集モード
    miss = _stage(html, "応募を送信")
    assert "イベント名が違うかも" in miss.select_one(".flow-nudge").get_text()
    key = miss.select_one("[data-edit-step]")["data-edit-step"]
    assert key in [s["key"] for s in data["steps"]]

    r = a.post("/flow/mapping", headers=JSON, data={"pack": "type-recruit", "step": "form_submit", "event": "submit_application"})
    assert r.status_code == 200 and r.json() == {"ok": True, "step": "form_submit", "event": "submit_application"}

    html = b.get("/live").text  # same property, another browser
    st = _stage(html, "応募を送信")
    assert "is-missing" not in st["class"]
    assert st.select_one(".flow-users strong").get_text() == "200"
    assert live.calls["flow"][-1] == ["session_start", "user_engagement", "view_search_results", "view_item", "form_start", "submit_application"]
    assert "submit_application" in live.calls["overlay"][-1]
    # イベント (詳しい数字): the flow's event stands in for the site's event (no duplicate row)
    details = b.get("/live/details").text
    events = details.split('id="g-events"', 1)[1].split('id="g-biz"', 1)[0]
    assert "← submit_application" in events or "submit_application" in events
    assert events.count('<code class="row-name">submit_application</code>') == 0
    # 主転換 (応募完了 = form_submit) now counts the site's event
    assert "260" in _soup(html).select_one(".verdict").get_text()

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


def test_board_first_with_a_guessed_flow_then_setup(live):
    """Numbers first: picking a property opens the board at once. The flow is guessed from
    the site's events and labelled as a guess until the user fits it or keeps it."""
    c = live()
    c.post("/connect/property/change")
    r = c.post("/connect/property", data={"property_id": "4242"})
    assert r.headers["location"] == "/live"
    assert c.get("/first").headers["location"] == "/live"  # the old 「はじめての5分」 URL
    html = c.get("/live").text
    soup = _soup(html)
    notice = soup.select_one(".notice")
    # the site sends submit_application, not a GA4 conversion event → reading flow, said so
    assert notice and "ブログ・記事を読んでもらう" in notice.get_text() and "転換イベントが見つからない" in notice.get_text()
    assert soup.select_one(".verdict .stat") and soup.select_one("#flow .flow-stage")
    # サイトの設定 opens on the board's own flow (the guess), with the site's numbers
    assert c.get("/setup").headers["location"] == "/live?edit=1"
    soup = _soup(c.get("/live?edit=1").text)
    assert soup.select_one("[data-edit-bar] [data-template] option[selected]")["value"] == "blog"
    assert soup.select_one(".notice [data-edit-open]")  # 「サイトに合わせる」 opens 編集モード in place
    r = c.post("/setup/keep")
    assert r.status_code == 303 and r.headers["location"] == "/live"
    assert not _soup(c.get("/live").text).select_one(".notice")


def test_setup_is_the_boards_edit_mode(live):
    c = live()
    c.post("/connect/property/change")
    c.post("/connect/property", data={"property_id": "4242"})
    # the old pages open the board in 編集モード / with the 業種 drawer
    assert c.get("/setup").headers["location"] == "/live?edit=1"
    assert c.get("/setup/industry").headers["location"] == "/live?industry=1"
    assert c.get("/setup/flow").headers["location"] == "/live?edit=1"
    soup = _soup(c.get("/live?edit=1").text)
    data = json.loads(soup.select_one("#setup-data").get_text())
    board = json.loads(soup.select_one("#board-data").get_text())
    assert board["auto_open"] == "edit"
    # every behaviour is a ひな形, grouped; the site's own events (most first) to pick from
    assert len(soup.select("[data-edit-bar] [data-template] option")) == 18 and soup.select("[data-template] optgroup")
    assert set(data["templates"]) >= {"recruit", "blog", "commerce"}
    assert data["counts"]["submit_application"] == 260
    assert soup.select_one("form[action='/setup'] [data-behavior]")
    assert soup.select_one("#drawer-step[data-drawer] [data-events]")
    assert soup.select_one(".top-right [data-drawer-open=industry]") and soup.select_one("#drawer-industry form[action='/setup/industry']")
    # choosing a ひな形 only: its standard flow, industry follows the behaviour
    r = c.post("/setup", data={"behavior": "recruit"})
    assert r.status_code == 303 and r.headers["location"] == "/live"
    assert _labels(c.get("/live").text) == [
        "サイトに来た", "サイトを開いた", "しっかり見た（10秒以上）", "求人を検索", "求人を見た", "応募を開始", "応募を送信"]
    data = json.loads(_soup(c.get("/live").text).select_one("#setup-data").get_text())
    assert [s["label"] for s in data["steps"]] == [
        "サイトを開いた", "しっかり見た（10秒以上）", "求人を検索", "求人を見た", "応募を開始", "応募を送信"]


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
    data = [("behavior", "recruit")] + data
    r = c.post("/setup", data=_form_lists(data))
    assert r.status_code == 303 and r.headers["location"] == "/live"
    html = c.get("/live").text
    labels = [n.get_text() for n in _soup(html).select("#flow .flow-node .flow-label")]
    assert labels == ["サイトに来た", "サイトを開いた", "スマホ応募", "応募を送信"]
    assert live.calls["flow"][-1] == ["session_start", "apply_mobile", "submit_application"]
    assert "260" in _soup(html).select_one(".verdict").get_text()  # last step = 主転換
    data = json.loads(_soup(c.get("/live").text).select_one("#setup-data").get_text())
    assert [s["label"] for s in data["steps"]] == ["サイトを開いた", "スマホ応募", "応募を送信"]
    # errors come back on the board, 編集モード open, with what was posted
    bad = [("behavior", "recruit"), ("key", ""), ("event", "bad name"), ("label", "")]
    r = c.post("/setup", data=_form_lists(bad))
    assert r.headers["location"] == "/live?edit=1"
    soup = _soup(c.get("/live?edit=1").text)
    assert "イベント名" in soup.select_one("[data-edit-error]").get_text()
    assert json.loads(soup.select_one("#setup-data").get_text())["steps"][0]["event"] == "bad name"
    many = [("behavior", "recruit")] + [x for n in range(9) for x in (("key", ""), ("event", f"e{n}"), ("label", ""))]
    c.post("/setup", data=_form_lists(many))
    assert "8 つまで" in c.get("/live?edit=1").text
    std = [("behavior", "recruit")] + [
        x for k in ("session_start", "user_engagement", "view_search_results", "view_item", "form_start", "form_submit")
        for x in (("key", k), ("event", k), ("label", ""))]
    c.post("/setup", data=_form_lists(std))
    labels = [n.get_text() for n in _soup(c.get("/live").text).select("#flow .flow-node .flow-label")]
    assert labels == ["サイトに来た", "サイトを開いた", "しっかり見た（10秒以上）", "求人を検索", "求人を見た", "応募を開始", "応募を送信"]


def test_industry_of_another_kind_uses_site_wide_standards_only(live):
    c = live()
    c.post("/setup", data={"behavior": "commerce"})
    c.post("/setup/industry", data={"industry": "legal"})
    html = c.get("/live").text
    soup = _soup(html)
    assert "買う" in soup.select_one(".rail .nav-site-sub").get_text()
    assert "士業・法律事務所" in soup.select_one("header.top .top-item b").get_text()
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
    node = soup.select_one(f"#flow .flow-node[data-step='{step}']")
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
        assert [n["data-step"] for n in nodes[1:]] == BEHAVIORS[cat]["flow"]
        assert not any(n.select_one(".flow-missing") for n in nodes)  # the sample records every step


def test_blog_flow_takes_any_industry(live):
    c = live()
    c.post("/setup", data={"behavior": "blog"})
    soup = _soup(c.get("/live?industry=1").text)
    drawer = soup.select_one("#drawer-industry")
    assert not drawer.select(".ind-card") and drawer.select_one("details.sx-more").has_attr("open")
    assert "業種を問いません" in drawer.get_text()
    c.post("/setup/industry", data={"industry": "news"})
    html = c.get("/live").text
    assert "ブログ・記事を読んでもらう" in _soup(html).select_one(".rail .nav-site-sub").get_text()
    assert "ニュース・購読" in _soup(html).select_one("header.top .top-item b").get_text()
    assert _template(html, "pop-bench-engaged_rate")  # site-wide standards still apply


def test_industry_step_compares_the_site_with_each_industry(live, monkeypatch):
    import sitekpi.routes.setup as setup_routes

    monkeypatch.setattr(setup_routes, "fetch_site_basics", lambda session, period="28d": {"uu": 19000, "engaged_rate": 48.0, "sessions": 21000})
    setup_routes._BASICS_CACHE._data.clear()
    c = live()
    c.post("/setup", data={"behavior": "recruit"})
    soup = _soup(c.get("/live?industry=1").text).select_one("#drawer-industry")
    cards = soup.select(".ind-card")
    assert cards and cards[0].select_one("input[data-ind]") and "パック" not in cards[0].get_text()
    # the preview puts the site's own number next to the chosen industry's 目安
    rows = soup.select("[data-ind-rows] .sx-ind-row")
    assert any("あなた 48.0%" in r.get_text() for r in rows)
    data = json.loads(soup.select_one("#ind-data").get_text())
    assert len(data["previews"]) > 20 and all(isinstance(v, list) for v in data["previews"].values())
