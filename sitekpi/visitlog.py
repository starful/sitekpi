"""SiteKPI's own visitor log + the 30-second survey, read by Starful HQ (docs/plan #visitlog).

- POST /events  — static/js/track.js mirrors every event it sends to GA4 here, plus a page view ("pv").
- POST /survey  — the survey card (static/js/survey.js): four choices + one optional line.
- GET  /hq/api/users?days=7 — Starful HQ's B1 Task Force popup. Bearer = hq_token(): HMAC of SESSION_SECRET
  (HQ reads Secret Manager SITEKPI_SESSION_SECRET and derives the same key), or HQ_API_TOKEN when set.

Who: an anonymous visitor id in the cookie ``sk_vid`` (random, 180 days). Never stored: IP, Google
account, anything read from the user's GA4 (property, numbers, event names). Rows are kept 90 days:
the Firestore field ``expire_at`` (the existing TTL policy on collection group ``rows``) and a purge on write for the local SQLite file.
"""

from __future__ import annotations

import hmac
import os
import re
import secrets
import threading
import time
from collections import defaultdict
from collections.abc import Iterable
from datetime import datetime, timedelta, timezone
from itertools import pairwise
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, Response

ROOT = Path(__file__).resolve().parents[1]
COOKIE = "sk_vid"
COOKIE_AGE = 180 * 24 * 3600
KEEP_DAYS = 90
DAILY_MAX = 600  # events per visitor per day (a stuck page can't flood the log)
JST = timezone(timedelta(hours=9))

_EVENT = re.compile(r"^[a-z][a-z0-9_]{1,39}$")
_VID = re.compile(r"^[a-f0-9]{24}$")
PARAM_KEYS = frozenset({
    "screen", "location", "mode", "purpose", "details", "period", "first_in_session", "metric", "industry",
    "behavior", "category", "cta", "reason", "vote", "has_comment", "language", "change", "from_guess",
    "faq_id", "search_term", "method", "tab", "template", "step",
})

# survey: question → allowed answers (labels for HQ in Korean; the card itself is in i18n/strings.py survey.*)
SURVEY: dict[str, dict[str, str]] = {
    "source": {"search": "검색", "sns": "SNS", "friend": "지인·동료", "blog": "블로그·기사", "other": "기타"},
    "goal": {"judge": "내 사이트 숫자가 좋은지 알고 싶다", "report": "상사·고객 보고에 쓰고 싶다",
             "glossary": "지표 뜻을 찾으러", "setup": "GA4 설정이 어렵다", "browse": "그냥 둘러보러"},
    "role": {"owner": "사이트 운영자", "marketer": "마케팅 담당", "agency": "대행사·컨설턴트",
             "engineer": "개발자", "executive": "경영자"},
    "pain": {"which": "어떤 숫자를 봐야 할지 모른다", "judge": "좋은지 나쁜지 판단이 안 된다",
             "report_time": "보고서 만드는 데 시간이 든다", "setup": "설정이 어렵다", "none": "특별히 없다"},
}
SURVEY_TITLES = {"goal": "오늘 무엇을 하려고 왔나", "source": "어디서 알았나", "role": "입장", "pain": "GA4에서 가장 곤란한 점"}

# HQ funnel: (label, predicate on one event row)
FUNNEL: tuple[tuple[str, Any], ...] = (
    ("랜딩", lambda r: r["e"] == "pv" and r["p"].get("screen") == "home"),
    ("견본 보드", lambda r: r["e"] == "board_view" and r["p"].get("mode") == "sample"),
    ("연결 시작", lambda r: r["e"] == "oauth_start"),
    ("연결 완료", lambda r: r["e"] == "login"),
    ("내 보드", lambda r: r["e"] == "board_view" and r["p"].get("mode") in ("live", "demo")),
    ("AI 프롬프트 복사", lambda r: r["e"] == "ai_prompt_copy"),
)
SCREEN_KO = {"home": "랜딩", "connect": "연결 화면", "glossary": "지표 사전", "samples": "견본 보드 목록",
             "builder": "대시보드 만들기", "settings": "설정", "policy": "개인정보 처리방침", "terms": "이용약관",
             "board": "보드", "help": "도움말", "other": "페이지"}


# --- store --------------------------------------------------------------------------------------------

