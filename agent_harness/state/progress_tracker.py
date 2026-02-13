"""Progress tracking for agent sessions."""

from datetime import datetime
from pathlib import Path
from typing import Optional


class ProgressTracker:
    """Manages the progress log file."""

    def __init__(self, progress_file: Path):
        self.progress_file = progress_file
        self._ensure_file()

    def _ensure_file(self):
        """Ensure progress file exists."""
        if not self.progress_file.exists():
            self.progress_file.parent.mkdir(parents=True, exist_ok=True)
            self.progress_file.write_text("# Agent Progress Log\n\n")

    def log_entry(self, message: str, session_id: Optional[str] = None):
        """Add a progress entry."""
        timestamp = datetime.now().isoformat()
        session_prefix = f"[Session {session_id}] " if session_id else ""
        entry = f"\n## {timestamp}\n{session_prefix}{message}\n"

        with open(self.progress_file, "a") as f:
            f.write(entry)

    def log_feature_start(self, feature_id: str, feature_name: str, session_id: Optional[str] = None):
        """Log the start of a feature."""
        message = f"Started working on feature: {feature_id} - {feature_name}"
        self.log_entry(message, session_id)

    def log_feature_complete(self, feature_id: str, feature_name: str, session_id: Optional[str] = None):
        """Log feature completion."""
        message = f"Completed feature: {feature_id} - {feature_name}"
        self.log_entry(message, session_id)

    def log_error(self, error: str, session_id: Optional[str] = None):
        """Log an error."""
        message = f"ERROR: {error}"
        self.log_entry(message, session_id)

    def log_session_start(self, session_id: str):
        """Log session start."""
        message = "=== SESSION START ==="
        self.log_entry(message, session_id)

    def log_session_end(self, session_id: str):
        """Log session end."""
        message = "=== SESSION END ==="
        self.log_entry(message, session_id)

    def read_recent(self, lines: int = 50) -> str:
        """Read recent progress entries."""
        if not self.progress_file.exists():
            return ""

        with open(self.progress_file, "r") as f:
            all_lines = f.readlines()
            recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
            return "".join(recent_lines)

    def read_all(self) -> str:
        """Read all progress entries."""
        if not self.progress_file.exists():
            return ""
        return self.progress_file.read_text()
