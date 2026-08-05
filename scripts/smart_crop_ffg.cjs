const fs = require("node:fs");
const path = require("node:path");
const sharp = require("sharp");

const ROOT = path.resolve(__dirname, "..");
const SOURCE = path.join(ROOT, "images", "ffg_originals");
const DESTINATION = path.join(ROOT, "images", "portraits");
const MANIFEST_PATH = path.join(DESTINATION, "ffg_sources.json");
const MANIFEST = JSON.parse(fs.readFileSync(MANIFEST_PATH, "utf8"));

// Values are only needed when the attention crop cannot understand a highly
// stylized composition. x=0 keeps the left edge; x=1 keeps the right edge.
const FOCUS_OVERRIDES = {
  "spider-man-peter": { x: 0.25 },
  "captain-america": { x: 0.2, trimBottom: 0.28 },
  hulk: { x: 0, artTop: 0.12 },
  daredevil: { x: 0.5, artLeft: 0.28, artRight: 0.78, artTop: 0.145, artBottom: 0.545 },
  hawkeye: { x: 0.5, artLeft: 0.28, artRight: 0.78, artTop: 0.145, artBottom: 0.545 },
  falcon: { x: 0.5, artLeft: 0.28, artRight: 0.78, artTop: 0.145, artBottom: 0.545 },
  "rocket-raccoon": { x: 0, artTop: 0.12 },
  "star-lord": { x: 0, artTop: 0.12 },
  drax: { x: 0, artTop: 0.12 },
  bishop: { x: 0.5, artTop: 0.12 },
  storm: { x: 0.85, artTop: 0.12 },
  cable: { x: 1, artTop: 0.12 },
  ironheart: { x: 0.15, artTop: 0.12 },
  "maria-hill": { x: 0.65, artTop: 0.11 },
  silk: { x: 0.5, artLeft: 0.28, artRight: 0.78, artTop: 0.145, artBottom: 0.545 },
  "venom-hero": { x: 0.5, artLeft: 0.28, artRight: 0.78, artTop: 0.145, artBottom: 0.545 },
  "luke-cage": { x: 0.7, artTop: 0.12 },
  "jessica-jones": { x: 0.7, artTop: 0.12 },
  echo: { x: 0.5, artLeft: 0.32, artRight: 0.62, artTop: 0.13, artBottom: 0.39 },
  valkyrie: { x: 1, trimBottom: 0.12 },
  deadpool: { x: 0.95, trimBottom: 0.42 },
  "nick-fury": { x: 1 },
  rhino: { x: 0, artLeft: 0.2 },
  wrecker: { x: 0.15, artTop: 0.12 },
  piledriver: { x: 0.2, artTop: 0.12 },
  crossbones: { x: 0, artTop: 0.12 },
  "absorbing-man": { x: 0.2, artTop: 0.12 },
  "red-skull": { x: 0.3, artTop: 0.12 },
  "green-goblin": {
    x: 0.5,
    artLeft: 0.32,
    artRight: 0.78,
    artTop: 0.12,
    artBottom: 0.53,
  },
  ultron: { x: 0 },
  "ebony-maw": { x: 0.22, artLeft: 0.12, artTop: 0.12 },
  enchantress: { x: 0.12, artTop: 0.1 },
  "proxima-midnight": { x: 0.25, artTop: 0.12 },
  drang: { x: 0.5, artLeft: 0.42, artRight: 0.72, artTop: 0.145, artBottom: 0.413 },
  "doctor-octopus": { x: 0.5, artLeft: 0.23, artRight: 0.48, artTop: 0.19, artBottom: 0.414 },
  scorpion: { x: 0.5, artLeft: 0.48, artRight: 0.73, artTop: 0.21, artBottom: 0.434 },
  "venom-goblin": { x: 0.5, artLeft: 0.45, artRight: 0.7, artTop: 0.21, artBottom: 0.434 },
  mojo: { x: 0, artTop: 0.12 },
  spiral: { x: 0, artTop: 0.12 },
  sabretooth: { x: 1, artTop: 0.12 },
  thanos: { x: 0 },
  arclight: { x: 0.5, artLeft: 0.225, artRight: 0.475, artTop: 0.21, artBottom: 0.434 },
  blockbuster: { x: 0 },
  greycrow: { x: 1, artTop: 0.12, trimBottom: 0.16 },
  harpoon: {
    x: 0,
    artLeft: 0.28,
    artTop: 0.12,
    trimBottom: 0.16,
  },
  riptide: {
    x: 0.5,
    artLeft: 0.12,
    artRight: 0.42,
    artTop: 0.14,
    artBottom: 0.408,
  },
  vertigo: { x: 0, trimBottom: 0.18 },
  "mister-sinister": { x: 1, artTop: 0.09, trimBottom: 0.2 },
  stryfe: { x: 1, artTop: 0.12 },
  apocalypse: { x: 0.5, artLeft: 0.3, artRight: 0.7, artTop: 0.1, artBottom: 0.458 },
  "en-sabah-nur": { x: 0.5, artLeft: 0.3, artRight: 0.75, artTop: 0.1, artBottom: 0.47 },
  "dark-beast": { x: 1, artTop: 0.12 },
  batroc: { x: 0.5, artLeft: 0.45, artRight: 0.7, artTop: 0.21, artBottom: 0.434 },
  modok: { x: 0, trimBottom: 0.08 },
  atlas: { x: 0 },
  "mach-x": { x: 1, artTop: 0.12 },
  songbird: { x: 1, artTop: 0.11, trimBottom: 0.12 },
  techno: { x: 0, trimBottom: 0.05 },
  thunderball: { x: 0.1, artTop: 0.12 },
  "iron-man-leader": { x: 0 },
  "captain-america-leader": { x: 0 },
  "spider-woman-leader": { x: 0 },
  "she-hulk-leader": { x: 1, artTop: 0.11 },
  "vision-leader": { x: 0.3, artTop: 0.12 },
  bullseye: { x: 0.5, artLeft: 0.41, artRight: 0.66, artTop: 0.145, artBottom: 0.369 },
};

