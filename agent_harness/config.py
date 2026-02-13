"""Configuration management for the agent harness."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration settings for the agent harness."""

    # API Configuration
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    MODEL_NAME = os.getenv("MODEL_NAME", "claude-opus-4-6")
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "8192"))

    # Project paths
    PROJECT_ROOT = Path(__file__).parent.parent
    WORKSPACE_DIR = PROJECT_ROOT / "workspace"

    # State files
    PROGRESS_FILE = WORKSPACE_DIR / "claude-progress.txt"
    FEATURE_LIST_FILE = WORKSPACE_DIR / "feature_list.json"
    INIT_SCRIPT = WORKSPACE_DIR / "init.sh"

    # Agent configuration
    MAX_ITERATIONS = 50
    MAX_RETRIES = 3

    @classmethod
    def ensure_workspace(cls):
        """Ensure workspace directory exists."""
        cls.WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def validate(cls):
        """Validate configuration."""
        if not cls.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not set in environment")
