"""Bash command execution tool."""

import subprocess
from typing import Any, Dict, Optional
from .base import BaseTool, ToolResult


class BashTool(BaseTool):
    """Execute bash commands."""

    def __init__(self, working_dir: str):
        self.working_dir = working_dir

    @property
    def name(self) -> str:
        return "bash"

    @property
    def description(self) -> str:
        return "Execute bash commands in the workspace. Use this for running scripts, git commands, tests, etc."

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The bash command to execute"
                }
            },
            "required": ["command"]
        }

    def execute(self, command: str, **kwargs) -> ToolResult:
        """Execute a bash command."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                timeout=30
            )

            output = result.stdout
            if result.stderr:
                output += f"\nSTDERR:\n{result.stderr}"

            return ToolResult(
                success=result.returncode == 0,
                output=output,
                error=result.stderr if result.returncode != 0 else None,
                metadata={"return_code": result.returncode}
            )
        except subprocess.TimeoutExpired:
            return ToolResult(
                success=False,
                output="",
                error="Command timed out after 30 seconds"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=str(e)
            )
