const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const root = path.resolve(__dirname, "..");
const app = fs.readFileSync(path.join(root, "app.js"), "utf8");
const index = fs.readFileSync(path.join(root, "index.html"), "utf8");
const styles = fs.readFileSync(path.join(root, "styles.css"), "utf8");

const context = vm.createContext({
  console,
  Blob,
  URL,
  setTimeout,
  localStorage: {
    getItem: () => null,
    setItem: () => {},
  },
  document: {
    querySelector: () => null,
    querySelectorAll: () => [],
    addEventListener: () => {},
  },
});

vm.runInContext(app, context);

function evaluate(expression) {
  return vm.runInContext(expression, context);
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

assert(index.includes('id="playerCount"'), "Player-count selector is missing.");
assert(index.includes('id="mobileToolsToggle"') && index.includes('aria-controls="toolbarActions"'), "Accessible mobile tools control is missing.");
assert(styles.includes('.toolbar.mobile-tools-open .actions{display:grid}') && styles.includes('.filter-strip{display:none}'), "Compact mobile toolbar styles are missing.");
assert(index.includes('styles.css?v=20260807-omega-threat') && index.includes('keyword-reference.js?v=20260806-keywords-v1') && index.includes('app.js?v=20260807-omega-threat'), "Versioned assets are missing; clients may receive stale layout files.");
assert(index.includes('id="keywordReference"') && index.includes('id="keywordDialog"') && index.includes('id="keywordSearch"'), "Compiled keyword-reference controls are missing.");
assert(styles.includes('.player-guide-bar') && styles.includes('.keyword-dialog') && styles.includes('.keyword-grid'), "Keyword-reference guide styles are missing.");
assert(index.indexOf('id="campaigns"') < index.indexOf('class="notice"'), "Sequence constraint should follow the campaign list.");
assert(index.indexOf('id="campaigns"') < index.indexOf('class="hero-usage"'), "Hero appearance counts should follow the campaign list.");
for (const className of ["tuner-guide", "tuner-tabs", "tuner-choice", "tuner-panel", "module-profile"]) {
  assert(styles.includes(`.${className}`), `Missing tuner style: ${className}.`);
}
for (const className of ["threat-summary", "threat-badge", "threat-origin", "effective-threat", "module-heading-status"]) {
  assert(styles.includes(`.${className}`), `Missing threat style: ${className}.`);
}
assert(styles.includes('.effective-threat.omega') && styles.includes('@keyframes omegaPulse') && styles.includes('prefers-reduced-motion:reduce'), "Accessible Omega threat treatment is missing.");

const baselineRecords = evaluate("Object.values(DATA.difficultyBaselines.scenarios)");
assert(baselineRecords.length === 65, "Expected a threat baseline for all 65 battles.");
assert(baselineRecords.filter((record) => record.status === "sourced").length === 46, "Expected 46 sourced threat baselines.");
assert(baselineRecords.filter((record) => record.status === "provisional").length === 19, "Expected 19 provisional threat baselines.");
assert(baselineRecords.every((record) => ["solo", "two", "group"].every((key) => Number.isInteger(record[key]) && record[key] >= 1 && record[key] <= 10)), "A threat baseline is outside the 1–10 scale.");

const rhinoThreat = evaluate("threatSummaryHtml(scenarioById('battle-01'))");
assert(rhinoThreat.includes("Base threat") && rhinoThreat.includes("2/10") && rhinoThreat.includes("VillainTheory"), "Rhino's sourced two-player baseline is missing.");
const blackWidowThreat = evaluate("threatSummaryHtml(scenarioById('battle-47'))");
assert(blackWidowThreat.includes("5/10") && blackWidowThreat.includes("Provisional"), "The newer provisional baseline is not labeled.");

const defaultRhino = evaluate("encounterModulesHtml(scenarioById('battle-01'))");
assert(defaultRhino.includes("Official ±0"), "Rhino does not default to the official setup.");
assert(defaultRhino.includes("Bomb Scare"), "Rhino official setup lost Bomb Scare.");
assert(defaultRhino.includes('data-choice="easier"') && defaultRhino.includes("disabled"), "Unavailable easier choice is not disabled.");
assert(defaultRhino.includes('data-choice="maximum"') && defaultRhino.includes("Maximum"), "Rhino Maximum choice is missing.");

evaluate("state.moduleChoices['battle-01']='maximum'; state.playerCount='two'");
const maximumRhino = evaluate("encounterModulesHtml(scenarioById('battle-01'))");
assert(maximumRhino.includes("Thanos with a Horn") && maximumRhino.includes("Maximum +4"), "Rhino Maximum recipe is not rendered.");
assert(maximumRhino.includes("VillainTheory source guide"), "Maximum source-guide attribution is missing.");
assert(maximumRhino.includes("Effective <strong>6/10</strong>") && maximumRhino.includes("+4 → 6/10"), "Rhino Maximum does not show its effective global threat.");

evaluate("state.moduleChoices['battle-17']='harder'; state.playerCount='two'");
const harderRonan = evaluate("encounterModulesHtml(scenarioById('battle-17'))");
assert(harderRonan.includes('effective-threat omega') && harderRonan.includes('Effective <strong>12<b aria-hidden="true">Ω</b></strong>'), "Harder Ronan should render as 12 with the Omega treatment.");
assert(harderRonan.includes('+2 → 12 Ω') && harderRonan.includes('Beyond scale'), "Harder Ronan should preserve the uncapped 10 + 2 arithmetic.");
evaluate("state.moduleChoices['battle-17']='thematic'");
const thematicRonan = evaluate("encounterModulesHtml(scenarioById('battle-17'))");
assert(thematicRonan.includes('+4 → 14 Ω') && thematicRonan.includes('Effective <strong>14<b aria-hidden="true">Ω</b></strong>'), "Infinity Ronan should preserve the uncapped 10 + 4 arithmetic.");

evaluate("state.moduleChoices['battle-01']='thematic'; state.playerCount='two'");
const thematicRhino = evaluate("encounterModulesHtml(scenarioById('battle-01'))");
assert(thematicRhino.includes("Property Damage"), "Rhino thematic recipe is not rendered.");
assert(thematicRhino.includes("Armadillo"), "Rhino thematic modular set is not rendered.");
assert(thematicRhino.includes("VillainTheory via Modular Champions"), "Tuner attribution is missing.");
assert(thematicRhino.includes("2 players:"), "Player-count profile is missing.");
assert(thematicRhino.includes("Effective <strong>3/10</strong>"), "Rhino thematic selection has the wrong effective threat.");

assert(evaluate("(state.playerCount='solo', threatFor(scenarioById('battle-01')).value)") === 3, "Solo baseline selection failed.");
assert(evaluate("(state.playerCount='group', threatFor(scenarioById('battle-11')).value)") === 5, "Group baseline selection failed.");
evaluate("state.playerCount='two'");

const rendered = evaluate(`DATA.campaigns.flatMap(c=>c.scenarios).map(encounterModulesHtml)`);
assert(rendered.length === 65, "Not all 65 encounter tuners render.");
assert(rendered.every((html) => !html.includes("undefined") && !html.includes("[object Object]")), "A tuner rendered invalid content.");
const choiceCounts = rendered.map((html) => (html.match(/class="tuner-choice/g) || []).length);
assert(choiceCounts.every((count) => count === 4 || count === 5), "A tuner has an invalid number of choice buttons.");
assert(choiceCounts.filter((count) => count === 5).length === 60, "Expected exactly 60 sourced Maximum choices.");
assert((rendered[26].match(/class="tuner-choice/g) || []).length === 4, "Sinister Six should not show a redundant Maximum choice.");

const brief = evaluate("workChatText()");
assert(brief.includes("Encounter tuner: 2 players"), "Work-chat export omits the player-count setting.");
assert(brief.includes("Property Damage"), "Work-chat export omits the selected recipe.");
assert(brief.includes("modularchampions.com/scenario/"), "Work-chat export omits recipe attribution.");
assert(brief.includes("Threat: Base threat 2/10") && brief.includes("effective 3/10"), "Work-chat export omits the global threat summary.");

console.log("Encounter tuner test passed");
console.log("65 tuners render with global baselines, effective threat, 60 sourced Maximum choices, player-count profiles, and export attribution");
