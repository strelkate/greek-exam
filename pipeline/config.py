import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def _require(key: str) -> str:
    val = os.getenv(key)
    if not val:
        raise RuntimeError(f"Required env var {key!r} is not set")
    return val


def load_config() -> dict:
    """Load and validate all required config. Returns dict of config values."""
    return {
        "ANTHROPIC_API_KEY": _require("ANTHROPIC_API_KEY"),
        "DATABASE_URL": _require("DATABASE_URL"),
        "AUDIO_DIR": Path(_require("AUDIO_DIR")),
    }


ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
DATABASE_URL: str = os.getenv("DATABASE_URL", "")
AUDIO_DIR: Path = Path(os.getenv("AUDIO_DIR", "audio"))
