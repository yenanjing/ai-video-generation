"""Tests for progress tracker."""

import pytest
import tempfile
from pathlib import Path
from agent_harness.state.progress_tracker import ProgressTracker


def test_progress_tracker_creation():
    """Test creating a progress tracker."""
    with tempfile.TemporaryDirectory() as tmpdir:
        progress_file = Path(tmpdir) / "progress.txt"
        pt = ProgressTracker(progress_file)

        assert progress_file.exists()


def test_log_entry():
    """Test logging an entry."""
    with tempfile.TemporaryDirectory() as tmpdir:
        progress_file = Path(tmpdir) / "progress.txt"
        pt = ProgressTracker(progress_file)

        pt.log_entry("Test message", session_id="test123")

        content = progress_file.read_text()
        assert "Test message" in content
        assert "[Session test123]" in content


def test_log_feature_events():
    """Test logging feature start and completion."""
    with tempfile.TemporaryDirectory() as tmpdir:
        progress_file = Path(tmpdir) / "progress.txt"
        pt = ProgressTracker(progress_file)

        pt.log_feature_start("F001", "Test Feature", "session1")
        pt.log_feature_complete("F001", "Test Feature", "session1")

        content = progress_file.read_text()
        assert "Started working on feature: F001" in content
        assert "Completed feature: F001" in content


def test_read_recent():
    """Test reading recent entries."""
    with tempfile.TemporaryDirectory() as tmpdir:
        progress_file = Path(tmpdir) / "progress.txt"
        pt = ProgressTracker(progress_file)

        for i in range(10):
            pt.log_entry(f"Message {i}")

        recent = pt.read_recent(lines=5)
        assert "Message 9" in recent
        assert "Message 4" not in recent


def test_session_markers():
    """Test session start/end markers."""
    with tempfile.TemporaryDirectory() as tmpdir:
        progress_file = Path(tmpdir) / "progress.txt"
        pt = ProgressTracker(progress_file)

        pt.log_session_start("session1")
        pt.log_entry("Work done", "session1")
        pt.log_session_end("session1")

        content = progress_file.read_text()
        assert "=== SESSION START ===" in content
        assert "=== SESSION END ===" in content
