"""Numbers first: start page → board in one step; the flow is guessed until the user fits it."""

from __future__ import annotations

import pytest
from bs4 import BeautifulSoup
from fastapi.testclient import TestClient

from main import app
from sitekpi.selection import guess_behavior


@pytest.fixture
def client():
    return TestClient(app, base_url="http://127.0.0.1:8766", follow_redirects=False)


@pytest.mark.parametrize("events,want", [
    ({"purchase": 3, "view_item": 9, "add_to_cart": 4}, ("commerce", "purchase")),
    ({"purchase": 1, "sign_up": 5, "login": 9}, ("commerce", "purchase")),  # a sale beats a sign-up
    ({"form_submit": 3, "form_start": 4, "view_item": 1, "view_search_results": 2}, ("recruit", "form_submit")),
    ({"form_submit": 3}, ("lead", "form_submit")),  # plain form → 問い合わせる
    ({"sign_up": 2, "login": 3}, ("free_trial", "sign_up")),
    ({"click": 4, "scroll": 3}, ("blog", "click")),
    ({"page_view": 10, "custom_thing": 2}, ("blog", "")),  # nothing to convert yet
])
def test_guess_behaviour_from_the_sites_events(events, want):
    assert guess_behavior(events) == want


def test_demo_guess_follows_the_demo_property():
    assert guess_behavior(None, "Demo Shop JP") == ("commerce", "demo")
    assert guess_behavior(None, "Demo Media") == ("content", "demo")


def test_landing_page_purpose_audience_features_how_and_seo(client):
    import json

    for lang in ("", "?lang=en", "?lang=ko"):
        s = BeautifulSoup(client.get("/" + lang).text, "html.parser")
        hrefs = [a["href"] for a in s.select(".lp-hero .lp-actions a")]
        assert hrefs == ["/connect", "/samples"]  # v5: no public demo — the sample boards instead
        for sec in ("problem", "features", "who", "samples", "how", "story", "faq"):
            assert s.select_one(f"section#{sec} h2"), (lang, sec)
        assert len(s.select(".lp-stat")) == 5 and len(s.select(".lp-feat")) == 4
        assert len(s.select("#who .lp-who img")) == 3 and len(s.select("#samples a.lp-sample")) == 6
        assert len(s.select("#how .lp-how > li")) == 4 and len(s.select("#faq details")) == 12
        assert "{" not in s.select_one("main").get_text()  # counts filled in
        for img in s.select("img.lp-shot"):
            assert client.get(img["src"].split("?")[0]).status_code == 200, img["src"]
        faq = next(json.loads(x.string) for x in s.select('script[type="application/ld+json"]')
                   if json.loads(x.string)["@type"] == "FAQPage")
        assert len(faq["mainEntity"]) == 12
        assert s.select_one('footer a[href^="https://script.google.com/macros/"]')  # お問い合わせ
    # the language picked on the landing page stays for the session (board after connecting too)
    assert client.get("/connect").text.count('lang="ko"') == 1
    client.get("/connect/demo?start=1")
    assert BeautifulSoup(client.get("/live").text, "html.parser").html["lang"] == "ko"
    client.cookies.clear()
    s = BeautifulSoup(client.get("/").text, "html.parser")
    assert s.select_one('a.lp-sample[href="/samples?b=commerce&i=ec"]')
    assert s.select_one('meta[name="description"]')["content"]
    assert s.select_one('link[rel="canonical"]')["href"].endswith("/")
    assert {a["hreflang"] for a in s.select('link[rel="alternate"]')} == {"ja", "en", "ko", "x-default"}
    kinds = {json.loads(x.string)["@type"] for x in s.select('script[type="application/ld+json"]')}
    assert kinds == {"SoftwareApplication", "FAQPage"}
    assert not s.select_one('meta[name="robots"]')  # public page is indexable
    assert s.select_one('footer a[href="/policy"]') and s.select_one('footer a[href="/terms"]')
    en = BeautifulSoup(client.get("/?lang=en").text, "html.parser")
    assert en.html["lang"].startswith("en") and "?lang=en" in en.select_one('link[rel="canonical"]')["href"]
    # connected: / goes to the board, the menu's 「SiteKPI について」 (/?home=1) shows the landing page
    client.cookies.clear()
    client.get("/connect/demo?start=1")
    assert client.get("/").headers["location"] == "/live"
    home = BeautifulSoup(client.get("/?home=1").text, "html.parser")
    assert home.select_one('.pub-top a.pub-login[href="/live"]') and home.select_one("#problem")
    board = BeautifulSoup(client.get("/live").text, "html.parser")
    assert board.select_one('.nav-bottom a[href="/help"]') and board.select_one('.nav-bottom a[href="/?home=1"]')
    # app pages stay out of search results
    assert BeautifulSoup(client.get("/glossary").text, "html.parser").select_one('meta[name="robots"]')


