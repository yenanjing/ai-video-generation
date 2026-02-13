"""Coding agent for incremental feature development."""

from typing import List
from .base_agent import BaseAgent
from ..tools.base import BaseTool
from ..tools.bash_tool import BashTool
from ..tools.file_tool import FileReadTool, FileWriteTool
from ..tools.state_tools import ReadProgressTool, ReadFeatureListTool, UpdateFeatureStatusTool
from ..state.progress_tracker import ProgressTracker
from ..state.feature_list import FeatureList
from ..config import Config


class CodingAgent(BaseAgent):
    """Agent responsible for implementing features one at a time."""

    def __init__(self, progress_tracker: ProgressTracker, feature_list: FeatureList):
        self.workspace = str(Config.WORKSPACE_DIR)
        self.progress_tracker = progress_tracker
        self.feature_list = feature_list

    @property
    def name(self) -> str:
        return "coding"

    @property
    def system_prompt(self) -> str:
        return """You are a coding agent responsible for implementing features incrementally.

Your workflow for EACH session:
1. Run 'pwd' to verify working directory
2. Read git logs to understand recent changes
3. Read the progress log to see what was done previously
4. Read the feature list to understand all tasks
5. Choose the NEXT pending feature (only ONE at a time)
6. Run init.sh to start the development environment
7. Run tests to verify current state
8. Implement the chosen feature
9. Test your implementation thoroughly
10. Commit with a descriptive message
11. Update feature status to 'completed'
12. Update progress log

IMPORTANT:
- Work on ONE feature at a time only
- Always run tests before and after changes
- Leave the environment in a clean state suitable for merging
- Write detailed commit messages
- If you encounter bugs from previous sessions, fix them first
- Never skip testing

You have access to bash, file operations, and state management tools."""

    def get_tools(self) -> List[BaseTool]:
        """Get tools for coding."""
        return [
            BashTool(self.workspace),
            FileReadTool(self.workspace),
            FileWriteTool(self.workspace),
            ReadProgressTool(self.progress_tracker),
            ReadFeatureListTool(self.feature_list),
            UpdateFeatureStatusTool(self.feature_list)
        ]

    def get_initial_message(self) -> str:
        """Get initial message for coding session."""
        return """Start a new coding session.

Follow the standard workflow:
1. Get your bearings (pwd, git log, read progress)
2. Review feature list
3. Choose next pending feature
4. Start environment (init.sh)
5. Run tests
6. Implement ONE feature
7. Test and commit
8. Update status and progress

Begin now."""
