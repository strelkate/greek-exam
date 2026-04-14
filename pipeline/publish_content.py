#!/usr/bin/env python3
# pipeline/publish_content.py
"""
Publish a unit: set is_published=True for its exercises and the unit itself.
Also supports rollback by generation_run_id.

Usage:
    python publish_content.py --unit-id <db_id>
    python publish_content.py --level a1 --unit-index 1
    python publish_content.py --rollback --run-id <generation_run_id>
"""
import argparse
import db


def publish_unit(unit_id: int) -> None:
    unit = db.fetchone(
        "SELECT id, title, is_published FROM curriculum_units WHERE id = %s",
        (unit_id,),
    )
    if not unit:
        raise SystemExit(f"Unit {unit_id} not found")
    if unit["is_published"]:
        print(f"Unit {unit_id} ({unit['title']}) is already published.")
        return

    # Warn if exercises have no audio
    missing_audio = db.fetchall(
        "SELECT id, type FROM exercises WHERE unit_id = %s AND audio_paths = '{}'",
        (unit_id,),
    )
    if missing_audio:
        print(f"WARNING: {len(missing_audio)} exercise(s) have no audio. Run generate_audio.py first.")
        print(f"  Exercise IDs without audio: {[r['id'] for r in missing_audio]}")
        confirm = input("Continue anyway? [y/N] ").strip().lower()
        if confirm != "y":
            raise SystemExit("Aborted.")

    db.execute("UPDATE exercises SET is_published = TRUE WHERE unit_id = %s", (unit_id,))
    db.execute("UPDATE curriculum_units SET is_published = TRUE WHERE id = %s", (unit_id,))

    ex_count = db.fetchone(
        "SELECT COUNT(*) as n FROM exercises WHERE unit_id = %s", (unit_id,)
    )["n"]
    vocab_count = db.fetchone(
        "SELECT COUNT(*) as n FROM vocabulary_cards WHERE unit_id = %s", (unit_id,)
    )["n"]
    print(f"Published unit {unit_id} ({unit['title']}): {ex_count} exercises, {vocab_count} vocab cards.")


def rollback_run(run_id: str) -> None:
    """Un-publish all content from a generation run (set is_published=False)."""
    db.execute(
        "UPDATE exercises SET is_published = FALSE WHERE generation_run_id = %s",
        (run_id,),
    )
    db.execute(
        "UPDATE curriculum_units SET is_published = FALSE "
        "WHERE id IN (SELECT DISTINCT unit_id FROM exercises WHERE generation_run_id = %s)",
        (run_id,),
    )
    print(f"Rolled back generation run {run_id}.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--unit-id", type=int)
    parser.add_argument("--level", choices=["a1", "a2", "b1"])
    parser.add_argument("--unit-index", type=int)
    parser.add_argument("--rollback", action="store_true")
    parser.add_argument("--run-id", help="generation_run_id for rollback")
    args = parser.parse_args()

    if args.rollback:
        if not args.run_id:
            raise SystemExit("--run-id is required with --rollback")
        rollback_run(args.run_id)
    elif args.unit_id:
        publish_unit(args.unit_id)
    elif args.level and args.unit_index:
        row = db.fetchone(
            "SELECT id FROM curriculum_units WHERE level = %s AND order_index = %s",
            (args.level, args.unit_index),
        )
        if not row:
            raise SystemExit(f"Unit {args.level}-{args.unit_index} not in DB")
        publish_unit(row["id"])
    else:
        raise SystemExit("Provide --unit-id, or --level + --unit-index, or --rollback + --run-id")


if __name__ == "__main__":
    main()
