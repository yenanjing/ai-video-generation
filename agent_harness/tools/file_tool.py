"""File operations tool."""

from pathlib import Path
from typing import Any, Dict
from .base import BaseTool, ToolResult


class FileReadTool(BaseTool):
    """Read file contents."""

    def __init__(self, working_dir: str):
        self.working_dir = Path(working_dir)

    @property
    def name(self) -> str:
        return "read_file"

    @property
    def description(self) -> str:
        return "Read the contents of a file in the workspace."

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative path to the file"
                }
            },
            "required": ["path"]
        }

    def execute(self, path: str, **kwargs) -> ToolResult:
        """Read a file."""
        try:
            file_path = self.working_dir / path
            if not file_path.exists():
                return ToolResult(
                    success=False,
                    output="",
                    error=f"File not found: {path}"
                )

            content = file_path.read_text()
            return ToolResult(
                success=True,
                output=content
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=str(e)
            )


class FileWriteTool(BaseTool):
    """Write file contents."""

    def __init__(self, working_dir: str):
        self.working_dir = Path(working_dir)

    @property
    def name(self) -> str:
        return "write_file"

    @property
    def description(self) -> str:
        return "Write content to a file in the workspace. Creates parent directories if needed."

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative path to the file"
                },
                "content": {
                    "type": "string",
                    "description": "Content to write to the file"
                }
            },
            "required": ["path", "content"]
        }

    def execute(self, path: str, content: str, **kwargs) -> ToolResult:
        """Write to a file."""
        try:
            file_path = self.working_dir / path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)

            return ToolResult(
                success=True,
                output=f"Successfully wrote {len(content)} characters to {path}"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=str(e)
            )
