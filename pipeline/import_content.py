#!/usr/bin/env python3
# pipeline/import_content.py
"""
Import generated JSON files into PostgreSQL.

Usage:
    python import_content.py [--level a1] [--unit-index 1]
    python import_content.py --placement
    python import_content.py              # imports everything in data/generated/

All content is inserted with is_published=False.
"""
import argparse
import json
import re
import uuid
from pathlib import Path
import db
from curriculum_data import UNITS

DATA_DIR = Path(__file__).parent / "data" / "generated"


def parse_unit_filename(filename: str) -> dict | None:
    """
    Returns metadata dict for a generated file, or None if unrecognised.
    unit_a1_01_true_false.json → {"level": "a1", "order_index": 1, "exercise_type": "true_false"}
    placement.json → {"placement": True}
    """
    if filename == "placement.json":
        return {"placement": True}
    m = re.match(r"^unit_([a-b][0-9])_(\d+)_(\w+)\.json$", filename)
    if m:
        return {
            "level": m.group(1),
            "order_index": int(m.group(2)),
            "exercise_type": m.group(3),
        }
    return None


def build_exercise_rows(
    unit_id: int,
    exercise_type: str,
    items: list[dict],
    generation_run_id: str,
    start_order_index: int,
) -> list[dict]:
    rows = []
    for i, item in enumerate(items):
        rows.append({
            "unit_id": unit_id,
            "type": exercise_type,
            "order_index": start_order_index + i,
            "content": item,
            "audio_paths": [],
            "is_published": False,
            "generation_run_id": generation_run_id,
        })
    return rows


def build_vocab_rows(unit_id: int, unit: dict, generation_run_id: str) -> list[dict]:
    rows = []
    for v in unit["vocab"]:
        rows.append({
            "unit_id": unit_id,
            "word_gr": v["word_gr"],
            "word_ru": v["word_ru"],
            "example_gr": v.get("example_gr"),
            "audio_path": None,
            "order_index": v["order_index"],
            "generation_run_id": generation_run_id,
        })
    return rows


def get_or_create_unit_id(level: str, order_index: int) -> int:
    """Return existing curriculum_units.id or insert and return new id."""
    level_db = level.upper()  # DB stores uppercase to match backend LevelEnum ("A1"/"A2"/"B1")
    row = db.fetchone(
        "SELECT id FROM curriculum_units WHERE level = %s AND order_index = %s",
        (level_db, order_index),
    )
    if row:
        return row["id"]
    unit_data = next(
        (u for u in UNITS if u["level"] == level and u["order_index"] == order_index),
        None,
    )
    if not unit_data:
        raise RuntimeError(f"Unit {level} #{order_index} not found in curriculum_data")
    row = db.fetchone(
        """INSERT INTO curriculum_units (level, title, order_index, is_published)
           VALUES (%s, %s, %s, FALSE) RETURNING id""",
        (level_db, f"{unit_data['title_ru']} — {unit_data['title_gr']}", order_index),
    )
    return row["id"]


def create_generation_run(run_id: str, description: str) -> None:
    db.execute(
        "INSERT INTO generation_runs (id, description) VALUES (%s, %s)",
        (run_id, description),
    )


def insert_exercises(rows: list[dict]) -> None:
    sql = """
        INSERT INTO exercises
            (unit_id, type, order_index, content, audio_paths, is_published, generation_run_id)
        VALUES (%s, %s, %s, %s, %s::text[], %s, %s)
    """
    db.executemany(sql, [
        (r["unit_id"], r["type"], r["order_index"],
         json.dumps(r["content"]), r["audio_paths"],
         r["is_published"], r["generation_run_id"])
        for r in rows
    ])


def insert_vocab(rows: list[dict]) -> None:
    sql = """
        INSERT INTO vocabulary_cards
            (unit_id, word_gr, word_ru, example_gr, audio_path, order_index, generation_run_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    db.executemany(sql, [
        (r["unit_id"], r["word_gr"], r["word_ru"], r["example_gr"],
         r["audio_path"], r["order_index"], r["generation_run_id"])
        for r in rows
    ])


def insert_placement_questions(items: list[dict]) -> None:
    sql = """
        INSERT INTO placement_test_questions
            (type, content, correct_answer, order_index, is_active)
        VALUES (%s, %s, %s, %s, TRUE)
    """
    db.executemany(sql, [
        (item["type"], json.dumps(item["content"]), json.dumps(item["correct_answer"]), i + 1)
        for i, item in enumerate(items)
    ])


def import_unit(level: str, order_index: int, run_id: str) -> None:
    print(f"Importing unit {level.upper()}-{order_index}...")
    unit_id = get_or_create_unit_id(level, order_index)

    # Idempotency guard: skip if this unit already has content
    existing = db.fetchone(
        "SELECT COUNT(*) as n FROM vocabulary_cards WHERE unit_id = %s", (unit_id,)
    )
    if existing["n"] > 0:
        print(f"  SKIP: content already imported for unit_id={unit_id}")
        return

    unit_data = next(u for u in UNITS if u["level"] == level and u["order_index"] == order_index)

    # Import vocabulary cards
    vocab_rows = build_vocab_rows(unit_id, unit_data, run_id)
    insert_vocab(vocab_rows)
    print(f"  Imported {len(vocab_rows)} vocab cards")

    # Import exercises from generated JSON files
    exercise_files = sorted(DATA_DIR.glob(f"unit_{level}_{order_index:02d}_*.json"))
    order_counter = 1
    for f in exercise_files:
        meta = parse_unit_filename(f.name)
        if not meta or "exercise_type" not in meta:
            continue
        items = json.loads(f.read_text())
        rows = build_exercise_rows(unit_id, meta["exercise_type"], items, run_id, order_counter)
        insert_exercises(rows)
        order_counter += len(rows)
        print(f"  Imported {len(rows)} {meta['exercise_type']} exercises from {f.name}")


def import_placement(run_id: str) -> None:
    path = DATA_DIR / "placement.json"
    if not path.exists():
        print("SKIP: placement.json not found")
        return
    items = json.loads(path.read_text())
    insert_placement_questions(items)
    print(f"Imported {len(items)} placement test questions")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", choices=["a1", "a2", "b1"])
    parser.add_argument("--unit-index", type=int)
    parser.add_argument("--placement", action="store_true")
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args()

    run_id = args.run_id or str(uuid.uuid4())
    create_generation_run(run_id, f"import level={args.level} unit={args.unit_index}")
    print(f"Generation run ID: {run_id}")

    if args.placement:
        import_placement(run_id)
    elif args.level and args.unit_index:
        import_unit(args.level, args.unit_index, run_id)
    else:
        # Import everything
        for unit in UNITS:
            import_unit(unit["level"], unit["order_index"], run_id)
        import_placement(run_id)

    print("Import complete.")


if __name__ == "__main__":
    main()
