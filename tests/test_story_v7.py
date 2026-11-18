"""Story v7 chapters: なぜ変わった？ · 誰が成果を出している？ · どこで起きている？ · いつから？ · 直したら効いた？"""

from __future__ import annotations

from datetime import date, timedelta
from types import SimpleNamespace

import pytest
from bs4 import BeautifulSoup
from fastapi.testclient import TestClient

from main import app
from sitekpi.board.story_x import today_jst


def _soup(c: TestClient, url: str) -> BeautifulSoup:
    r = c.get(url)
    assert r.status_code == 200, url
    return BeautifulSoup(r.text, "html.parser")


def test_ec_sample_tells_all_seven_chapters():
    s = _soup(TestClient(app), "/ec")
    assert [a.select_one(".qn").get_text() for a in s.select(".story-toc a")] == list("0123456")
    # 0: うまくいっていること — only metrics that got better
    goods = s.select(".goods li")
    assert 1 <= len(goods) <= 3 and all("+" in g.select_one(".tone-up").get_text() for g in goods)
    # 1: the outcome split into visitors × rate (× revenue per conversion) — the terms multiply back
    ch = s.select_one("#qch")
    assert ch.select_one("h2").get_text().strip() and len(ch.select(".x-term")) in (3, 4)
    assert ch.select_one(".x-take")
    # 2: traffic map (PC svg + phone list carry the same channels) and new vs returning
    who = s.select_one("#qb")
    names_svg = [t.get_text().rsplit(" ", 1)[0] for t in who.select(".x-map-svg .x-dot-k")]
    names_list = [b.get_text() for b in who.select(".x-map-list .x-ml-row:not(.is-head) b[role=rowheader]")]
    assert names_svg == names_list and "その他" not in " ".join(names_list)
    assert who.select(".x-stack") and len(who.select(".x-card")) == 3
    # 4: where (devices + traffic on one ruler) and since when (8 weeks)
    why = s.select_one("#q3")
    assert len(why.select(".x-bars-col")) == 2 and why.select(".x-bar-row")
    assert len(why.select(".x-when-svg.pc-only circle")) == 8
    # 5: the sample shows fix ① done 14+ days ago with its before / after, and saves nothing
    do = s.select_one("#q4")
    eff = do.select_one("#q5")
    assert eff.select_one("form[data-sample] button[disabled]") and eff.select(".x-eff-row:not(.is-head)")
    assert eff.select_one(".x-rels li") and not eff.select(".x-rel-del")
    assert do.select_one(".act .act-rec.is-done") and do.select(".act [data-rec-pick]")
    assert why.select(".x-when-svg.pc-only .x-mark")  # the fix is marked on いつから？
    assert do.select_one(".ai-card [data-ai-copy]")  # the AI question is one click, not hidden
    # 6: まとめ before 詳しい数字, four lines, copyable
    sm = s.select_one("#qsum")
    assert len(sm.select(".sum-rows div")) == 4 and sm.find_next_sibling("section")["id"] == "s-l2"
    assert "まとめ" in s.select(".story-toc a")[-1].get_text()


@pytest.mark.parametrize("lang", ["en", "ko"])
def test_v7_chapters_are_localized(lang):
    c = TestClient(app)
    c.post("/settings", data={"locale": lang})
    s = _soup(c, "/ec")
    html = str(s.select_one(".content"))
    for ja in ("なぜ変わった", "誰が成果", "どこで起きている", "いつから", "やった日を記録", "うまくいっていること", "まとめ",
               "質問文をコピー"):
        assert ja not in html, (lang, ja)


