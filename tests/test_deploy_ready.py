"""Cloud Run readiness: Firestore stores (fake client), feedback, policy/terms, revoke on disconnect."""

from __future__ import annotations

import copy

import pytest
from bs4 import BeautifulSoup
from fastapi.testclient import TestClient

from sitekpi import firestore_store as fs


class _Snap:
    def __init__(self, data):
        self._data = data

    @property
    def exists(self):
        return self._data is not None

    def to_dict(self):
        return copy.deepcopy(self._data) if self._data is not None else None


class _Doc:
    def __init__(self, db, path):
        self.db, self.path = db, path

    def collection(self, name):
        return _Col(self.db, self.path + (name,))

    def get(self):
        return _Snap(self.db.data.get(self.path))

    def set(self, data):
        self.db.data[self.path] = dict(data)

    def delete(self):
        self.db.data.pop(self.path, None)


class _Col:
    def __init__(self, db, path):
        self.db, self.path = db, path

    def document(self, doc_id=None):
        self.db.n += 1
        return _Doc(self.db, self.path + (doc_id or f"auto{self.db.n}",))


class FakeFirestore:
    def __init__(self):
        self.data, self.n = {}, 0

    def collection(self, name):
        return _Col(self, (name,))


@pytest.fixture
def fake(monkeypatch):
    db = FakeFirestore()
    monkeypatch.setenv("STORE_BACKEND", "firestore")
    fs.set_client(db)
    yield db
    fs.set_client(None)


def test_firestore_mapping_store(fake):
    st = fs.FirestoreMappingStore()
    st.set("prop:1", "type-commerce", "begin_checkout", "start_checkout")
    assert st.get("prop:1", "type-commerce") == {"begin_checkout": "start_checkout"}
    st.set_custom_flow("prop:1", "type-commerce", [{"key": "a", "event": "b", "label": "c"}])
    assert st.custom_flow("prop:1", "type-commerce")[0]["event"] == "b"
    ids = [st.add_branch("prop:1", "type-commerce", "a", "above", f"e{i}", "x") for i in range(4)]
    assert ids[3] is None and len(st.branches("prop:1", "type-commerce")) == 3
    assert st.update_branch("prop:1", "type-commerce", ids[0], "z", "y")
    st.delete_branch("prop:1", "type-commerce", ids[1])
    assert [b["event"] for b in st.branches("prop:1", "type-commerce")] == ["z", "e2"]
    st.set("prop:1", "type-commerce", "begin_checkout", None)
    st.set_custom_flow("prop:1", "type-commerce", None)
    for b in st.branches("prop:1", "type-commerce"):
        st.delete_branch("prop:1", "type-commerce", b["id"])
    assert not fake.data  # empty → document removed
    assert all(k[0] == "sitekpi" for k in fake.data)


def test_firestore_benchmark_and_session_stores(fake):
    b = fs.FirestoreBenchmarkStore()
    b.set_many("prop:1", "ec", {"engaged": (50.0, 60.0), "bounce_rate": (30.0, 40.0)})
    assert b.get("prop:1", "ec")["engaged"]["low"] == 50.0
    b.reset("prop:1", "ec", "engaged")
    assert list(b.get("prop:1", "ec")) == ["bounce_rate"]
    b.reset("prop:1", "ec")
    assert b.get("prop:1", "ec") == {}

    s = fs.FirestoreSessionStore("secret-for-tests-0123456789", 3600)
    s.save("sid-1", {"ga4_property": {"id": "1"}})
    data, exp = s.load("sid-1")
    assert data == {"ga4_property": {"id": "1"}} and exp > 0
    stored = next(iter(fake.data.values()))
    assert b"ga4_property" not in bytes(stored["data"])  # encrypted at rest
    s.delete("sid-1")
    assert s.load("sid-1") is None


def test_getters_pick_firestore(fake):
    from sitekpi.benchmarks import get_store
    from sitekpi.flow import get_mapping_store

    assert isinstance(get_mapping_store(), fs.FirestoreMappingStore)
    assert isinstance(get_store(), fs.FirestoreBenchmarkStore)


@pytest.fixture
def client():
    from main import app

    return TestClient(app)


def test_feedback_saved_without_ip(client, fake):
    r = client.post("/feedback", json={"vote": "up", "comment": "わかりやすい", "screen": "glossary", "path": "/glossary"})
    assert r.status_code == 200 and r.json() == {"ok": True}
    row = next(v for k, v in fake.data.items() if k[:2] == ("sitekpi", "feedback"))
    assert row["vote"] == "up" and row["screen"] == "glossary" and row["connected"] == "none"
    assert not any("ip" in k.lower() for k in row)
    assert client.post("/feedback", json={"vote": "maybe"}).status_code == 400
    assert client.post("/feedback", json={}).status_code == 400


def test_policy_terms_and_rail_links(client):
    for path in ("/policy", "/policy?lang=en", "/policy?lang=ko", "/terms", "/terms?lang=en", "/terms?lang=ko"):
        s = BeautifulSoup(client.get(path).text, "html.parser")
        assert s.select_one(".legal-body h1"), path
    en = client.get("/policy?lang=en").text
    assert "analytics.readonly" in en and "Limited Use" in en
    s = BeautifulSoup(client.get("/glossary").text, "html.parser")
    assert s.select_one("[data-feedback-open]") and s.select_one("dialog#feedback")
    assert s.select_one('.nav-legal a[href="/policy"]') and s.select_one('.nav-legal a[href="/terms"]')


def test_disconnect_revokes_at_google(client, monkeypatch):
    import sitekpi.routes.connect as connect

    seen = []
    monkeypatch.setattr(connect, "_revoke_at_google", lambda creds: seen.append(creds.get("refresh_token")))
    client.get("/connect/demo")  # demo: nothing to revoke
    client.post("/connect/disconnect")
    assert seen == []
