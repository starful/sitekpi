# Google OAuth 심사 신청 체크리스트

2026-11-22 작성 · 대상: OAuth 동의 화면·클라이언트 프로젝트 `sitekpi` · 요청 scope: `https://www.googleapis.com/auth/analytics.readonly` 하나

> **왜 지금:** 심사 전에는 동의 화면이 "테스트/미인증" 상태라 사용자 100명 상한이 걸리고, 사용자에게 "확인되지 않은 앱" 경고가 뜬다. 광고(PLAN.md)의 효과도 이 상한이 천장이 된다.
> 콘솔 작업은 운영자가 직접 한다. 이 문서는 순서와 제출할 글을 준비해 둔 것이다.

Google 공식 안내: sensitive scope 심사는 **최대 10일 정도** 걸린다고 되어 있으니 광고 일정보다 먼저 신청한다. scope가 sensitive/restricted 중 어디로 분류되는지는 Cloud Console 동의 화면의 scope 목록에 표시된다(신청 전에 화면에서 확인).

---

## 0. 먼저 정해야 하는 것 (막히는 항목)

- [ ] **운영자명 · 소재지** (`OPERATOR_NAME` · `OPERATOR_ADDRESS`) — 처리방침·약관이 지금 중립 문구. 심사자는 처리방침에서 운영 주체를 본다. 정해지면 `OPERATOR_NAME=… OPERATOR_ADDRESS=… ./deploy.sh`.
- [ ] **주간 메일을 넣을지** (`docs/design/weekly-mail.md` §8-1) — 넣는다면 refresh token 서버 보관이 생기므로, 처리방침과 심사 설명을 **신청 전에** 그에 맞춰 쓴다. 심사 후에 바꾸면 재심사가 될 수 있다.
- [ ] 업계 기준 출처 이용 조건 정리 (`docs/launch/benchmark-sources-terms.md`) — 심사 항목은 아니지만 공개 확대 전에.

## 1. 브랜드 확인 (Brand verification)

- [ ] 홈페이지 `https://sitekpi.net` — 본인이 소유한 **확인된 도메인**이어야 한다. Google Search Console에서 `sitekpi.net` 소유권 확인(DNS TXT) → 같은 Google 계정이 Cloud 프로젝트 `sitekpi`의 소유자/편집자인지 확인.
- [ ] 홈페이지가 앱이 무엇을 하는지 설명하고, 처리방침 링크가 보일 것 (랜딩 푸터 `/policy` ✓).
- [ ] 처리방침 `https://sitekpi.net/policy` — 홈페이지와 **같은 도메인**, 동의 화면에 링크.
- [ ] 이용약관 `https://sitekpi.net/terms`.
- [ ] 동의 화면 정보: 앱 이름 `SiteKPI`, 로고(120×120 PNG, `brand/`에서), 지원 메일, 개발자 연락처 메일, 승인된 도메인 `sitekpi.net`.
- [ ] 앱 이름·로고가 Google 상표와 헷갈리지 않을 것 (이름에 "Google"·"Analytics" 넣지 않기).

## 2. 처리방침에 꼭 있어야 하는 것 (Google API Services User Data Policy · Limited Use)

현재 `/policy`(ja/en/ko)에 「Google 사용자 데이터」 항목이 있다. 아래가 **명시적으로** 들어 있는지 확인:

- [ ] 어떤 Google 데이터를 읽는지: GA4 속성 목록과 보고서 수치(읽기 전용).
- [ ] 어디에 쓰는지: 사용자 본인에게 보드(판정·前期比·業界目安)를 보여 주기 위해서만.
- [ ] 저장: 로그인 토큰은 서버 세션에 암호화 저장, 14일 후 자동 삭제, 연결 해제 시 즉시 삭제·Google에 토큰 폐기 요청. GA4 수치는 5분 메모리 캐시뿐(디스크에 저장 안 함). 흐름 매핑·自社目安은 속성 ID에 묶어 저장.
- [ ] 공유하지 않음: 제3자 제공·광고·판매 없음. SiteKPI 자체 GA4 측정에는 사용자 GA4 데이터를 보내지 않음.
- [ ] **Limited Use 문구** (영문 그대로 넣는 것이 관례):
  > SiteKPI's use and transfer of information received from Google APIs to any other app will adhere to the Google API Services User Data Policy, including the Limited Use requirements.
