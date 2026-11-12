# SiteKPI 개발 사양

> **무엇을·왜 만드는가**(목적 · 화면 설계 · 판정 규칙 · 행동/업종 목록 · 로드맵)는 기획서 [docs/plan/index.html](plan/index.html).
> 이 파일은 **어떻게 만드는가**만 적는다: 구조 · 라우트 · 데이터 흐름 · 저장 · 기획 규칙이 코드 어디에 있는지 · 테스트.
> 기획 규칙의 내용(숫자·문구)은 여기에 다시 쓰지 않는다. 바뀌면 기획서와 코드만 고친다.

2026-11-04 갱신

---

## 1. 실행 · 환경

| 항목 | 내용 |
|---|---|
| 스택 | Python 3.12+ · FastAPI · Jinja2(StrictUndefined) · 바닐라 JS · SQLite |
| 실행 | `./run.sh` → http://127.0.0.1:8766 (`PORT=` 로 변경). 개발 중: `python3 -m uvicorn main:app --port 8766 --reload` |
| 환경 변수 | `.env.example` 참고. `GOOGLE_CLIENT_ID` · `GOOGLE_CLIENT_SECRET` · `GOOGLE_REDIRECT_URI` · `APP_BASE_URL` · `SESSION_SECRET` (데모 접속만이면 불필요). 선택: `SESSION_DB_PATH` · `SESSION_ENCRYPTION_KEY` · `APP_DB_PATH` · 로컬 http 전용 `OAUTHLIB_INSECURE_TRANSPORT` |
| GA4 권한 | `analytics.readonly` 하나 (읽기 전용) |
| 배포 | Cloud Run(`starful-258005`, us-central1, 서비스 `sitekpi-service`) · 도메인 `sitekpi.net`. 최초 1회 `scripts/gcp_setup.sh <client_secret.json>`(API·Artifact Registry·Secret Manager·IAM·Firestore TTL), 이후 `./deploy.sh`(Cloud Build: 테스트 → 빌드 → 배포), 도메인 연결 `scripts/gcp_setup.sh --domain`. OAuth 동의 화면·클라이언트는 별도 프로젝트 `sitekpi` |
| 운영 환경 변수 | `STORE_BACKEND=firestore` · `FIRESTORE_COLLECTION=sitekpi` · `APP_BASE_URL` · `GOOGLE_REDIRECT_URI` · `OPERATOR_NAME` · `OPERATOR_ADDRESS` · `LEGAL_COURT`(선택, /policy·/terms 표기. 비면 중립 문구) · `GTM_ID`(Google 태그 관리자 컨테이너, `GTM-` 형식만 출력. 비어 있으면 태그 없음 → 로컬은 측정 안 함) · `DEMO_CONNECT`(운영에서는 비워 둔다. `1`이면 데모 연결을 연다 — 개발·테스트용). 비밀값은 Secret Manager `SITEKPI_SESSION_SECRET` · `SITEKPI_GOOGLE_CLIENT_ID` · `SITEKPI_GOOGLE_CLIENT_SECRET` |
| 테스트 | `pip install -r requirements-dev.txt` 후 `python -m pytest` (2026-11-05 기준 230개). 팩 전수 점검: `python3 scripts/smoke_packs.py` (30 팩 × 3 언어) |

## 2. 디렉터리

```
main.py                      앱 진입점 (sitekpi.app)
sitekpi/
  app.py                     FastAPI 조립 · 미들웨어 · 정적 파일
  session.py                 서버 측 세션 (SQLite, Fernet 암호화)
  selection.py               행동 × 업종 선택 · 첫 추측 · 仮 안내 · 目安 합성
  flow.py                    흐름(단계·이벤트 매핑·別の行動) 저장소와 계산
  benchmarks.py              自社目安 저장소 · 실효 目安 계산
  cache.py                   TTLCache (프로세스 내, GA4 응답 5분)
  board/   data.py           보드용 숫자 조립 (build_dense_board)
           extras.py         詳しい数字의 추가 데이터 (sample_extras / live_extras)
           prev.py           견본의 前期 숫자
  ga4/     oauth.py          Google OAuth (state 검증, 토큰 갱신)
           data.py           GA4 Data/Admin API 호출 (batch, 이벤트 탐색, 흐름, 빌더 값)
  packs/                     업종 팩 30 + 행동 18 (behaviors.py · flows.py · catalog.py · sources.py …)
  metrics/help.py            지표 카탈로그 HELP (指標辞典 · 「説明」 · 빌더 공통)
  i18n/                      UI 문구 strings.py (ja/en/ko) · help/metric/pack 번역
  views/                     화면별 뷰 모델 (HTML 없음) — board.py · setup.py · samples.py …
  routes/                    pages · connect · setup · flow · benchmarks · nav
  templates/                 Jinja 템플릿 (board/ · partials/)
static/css · static/js       화면별 CSS/JS (아래 4장)
docs/plan/                   기획서 + 화면 설계 사본(screens/*.dc.html, support.js)
tests/ · scripts/
```

