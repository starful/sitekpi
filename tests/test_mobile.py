"""Phone layout (canvas Sp*) and first-visit language from the browser (Accept-Language, never IP)."""

from __future__ import annotations

import pytest
from bs4 import BeautifulSoup
from fastapi.testclient import TestClient

from main import app
from sitekpi.i18n import browser_locale


@pytest.fixture
def client():
    return TestClient(app, base_url="http://127.0.0.1:8766", follow_redirects=False)


def _soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


@pytest.mark.parametrize(
    "header, want",
    [("en-US,en;q=0.9,ja;q=0.8", "en"), ("ko-KR,ko;q=0.9", "ko"), ("ja,en;q=0.5", "ja"),
     ("zh-TW,ko;q=0.7,en;q=0.6", "ko"), ("fr-FR", None), ("", None), ("en;q=0", None)],
)
def test_browser_locale(header, want):
    assert browser_locale(header) == want


def test_first_visit_follows_browser_language(client):
    r = client.get("/", headers={"Accept-Language": "en-US,en;q=0.9"})
    assert _soup(r.text).html["lang"] == "en"
    # remembered for the next page of the same visit
    assert _soup(client.get("/help").text).html["lang"] == "en"


def test_lang_query_and_bots_win_over_browser_language(client):
    r = client.get("/?lang=ja", headers={"Accept-Language": "ko"})
    assert _soup(r.text).html["lang"] == "ja"
    bot = TestClient(app, base_url="http://127.0.0.1:8766")
    r = bot.get("/", headers={"Accept-Language": "en", "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1)"})
    assert _soup(r.text).html["lang"] == "ja"


def test_landing_phone_parts(client):
    soup = _soup(client.get("/").text)
    assert soup.select_one(".lp-feat.is-open .lp-acc-btn")["aria-expanded"] == "true"
    assert soup.select_one("[data-lp-rail]")["data-hint"]
    assert soup.select_one("[data-lp-sp-cta] a.lp-cta")["href"] == "/connect"
    more = soup.select(".lp-faq details.lp-faq-more")
    if more:
        assert str(len(more)) in soup.select_one("[data-lp-faq-all]").get_text()


def test_memo_button_in_top_bar_on_sample_board(client):
    soup = _soup(client.get("/apparel").text)
    assert soup.select_one(".mobile-bar [data-memo-open]")


def test_connect_sample_has_no_affiliate_numbers(client):
    text = _soup(client.get("/connect").text).select_one(".cx-sample").get_text()
    for word in ("報酬", "クリック", "commission"):
        assert word not in text
    assert "1,580" in text


def test_help_has_no_path_label_and_has_jump(client):
    soup = _soup(client.get("/help").text)
    assert "/help" not in soup.select_one(".hp-main").get_text()
    assert len(soup.select("[data-hp-jump] option")) == 7


def test_glossary_groups_fold_after_four(client):
    soup = _soup(client.get("/glossary").text)
    for sec in soup.select(".gl-group"):
        cards = sec.select(".gl-card")
        btn = sec.select_one("[data-gl-more]")
        assert bool(btn) == (len(cards) > 4)
        assert len(sec.select(".gl-card.gl-extra")) == max(0, len(cards) - 4)


def test_samples_phone_lead_and_open_bar(client):
    soup = _soup(client.get("/samples?b=commerce&i=apparel").text)
    assert soup.select_one(".sp-only") and soup.select_one("[data-goal-pick]")
    assert soup.select_one(".sp-open-bar a")["href"] == "/apparel"
