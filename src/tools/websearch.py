# ============================================
# WEB SEARCH TOOLS - DuckDuckGo search
# ============================================

import logging
from typing import Any, Dict, List

from ddgs import DDGS

from tools.base import BaseTool, ToolResult

logger = logging.getLogger(__name__)


class WebSearchTool(BaseTool):
    """Tool for searching the web using DuckDuckGo."""

    def __init__(self):
        self.ddgs = DDGS()

    @property
    def name(self) -> str:
        return "web_search"

    @property
    def description(self) -> str:
        return (
            "Search the web for current information. "
            "Use this when the user asks about recent news, current events, "
            "facts you don't know, or anything that requires up-to-date information."
        )

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query (e.g., 'weather in New York', 'latest news about AI')"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Number of results to return (default: 5)"
                }
            },
            "required": ["query"]
        }

    async def execute(self, query: str, max_results: int = 5, **kwargs) -> ToolResult:
        """Search the web."""
        try:
            logger.info(f"Web search: {query}")

            # Perform search
            results = list(self.ddgs.text(query, max_results=max_results))

            if not results:
                return ToolResult(
                    success=True,
                    data=f"No results found for '{query}'."
                )

            # Format results
            formatted = []
            for i, r in enumerate(results, 1):
                title = r.get("title", "No title")
                body = r.get("body", "No description")
                url = r.get("href", "")
                formatted.append(f"{i}. **{title}**\n   {body}\n   URL: {url}")

            return ToolResult(
                success=True,
                data=f"Search results for '{query}':\n\n" + "\n\n".join(formatted)
            )

        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return ToolResult(
                success=False,
                data=None,
                error=str(e)
            )


class NewsSearchTool(BaseTool):
    """Tool for searching recent news using DuckDuckGo."""

    def __init__(self):
        self.ddgs = DDGS()

    @property
    def name(self) -> str:
        return "news_search"

    @property
    def description(self) -> str:
        return (
            "Search for recent news articles. "
            "Use this when the user asks about current events, "
            "latest news, or recent happenings."
        )

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "News search query (e.g., 'AI news', 'stock market today')"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Number of results to return (default: 5)"
                }
            },
            "required": ["query"]
        }

    async def execute(self, query: str, max_results: int = 5, **kwargs) -> ToolResult:
        """Search for news."""
        try:
            logger.info(f"News search: {query}")

            # Perform news search
            results = list(self.ddgs.news(query, max_results=max_results))

            if not results:
                return ToolResult(
                    success=True,
                    data=f"No news found for '{query}'."
                )

            # Format results
            formatted = []
            for i, r in enumerate(results, 1):
                title = r.get("title", "No title")
                body = r.get("body", "No description")
                source = r.get("source", "Unknown source")
                date = r.get("date", "")
                url = r.get("url", "")
                formatted.append(f"{i}. **{title}**\n   {body}\n   Source: {source} | {date}\n   URL: {url}")

            return ToolResult(
                success=True,
                data=f"News results for '{query}':\n\n" + "\n\n".join(formatted)
            )

        except Exception as e:
            logger.error(f"News search failed: {e}")
            return ToolResult(
                success=False,
                data=None,
                error=str(e)
            )
