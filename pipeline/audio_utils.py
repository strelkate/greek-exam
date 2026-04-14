import hashlib


def audio_filename(text: str) -> str:
    """Return SHA-256(text)[:12].mp3 — deterministic, collision-resistant filename."""
    return hashlib.sha256(text.encode()).hexdigest()[:12] + ".mp3"


def audio_path_for_text(text: str) -> str:
    """Return the public URL path /audio/<filename>.mp3"""
    return f"/audio/{audio_filename(text)}"
