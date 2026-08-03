# Marvel Champions Matchup Site

Open `index.html` in any modern browser. The page is fully static and needs no build step.

## Files
- `index.html` — page shell
- `styles.css` — visual design and print styles
- `app.js` — filters, rendering, encounter modules, hero usage counts, repeat markers, and JSON export
- `scripts/audit_matchups.cjs` — validates roster coverage, identity sequencing, pair uniqueness, repeat markers, encounter setup, and local portraits
- `images/portraits/` — locally bundled, compressed character portraits
- `matchups.json` — canonical structured dataset
- `WORK_CHAT_SOURCE.md` — text-first source designed for upload/paste into another assistant

## Character portraits
All 158 hero and villain portraits are bundled locally as compressed WebP files. The unified set uses cropped Fantasy Flight Games/Marvel Champions card illustrations for 145 characters, with 13 visually reviewed local fallbacks where official scans are not yet available. FFG portraits are made from the original full-resolution scans in a single subject-aware crop, with hand-tuned focal overrides where automatic attention favors a weapon, effect, or card icon over the character. The complete set is reviewed in contact sheets before release. Card frames, titles, rules text, and logos are excluded from the portrait crops. The site makes no external image requests and remains fully usable offline. Source metadata is recorded in `images/portraits/ffg_sources.json` and `images/portraits/sources.json`; styled monograms remain as error fallbacks.

## MarvelCDB deck links

Every hero card links to a transparent MarvelCDB recommendation checked August 3, 2026. The baseline is the most-liked published deck with a play guide of at least 500 characters. A deck published since August 3, 2025 is preferred only when it retains at least 70% of the guided community leader's likes. Luke Cage and Jessica Jones display a pending state because MarvelCDB does not yet list either identity for published decklists. The complete decision data is recorded in `recommended-decks.json`.

## Local editing
Edit `matchups.json` for reference, but the current `app.js` contains an embedded copy of the dataset so the page also works when opened directly from disk. To make content changes, update both or regenerate the page from your source workflow.

## Current usability improvements
- All 65 battles now use a distinct two-hero pairing.
- All 69 heroes and all 89 villain-side identities appear in the schedule.
- No hero fights their own villain incarnation, and Nebula, Magneto, and Angel debut as heroes only after their villain encounters.
- Every battle shows its official recommended or required encounter modules; variable and catalog-pending setups are labeled honestly.
- A frequency-sorted hero usage panel shows total appearances and repeat counts for all 69 heroes.
- No hero appears more than three times, and repeat appearances are always separated by at least six battle numbers.
- Daredevil now appears twice instead of six times; Thor appears three times instead of five.
- Only Thor, Peter Parker, and Scarlet Witch reach three appearances; 55 of the 69 heroes now appear exactly twice.
- Active search and campaign filters now show a concise results summary.
- A Reset filters button returns the full 65-matchup sequence in one step.
- Empty searches offer an immediate “Show all matchups” recovery action.
- Pressing Escape clears active filters.
- Campaign expand/collapse controls now expose their state to assistive technology.
