# Event taxonomy: context

Last Updated: 2026-09-30 (phase 2)

## Key files
- `docs/taxonomy/events.csv`, `docs/taxonomy/README.md` (new, SSOT for events and properties)
- `landing/concept.html` (all `track()` calls; COMMON props built around line 170)
- `docs/tracking-plan-draft.md` (mirror of Notion 계측 설계; owns UTM rules, survey wording, metrics)

## Sources
- Martinee blog: naver-series 1-2, burger king honeytip 1-3 (read 2026-09-30)
- `~/Downloads/taxonomy_샘플 (1).csv` (column layout)

## Decisions so far
- Keep A/B as the `variant` property, not separate events (always compared side by side)
- Only two view events: landing_view, survey_view
- No user properties set by our code; segment by survey answers with Amplitude cohorts
- Rows are never deleted once data exists; use Status=deprecated

## Decided 2026-09-30 (README section 7)
- Keep `{object}_{action}` present-tense names
- Repo events.csv is SSOT; Notion 계측 설계 event tables replaced with links (done)
- Meta InterestClick: rejected
