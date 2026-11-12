"""v6 story: 0 総評 → 1 どこで？ → 2 どこがおかしい？ → 3 どうする？ (views/story.py, i18n/story_l10n.py)."""

from __future__ import annotations

import json

import pytest
from bs4 import BeautifulSoup
from fastapi.testclient import TestClient

from main import app
from sitekpi.i18n.story_l10n import ACTIONS, KINDS, STORY, kind_of_event
from sitekpi.packs.behaviors import BEHAVIORS


def _soup(c, path):
    return BeautifulSoup(c.get(path).text, "html.parser")


def test_catalog_has_three_actions_for_every_kind_in_every_language():
    for loc in ("ja", "en", "ko"):
        assert set(ACTIONS[loc]) == set(KINDS), loc
        assert set(STORY[loc]) == set(STORY["ja"]), loc
        for kind, entry in ACTIONS[loc].items():
            assert entry["head"] and len(entry["acts"]) == 3, (loc, kind)
            for title, why, check, link in entry["acts"]:
                assert title and why and check and link in ("", "edit", "ch", "gl"), (loc, kind)


@pytest.mark.parametrize("event,kind", [
    ("user_engagement", "engage"), ("add_to_cart", "cart"), ("begin_checkout", "checkout"), ("purchase", "checkout"),
    ("pay_success", "checkout"), ("form_start", "form_start"), ("apply_start", "form_start"), ("form_submit", "form_submit"),
    ("entry_complete", "form_submit"), ("sign_up", "signup"), ("login", "signup"), ("click", "click"),
    ("file_download", "download"), ("video_complete", "video"), ("view_item", "browse"), ("scroll", "browse"),
])
def test_step_kinds(event, kind):
    assert kind_of_event(event) == kind


@pytest.mark.parametrize("cat", list(BEHAVIORS))
def test_every_behaviour_sample_tells_one_story(cat):
    """Every 目的 has ①〜④ with one issue: its steps are the orange stretch, ④ lists three actions."""
    s = _soup(TestClient(app), f"/type-{cat}")
    assert len(s.select(".story-toc .story-toc-step")) == 4, cat
    assert s.select_one(".story-toc-step.is-lede"), cat
    assert s.select_one(".verdict-text .v-issue"), cat
    assert not s.select_one("#q1"), cat

    stretch = s.select("#flow .flow-stage.is-issue")
    assert len(stretch) >= 2, cat
    a, b = stretch[0].select_one(".flow-label").get_text(), stretch[-1].select_one(".flow-label").get_text()
    assert f"「{a} → {b}」" in s.select_one("h2.where-answer").get_text(), cat
    assert len(s.select("#q4 .acts .act")) == 3 and s.select_one("#q4 [data-story-kind]")["data-story-kind"] in KINDS
    assert s.select_one("#q3 h2") and s.select_one(".q-next")


def test_gain_and_prompt_on_the_ec_sample():
    s = _soup(TestClient(app), "/ec")
    h4 = s.select_one("#q4 h2").get_text()
    assert "目安の下限 19.8% まで上がると、購入は +約 556 人 増える見込みです" in h4
    assert "10,800 人 × 19.8% − 1,580 人" in s.select_one("#q4 .q-note").get_text()
    assert [x.select_one(".act-t").get_text() for x in s.select("#q4 .act")][0] == "送料・手数料・届く日を、カートより前に見せる"
    # 自分の AI に聞く: copy only — the page holds the pieces, nothing is posted anywhere
    ai = s.select_one("#q4 [data-ai]")
    assert ai.select_one("button[data-ai-copy]") and ai.select_one("textarea[data-ai-text][readonly]")
    assert [b["data-ai-ask"] for b in ai.select("[data-ai-ask]")] == ["cause", "ideas", "report"]
    assert not ai.select("form") and not ai.select("a[href*='chatgpt'], a[href*='claude.ai'], a[href*='gemini']")
    p = json.loads(s.select_one("#ai-data").get_text())
    assert p["has_site"] is False  # samples have no site name
    assert "カートに追加 10,800" in p["body"] and "SiteKPI の対策案" in p["body"] and "+約" in p["body"]
    assert set(p["asks"]) == {"cause", "ideas", "report"} and "断定せず" in p["tail"]
    assert "転換ファネル" in p["details"]


def test_live_prompt_leaves_the_site_name_out_unless_asked():
    c = TestClient(app)
    c.get("/connect/demo?start=1")
    s = _soup(c, "/live")
    p = json.loads(s.select_one("#ai-data").get_text())
    assert p["has_site"] and "Demo Shop JP" in p["site_named"] and "Demo Shop JP" not in p["site_anon"]
    assert "Demo Shop JP" not in p["body"] and "Demo Shop JP" not in p["details"]
    assert s.select_one("[data-ai-anon][checked]")


@pytest.mark.parametrize("loc,q", [("en", "What to do?"), ("ko", "어떻게 할까?")])
def test_story_localized(loc, q):
    c = TestClient(app)
    c.post("/settings", data={"locale": loc})
    s = _soup(c, "/ec")
    assert s.select(".story-toc .story-toc-step")[0].get_text(" ", strip=True) in ("0 Overview", "0 총평")
    assert s.select(".story-toc .story-toc-step")[3].get_text(" ", strip=True) == f"3 {q}"
    html = str(s.select_one(".content"))
    assert "大丈夫？" not in html and "どうする？" not in html
    assert "있어요. ." not in html and ". . " not in s.select_one(".verdict-text").get_text()


def test_samples_preview_tells_the_same_story_as_the_board():
    """見本ボード一覧: the preview's 総評 and orange stretch are the board's (one issue everywhere)."""
    c = TestClient(app)
    prev = _soup(c, "/samples?b=commerce")
    board = _soup(c, prev.select_one(".sp-card-head a.sp-btn-primary")["href"])  # 「この見本をボードで開く」
    assert prev.select_one(".sp-verdict").get_text() == board.select_one(".verdict-text").get_text()
    marked = [li.select_one(".sp-bar-label").get_text() for li in prev.select(".sp-bars li.is-issue")]
    assert marked == [st.select_one(".flow-label").get_text() for st in board.select("#flow .flow-stage.is-issue")]
    assert len(prev.select(".sp-bars li")) == 7
