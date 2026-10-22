"""Templates: autoescape, versioned static assets, no inline CSS/JS blobs."""

from __future__ import annotations

import re

from fastapi.testclient import TestClient

from main import app
from sitekpi.templating import render

PAGES = ["/", "/ec", "/builder", "/connect", "/settings"]


def _client() -> TestClient:
    return TestClient(app, base_url="http://127.0.0.1:8766", follow_redirects=False)


def test_values_are_autoescaped():
    html = render(
        "connect.html", loc="ja", rail=None, configured=True, oauth_ready=True,
        connected=True, demo=False, email="", properties=[], preview=None,
        selected={"id": "1", "name": "<script>alert(1)</script>", "account": "a&b"},
        error='"><img src=x onerror=alert(1)>', pack_groups=[], benchmark_pack="",
        benchmark_pack_label="", redirect_uri="", base_url="", knows_events=False,
    )
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    assert "<img src=x" not in html
    assert "a&amp;b" in html


def test_json_data_islands_cannot_break_out():
    from sitekpi.views.builder import render_builder

    html = render_builder(widgets=[{"id": "x", "group": "digital", "label": "</script><b>", "value": "1"}])
    island = html.split('id="builder-data">', 1)[1].split("</script>", 1)[0]
    assert "</script>" not in island and "<b>" not in island  # tojson escapes < >


def test_pages_use_versioned_static_assets_and_cache_headers():
    c = _client()
    seen = set()
    for path in PAGES:
        html = c.get(path).text
        assert "<style" not in html, path  # CSS lives in static/css
        for url in re.findall(r'(?:href|src)="(/static/(?:css|js|vendor)/[^"]+)"', html):
            assert "?v=" in url, url
            seen.add(url)
    assert seen
    for url in seen:
        r = c.get(url)
        assert r.status_code == 200, url
        assert "immutable" in r.headers["cache-control"]
    plain = c.get("/static/favicon.svg")
    assert plain.headers["cache-control"] == "no-cache"


def test_builder_uses_bundled_sortable():
    html = _client().get("/builder").text
    assert "cdn.jsdelivr.net" not in html
    assert "/static/vendor/sortable-1.15.6.min.js" in html


def test_html_is_gzipped():
    r = _client().get("/ec", headers={"Accept-Encoding": "gzip"})
    assert r.headers.get("content-encoding") == "gzip"
