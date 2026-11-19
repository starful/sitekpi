"""Page-level numbers for the story (docs/plan s03, v7.3): which pages people start on, and how far they get.

Shape (``story_x["pages"]``, read only by views/story_pages.py):

    entry: [{"path", "title", "users", "eng", "ev": {event: users}}]   landing page (the first page of a visit)
           users = people whose visit started there; ev = those of them who fired the event in that visit;
           eng = engagement rate of those visits (%, or None)
    views: [{"path", "title", "views"}]                                  most viewed pages
    url on both lists: "https://{host}{path}" — the host GA4 saw most for that path (live only; samples have none)
    n_pages: how many pages GA4 saw in the period

Titles: GA4 page titles with the site-name tail most titles share taken off; a dict {ja, en, ko} for samples.
"""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlsplit

from sitekpi.board.prev import _jitter


def path_key(url: str) -> str:
    """'https://x.com/a/b/?q=1' · '/a/b' · '/a/b/' → '/a/b'. Home → '/'."""
    raw = str(url or "").strip()
    path = urlsplit(raw).path if "://" in raw else raw.split("?", 1)[0].split("#", 1)[0]
    path = path or "/"
    if not path.startswith("/"):
        path = "/" + path
    return path.rstrip("/") or "/"


SEPS = (" | ", " ｜ ", " - ", " — ", " – ", " · ")


