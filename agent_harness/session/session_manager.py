"""Session management for agent runs."""

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from anthropic import Anthropic
from ..config import Config
from ..tools.base import BaseTool, ToolResult


class Message:
    """Represents a message in the conversation."""

    def __init__(self, role: str, content: Any):
        self.role = role
        self.content = content

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "role": self.role,
            "content": self.content
        }


class AgentSession:
    """Manages a single agent session."""

    def __init__(self,
                 system_prompt: str,
                 tools: List[BaseTool],
                 max_iterations: int = 50):
        self.session_id = str(uuid.uuid4())[:8]
        self.system_prompt = system_prompt
        self.tools = tools
        self.max_iterations = max_iterations

        self.client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        self.messages: List[Message] = []
        self.iteration_count = 0

    def add_message(self, role: str, content: Any):
        """Add a message to the conversation."""
        self.messages.append(Message(role, content))

    def run(self, initial_message: str) -> Dict[str, Any]:
        """Run the agent session."""
        self.add_message("user", initial_message)

        while self.iteration_count < self.max_iterations:
            self.iteration_count += 1

            # Call Claude API
            response = self._call_api()

            # Handle stop reason
            if response.stop_reason == "end_turn":
                # Agent finished
                return {
                    "status": "completed",
                    "iterations": self.iteration_count,
                    "final_message": self._extract_text(response)
                }
            elif response.stop_reason == "tool_use":
                # Execute tools and continue
                tool_results = self._execute_tools(response)
                self.add_message("user", tool_results)
            elif response.stop_reason == "max_tokens":
                return {
                    "status": "incomplete",
                    "reason": "max_tokens_reached",
                    "iterations": self.iteration_count
                }
            else:
                return {
                    "status": "error",
                    "reason": f"Unexpected stop reason: {response.stop_reason}",
                    "iterations": self.iteration_count
                }

        return {
            "status": "incomplete",
            "reason": "max_iterations_reached",
            "iterations": self.iteration_count
        }

    def _call_api(self):
        """Call the Claude API."""
        messages = [m.to_dict() for m in self.messages]
        tools_schema = [tool.to_anthropic_tool() for tool in self.tools]

        response = self.client.messages.create(
            model=Config.MODEL_NAME,
            max_tokens=Config.MAX_TOKENS,
            system=self.system_prompt,
            messages=messages,
            tools=tools_schema
        )

        # Add assistant response to messages
        self.add_message("assistant", response.content)

        return response

    def _execute_tools(self, response) -> List[Dict[str, Any]]:
        """Execute tools from the response."""
        tool_results = []

        for block in response.content:
            if block.type == "tool_use":
                tool = self._find_tool(block.name)
                if tool:
                    result = tool.execute(**block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result.output if result.success else f"Error: {result.error}"
                    })
                else:
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": f"Error: Tool {block.name} not found"
                    })

        return tool_results

    def _find_tool(self, name: str) -> Optional[BaseTool]:
        """Find a tool by name."""
        for tool in self.tools:
            if tool.name == name:
                return tool
        return None

    def _extract_text(self, response) -> str:
        """Extract text content from response."""
        text_parts = []
        for block in response.content:
            if hasattr(block, "text"):
                text_parts.append(block.text)
        return "\n".join(text_parts)
