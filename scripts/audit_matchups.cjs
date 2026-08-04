const fs = require("node:fs");
const path = require("node:path");

const root = path.resolve(__dirname, "..");
const data = JSON.parse(fs.readFileSync(path.join(root, "matchups.json"), "utf8"));
const errors = [];

// Shared identities use explicit keys so equal codenames held by different people
// (such as Natasha/Yelena and Eddie Brock/Flash Thompson) stay distinct.
const identityOverrides = {
  angel: "warren-worthington",
  "horseman-death": "warren-worthington",
  "nebula-hero": "nebula",
  "nebula-villain": "nebula",
  "magneto-hero": "magneto",
  "magneto-villain": "magneto",
  "iron-man": "tony-stark",
  "iron-man-leader": "tony-stark",
  "captain-marvel": "carol-danvers",
  "captain-marvel-leader": "carol-danvers",
  "captain-america": "steve-rogers",
  "captain-america-leader": "steve-rogers",
  "spider-woman": "jessica-drew",
  "spider-woman-leader": "jessica-drew",
  "she-hulk": "jennifer-walters",
  "she-hulk-leader": "jennifer-walters",
  vision: "vision",
  "vision-leader": "vision",
  "norman-osborn": "norman-osborn",
  "green-goblin": "norman-osborn",
  "venom-goblin": "norman-osborn",
  apocalypse: "en-sabah-nur",
  "en-sabah-nur": "en-sabah-nur",
  loki: "loki",
  "loki-god-of-lies": "loki",
  electro: "max-dillon",
  "electro-fne": "max-dillon",
};

const opposingLeaderIds = new Set([
  "iron-man-leader",
  "captain-marvel-leader",
  "captain-america-leader",
  "spider-woman-leader",
  "she-hulk-leader",
  "vision-leader",
]);

const identityLabels = {
  nebula: "Nebula",
  magneto: "Magneto",
  "warren-worthington": "Angel / Death",
};

const identityFor = (id) => identityOverrides[id] || id;
const characters = Object.entries(data.characters);
const heroRoster = characters.filter(([, character]) => character.role === "hero");
const villainRoster = characters.filter(([, character]) => character.role === "villain");
const usedHeroes = new Set();
const usedVillains = new Set();
const seenHeroes = new Set();
const seenPairs = new Map();
const seenBattleIds = new Set();
const heroBattles = new Map();
const validModuleTypes = new Set(["official", "variable", "self-contained", "campaign", "special"]);
const firstHeroBattle = new Map();
const firstVillainBattle = new Map();
let battleCount = 0;

