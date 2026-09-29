# Concept landing skeleton: context

Last Updated: 2026-09-29

## Key files
- `landing/concept.html` (new)
- `landing/index.html` (current tool page, becomes the appendix; untouched)
- `landing/vercel.json` (`cleanUrls: true` so `/concept` serves `concept.html`)
- `docs/tracking-plan-draft.md` (event spec mirror)

## Decisions
- Landing type: pre-launch concept page (fake door) with clear "not for sale" notice. Decided 2026-09-29.
- Round 1: one common page for both ads, no product or ingredient name before the survey.
- Properties: variant (name/benefit), round (r1/r2), landing_page (common/name/benefit).
- Survey: Q1 ad reason (cpc only), Q2 first thing checked, Q3 ingredient-list habit. One card, one question at a time, progress label.
- Survey shows on interest click or after 20 s, once per device (localStorage, best effort).
- Appendix link mentions PDRN, so it appears only after the survey is answered or closed.

## Open
- Amplitude loader URL and init options must be checked against the snippet shown in the Amplitude project tomorrow.
- Pixel custom event for interest click is still a proposal.