def strip_site_tail(titles: dict[str, str]) -> dict[str, str]:
    """Drop the site-name tail a third or more of the titles share (「… | Shop」 · 「… - Shop」), whatever the dash."""
    tails: dict[str, int] = {}
    for t in titles.values():
        seen = set()
        for sep in SEPS:
            if sep in t:
                tail = t.rsplit(sep, 1)[1].strip().lower()
                if tail and tail not in seen:
                    seen.add(tail)
                    tails[tail] = tails.get(tail, 0) + 1
    need = max(2, len(titles) // 3)
    common = {k for k, n in tails.items() if n >= need and len(k) <= 40}
    out = {}
    for p, t in titles.items():
        for _ in range(2):  # 「… | Shop - Shop Online」: two tails
            before = t
            for sep in SEPS:
                if sep in t and t.rsplit(sep, 1)[1].strip().lower() in common and t.rsplit(sep, 1)[0].strip():
                    t = t.rsplit(sep, 1)[0].strip()
                    break
            if t == before:
                break
        out[p] = t.strip()
    return out


_NOT_PAGE = re.compile(r"^\(not set\)$|^\(other\)$", re.I)


_HOST = re.compile(r"^[a-z0-9.-]+\.[a-z]{2,}(:\d+)?$", re.I)


def _url(host: str, path: str) -> str:
    """A link only for a real public host (not localhost, an IP-less name or (not set))."""
    return f"https://{host}{path}" if host and _HOST.match(host) and not host.startswith("localhost") else ""


def from_ga4(entry_rows: list[tuple[str, int, float | None]], ev_rows: list[tuple[str, str, int]],
             view_rows: list[tuple[Any, ...]], n_pages: int, events: list[str]) -> dict[str, Any] | None:
    """Merge the three GA4 reports (rows already read) into the shape above, paths normalised.

    view_rows: (pagePath, pageTitle, views[, hostName])."""
    titles: dict[str, str] = {}
    views: dict[str, int] = {}
    best: dict[str, int] = {}
    host_v: dict[str, dict[str, int]] = {}
    for row in view_rows:
        path, title, v = row[0], row[1], row[2]
        host = str(row[3]).strip().lower() if len(row) > 3 else ""
        if _NOT_PAGE.match(path or ""):
            continue
        k = path_key(path)
        views[k] = views.get(k, 0) + v
        if host and not _NOT_PAGE.match(host):
            host_v.setdefault(k, {})[host] = host_v.setdefault(k, {}).get(host, 0) + v
        if title and not _NOT_PAGE.match(title) and v > best.get(k, -1):
            titles[k], best[k] = title, v
    titles = strip_site_tail(titles)
    totals_h: dict[str, int] = {}
    for hv in host_v.values():
        for h, v in hv.items():
            totals_h[h] = totals_h.get(h, 0) + v
    site = max(totals_h, key=lambda h: totals_h[h]) if totals_h else ""

    def url(k: str) -> str:
        hv = host_v.get(k)
        return _url(max(hv, key=lambda h: hv[h]) if hv else site, k)
    entry: dict[str, dict[str, Any]] = {}
    for path, users, eng in entry_rows:
        if not path or _NOT_PAGE.match(path):
            continue
        k = path_key(path)
        e = entry.setdefault(k, {"path": k, "title": titles.get(k, ""), "users": 0, "eng": eng, "ev": {}, "url": url(k)})
        e["users"] += users
    for path, name, users in ev_rows:
        k = path_key(path)
        if k in entry and name in events:
            entry[k]["ev"][name] = entry[k]["ev"].get(name, 0) + users
    if not entry and not views:
        return None
    return {
        "entry": sorted(entry.values(), key=lambda e: -e["users"]),
        "views": [{"path": k, "title": titles.get(k, ""), "views": v, "url": url(k)}
                  for k, v in sorted(views.items(), key=lambda kv: -kv[1])],
        "n_pages": max(n_pages, len(views)),
    }


# ---------------------------------------------------------------- samples (見本 / demo boards)

# (path, {ja, en, ko}, share of visits that start here, how much further its visitors get, views per entry, engagement %)
_EC = [
    ("/", {"ja": "トップ", "en": "Home", "ko": "홈"}, 0.32, 1.13, 2.2, 49),
    ("/feature/winter-coat", {"ja": "冬のコート特集", "en": "Winter coat feature", "ko": "겨울 코트 특집"}, 0.20, 0.48, 1.96, 38),
    ("/item/wool-navy", {"ja": "ウールコート ネイビー", "en": "Wool coat, navy", "ko": "울 코트 네이비"}, 0.14, 1.70, 3.27, 61),
    ("/sale", {"ja": "セール一覧", "en": "Sale", "ko": "세일 목록"}, 0.11, 1.35, 2.65, 58),
    ("/blog/coat-guide", {"ja": "ブログ: コートの選び方", "en": "Blog: choosing a coat", "ko": "블로그: 코트 고르는 법"}, 0.09, 0.26, 1.47, 44),
    ("/about", {"ja": "ブランドについて", "en": "About the brand", "ko": "브랜드 소개"}, 0.03, 1.91, 1.57, 66),
    ("/cart", {"ja": "カート", "en": "Cart", "ko": "장바구니"}, 0.006, 2.4, 42.9, 72),
    ("/checkout", {"ja": "ご購入手続き", "en": "Checkout", "ko": "구매 절차"}, 0.002, 4.0, 57.5, 81),
]
_EC_MORE = [("/item/down-black", {"ja": "ダウンジャケット ブラック", "en": "Down jacket, black", "ko": "다운 재킷 블랙"}),
            ("/item/cashmere-muffler", {"ja": "カシミヤマフラー", "en": "Cashmere scarf", "ko": "캐시미어 머플러"}),
            ("/item/leather-boots", {"ja": "レザーブーツ", "en": "Leather boots", "ko": "가죽 부츠"}),
            ("/faq", {"ja": "よくある質問", "en": "FAQ", "ko": "자주 묻는 질문"}),
            ("/news", {"ja": "お知らせ", "en": "News", "ko": "공지사항"})]
_GENERIC = [
    ("/", {"ja": "ホーム", "en": "Home", "ko": "홈"}, 0.34, 1.12, 2.1, 52),
    ("/campaign", {"ja": "キャンペーン特集", "en": "Campaign page", "ko": "캠페인 페이지"}, 0.19, 0.50, 1.5, 37),
    ("/service", {"ja": "サービス紹介", "en": "Services", "ko": "서비스 소개"}, 0.13, 1.60, 2.9, 60),
    ("/pricing", {"ja": "料金", "en": "Pricing", "ko": "요금"}, 0.10, 1.40, 2.4, 63),
    ("/blog/guide", {"ja": "ブログ記事", "en": "Blog post", "ko": "블로그 글"}, 0.10, 0.30, 1.3, 45),
    ("/about", {"ja": "会社概要", "en": "About us", "ko": "회사 소개"}, 0.03, 1.80, 1.6, 64),
    ("/contact", {"ja": "お問い合わせ", "en": "Contact", "ko": "문의"}, 0.008, 3.0, 20.0, 70),
]
_GENERIC_MORE = [("/cases", {"ja": "事例・実績", "en": "Case studies", "ko": "사례"}),
                 ("/faq", {"ja": "よくある質問", "en": "FAQ", "ko": "자주 묻는 질문"}),
                 ("/news", {"ja": "お知らせ", "en": "News", "ko": "공지사항"}),
                 ("/recruit", {"ja": "採用情報", "en": "Careers", "ko": "채용 정보"}),
                 ("/access", {"ja": "アクセス", "en": "Access", "ko": "오시는 길"})]
# the ad landing page of each sample loses people right at the last step (the story the sample tells)
_LATE = {"/feature/winter-coat": 0.5, "/campaign": 0.5}
_SHOPS = {"ec", "d2c", "marketplace", "apparel", "food_ec", "furniture_ec", "type-commerce"}


def sample_pages(slug: str, entry: int, totals: dict[str, int], events: list[str]) -> dict[str, Any] | None:
    """Deterministic pages whose numbers add up to the sample flow (every event total is split over the pages)."""
    if not entry or not events:
        return None
    tag = f"sp|{slug}|"
    base, more = (_EC, _EC_MORE) if slug in _SHOPS else (_GENERIC, _GENERIC_MORE)
    left = max(0.0, 1.0 - sum(r[2] for r in base))
    rows = [(p, t, s, m, vx, eng) for p, t, s, m, vx, eng in base]
    for n, (p, t) in enumerate(more):  # the rest of the visits, a little less each
        share = left * (0.30 - 0.05 * n)
        rows.append((p, t, share, _jitter(f"{tag}m{n}", 0.6, 1.3), 2.0, round(45 + 3 * n)))
    pages = [{"path": p, "title": t, "users": round(entry * s), "eng": float(eng), "ev": {}, "_m": m, "_vx": vx}
             for p, t, s, m, vx, eng in rows]
    for i, ev in enumerate(events, start=1):
        depth = i / len(events)
        raw = [pg["users"] * (pg["_m"] ** depth) * (_LATE.get(pg["path"], 1.0) if i == len(events) else 1.0) for pg in pages]
        scale = totals.get(ev, 0) / sum(raw) if sum(raw) else 0.0
        prev_ev = events[i - 2] if i > 1 else None
        for pg, r in zip(pages, raw):
            cap = pg["ev"][prev_ev] if prev_ev else pg["users"]
            pg["ev"][ev] = min(round(r * scale), cap)
    views = []
    for pg in pages:
        views.append({"path": pg["path"], "title": pg["title"], "views": round(pg["users"] * pg.pop("_vx") * _jitter(tag + pg["path"], 0.97, 1.03))})
        pg.pop("_m")
    return {"entry": sorted(pages, key=lambda e: -e["users"]), "views": sorted(views, key=lambda v: -v["views"]),
            "n_pages": 214 if slug in _SHOPS else 86}
