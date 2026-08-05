import json
import sys
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
compare_sources = "--compare" in sys.argv
requested_ids = [argument for argument in sys.argv[1:] if not argument.startswith("--")]
OUTPUT = ROOT / ("_crop_compare" if compare_sources else "_crop_audit")
OUTPUT.mkdir(exist_ok=True)

columns = 2 if compare_sources else 5
batch_size = 16 if compare_sources else 40
tile_width = 520 if compare_sources else 200
tile_height = 260 if compare_sources else 250
ids = requested_ids or list(DATA["characters"])

for offset in range(0, len(ids), batch_size):
    batch = ids[offset : offset + batch_size]
    canvas = Image.new(
        "RGB",
        (columns * tile_width, ceil(len(batch) / columns) * tile_height),
        "#111722",
    )
    draw = ImageDraw.Draw(canvas)
    for index, character_id in enumerate(batch):
        portrait = Image.open(
            ROOT / "images" / "portraits" / f"{character_id}.webp"
        ).convert("RGB")
        x = (index % columns) * tile_width
        y = (index // columns) * tile_height
        if compare_sources:
            original = Image.open(
                ROOT / "images" / "ffg_originals" / f"{character_id}.png"
            ).convert("RGB")
            width, height = original.size
            source_art = original.crop(
                (
                    round(width * 0.225),
                    round(height * 0.145),
                    round(width * 0.93),
                    round(height * 0.545),
                )
            )
            source_art.thumbnail((340, 210), Image.Resampling.LANCZOS)
            canvas.paste(source_art, (x + 5, y + 35))
            canvas.paste(
                portrait.resize((160, 200), Image.Resampling.LANCZOS),
                (x + 350, y + 35),
            )
        else:
            canvas.paste(
                portrait.resize((160, 200), Image.Resampling.LANCZOS),
                (x + 5, y + 28),
            )
        source = (
            "FFG"
            if MANIFEST.get(character_id, {}).get("status") == "ok"
            else "fallback"
        )
        draw.text((x + 5, y + 7), f"{character_id} [{source}]", fill="white")
    page = offset // batch_size + 1
    canvas.save(OUTPUT / f"page-{page}.jpg", quality=92)
