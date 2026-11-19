"""v7.3 page-level numbers: ② 入口ページ別 · ④ どのページで？ · 詳しい数字 › ページ別."""

import pytest
from bs4 import BeautifulSoup
from fastapi.testclient import TestClient

from main import app
from sitekpi.board.story_pages import path_key, sample_pages, strip_site_tail


def _soup(lang):
    c = TestClient(app, headers={"Accept-Language": lang})
    r = c.get("/ec")
    assert r.status_code == 200
    return BeautifulSoup(r.text, "html.parser")


def test_paths_and_titles_are_tidied():
    assert path_key("https://x.com/a/b/?q=1") == "/a/b" == path_key("/a/b/") == path_key("/a/b#top")
    assert path_key("") == "/" == path_key("/")
    t = strip_site_tail({"/": "Home | Shop", "/a": "Coat - Shop", "/b": "Sale ｜ Shop", "/c": "A - B | Shop"})
    assert t == {"/": "Home", "/a": "Coat", "/b": "Sale", "/c": "A - B"}
    assert strip_site_tail({"/": "Home | Shop", "/a": "About"}) == {"/": "Home | Shop", "/a": "About"}  # one title is no pattern


def test_sample_pages_add_up_to_the_flow():
    totals = {"view_item": 30000, "add_to_cart": 10000, "purchase": 1500}
    pg = sample_pages("ec", 68000, totals, list(totals))
    assert pg["entry"][0]["title"]["ja"] == "トップ" and pg["views"][0]["views"] > pg["views"][-1]["views"]
    for ev, n in totals.items():
        assert abs(sum(e["ev"][ev] for e in pg["entry"]) - n) <= n * 0.02
    for e in pg["entry"]:  # each page's numbers go down the flow
        assert e["users"] >= e["ev"]["view_item"] >= e["ev"]["add_to_cart"] >= e["ev"]["purchase"]
    assert sample_pages("saas", 1000, {"signup": 50}, ["signup"])["entry"][0]["path"] == "/"
    assert sample_pages("ec", 0, totals, list(totals)) is None


@pytest.mark.parametrize("lang,worst", [("ja", "冬のコート特集"), ("en", "Winter coat feature"), ("ko", "겨울 코트 특집")])
def test_story_shows_pages_in_three_places(lang, worst):
    s = _soup(lang)
    # ② 入口ページ別: same split as the map, the ad landing page is the one to fix
    pg = s.select_one("#qb .x-pg")
    rows = pg.select(".x-pg-row:not(.is-head)")
    assert 2 <= len(rows) <= 6 and worst in pg.select_one(".x-sub-lead").get_text()
    fix = [r for r in rows if r.select_one(".q-fix")]
    assert fix and worst in fix[0].select_one(".x-pg-name").get_text()
    assert pg.select_one(".x-map-notes").find_parent("details")  # the explanation folds (v7.2b)
    # ④ どのページで？: same ruler as devices / traffic, the worst page outlined, the rest as 「その他」
    pw = s.select_one("#q3 .x-pgw")
    assert worst in pw.select_one(".x-sub-lead").get_text()
    assert worst in pw.select_one(".is-worst .x-bar-name").get_text()
    assert pw.select(".x-bar-band") and pw.select(".x-bar-row")[-1].select_one(".x-bar-name").get_text().strip()
    assert worst in s.select_one("#q3 .q-next").get_text()  # ⑤ starts where those people come in
    # 詳しい数字 › ページ別: closed, sortable, 10 rows then 「もっと見る」
    g = s.select_one("#s-l2 #g-pages")
    assert g.select_one("[data-dgroup-toggle]")["aria-expanded"] == "false" and g.select_one("#dt-pages").has_attr("hidden")
    t = g.select_one("[data-pt-table]")
    assert len(t.select("thead [data-pt-sort]")) == 6 and t.select_one('[data-pt-sort="views"]')["aria-sort"] == "descending"
    shown = [r for r in t.select("tbody tr") if not r.has_attr("hidden")]
    views = [int(r["data-views"]) for r in shown]
    assert len(shown) == 10 and views == sorted(views, reverse=True) and g.select_one("[data-pt-more]")
    assert all(td.get("data-k") for td in t.select("tbody td"))  # phones read each number by its label


def test_no_pages_no_blocks():
    from sitekpi.views.story_pages import entry_pages, table

    flow = {"stages": [{"label": "来た", "users": 100, "event": ""}, {"label": "買った", "users": 40, "event": "purchase"}]}
    assert entry_pages(flow, {"pages": None}, "ja") is None and table(flow, {}, "ja") is None
    one = {"pages": {"entry": [{"path": "/", "title": "Home", "users": 100, "eng": 50.0, "ev": {"purchase": 40}}],
                     "views": [{"path": "/", "title": "Home", "views": 300}], "n_pages": 1}}
    assert entry_pages(flow, one, "ja") is None  # one page says nothing about pages
    assert table(flow, one, "ja")["rows"][0]["rate"] == "40.0%"
