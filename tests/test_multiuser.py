"""Nothing user-specific may leak through process-wide state."""

from __future__ import annotations

import threading
from pathlib import Path

from fastapi.testclient import TestClient

from main import app
from sitekpi.cache import TTLCache
from sitekpi.views.board import render_sample_dense

ROOT = Path(__file__).resolve().parents[1]


def test_concurrent_renders_keep_their_own_benchmarks():
    """Regression: 業界目安 used to live in a module global shared by all requests."""
    slugs = ["ec", "finance", "hr", "gov"]
    expected = {s: render_sample_dense(industry=s, period="28d", locale="ja") for s in slugs}
    wrong: list[str] = []

    def worker(slug: str) -> None:
        for _ in range(25):
            if render_sample_dense(industry=slug, period="28d", locale="ja") != expected[slug]:
                wrong.append(slug)

    threads = [threading.Thread(target=worker, args=(s,)) for s in slugs * 2]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert wrong == []


def test_two_users_have_independent_sessions():
    a = TestClient(app, base_url="http://127.0.0.1:8766", follow_redirects=False)
    b = TestClient(app, base_url="http://127.0.0.1:8766", follow_redirects=False)
    for c, pack in ((a, "ec"), (b, "hr")):
        c.get("/connect/demo")
        c.post("/connect/property", data={"property_id": "123456789"})
        c.post("/connect/pack", data={"pack_slug": pack})
    assert "EC・小売" in a.get("/live").text
    assert "人事・採用" in b.get("/live").text
    b.post("/connect/disconnect")  # B leaving must not affect A
    assert a.get("/live").status_code == 200
    assert b.get("/live").status_code == 302


def test_no_shared_choice_file_is_written():
    path = ROOT / ".ga4_connection.json"
    before = path.stat().st_mtime if path.exists() else None
    c = TestClient(app, base_url="http://127.0.0.1:8766", follow_redirects=False)
    c.get("/connect/demo")
    c.post("/connect/property", data={"property_id": "987654321"})
    c.post("/connect/pack", data={"pack_slug": "news"})
    after = path.stat().st_mtime if path.exists() else None
    assert before == after


def test_ttl_cache_expires_and_is_bounded(monkeypatch):
    now = [1000.0]
    monkeypatch.setattr("sitekpi.cache.time.monotonic", lambda: now[0])
    cache = TTLCache(maxsize=2, ttl=60)
    cache.set("a", 1)
    cache.set("b", 2)
    cache.set("c", 3)  # evicts the oldest
    assert cache.get("a") is None and cache.get("c") == 3 and len(cache) == 2
    now[0] += 61
    assert cache.get("b") is None and cache.get("c") is None
