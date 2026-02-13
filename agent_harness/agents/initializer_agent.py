"""Initializer agent for setting up the environment."""

from typing import List
from .base_agent import BaseAgent
from ..tools.base import BaseTool
from ..tools.bash_tool import BashTool
from ..tools.file_tool import FileReadTool, FileWriteTool
from ..config import Config


class InitializerAgent(BaseAgent):
    """Agent responsible for initial environment setup."""

    def __init__(self):
        self.workspace = str(Config.WORKSPACE_DIR)

    @property
    def name(self) -> str:
        return "initializer"

    @property
    def system_prompt(self) -> str:
        return """You are an initializer agent responsible for setting up the development environment.

Your tasks:
1. Create the init.sh script that will be used to start the development environment
2. Set up basic project structure
3. Initialize git repository if needed
4. Create initial test files
5. Document the setup in the progress log

You have access to bash commands, file read/write tools. Be thorough but efficient.
After completing setup, provide a summary of what was created and any important notes.

Always leave the environment in a clean, ready-to-use state."""

    def get_tools(self) -> List[BaseTool]:
        """Get tools for initialization."""
        return [
            BashTool(self.workspace),
            FileReadTool(self.workspace),
            FileWriteTool(self.workspace)
        ]

    def get_initial_message(self) -> str:
        """Get initial message for setup."""
        return f"""Initialize the development environment in {self.workspace}.

Please:
1. Check if this is a new environment or existing one
2. Create an init.sh script that can start the development server/environment
3. Set up any necessary configuration files
4. Initialize git if not already done
5. Create a basic project structure if needed
6. Provide a summary of the setup

Be thorough and document your actions."""
