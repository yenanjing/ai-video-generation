"""
Storyboard generator - manages LLM clients.
"""
from typing import Optional
from video_engine.llm.base import BaseLLMClient
from video_engine.llm.claude_client import ClaudeClient
from video_engine.models.schemas import Storyboard
from video_engine.config import config


class StoryboardGenerator:
    """Manages storyboard generation using available LLMs."""

    def __init__(self, llm: str = "claude"):
        """
        Initialize storyboard generator.

        Args:
            llm: LLM to use ("claude" or "openai")
        """
        self.llm_name = llm
        self.client = self._get_client(llm)

    def _get_client(self, llm: str) -> BaseLLMClient:
        """Get LLM client."""
        if llm == "claude":
            return ClaudeClient()
        elif llm == "openai":
            # Will implement OpenAI later
            raise NotImplementedError("OpenAI client not yet implemented")
        else:
            raise ValueError(f"Unknown LLM: {llm}")

    def generate(
        self,
        user_prompt: str,
        max_shots: int = 5,
        style_preferences: Optional[dict] = None,
    ) -> Storyboard:
        """
        Generate storyboard from user prompt.

        Args:
            user_prompt: User's video description
            max_shots: Maximum number of shots
            style_preferences: Optional style guidance

        Returns:
            Storyboard object
        """
        if not self.client.is_available():
            raise RuntimeError(f"{self.llm_name} client not available (check API key)")

        return self.client.generate_storyboard(
            user_prompt=user_prompt,
            max_shots=max_shots,
            style_preferences=style_preferences,
        )

    @staticmethod
    def get_available_llms() -> list:
        """Get list of available LLM providers."""
        available = []

        # Check Claude
        try:
            claude = ClaudeClient()
            if claude.is_available():
                available.append("claude")
        except:
            pass

        return available
