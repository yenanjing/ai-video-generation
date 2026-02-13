"""
Claude LLM client for storyboard generation.
"""
import json
import uuid
from datetime import datetime
from typing import Optional
from anthropic import Anthropic

from video_engine.llm.base import BaseLLMClient
from video_engine.models.schemas import Storyboard, Shot
from video_engine.config import config


STORYBOARD_SYSTEM_PROMPT = """You are a professional film director and cinematographer. Your task is to create detailed storyboards for AI video generation.

Given a user's video description, you will:
1. Break down the concept into individual shots (typically 3-7 shots)
2. For each shot, provide:
   - A clear description of what happens
   - A detailed text prompt optimized for AI video generation
   - Camera movement and angle
   - Duration (typically 2-4 seconds per shot)
   - Motion intensity (0.0 = static, 1.0 = high motion)

Guidelines:
- Keep shots short (2-4 seconds) for best AI generation quality
- Each shot should have ONE clear focus/action
- Use descriptive, visual language in prompts
- Specify camera movements (pan, zoom, dolly, static)
- Consider continuity between shots
- Optimize prompts for AI (avoid complex compositions)

Output ONLY valid JSON in this exact format:
{
  "title": "Brief title for the video",
  "shots": [
    {
      "sequence_number": 1,
      "duration_seconds": 3.0,
      "description": "Human-readable description",
      "text_prompt": "Detailed prompt for AI video generation, cinematic, high quality",
      "camera_movement": "static/pan/zoom/dolly",
      "camera_angle": "eye_level/low_angle/high_angle/birds_eye",
      "motion_intensity": 0.5
    }
  ],
  "style": {
    "mood": "calm/energetic/dramatic",
    "color_palette": "warm/cool/vibrant",
    "lighting": "natural/dramatic/soft"
  }
}"""


class ClaudeClient(BaseLLMClient):
    """Claude LLM client for storyboard generation."""

    def __init__(self):
        """Initialize Claude client."""
        if not config.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not configured")
        self.client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
        self.model = config.LLM_MODEL_CLAUDE

    def is_available(self) -> bool:
        """Check if Claude is available."""
        return bool(config.ANTHROPIC_API_KEY)

    def generate_storyboard(
        self,
        user_prompt: str,
        max_shots: int = 5,
        style_preferences: Optional[dict] = None,
    ) -> Storyboard:
        """
        Generate storyboard using Claude.

        Args:
            user_prompt: User's video description
            max_shots: Maximum shots to generate
            style_preferences: Optional style guidance

        Returns:
            Storyboard object
        """
        # Build user message
        user_message = f"""Create a storyboard for this video concept:

"{user_prompt}"

Requirements:
- Generate between 3 and {max_shots} shots
- Each shot should be 2-4 seconds long
- Total video duration should be under {config.MAX_VIDEO_DURATION} seconds
"""

        if style_preferences:
            user_message += f"\nStyle preferences: {json.dumps(style_preferences, indent=2)}"

        user_message += "\n\nProvide ONLY the JSON output, no additional text."

        # Call Claude API
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=config.LLM_MAX_TOKENS,
                temperature=config.LLM_TEMPERATURE,
                system=STORYBOARD_SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": user_message,
                    }
                ],
            )

            # Extract JSON from response
            response_text = response.content[0].text.strip()

            # Try to extract JSON if wrapped in markdown code blocks
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                response_text = "\n".join(lines[1:-1])  # Remove first and last lines
                if response_text.startswith("json"):
                    response_text = response_text[4:].strip()

            storyboard_data = json.loads(response_text)

            # Convert to Storyboard object
            return self._parse_storyboard(
                storyboard_data=storyboard_data,
                user_prompt=user_prompt,
            )

        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse Claude response as JSON: {e}\nResponse: {response_text}")
        except Exception as e:
            raise RuntimeError(f"Failed to generate storyboard with Claude: {e}")

    def _parse_storyboard(self, storyboard_data: dict, user_prompt: str) -> Storyboard:
        """Parse storyboard data into Storyboard object."""
        storyboard_id = f"storyboard_{uuid.uuid4().hex[:8]}"

        # Parse shots
        shots = []
        for shot_data in storyboard_data.get("shots", []):
            shot_id = f"shot_{uuid.uuid4().hex[:8]}"

            shot = Shot(
                id=shot_id,
                sequence_number=shot_data.get("sequence_number", len(shots) + 1),
                duration_seconds=shot_data.get("duration_seconds", config.DEFAULT_SHOT_DURATION),
                description=shot_data.get("description", ""),
                text_prompt=shot_data.get("text_prompt", shot_data.get("description", "")),
                camera_movement=shot_data.get("camera_movement", "static"),
                camera_angle=shot_data.get("camera_angle", "eye_level"),
                motion_intensity=shot_data.get("motion_intensity", 0.5),
                model_id=config.DEFAULT_VIDEO_MODEL,
                num_frames=config.DEFAULT_NUM_FRAMES,
                fps=config.DEFAULT_FPS,
            )
            shots.append(shot)

        # Sort by sequence number
        shots.sort(key=lambda s: s.sequence_number)

        # Calculate total duration
        total_duration = sum(s.duration_seconds for s in shots)

        storyboard = Storyboard(
            id=storyboard_id,
            title=storyboard_data.get("title", "Generated Video"),
            user_prompt=user_prompt,
            shots=shots,
            style=storyboard_data.get("style", {}),
            total_duration_seconds=total_duration,
            shot_count=len(shots),
            generated_at=datetime.now(),
            generated_by="claude",
        )

        return storyboard
