"""Add sourced Maximum recipes from VillainTheory's public DOCX guide.

The normal catalog importer intentionally aims the Harder slot near +2. This
companion importer reads the source guide's highest published difficulty row
and adds a fifth choice only when it is distinct and strictly harder.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from docx import Document


SOURCE_URL = "https://docs.google.com/document/d/1AOED4MPkrEGIOAVzV4VJaFAc4bWHfhstOSVTqhSpvHU/edit"
UPDATED = "2026-08-04"

# The guide includes reference-only tables between the actual villain tables,
# so each battle is pinned to its validated source-table index.
BATTLE_TABLES = {
    "battle-01": (1,), "battle-02": (2,), "battle-03": (3,),
    "battle-04": (4,), "battle-05": (5,), "battle-06": (6,),
    "battle-07": (12,), "battle-08": (7,), "battle-09": (8,),
    "battle-10": (9,), "battle-11": (10,), "battle-12": (11,),
    "battle-13": (13,), "battle-14": (14,), "battle-15": (15,),
    "battle-16": (16,), "battle-17": (17,), "battle-18": (18,),
    "battle-19": (19,), "battle-20": (20,), "battle-21": (21,),
    "battle-22": (22,), "battle-23": (23, 24), "battle-24": (25,),
    "battle-25": (26,), "battle-26": (27,), "battle-27": (28,),
    "battle-28": (29,), "battle-29": (35,), "battle-30": (36,),
    "battle-31": (37,), "battle-32": (30,), "battle-33": (31,),
    "battle-34": (32,), "battle-35": (33,), "battle-36": (34,),
    "battle-37": (38,), "battle-38": (39,), "battle-39": (40,),
    "battle-40": (41,), "battle-41": (42,), "battle-42": (43,),
    "battle-43": (44,), "battle-44": (45,), "battle-45": (46,),
    "battle-46": (47,), "battle-47": (48,), "battle-48": (49,),
    "battle-49": (50,), "battle-50": (51,), "battle-51": (53,),
    "battle-52": (54,), "battle-53": (55,), "battle-54": (58,),
    "battle-55": (59,), "battle-56": (60,), "battle-57": (61,),
    "battle-58": (62,), "battle-59": (63,), "battle-60": (64,),
    "battle-61": (65,), "battle-62": (66,), "battle-63": (67,),
    "battle-64": (68,), "battle-65": (73,),
}

EXPECTED_HEADINGS = {
    "battle-01": "RHINO", "battle-02": "KLAW", "battle-03": "ULTRON",
    "battle-04": "RISKY BUSINESS", "battle-05": "MUTAGEN FORMULA",
    "battle-06": "WRECKING CREW", "battle-07": "KANG",
    "battle-08": "CROSSBONES", "battle-09": "ABSORBING MAN",
    "battle-10": "TASKMASTER", "battle-11": "ZOLA", "battle-12": "RED SKULL",
    "battle-13": "BROTHERHOOD OF BADOON", "battle-14": "INFILTRATE THE MUSEUM",
    "battle-15": "ESCAPE THE MUSEUM", "battle-16": "NEBULA",
    "battle-17": "RONAN THE ACCUSER", "battle-18": "EBONY MAW",
    "battle-19": "TOWER DEFENSE", "battle-20": "THANOS", "battle-21": "HELA",
    "battle-22": "LOKI", "battle-23": "THE HOOD", "battle-24": "SANDMAN",
    "battle-25": "VENOM", "battle-26": "MYSTERIO", "battle-27": "THE SINISTER SIX",
    "battle-28": "VENOM GOBLIN", "battle-29": "MAGOG", "battle-30": "SPIRAL",
    "battle-31": "MOJO", "battle-32": "SABRETOOTH",
    "battle-33": "PROJECT WIDEAWAKE", "battle-34": "MASTER MOLD",
    "battle-35": "MANSION ATTACK", "battle-36": "MAGNETO",
    "battle-37": "MORLOCK SIEGE", "battle-38": "ON THE RUN",
    "battle-39": "JUGGERNAUT", "battle-40": "MISTER SINISTER",
    "battle-41": "STRYFE", "battle-42": "UNUS", "battle-43": "FOUR HORSEMEN",
    "battle-44": "APOCALYPSE", "battle-45": "DARK BEAST",
    "battle-46": "EN SABAH NUR", "battle-47": "BLACK WIDOW",
    "battle-48": "BATROC", "battle-49": "M.O.D.O.K.",
    "battle-50": "THUNDERBOLTS", "battle-51": "BARON ZEMO",
    "battle-52": "ENCHANTRESS", "battle-53": "GOD OF LIES",
    "battle-54": "IRON MAN", "battle-55": "CAPTAIN MARVEL",
    "battle-56": "CAPTAIN AMERICA", "battle-57": "SPIDER-WOMAN",
    "battle-58": "SHE-HULK", "battle-59": "VISION", "battle-60": "BULLSEYE",
    "battle-61": "ELECTRO", "battle-62": "HAMMERHEAD", "battle-63": "PURPLE MAN",
    "battle-64": "TYPHOID MARY", "battle-65": "KINGPIN",
}


@dataclass
class Recipe:
    name: str
    difficulty: int
    sets: list[str]
    packs: list[str]
    main_schemes: list[str]
    notes: str
    recommended: bool
    order: int


def normalized(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def clean_set(value: str) -> str:
    return clean_text(re.sub(r"\*+$", "", value.strip()))


def split_lines(value: str) -> list[str]:
    return [clean_set(line) for line in value.splitlines() if clean_set(line)]


def parse_name_and_schemes(value: str) -> tuple[str, list[str]]:
    lines = [clean_text(line) for line in value.splitlines() if clean_text(line)]
    scheme_start = next((i for i, line in enumerate(lines) if re.search(r"\([12]B\)$", line, re.I)), len(lines))
    raw_name = " ".join(lines[:scheme_start])
    name = clean_text(raw_name.replace("✔️", "").replace("✔", ""))
    schemes = [clean_text(re.sub(r"\s*\([12]B\)$", "", line, flags=re.I)) for line in lines[scheme_start:]]
    return name, schemes


def table_headings(document: Document) -> dict[int, str]:
    headings: dict[int, str] = {}
    current = ""
    table_index = 0
    namespace = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    for child in document.element.body.iterchildren():
        if child.tag.endswith("}p"):
            text = "".join(node.text or "" for node in child.iter() if node.tag.endswith("}t")).strip()
            properties = child.find(namespace + "pPr")
            style = properties.find(namespace + "pStyle") if properties is not None else None
            style_name = style.get(namespace + "val", "") if style is not None else ""
            if text and style_name in {"Heading3", "Heading 3"}:
                current = text
        elif child.tag.endswith("}tbl"):
            headings[table_index] = current
            table_index += 1
    return headings


def recipes_from_table(document: Document, table_index: int) -> list[Recipe]:
    table = document.tables[table_index]
    if len(table.columns) < 5 or "difficulty" not in normalized(table.rows[0].cells[2].text):
        raise ValueError(f"Table {table_index} is not a five-column difficulty table")
    recipes: list[Recipe] = []
    for order, row in enumerate(table.rows[1:]):
        cells = [cell.text.strip() for cell in row.cells]
        difficulty_match = re.search(r"([+-]?\d+)", cells[2])
        if not difficulty_match:
            continue
        name, main_schemes = parse_name_and_schemes(cells[0])
        sets = split_lines(cells[1])
        packs = [clean_text(line) for line in cells[4].splitlines() if clean_text(line)]
        if not name or not sets:
            continue
        recipes.append(Recipe(
            name=name,
            difficulty=int(difficulty_match.group(1)),
            sets=sets,
            packs=packs,
            main_schemes=main_schemes,
            notes=clean_text(cells[3]),
            recommended="✔" in cells[0],
            order=order,
        ))
    return recipes


def signature(sets: list[str], schemes: list[str]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    return tuple(sorted(normalized(item) for item in sets)), tuple(sorted(normalized(item) for item in schemes))


def existing_usage(data: dict) -> Counter[str]:
    usage: Counter[str] = Counter()
    for info in data.get("encounterModules", {}).values():
        usage.update(normalized(name) for name in info.get("sets", []) if not name.lower().startswith(("choose ", "each ")))
    for choices in data["difficultyTuner"]["scenarios"].values():
        for key in ("easier", "thematic", "harder"):
            choice = choices.get(key)
            if choice:
                usage.update(normalized(item["name"]) for item in choice["sets"])
    return usage


def compact(recipe: Recipe, battle_id: str) -> dict:
    return {
        "id": f"villaintheory-maximum-{battle_id}",
        "name": recipe.name,
        "difficulty": recipe.difficulty,
        "sets": [{"name": name, "code": normalized(name).replace(" ", "_")} for name in recipe.sets],
        "mainSchemes": recipe.main_schemes,
        "tags": ["Maximum challenge"],
        "notes": recipe.notes,
        "updated": UPDATED,
        "url": SOURCE_URL,
        "source": "VillainTheory source guide",
        "packs": recipe.packs,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("guide", type=Path)
    parser.add_argument("matchups", type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    document = Document(args.guide)
    data = json.loads(args.matchups.read_text(encoding="utf-8"))
    headings = table_headings(document)
    usage = existing_usage(data)
    scenarios = data["difficultyTuner"]["scenarios"]
    added = 0

    for battle_id, table_indices in BATTLE_TABLES.items():
        expected = EXPECTED_HEADINGS[battle_id]
        for table_index in table_indices:
            if expected not in headings.get(table_index, "").upper():
                raise ValueError(f"{battle_id}: expected {expected!r} at table {table_index}, found {headings.get(table_index)!r}")
        candidates = [recipe for index in table_indices for recipe in recipes_from_table(document, index)]
        highest = max(recipe.difficulty for recipe in candidates)
        harder = scenarios[battle_id].get("harder")
        harder_difficulty = harder["difficulty"] if harder else 0
        existing_signatures = {
            signature([item["name"] for item in choice["sets"]], choice["mainSchemes"])
            for key in ("easier", "thematic", "harder")
            if (choice := scenarios[battle_id].get(key))
        }
        eligible = [
            recipe for recipe in candidates
            if recipe.difficulty == highest
            and recipe.difficulty > harder_difficulty
            and signature(recipe.sets, recipe.main_schemes) not in existing_signatures
        ]
        if not eligible:
            scenarios[battle_id]["maximum"] = None
            continue

        # Equal-difficulty ties favor new/rare modular sets, then VillainTheory's
        # check-marked recommendation, then the later source-guide entry.
        chosen = max(eligible, key=lambda recipe: (
            sum(1 for name in recipe.sets if usage[normalized(name)] == 0),
            -sum(usage[normalized(name)] for name in recipe.sets),
            recipe.recommended,
            recipe.order,
        ))
        scenarios[battle_id]["maximum"] = compact(chosen, battle_id)
        usage.update(normalized(name) for name in chosen.sets)
        added += 1
        print(f"{battle_id}: {chosen.name} ({chosen.difficulty:+d}) — {', '.join(chosen.sets)}")

    data["difficultyTuner"]["source"]["method"] = (
        "Published VillainTheory combinations: closest easier option, near-neutral thematic option, "
        "moderate harder option, and a distinct source-guide maximum only when rated above harder."
    )
    if args.apply:
        args.matchups.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Updated {args.matchups} with {added} Maximum recipes")
    else:
        print(f"Would add {added} Maximum recipes; rerun with --apply to write them")


if __name__ == "__main__":
    main()