규칙
- **git에 들어가는 파일·폴더 이름은 모두 영어(ASCII 영문·숫자·`-`·`_`·`.`)로.** 한글·일본어 이름은 쓰지 않는다(파일 내용은 어느 언어든 됨). 예: `docs/plan/index.html`, `screens/03-board.dc.html`.
- **README(`README.md`, `sitekpi/packs/README.md` 등)는 영어로 쓴다.** 화면 용어는 필요하면 괄호로 원문을 붙인다(예: industry benchmarks (業界目安)).
- 뷰 모델(`views/*`)은 dict만 만든다. HTML 문자열을 파이썬에서 만들지 않는다.
- 템플릿은 StrictUndefined: 없는 키는 `.get()`으로. dict 키에 `items` · `pop` 등 dict 메서드 이름을 쓰지 않는다.
- 정적 파일은 `static_url()`(내용 해시 붙음)로 참조.
- 문구는 모두 `i18n/strings.py`의 `t(key, loc)`. 새 키는 파일 끝 `UI.update({...})` 블록에 ja/en/ko 함께.

## 3. 라우트

### 3.1 페이지

| 메서드 · 경로 | 처리 | 비고 |
|---|---|---|
| GET `/` | 홈(랜딩). 연결돼 있으면 `/live`로, `?home=1`이면 연결돼 있어도 랜딩. `?lang=`은 세션에 저장 | `routes/pages.index` |
| GET `/help` | 使い方・ヘルプ (ja/en/ko, `?lang=` 저장) | `routes/pages.page_help` · `help.html` · `i18n/guide_l10n.py` · `help.css` |
| GET `/connect` | 연결 상태별: 로그인 / 속성 선택 / 연결됨 | `routes/connect.py` |
| GET `/connect/google` · `/connect/callback` | OAuth 시작 · 콜백(state 검증, 세션 재발급) | |
| GET `/connect/demo?start=1` | 데모 연결 → 바로 `/live`. **개발·테스트 전용**: `DEMO_CONNECT=1` 또는 OAuth 미설정일 때만, 그 외는 `/samples`로 302 | `routes/connect.demo_allowed` · 테스트는 `conftest.py`에서 `DEMO_CONNECT=1` |
| POST `/connect/property` · `/property/change` · `/disconnect` · `/selection` · `/pack` | 속성 선택 · 변경 · 해제 · 선택 저장 | |
| GET `/live?period=28d\|7d` | 내 보드. 미선택이면 첫 추측 후 표시 | `routes/pages._live` |
| GET `/live?edit=1` · `?industry=1` | 편집 모드 / 업종 드로어를 열린 채로 | `auto_open` |
| GET `/live/details?period=` | 詳しい数字 조각 (실 GA4일 때 board.js가 나중에 불러옴) | `fragment=True` |
| GET `/{slug}` | 見本 보드 (업종 팩, 예의 숫자). 「例の数字」 · 노란 띠 · 해 보기 편집(저장 안 됨) · 업종 드로어 = 다른 見本 | `routes/setup.sample_setup` · `partials/ex_banner.html` |
| GET `/samples/open?industry=` | 見本의 업종 드로어 → `/{industry}`로 303 (없는 키는 `/samples`) | `routes/setup.samples_open` |
| GET `/samples` · `/samples/preview?b=&i=` | 견본 목록 · 미리보기 조각 | samples.js가 교체 |
| GET `/glossary` | 指標辞典 | |
| GET `/builder` · `/builder/values` | 대시보드 만들기 · GA4 값(JSON) | |
| GET/POST `/settings` | 언어 · 연결 사이트 | |
| GET `/beginner` | 「はじめての5分」 견본 (메뉴에는 없음) | |
| GET `/first` · `/sample` · `/b2c_membership` · `/content_media` | 옛 주소 → 리다이렉트 | |

### 3.2 설정 (모두 보드로 돌아간다)

