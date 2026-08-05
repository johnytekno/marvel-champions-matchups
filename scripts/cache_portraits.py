import io
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "images" / "portraits"
OUT.mkdir(parents=True, exist_ok=True)
DATA = json.loads((ROOT / "matchups.json").read_text(encoding="utf-8"))
API = "https://marvel.fandom.com/api.php"
HEADERS = {"User-Agent": "MarvelChampionsMatchupPlanner/1.0 (offline fan project)"}
SEARCH_OVERRIDES = {
    "spider-man-peter": "Peter Parker Earth-616",
    "ghost-spider": "Gwen Stacy Earth-65",
    "spider-man-miles": "Miles Morales Earth-1610",
    "thor": "Thor Odinson Earth-616",
    "captain-america": "Steve Rogers Earth-616",
    "hulk": "Bruce Banner Earth-616",
    "black-widow": "Natasha Romanoff Earth-616",
    "hawkeye": "Clint Barton Earth-616",
    "war-machine": "James Rhodes Earth-616",
    "falcon": "Sam Wilson Earth-616",
    "spectrum": "Monica Rambeau Earth-616",
    "gamora": "Gamora Earth-616",
    "nova": "Richard Rider Earth-616",
    "spdr": "Peni Parker Earth-14512",
    "wolverine": "James Howlett Earth-616",
    "bishop": "Lucas Bishop Earth-616",
    "cyclops": "Scott Summers Earth-616",
    "storm": "Ororo Munroe Earth-616",
    "colossus": "Piotr Rasputin Earth-616",
    "magneto-hero": "Max Eisenhardt Earth-616",
    "magneto-villain": "Max Eisenhardt Earth-616",
    "x-23": "Laura Kinney Earth-616",
    "phoenix": "Jean Grey Earth-616",
    "nick-fury": "Nicholas Joseph Fury Earth-616",
    "ms-marvel": "Kamala Khan Earth-616",
    "quicksilver": "Pietro Maximoff Earth-616",
    "luke-cage": "Luke Cage Earth-616",
    "green-goblin": "Norman Osborn Earth-616",
    "red-skull": "Johann Schmidt Earth-616",
    "sandman": "Flint Marko Earth-616",
    "mojo": "Mojo Earth-616",
    "sabretooth": "Victor Creed Earth-616",
    "sentinel": "Sentinel Earth-616",
    "mister-sinister": "Nathaniel Essex Earth-616",
    "stryfe": "Stryfe Earth-4935",
    "black-widow-yelena": "Yelena Belova Earth-616",
    "atlas": "Erik Josten Earth-616",
    "meteorite": "Karla Sofen Earth-616",
    "techno": "Norbert Ebersol Earth-616",
    "enchantress": "Amora Earth-616",
    "captain-america-leader": "Steve Rogers Earth-616",
}
TITLE_OVERRIDES = {
    "spider-man-peter": "Peter Parker (Earth-616)",
    "spider-man-miles": "Miles Morales (Earth-1610)/Gallery",
    "she-hulk": "Jennifer Walters (Earth-616)",
    "she-hulk-leader": "Jennifer Walters (Earth-616)",
    "norman-osborn": "Norman Osborn (Earth-616)",
    "green-goblin": "Green Goblin",
    "thor": "Thor Odinson (Earth-616)",
    "iron-man": "Anthony Stark (Earth-616)",
    "iron-man-leader": "Anthony Stark (Earth-616)",
    "falcon": "Samuel Wilson (Earth-616)",
    "gamora": "Gamora Zen Whoberi Ben Titan (Earth-616)",
    "wolverine": "James Howlett (Earth-616)",
    "cyclops": "Scott Summers (Earth-616)",
    "mojo": "Mojo (Earth-616)",
}
FILE_OVERRIDES = {
    "spider-man-miles": "https://static.wikia.nocookie.net/marveldatabase/images/d/d1/Miles_Morales_Spider-Man_Vol_1_25_Greg_Horn_Art_and_Bird_City_Comics_Exclusive_Variant_C.jpg/revision/latest/scale-to-width-down/500?cb=20210428204343",
    "she-hulk": "https://static.wikia.nocookie.net/marveldatabase/images/5/53/Jennifer_Walters_%28Earth-616%29_from_Sensational_She-Hulk_Vol_2_9_001.jpg/revision/latest/scale-to-width-down/500?cb=20240818212144",
    "she-hulk-leader": "https://static.wikia.nocookie.net/marveldatabase/images/5/53/Jennifer_Walters_%28Earth-616%29_from_Sensational_She-Hulk_Vol_2_9_001.jpg/revision/latest/scale-to-width-down/500?cb=20240818212144",
    "norman-osborn": "https://static.wikia.nocookie.net/marveldatabase/images/a/ac/What_If%3F_Dark_Reign_Vol_1_1_Textless.jpg/revision/latest/scale-to-width-down/500?cb=20101210183345",
    "captain-america": "https://static.wikia.nocookie.net/marveldatabase/images/b/bf/Steven_Rogers_%28Earth-201163%29_from_Captain_America_This_Is_Captain_America_001.jpg/revision/latest/scale-to-width-down/500?cb=20260109191327",
    "captain-america-leader": "https://static.wikia.nocookie.net/marveldatabase/images/b/bf/Steven_Rogers_%28Earth-201163%29_from_Captain_America_This_Is_Captain_America_001.jpg/revision/latest/scale-to-width-down/500?cb=20260109191327",
    "hulk": "https://static.wikia.nocookie.net/marveldatabase/images/1/1a/Bruce_Banner_%28Earth-616%29_from_Incredible_Hulk_Vol_6_1_001.jpeg/revision/latest/scale-to-width-down/500?cb=20250623175330",
    "black-widow": "https://static.wikia.nocookie.net/marveldatabase/images/e/e6/Natasha_Romanoff_%28Earth-78149%29_from_Marvel_Strike_Force_001.jpg/revision/latest/scale-to-width-down/500?cb=20190712230819",
    "hawkeye": "https://static.wikia.nocookie.net/marveldatabase/images/5/55/Clint_Barton_%28Earth-1610%29_from_Ultimate_Hawkeye_Vol_1_1_Kubert_Variant_Cover.png/revision/latest/scale-to-width-down/500?cb=20110615030330",
    "war-machine": "https://static.wikia.nocookie.net/marveldatabase/images/2/22/James_Rhodes_%28Earth-616%29_from_War_Machine_Vol_2_2_0001.jpg/revision/latest/scale-to-width-down/500?cb=20220729230144",
    "spectrum": "https://static.wikia.nocookie.net/marveldatabase/images/0/0f/Monica_Rambeau_%28Earth-616%29_from_Astonishing_Avengers_Infinity_Comic_Vol_1_1_001.jpg/revision/latest/scale-to-width-down/500?cb=20250127153353",
    "venom-hero": "https://static.wikia.nocookie.net/marveldatabase/images/4/4f/Venom_Vol_4_19_Codex_Variant_Textless.jpg/revision/latest/scale-to-width-down/500?cb=20200823015905",
    "adam-warlock": "https://static.wikia.nocookie.net/marveldatabase/images/b/b2/Adam_Warlock_from_Marvel_Snap_004.jpg/revision/latest/scale-to-width-down/500?cb=20241111101320",
    "bishop": "https://static.wikia.nocookie.net/marveldatabase/images/a/a5/Lucas_Bishop_%28Earth-31393%29_from_X-Men_%2797_Season_1_001.jpg/revision/latest/scale-to-width-down/500?cb=20240222042319",
    "colossus": "https://static.wikia.nocookie.net/marveldatabase/images/9/97/Piotr_Rasputin_%28Earth-TRN1507%29_from_X-Men_Genetix_001.png/revision/latest?cb=20250106071317",
    "magneto-hero": "https://static.wikia.nocookie.net/marveldatabase/images/1/11/Max_Eisenhardt_%28Earth-616%29_from_X-Men_Vol_2_1_cover.png/revision/latest?cb=20090102052225",
    "magneto-villain": "https://static.wikia.nocookie.net/marveldatabase/images/1/11/Max_Eisenhardt_%28Earth-616%29_from_X-Men_Vol_2_1_cover.png/revision/latest?cb=20090102052225",
    "x-23": "https://static.wikia.nocookie.net/marveldatabase/images/8/8a/Generation_X-23_Vol_1_6_Hellfire_Costume_Swap_Variant.jpg/revision/latest/scale-to-width-down/500?cb=20260726020949",
    "domino": "https://static.wikia.nocookie.net/marveldatabase/images/4/4f/Domino_Vol_3_1_ComicXposure_Exclusive_Variant_Textless.jpg/revision/latest/scale-to-width-down/500?cb=20180703235530",
    "luke-cage": "https://static.wikia.nocookie.net/marveldatabase/images/1/12/Luke_Cage_%28Earth-51156%29_from_Marvel_Future_Fight_001.jpg/revision/latest?cb=20160702231221",
    "red-skull": "https://static.wikia.nocookie.net/marveldatabase/images/c/c9/Johann_Shmidt_%28Earth-18191%29_from_Red_Skull_Vol_2_1_0001.jpg/revision/latest/scale-to-width-down/500?cb=20180702002612",
    "loki": "https://static.wikia.nocookie.net/marveldatabase/images/d/da/Loki_Laufeyson_%28Earth-199999%29_from_Thor_%28film%29_Concept_Art_0001.jpg/revision/latest?cb=20120113072505",
    "loki-god-of-lies": "https://static.wikia.nocookie.net/marveldatabase/images/d/da/Loki_Laufeyson_%28Earth-199999%29_from_Thor_%28film%29_Concept_Art_0001.jpg/revision/latest?cb=20120113072505",
    "venom-villain": "https://static.wikia.nocookie.net/marveldatabase/images/b/b7/Carnage_Vol_3_13_Venom_The_Other_Variant.jpg/revision/latest/scale-to-width-down/500?cb=20230608202337",
    "mojo": "https://static.wikia.nocookie.net/marveldatabase/images/a/a1/Mojo_%28Mojoverse%29_from_X-Men_Black_-_Mojo_Vol_1_1_003.jpg/revision/latest/scale-to-width-down/500?cb=20181013190140",
    "sentinel": "https://static.wikia.nocookie.net/marveldatabase/images/f/f5/Sentinels_%28Earth-616%29_Mark_X_from_Cable_and_X-Force_Vol_1_15.jpg/revision/latest?cb=20131002020031",
    "harpoon": "https://static.wikia.nocookie.net/marveldatabase/images/4/4e/Kodiak_Noatak_%28Earth-616%29_from_Official_Handbook_of_the_Marvel_Universe_Update_%2789_Vol_1_5.jpg/revision/latest?cb=20130607221519",
    "unus": "https://static.wikia.nocookie.net/marveldatabase/images/2/2a/Gunther_Bain_%28Earth-58163%29_from_Civil_War_House_of_M_Vol_1_2_001.jpg/revision/latest?cb=20200516020935",
    "horseman-war": "https://static.wikia.nocookie.net/marveldatabase/images/7/7c/Horseman_of_War_%28Earth-41578%29_from_X-Men-_Apocalypse_001.png/revision/latest?cb=20160701043937",
    "horseman-famine": "https://static.wikia.nocookie.net/marveldatabase/images/9/95/Famine_%28First_Horsemen%29_%28Earth-616%29_from_X_of_Swords_Creation_Vol_1_1_001.jpg/revision/latest/scale-to-width-down/500?cb=20200925012408",
    "black-widow-yelena": "https://static.wikia.nocookie.net/marveldatabase/images/e/e1/Yelena_Belova_%28Earth-616%29_from_Web_of_Black_Widow_Vol_1_3_001.jpg/revision/latest?cb=20191108064231",
    "modok": "https://static.wikia.nocookie.net/marveldatabase/images/2/21/Super-Villain_Team-Up_MODOK%27s_11_Vol_1_1.jpg/revision/latest/scale-to-width-down/500?cb=20210610024833",
    "atlas": "https://static.wikia.nocookie.net/marveldatabase/images/4/46/Erik_Josten_%28Earth-616%29_from_Thunderbolts_Vol_4_2_002.png/revision/latest/scale-to-width-down/500?cb=20160608174810",
    "baron-zemo": "https://static.wikia.nocookie.net/marveldatabase/images/c/c0/Helmut_Zemo_%28Earth-51156%29_from_Marvel_Future_Fight_001.jpg/revision/latest/scale-to-width-down/500?cb=20200506074751",
    "hammerhead": "https://static.wikia.nocookie.net/marveldatabase/images/c/c2/Hammerhead_%28Joseph%29_%28Earth-616%29_from_Amazing_Spider-Man_Vol_3_17.1_001.jpg/revision/latest?cb=20150425030948",
    "purple-man": "https://static.wikia.nocookie.net/marveldatabase/images/f/f2/New_Thunderbolts_Vol_1_10_Textless.jpg/revision/latest?cb=20100210173134",
}
CENTER_OVERRIDES = {
    "venom-villain": (0.5, 0.68),
    "modok": (0.5, 0.68),
}
CROP_OVERRIDES = {
    "spider-man-miles": (0.03, 0.12, 0.97, 0.70),
    "spectrum": (0.0, 0.0, 0.91, 1.0),
    "x-23": (0.0, 0.08, 1.0, 1.0),
    "venom-villain": (0.08, 0.16, 0.92, 0.92),
    "modok": (0.05, 0.26, 0.95, 0.82),
    "purple-man": (0.29, 0.15, 0.71, 0.50),
}


