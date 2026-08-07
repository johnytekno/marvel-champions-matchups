const fs = require("node:fs");
const path = require("node:path");

const root = path.resolve(__dirname, "..");
const dataPath = path.join(root, "matchups.json");
const apply = process.argv.includes("--apply");

// VillainTheory's published Standard-mode tier lists, using each scenario's
// printed/recommended setup. Ratings are keyed by the site's player-count modes.
const sourced = {
  "battle-01": [3, 2, 2],
  "battle-02": [4, 4, 4],
  "battle-03": [6, 6, 6],
  "battle-04": [1, 1, 1],
  "battle-05": [5, 5, 5],
  "battle-06": [1, 1, 1],
  "battle-07": [4, 4, 4],
  "battle-08": [2, 2, 2],
  "battle-09": [2, 2, 2],
  "battle-10": [3, 3, 3],
  "battle-11": [7, 6, 5],
  "battle-12": [6, 6, 6],
  "battle-13": [4, 4, 5],
  "battle-14": [8, 7, 7],
  "battle-15": [3, 3, 3],
  "battle-16": [8, 8, 8],
  "battle-17": [10, 10, 10],
  "battle-18": [4, 4, 4],
  "battle-19": [1, 1, 1],
  "battle-20": [7, 7, 7],
  "battle-21": [4, 4, 4],
  "battle-22": [9, 9, 9],
  "battle-23": [6, 6, 6],
  "battle-24": [2, 2, 2],
  "battle-25": [5, 5, 5],
  "battle-26": [4, 4, 4],
  "battle-27": [3, 3, 3],
  "battle-28": [9, 9, 9],
  "battle-29": [4, 4, 4],
  "battle-30": [5, 5, 6],
  "battle-31": [7, 7, 7],
  "battle-32": [5, 5, 5],
  "battle-33": [6, 5, 5],
  "battle-34": [2, 3, 4],
  "battle-35": [5, 5, 5],
  "battle-36": [9, 9, 9],
  "battle-37": [2, 2, 2],
  "battle-38": [5, 5, 5],
  "battle-39": [6, 6, 6],
  "battle-40": [5, 5, 5],
  "battle-41": [5, 5, 5],
  "battle-42": [4, 4, 4],
  "battle-43": [8, 8, 8],
  "battle-44": [8, 8, 8],
  "battle-45": [5, 5, 5],
  "battle-46": [6, 6, 6],
};

// Later releases do not yet have a complete three-player-count Standard set
// from VillainTheory. These transparent estimates keep every battle useful and
// are intentionally flagged in both data and UI until a published list exists.
const provisional = {
  "battle-47": [5, 5, 5],
  "battle-48": [4, 4, 4],
  "battle-49": [4, 4, 4],
  "battle-50": [3, 3, 3],
  "battle-51": [7, 7, 7],
  "battle-52": [6, 6, 6],
  "battle-53": [3, 3, 3],
  "battle-54": [5, 5, 5],
  "battle-55": [5, 5, 5],
  "battle-56": [4, 4, 4],
  "battle-57": [5, 5, 5],
  "battle-58": [6, 6, 6],
  "battle-59": [6, 6, 6],
  "battle-60": [7, 7, 8],
  "battle-61": [5, 5, 5],
  "battle-62": [5, 5, 5],
  "battle-63": [6, 6, 6],
  "battle-64": [6, 6, 6],
  "battle-65": [7, 8, 8],
};

function record(values, status) {
  const [solo, two, group] = values;
  return { solo, two, group, status };
}

const data = JSON.parse(fs.readFileSync(dataPath, "utf8"));
const scenarioIds = data.campaigns.flatMap((campaign) =>
  campaign.scenarios.map((scenario) => scenario.id),
);
const scenarios = Object.fromEntries([
  ...Object.entries(sourced).map(([id, values]) => [id, record(values, "sourced")]),
  ...Object.entries(provisional).map(([id, values]) => [id, record(values, "provisional")]),
]);

const missing = scenarioIds.filter((id) => !scenarios[id]);
const extra = Object.keys(scenarios).filter((id) => !scenarioIds.includes(id));
if (missing.length || extra.length) {
  throw new Error(`Baseline coverage mismatch. Missing: ${missing.join(", ") || "none"}; extra: ${extra.join(", ") || "none"}`);
}
for (const [id, values] of Object.entries(scenarios)) {
  for (const key of ["solo", "two", "group"]) {
    if (!Number.isInteger(values[key]) || values[key] < 1 || values[key] > 10) {
      throw new Error(`${id} has invalid ${key} baseline: ${values[key]}`);
    }
  }
}

data.difficultyBaselines = {
  source: {
    curator: "VillainTheory",
    title: "Complete Villain Difficulty Ranking",
    rankingUrl: "https://www.youtube.com/watch?v=OIHxE77U928",
    scaleUrl: "https://tiermaker.com/create/marvel-champions-villains-16731517",
    mode: "Standard I/II with each scenario's printed or recommended setup",
    published: "2024-09-19",
    imported: "2026-08-07",
    coverage: "Battles 1–46 are published player-count rankings. Battles 47–65 are clearly labeled provisional estimates pending a complete published Standard update.",
  },
  labels: {
    1: "Ultra Easy",
    2: "Very Easy",
    3: "Easy",
    4: "Medium",
    5: "Good Challenge",
    6: "Difficult",
    7: "Very Difficult",
    8: "Punishing",
    9: "Nightmare",
    10: "Omega-Level Threat",
  },
  scenarios,
};
data.updated = "2026-08-07";

const sourcedCount = Object.values(scenarios).filter((item) => item.status === "sourced").length;
const provisionalCount = Object.values(scenarios).filter((item) => item.status === "provisional").length;
console.log(`${scenarioIds.length} baselines ready: ${sourcedCount} sourced, ${provisionalCount} provisional.`);

if (apply) {
  fs.writeFileSync(dataPath, `${JSON.stringify(data, null, 2)}\n`, "utf8");
  console.log("matchups.json updated");
}
