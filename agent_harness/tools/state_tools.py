"""Tools for accessing and updating state."""

from typing import Any, Dict
from .base import BaseTool, ToolResult
from ..state.progress_tracker import ProgressTracker
from ..state.feature_list import FeatureList, FeatureStatus


class ReadProgressTool(BaseTool):
    """Read the progress log."""

    def __init__(self, progress_tracker: ProgressTracker):
        self.progress_tracker = progress_tracker

    @property
    def name(self) -> str:
        return "read_progress"

    @property
    def description(self) -> str:
        return "Read the recent progress log entries to understand what has been done in previous sessions."

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "lines": {
                    "type": "integer",
                    "description": "Number of recent lines to read (default: 50)",
                    "default": 50
                }
            }
        }

    def execute(self, lines: int = 50, **kwargs) -> ToolResult:
        """Read progress log."""
        try:
            content = self.progress_tracker.read_recent(lines)
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


class ReadFeatureListTool(BaseTool):
    """Read the feature list."""

    def __init__(self, feature_list: FeatureList):
        self.feature_list = feature_list

    @property
    def name(self) -> str:
        return "read_feature_list"

    @property
    def description(self) -> str:
        return "Read the feature list to see what tasks need to be done and their status."

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {}
        }

    def execute(self, **kwargs) -> ToolResult:
        """Read feature list."""
        try:
            features = self.feature_list.get_all_features()
            summary = self.feature_list.get_summary()

            output = f"Feature Summary: {summary}\n\n"
            for feature in features:
                output += f"[{feature.status.value.upper()}] {feature.id}: {feature.name}\n"
                output += f"  Description: {feature.description}\n"
                if feature.acceptance_criteria:
                    output += f"  Criteria: {', '.join(feature.acceptance_criteria)}\n"
                if feature.notes:
                    output += f"  Notes: {feature.notes}\n"
                output += "\n"

            return ToolResult(
                success=True,
                output=output,
                metadata={"summary": summary}
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=str(e)
            )


class UpdateFeatureStatusTool(BaseTool):
    """Update feature status."""

    def __init__(self, feature_list: FeatureList):
        self.feature_list = feature_list

    @property
    def name(self) -> str:
        return "update_feature_status"

    @property
    def description(self) -> str:
        return "Update the status of a feature (pending, in_progress, completed, or failed)."

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "feature_id": {
                    "type": "string",
                    "description": "The feature ID"
                },
                "status": {
                    "type": "string",
                    "enum": ["pending", "in_progress", "completed", "failed"],
                    "description": "The new status"
                },
                "notes": {
                    "type": "string",
                    "description": "Optional notes about the status change"
                }
            },
            "required": ["feature_id", "status"]
        }

    def execute(self, feature_id: str, status: str, notes: str = None, **kwargs) -> ToolResult:
        """Update feature status."""
        try:
            self.feature_list.update_feature_status(
                feature_id=feature_id,
                status=FeatureStatus(status),
                notes=notes
            )
            return ToolResult(
                success=True,
                output=f"Updated feature {feature_id} to status: {status}"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=str(e)
            )
