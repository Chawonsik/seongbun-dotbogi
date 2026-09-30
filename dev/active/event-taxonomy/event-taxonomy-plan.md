# Event taxonomy: plan

Goal: one source of truth for events and properties that stays in sync with the landing code as features are added.

## Phase 1: document (this PR)
1. `docs/taxonomy/events.csv`: sample CSV columns plus Required, Analysis, Status, Since. One row per event x property. `*` rows are common properties.
2. `docs/taxonomy/README.md`: purpose, event path, naming rules, design decisions, analysis rules, change process, open decisions, change log.
3. User reviews; open decisions in README section 7 get answered.

## Phase 2: development (after phase 1 is approved)
1. `scripts/check_taxonomy.py`: parse `track()`/`trackOnce()` calls and their extra keys in `landing/*.html`, compare with active SDK rows in events.csv. Exit non-zero on mismatch.
2. GitHub Actions workflow running the check on every PR.
3. Repo `CLAUDE.md` rule and PR template checkbox: tracking changes must edit events.csv in the same PR.
4. Optional: import events.csv into Amplitude Data tracking plan.
5. Apply any rename decided in phase 1 (before the first campaign).

## Not in scope
- Notion 계측 설계 page edits (user said not to touch; propose only)
- Changing UTM rules or survey wording
