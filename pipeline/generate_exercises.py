#!/usr/bin/env python3
# pipeline/generate_exercises.py
"""
Generate exercises for a curriculum unit via Claude API.

Usage:
    python generate_exercises.py --level <a1|a2|b1> --unit-index <N>

Output:
    data/generated/unit_{level}_{order_index:02d}_{type}.json  — one file per exercise type

Exercise counts per unit:
    A1: 2 true_false + 1 matching + 2 multiple_choice + 1 fill_blank (6 total)
    A2/B1: above + 1 image_description + 1 dialogue (8 total)
"""
import argparse
import json
from pathlib import Path
from curriculum_data import UNITS
from generators.claude_client import call_claude
from schemas.exercise_schemas import validate_exercise_content

PROMPTS_DIR = Path(__file__).parent / "prompts"
DATA_DIR = Path(__file__).parent / "data" / "generated"


def load_prompt(exercise_type: str) -> str:
    return (PROMPTS_DIR / f"{exercise_type}.txt").read_text()


def build_vocab_list(vocab: list[dict]) -> str:
    return ", ".join(f"{v['word_gr']} ({v['word_ru']})" for v in vocab)


def generate_for_type(unit: dict, exercise_type: str, count: int) -> list[dict]:
    prompt_template = load_prompt(exercise_type)
    prompt = prompt_template.format(
        level=unit["level"].upper(),
        unit_topic=f"{unit['title_ru']} / {unit['title_gr']}",
        vocabulary_list=build_vocab_list(unit["vocab"]),
        count=count,
        # placement_test.txt extras (unused here, safe to pass)
        count_tf=0, count_mc=0, count_fb=0,
    )
    raw = call_claude(prompt)
    # Claude may return a list or a single dict; normalise to list
    items = raw if isinstance(raw, list) else [raw]
    # Validate each item
    for item in items:
        validate_exercise_content(exercise_type, item)
    return items


# exercise plan per level
_EXERCISE_PLAN_A1 = [
    ("true_false", 2),
    ("matching", 1),
    ("multiple_choice", 2),
    ("fill_blank", 1),
]
_EXERCISE_PLAN_A2_B1 = _EXERCISE_PLAN_A1 + [
    ("image_description", 1),
    ("dialogue", 1),
]


def get_exercise_plan(level: str) -> list[tuple[str, int]]:
    return _EXERCISE_PLAN_A1 if level == "a1" else _EXERCISE_PLAN_A2_B1


def generate_unit(unit: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    level = unit["level"]
    idx = unit["order_index"]
    plan = get_exercise_plan(level)

    for exercise_type, count in plan:
        out_path = DATA_DIR / f"unit_{level}_{idx:02d}_{exercise_type}.json"
        if out_path.exists():
            print(f"  SKIP {out_path.name} (already exists)")
            continue

        print(f"  Generating {exercise_type} (count={count})...")
        items = generate_for_type(unit, exercise_type, count)
        out_path.write_text(json.dumps(items, ensure_ascii=False, indent=2))
        print(f"  Saved {out_path.name}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", required=True, choices=["a1", "a2", "b1"])
    parser.add_argument("--unit-index", required=True, type=int,
                        help="1-based order_index within the level")
    args = parser.parse_args()

    matches = [u for u in UNITS
               if u["level"] == args.level and u["order_index"] == args.unit_index]
    if not matches:
        raise SystemExit(f"Unit not found: level={args.level}, order_index={args.unit_index}")

    unit = matches[0]
    print(f"Generating exercises for: {unit['title_ru']} ({unit['title_gr']})")
    generate_unit(unit)
    print("Done.")


if __name__ == "__main__":
    main()