for (const campaign of data.campaigns) {
  for (const scenario of campaign.scenarios) {
    battleCount += 1;
    if (scenario.number !== battleCount) {
      errors.push(`Expected battle ${battleCount}, found ${scenario.number}.`);
    }
    seenBattleIds.add(scenario.id);

    const moduleInfo = data.encounterModules?.[scenario.id];
    if (!moduleInfo) {
      errors.push(`Battle ${scenario.number} is missing encounter-module setup.`);
    } else {
      if (!validModuleTypes.has(moduleInfo.type)) {
        errors.push(`Battle ${scenario.number} has invalid encounter-module type ${moduleInfo.type}.`);
      }
      if (!Array.isArray(moduleInfo.sets) || moduleInfo.sets.some((set) => typeof set !== "string" || !set.trim())) {
        errors.push(`Battle ${scenario.number} has an invalid encounter-module set list.`);
      }
      if (moduleInfo.scenarioSet !== undefined && (typeof moduleInfo.scenarioSet !== "string" || !moduleInfo.scenarioSet.trim())) {
        errors.push(`Battle ${scenario.number} has an invalid scenario-set label.`);
      }
      if (moduleInfo.note !== undefined && (typeof moduleInfo.note !== "string" || !moduleInfo.note.trim())) {
        errors.push(`Battle ${scenario.number} has an invalid encounter-module note.`);
      }
    }

    const tuning = data.difficultyTuner?.scenarios?.[scenario.id];
    if (!tuning) {
      errors.push(`Battle ${scenario.number} is missing encounter-tuner data.`);
    } else {
      if (typeof tuning.villainCode !== "string" || !tuning.villainCode.trim()) {
        errors.push(`Battle ${scenario.number} has an invalid tuner villain code.`);
      }
      const signatures = new Set();
      for (const key of ["easier", "thematic", "harder"]) {
        const choice = tuning[key];
        if (choice === null) continue;
        if (!choice || typeof choice.name !== "string" || !choice.name.trim()) {
          errors.push(`Battle ${scenario.number} has an invalid ${key} tuner choice.`);
          continue;
        }
        if (!Number.isInteger(choice.difficulty)) {
          errors.push(`Battle ${scenario.number} ${key} choice has a non-integer difficulty delta.`);
        }
        if (key === "easier" && choice.difficulty >= 0) {
          errors.push(`Battle ${scenario.number} easier choice is not below the official baseline.`);
        }
        if (key === "harder" && choice.difficulty <= 0) {
          errors.push(`Battle ${scenario.number} harder choice is not above the official baseline.`);
        }
        if (!Array.isArray(choice.sets) || choice.sets.some((set) => !set?.name || !set?.code)) {
          errors.push(`Battle ${scenario.number} ${key} choice has invalid modular sets.`);
        }
        if (!Array.isArray(choice.mainSchemes) || !Array.isArray(choice.tags)) {
          errors.push(`Battle ${scenario.number} ${key} choice has invalid setup metadata.`);
        }
        if (typeof choice.notes !== "string" || !choice.url?.startsWith("https://modularchampions.com/scenario/")) {
          errors.push(`Battle ${scenario.number} ${key} choice has invalid attribution.`);
        }
        const signature = JSON.stringify([
          choice.sets.map((set) => set.code).sort(),
          [...choice.mainSchemes].sort(),
        ]);
        if (signatures.has(signature)) {
          errors.push(`Battle ${scenario.number} repeats an exact tuner recipe.`);
        }
        signatures.add(signature);
      }
    }

    const heroIdentities = new Set();
    const villainIdentities = new Set();

    for (const villainId of scenario.villains) {
      const character = data.characters[villainId];
      if (!character) {
        errors.push(`Battle ${scenario.number} references missing villain ${villainId}.`);
        continue;
      }
      if (character.role !== "villain") {
        errors.push(`Battle ${scenario.number} lists non-villain ${villainId} on the villain side.`);
      }
      usedVillains.add(villainId);
      const identity = identityFor(villainId);
      villainIdentities.add(identity);
      if (!opposingLeaderIds.has(villainId) && !firstVillainBattle.has(identity)) {
        firstVillainBattle.set(identity, scenario.number);
      }
    }

    for (const heroId of scenario.heroes) {
      const character = data.characters[heroId];
      if (!character) {
        errors.push(`Battle ${scenario.number} references missing hero ${heroId}.`);
        continue;
      }
      if (character.role !== "hero") {
        errors.push(`Battle ${scenario.number} lists non-hero ${heroId} on the hero team.`);
      }
      usedHeroes.add(heroId);
      if (!heroBattles.has(heroId)) heroBattles.set(heroId, []);
      heroBattles.get(heroId).push(scenario.number);
      const identity = identityFor(heroId);
      heroIdentities.add(identity);
      if (!firstHeroBattle.has(identity)) firstHeroBattle.set(identity, scenario.number);
    }

    for (const identity of heroIdentities) {
      if (villainIdentities.has(identity)) {
        errors.push(`Battle ${scenario.number} pits ${identity} against themself.`);
      }
    }

    const pairKey = [...scenario.heroes].sort().join("|");
    if (seenPairs.has(pairKey)) {
      errors.push(`Battles ${seenPairs.get(pairKey)} and ${scenario.number} repeat hero pair ${pairKey}.`);
    } else {
      seenPairs.set(pairKey, scenario.number);
    }

    if (scenario.heroAssignments.length !== scenario.heroes.length) {
      errors.push(`Battle ${scenario.number} has mismatched hero assignment counts.`);
    }
    scenario.heroAssignments.forEach((assignment, index) => {
      if (assignment.id !== scenario.heroes[index]) {
        errors.push(`Battle ${scenario.number} hero assignment order does not match its hero team.`);
      }
      const expectedRepeat = seenHeroes.has(assignment.id);
      if (assignment.repeat !== expectedRepeat) {
        errors.push(`Battle ${scenario.number} has an incorrect repeat marker for ${assignment.id}.`);
      }
      seenHeroes.add(assignment.id);
    });
  }
}

