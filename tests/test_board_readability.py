"""Readability: いまの状態 → どこ → 詳しく, judge chips, grouped channels, collapsed 業務KPI."""

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
    assert len(s.select(".verdict .tile")) == 3
    assert "view-switch" not in html  # one table per tab; no per-section view modes


def _rows(s, group):
    return [r for r in s.select(f"#g-{group} .dt-row") if "dt-head" not in r["class"]]


def _name(r):
    return r.select_one(".row-name").get_text()


def _tpl(s, tid):
    raw = str(s.select_one(f"template#pop-{tid}"))
    return BeautifulSoup(raw.replace("<template", "<section").replace("</template>", "</section>"), "html.parser")


def test_board_reads_verdict_then_where_then_detail(client):
    """L0 いまの状態 (一言 + 3) → L1 どこ (行動フロー + 今見るべきこと) → L2 詳しい数字 (stacked)."""
    s = _soup(client, "/ec")
    order = [sec.get("class")[0] for sec in s.select(".content > section")]
    assert order == ["verdict", "where", "detail"]
    text = s.select_one(".verdict-text").get_text()
    assert text.startswith("購入完了は増えています。いちばんの課題は")
    tiles = s.select(".verdict .tile")
    assert [t.select_one(".tile-label").get_text() for t in tiles] == ["購入完了", "購入CVR", "カート→購入率"]
    assert "is-issue" in tiles[2]["class"] and tiles[2].select_one(".judge-down")
    assert tiles[0].select_one(".judge-na-chip")  # counts are never judged against the industry
    assert s.select_one(".where #flow, #flow.where") and s.select_one(".where .watch-list")
    groups = [g["id"] for g in s.select(".dgroup")]
    assert groups == ["g-funnel", "g-revenue", "g-engage", "g-channels", "g-device", "g-audience", "g-events", "g-biz"]
    assert [a["href"] for a in s.select(".dnav a")] == ["#" + g for g in groups]
    # よく見ないカテゴリは閉じて、上位3つを1行で
    assert s.select_one("#dt-audience[hidden]") and s.select_one("#g-audience [data-dgroup-summary]")
    assert not s.select_one("#dt-funnel[hidden]")
    # the page menu in the top bar
    assert [a["href"] for a in s.select(".top .page-nav a")] == ["#s-l0", "#flow", "#s-l2"]


def test_rows_show_benchmark_gap_trend_and_help(client):
    s = _soup(client, "/ec")
    row = _rows(s, "funnel")[1]
    assert row.select_one(".dt-bench .bench-v").get_text() == "19.8–39.8%"
    # あと: to the near edge of the range, then 〜 to the far edge
    gap = row.select_one(".dt-gap .rg-gap.is-short")
    assert gap.select_one("b").get_text() == "+5.2" and gap.select_one("small").get_text() == "〜+25.2pt"
    btn = row.select_one(".help-btn[data-help]")
    card = s.select_one(f"dialog#help-{btn['data-help']}")
    # the 説明 card is the 指標辞典 card: kind · title · 計算 · 見るポイント · 業界目安あり
    assert card.select_one(".gl-chip") and card.select_one(".gl-formula .mono") and card.select_one(".gl-tip")
    assert card.select_one(".gl-bench.is-on")
    assert _rows(s, "funnel")[0].select_one("svg.spark polyline")  # 8週の推移


def test_watch_ranks_metrics_outside_benchmark(client):
    s = _soup(client, "/hr")
    items = s.select(".watch-list .watch-item")
    assert items and "tone-down" in items[0]["class"]
    # 開始→完了率 has only a SiteKPI 初期値 → never judged; the sourced CVR is
    assert "応募CVR" in items[0].select_one(".watch-name").get_text()
    assert items[0].select_one(".judge.judge-down")
    assert not any("開始→完了率" in i.get_text() for i in items)
    # the long lines (目安帯 · 前期 · 見るポイント) moved to the 説明 popover
    pop = _tpl(s, "watch-1")
    assert "応募CVRが目安より低い" in pop.get_text() and pop.select_one(".pop-line")


def test_watch_says_so_when_nothing_is_off(client):
    s = _soup(client, "/b2c")
    assert not s.select(".watch-item")
    assert "大きく外れている指標はありません" in s.select_one(".watch").get_text()


def test_band_only_in_tooltip_and_judge_chips_in_tables(client):
    s = _soup(client, "/hr")
    assert not s.select(".bench-band")
    assert s.select_one("#g-funnel .dt-bench .bench-v[title]")
    chips = [c.get_text() for c in s.select("#g-funnel .judge-cell .judge:not(.judge-none)")]
    assert chips == ["要注意"]  # only the sourced 応募CVR is judged; 初期値 rows say 基準なし
    row = [r for r in _rows(s, "funnel") if "開始→完了率" in _name(r)][0]
    assert row.select_one(".judge-cell .judge-none[data-pop-open]")


def test_channels_top5_plus_others_with_help(client):
    s = _soup(client, "/hr")
    names = [_name(r) for r in _rows(s, "channels")]
    assert len(names) == 6 and names[-1] == "その他（5チャネル）"
    assert s.select_one("dialog#help-ch_others")
    pct = sum(int(r.select_one(".dt-value").get_text().rstrip("%")) for r in _rows(s, "channels"))
    assert pct == 100
    assert "セッション" in _rows(s, "channels")[0].select_one(".dt-sub").get_text()


def test_unlinked_business_kpis_collapse_to_one_line(client):
    s = _soup(client, "/hr")
    biz = s.select_one("#g-biz")
    assert "業務データ未連携（6指標）" in biz.select_one(".dgroup-note").get_text()
    assert not biz.select(".dt-row")


@pytest.mark.parametrize("loc,text", [("en", "What to look at now"), ("ko", "지금 봐야 할 것")])
def test_localized(client, loc, text):
    client.post("/settings", data={"locale": loc})
    html = client.get("/hr").text
    assert text in html and "今見るべきこと" not in html
    assert not re.search(r'class="judge[^"]*">(要注意|目安内|良好)<', html)


def test_cited_benchmarks_link_their_source(client):
    html = client.get("/ec").text
    s = BeautifulSoup(html, "html.parser")
    link = _tpl(s, "bench-signup_to_pay").select_one("a.src-btn[href='https://baymard.com/lists/cart-abandonment-rate']")
    assert link and "70.22%" in link["title"] and link.get_text(strip=True) == "出典"
    assert _tpl(s, "bench-pages_session").select_one(".pop-why") and not _tpl(s, "bench-pages_session").select_one("a.src-btn")
    cell = s.select_one("#g-funnel .dt-bench .bench-v[title*='Baymard']")
    assert cell and cell.get_text() == "19.8–39.8%" and "±10pt" in cell["title"]
    assert cell["title"].startswith("業界目安帯 19.8–39.8%")


def test_issue_tile_never_repeats_the_rate_tile(client):
    """/hr: 応募CVR is the only metric below its 目安 and already has tile 2 → tile 3 is the flow's biggest drop."""
    s = _soup(client, "/hr")
    labels = [t.select_one(".tile-label").get_text() for t in s.select(".verdict .tile")]
    assert labels == ["応募完了", "応募CVR", "求人を見た → 応募を開始"]
    assert "90.7% が次に進まない" in _tpl(s, "tile-3").get_text()