def fetch_json(url):
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def portrait_url(name):
    if name.startswith("title:"):
        query = urllib.parse.urlencode(
            {
                "action": "query",
                "titles": name.removeprefix("title:"),
                "prop": "pageimages",
                "piprop": "thumbnail",
                "pithumbsize": 500,
                "format": "json",
                "origin": "*",
            }
        )
        payload = fetch_json(f"{API}?{query}")
        page = next(iter(payload.get("query", {}).get("pages", {}).values()), {})
        return page.get("thumbnail", {}).get("source"), page.get("title")
    query = urllib.parse.urlencode(
        {
            "action": "query",
            "generator": "search",
            "gsrsearch": f"{name} Earth-616",
            "gsrnamespace": 0,
            "gsrlimit": 4,
            "prop": "pageimages",
            "piprop": "thumbnail",
            "pithumbsize": 500,
            "format": "json",
            "origin": "*",
        }
    )
    payload = fetch_json(f"{API}?{query}")
    pages = list(payload.get("query", {}).get("pages", {}).values())
    pages.sort(
        key=lambda page: (
            "earth-616" not in page.get("title", "").lower(),
            page.get("index", 999),
        )
    )
    for page in pages:
        thumbnail = page.get("thumbnail", {}).get("source")
        if thumbnail:
            return thumbnail, page.get("title", "")
    return None, None