def test_numbers_in_chapter_one_multiply_back():
    from sitekpi.views.story_more import changed

    board = {"summary": [{"id": "primary", "label": "購入", "value_num": 1580, "prev_num": 1516},
                         {"id": "signup_cvr", "label": "購入CVR"}]}
    sx = {"money": {"cur": {"revenue": 8_412_000}, "prev": {"revenue": 7_928_000}}}
    nums = {"where": "③", "span": "③〜⑤", "do": "⑤"}
    c = changed(board, {"uu": 68500}, {"uu": 65680}, sx, "ja", nums)
    assert c["result"]["value"] == "¥8,412,000" and c["result"]["delta"] == "+6.1%"
    assert "来た人が増えたから" in c["head"] and "購入CVRは前期とほぼ同じ" in c["head"]
    total = sum(float(g["amount"].replace("¥", "").replace(",", "").replace("−", "-")) for g in c["segs"])
    assert abs(total - (8_412_000 - 7_928_000)) < 5_000  # 購入CVR is flat → left out of the bar
    assert "購入CVR" in c["flat"]


def test_release_is_saved_per_property_and_compared(monkeypatch):
    from sitekpi.routes import flow as rf

    c = TestClient(app)
    c.get("/connect/demo?start=1")
    # demo connection: no property scope → nothing saved
    r = c.post("/story/release", data={"act": "1", "date": "2026-01-01"}, follow_redirects=False)
    assert r.status_code == 303
    monkeypatch.setattr(rf, "property_scope", lambda s: "prop:1")
    day = (today_jst() - timedelta(days=20)).isoformat()
    c.post("/story/release", data={"act": "own", "title": "送料を商品ページに表示", "date": day})
    c.post("/story/release", data={"act": "2", "act_title_2": "決済の入力を減らす", "date": day})
    future = (today_jst() + timedelta(days=2)).isoformat()
    c.post("/story/release", data={"act": "1", "date": future})  # future dates are ignored
    s = _soup(c, "/live")  # the demo board shows the sample fix, never a form that saves
    assert s.select_one("#q4 #q5 form[data-sample]")
    assert rf.load_releases({"story_releases": {"prop:1": [{"date": day, "title": "x"}, {"title": "no date"}]}}) == [
        {"date": day, "title": "x"}]


def test_release_window_waits_for_fourteen_days():
    from sitekpi.ga4.story import release_ranges

    today = date(2026, 11, 18)
    assert release_ranges(date(2026, 11, 10), today) is None
    before, after = release_ranges(date(2026, 11, 3), today)
    assert before == ("2026-10-20", "2026-11-02") and after == ("2026-11-03", "2026-11-16")


class _FakeClient:
    """Answers each report by its dimensions (device / week / new-vs-returning / two date ranges)."""

    def __init__(self, credentials=None):
        pass

    @staticmethod
    def _row(dims, vals):
        return SimpleNamespace(dimension_values=[SimpleNamespace(value=d) for d in dims],
                               metric_values=[SimpleNamespace(value=str(v)) for v in vals])

    def batch_run_reports(self, req):
        out = []
        for q in req.requests:
            dims = [d.name for d in q.dimensions]
            n_ranges = len(q.date_ranges)
            rows = []
            if dims == ["deviceCategory"]:
                rows = [self._row([d], [n]) for d, n in (("mobile", 600), ("desktop", 350), ("tablet", 50))]
            elif dims == ["deviceCategory", "eventName"]:
                rows = [self._row([d, e], [n]) for d, k in (("mobile", 0.5), ("desktop", 1.0)) for e, n in
                        (("view_item", 300 * k), ("add_to_cart", 90 * k), ("purchase", 20 * k))]
            elif dims == ["nthWeek"]:
                rows = [self._row([f"000{i}"], [250]) for i in range(8)]
            elif dims == ["nthWeek", "eventName"]:
                rows = [self._row([f"000{i}", e], [n]) for i in range(8) for e, n in
                        (("view_item", 140), ("add_to_cart", 40 - i), ("purchase", 9))]
            elif dims == ["newVsReturning"] and n_ranges == 1:
                rows = [self._row(["new"], [700]), self._row(["returning"], [300])]
            elif n_ranges == 2 and not dims:
                rows = [self._row(["r0"], [500]), self._row(["r1"], [520])]
            elif n_ranges == 2:
                rows = [self._row([e, r], [n]) for e, r, n in (("add_to_cart", "r0", 100), ("add_to_cart", "r1", 120),
                                                               ("purchase", "r0", 20), ("purchase", "r1", 21))]
            elif not dims:
                rows = [self._row([], [1000, 500000])]
            out.append(SimpleNamespace(rows=rows))
        return SimpleNamespace(reports=out)