def test_demo_is_one_click_to_a_board_with_a_guess_notice(client):
    r = client.get("/connect/demo?start=1")
    assert r.headers["location"] == "/live"
    s = BeautifulSoup(client.get("/live").text, "html.parser")
    # v5: one small line at the top of the verdict card — both guesses, 直す · このままでよい
    note = s.select_one(".verdict .notice")
    assert [b.get_text() for b in note.select("b")] == ["買う", "EC・小売"] and "仮で決めた設定" in note.get_text()
    assert note.select_one("form[action='/setup/keep']") and note.select_one("[data-edit-open]")
    # 上のバー (text): 比べる業種 … 変える ▾ with 期間; 目安を調整 moved into the 業種 drawer
    assert s.select_one(".top-right [data-drawer-open='industry'].link-btn") and not s.select_one(".top-right .adjust-link")
    assert s.select_one("#drawer-industry .drawer-adjust [data-ind-adjust]") and s.select_one("template#pop-bench-all")
    assert s.select_one(".where-head .where-edit")  # 流れを直す as blue text in the card head
    # v5.1: 流れを直す · 業種を変える ▾ · 流入別に見る ▾ side by side
    tools = s.select_one(".where-head .where-tools")
    assert [x.get_text(" ", strip=True) for x in tools.select(".link-btn")] == ["✎ 流れを直す", "業種を変える ▾", "流入別に見る ▾"]
    assert tools.select_one(".where-ind[data-drawer-open='industry']")
    assert "デモ接続の見本" in str(s.select_one("template#pop-flow-help"))  # not 「GA4 を接続すると」
    assert client.get("/").headers["location"] == "/live"  # connected → straight to the board


def test_board_period_switch_and_edit_numbers_match_the_flow(client):
    import json

    client.get("/connect/demo?start=1")
    for period in ("28d", "7d"):
        s = BeautifulSoup(client.get(f"/live?period={period}").text, "html.parser")
        sel = s.select_one(".top-right form[data-period] select[name=period]")
        assert sel and not sel.has_attr("disabled")
        assert sel.select_one("option[selected]")["value"] == period
        assert s.select_one("[data-details]") is not None
        # 編集モード shows the same people as the flow it replaces (this period too)
        data = json.loads(s.select_one("#setup-data").get_text())
        nodes = s.select("#flow .flow-node")
        shown = [n.select_one(".flow-users strong").get_text() for n in nodes]
        assert f"{data['entry']:,}" == shown[0]
        for st, txt in zip(data["steps"], shown[1:]):
            assert f"{data['counts'][st['event']]:,}" == txt, (period, st)
    # the 段 drawer can save (the drawer covers the 編集中 bar)
    assert s.select_one("#drawer-step button[type=submit][form=edit-form]") and s.select_one("form#edit-form")


