from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import engine, patch_sqlite_types, _is_sqlite
from app.routers import auth, curriculum, exercises, vocabulary
from app.routers import mini_test
from app.routers import settings as settings_router
from app.routers import sync


@asynccontextmanager
async def lifespan(app: FastAPI):
    if _is_sqlite(settings.database_url):
        import app.models  # noqa: F401 — register all models with Base
        from app.database import Base
        patch_sqlite_types(Base)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="Greek Learning App API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(curriculum.router)
app.include_router(exercises.router)
app.include_router(vocabulary.router)
app.include_router(mini_test.router)
app.include_router(settings_router.router)
app.include_router(sync.router)


# Serve generated audio files
# In Docker: mounted at /audio via volume. In local dev: relative to repo root.
import os as _os
_audio_dir = Path(_os.environ.get("AUDIO_DIR", "")) or Path(__file__).parent.parent.parent / "pipeline" / "audio"
if _audio_dir.exists():
    app.mount("/audio", StaticFiles(directory=str(_audio_dir)), name="audio")


@app.get("/health")
async def health():
    return {"status": "ok"}
