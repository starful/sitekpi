"""自社の前期比: every metric compares with the previous period (not made-up deltas)."""

from __future__ import annotations

from sitekpi.board.data import build_dense_board
from sitekpi.board.prev import sample_prev
from sitekpi.packs import BENCHMARKS, DEMO, INDUSTRIES


def _board(slug, data, prev):
    return build_dense_board(industry=slug, period="28d", ind=INDUSTRIES[slug], data=data,
                             benches_raw=BENCHMARKS[slug], prev=prev)


def _rows(board):
    return {r["id"]: r for r in board["summary"] + board["funnel"] + board["engage"] + board["audience"]}


def test_sample_prev_matches_the_demo_growth():
    data = DEMO["ec"]["28d"]
    rows = _rows(_board("ec", data, sample_prev("ec", "28d", data)))
    assert rows["uu"]["delta"] == f"+{data['uu_delta']:.1f}%"
    assert rows["sessions"]["delta"] == f"+{data['sessions_delta']:.1f}%"
    assert all(rows[k]["delta"].endswith("pt") for k in ("signup_cvr", "engaged", "funnel_rate_a"))


def test_prev_is_judged_by_direction():
    data = dict(DEMO["hr"]["28d"])
    prev = dict(data, engaged_rate=data["engaged_rate"] + 5, uu=data["uu"] // 2)
    rows = _rows(_board("hr", data, prev))
    assert rows["engaged"]["delta"] == "−5.0pt" and rows["engaged"]["tone"] == "down"
    assert rows["bounce_like"]["delta"] == "+5.0pt" and rows["bounce_like"]["tone"] == "down"  # more bounce = worse
    assert rows["uu"]["tone"] == "up"


def test_without_prev_nothing_is_invented():
    rows = _rows(_board("hr", DEMO["hr"]["28d"], None))
    assert {r["delta"] for r in rows.values()} == {"—"}


def test_board_shows_prev_column_and_trend_in_watch():
    from fastapi.testclient import TestClient
    from main import app

    html = TestClient(app).get("/ec").text
    assert "<th style=\"text-align:right\">前期比</th>" in html
    assert 'class="watch-trend"' in html and "自社の前期" in html
