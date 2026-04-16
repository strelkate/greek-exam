#!/usr/bin/env python3
"""Generate MP3 audio for exercises via gTTS (dev/SQLite version)."""
import asyncio
import hashlib
import json
from pathlib import Path

from gtts import gTTS

AUDIO_DIR = Path(__file__).parent.parent / "pipeline" / "audio"


def audio_filename(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:12] + ".mp3"


def synthesise(text: str) -> str:
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    filename = audio_filename(text)
    dest = AUDIO_DIR / filename
    if not dest.exists():
        tts = gTTS(text=text, lang="el", slow=False)
        tts.save(str(dest))
    return f"/audio/{filename}"


def extract_texts(ex_type: str, content: dict) -> list[str]:
    if ex_type == "true_false":
        return [content.get("text", "")]
    if ex_type == "matching":
        return [p["left"] for p in content.get("pairs", [])]
    if ex_type == "multiple_choice":
        return [content.get("question", "")]
    if ex_type == "fill_blank":
        return [content.get("text_template", "").replace("___", "").strip()]
    if ex_type == "dialogue":
        return [line["text"].replace("___", "").strip()
                for line in content.get("dialogue_lines", [])]
    return []


async def main():
    from app.database import engine
    from sqlalchemy import text

    async with engine.begin() as conn:
        rows = (await conn.execute(text("SELECT id, type, content, audio_paths FROM exercises"))).fetchall()
        total_audio = 0

        for row in rows:
            ex_id, ex_type, raw_content, existing = row
            content = raw_content if isinstance(raw_content, dict) else json.loads(raw_content)
            texts = extract_texts(ex_type.lower(), content)
            audio_paths = [synthesise(t) for t in texts if t]

            existing_parsed = json.loads(existing) if isinstance(existing, str) else (existing or [])
            if audio_paths and audio_paths != existing_parsed:
                await conn.execute(
                    text("UPDATE exercises SET audio_paths = :paths WHERE id = :id"),
                    {"paths": json.dumps(audio_paths), "id": ex_id},
                )
                total_audio += len(audio_paths)
                print(f"  Exercise {ex_id} ({ex_type}): {len(audio_paths)} audio(s)")

        print(f"Done: {total_audio} audio files generated/linked.")


if __name__ == "__main__":
    asyncio.run(main())
