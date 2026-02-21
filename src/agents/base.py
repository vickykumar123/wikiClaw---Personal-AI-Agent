# ============================================
# BASE SUB-AGENT - Base class for all sub-agents
# ============================================

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from dataclasses import dataclass

from agent.llm import OllamaClient
from tools.base import BaseTool

logger = logging.getLogger(__name__)

# Max tool loop iterations per sub-agent
MAX_SUB_AGENT_ITERATIONS = 3


@dataclass
class SubAgentResult:
    """Result from a sub-agent execution."""
    success: bool
    response: str
    error: str = ""


class BaseSubAgent(ABC):
    """
    Base class for all sub-agents.

    Each sub-agent:
    - Has a specific domain (memory, notes, calendar, etc.)
    - Has its own system prompt
    - Has access to specific tools
    - Can execute tasks and return results
    """

    def __init__(self, llm_client: OllamaClient):
        self.llm = llm_client

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this agent."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what this agent does (for orchestrator)."""
        pass

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """System prompt for this agent."""
        pass

    @abstractmethod
    def get_tools(self) -> List[BaseTool]:
        """Get the tools available to this agent."""
        pass

    def to_schema(self) -> Dict[str, Any]:
        """
        Convert to schema for orchestrator.

        The orchestrator sees sub-agents as "tools" it can call.
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task": {
                            "type": "string",
                            "description": "The task for this agent to perform"
                        }
                    },
                    "required": ["task"]
                }
            }
        }

    async def execute(self, task: str) -> SubAgentResult:
        """
        Execute a task using this agent.

        Args:
            task: The task description from orchestrator

        Returns:
            SubAgentResult with response or error
        """
        logger.info(f"[{self.name}] Executing task: {task[:50]}...")

        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": task}
            ]

            tools = self.get_tools()
            tool_schemas = [tool.to_schema() for tool in tools]
            tool_map = {tool.name: tool for tool in tools}

            response = await self._run_tool_loop(messages, tool_schemas, tool_map)

            logger.info(f"[{self.name}] Completed: {response[:50]}...")
            return SubAgentResult(success=True, response=response)

        except Exception as e:
            logger.error(f"[{self.name}] Error: {e}")
            return SubAgentResult(
                success=False,
                response="",
                error=str(e)
            )

    async def _run_tool_loop(
        self,
        messages: List[Dict],
        tool_schemas: List[Dict],
        tool_map: Dict[str, BaseTool]
    ) -> str:
        """
        Run tool execution loop.

        Sub-agents typically need only ONE tool call.
        After successful execution, return the result immediately.
        """
        iterations = 0

        while iterations < MAX_SUB_AGENT_ITERATIONS:
            iterations += 1
            logger.debug(f"[{self.name}] Loop iteration {iterations}/{MAX_SUB_AGENT_ITERATIONS}")

            response = await self.llm.chat_with_tools(
                messages=messages,
                tools=tool_schemas
            )

            # If LLM responds without tool calls, return
            if response.finished:
                return response.content

            # Execute FIRST tool only, then return result
            if response.tool_calls:
                tool_call = response.tool_calls[0]  # Take first tool only
                tool_name = tool_call.name
                tool_args = tool_call.arguments

                logger.info(f"[{self.name}] Calling tool: {tool_name}")

                if tool_name in tool_map:
                    tool = tool_map[tool_name]
                    result = await tool.execute(**tool_args)

                    result_content = str(result.data) if result.success else f"Error: {result.error}"

                    # Return immediately after first successful tool execution
                    logger.info(f"[{self.name}] Tool executed, returning: {result_content[:50]}...")
                    return result_content
                else:
                    logger.warning(f"Unknown tool: {tool_name}")
                    return f"Error: Unknown tool '{tool_name}'"

        logger.warning(f"[{self.name}] Max iterations reached")
        return "Could not complete the task."
