# Concept landing skeleton: plan

Goal: a function-only page at `/concept` so the 2026-09-30 Amplitude session can wire and verify the 7 events.
Design is out of scope. The partner (or a later pass) restyles it while keeping `data-track` hooks.

Spec source: Notion "계측 설계 초안: 로그, UTM, 설문" (synced to docs/tracking-plan-draft.md).

## Scope
1. `landing/concept.html`: hero (no product name, round 1 common page), pre-launch notice, intro and price placeholders,
   interest button, survey card (Q1 paid only, Q2, Q3, 1/3 progress, one per device), appendix link shown after the survey,
   footer with privacy link.
2. Tracking adapter: common props (utm x4, round, variant, landing_page), queue until Amplitude loads,
   Amplitude loader that activates only when `SD_CONFIG.amplitude` is set, `?debug=1` on-page event log.
3. Meta pixel PageView only. No GA4.
4. `noindex` until the page is final.

## Not in scope
- Visual design, real copy, images, per-variant round 2 pages
- Privacy policy update (needed before real traffic; tracked separately)
- Deploy (ask the user first)

## Verify
- Local static server, open with `?utm_source=facebook&utm_medium=cpc&utm_campaign=kr_2040_skincare&utm_content=r1_name&debug=1`
- Check each of the 7 events fires once with the right props; Q1 hidden without cpc; survey not shown again after reload
