# ============================================
# WEB SUB-AGENT - Handles web searches
# ============================================

from typing import List

from agents.base import BaseSubAgent
from agent.llm import OllamaClient
from tools.base import BaseTool
from tools.websearch import WebSearchTool, NewsSearchTool


WEB_AGENT_PROMPT = """You are a web search agent.

Your job is to:
- Search the web for information
- Find recent news articles

You have these tools:
- web_search: Search the web for general information, facts, tutorials, etc.
- news_search: Search for recent news articles on a topic

IMPORTANT:
- Call ONE tool (web_search or news_search) to complete the task
- After results return, IMMEDIATELY summarize the key findings
- Do NOT call multiple tools or the same tool twice
- Be concise but informative in your summary
- Do NOT use markdown formatting - use plain text only"""


class WebAgent(BaseSubAgent):
    """Sub-agent for handling web searches."""

    def __init__(self, llm_client: OllamaClient):
        super().__init__(llm_client)

    @property
    def name(self) -> str:
        return "web_agent"

    @property
    def description(self) -> str:
        return (
            "Searches the web for information and news. "
            "Use this when user asks about current info, facts, tutorials, "
            "recent news, or anything requiring web lookup."
        )

    @property
    def system_prompt(self) -> str:
        return WEB_AGENT_PROMPT

    def get_tools(self) -> List[BaseTool]:
        return [
            WebSearchTool(),
            NewsSearchTool()
        ]