for (const battleId of Object.keys(data.encounterModules || {})) {
  if (!seenBattleIds.has(battleId)) errors.push(`Encounter-module setup references unknown battle ${battleId}.`);
}
for (const battleId of Object.keys(data.difficultyTuner?.scenarios || {})) {
  if (!seenBattleIds.has(battleId)) errors.push(`Encounter-tuner data references unknown battle ${battleId}.`);
}
if (data.difficultyTuner?.source?.curator !== "VillainTheory") {
  errors.push("Encounter-tuner source attribution is missing or incorrect.");
}
if (Object.keys(data.difficultyTuner?.moduleRatings || {}).length < 100) {
  errors.push("Encounter-tuner player-count matrix is missing or incomplete.");
} else {
  for (const [moduleName, ratings] of Object.entries(data.difficultyTuner.moduleRatings)) {
    for (const playerCount of ["solo", "two", "group"]) {
      const rating = ratings[playerCount];
      if (rating !== null && (!Number.isInteger(rating) || rating < 1 || rating > 10)) {
        errors.push(`${moduleName} has an invalid ${playerCount} module rating.`);
      }
    }
  }
}

for (const [heroId, battles] of heroBattles) {
  if (battles.length > data.rules.appearanceCap) {
    errors.push(`${heroId} appears ${battles.length} times, above the cap of ${data.rules.appearanceCap}.`);
  }
  for (let index = 1; index < battles.length; index += 1) {
    const gap = battles[index] - battles[index - 1];
    if (gap < data.rules.minimumRepeatGap) {
      errors.push(`${heroId} repeats in battles ${battles[index - 1]} and ${battles[index]}, only ${gap} battles apart.`);
    }
  }
}

for (const [identity, heroBattle] of firstHeroBattle) {
  const villainBattle = firstVillainBattle.get(identity);
  if (villainBattle !== undefined && heroBattle <= villainBattle) {
    errors.push(`${identityLabels[identity] || identity} appears as a hero in battle ${heroBattle} before its villain encounter in battle ${villainBattle}.`);
  }
}

for (const [id] of heroRoster) {
  if (!usedHeroes.has(id)) errors.push(`Hero roster entry ${id} is unused.`);
}
for (const [id] of villainRoster) {
  if (!usedVillains.has(id)) errors.push(`Villain roster entry ${id} is unused.`);
}
for (const [id] of characters) {
  if (!fs.existsSync(path.join(root, "images", "portraits", `${id}.webp`))) {
    errors.push(`Character ${id} is missing a local portrait.`);
  }
}

const app = fs.readFileSync(path.join(root, "app.js"), "utf8");
const embeddedStart = app.indexOf("const DATA = ");
const embeddedLineEnd = app.indexOf("\n", embeddedStart);
if (embeddedStart === -1 || embeddedLineEnd === -1) {
  errors.push("app.js is missing its embedded matchup data.");
} else {
  try {
    const embeddedLine = app.slice(embeddedStart + "const DATA = ".length, embeddedLineEnd).trim();
    const embeddedJson = embeddedLine.endsWith(";") ? embeddedLine.slice(0, -1) : embeddedLine;
    const embeddedData = JSON.parse(embeddedJson);
    if (JSON.stringify(embeddedData) !== JSON.stringify(data)) {
      errors.push("app.js embedded data does not match matchups.json.");
    }
  } catch {
    errors.push("app.js contains invalid embedded matchup data.");
  }
}

if (errors.length) {
  console.error(`Matchup audit failed with ${errors.length} problem(s):`);
  errors.forEach((error) => console.error(`- ${error}`));
  process.exit(1);
}

const sequencedIdentities = [...firstHeroBattle.keys()]
  .filter((identity) => firstVillainBattle.has(identity))
  .map((identity) => `${identityLabels[identity] || identity}: villain ${firstVillainBattle.get(identity)} -> hero ${firstHeroBattle.get(identity)}`)
  .join("; ");
const appearanceMaximum = Math.max(...[...heroBattles.values()].map((battles) => battles.length));
const repeatGaps = [...heroBattles.values()].flatMap((battles) => battles.slice(1).map((battle, index) => battle - battles[index]));
const closestRepeat = Math.min(...repeatGaps);

console.log("Matchup audit passed");
console.log(`${battleCount} battles; ${heroRoster.length} heroes; ${villainRoster.length} villain-side identities; ${characters.length} local portraits`);
console.log(`${Object.keys(data.difficultyTuner.scenarios).length} encounter tuners; ${Object.keys(data.difficultyTuner.moduleRatings).length} player-count-rated modular sets`);
console.log(`Maximum ${appearanceMaximum} appearances per hero; closest repeat is ${closestRepeat} battles apart`);
console.log("0 self-matchups; 0 premature hero debuts; 0 repeated hero pairs; 0 unused roster entries; 0 repeat-marker errors; 0 casting-balance errors");
console.log(`Sequenced dual-role identities: ${sequencedIdentities}`);