def test_fetch_story_x_reads_ga4(monkeypatch):
    from sitekpi.ga4 import data as g
    from sitekpi.ga4.story import fetch_story_x

    monkeypatch.setattr(g, "connection_info", lambda s: {"property_id": "1", "property_name": "P"})
    monkeypatch.setattr(g, "HAS_DATA", True)
    monkeypatch.setattr(g, "HAS_GOOGLE_AUTH", True)
    monkeypatch.setattr(g, "creds_from_session", lambda s: object())
    monkeypatch.setattr(g, "BetaAnalyticsDataClient", _FakeClient)
    rel = {"date": (today_jst() - timedelta(days=30)).isoformat()}
    sx, err = fetch_story_x({}, period="28d", events=["view_item", "add_to_cart", "purchase"], last="purchase",
                            release=rel)
    assert err is None
    assert sx["devices"]["mobile"]["entry"] == 600 and sx["devices"]["desktop"]["ev"]["purchase"] == 20
    assert sx["weeks"]["entry"] == [250] * 8 and sx["weeks"]["ev"]["add_to_cart"][7] == 33
    assert sx["money"]["cur"]["revenue"] == 500000
    assert sx["nvr"]["new"]["users"] == 700
    assert sx["release"]["before"]["entry"] == 500 and sx["release"]["after"]["ev"]["add_to_cart"] == 120


def test_chapter_two_uses_a_step_enough_people_reached_and_labels_do_not_overlap():
    """A site with 10 conversions (the field report): rates come from a step with ≥ 30 people,
    tiny channels are left out by name, and no two names sit on top of each other."""
    from sitekpi.views.story_more import buyers

    ch = [("ch_direct", "Direct", 6370), ("ch_org", "Organic Search", 640), ("ch_ref", "Referral", 400),
          ("ch_social", "Organic Social", 80), ("ch_ai", "AI Assistant", 25)]
    entry = sum(n for _, _, n in ch)
    stages = [
        {"label": "サイトに来た", "users": entry, "event": ""},
        {"label": "しっかり見た", "users": 2100, "event": "user_engagement",
         "ch_users": {"ch_direct": 1500, "ch_org": 420, "ch_ref": 70, "ch_social": 30, "ch_ai": 20}},
        {"label": "外部リンクをクリック", "users": 10, "event": "click",
         "ch_users": {"ch_direct": 2, "ch_org": 8, "ch_ref": 0, "ch_social": 0, "ch_ai": 0}},
    ]
    flow = {"stages": stages, "last_label": "外部リンクをクリック",
            "channels": [{"id": i, "name": n, "entry": e} for i, n, e in ch]}
    sx = {"nvr": {"new": {"users": 7100, "ev": {"user_engagement": 1900, "click": 8}},
                  "returning": {"users": 135, "ev": {"user_engagement": 200, "click": 2}}, "prev_returning": 140}}
    w = buyers(flow, sx, "ja")
    assert "しっかり見た" in w["head"] and "外部リンク" not in w["head"]
    m = w["map"]
    names = [p["name"] for p in m["pts"]]
    assert names == ["Direct", "Organic Search", "Referral"] and "AI Assistant" in m["small"]
    assert all(p["r"] <= 18 for p in m["pts"])
    boxes = []
    for p in m["pts"]:
        w_ = 7.5 * len(p["label"]) + 4
        x0 = p["tx"] - w_ if p["anchor"] == "end" else p["tx"]
        boxes.append((x0, p["ty"] - 16, x0 + w_, p["ty"] - 2))
        assert x0 >= 0 and x0 + w_ <= m["r"] + 1, p
    for i, a in enumerate(boxes):
        for b in boxes[i + 1:]:
            assert a[2] < b[0] or b[2] < a[0] or a[3] < b[1] or b[3] < a[1], (a, b)
    # the new / returning bar never squeezes text into a 2% slice
    assert w["nvr"]["users"]["narrow_ret"] and not w["nvr"]["users"]["narrow_new"]
