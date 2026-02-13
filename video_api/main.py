"""
FastAPI application for AI video generation.

This API provides REST endpoints and WebSocket support for video generation.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from video_engine.config import config
from video_api.routes import jobs, models, upload, health, websocket_route


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print("🚀 Starting AI Video Generation API...")
    config.ensure_directories()
    print(f"✓ Workspace directories initialized")
    print(f"✓ API running on http://{config.API_HOST}:{config.API_PORT}")

    yield

    # Shutdown
    print("👋 Shutting down AI Video Generation API...")


# Create FastAPI application
app = FastAPI(
    title="AI Video Generation API",
    description="REST API for AI-powered video generation with LLM storyboarding",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# CORS middleware
if config.ENABLE_CORS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify exact origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(jobs.router, prefix="/api/v1", tags=["Jobs"])
app.include_router(models.router, prefix="/api/v1", tags=["Models"])
app.include_router(upload.router, prefix="/api/v1", tags=["Upload"])
app.include_router(websocket_route.router, tags=["WebSocket"])


# Serve generated videos as static files
try:
    app.mount(
        "/videos",
        StaticFiles(directory=str(config.VIDEO_OUTPUT_DIR)),
        name="videos"
    )
except RuntimeError:
    # Directory might not exist yet
    pass


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "AI Video Generation API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/api/v1/health",
        "repository": "https://github.com/yenanjing/ai-video-generation"
    }


def run_server(
    host: str = None,
    port: int = None,
    reload: bool = False,
):
    """
    Run the FastAPI server.

    Args:
        host: Host to bind to (defaults to config.API_HOST)
        port: Port to bind to (defaults to config.API_PORT)
        reload: Enable auto-reload for development
    """
    host = host or config.API_HOST
    port = port or config.API_PORT

    uvicorn.run(
        "video_api.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )


if __name__ == "__main__":
    run_server(reload=True)
