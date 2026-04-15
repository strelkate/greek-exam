#!/usr/bin/env python3
"""
Import newly generated image_description and dialogue JSON files
for units that already have other exercises in the DB.

Usage:
    python import_new_exercise_types.py [--level a2] [--dry-run]
"""
import argparse
import json
import uuid
from pathlib import Path
import db

DATA_DIR = Path(__file__).parent / "data" / "generated"
NEW_TYPES = ("image_description", "dialogue")


def get_unit_id(level: str, order_index: int) -> int | None:
    row = db.fetchone(
        "SELECT id FROM curriculum_units WHERE level = %s AND order_index = %s",
        (level.upper(), order_index),
    )
    return row["id"] if row else None


def get_max_order_index(unit_id: int) -> int:
    row = db.fetchone(
        "SELECT COALESCE(MAX(order_index), 0) AS max_oi FROM exercises WHERE unit_id = %s",
        (unit_id,),
    )
    return row["max_oi"]


def already_imported(unit_id: int, exercise_type: str) -> bool:
    row = db.fetchone(
        "SELECT COUNT(*) AS n FROM exercises WHERE unit_id = %s AND type = %s",
        (unit_id, exercise_type),
    )
    return row["n"] > 0


def import_file(json_path: Path, unit_id: int, exercise_type: str, run_id: str, dry_run: bool) -> int:
    items = json.loads(json_path.read_text())
    if isinstance(items, dict):
        items = [items]

    start_oi = get_max_order_index(unit_id) + 1
    rows = [
        (unit_id, exercise_type, start_oi + i,
         json.dumps(item), [], True, run_id)
        for i, item in enumerate(items)
    ]

    if dry_run:
        print(f"    [DRY RUN] would insert {len(rows)} rows (order_index starts {start_oi})")
        return len(rows)

    db.executemany(
        """INSERT INTO exercises
               (unit_id, type, order_index, content, audio_paths, is_published, generation_run_id)
           VALUES (%s, %s, %s, %s, %s::text[], %s, %s)""",
        rows,
    )
    return len(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", choices=["a2", "b1"], help="Only import this level")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    run_id = str(uuid.uuid4())
    if not args.dry_run:
        db.execute(
            "INSERT INTO generation_runs (id, description) VALUES (%s, %s)",
            (run_id, f"import image_description+dialogue level={args.level or 'all'}"),
        )

    levels = [args.level] if args.level else ["a2", "b1"]
    total = 0

    for level in levels:
        # Collect all unit indices that have generated files for new types
        for exercise_type in NEW_TYPES:
            for json_path in sorted(DATA_DIR.glob(f"unit_{level}_*_{exercise_type}.json")):
                # parse order_index from filename: unit_a2_03_image_description.json
                parts = json_path.stem.split("_")  # ['unit', 'a2', '03', 'image', 'description']
                order_index = int(parts[2])

                unit_id = get_unit_id(level, order_index)
                if unit_id is None:
                    print(f"  SKIP {json_path.name}: unit {level.upper()}-{order_index} not in DB")
                    continue

                if already_imported(unit_id, exercise_type):
                    print(f"  SKIP {json_path.name}: already imported (unit_id={unit_id})")
                    continue

                print(f"  Importing {json_path.name} → unit_id={unit_id} ...")
                n = import_file(json_path, unit_id, exercise_type, run_id, args.dry_run)
                print(f"    Inserted {n} exercise(s)")
                total += n

    print(f"\nDone. Total inserted: {total}")


if __name__ == "__main__":
    main()
