"""更新情報 (/updates): same releases in three languages, newest first, linked from the menu and footer."""

from pathlib import Path

import pytest
from bs4 import BeautifulSoup
from fastapi.testclient import TestClient

from main import app
from sitekpi.i18n.updates_l10n import _ENTRIES, _TEXT, updates


def test_entries_line_up_in_every_language():
    dates = [d for _, d, _, _ in _ENTRIES]
    assert dates == sorted(dates, reverse=True)
    vers = [v for _, _, v, _ in _ENTRIES]
    assert len(set(vers)) == len(vers) and all(v.startswith("v0.") for v in vers)
    for loc, t in _TEXT.items():
        assert len(t["entries"]) == len(_ENTRIES), loc
        assert [[k for k, _ in items] for _, items in t["entries"]] == [[k for k, _ in items] for _, items in _TEXT["ja"]["entries"]]
        assert "{link}" in t["dev"]


def test_versions_match_the_github_release_notes():
    """Each release file (docs/releases, when present) has a card here, with the same date."""
    notes = Path(__file__).resolve().parent.parent / "docs" / "releases"
    files = sorted(notes.glob("v*.md")) if notes.is_dir() else []
    cards = {v: d for _, d, v, _ in _ENTRIES}
    for f in files:
        meta = dict(line.split(": ", 1) for line in f.read_text(encoding="utf-8").split("---")[1].strip().splitlines())
        assert cards.get(meta["tag"]) == meta["date"], f.name


@pytest.mark.parametrize("lang,title", [("ja", "更新情報"), ("en", "What's new"), ("ko", "업데이트 소식")])
def test_page_and_links(lang, title):
    c = TestClient(app, headers={"Accept-Language": lang})
    s = BeautifulSoup(c.get("/updates").text, "html.parser")
    assert s.select_one("h1").get_text() == title
    cards = s.select(".up-card")
    assert len(cards) == len(_ENTRIES) and "is-new" in cards[0]["class"] and not s.select(".up-card.is-new")[1:]
    assert [c_.select_one(".up-ver").get_text() for c_ in cards] == [v for _, _, v, _ in _ENTRIES]
    assert cards[0].select_one(".up-try a")["href"] == "/glossary" and cards[2].select_one(".up-try a")["href"] == "/ec"
    assert s.select_one('.up-dev a[href="https://github.com/starful/sitekpi/releases"]')
    assert [a["href"] for a in s.select(".hp-toc a")] == [f"#{e['id']}" for e in updates(lang)["entries"]]
    assert s.select('a[href="/updates"]')  # the menu
    home = BeautifulSoup(c.get("/").text, "html.parser")
    assert home.select('a[href^="/updates"]')  # the public footer
    assert "/updates" in TestClient(app).get("/sitemap.xml").text