- [ ] AI 기능: 「AI に聞く」는 **복사만** 하고 SiteKPI가 AI에 보내지 않는다는 점(사용자가 직접 붙여넣음). — Google 데이터를 AI 학습에 쓰지 않는다고 명시.

## 3. scope 설명문 (제출용 초안)

**Scope:** `.../auth/analytics.readonly`

> SiteKPI is a dashboard that tells a site owner, in one screen, how their website is doing compared with the previous period and published industry benchmarks. After the user signs in, SiteKPI lists the GA4 properties they can access (Analytics Admin API, account summaries) and, for the property they choose, runs read-only reports with the Analytics Data API (users, sessions, engagement, the events that make up their conversion flow, channels, devices and landing pages). The numbers are shown only to that user on their own board.
>
> We need analytics.readonly because the app only reads reports; it never creates, edits or deletes anything in Google Analytics. There is no narrower scope that allows reading GA4 reports and listing the user's properties. We do not request edit, manage-users or any other scope.

일본어판(심사 담당자가 일본어를 요청할 경우 대비)은 처리방침 일본어판과 같은 표현으로 맞춘다.

## 4. 데모 영상 (YouTube 일부 공개, 2~3분)

심사자가 보는 것: ① 동의 화면에 앱 이름과 요청 scope가 보이는지 ② 그 데이터가 앱 안에서 어떻게 쓰이는지. 아래 순서로 한 번에 녹화한다(브라우저 주소창이 보이게, 영어 UI `?lang=en` 권장).

1. `https://sitekpi.net` 랜딩 → 「Connect GA4」.
2. Google 계정 선택 → **동의 화면**: 앱 이름 SiteKPI, "See and download your Google Analytics data" 표시가 보이게 몇 초 멈춤. (OAuth 클라이언트 ID가 주소창에 보이게)
3. 속성 선택 화면 → 속성 하나 선택.
4. 보드: 総評 한 문장 → 흐름 → 詳しい数字(8주 추이·기기)를 스크롤하며 "these are read-only GA4 reports" 자막.
5. 「説明」 팝업 하나 열기 → 출처·확인일 표시.
6. 설정 → 「接続・切断」 → **연결 해제** → 토큰 삭제 안내 화면.
7. (선택) 처리방침 `/policy`의 Google 사용자 데이터 항목.

## 5. 신청 후

- [ ] OAuth Verification Center에서 상태 확인, 메일로 오는 추가 질문에 빨리 답하기(답이 늦으면 지연·반려).
- [ ] 통과 전까지는 100명 상한 → 광고 예산을 늘리지 않는다(PLAN.md의 14일 실험 범위).
- [ ] 통과 후: 기획서 로드맵 「공개 · OAuth 심사」 → 완료, 변경 이력에 날짜.

## 6. 앱에서 이미 되어 있는 것 (심사에 유리)

- scope 하나, 읽기 전용 (`ga4/oauth.py` `SCOPES`).
- OAuth state 검증, 콜백 후 세션 재발급, 코드가 URL에 남는 페이지 없음 (`routes/connect.py`, `tests/test_oauth_state.py`).
- 세션 서버 측 저장 + Fernet 암호화, 14일 TTL, 연결 해제 시 Google 토큰 폐기 요청 (`session.py`, `routes/connect._revoke_at_google`).
- 자체 측정에 사용자 GA4 데이터 미전송 (`static/js/track.js` 머리말, `visitlog.py`).