class SqliteVisitStore:
    """Local / tests: .data/app.sqlite3 (tables visit_events, visit_survey)."""

    def __init__(self, path: Path) -> None:
        from sitekpi.sqlite_util import connect, init_wal

        self.path = path
        self._lock = threading.Lock()
        init_wal(path)
        with connect(path) as db:
            db.execute("CREATE TABLE IF NOT EXISTS visit_events (vid TEXT, at INTEGER, e TEXT, p TEXT, path TEXT,"
                       " ref TEXT, lang TEXT)")
            db.execute("CREATE INDEX IF NOT EXISTS visit_events_at ON visit_events (at)")
            db.execute("CREATE TABLE IF NOT EXISTS visit_survey (vid TEXT PRIMARY KEY, at INTEGER, answers TEXT,"
                       " text TEXT, lang TEXT)")

    def add_events(self, rows: list[dict[str, Any]]) -> None:
        import json

        from sitekpi.sqlite_util import connect

        cutoff = int(time.time()) - KEEP_DAYS * 86400
        with self._lock, connect(self.path) as db:
            db.executemany("INSERT INTO visit_events VALUES (?, ?, ?, ?, ?, ?, ?)",
                           [(r["vid"], r["at"], r["e"], json.dumps(r["p"], ensure_ascii=False), r["path"], r["ref"],
                             r["lang"]) for r in rows])
            db.execute("DELETE FROM visit_events WHERE at < ?", (cutoff,))
            db.execute("DELETE FROM visit_survey WHERE at < ?", (cutoff,))

    def put_survey(self, row: dict[str, Any]) -> None:
        import json

        from sitekpi.sqlite_util import connect

        with self._lock, connect(self.path) as db:
            db.execute("INSERT OR REPLACE INTO visit_survey VALUES (?, ?, ?, ?, ?)",
                       (row["vid"], row["at"], json.dumps(row["answers"]), row["text"], row["lang"]))

    def events_since(self, since: int) -> list[dict[str, Any]]:
        import json

        from sitekpi.sqlite_util import connect

        with connect(self.path) as db:
            cur = db.execute("SELECT vid, at, e, p, path, ref, lang FROM visit_events WHERE at >= ? ORDER BY at", (since,))
            return [{"vid": v, "at": a, "e": e, "p": json.loads(p or "{}"), "path": pa, "ref": rf, "lang": lg}
                    for v, a, e, p, pa, rf, lg in cur.fetchall()]

    def surveys_since(self, since: int) -> list[dict[str, Any]]:
        import json

        from sitekpi.sqlite_util import connect

        with connect(self.path) as db:
            cur = db.execute("SELECT vid, at, answers, text, lang FROM visit_survey WHERE at >= ? ORDER BY at", (since,))
            return [{"vid": v, "at": a, "answers": json.loads(an or "{}"), "text": tx, "lang": lg}
                    for v, a, an, tx, lg in cur.fetchall()]


_store: Any = None
_store_lock = threading.Lock()


def get_store() -> Any:
    global _store
    with _store_lock:
        from sitekpi import firestore_store

        if firestore_store.enabled():  # Cloud Run
            if not isinstance(_store, firestore_store.FirestoreVisitStore):
                _store = firestore_store.FirestoreVisitStore()
        elif not isinstance(_store, SqliteVisitStore):
            _store = SqliteVisitStore(Path(os.getenv("APP_DB_PATH") or (ROOT / ".data" / "app.sqlite3")))
        return _store


# --- input --------------------------------------------------------------------------------------------

def _clean_params(raw: Any) -> dict[str, str]:
    out: dict[str, str] = {}
    if isinstance(raw, dict):
        for k, v in raw.items():
            if k in PARAM_KEYS and isinstance(v, (str, int, float, bool)) and len(out) < 10:
                out[k] = str(v)[:60]
    return out


def _host(ref: Any) -> str:
    """Only the referring site's host name (never its path or query)."""
    m = re.match(r"^https?://([^/:?#]+)", str(ref or ""))
    return m.group(1).lower()[:80] if m else ""


_counts: dict[str, tuple[str, int]] = {}
_counts_lock = threading.Lock()


