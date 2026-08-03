const fs = require("node:fs");
const path = require("node:path");

const root = path.resolve(__dirname, "..");
const data = JSON.parse(
  fs.readFileSync(path.join(root, "matchups.json"), "utf8"),
);
const appPath = path.join(root, "app.js");
const app = fs.readFileSync(appPath, "utf8");
const dataStart = app.indexOf("const DATA = ");
const dataLineEnd = app.indexOf("\n", dataStart);

if (dataStart === -1 || dataLineEnd === -1) {
  throw new Error("Could not find the embedded DATA declaration in app.js");
}

fs.writeFileSync(
  appPath,
  `${app.slice(0, dataStart)}const DATA = ${JSON.stringify(data)};\n${app.slice(dataLineEnd + 1)}`,
  "utf8",
);

console.log("Embedded matchup data synchronized");
