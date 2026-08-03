import io
import json
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads(
    (ROOT / "images" / "portraits" / "ffg_sources.json").read_text(
        encoding="utf-8"
    )
)
DESTINATION = ROOT / "images" / "ffg_originals"
DESTINATION.mkdir(parents=True, exist_ok=True)
HEADERS = {"User-Agent": "MarvelChampionsMatchupPlanner/1.0"}


def fetch(url):
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=45) as response:
        return response.read()


resolved = [
    (character_id, details)
    for character_id, details in MANIFEST.items()
    if details.get("status") == "ok"
]

for index, (character_id, details) in enumerate(resolved, start=1):
    target = DESTINATION / f"{character_id}.png"
    if target.exists():
        print(f"{index:03}/{len(resolved)} {character_id}: cached")
        continue
    raw = fetch(details["source"])
    image = Image.open(io.BytesIO(raw))
    image.verify()
    target.write_bytes(raw)
    print(f"{index:03}/{len(resolved)} {character_id}: downloaded")

print(f"Cached {len(resolved)} original FFG card scans")