def test_help_page_and_connect_explain_the_unverified_app_screen(client, monkeypatch):
    for lang in ("ja", "en", "ko"):
        s = BeautifulSoup(client.get(f"/help?lang={lang}").text, "html.parser")
        for sec in ("start", "connect", "read", "words", "fix", "trouble", "contact"):
            assert s.select_one(f"section#{sec} h2"), (lang, sec)
        assert len(s.select("#words .hp-word")) == 8 and s.select_one("#contact a[href^='https://script.google.com/']")
        assert s.select_one('link[rel="canonical"]') and not s.select_one('meta[name="robots"]')
    client.cookies.clear()
    import sitekpi.routes.connect as connect
    monkeypatch.setattr(connect, "oauth_configured", lambda: True)
    s = BeautifulSoup(client.get("/connect").text, "html.parser")
    note = s.select_one(".cx-unverified")
    assert note and "続行" in note.get_text() and note.select_one('a[href="/help#connect"]')


def test_v5_samples_only_no_public_demo(client, monkeypatch):
    """v5: the demo connection is a dev / test mode; the public sees sample boards (例 everywhere)."""
    from fastapi.testclient import TestClient

    c = TestClient(client.app, follow_redirects=False)
    monkeypatch.delenv("DEMO_CONNECT")
    r = c.get("/connect/demo?start=1")
    assert r.status_code == 302 and r.headers["location"] == "/samples"
    monkeypatch.setenv("DEMO_CONNECT", "1")
    # sample board: 例の数字 by the title, the yellow banner, 例 in the menu
    s = BeautifulSoup(client.get("/ec").text, "html.parser")
    assert s.select_one(".top .ex-tag").get_text() == "例の数字"
    banner = s.select_one(".ex-banner")
    assert "数字はすべて例" in banner.get_text() and banner.select_one('a[href="/connect"]') and banner.select_one('a[href="/samples"]')
    assert s.select_one(".rail a.nav-sample.is-on .nav-ex")
    # 比べる業種 on a sample opens another sample (GET) — nothing is saved
    form = s.select_one("#drawer-industry form#ind-form")
    assert form["method"] == "get" and form["action"] == "/samples/open"
    r = c.get("/samples/open?industry=hr")
    assert r.status_code == 303 and r.headers["location"] == "/hr"
    assert c.get("/samples/open?industry=nope").headers["location"] == "/samples"
    # the samples list says the same
    lst = BeautifulSoup(client.get("/samples").text, "html.parser")
    assert "すべて例" in lst.select_one(".ex-banner").get_text()
    # every 「デモで試す」 became 「見本ボードを見る」
    for path in ("/", "/connect", "/help"):
        html = client.get(path).text
        assert "/connect/demo" not in html.replace('/connect/demo"', "") or path == "/connect", path
        assert "デモで試す" not in html, path


def test_v5_memo_panel_on_board_glossary_samples_builder(client):
    for path in ("/ec", "/glossary", "/samples", "/builder"):
        s = BeautifulSoup(client.get(path).text, "html.parser")
        memo = s.select_one(".shell.has-memo aside.memo[data-memo]")
        assert memo and memo.select_one("textarea[data-memo-text][maxlength='500']"), path
        assert "返信はしません" in memo.get_text() and memo.select_one("[data-mood=up]"), path
    for path in ("/settings", "/help"):
        assert not BeautifulSoup(client.get(path).text, "html.parser").select_one("aside.memo"), path
    r = client.post("/feedback", json={"comment": "「あと」がわからない", "screen": "samples", "section": "どこで離れているか", "path": "/ec"})
    assert r.status_code == 200 and r.json()["ok"]


def test_v51_layout_rules():
    """FAQ cards share one height; the board grows to 1360px and stays centered; the sideways flow's
    min-width never applies to the stacked layout; 編集中 outlines the card."""
    from pathlib import Path

    css = Path(__file__).resolve().parents[1] / "static" / "css"
    lp = (css / "landing.css").read_text()
    assert "min-height: 3.2em" in lp.split(".lp-faq summary {", 1)[1].split("}", 1)[0]
    board = (css / "board.css").read_text()
    assert "@container flow (min-width: 521px)" in board and "@media (min-width: 901px)" not in board
    assert ".content { padding: 16px 32px 56px; gap: 20px; max-width: 1360px; margin: 0 auto;" in board
    assert ".content > section.card.where.is-editing { outline: 2px solid var(--accent);" in board
