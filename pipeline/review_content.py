#!/usr/bin/env python3
# pipeline/review_content.py
"""
Display unit content in the terminal for human review before publishing.

Usage:
    python review_content.py --unit-id <db_id>
    python review_content.py --level a1 --unit-index 1
"""
import argparse
import json
import db


def display_unit(unit_id: int) -> None:
    unit = db.fetchone(
        "SELECT id, level, title, order_index FROM curriculum_units WHERE id = %s",
        (unit_id,),
    )
    if not unit:
        raise SystemExit(f"Unit {unit_id} not found")

    print(f"\n{'='*60}")
    print(f"Unit: {unit['title']}  (level={unit['level']}, order={unit['order_index']}, id={unit_id})")
    print(f"{'='*60}")

    # Vocab cards
    vocab = db.fetchall(
        "SELECT order_index, word_gr, word_ru, example_gr, audio_path "
        "FROM vocabulary_cards WHERE unit_id = %s ORDER BY order_index",
        (unit_id,),
    )
    print(f"\n── Vocabulary ({len(vocab)} cards) ──────────────────────────")
    for v in vocab:
        audio_status = "✓" if v["audio_path"] else "✗"
        print(f"  [{v['order_index']:2d}] {v['word_gr']} → {v['word_ru']}  [audio: {audio_status}]")
        if v["example_gr"]:
            print(f"       ex: {v['example_gr']}")

    # Exercises
    exercises = db.fetchall(
        "SELECT id, type, order_index, content, audio_paths, is_published "
        "FROM exercises WHERE unit_id = %s ORDER BY order_index",
        (unit_id,),
    )
    print(f"\n── Exercises ({len(exercises)} total) ──────────────────────")
    for ex in exercises:
        published = "PUBLISHED" if ex["is_published"] else "draft"
        audio_count = len(ex["audio_paths"]) if ex["audio_paths"] else 0
        print(f"\n  [{ex['order_index']}] type={ex['type']}  id={ex['id']}  [{published}]  audio={audio_count} file(s)")
        content = ex["content"] if isinstance(ex["content"], dict) else json.loads(ex["content"])
        print(f"  {json.dumps(content, ensure_ascii=False, indent=4)[:400]}")


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--unit-id", type=int)
    group.add_argument("--level", choices=["a1", "a2", "b1"])
    parser.add_argument("--unit-index", type=int)
    args = parser.parse_args()

    if args.unit_id:
        display_unit(args.unit_id)
    elif args.level and args.unit_index:
        row = db.fetchone(
            "SELECT id FROM curriculum_units WHERE level = %s AND order_index = %s",
            (args.level, args.unit_index),
        )
        if not row:
            raise SystemExit(f"Unit {args.level}-{args.unit_index} not found in DB")
        display_unit(row["id"])
    else:
        raise SystemExit("Provide --unit-id or both --level and --unit-index")


if __name__ == "__main__":
    main()