| 메서드 · 경로 | 처리 |
|---|---|
| GET `/setup` · `/setup/{step}` | → `/live?edit=1` (옛 설정 페이지 없음) |
| GET `/setup/industry` | → `/live?industry=1` |
| POST `/setup` | 흐름 저장 (behavior · key/event/label 배열 · period). 오류는 세션 flash(`board_edit_flash`)로 편집 모드에 표시 |
| POST `/setup/industry` | 업종 저장. 오류는 flash로 업종 드로어에 표시 |
| POST `/setup/keep` | 「このままでよい」: 仮 표시 해제 |
| POST `/flow/mapping` | 단 → 사이트 이벤트 매핑 (JSON 가능, 데모는 403) |
| POST `/flow/branch` | 別の行動 추가·수정·삭제 |
| GET/POST `/benchmarks` · POST `/benchmarks/reset` | 自社目安 조회·저장·초기화 |

## 4. 화면별 구현 위치

| 화면 | 뷰 모델 | 템플릿 | JS / CSS |
|---|---|---|---|
| 03 보드 | `views/board.py` (`_render_sample_dense`, `_verdict`, `_watch_items`, `_details_view`) · `views/flow.py` · `views/setup.py`(편집 모드·업종 드로어 데이터) | `board.html`, `board/{flow,details,info_pops,bench_pops,edit_bar,drawer_step,drawer_industry,_macros}.html` | `board.js`(설명 팝업 위임 · 상세 지연 로드 · 카테고리 열고 닫기 · `SiteDrawer` · 기간 전환 · 目安 조정 열기) · `board_edit.js`(편집 모드 · 업종 미리보기 · 見本은 `data-try-only`로 전송 안 함) · `popover.js`(`SiteKPIPop`) · `board.css` · `helpcard.css` · `setup.css` |
| 02 접속 | `views/connect.py` | `connect.html` | `connect.css` |
| 04 사전 | `views/glossary.py` | `glossary.html`, `partials/help_card.html` | `glossary.css` · `helpcard.css` |
| 05 견본 | `views/samples.py` | `samples.html`, `samples/_preview.html` | `samples.js` · `samples.css` |
| 06 빌더 | `views/builder.py` | `builder.html` | `builder.js` (localStorage `sitekpi.builder.v4`) · `builder.css` |
| 07 설정 | `views/settings.py` | `settings.html` | `settings.css` |
| 01 홈(랜딩) | `views/landing.py` (`landing_context`, 숫자는 카탈로그에서) · 문구 `i18n/landing_l10n.py` (ja/en/ko) | `landing.html` · `public.html`(공개 헤더·푸터) | `landing.css` · 이미지 `static/img/lp/{hero,state,flow,watch,notice,gloss}-{ja,en,ko}.webp`(데모 보드 캡처) |
| 08·09 처리방침·약관 | `routes/legal.py` (`operator()` ← `OPERATOR_NAME`·`OPERATOR_ADDRESS`·`LEGAL_COURT`) | `legal.html` · `legal/{policy,terms}_{ja,en,ko}.html` | `legal.css` |
| 측정(GA4) | `templating.gtm_id` (← `GTM_ID`) · `routes/connect._mark` (쿠키 `sk_ev` 1회 이벤트, `sk_conn` none·demo·live) | `base.html` (GTM 태그 · `track.js`) | `static/js/track.js` (`SiteKPITrack`, `data-track*` 속성, 화면별 위임 리스너) |
| 공통 메뉴 | `routes/nav.py` (`nav_context`, `nav_rail_context`) | `partials/rail*.html` | `rail.js` · `rail.css` |

「説明」 팝업 = `<template id="pop-…">` + `data-pop-open` (popover.js). 지표 「説明」 카드는 指標辞典과 같은 `partials/help_card.html`.
드로어 = `[data-drawer]` + `data-drawer-open/close` (board.js `SiteDrawer`, 한 번에 하나).

## 5. 데이터 흐름

### 5.1 `/live` 한 번의 요청