def _allow(vid: str, n: int) -> bool:
    day = time.strftime("%Y%m%d")
    with _counts_lock:
        d, used = _counts.get(vid, (day, 0))
        if d != day:
            used = 0
        if used + n > DAILY_MAX:
            return False
        if len(_counts) > 50000:
            _counts.clear()
        _counts[vid] = (day, used + n)
        return True


def _vid(request: Request) -> tuple[str, bool]:
    v = request.cookies.get(COOKIE) or ""
    return (v, False) if _VID.match(v) else (secrets.token_hex(12), True)


def _with_cookie(resp: Response, request: Request, vid: str, new: bool) -> Response:
    if new:
        resp.set_cookie(COOKIE, vid, max_age=COOKIE_AGE, httponly=True, samesite="lax",
                        secure=request.url.scheme == "https", path="/")
    return resp


async def vid_middleware(request: Request, call_next: Any) -> Response:
    """Give every HTML page view the anonymous id up front, so /events and /survey (sent at the same
    moment from one page) never mint two different ids for one visitor."""
    resp = await call_next(request)
    if request.method == "GET" and resp.headers.get("content-type", "").startswith("text/html"):
        vid, new = _vid(request)
        _with_cookie(resp, request, vid, new)
    return resp


router = APIRouter(tags=["visitlog"])


@router.post("/events")
async def post_events(request: Request) -> Response:
    try:
        body = await request.json()
    except ValueError:
        return JSONResponse({"ok": False}, status_code=400)
    items = body.get("events") if isinstance(body, dict) else None
    if not isinstance(items, list) or not items or len(items) > 20:
        return JSONResponse({"ok": False}, status_code=400)
    vid, new = _vid(request)
    now = int(time.time())
    lang = str(body.get("lang") or "")[:5]
    rows = []
    for it in items:
        if not isinstance(it, dict) or not _EVENT.match(str(it.get("e") or "")):
            continue
        rows.append({"vid": vid, "at": now, "e": it["e"], "p": _clean_params(it.get("p")),
                     "path": str(body.get("path") or "")[:120].split("?")[0], "ref": _host(it.get("ref")), "lang": lang})
    if rows and _allow(vid, len(rows)):
        get_store().add_events(rows)
    return _with_cookie(JSONResponse({"ok": True}), request, vid, new)


@router.post("/survey")
async def post_survey(request: Request) -> Response:
    try:
        body = await request.json()
    except ValueError:
        return JSONResponse({"ok": False}, status_code=400)
    raw = body.get("answers") if isinstance(body, dict) else None
    answers = {q: str(raw.get(q)) for q in SURVEY if isinstance(raw, dict) and str(raw.get(q)) in SURVEY[q]}
    text = str(body.get("text") or "").strip()[:200]
    if not answers and not text:
        return JSONResponse({"ok": False}, status_code=400)
    vid, new = _vid(request)
    get_store().put_survey({"vid": vid, "at": int(time.time()), "answers": answers, "text": text,
                            "lang": str(body.get("lang") or "")[:5]})
    return _with_cookie(JSONResponse({"ok": True}), request, vid, new)


# --- HQ read API --------------------------------------------------------------------------------------

def hq_token(secret: str | None = None) -> str:
    """The HQ read key: HQ_API_TOKEN if set, else derived from SESSION_SECRET (HQ derives the same from
    Secret Manager SITEKPI_SESSION_SECRET, so no extra secret to create). Empty → the API is off."""
    explicit = (os.getenv("HQ_API_TOKEN") or "").strip()
    if explicit:
        return explicit
    base = (os.getenv("SESSION_SECRET") if secret is None else secret) or ""
    if not base.strip():
        return ""
    return hmac.new(base.strip().encode(), b"sitekpi-hq-api-v1", "sha256").hexdigest()


def _token_ok(request: Request) -> bool | None:
    """None: the API is off (no key). True/False: the bearer token matches."""
    want = hq_token()
    if not want:
        return None
    got = (request.headers.get("authorization") or "").removeprefix("Bearer ").strip()
    return bool(got) and hmac.compare_digest(got, want)


