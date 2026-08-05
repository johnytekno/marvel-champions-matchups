"""Measure rated modular-set coverage and identify frequency outliers."""

from __future__ import annotations

import argparse
import json
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path

from docx import Document


PACK_CODES = {"CORE", "GG", "PRINT", "RORS", "KANG", "GMW", "MTS", "HOOD", "SM", "MG", "MOJO", "NEXT", "APOC", "SHIELD", "TT", "CW", "SS", "FNE"}


def normalized(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def clean_set(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"\*+$", "", value.strip())).strip()


def resolve(name: str, universe: set[str]) -> list[str]:
    base = normalized(name)
    manual = {
        "weapon master": "weapons master",
        "the black order": "black order",
        "taskmaster": "taskmaster reg tbolt",
    }
    base = manual.get(base, base)
    matches = [key for key in universe if key == base or key in {
        f"{base} setup", f"{base} reg", f"{base} res", f"{base} tbolt",
        f"{base} mojo", f"{base} expert", f"{base} standard",
    }]
    return sorted(matches)


def origin_map(document: Document, universe: set[str]) -> dict[str, set[str]]:
    origins: dict[str, set[str]] = defaultdict(set)
    for table in document.tables:
        if len(table.columns) < 5:
            continue
        for row in table.rows[1:]:
            cells = [cell.text.strip() for cell in row.cells]
            set_names = [clean_set(line) for line in cells[1].splitlines() if clean_set(line)]
            packs = [re.sub(r"\s+", " ", line).strip().upper() for line in cells[4].splitlines() if line.strip()]
            if len(set_names) != len(packs):
                continue
            for name, pack in zip(set_names, packs):
                for key in resolve(name, universe):
                    if pack == "CORE":
                        origins[key].add("Core")
                    elif pack in PACK_CODES:
                        origins[key].add("Expansion / scenario pack")
                    else:
                        origins[key].add("Hero pack")
    # The guide contains a few pack-cell typos/reprint ambiguities. These four
    # canonical origins keep the category totals exclusive and complete.
    origins["masters of evil"] = {"Core"}
    origins["osborn tech"] = {"Expansion / scenario pack"}
    origins["taskmaster reg tbolt"] = {"Expansion / scenario pack"}
    origins["the inheritors"] = {"Hero pack"}
    return origins


def option_usage(data: dict, include_maximum: bool) -> tuple[Counter[str], Counter[str]]:
    universe = set(data["difficultyTuner"]["moduleRatings"])
    usage: Counter[str] = Counter()
    unresolved: Counter[str] = Counter()

    def add_recipe(names: list[str]) -> None:
        keys: set[str] = set()
        for name in names:
            matches = resolve(name, universe)
            if not matches and not normalized(name).startswith(("choose ", "each hero", "random ", "1 random", "3 random")):
                unresolved[name] += 1
            keys.update(matches)
        usage.update(keys)

    for info in data["encounterModules"].values():
        add_recipe(info.get("sets", []))
    choice_keys = ["easier", "thematic", "harder"] + (["maximum"] if include_maximum else [])
    for choices in data["difficultyTuner"]["scenarios"].values():
        for key in choice_keys:
            choice = choices.get(key)
            if choice:
                add_recipe([item["name"] for item in choice["sets"]])
    return usage, unresolved


def print_ranked(title: str, rows: list[tuple[str, int]], limit: int = 15) -> None:
    print(title)
    for name, count in rows[:limit]:
        print(f"  {count:>3}  {name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("guide", type=Path)
    parser.add_argument("matchups", type=Path)
    args = parser.parse_args()

    data = json.loads(args.matchups.read_text(encoding="utf-8"))
    universe = set(data["difficultyTuner"]["moduleRatings"])
    origins = origin_map(Document(args.guide), universe)
    before, unresolved_before = option_usage(data, False)
    after, unresolved_after = option_usage(data, True)

    print(f"Rated modular-set universe: {len(universe)}")
    print(f"Used before Maximum: {len(before)}/{len(universe)} ({len(before) / len(universe):.1%})")
    print(f"Used with Maximum:   {len(after)}/{len(universe)} ({len(after) / len(universe):.1%}, +{len(after) - len(before)})")
    print(f"Never used: {len(universe - set(after))}")
    print(f"Used once: {sum(1 for count in after.values() if count == 1)}")
    print(f"Additional unique option labels outside the rating matrix: {len(unresolved_after)}")
    frequencies = sorted(after.values())
    quartiles = statistics.quantiles(frequencies, n=4, method="inclusive")
    outlier_threshold = quartiles[2] + 1.5 * (quartiles[2] - quartiles[0])
    outliers = sorted(((name, count) for name, count in after.items() if count > outlier_threshold), key=lambda item: (-item[1], item[0]))
    print(f"Frequency median: {statistics.median(frequencies):g}; Tukey high-outlier threshold: >{outlier_threshold:g}; outliers: {len(outliers)}")
    print()

    for category in ("Core", "Expansion / scenario pack", "Hero pack"):
        category_keys = {key for key in universe if category in origins.get(key, set())}
        used_keys = category_keys & set(after)
        print(f"{category}: {len(used_keys)}/{len(category_keys)} used")
    unmapped_origin = universe - set(origins)
    print(f"Origin not recoverable from guide rows: {len(unmapped_origin)}")
    print()

    top = sorted(after.items(), key=lambda item: (-item[1], item[0]))
    print_ranked("Most repeated rated sets:", top)
    if outliers:
        print_ranked("Statistical high-frequency outliers:", outliers)
    print()
    print_ranked("Never-used rated sets:", [(name, 0) for name in sorted(universe - set(after))], limit=200)
    print()
    unresolved = unresolved_after
    print_ranked("Option labels outside the rating matrix (story/required/nemesis/new material):", sorted(unresolved.items(), key=lambda item: (-item[1], item[0])), limit=200)


if __name__ == "__main__":
    main()