1. 연결 확인 → 선택(`selection(session)`)이 없으면 `ensure_selection` = 첫 추측(`guess_behavior`) + `AUTO_KEY` 기록.
2. 행동 → 팩(`flow_pack`), 매핑(`board_mapping`: 속성별 매핑 · 수정본 흐름 · 주전환).
3. 병렬: 흐름(`live_flow_context` → `ga4.data.fetch_flow`) ∥ 보드 숫자(`_live_pack` → `fetch_pack_overlay`). 둘 다 `TTLCache` 5분.
4. 前期: 실 GA4는 같은 요청의 직전 기간, 견본은 `board/prev.sample_prev`.
5. 詳しい数字: 실 GA4는 `/live/details` 조각으로 나중에(`live_extras`: 7~8개 리포트 batch), 견본·데모는 같은 요청에서 `sample_extras`(결정적).
6. 편집 모드·업종 드로어: `routes/setup.board_setup(request, flow_users=…, flow_entry=…)` — 편집 모드 인원은 3의 흐름 숫자를 그대로 쓴다.
7. 目安: `compose_benchmarks(행동, 업종)` → `load_effective`(自社目安 덮어쓰기) → `views/board`에서 판정.

GA4 오류 시 `_live_pack`은 DEMO 숫자로 열고 메모에 `live.note.err`.

### 5.2 기획 규칙 → 코드 위치

| 기획서 항목 | 코드 |
|---|---|
| 첫 추측 (행동 · 업종 · 데모) | `selection.guess_behavior` (`_PRIMARY_RANK`, `FALLBACK_BEHAVIOR`) · `default_industry` · `ensure_selection` |
| 仮 안내 문구 | `selection.auto_notice` → `board.html` `.notice` |
| 행동 18개 · 단계 · 주전환 | `selection.BEHAVIORS` (← `packs/behaviors.py`) · `packs/flows.py` `FLOW_STEPS` |
| 업계·업종 30개 | `packs/*.py` · `packs/catalog.py` · `packs/registry.py` |
| 業界目安 · 출처 등급 · 범위 폭 | `packs/sources.py` (`ENGAGE_RULE` · `CVR_RULE` · `CART_RULE`) · `packs/derived.py` · `benchmarks.effective_benchmarks` |
| 판정 (良好·目安内·要注意, v5는 색 글자 `.jt-*`) | `views/board._bench_info` · `_judge` · `board/_macros.html` `judge_text` |
| 스토리 ①〜④ | `views/story.py` (`pick_issue` 규칙 · `build_story` · `_prompt`) ← `views/board._story` · 문구·대책 카탈로그 `i18n/story_l10n.py` (`STORY` · `ACTIONS` · `kind_of_event`) · 비율의 흐름 구간은 `board/data.py` 행의 `seg` · `board.html` `.story-strip` `#q1`〜`#q4` · `static/js/story.js` (프롬프트 조립·복사, 단 이름 높이 맞춤) · GA4 `ai_prompt_copy` |
| 보드 폭 · 흐름 배치 | `.content` 최대 1360px 가운데 · 흐름은 컨테이너 쿼리 `@container flow`: 521px 이상 가로(최소 폭, 넘치면 스크롤), 520px 이하 세로 · 편집 중 `.where.is-editing` 파란 테두리 |
| v5 보드 모양 | 카드 3장 `.card` · 숫자 3열 `.stats/.stat` · 今見るべきこと `.wtable/.wrow` · 詳しい数字 위 3개 열림(`_details_view`의 `collapsed`) · `?` 동그라미 `.help-q` · 파란 글자 버튼 `.link-btn` · 課題 강조 `_verdict` → `short_html` (`.v-issue`) |
| メモ・ご意見 패널 | `partials/memo.html` (base.html, 레일의 `rail.active` ∈ live · samples · glossary · builder) · `static/js/memo.js` · `static/css/memo.css` · localStorage `sk_memo_open` · `sk_memo_sent`(최근 10개) |
| 글자 6단계 | `board.css` · `rail.css` · `helpcard.css` · `setup.css`의 font-size는 0.75 · 0.8125 · 0.9375 · 1.125 · 1.375 · 1.625rem만 |
| 이탈 인원 · 단 빼기 | `views/flow.flow_context` 링크의 `lost` · 단의 `in_link` → `flow.html` `.flow-lost` · `board_edit.js` 「× 外す」/「元に戻す」 |
| 今 · 業界(범위) · あと(범위) | `views/board._range_gap` → `_bench_view`의 `rg` · `board/_macros.html` `rg_box` · `rg_gap` (타일 · 今見るべきこと · 詳しい数字) |
| GA4 이벤트 설계 | 기획서 `#analytics` → `static/js/track.js` · 사용자 GA4 데이터는 보내지 않음 |
| 今見るべきこと · 一番の課題 · 업종 안내(`far`) | `views/board._watch_items` · `_verdict` · `board.html` `.watch-ind` |
| 흐름 계산 (인원 · %) | `views/flow.flow_context` · `flow.sample_flow` |
| 지표 목록 | `metrics/help.py` `HELP` (+ `i18n/help_l10n.py`) |

