"""SiteKPI's own visitor log, the 30-second survey and the HQ read API (sitekpi/visitlog.py)."""

import time

import pytest
from fastapi.testclient import TestClient

from sitekpi import visitlog
from sitekpi.app import app


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(visitlog, "_counts", {})
    return TestClient(app)


def test_events_set_an_anonymous_id_and_keep_only_whitelisted_params(client):
    r = client.post("/events", json={"path": "/ec?x=secret", "lang": "ja", "events": [
        {"e": "pv", "p": {"screen": "home", "property_id": "123456"}, "ref": "https://www.google.com/search?q=ga4"},
        {"e": "board_view", "p": {"mode": "sample", "period": "28d"}},
        {"e": "Bad Name!", "p": {}},
    ]})
    assert r.status_code == 200
    vid = r.cookies.get("sk_vid")
    assert vid and len(vid) == 24
    rows = [x for x in visitlog.get_store().events_since(int(time.time()) - 60) if x["vid"] == vid]
    assert [x["e"] for x in rows] == ["pv", "board_view"]
    assert rows[0]["p"] == {"screen": "home"}  # property_id is not a SiteKPI key → dropped
    assert rows[0]["ref"] == "www.google.com"  # host only
    assert rows[0]["path"] == "/ec"  # no query


def test_events_reject_junk_and_flooding(client, monkeypatch):
    assert client.post("/events", content=b"nope").status_code == 400
    assert client.post("/events", json={"events": []}).status_code == 400
    monkeypatch.setattr(visitlog, "DAILY_MAX", 3)
    client.cookies.set("sk_vid", "a" * 24)
    for _ in range(3):
        client.post("/events", json={"events": [{"e": "cta_click", "p": {}}] * 2})
    rows = [x for x in visitlog.get_store().events_since(int(time.time()) - 60) if x["vid"] == "a" * 24]
    assert len(rows) == 2


def test_survey_keeps_known_answers_and_one_line(client):
    client.cookies.set("sk_vid", "b" * 24)
    r = client.post("/survey", json={"answers": {"source": "search", "goal": "report", "role": "hacker", "pain": "none"},
                                     "text": "x" * 300, "lang": "ko"})
    assert r.status_code == 200
    row = next(s for s in visitlog.get_store().surveys_since(0) if s["vid"] == "b" * 24)
    assert row["answers"] == {"source": "search", "goal": "report", "pain": "none"}
    assert len(row["text"]) == 200
    assert client.post("/survey", json={"answers": {"goal": "nope"}}).status_code == 400


def test_hq_key_comes_from_the_session_secret():
    import hashlib
    import hmac
    want = hmac.new(b"abc", b"sitekpi-hq-api-v1", hashlib.sha256).hexdigest()
    assert visitlog.hq_token("abc") == want and visitlog.hq_token("") == ""


def test_hq_api_is_off_without_token_and_needs_the_bearer(client, monkeypatch):
    monkeypatch.delenv("HQ_API_TOKEN", raising=False)
    monkeypatch.setenv("SESSION_SECRET", "")
    assert client.get("/hq/api/users").status_code == 404
    monkeypatch.setenv("SESSION_SECRET", "test-secret")
    assert client.get("/hq/api/users", headers={"Authorization": "Bearer " + visitlog.hq_token("test-secret")}).status_code == 200
    monkeypatch.setenv("HQ_API_TOKEN", "t0ken-for-tests")
    assert client.get("/hq/api/users").status_code == 401
    assert client.get("/hq/api/users", headers={"Authorization": "Bearer wrong"}).status_code == 401
    r = client.get("/hq/api/users?days=30", headers={"Authorization": "Bearer t0ken-for-tests"})
    assert r.status_code == 200
    body = r.json()
    assert body["days"] == 30 and [k["label"] for k in body["kpis"]][0] == "방문자"


def test_summarize_funnel_survey_and_timeline():
    now = int(time.time())
    ev = lambda vid, t, e, **p: {"vid": vid, "at": now - t, "e": e, "p": p, "path": "/", "ref": "", "lang": "ja"}
    events = [
        ev("v1" * 12, 900, "pv", screen="home"), ev("v1" * 12, 800, "board_view", mode="sample"),
        ev("v1" * 12, 700, "oauth_start"), ev("v1" * 12, 600, "login"), ev("v1" * 12, 500, "board_view", mode="live"),
        ev("v2" * 12, 9000, "pv", screen="home"), ev("v2" * 12, 100, "board_view", mode="sample"),
        ev("v3" * 12, 50, "pv", screen="home"),
    ]
    surveys = [{"vid": "v2" * 12, "at": now - 90, "answers": {"goal": "judge", "role": "owner"}, "text": "주간 보고", "lang": "ko"}]
    out = visitlog.summarize(events, surveys, days=7, now=now, prev_visitors=1)
    assert [f["n"] for f in out["funnel"]] == [3, 2, 1, 1, 1, 0]
    assert out["stuck"].startswith("가장 많이 멈추는 곳: 랜딩 → 견본 보드")
    assert out["kpis"][0]["value"] == 3 and out["kpis"][2]["value"] == 1
    goal = next(q for q in out["survey"] if q["q"] == "오늘 무엇을 하려고 왔나")
    assert goal["rows"] == [{"label": "내 사이트 숫자가 좋은지 알고 싶다", "n": 1}]
    assert out["wishes"][0]["text"] == "주간 보고" and "사이트 운영자" in out["wishes"][0]["who"]
    v2 = next(v for v in out["visitors"] if v["id"] == "v2v2")
    assert v2["visits"] == 2 and v2["why"] == "내 사이트 숫자가 좋은지 알고 싶다"
    v1 = next(v for v in out["visitors"] if v["id"] == "v1v1")
    assert v1["did"].startswith("견본 보드 · 연결 시작 · GA4 연결 · 내 보드")
    assert [s["what"] for s in v1["steps"]][:2] == ["랜딩", "견본 보드 보기"]


def test_board_pages_carry_the_survey_card_and_policy_mentions_the_cookie(client):
    html = client.get("/ec").text
    assert "data-survey" in html and "js/survey.js" in html
    for lang, word in (("ja", "sk_vid"), ("en", "sk_vid"), ("ko", "sk_vid")):
        assert word in client.get(f"/policy?lang={lang}").text
