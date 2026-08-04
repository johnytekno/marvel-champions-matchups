"""Import a compact VillainTheory difficulty tuner into matchups.json.

Inputs are public exports downloaded from Modular Champions and VillainTheory's
2026 modular-set spreadsheet. The importer deliberately keeps only three
curated alternatives per battle; the printed/official setup remains canonical.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import openpyxl


BATTLE_CODES = {
    "battle-01": "rhino",
    "battle-02": "klaw",
    "battle-03": "ultron",
    "battle-04": "risky_business",
    "battle-05": "mutagen_formula",
    "battle-06": "wrecking_crew",
    "battle-07": "kang",
    "battle-08": "crossbones",
    "battle-09": "absorbing_man",
    "battle-10": "taskmaster",
    "battle-11": "zola",
    "battle-12": "red_skull",
    "battle-13": "brotherhood_of_badoon",
    "battle-14": "infiltrate_the_museum",
    "battle-15": "escape_the_museum",
    "battle-16": "nebula",
    "battle-17": "ronan",
    "battle-18": "ebony_maw",
    "battle-19": "tower_defense",
    "battle-20": "thanos",
    "battle-21": "hela",
    "battle-22": "loki",
    "battle-23": "the_hood",
    "battle-24": "sandman",
    "battle-25": "venom",
    "battle-26": "mysterio",
    "battle-27": "sinister_six",
    "battle-28": "venom_goblin",
    "battle-29": "magog",
    "battle-30": "spiral",
    "battle-31": "mojo",
    "battle-32": "sabretooth",
    "battle-33": "project_wideawake",
    "battle-34": "master_mold",
    "battle-35": "mansion_attack",
    "battle-36": "magneto_villain",
    "battle-37": "morlock_siege",
    "battle-38": "on_the_run",
    "battle-39": "juggernaut",
    "battle-40": "mister_sinister",
    "battle-41": "stryfe",
    "battle-42": "unus",
    "battle-43": "four_horsemen",
    "battle-44": "apocalypse",
    "battle-45": "dark_beast",
    "battle-46": "en_sabah_nur",
    "battle-47": "black_widow_villain",
    "battle-48": "batroc",
    "battle-49": "m.o.d.o.k.",
    "battle-50": "thunderbolts",
    "battle-51": "baron_zemo",
    "battle-52": "enchantress_villain",
    "battle-53": "god_of_lies",
    "battle-54": "iron_man_leader",
    "battle-55": "captain_marvel_leader",
    "battle-56": "captain_america_leader",
    "battle-57": "spider_woman_leader",
    "battle-58": "she_hulk_leader",
    "battle-59": "vision_leader",
    "battle-60": "bullseye",
    "battle-61": "electro",
    "battle-62": "hammerhead",
    "battle-63": "purple_man",
    "battle-64": "typhoid_mary",
    "battle-65": "kingpin",
}

PLAYER_SHEETS = {
    "solo": "1-Player Mod Sets",
    "two": "2-Player Mod Sets",
    "group": "3-4 Player Mod Sets",
}


def normalized(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def module_ratings(workbook_path: Path) -> dict[str, dict[str, int]]:
    workbook = openpyxl.load_workbook(workbook_path, data_only=True)
    by_player: dict[str, dict[str, int]] = {}
    for player_key, sheet_name in PLAYER_SHEETS.items():
        current_level = None
        ratings: dict[str, int] = {}
        for row in workbook[sheet_name].iter_rows(values_only=True):
            level_cell = str(row[0] or "")
            level_match = re.search(r"Difficulty Level\s+(\d+)", level_cell, re.I)
            if level_match:
                current_level = int(level_match.group(1))
            module_name = str(row[2] or "").strip()
            if current_level and module_name and module_name != "Modular Sets":
                ratings[normalized(module_name)] = current_level
        by_player[player_key] = ratings
    module_names = sorted({name for ratings in by_player.values() for name in ratings})
    return {
        name: {player: by_player[player].get(name) for player in PLAYER_SHEETS}
        for name in module_names
    }


def scenario_signature(record: dict) -> tuple:
    sets = tuple(sorted(item["sets"]["code"] for item in record["scenario_modular_sets"]))
    schemes = tuple(sorted(item["sets"]["code"] for item in record["scenario_main_schemes"]))
    return sets, schemes


def scenario_tags(record: dict) -> set[str]:
    return {item["tags"]["code"] for item in record["scenario_tags"]}


def pick_unique(candidates: list[dict], used: set[tuple]) -> dict | None:
    for candidate in candidates:
        signature = scenario_signature(candidate)
        if signature not in used:
            used.add(signature)
            return candidate
    return None


def choose_records(records: list[dict]) -> dict[str, dict | None]:
    used: set[tuple] = set()

    easier_candidates = sorted(
        (record for record in records if record["difficulty"] < 0),
        key=lambda record: (
            -record["difficulty"],
            "thematic" not in scenario_tags(record),
            len(record["scenario_modular_sets"]),
            record["name"],
        ),
    )
    easier = pick_unique(easier_candidates, used)

    thematic_candidates = sorted(
        (record for record in records if "thematic" in scenario_tags(record)),
        key=lambda record: (
            abs(record["difficulty"]),
            record["difficulty"] < 0,
            len(record["scenario_modular_sets"]),
            record["name"],
        ),
    )
    thematic = pick_unique(thematic_candidates, used)

    harder_candidates = sorted(
        (record for record in records if record["difficulty"] > 0),
        key=lambda record: (
            abs(record["difficulty"] - 2),
            record["difficulty"] > 3,
            "thematic" not in scenario_tags(record),
            len(record["scenario_modular_sets"]),
            record["name"],
        ),
    )
    harder = pick_unique(harder_candidates, used)
    return {"easier": easier, "thematic": thematic, "harder": harder}


def compact_record(record: dict | None) -> dict | None:
    if record is None:
        return None
    sets = [
        {
            "name": item["sets"]["name"],
            "code": item["sets"]["code"],
        }
        for item in record["scenario_modular_sets"]
    ]
    main_schemes = [item["sets"]["name"] for item in record["scenario_main_schemes"]]
    tags = [item["tags"]["name"] for item in record["scenario_tags"]]
    return {
        "id": record["id"],
        "name": record["name"],
        "difficulty": record["difficulty"],
        "sets": sets,
        "mainSchemes": main_schemes,
        "tags": tags,
        "notes": record["notes"].strip(),
        "updated": record["updated_at"][:10],
        "url": f"https://modularchampions.com/scenario/{record['id']}",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("catalog", type=Path)
    parser.add_argument("matrix", type=Path)
    parser.add_argument("matchups", type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    catalog = json.loads(args.catalog.read_text(encoding="utf-8-sig"))
    data = json.loads(args.matchups.read_text(encoding="utf-8"))
    ratings = module_ratings(args.matrix)
    by_villain: dict[str, list[dict]] = {}
    for record in catalog:
        by_villain.setdefault(record["villain_code"], []).append(record)

    scenarios = {
        scenario["id"]: scenario
        for campaign in data["campaigns"]
        for scenario in campaign["scenarios"]
    }
    tuner = {
        "source": {
            "curator": "VillainTheory",
            "catalog": "Modular Champions",
            "catalogUrl": "https://modularchampions.com",
            "recommendationsUrl": "https://docs.google.com/document/d/1AOED4MPkrEGIOAVzV4VJaFAc4bWHfhstOSVTqhSpvHU/edit",
            "matrixUrl": "https://docs.google.com/spreadsheets/d/1nmrzdk9KpIvOWY8eRy5okYFDOmWaxK7UPdkHS_Hlx7k/edit",
            "matrixUpdated": "2026-05",
            "imported": "2026-08-04",
            "method": "Published VillainTheory combinations; closest easier option, near-neutral thematic option, and moderate harder option.",
        },
        "playerCounts": {
            "solo": "Solo",
            "two": "2 players",
            "group": "3–4 players",
        },
        "moduleRatings": ratings,
        "scenarios": {},
    }
    tuner_sources = [
        {
            "label": "VillainTheory — Every Villain’s Best Modular Sets",
            "url": tuner["source"]["recommendationsUrl"],
        },
        {
            "label": "VillainTheory — 2026 Modular Set Difficulty Ranking",
            "url": tuner["source"]["matrixUrl"],
        },
        {
            "label": "Modular Champions public scenario catalog",
            "url": tuner["source"]["catalogUrl"],
        },
    ]

    missing = []
    for battle_id, villain_code in BATTLE_CODES.items():
        if battle_id not in scenarios or villain_code not in by_villain:
            missing.append((battle_id, villain_code))
            continue
        choices = choose_records(by_villain[villain_code])
        tuner["scenarios"][battle_id] = {
            "villainCode": villain_code,
            **{key: compact_record(record) for key, record in choices.items()},
        }

    if missing:
        raise SystemExit(f"Unmapped battles: {missing}")

    for battle_id, choices in tuner["scenarios"].items():
        labels = []
        for key in ("easier", "thematic", "harder"):
            choice = choices[key]
            labels.append(f"{key}={choice['name']} ({choice['difficulty']:+d})" if choice else f"{key}=unavailable")
        print(f"{battle_id} {scenarios[battle_id]['title']}: " + "; ".join(labels))

    if args.apply:
        data["difficultyTuner"] = tuner
        data["updated"] = "2026-08-04"
        known_source_urls = {source["url"] for source in data.get("sources", [])}
        data.setdefault("sources", []).extend(
            source for source in tuner_sources if source["url"] not in known_source_urls
        )
        args.matchups.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Updated {args.matchups}")


if __name__ == "__main__":
    main()
