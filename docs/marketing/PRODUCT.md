# SiteKPI product backlog (marketing window)

Product work that makes [PLAN.md](PLAN.md) measurable and less leaky.  
**Channels / budget / Day-15 ads verdict → PLAN.md.**  
**App changes / status → this file.**

Ads stay **OFF** until P0 checklist below is done.

No new landing URL. Production “demo” = **見本** `/samples` (not `/connect/demo`). Ads land on `/` with PLAN UTM.

```text
Ads → /?utm_… → cta_click(connect|samples) → /connect or /samples → oauth_start / sample_view
```

---

## Status

| ID | Item | Priority | Status | Date |
|----|------|----------|--------|------|
| P0-1 | GA4 key events + UTM + Ads conversion checklist | P0 | done (checklist; console steps for operator) | 2026-11-17 |
| P0-2 | Landing hero copy ↔ ad promise (ja + parallel en/ko) | P0 | done | 2026-11-17 |
| P0-3 | Connect lead ↔ board promise (判定 · 前期 · 業界目安) | P0 | done | 2026-11-17 |
| P1-1 | Weekend funnel: fix only weakest step if leak | P1 | todo (during ads) | — |
| P1-2 | Mobile sticky CTA only if SP bounce after ads is clear | P1 | todo (if needed) | — |
| P2-1 | Post Day-15: deeper landing/connect pass if relevant clicks, ~0 connect | P2 | todo | — |
| P2-2 | Junk intent → no product thrash; stop ads per PLAN | P2 | todo | — |

---

## P0-1 — Measurement checklist (operator)

Code already sends events via `static/js/track.js` + `gtag` when `GA4_ID` is set (Cloud Run). Confirm in **SiteKPI’s own GA4** (not the customer’s):

### Before ads ON

- [ ] Open `/` with  
  `?utm_source=google&utm_medium=cpc&utm_campaign=ga4_intent_14d`  
  and confirm Realtime / Traffic acquisition shows campaign `ga4_intent_14d` (or session source/medium google/cpc).
- [ ] Admin → Events: mark **`cta_click`** as a key event (primary ads signal). Explore with parameter `cta` = `connect` | `samples`.
- [ ] Optional key events for the funnel: `oauth_start`, `login`, `board_view` (see `docs/plan/index.html` #analytics).
- [ ] Google Ads: import GA4 conversion for `cta_click` (prefer `cta=connect` via secondary dimension / audience if Ads UI allows), or fallback URL/`page_view` on `/connect`.
- [ ] Sanity: click hero「GA4 を接続」once in an incognito window; see `cta_click` in DebugView / Realtime.

### Weekend read (during 14 days) — feeds P1-1

Pull for the ads campaign only:

1. Sessions on `/` with campaign `ga4_intent_14d`
2. `cta_click` where `cta=connect` vs `cta=samples`
3. `/connect` page views / `oauth_start` / `login`
4. Sample board views from ads sessions

**P1-1 rule:** change **one** thing only — hero CTA label, hero lead, or `connect.lead` — whichever step lost the most people. No redesign.

Log the chosen fix and date in the Log table below.

---

## P0-2 / P0-3 — Copy shipped

| Surface | File | Intent |
|---------|------|--------|
| Landing hero | `sitekpi/i18n/landing_l10n.py` | Ad:「今どうか」一画面 → hero title/lead/meta continuous |
| Connect lead | `sitekpi/i18n/strings.py` (`connect.lead`, `connect.title_x`) | OAuth screen promises 判定 + 前期 + 業界目安, not “random Google login” |

---

## Out of scope (same as PLAN)

- New ad landing route  
- Production `/connect/demo` as public demo  
- Display / YouTube ads  
- Reddit product links  

---

## Log

| Date | Note |
|------|------|
| 2026-11-17 | PRODUCT.md created; P0-2/P0-3 copy; P0-1 checklist for operator before ads ON |
