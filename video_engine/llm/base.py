"""
Base LLM client interface.
"""
from abc import ABC, abstractmethod
from typing import Optional
from video_engine.models.schemas import Storyboard


class BaseLLMClient(ABC):
    """Base class for LLM clients."""

    @abstractmethod
    def generate_storyboard(
        self,
        user_prompt: str,
        max_shots: int = 5,
        style_preferences: Optional[dict] = None,
    ) -> Storyboard:
        """
        Generate a storyboard from user prompt.

        Args:
            user_prompt: User's description of desired video
            max_shots: Maximum number of shots to generate
            style_preferences: Optional style guidance

        Returns:
            Storyboard object with shots
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if LLM client is available (API key configured)."""
        pass
