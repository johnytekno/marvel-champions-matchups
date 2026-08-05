# Marvel Champions Matchup Site

Open `index.html` in any modern browser. The page is fully static and needs no build step.

## Files
- `index.html` — page shell
- `styles.css` — visual design and print styles
- `app.js` — filters, encounter tuner, rendering, hero usage counts, repeat markers, and JSON export
- `scripts/audit_matchups.cjs` — validates roster coverage, identity sequencing, pair uniqueness, repeat markers, encounter setup, tuner data, and local portraits
- `scripts/test_tuner.cjs` — statically exercises all 65 tuner panels, player-count profiles, persistence state, and work-chat export
- `scripts/import_villaintheory.py` — reproducible importer for the public Modular Champions catalog and VillainTheory matrix exports
- `scripts/import_villaintheory_maximum.py` — imports the highest distinct recipe directly from VillainTheory's public source guide
- `scripts/audit_module_coverage.py` — measures rated-set coverage and flags unused or overrepresented modular sets
- `images/portraits/` — locally bundled, compressed character portraits
- `matchups.json` — canonical structured dataset
- `WORK_CHAT_SOURCE.md` — text-first source designed for upload/paste into another assistant

## Character portraits
All 158 hero and villain portraits are bundled locally as compressed WebP files. The unified set uses cropped Fantasy Flight Games/Marvel Champions card illustrations for 145 characters, with 13 visually reviewed local fallbacks where official scans are not yet available. FFG portraits are made from the original full-resolution scans in a single subject-aware crop, with hand-tuned focal overrides where automatic attention favors a weapon, effect, or card icon over the character. The complete set is reviewed in contact sheets before release. Card frames, titles, rules text, and logos are excluded from the portrait crops. The site makes no external image requests and remains fully usable offline. Source metadata is recorded in `images/portraits/ffg_sources.json` and `images/portraits/sources.json`; styled monograms remain as error fallbacks.

## MarvelCDB deck links

Every hero card links to a transparent MarvelCDB recommendation checked August 3, 2026. The baseline is the most-liked published deck with a play guide of at least 500 characters. A deck published since August 3, 2025 is preferred only when it retains at least 70% of the guided community leader's likes. Luke Cage and Jessica Jones display a pending state because MarvelCDB does not yet list either identity for published decklists. The complete decision data is recorded in `recommended-decks.json`.

## Encounter tuner

Every battle defaults to the printed Fantasy Flight Games setup and offers up to four optional VillainTheory recipes: easier, thematic, harder, and Maximum. Maximum appears only when the public source guide has a distinct recipe rated above the scenario's Harder choice; 60 of 65 battles qualify. The 719-record public VillainTheory catalog on Modular Champions was imported August 4, 2026 and covers all 65 scenarios in this schedule. The compact site dataset keeps one published recipe per available slot and links directly back to its source record.

The VillainTheory difficulty delta is relative to the selected villain; it is not a global score. A global solo, two-player, or 3–4-player selector supplements that delta with the corresponding modular-set profile from VillainTheory's May 2026 matrix. Required, story, campaign, and nemesis sets that are absent from that matrix are labeled as unrated instead of receiving invented scores. Player count and per-battle choices persist locally in the browser. The selected recipes are also included in the work-chat and print/PDF outputs.

Expert mode is independent of the recipe picker: normally use villain stages II/III instead of I/II, add the Expert encounter set, and follow any scenario or campaign-specific Expert instructions. Standard II/Expert II and Standard III are optional replacement encounter sets, not automatic parts of Expert mode.

## Local editing
Edit `matchups.json` for reference, but the current `app.js` contains an embedded copy of the dataset so the page also works when opened directly from disk. To make content changes, update both or regenerate the page from your source workflow.

## Current usability improvements
- All 65 battles now use a distinct two-hero pairing.
- All 69 heroes and all 89 villain-side identities appear in the schedule.
- No hero fights their own villain incarnation, and Nebula, Magneto, and Angel debut as heroes only after their villain encounters.
- Every battle shows its official recommended or required encounter modules; variable and catalog-pending setups are labeled honestly.
- All 65 battles include an official-first encounter tuner backed by published VillainTheory recipes, with unavailable slots disabled rather than guessed.
- Player-count-aware modular ratings switch globally among solo, two-player, and 3–4-player profiles.
- A frequency-sorted hero usage panel shows total appearances and repeat counts for all 69 heroes.
- No hero appears more than three times, and repeat appearances are always separated by at least six battle numbers.
- Daredevil now appears twice instead of six times; Thor appears three times instead of five.
- Only Thor, Peter Parker, and Scarlet Witch reach three appearances; 55 of the 69 heroes now appear exactly twice.
- Active search and campaign filters now show a concise results summary.
- A Reset filters button returns the full 65-matchup sequence in one step.
- Empty searches offer an immediate “Show all matchups” recovery action.
- Pressing Escape clears active filters.
- Campaign expand/collapse controls now expose their state to assistive technology.
- Phone layouts use a compact two-row filter bar, hide redundant campaign chips, and place secondary actions behind an accessible Tools toggle.
