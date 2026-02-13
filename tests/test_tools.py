"""Tests for tools."""

import pytest
import tempfile
from pathlib import Path
from agent_harness.tools import BashTool, FileReadTool, FileWriteTool


def test_bash_tool_success():
    """Test successful bash command."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tool = BashTool(tmpdir)
        result = tool.execute(command="echo 'Hello World'")

        assert result.success
        assert "Hello World" in result.output


def test_bash_tool_failure():
    """Test failed bash command."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tool = BashTool(tmpdir)
        result = tool.execute(command="nonexistent_command_xyz")

        assert not result.success
        assert result.error is not None


def test_file_read_tool():
    """Test reading a file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a test file
        test_file = Path(tmpdir) / "test.txt"
        test_file.write_text("Test content")

        tool = FileReadTool(tmpdir)
        result = tool.execute(path="test.txt")

        assert result.success
        assert result.output == "Test content"


def test_file_read_tool_not_found():
    """Test reading non-existent file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tool = FileReadTool(tmpdir)
        result = tool.execute(path="nonexistent.txt")

        assert not result.success
        assert "not found" in result.error.lower()


def test_file_write_tool():
    """Test writing a file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tool = FileWriteTool(tmpdir)
        result = tool.execute(path="new_file.txt", content="New content")

        assert result.success

        # Verify file was created
        created_file = Path(tmpdir) / "new_file.txt"
        assert created_file.exists()
        assert created_file.read_text() == "New content"


def test_file_write_tool_creates_dirs():
    """Test that write tool creates parent directories."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tool = FileWriteTool(tmpdir)
        result = tool.execute(path="subdir/nested/file.txt", content="Content")

        assert result.success

        created_file = Path(tmpdir) / "subdir/nested/file.txt"
        assert created_file.exists()
