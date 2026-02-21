# ============================================
# TOOLS BASE - Base class for all tools
# ============================================

from abc import ABC, abstractmethod
from typing import Any, Dict
from dataclasses import dataclass


@dataclass
class ToolResult:
    """Result from a tool execution."""
    success: bool
    data: Any
    error: str = ""


class BaseTool(ABC):
    """
    Base class for all tools.

    Each tool has:
    - name: Unique identifier for the tool
    - description: What the tool does (for LLM)
    - parameters: What arguments it accepts
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name (used by LLM to call it)."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what the tool does."""
        pass

    @property
    @abstractmethod
    def parameters(self) -> Dict[str, Any]:
        """
        JSON schema for tool parameters.

        Example:
        {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                }
            },
            "required": ["query"]
        }
        """
        pass

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """
        Execute the tool with given arguments.

        Args:
            **kwargs: Tool-specific arguments

        Returns:
            ToolResult with success status and data/error
        """
        pass

    def to_schema(self) -> Dict[str, Any]:
        """
        Convert tool to schema format for LLM.

        Returns:
            Tool schema dict
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }
