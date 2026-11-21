"""今見るべきこと · 見るポイント by visitor behavior (i18n/watch_tips_l10n.py)."""

from __future__ import annotations

from sitekpi.i18n.watch_tips_l10n import BY_BEHAVIOR, BY_GROUP, watch_tip
from sitekpi.packs import BENCHMARKS, DEMO, INDUSTRIES
from sitekpi.packs.behaviors import BEHAVIORS, GROUPS, PREFIX
from sitekpi.views.board_verdict import behavior_of

BENCH_KEYS = {k for b in BENCHMARKS.values() for k in b}


def test_catalog_keys_and_languages():
    assert set(BY_GROUP) == set(GROUPS)
    assert set(BY_BEHAVIOR) <= set(BEHAVIORS)
    for table in list(BY_GROUP.values()) + list(BY_BEHAVIOR.values()):
        for key, tip in table.items():
            assert key in BENCH_KEYS, key
            assert set(tip) == {"ja", "en", "ko"} and all(v.strip() for v in tip.values())


def test_behavior_first_then_group_then_nothing():
    assert watch_tip("call_line", "contact", "signup_rate", "en").startswith("This counts phone")
    assert watch_tip("lead", "contact", "signup_rate", "ko") == BY_GROUP["contact"]["signup_rate"]["ko"]
    assert watch_tip("lead", "contact", "churn_rate", "ja") == ""  # → the metric's common tip


def test_behavior_of_pack_slugs():
    assert behavior_of("ec") == ("commerce", "buy")
    assert behavior_of(PREFIX + "video") == ("video", "read")
    assert behavior_of("nope") == ("", "")


def test_board_watch_rows_use_behavior_tips():
    """Every pack × language: a bad watch row with a catalog entry shows that entry, not the common tip."""
    from sitekpi.views.board import build_dense_board
    from sitekpi.views.board_bench import _bench_info  # noqa: F401  (ContextVar set below)
    from sitekpi.views.board_ctx import _ACTIVE_BENCH
    from sitekpi.views.board_verdict import _watch_items

    hits = 0
    for slug in INDUSTRIES:
        beh, group = behavior_of(slug)
        for loc in ("ja", "en", "ko"):
            board = build_dense_board(industry=slug, period="28d", ind=INDUSTRIES[slug], data=DEMO[slug]["28d"],
                                      benches_raw=BENCHMARKS[slug], locale=loc, prev=None)
            token = _ACTIVE_BENCH.set(board["benches"])
            try:
                for w in _watch_items(board, loc, industry=slug):
                    want = watch_tip(beh, group, w["bench_key"], loc)
                    if w["tone"] == "down" and want:
                        assert w["tip"] == want
                        hits += 1
            finally:
                _ACTIVE_BENCH.reset(token)
    assert hits  # the samples do have off-target rows that get a behavior tip
