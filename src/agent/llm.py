# ============================================
# LLM - Ollama client for LLM interactions
# ============================================

import logging
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass

import httpx

from constants import DEFAULT_OLLAMA_HOST, DEFAULT_OLLAMA_MODEL, ERROR_OLLAMA_CONNECTION

# Set up logging
logger = logging.getLogger(__name__)


@dataclass
class ToolCall:
    """Represents a tool call from the LLM."""
    name: str
    arguments: Dict[str, Any]


@dataclass
class ChatResponse:
    """Response from chat, may include tool calls."""
    content: str
    tool_calls: List[ToolCall]
    finished: bool  # True if no more tool calls needed


class OllamaClient:
    """
    Client for interacting with Ollama API.

    Handles all communication with the Ollama server,
    which routes to local or cloud models.
    """

    def __init__(
        self,
        host: str = DEFAULT_OLLAMA_HOST,
        model: str = DEFAULT_OLLAMA_MODEL,
        timeout: float = 120.0
    ):
        """
        Initialize Ollama client.

        Args:
            host: Ollama server URL (default: localhost:11434)
            model: Model to use (default: gpt-oss:120b-cloud)
            timeout: Request timeout in seconds
        """
        self.host = host.rstrip("/")
        self.model = model
        self.timeout = timeout

    async def health_check(self) -> bool:
        """
        Check if Ollama server is running.

        Returns:
            True if server is reachable, False otherwise
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.host}/api/tags",
                    timeout=5.0
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"{ERROR_OLLAMA_CONNECTION}: {e}")
            return False

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None
    ) -> str:
        """
        Send chat messages to the LLM and get response.

        Args:
            messages: List of message dicts with 'role' and 'content'
                      Example: [
                          {"role": "system", "content": "You are helpful"},
                          {"role": "user", "content": "Hello"}
                      ]
            model: Override default model (optional)

        Returns:
            LLM response text

        Raises:
            Exception: If request fails
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.host}/api/chat",
                    json={
                        "model": model or self.model,
                        "messages": messages,
                        "stream": False
                    },
                    timeout=self.timeout
                )

                response.raise_for_status()
                data = response.json()

                # Extract response text
                return data["message"]["content"]

        except httpx.TimeoutException:
            logger.error("Ollama request timed out")
            raise Exception("LLM request timed out. Please try again.")

        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama HTTP error: {e}")
            raise Exception(f"LLM request failed: {e}")

        except Exception as e:
            logger.error(f"Ollama error: {e}")
            raise Exception(f"LLM error: {e}")

    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None
    ) -> str:
        """
        Generate completion for a single prompt.

        Simpler interface when you don't need chat history.

        Args:
            prompt: The prompt text
            model: Override default model (optional)

        Returns:
            LLM response text
        """
        messages = [{"role": "user", "content": prompt}]
        return await self.chat(messages, model)

    async def chat_with_tools(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]],
        model: Optional[str] = None
    ) -> ChatResponse:
        """
        Send chat messages with available tools.

        Args:
            messages: List of message dicts with 'role' and 'content'
            tools: List of tool schemas
            model: Override default model (optional)

        Returns:
            ChatResponse with content and/or tool calls
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.host}/api/chat",
                    json={
                        "model": model or self.model,
                        "messages": messages,
                        "tools": tools,
                        "stream": False
                    },
                    timeout=self.timeout
                )

                response.raise_for_status()
                data = response.json()

                message = data.get("message", {})
                content = message.get("content", "")
                raw_tool_calls = message.get("tool_calls", [])

                # Parse tool calls
                tool_calls = []
                for tc in raw_tool_calls:
                    func = tc.get("function", {})
                    tool_calls.append(ToolCall(
                        name=func.get("name", ""),
                        arguments=func.get("arguments", {})
                    ))

                # Finished if no tool calls
                finished = len(tool_calls) == 0

                return ChatResponse(
                    content=content,
                    tool_calls=tool_calls,
                    finished=finished
                )

        except httpx.TimeoutException:
            logger.error("Ollama request timed out")
            raise Exception("LLM request timed out. Please try again.")

        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama HTTP error: {e}")
            raise Exception(f"LLM request failed: {e}")

        except Exception as e:
            logger.error(f"Ollama error: {e}")
            raise Exception(f"LLM error: {e}")
