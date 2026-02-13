"""
Model management endpoints.
"""
from fastapi import APIRouter, HTTPException

from video_engine.models.registry import registry
from video_api.schemas.responses import ModelListResponse


router = APIRouter()


@router.get("/models", response_model=ModelListResponse)
async def list_models(available_only: bool = False):
    """
    List all registered video generation models.

    Args:
        available_only: If True, only return models that are currently available

    Returns:
        List of models with their capabilities and status
    """
    models = registry.list_models(available_only=available_only)

    return ModelListResponse(
        models=models,
        total=len(models),
    )


@router.get("/models/{model_id}")
async def get_model_info(model_id: str):
    """
    Get detailed information about a specific model.

    Args:
        model_id: Model identifier (e.g., "replicate:svd-xt")

    Returns:
        Model information including capabilities and requirements
    """
    model = registry.get_model_info(model_id)

    if model is None:
        raise HTTPException(
            status_code=404,
            detail=f"Model not found: {model_id}"
        )

    return model
