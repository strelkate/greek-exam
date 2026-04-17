#!/usr/bin/env python3
# pipeline/generate_audio.py
"""
Generate MP3 audio for exercises and vocabulary cards via gTTS.

Usage:
    python generate_audio.py --unit-id <db_id>
    python generate_audio.py --all

For exercises, synthesises audio for each relevant text field.
For vocab cards, synthesises word_gr.
Skips files that already exist (idempotent).
Updates audio_paths (exercises) and audio_path (vocabulary_cards) in DB.
"""
import argparse
import json
from pathlib import Path
from gtts import gTTS
import config
import db
from audio_utils import audio_filename, audio_path_for_text


def ensure_audio_dir() -> Path:
    config.AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    return config.AUDIO_DIR


def synthesise(text: str, dest_dir: Path) -> str:
    """Generate MP3 for text if not already present. Return /audio/<file>.mp3."""
    filename = audio_filename(text)
    dest = dest_dir / filename
    if not dest.exists():
        tts = gTTS(text=text, lang="el", slow=False)
        tts.save(str(dest))
    return f"/audio/{filename}"


def _extract_texts_for_exercise(ex_type: str, content: dict) -> list[str]:
    """Return the list of texts that need audio for a given exercise type."""
    if ex_type == "true_false":
        return [content["text"]]
    elif ex_type == "matching":
        return [p["left"] for p in content["pairs"]]
    elif ex_type == "multiple_choice":
        return [content["question"].replace("___", "").strip()]
    elif ex_type == "fill_blank":
        return [content["text_template"].replace("___", "").strip()]
    elif ex_type == "image_description":
        return [content["description_text"]]
    elif ex_type == "dialogue":
        return [line["text"].replace("___", "").strip()
                for line in content["dialogue_lines"]]
    return []


def process_exercises_for_unit(unit_id: int, dest_dir: Path) -> None:
    rows = db.fetchall(
        "SELECT id, type, content FROM exercises WHERE unit_id = %s AND is_published = FALSE",
        (unit_id,),
    )
    for row in rows:
        ex_id = row["id"]
        ex_type = row["type"]
        content = row["content"] if isinstance(row["content"], dict) else json.loads(row["content"])
        texts = _extract_texts_for_exercise(ex_type, content)
        audio_paths = [synthesise(t, dest_dir) for t in texts if t]

        if ex_type == "dialogue":
            # Update audio_path per line in content JSON
            for i, line in enumerate(content["dialogue_lines"]):
                if i < len(audio_paths):
                    line["audio_path"] = audio_paths[i]
            db.execute(
                "UPDATE exercises SET audio_paths = %s::text[], content = %s WHERE id = %s",
                (audio_paths, json.dumps(content), ex_id),
            )
        else:
            db.execute(
                "UPDATE exercises SET audio_paths = %s::text[] WHERE id = %s",
                (audio_paths, ex_id),
            )
        print(f"  Exercise {ex_id} ({ex_type}): {len(audio_paths)} audio file(s)")


def process_vocab_for_unit(unit_id: int, dest_dir: Path) -> None:
    rows = db.fetchall(
        "SELECT id, word_gr FROM vocabulary_cards WHERE unit_id = %s AND audio_path IS NULL",
        (unit_id,),
    )
    for row in rows:
        path = synthesise(row["word_gr"], dest_dir)
        db.execute(
            "UPDATE vocabulary_cards SET audio_path = %s WHERE id = %s",
            (path, row["id"]),
        )
    print(f"  {len(rows)} vocab card(s) processed")


def process_unit(unit_id: int) -> None:
    dest_dir = ensure_audio_dir()
    print(f"Processing unit_id={unit_id}...")
    process_exercises_for_unit(unit_id, dest_dir)
    process_vocab_for_unit(unit_id, dest_dir)


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--unit-id", type=int)
    group.add_argument("--all", action="store_true")
    args = parser.parse_args()

    if args.unit_id:
        process_unit(args.unit_id)
    else:
        rows = db.fetchall("SELECT id FROM curriculum_units ORDER BY level, order_index")
        for row in rows:
            process_unit(row["id"])

    print("Audio generation complete.")


if __name__ == "__main__":
    main()