## 6. 저장

| 무엇 | 어디 | 키 |
|---|---|---|
| 세션 (로그인 토큰 포함) | `.data/sessions.sqlite3` — 서버 측, Fernet 암호화, 행 키 = sha256(세션 id). 쿠키에는 무작위 id만 | — |
| 선택 · 仮 · flash | 세션 | `flow_behavior` · `industry` · `auto_selection` · `board_edit_flash` · `ga4_property` · `ga4_demo` |
| 단 매핑 · 수정본 흐름 · 別の行動 | `.data/app.sqlite3` (`APP_DB_PATH`) 테이블 `event_mappings` · `flow_custom` · `flow_branches` | scope = `prop:{property_id}` (같은 속성은 브라우저가 달라도 공유). 데모는 저장 안 함 |
| 自社目安 | 같은 DB 테이블 `benchmark_overrides` | 실 GA4: `prop:{id}` / 견본·데모: `sess:{bench_owner}` (저장할 때만 생성) |
| 운영(Cloud Run) | 위 세 가지(세션 · 흐름 · 自社目安)는 Firestore `sitekpi/{sessions,flow,benchmarks}/rows/…` (`sitekpi/firestore_store.py`, `STORE_BACKEND=firestore`). 세션은 같은 Fernet 암호화, `expire_at` TTL로 자동 삭제 | — |
| メモ・ご意見 | 같은 `/feedback`, `screen`(rail.active) · `section`(보고 있던 카드 이름, 60자) · `path` · 선택 `vote` | — |
| 의견(메모 · 랜딩 「ご意見」) | 로컬 `.data/feedback.jsonl`, 운영 Firestore `sitekpi/feedback/rows` — 화면·위치(section)·👍/👎·의견·언어·연결 여부·시각 (IP·계정 없음) | — |
| 측정 쿠키 | `sk_ev`(5분, 1회 이벤트 이름) · `sk_conn`(14일, none·demo·live). JS가 읽음(HttpOnly 아님), ID·GA4 값 없음 | — |
| 빌더 | 브라우저 localStorage `sitekpi.builder.v4` (v3 자동 이전) | — |

## 7. 기획서 화면 사본

- 화면 설계의 원본은 Claude의 디자인 캔버스 「SiteKPI 新デザイン」. `docs/plan/screens/*.dc.html`은 그 사본(번호 붙은 파일명).
- `screens/support.js`가 캔버스 형식(`<x-dc>` 템플릿 · `{{식}}` · `<sc-for>` · `<sc-if>` · `onClick`)을 그린다. 캔버스 런타임 전체가 아니라 이 파일들에 필요한 만큼만.
- 「반영해줘」 때: 코드 → 테스트 → 캔버스 파일을 `screens/`로 복사(링크의 파일명 치환) → 기획서 결정 ✓ 추가 → 변경 이력.

## 8. 테스트

| 파일 | 다루는 것 |
|---|---|
| `test_entry.py` | 데모 한 번에 보드 · 仮 안내 · 상단 바 · 기간 전환 · 편집 모드 숫자 일치 |
| `test_flow.py` | 흐름 · 매핑 · 수정본 · 別の行動 · 記録なし 안내 |
| `test_board_readability.py` · `test_pages_v2.py` | 보드 구성 · 詳しい数字 숫자 · live_extras(가짜 GA4) |
| `test_benchmarks.py` | 目安 · 自社目安 저장/초기화 |
| `test_events_live.py` · `test_ga4_batch.py` | GA4 응답 처리 (가짜 클라이언트) |
| `test_oauth_state.py` · `test_session.py` · `test_multiuser.py` | OAuth state · 세션 암호화 · 사용자 분리 |
| `test_nav.py` · `test_templates.py` · `test_prev.py` | 메뉴 · 템플릿 전수 렌더 · 前期 |

실제 GA4 계정으로는 자동 테스트하지 않는다(가짜 클라이언트). 실데이터 확인은 기획서 「정할 것·확인할 것」.

## 9. 알려진 문제

- 全業種 판별이 출처 문구 "All industries" 문자열에 의존 (`packs/sources.py`).
- 견본 팩 일부의 `FLOW_STEPS`에 팩 고유 이벤트 이름이 남아 있다 (견본만 영향).
- `/live/details`는 매 요청 GA4 batch(캐시 5분). 기간을 자주 바꾸면 호출이 는다.