@router.get("/hq/api/users")
def hq_users(request: Request, days: int = 7) -> Response:
    ok = _token_ok(request)
    if ok is None:
        return Response(status_code=404)
    if not ok:
        return JSONResponse({"error": "unauthorized"}, status_code=401)
    days = days if days in (7, 30, 90) else 7
    now = int(time.time())
    store = get_store()
    since = now - days * 86400
    prev_since = since - days * 86400
    events = store.events_since(prev_since)
    surveys = store.surveys_since(now - KEEP_DAYS * 86400)
    return JSONResponse(summarize([r for r in events if r["at"] >= since], surveys, days=days, now=now,
                                  prev_visitors=len({r["vid"] for r in events if r["at"] < since})))


def _short(vid: str) -> str:
    return vid[:4]


def _hm(at: int) -> str:
    return datetime.fromtimestamp(at, JST).strftime("%H:%M")


def _md_hm(at: int) -> str:
    return datetime.fromtimestamp(at, JST).strftime("%m-%d %H:%M")


def _what(r: dict[str, Any]) -> tuple[str, str, str]:
    """(label, where, tone) for one event in the visitor's timeline. tone: key · stop · ''."""
    e, p = r["e"], r["p"]
    if e == "pv":
        return SCREEN_KO.get(p.get("screen", ""), "페이지"), r["path"], ""
    if e == "board_view":
        return ("견본 보드 보기", r["path"], "") if p.get("mode") == "sample" else ("내 보드 보기", r["path"], "key")
    labels = {
        "oauth_start": ("연결 시작", "", ""), "login": ("GA4 연결 완료", "", "key"),
        "oauth_error": ("연결 실패", p.get("reason", ""), "stop"), "ai_prompt_copy": ("AI 프롬프트 복사", p.get("purpose", ""), "key"),
        "flow_edit_start": ("흐름 고치기", p.get("location", ""), ""), "flow_save": ("흐름 저장", "", "key"),
        "sample_view": ("견본 미리보기", p.get("behavior", ""), ""), "sample_to_board": ("견본 → 보드", p.get("cta", ""), ""),
        "explain_open": ("설명 열기", p.get("metric", ""), ""), "cta_click": ("버튼", p.get("cta", ""), ""),
        "feedback_submit": ("메모 보냄", "", "key"), "survey_submit": ("설문 답함", "", "key"),
        "survey_view": ("설문 보임", "", ""), "survey_skip": ("설문 넘김", p.get("reason", ""), "stop"),
        "industry_change": ("업종 바꿈", p.get("industry", ""), ""), "period_change": ("기간 바꿈", p.get("period", ""), ""),
        "glossary_open": ("지표 열기", p.get("metric", ""), ""), "search": ("지표 검색", p.get("search_term", ""), ""),
        "disconnect": ("연결 해제", "", "stop"), "memo_toggle": ("메모 패널", "", ""), "feedback_open": ("의견 열기", "", ""),
        "builder_template": ("템플릿 고름", p.get("template", ""), ""), "builder_metric_add": ("지표 추가", p.get("metric", ""), ""),
        "glossary_filter": ("사전 분류", p.get("category", ""), ""), "benchmark_save": ("자사 목표 저장", p.get("metric", ""), "key"),
        "guess_confirm": ("업종 확인", "", ""), "lang_change": ("언어 바꿈", p.get("language", ""), ""), "demo_start": ("데모 시작", "", ""), "channel_filter": ("유입별 보기", "", ""),
        "contact_click": ("문의", "", ""), "faq_open": ("FAQ 열기", p.get("faq_id", ""), ""),
    }
    return labels.get(e, (e, "", ""))


TIMELINE_SKIP = frozenset({"first_board_view", "signup_complete", "ga4_connect_complete", "property_select"})
MILESTONES = (("견본 보드", lambda r: r["e"] == "board_view" and r["p"].get("mode") == "sample"),
              ("연결 시작", lambda r: r["e"] == "oauth_start"), ("GA4 연결", lambda r: r["e"] == "login"),
              ("내 보드", lambda r: r["e"] == "board_view" and r["p"].get("mode") in ("live", "demo")),
              ("AI 복사", lambda r: r["e"] == "ai_prompt_copy"),
              ("지표 사전", lambda r: r["e"] == "pv" and r["p"].get("screen") == "glossary"))


def _sessions(ats: Iterable[int]) -> int:
    n, last = 0, None
    for a in sorted(ats):
        if last is None or a - last > 30 * 60:
            n += 1
        last = a
    return n


