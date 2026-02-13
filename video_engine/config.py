"""
Configuration for video generation engine.
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class VideoEngineConfig:
    """Video engine configuration."""

    # API Keys
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    REPLICATE_API_TOKEN: str = os.getenv("REPLICATE_API_TOKEN", "")
    HUGGINGFACE_TOKEN: str = os.getenv("HUGGINGFACE_TOKEN", "")

    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    WORKSPACE_DIR: Path = BASE_DIR / "workspace"
    VIDEO_OUTPUT_DIR: Path = WORKSPACE_DIR / "videos"
    VIDEO_UPLOAD_DIR: Path = WORKSPACE_DIR / "uploads"
    JOBS_DIR: Path = WORKSPACE_DIR / "jobs"
    TEMP_DIR: Path = WORKSPACE_DIR / "temp"

    # Video Generation Limits
    MAX_VIDEO_DURATION: int = int(os.getenv("MAX_VIDEO_DURATION", "60"))
    MAX_SHOTS_PER_VIDEO: int = int(os.getenv("MAX_SHOTS_PER_VIDEO", "10"))
    DEFAULT_SHOT_DURATION: float = 3.0
    DEFAULT_FPS: int = 8
    DEFAULT_NUM_FRAMES: int = 81

    # Model Config
    DEFAULT_VIDEO_MODEL: str = os.getenv("DEFAULT_VIDEO_MODEL", "replicate:svd-xt")
    DEFAULT_LLM: str = os.getenv("DEFAULT_LLM", "claude")
    ENABLE_LOCAL_MODELS: bool = os.getenv("ENABLE_LOCAL_MODELS", "false").lower() == "true"
    GPU_MEMORY_FRACTION: float = float(os.getenv("GPU_MEMORY_FRACTION", "0.9"))

    # LLM Config
    LLM_MODEL_CLAUDE: str = "claude-3-5-sonnet-20241022"
    LLM_MODEL_GPT: str = "gpt-4-turbo-preview"
    LLM_MAX_TOKENS: int = 4000
    LLM_TEMPERATURE: float = 0.7

    # API Config (for FastAPI)
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    ENABLE_CORS: bool = os.getenv("ENABLE_CORS", "true").lower() == "true"
    MAX_CONCURRENT_JOBS: int = int(os.getenv("MAX_CONCURRENT_JOBS", "3"))

    # Video Processing
    VIDEO_CODEC: str = "libx264"
    VIDEO_PIXEL_FORMAT: str = "yuv420p"
    VIDEO_CRF: int = 23  # Quality (lower = better, 18-28 is good range)

    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist."""
        for directory in [
            cls.WORKSPACE_DIR,
            cls.VIDEO_OUTPUT_DIR,
            cls.VIDEO_UPLOAD_DIR,
            cls.JOBS_DIR,
            cls.TEMP_DIR,
        ]:
            directory.mkdir(parents=True, exist_ok=True)

    @classmethod
    def validate_api_keys(cls) -> dict:
        """Check which API keys are configured."""
        return {
            "anthropic": bool(cls.ANTHROPIC_API_KEY),
            "openai": bool(cls.OPENAI_API_KEY),
            "replicate": bool(cls.REPLICATE_API_TOKEN),
            "huggingface": bool(cls.HUGGINGFACE_TOKEN),
        }


config = VideoEngineConfig()
