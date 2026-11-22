# SiteKPI 자체 GA4 설정 체크리스트 (퍼널 보고서까지)

2026-11-22 작성 · 대상: SiteKPI **자신의** GA4 속성 (측정 ID `G-1MKNTCMQ13`, 속성 562484368). 고객의 GA4가 아니다.
이벤트 설계의 원본은 기획서 `#analytics`. 이 문서는 GA4 관리 화면에서 할 일을 순서대로 적은 것이다.

---

## 1. 속성 설정 (관리)

- [ ] 데이터 설정 → 데이터 보관: **14개월**.
- [ ] 데이터 설정 → 데이터 수집: **Google 신호 끔**, 광고 맞춤설정 끔.
- [ ] 데이터 스트림 → 웹 → 향상된 측정: 페이지 조회 · 스크롤 · 이탈 클릭만 켬 / 양식 상호작용 · 사이트 검색 · 동영상 · 파일 다운로드 끔(기획서 결정).
- [ ] 데이터 스트림 → 태그 설정 → 내부 트래픽 정의: 운영자 IP. 데이터 필터 「Internal Traffic」을 **활성**으로.
- [ ] 데이터 스트림 → 태그 설정 → 원치 않는 추천 목록: `accounts.google.com` (OAuth에서 돌아올 때 유입이 Google로 잡히지 않게).

## 2. 맞춤 정의 (관리 → 맞춤 정의 → 맞춤 측정기준 만들기)

범위 = **이벤트**, 이벤트 매개변수 이름 = 측정기준 이름과 같게.

| 측정기준 | 값 예 | 쓰는 이벤트 |
|---|---|---|
| `screen` | home · connect · board · glossary · samples · builder · settings · sites | 모든 맞춤 이벤트 |
| `cta` | connect · samples · sample_card · sites_open · sites_pro | cta_click · sample_to_board |
| `location` | header · hero · final · tile · watch … | cta_click · oauth_start · explain_open |
| `mode` | live · sample | board_view · flow_edit_start · **story_reach** |
| `period` | 28d · 7d | board_view · period_change |
| `step` | q0 · qch · qb · q2 · q3 · q4 · q5 · qsum · details | **story_reach** (2026-11-22 추가) |
| `metric` · `industry` · `behavior` · `purpose` · `details` · `faq_id` · `reason` · `vote` · `change` · `category` · `template` · `first_in_session` | 기획서 표대로 | 각 이벤트 |

사용자 범위: `ui_language`, `connection`.

> 맞춤 측정기준은 **만든 뒤부터** 데이터가 쌓인다(과거 소급 안 됨). 광고를 켜기 전에 만든다.

## 3. 주요 이벤트 (관리 → 이벤트 → 주요 이벤트로 표시)

- [ ] `cta_click` (광고 전환의 1차 신호, PRODUCT.md P0-1)
- [ ] `login` (GA4 연결 완료)
- [ ] `first_board_view` (활성화)
- [ ] `sample_to_board`, `contact_click`, `feedback_submit` (기획서 ★)
- 선택: `oauth_start`

Google Ads 연결 후: 전환 → GA4에서 가져오기 → `cta_click` (가능하면 `cta = connect` 조건).

## 4. 탐색 보고서 (탐색 → 유입경로 탐색 분석)

각 보고서를 "열린 유입경로"가 아닌 **닫힌 유입경로**로, 기간 28일, 분석 기준은 사용자.

| 이름 | 단계 (이벤트 + 조건) | 분할 |
|---|---|---|
| ① 획득 | `page_view` (페이지 경로 = `/`) → `cta_click` (cta = connect) → `oauth_start` → `login` → `property_select` → `board_view` (mode = live, first_in_session = true) | 세션 캠페인 (광고 `ga4_intent_14d` 비교) |
| ② 見本 | `cta_click` (cta = samples) → `sample_view` → `board_view` (mode = sample) → `oauth_start` | 기기 |
| ③ 보드 읽기 | `board_view` → `story_reach` (step = q2) → `story_reach` (step = q3) → `story_reach` (step = q4) → `story_reach` (step = qsum) | mode (live · sample) |
| ④ 활성 | `board_view` (live) → `explain_open` / `flow_edit_start` / `industry_change` / `guess_confirm` | — |

추가로 **코호트 탐색 분석**: 포함 조건 `login`(첫 접촉), 재방문 조건 `board_view`(mode = live), 주 단위 → 재방문(기획서 「재방문」).

③은 이번에 넣은 `story_reach`로 처음 볼 수 있다. 「스토리 장을 더 늘릴지」 판단에 쓴다: q4(どうする？)까지 가는 비율이 낮으면 장을 늘리기보다 앞쪽을 줄인다.

## 5. 확인

- [ ] 시크릿 창에서 `https://sitekpi.net/?utm_source=google&utm_medium=cpc&utm_campaign=ga4_intent_14d` → 히어로 「GA4 を接続」 클릭 → 실시간/DebugView에 `cta_click` (cta = connect).
- [ ] 見本 보드(`/ec`)를 끝까지 스크롤 → DebugView에 `story_reach`가 step별로 한 번씩.
- [ ] 보드 「印刷・PDF」 → `board_print`.
- [ ] HQ 「SiteKPI 이용자」 팝업 API(`/hq/api/users`)에 `story`·`feedback`이 나오는지 (HQ 화면에 표시하려면 HQ 쪽 수정 필요).
