import json
from math import ceil
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "matchups.json").read_text(encoding="utf-8"))
MANIFEST = json.loads(
    (ROOT / "images" / "portraits" / "ffg_sources.json").read_text(
        encoding="utf-8"
    )
)
OUTPUT = ROOT / "_crop_audit"
OUTPUT.mkdir(exist_ok=True)

columns = 5
batch_size = 40
tile_width = 200
tile_height = 250
ids = list(DATA["characters"])

for offset in range(0, len(ids), batch_size):
    batch = ids[offset : offset + batch_size]
    canvas = Image.new(
        "RGB",
        (columns * tile_width, ceil(len(batch) / columns) * tile_height),
        "#111722",
    )
    draw = ImageDraw.Draw(canvas)
    for index, character_id in enumerate(batch):
        image = Image.open(
            ROOT / "images" / "portraits" / f"{character_id}.webp"
        ).convert("RGB")
        x = (index % columns) * tile_width
        y = (index // columns) * tile_height
        canvas.paste(image.resize((160, 200)), (x + 5, y + 28))
        source = (
            "FFG"
            if MANIFEST.get(character_id, {}).get("status") == "ok"
            else "fallback"
        )
        draw.text((x + 5, y + 7), f"{character_id} [{source}]", fill="white")
    page = offset // batch_size + 1
    canvas.save(OUTPUT / f"page-{page}.jpg", quality=92)
