"""Readability: 今見るべきこと, judge chips, grouped channels, collapsed 業務KPI."""

from __future__ import annotations

import re

import pytest
from bs4 import BeautifulSoup
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    return TestClient(app, base_url="http://127.0.0.1:8766", follow_redirects=False)


def _soup(client, path):
    return BeautifulSoup(client.get(path).text, "html.parser")


def test_no_simple_mode_and_no_next_points(client):
    """かんたん mode and 次に見るポイント were removed (user decision)."""
    html = client.get("/hr").text
    assert "board-mode" not in html and "mode-toggle" not in html
    assert "detail-only" not in html and "simple-hide" not in html
    assert "次に見るポイント" not in html and 'class="insights"' not in html
    s = BeautifulSoup(html, "html.parser")
    assert len(s.select(".summary .sum-item")) == 6


def test_watch_ranks_metrics_outside_benchmark(client):
    s = _soup(client, "/hr")
    items = s.select(".watch-list .watch-item")
    assert items and "tone-down" in items[0]["class"]
    assert "開始→完了率が目安より低い" in items[0].get_text()
    assert items[0].select_one(".judge.judge-down")
    assert "差 -18.3pt" in items[0].get_text()
    assert s.select_one(".watch-sample")  # sample boards say so


def test_watch_says_so_when_nothing_is_off(client):
    s = _soup(client, "/b2c")
    assert not s.select(".watch-item")
    assert "大きく外れている指標はありません" in s.select_one(".watch").get_text()


def test_band_only_in_tooltip_and_judge_chips_in_tables(client):
    s = _soup(client, "/hr")
    assert not s.select(".bench-band")
    cell = s.select_one("#panel-funnel td.bench-cell[title]")
    assert "40–65%" in s.select_one("#panel-funnel").decode() and cell
    chips = [c.get_text() for c in s.select("#panel-funnel td.bench-gap .judge")]
    assert "要注意" in chips and "目安内" in chips


def test_channels_top5_plus_others_with_help(client):
    s = _soup(client, "/hr")
    names = [n.get_text() for n in s.select("#panel-channels .mode-list .row-name")]
    assert len(names) == 6 and names[-1] == "その他（5チャネル）"
    assert s.select_one("dialog#help-ch_others")
    pct = sum(int(x.get_text().rstrip("%")) for x in s.select("#panel-channels .mode-list .chan-meta strong"))
    assert pct == 100


def test_unlinked_business_kpis_collapse_to_one_line(client):
    s = _soup(client, "/hr")
    biz = s.select_one("#panel-biz")
    assert "業務データ未連携（6指標）" in biz.get_text()
    assert not biz.select("table") and not biz.select(".view-switch")
    assert len(biz.select(".biz-collapsed-list li .help-btn")) == 6


@pytest.mark.parametrize("loc,text", [("en", "What to look at now"), ("ko", "지금 봐야 할 것")])
def test_localized(client, loc, text):
    client.post("/settings", data={"locale": loc})
    html = client.get("/hr").text
    assert text in html and "今見るべきこと" not in html
    assert not re.search(r'class="judge[^"]*">(要注意|目安内|良好)<', html)


def test_cited_benchmarks_link_their_source(client):
    html = client.get("/ec").text
    s = BeautifulSoup(html, "html.parser")
    def pop(key):
        raw = str(s.select_one(f"template#pop-bench-{key}"))
        return BeautifulSoup(raw.replace("<template", "<section").replace("</template>", "</section>"), "html.parser")
    link = pop("signup_to_pay").select_one("a.src-btn[href='https://baymard.com/lists/cart-abandonment-rate']")
    assert link and "70.22%" in link["title"] and link.get_text(strip=True) == "出典"
    assert "SiteKPI 初期値" in pop("pages_session").select_one(".src-none").get_text()
    cell = s.select_one("#panel-funnel td.bench-cell[title*='Baymard']")
    assert cell and cell.get_text() == "29.8%" and "±10pt" in cell["title"]
    assert cell["title"].startswith("業界目安帯 19.78–39.78%")