function artBounds(width, height, focus) {
  const left = Math.round(width * (focus?.artLeft ?? 0.225));
  const top = Math.round(height * (focus?.artTop ?? 0.145));
  const right = Math.round(width * (focus?.artRight ?? 0.93));
  const bottom = Math.round(height * (focus?.artBottom ?? 0.545));
  return {
    left,
    top,
    width: right - left,
    height: bottom - top,
  };
}

function focalCrop(bounds, focus) {
  const targetAspect = 240 / 300;
  const sourceAspect = bounds.width / bounds.height;
  if (sourceAspect > targetAspect) {
    const width = Math.round(bounds.height * targetAspect);
    const travel = bounds.width - width;
    return {
      left: Math.round(travel * focus.x),
      top: 0,
      width,
      height: bounds.height,
    };
  }
  const height = Math.round(bounds.width / targetAspect);
  const travel = bounds.height - height;
  return {
    left: 0,
    top: Math.round(travel * (focus.y ?? 0.42)),
    width: bounds.width,
    height,
  };
}

async function cropPortrait(characterId) {
  const input = path.join(SOURCE, `${characterId}.png`);
  const output = path.join(DESTINATION, `${characterId}.webp`);
  const metadata = await sharp(input).metadata();
  const focus = FOCUS_OVERRIDES[characterId];
  const initialBounds = artBounds(metadata.width, metadata.height, focus);
  const trimLeft = Math.round(initialBounds.width * (focus?.trimLeft ?? 0));
  const trimTop = Math.round(initialBounds.height * (focus?.trimTop ?? 0));
  const trimRight = Math.round(initialBounds.width * (focus?.trimRight ?? 0));
  const trimBottom = Math.round(initialBounds.height * (focus?.trimBottom ?? 0));
  const bounds = {
    left: initialBounds.left + trimLeft,
    top: initialBounds.top + trimTop,
    width: initialBounds.width - trimLeft - trimRight,
    height: initialBounds.height - trimTop - trimBottom,
  };
  let pipeline;
  if (focus) {
    const crop = focalCrop(bounds, focus);
    pipeline = sharp(input)
      .extract({
        left: bounds.left + crop.left,
        top: bounds.top + crop.top,
        width: crop.width,
        height: crop.height,
      })
      .resize(240, 300, { fit: "fill" });
  } else {
    pipeline = sharp(input)
      .extract(bounds)
      .resize(240, 300, {
        fit: "cover",
        position: sharp.strategy.attention,
      });
  }

  await pipeline.webp({ quality: 86, effort: 6 }).toFile(output);
}

async function main() {
  const availableIds = Object.entries(MANIFEST)
    .filter(([, details]) => details.status === "ok")
    .map(([characterId]) => characterId);
  const requestedIds = process.argv.slice(2);
  const ids = requestedIds.length
    ? requestedIds.filter((id) => availableIds.includes(id))
    : availableIds;

  for (const [index, characterId] of ids.entries()) {
    await cropPortrait(characterId);
    console.log(
      `${String(index + 1).padStart(3, "0")}/${ids.length} ${characterId}`,
    );
  }
  console.log(`Subject-aware crops applied to ${ids.length} portraits`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
