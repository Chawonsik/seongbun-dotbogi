# Project rules

## Tracking taxonomy
- `docs/taxonomy/events.csv` is the source of truth for every Amplitude event, event property and Meta Pixel event.
- Any change that adds, renames or removes a `track()` / `trackOnce()` call, a key in `COMMON`, an extra property, or an `fbq('track', ...)` call must update `events.csv` in the same PR and add a line to the change log in `docs/taxonomy/README.md`.
- Never delete a row whose event has shipped data. Set Status to `deprecated` and note the date and reason.
- Before adding an event, answer the five questions in `docs/taxonomy/README.md` section 6. Leave Analysis empty and the check fails.
- Run `python3 scripts/check_taxonomy.py` before committing. CI runs the same check on every PR that touches `landing/`, `docs/taxonomy/` or `scripts/`.
- After a tracking change is merged, sync the Amplitude tracking plan (project 성분돋보기, 870210) so new events are not "unexpected".
