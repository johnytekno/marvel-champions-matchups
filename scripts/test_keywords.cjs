const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const root = path.resolve(__dirname, "..");
const source = fs.readFileSync(path.join(root, "keyword-reference.js"), "utf8");
const context = vm.createContext({
  document: { addEventListener: () => {} },
});

vm.runInContext(source, context);

const keywords = context.MC_KEYWORDS;
const names = keywords.map(keyword => keyword.name);
const expected = ["Alliance", "Assault", "Form", "Guard", "Hinder X", "Incite X", "Linked (Card Title)", "Overkill", "Patrol", "Peril", "Permanent", "Piercing", "Quickstrike", "Ranged", "Requirement (Resources)", "Restricted", "Retaliate X", "Setup", "Stalwart", "Steady", "Surge", "Team-Up", "Teamwork (Trait)", "Temporary", "Toughness", "Uses (X type)", "Victory X", "Villainous"];

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

assert(keywords.length === 28, `Expected 28 official keywords, found ${keywords.length}.`);
assert(new Set(names).size === names.length, "Keyword names must be unique.");
assert(JSON.stringify(names) === JSON.stringify(expected), "Keyword list is incomplete or not alphabetized.");
assert(keywords.every(keyword => keyword.category && keyword.summary.length >= 25), "Each keyword needs a category and useful quick definition.");
assert(keywords.find(keyword => keyword.name === "Surge").summary.includes("facedown encounter card"), "Surge must follow the v1.8 timing update.");
assert(keywords.find(keyword => keyword.name === "Steady").summary.includes("two Stunned") && keywords.find(keyword => keyword.name === "Steady").summary.includes("two Confused"), "Steady definition is incomplete.");

console.log("Keyword reference test passed");
console.log("28 official v1.8 keywords; alphabetized, unique, categorized, and searchable");
