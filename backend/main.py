"""
Nexus Social Platform — FastAPI Backend
========================================
All Gemini AI business logic lives in Python.
Frontend (HTML/CSS/JS) is served as static files — pure UI, no AI logic.

Endpoints:
  POST /api/social/captions          — Generate 3 captions
  POST /api/social/hashtags          — Generate 20 hashtags
  POST /api/social/moderate          — Content moderation + scoring
  POST /api/social/sentiment         — Sentiment analysis
  POST /api/social/growth            — Creator growth strategy
  POST /api/social/predict           — Post performance prediction
  POST /api/social/search            — AI-powered smart search
  POST /api/social/trending-summary  — Trending topic summary
  GET  /health                       — Cloud Run health check
  GET  /*                            — Serve frontend SPA
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from backend.config import get_settings
from backend.routers import social
from backend.services.gemini_service import GeminiService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise Gemini service on startup."""
    logger.info("Starting Nexus Social API...")
    settings = get_settings()
    gemini = GeminiService(settings)
    await gemini.initialise()
    app.state.gemini = gemini
    logger.info(f"Gemini service ready | model: {settings.gemini_model}")
    yield
    logger.info("Shutting down Nexus Social API")


app = FastAPI(
    title="Nexus Social API",
    description="AI-powered social media platform backed by Google Gemini 1.5 Flash",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(social.router, prefix="/api/social", tags=["Social"])


@app.get("/health", tags=["System"])
async def health():
    return {
        "status": "ok",
        "service": "nexus-social",
        "model": get_settings().gemini_model
    }


FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_frontend(full_path: str):
        file_path = FRONTEND_DIR / full_path
        if file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(FRONTEND_DIR / "index.html"))
