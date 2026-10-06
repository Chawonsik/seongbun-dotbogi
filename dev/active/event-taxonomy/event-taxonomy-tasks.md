# Event taxonomy: tasks

## Phase 1
- [x] Read reference posts and sample CSV
- [x] Extract current events and values from landing/concept.html
- [x] Write events.csv and README.md
- [x] User review, answer open decisions (keep names, repo SSOT, no InterestClick)
- [x] Merge docs PR (#11)

## Phase 2
- [x] check_taxonomy.py + tests (17)
- [x] GitHub Actions workflow
- [x] Repo CLAUDE.md rule and PR template
- [x] Apply rename if decided (not needed: names kept)
- [x] Amplitude tracking plan synced via MCP (7 events, 12 properties, enums on closed sets)

## Phase 3 (section views, 2026-10-06)
- [x] events.csv row first, check fails (RED), then concept.html observer, check and 26 tests pass
- [x] README 4.2, 4.3, change log; privacy sections 1 and 11; landing/README.md
- [x] Local browser check with `?debug=1` at 375x812 and 360x640
- [ ] Code review, PR, merge
- [ ] Production check with `&debug=1`, record the deploy time in dev/active/ingredient-map context
- [ ] Sync the Amplitude tracking plan (`section_view`, `section` enum)