def summarize(events: list[dict[str, Any]], surveys: list[dict[str, Any]], *, days: int, now: int,
              prev_visitors: int = 0) -> dict[str, Any]:
    """Everything the HQ popup shows (labels in Korean, times in JST). Pure: easy to test."""
    by_vid: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in events:
        by_vid[r["vid"]].append(r)
    survey_by = {s["vid"]: s for s in surveys}
    visitors = len(by_vid)
    in_period_survey = [s for s in surveys if s["vid"] in by_vid or s["at"] >= now - days * 86400]

    def has(vid_rows: list[dict[str, Any]], pred: Any) -> bool:
        return any(pred(r) for r in vid_rows)

    board = sum(1 for rows in by_vid.values() if has(rows, lambda r: r["e"] == "board_view"))
    connected = sum(1 for rows in by_vid.values() if has(rows, lambda r: r["e"] == "login"))
    pct = lambda n, d: f"{round(n / d * 100)}%" if d else "—"
    kpis = [
        {"label": "방문자", "value": visitors, "unit": "명", "note": f"이전 {days}일 {prev_visitors}명"},
        {"label": "보드를 본 사람", "value": board, "unit": "명", "note": f"방문자의 {pct(board, visitors)}"},
        {"label": "GA4 연결", "value": connected, "unit": "명", "note": f"방문자의 {pct(connected, visitors)}"},
        {"label": "설문에 답한 사람", "value": len(in_period_survey), "unit": "명",
         "note": f"보드를 본 사람의 {pct(len(in_period_survey), board)}"},
    ]
    funnel = []
    for label, pred in FUNNEL:
        n = sum(1 for rows in by_vid.values() if has(rows, pred))
        funnel.append({"label": label, "n": n, "pct": pct(n, visitors)})
    stuck = ""
    worst = None
    for a, b in pairwise(funnel):
        if a["n"] and (worst is None or a["n"] - b["n"] > worst[2]):
            worst = (a, b, a["n"] - b["n"])
    if worst and worst[2] > 0:
        stuck = f"가장 많이 멈추는 곳: {worst[0]['label']} → {worst[1]['label']} ({worst[0]['n']}명 중 {worst[1]['n']}명)"

    survey = []
    for q in ("goal", "source", "role", "pain"):
        counts: dict[str, int] = defaultdict(int)
        for s in in_period_survey:
            a = s["answers"].get(q)
            if a:
                counts[a] += 1
        rows = sorted(({"label": SURVEY[q][k], "n": n} for k, n in counts.items()), key=lambda x: -x["n"])
        survey.append({"q": SURVEY_TITLES[q], "rows": rows})
    wishes = [{"text": s["text"], "who": _short(s["vid"]) + (" · " + SURVEY["role"][s["answers"]["role"]]
                                                             if s["answers"].get("role") else "")}
              for s in sorted(in_period_survey, key=lambda s: -s["at"]) if s.get("text")][:30]

    people = []
    for vid, rows in sorted(by_vid.items(), key=lambda kv: -kv[1][-1]["at"])[:100]:
        first = rows[0]
        ref = next((r["ref"] for r in rows if r["ref"]), "")
        s = survey_by.get(vid) or {}
        ans = s.get("answers") or {}
        did = [m for m, pred in MILESTONES if has(rows, pred)]
        steps = []
        for r in [r for r in rows if r["e"] not in TIMELINE_SKIP][-60:]:
            what, where, tone = _what(r)
            steps.append({"at": _hm(r["at"]), "what": what, "where": where, "tone": tone})
        people.append({
            "id": _short(vid), "first": _md_hm(first["at"]), "last": _md_hm(rows[-1]["at"]),
            "from": ref or "직접", "why": SURVEY["goal"].get(ans.get("goal", ""), "—"),
            "role": SURVEY["role"].get(ans.get("role", ""), ""), "did": " · ".join(did) or "둘러봄",
            "visits": _sessions(r["at"] for r in rows), "lang": first.get("lang", ""), "steps": steps,
        })
    return {"days": days, "generated_at": _md_hm(now), "kpis": kpis, "funnel": funnel, "stuck": stuck,
            "survey": survey, "answered": len(in_period_survey), "wishes": wishes, "visitors": people,
            "keep_days": KEEP_DAYS}
