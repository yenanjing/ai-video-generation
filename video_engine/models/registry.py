"""
Model registry - manages available video generation models.
"""
from typing import Dict, List, Optional
from video_engine.models.adapters.base import BaseModelAdapter
from video_engine.models.adapters.replicate_adapter import ReplicateAdapter
from video_engine.models.schemas import ModelInfo


class ModelRegistry:
    """Registry of available video generation models."""

    def __init__(self):
        """Initialize model registry."""
        self._adapters: Dict[str, BaseModelAdapter] = {}
        self._register_default_models()

    def _register_default_models(self):
        """Register default available models."""
        # Replicate models
        try:
            self.register_adapter(ReplicateAdapter("replicate:svd"))
        except:
            pass

        try:
            self.register_adapter(ReplicateAdapter("replicate:svd-xt"))
        except:
            pass

    def register_adapter(self, adapter: BaseModelAdapter):
        """
        Register a model adapter.

        Args:
            adapter: Model adapter instance
        """
        self._adapters[adapter.model_id] = adapter

    def get_adapter(self, model_id: str) -> Optional[BaseModelAdapter]:
        """
        Get adapter for a model.

        Args:
            model_id: Model identifier

        Returns:
            Model adapter or None if not found
        """
        return self._adapters.get(model_id)

    def list_models(self, available_only: bool = False) -> List[ModelInfo]:
        """
        List all registered models.

        Args:
            available_only: Only return available models

        Returns:
            List of ModelInfo objects
        """
        models = []

        for model_id, adapter in self._adapters.items():
            if available_only and not adapter.is_available():
                continue

            capabilities = adapter.get_capabilities()
            memory_reqs = adapter.get_memory_requirements()

            # Parse model info from ID
            provider, name = model_id.split(":", 1)

            model_info = ModelInfo(
                id=model_id,
                name=name.upper().replace("-", " "),
                description=f"{name} via {provider}",
                provider=provider,
                capabilities=capabilities,
                memory_requirements=memory_reqs,
                is_available=adapter.is_available(),
            )
            models.append(model_info)

        return models

    def get_model_info(self, model_id: str) -> Optional[ModelInfo]:
        """
        Get information about a specific model.

        Args:
            model_id: Model identifier

        Returns:
            ModelInfo or None if not found
        """
        adapter = self.get_adapter(model_id)
        if adapter is None:
            return None

        models = self.list_models()
        for model in models:
            if model.id == model_id:
                return model

        return None

    def is_model_available(self, model_id: str) -> bool:
        """
        Check if a model is available.

        Args:
            model_id: Model identifier

        Returns:
            True if model is available
        """
        adapter = self.get_adapter(model_id)
        return adapter is not None and adapter.is_available()


# Global registry instance
registry = ModelRegistry()
