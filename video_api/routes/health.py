"""
Health check endpoints.
"""
from datetime import datetime
from fastapi import APIRouter

from video_engine.config import config
from video_engine.models.registry import registry
from video_api.schemas.responses import HealthResponse


router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Check API health and configuration status.

    Returns information about:
    - API status
    - Version
    - API keys configuration
    - Available models count
    """
    # Check API keys
    api_keys = config.validate_api_keys()

    # Count available models
    models = registry.list_models(available_only=True)
    models_count = len(models)

    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now(),
        api_keys_configured=api_keys,
        models_available=models_count,
    )
