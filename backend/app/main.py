from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, curriculum, exercises, vocabulary
from app.routers import mini_test, placement_test
from app.routers import settings as settings_router

app = FastAPI(title="Greek Learning App API", version="0.1.0")

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
app.include_router(placement_test.router)
app.include_router(settings_router.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
