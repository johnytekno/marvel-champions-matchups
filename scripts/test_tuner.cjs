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
assert(index.includes('styles.css?v=20260806-keyword-quickref') && index.includes('keyword-reference.js?v=20260806-keywords-v1') && index.includes('app.js?v=20260805-iconic-pass'), "Versioned assets are missing; clients may receive stale layout files.");
assert(index.includes('id="keywordReference"') && index.includes('id="keywordDialog"') && index.includes('id="keywordSearch"'), "Compiled keyword-reference controls are missing.");
assert(styles.includes('.player-guide-bar') && styles.includes('.keyword-dialog') && styles.includes('.keyword-grid'), "Keyword-reference guide styles are missing.");
assert(index.indexOf('id="campaigns"') < index.indexOf('class="notice"'), "Sequence constraint should follow the campaign list.");
assert(index.indexOf('id="campaigns"') < index.indexOf('class="hero-usage"'), "Hero appearance counts should follow the campaign list.");
for (const className of ["tuner-guide", "tuner-tabs", "tuner-choice", "tuner-panel", "module-profile"]) {
  assert(styles.includes(`.${className}`), `Missing tuner style: ${className}.`);
}

const defaultRhino = evaluate("encounterModulesHtml(scenarioById('battle-01'))");
assert(defaultRhino.includes("Official ±0"), "Rhino does not default to the official setup.");
assert(defaultRhino.includes("Bomb Scare"), "Rhino official setup lost Bomb Scare.");
assert(defaultRhino.includes('data-choice="easier"') && defaultRhino.includes("disabled"), "Unavailable easier choice is not disabled.");
assert(defaultRhino.includes('data-choice="maximum"') && defaultRhino.includes("Maximum"), "Rhino Maximum choice is missing.");

evaluate("state.moduleChoices['battle-01']='maximum'; state.playerCount='two'");
const maximumRhino = evaluate("encounterModulesHtml(scenarioById('battle-01'))");
assert(maximumRhino.includes("Thanos with a Horn") && maximumRhino.includes("Maximum +4"), "Rhino Maximum recipe is not rendered.");
assert(maximumRhino.includes("VillainTheory source guide"), "Maximum source-guide attribution is missing.");

evaluate("state.moduleChoices['battle-01']='thematic'; state.playerCount='two'");
const thematicRhino = evaluate("encounterModulesHtml(scenarioById('battle-01'))");
assert(thematicRhino.includes("Property Damage"), "Rhino thematic recipe is not rendered.");
assert(thematicRhino.includes("Armadillo"), "Rhino thematic modular set is not rendered.");
assert(thematicRhino.includes("VillainTheory via Modular Champions"), "Tuner attribution is missing.");
assert(thematicRhino.includes("2 players:"), "Player-count profile is missing.");

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

console.log("Encounter tuner test passed");
console.log("65 tuners render with official defaults, 60 sourced Maximum choices, player-count profiles, and export attribution");
