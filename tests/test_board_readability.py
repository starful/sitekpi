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
    assert len(s.select(".verdict .stat")) == 3
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
    assert order == ["verdict", "where", "why", "do", "detail"]
    # v6 story: the same one issue in ① (orange clause) … ④
    text = s.select_one(".verdict-text").get_text()
    assert text == "購入完了は増えています。ただ、カートに入れた人が買い切れていません。"
    assert [a.get_text(" ", strip=True) for a in s.select(".story-strip .story-step .qk")] == ["1 大丈夫？", "2 どこで離れている？", "3 どこがおかしい？", "4 どうする？"]
    assert [a["href"] for a in s.select(".story-strip a")] == ["#q1", "#q2", "#q3", "#q4"]
    tiles = s.select(".verdict .stat")
    # v5: 3 columns, no boxes or chips; the issue says so in its label and in orange in the sentence
    assert [t.select_one(".stat-name").get_text() for t in tiles] == ["購入完了", "購入CVR", "カート→購入率（いちばんの課題）"]
    assert s.select_one(".verdict-text .v-issue").get_text() == "カートに入れた人が買い切れていません"
    assert "is-issue" in tiles[2]["class"] and tiles[2].select_one(".jt.jt-down")
    assert "業界と比べません" in tiles[0].select_one(".stat-note").get_text()  # counts are never judged
    assert not s.select(".verdict .judge, .verdict .tile-tag, .tiles")
    assert s.select_one(".where #flow, #flow.where") and s.select_one("#q3 .wtable")
    groups = [g["id"] for g in s.select(".dgroup")]
    assert groups == ["g-funnel", "g-revenue", "g-engage", "g-channels", "g-device", "g-audience", "g-events", "g-biz"]
    assert not s.select(".dnav")
    # v5: the first three categories are open, the rest closed; a chevron, no 開く / 閉じる text
    assert not s.select("#dt-funnel[hidden], #dt-revenue[hidden], #dt-engage[hidden]")
    assert s.select_one("#dt-audience[hidden]") and s.select_one("#dt-channels[hidden]")
    tg = s.select_one('#g-funnel [data-dgroup-toggle][aria-controls="dt-funnel"]')
    assert tg["aria-expanded"] == "true" and tg.select_one(".chev svg") and "開く" not in tg.get_text()
    assert [h.get_text() for h in s.select("#dt-funnel .dt-head span")] == ["指標", "値", "8週", "前期比", "業界", "あと"]
    # less on screen first: channel chips and the 流入別 table wait behind 「流入別に見る」
    assert s.select_one("[data-ch-toggle]") and all(x.has_attr("hidden") for x in s.select("[data-ch-part]"))
    # v5: メモ panel instead of 👍 👎 under each card; 「? 見方」 in the top bar; no page menu
    assert not s.select("[data-card-fb]") and s.select_one("aside.memo[data-memo] textarea[data-memo-text]")
    assert [x["data-memo-where"] for x in s.select(".content > section")] == ["大丈夫？", "どこで離れている？", "どこがおかしい？", "どうする？", "詳しい数字"]
    assert s.select_one('.top a.top-help[href="/help#read"]')
    assert not s.select(".page-nav")


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
    # v6: ③ どこがおかしい？ — the issue's step first, then the metrics that are off (with 業界目安)
    items = s.select("#q3 .wtable .watch-item")
    assert items and "tone-down" in items[0]["class"]
    assert items[0].select_one(".watch-name").get_text() == "求人を見た → 応募を開始"
    # 開始→完了率 has only a SiteKPI 初期値 → never judged; the sourced CVR is
    assert "応募CVR" in items[1].select_one(".watch-name").get_text() and items[1]["data-metric"] == "signup_rate"
    assert [h.get_text() for h in s.select("#q3 .wtable .whead span")] == ["", "今", "前期比", "業界", "あと"]
    assert not any("開始→完了率" in i.get_text() for i in items)
    # the long lines (目安帯 · 前期 · 見るポイント) moved to the 説明 popover
    pop = _tpl(s, "watch-1")
    assert "応募CVRが目安より低い" in pop.get_text() and pop.select_one(".pop-line")


def test_watch_says_so_when_nothing_is_off(client):
    s = _soup(client, "/b2c")
    assert not s.select(".watch-item[data-metric]")
    assert "大きく外れている指標はありません" in s.select_one("#q3 .watch").get_text()


def test_band_only_in_tooltip_and_judge_chips_in_tables(client):
    s = _soup(client, "/hr")
    assert not s.select(".bench-band")
    assert s.select_one("#g-funnel .dt-bench .bench-v[title]")
    assert not s.select("#g-funnel .judge-cell, #g-funnel .judge")  # v5: no 判定 column, no chips
    judged = [r for r in _rows(s, "funnel") if r.select_one(".dt-gap .rg-gap")]
    assert [_name(r) for r in judged] == ["応募CVR"]  # only the sourced 応募CVR is judged
    row = [r for r in _rows(s, "funnel") if "開始→完了率" in _name(r)][0]
    assert row.select_one(".dt-gap .jt-none[data-pop-open]")  # 初期値 rows say 基準なし


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


@pytest.mark.parametrize("loc,text", [("en", "What is off?"), ("ko", "어디가 이상한가?")])
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
    labels = [t.select_one(".stat-name").get_text() for t in s.select(".verdict .stat")]
    assert labels == ["応募完了", "応募CVR", "求人を見た → 応募を開始（いちばんの課題）"]
    assert "90.7% が次に進まない" in _tpl(s, "tile-3").get_text()

def test_board_css_uses_the_six_text_sizes_only():
    """v4: 26 · 22 · 18 · 15 · 13 · 12px — nothing in between."""
    import re
    from pathlib import Path

    allowed = {"0.75rem", "0.8125rem", "0.9375rem", "1.125rem", "1.375rem", "1.625rem"}
    for name in ("board.css", "rail.css", "helpcard.css", "setup.css"):
        css = (Path(__file__).resolve().parents[1] / "static" / "css" / name).read_text()
        sizes = set(re.findall(r"font-size:\s*([0-9.]+(?:rem|px))", css))
        assert sizes <= allowed, (name, sorted(sizes - allowed))
