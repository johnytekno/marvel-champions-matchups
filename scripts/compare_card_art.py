import sys
from math import ceil
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps


paths = [Path(argument) for argument in sys.argv[1:]]
if not paths:
    raise SystemExit("Pass one or more card-image paths.")

columns = min(5, len(paths))
tile_width = 210
tile_height = 270
canvas = Image.new(
    "RGB",
    (columns * tile_width, ceil(len(paths) / columns) * tile_height),
    "#111722",
)
draw = ImageDraw.Draw(canvas)

for index, path in enumerate(paths):
    image = Image.open(path).convert("RGB")
    width, height = image.size
    art = image.crop(
        (
            round(width * 0.225),
            round(height * 0.145),
            round(width * 0.93),
            round(height * 0.545),
        )
    )
    preview = ImageOps.fit(
        art,
        (180, 225),
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.35),
    )
    x = (index % columns) * tile_width
    y = (index // columns) * tile_height
    draw.text((x + 10, y + 8), path.stem, fill="white")
    canvas.paste(preview, (x + 10, y + 32))

output = Path("_crop_audit") / "candidate-card-art.jpg"
output.parent.mkdir(exist_ok=True)
canvas.save(output, quality=92)
print(output.resolve())
