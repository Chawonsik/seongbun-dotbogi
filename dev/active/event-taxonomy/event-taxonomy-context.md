# Event taxonomy: context

Last Updated: 2026-10-01 (after phase 2; no open tasks)

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

## Since phase 2 (2026-10-01)
- `variant` and `landing_page` use `review` instead of `benefit`; survey Q1 gained `texture` (PR #13)
- The concept page hero photo follows `utm_content` (PR #19). No tracking call changed, `landing_page` stays `common` in round 1
- Production check with `&debug=1`: both ad links sent `round=r1`, `variant=name|review`, Pixel PageView. Repeat right before publishing because the headline changed after the check (PR #22)
- Analysis uses the campaign period only and excludes `is_test`. No charts are prepared in advance
- The ad-side metric is Ads Manager "CTR(링크 클릭률)", documented in `ads/README.md`

## Decided 2026-09-30 (README section 7)
- Keep `{object}_{action}` present-tense names
- Repo events.csv is SSOT; Notion 계측 설계 event tables replaced with links (done)
- Meta InterestClick: rejected
