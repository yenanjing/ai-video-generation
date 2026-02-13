"""Base agent class."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from ..tools.base import BaseTool
from ..session.session_manager import AgentSession


class BaseAgent(ABC):
    """Base class for agents."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Agent name."""
        pass

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """System prompt for the agent."""
        pass

    @abstractmethod
    def get_tools(self) -> List[BaseTool]:
        """Get tools available to the agent."""
        pass

    @abstractmethod
    def get_initial_message(self) -> str:
        """Get the initial message to start the agent."""
        pass

    def run(self, max_iterations: int = 50) -> Dict[str, Any]:
        """Run the agent."""
        session = AgentSession(
            system_prompt=self.system_prompt,
            tools=self.get_tools(),
            max_iterations=max_iterations
        )

        initial_message = self.get_initial_message()
        result = session.run(initial_message)

        return {
            "agent": self.name,
            "session_id": session.session_id,
            **result
        }
