# ============================================
# CALENDAR SUB-AGENT - Handles calendar events
# ============================================

from typing import List

from agents.base import BaseSubAgent
from agent.llm import OllamaClient
from integrations.google.calendar import GoogleCalendarClient
from tools.base import BaseTool
from tools.calendar import CreateEventTool, ListEventsTool, SearchEventsTool, DeleteEventTool


CALENDAR_AGENT_PROMPT = """You are a calendar management agent.

Your job is to:
- Create new calendar events
- List upcoming events
- Search for specific events
- Delete events when requested

You have these tools:
- create_event: Schedule a new event with title, datetime, and optional description
- list_events: Show upcoming events (can filter by date)
- search_events: Find events by title
- delete_event: Remove an event by title or date

IMPORTANT:
- Call ONE tool to complete the task
- After the tool returns a result, IMMEDIATELY respond with a confirmation
- Do NOT call multiple tools or the same tool twice
- Be concise - just confirm what was done"""


class CalendarAgent(BaseSubAgent):
    """Sub-agent for handling calendar events."""

    def __init__(
        self,
        llm_client: OllamaClient,
        calendar_client: GoogleCalendarClient
    ):
        super().__init__(llm_client)
        self.calendar = calendar_client

    @property
    def name(self) -> str:
        return "calendar_agent"

    @property
    def description(self) -> str:
        return (
            "Creates, lists, searches, and deletes calendar events. "
            "Use this when user asks to schedule something, check their calendar, "
            "find an event, or cancel a meeting."
        )

    @property
    def system_prompt(self) -> str:
        return CALENDAR_AGENT_PROMPT

    def get_tools(self) -> List[BaseTool]:
        return [
            CreateEventTool(calendar_client=self.calendar),
            ListEventsTool(calendar_client=self.calendar),
            SearchEventsTool(calendar_client=self.calendar),
            DeleteEventTool(calendar_client=self.calendar)
        ]
