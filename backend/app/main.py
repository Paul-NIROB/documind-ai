"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import documents, health, me   # replaces the old import line
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title="DocuMind AI API", version="0.1.0")

# CORS lets the browser frontend call this API; only our own frontend origin is allowed
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(me.router)
app.include_router(documents.router)   # add below the existing include_router lines