def save_portrait(character_id, url):
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=30) as response:
        image = Image.open(io.BytesIO(response.read())).convert("RGB")
    if character_id in CROP_OVERRIDES:
        left, top, right, bottom = CROP_OVERRIDES[character_id]
        width, height = image.size
        image = image.crop(
            (width * left, height * top, width * right, height * bottom)
        )
    fitted = ImageOps.fit(
        image,
        (240, 300),
        method=Image.Resampling.LANCZOS,
        centering=CENTER_OVERRIDES.get(character_id, (0.5, 0.28)),
    )
    fitted.save(OUT / f"{character_id}.webp", "WEBP", quality=78, method=6)


manifest_path = OUT / "sources.json"
requested_ids = set(sys.argv[1:])
unknown_ids = requested_ids - set(DATA["characters"])
if unknown_ids:
    raise SystemExit("Unknown character ids: " + ", ".join(sorted(unknown_ids)))
character_items = [
    item
    for item in DATA["characters"].items()
    if not requested_ids or item[0] in requested_ids
]
results = (
    json.loads(manifest_path.read_text(encoding="utf-8"))
    if requested_ids and manifest_path.exists()
    else {}
)
for index, (character_id, meta) in enumerate(character_items, start=1):
    target = OUT / f"{character_id}.webp"
    if target.exists() and character_id not in SEARCH_OVERRIDES and character_id not in TITLE_OVERRIDES and character_id not in FILE_OVERRIDES:
        results[character_id] = {"status": "cached"}
        continue
    try:
        if character_id in FILE_OVERRIDES:
            url, title = FILE_OVERRIDES[character_id], "curated file"
        else:
            search = f"title:{TITLE_OVERRIDES[character_id]}" if character_id in TITLE_OVERRIDES else SEARCH_OVERRIDES.get(character_id, meta["display"])
            url, title = portrait_url(search)
        if not url:
            raise RuntimeError("no thumbnail found")
        save_portrait(character_id, url)
        results[character_id] = {"status": "ok", "source": title, "url": url}
        print(f"{index:03}/{len(character_items)} {character_id}: {title}")
    except Exception as error:
        results[character_id] = {"status": "failed", "error": str(error)}
        print(f"{index:03}/{len(character_items)} {character_id}: FAILED {error}")
    time.sleep(0.08)

manifest_path.write_text(
    json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8"
)
ok = sum(item["status"] in {"ok", "cached"} for item in results.values())
print(f"Cached {ok}/{len(results)} portraits; refreshed {len(character_items)}")
