# 業界目安 출처의 이용 조건 정리

2026-11-22 조사 · 대상: `sitekpi/packs/sources.py`의 출처 4곳 · **법률 자문이 아님** — 사실 정리와 권장 조치만 적는다. 최종 판단은 운영자(필요하면 변호사).

---

## 요약

| 출처 | SiteKPI가 쓰는 것 | 이용 조건에서 확인한 것 | 위험도 | 권장 |
|---|---|---|---|---|
| **Databox** — GA4 Industry Benchmarks (2023-08 중앙값) | 업종별 참여율·이탈률 15개 값 → 30 팩의 目安 중심값 | 이용약관(2023-04-26 개정)의 지적재산 조항: 사이트·서비스의 내용에 대해 **복사·재배포·이용·게시를 금지**한다고 적혀 있고, 데이터 인용을 허락하는 문구는 찾지 못함. 서비스 이용 허락은 "내부 업무 목적"으로 한정 | **높음** | 서면 허락 요청(아래 메일 초안). 답이 없거나 거절이면 대체 출처로 교체 |
| **Baymard Institute** — cart abandonment 70.22% (50개 연구 평균, 2025-09-22 갱신) | 장바구니→구매 目安 (100 − 70.22) | 페이지가 "50개 대신 숫자 하나를 쉽게 인용할 수 있도록 평균을 냈다"고 밝힘 → 인용을 전제로 공개된 수치 | 낮음 | 지금처럼 출처 이름 + 링크 유지 |
| **First Page Sage** — B2B Conversion Rates by Industry | 리드형 업종 13개의 주CVR 중심값 | 이번 조사에서 이용약관·인용 정책을 확인하지 못함 | 중간 (미확인) | 사이트 약관 확인 후, 필요하면 Databox와 같은 메일 |
| **Dynamic Yield 2024 (Smart Insights 기사 경유)** — 이커머스 CVR | EC 6팩의 주CVR | 재인용(2차 출처). 원 출처(Dynamic Yield Benchmarks)와 Smart Insights 양쪽 약관 미확인 | 중간 (미확인) | 원 출처 페이지로 링크를 바꾸고 약관 확인 |

## 무엇이 문제인가

- **숫자 자체**(예: "SaaS 참여율 중앙값 52.43%")는 일반적으로 사실에 가깝지만, **약관은 계약**이다. Databox 사이트를 이용하며 약관에 동의한 상태에서 그 내용을 상업 서비스에 넣으면, 저작권과 별개로 약관 위반 문제가 될 수 있다.
- SiteKPI는 Databox 값을 **15개 업종 × 2지표**로 체계적으로 가져와 판정의 근거로 쓰고 있다 — 한두 개 인용보다 범위가 크다.
- Databox 약관에는 "비슷한 아이디어·기능의 제품을 만들기 위해 서비스에 접근"하는 것을 금지하는 조항도 있다. SiteKPI는 Databox를 이용해 만든 것이 아니므로 직접 해당한다고 보기는 어렵지만, 같은 분야(대시보드)라 상대가 민감할 수 있다.

## 권장 순서

1. **Databox에 허락 요청** (아래 초안, 발신: 운영자). 회신까지 공개 확대(광고 연장·OAuth 심사 후 홍보)를 미루는 것도 선택지.
2. 허락을 못 받으면: 다른 공개 출처로 교체 후보를 찾는다 — 예: 공개 보고서에 **인용 조건(CC BY 등)이 명시된** 벤치마크, 또는 SiteKPI 사용자 집계로 만드는 目安(기획서 「사용자 집계로 만드는 目安」, 지금 보류).
   교체 시 `packs/sources.py`의 `_DATABOX`·`_DATABOX_SEGMENT`만 바꾸면 되고, 보드는 출처 표시(이름·링크·**확인일**)가 따라 바뀐다.
3. First Page Sage · Dynamic Yield 약관 확인 → 이 표의 "미확인"을 채운다.
4. 결과를 기획서 「정할 것·확인할 것」의 해당 줄에 반영.

## Databox 허락 요청 메일 (초안, 영어)

> **Subject:** Permission to cite your GA4 Industry Benchmarks in a free analytics dashboard
>
> Hello Databox team,
>
> I run SiteKPI (https://sitekpi.net), a small web dashboard that helps site owners in Japan read their own Google Analytics 4 numbers. Next to a site's engagement rate and bounce rate, we would like to show the industry medians from your "GA4 Industry Benchmarks" report (August 2023) as a reference, with "Source: Databox" and a link to your page on every figure.
>
> We use 15 industry medians (engagement rate and bounce rate). We do not copy your text, charts or any other content, and we do not resell the data.
>
> Could you let us know whether this use is acceptable, and whether you would like a particular attribution wording? If you'd prefer we didn't, we will remove the figures.
>
> Thank you,
> (운영자 이름) — SiteKPI

## 근거 (2026-11-22 확인)

- Databox Terms of Service — https://www.databox.com/terms-of-service (Last revised April 26th, 2023)
- Baymard Institute, Cart Abandonment Rate — https://baymard.com/lists/cart-abandonment-rate
- (미확인) First Page Sage, Dynamic Yield / Smart Insights 약관
