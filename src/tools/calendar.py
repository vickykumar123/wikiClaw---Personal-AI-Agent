# ============================================
# CALENDAR TOOLS - Google Calendar tools
# ============================================

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from dateutil import parser as date_parser

from tools.base import BaseTool, ToolResult
from integrations.google.calendar import GoogleCalendarClient

logger = logging.getLogger(__name__)


class CreateEventTool(BaseTool):
    """Tool for creating calendar events."""

    def __init__(self, calendar_client: GoogleCalendarClient):
        self.calendar = calendar_client

    @property
    def name(self) -> str:
        return "create_event"

    @property
    def description(self) -> str:
        return (
            "Create a calendar event or reminder. "
            "Use this when the user asks to schedule something, "
            "set a reminder, or add an event to their calendar."
        )

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Event title (e.g., 'Meeting with John', 'Doctor appointment')"
                },
                "start_time": {
                    "type": "string",
                    "description": "Start time in natural format or ISO format (e.g., 'tomorrow at 3pm', '2024-01-15T15:00:00')"
                },
                "duration_minutes": {
                    "type": "integer",
                    "description": "Duration in minutes (default: 60)"
                },
                "description": {
                    "type": "string",
                    "description": "Optional event description"
                }
            },
            "required": ["title", "start_time"]
        }

    async def execute(
        self,
        title: str,
        start_time: str,
        duration_minutes: int = 60,
        description: str = None,
        **kwargs
    ) -> ToolResult:
        """Create a calendar event."""
        try:
            # Parse start time
            try:
                start_dt = date_parser.parse(start_time)
            except Exception:
                return ToolResult(
                    success=False,
                    data=None,
                    error=f"Could not parse time: {start_time}"
                )

            # Calculate end time
            end_dt = start_dt + timedelta(minutes=duration_minutes)

            # Create event
            result = await self.calendar.create_event(
                title=title,
                start_time=start_dt,
                end_time=end_dt,
                description=description
            )

            if result:
                event_link = result.get("htmlLink", "")
                formatted_time = start_dt.strftime("%B %d, %Y at %I:%M %p")
                return ToolResult(
                    success=True,
                    data=f"Event '{title}' created for {formatted_time}."
                )
            else:
                return ToolResult(
                    success=False,
                    data=None,
                    error="Failed to create event"
                )

        except Exception as e:
            logger.error(f"Failed to create event: {e}")
            return ToolResult(
                success=False,
                data=None,
                error=str(e)
            )


class ListEventsTool(BaseTool):
    """Tool for listing upcoming calendar events."""

    def __init__(self, calendar_client: GoogleCalendarClient):
        self.calendar = calendar_client

    @property
    def name(self) -> str:
        return "list_events"

    @property
    def description(self) -> str:
        return (
            "List calendar events. Can list all upcoming events or events for a specific date. "
            "Use this when the user asks what's on their calendar, "
            "upcoming events, schedule for today/tomorrow/specific date."
        )

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "Optional date to filter events (e.g., 'today', 'tomorrow', '2024-01-15'). If not provided, lists all upcoming events."
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of events to return (default: 10)"
                }
            },
            "required": []
        }

    async def execute(self, date: str = None, max_results: int = 10, **kwargs) -> ToolResult:
        """List events, optionally filtered by date."""
        try:
            time_min = None
            time_max = None

            # Parse date if provided
            if date:
                try:
                    # Parse the date
                    parsed_date = date_parser.parse(date)
                    # Set to start of day
                    time_min = parsed_date.replace(hour=0, minute=0, second=0, microsecond=0)
                    # Set to end of day
                    time_max = parsed_date.replace(hour=23, minute=59, second=59, microsecond=999999)
                except Exception:
                    pass  # Fall back to listing all upcoming

            events = await self.calendar.list_events(
                max_results=max_results,
                time_min=time_min,
                time_max=time_max
            )

            date_str = f" for {date}" if date else ""

            if not events:
                return ToolResult(
                    success=True,
                    data=f"No events found{date_str}."
                )

            # Format events
            event_list = []
            for event in events:
                title = event.get("summary", "No title")
                start = event.get("start", {})

                # Handle all-day vs timed events
                if "dateTime" in start:
                    start_dt = date_parser.parse(start["dateTime"])
                    time_str = start_dt.strftime("%B %d at %I:%M %p")
                else:
                    time_str = start.get("date", "Unknown date")

                event_list.append(f"- **{title}**: {time_str}")

            header = f"Events{date_str}:" if date else "Upcoming events:"
            return ToolResult(
                success=True,
                data=header + "\n" + "\n".join(event_list)
            )

        except Exception as e:
            logger.error(f"Failed to list events: {e}")
            return ToolResult(
                success=False,
                data=None,
                error=str(e)
            )


class SearchEventsTool(BaseTool):
    """Tool for searching calendar events."""

    def __init__(self, calendar_client: GoogleCalendarClient):
        self.calendar = calendar_client

    @property
    def name(self) -> str:
        return "search_events"

    @property
    def description(self) -> str:
        return (
            "Search for calendar events by keyword. "
            "Use this when the user asks about a specific event or meeting."
        )

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search term (e.g., 'meeting', 'doctor', 'John')"
                }
            },
            "required": ["query"]
        }

    async def execute(self, query: str, **kwargs) -> ToolResult:
        """Search for events."""
        try:
            events = await self.calendar.search_events(query)

            if not events:
                return ToolResult(
                    success=True,
                    data=f"No events found matching '{query}'."
                )

            # Format events
            event_list = []
            for event in events:
                title = event.get("summary", "No title")
                start = event.get("start", {})

                if "dateTime" in start:
                    start_dt = date_parser.parse(start["dateTime"])
                    time_str = start_dt.strftime("%B %d at %I:%M %p")
                else:
                    time_str = start.get("date", "Unknown date")

                event_list.append(f"- **{title}**: {time_str}")

            return ToolResult(
                success=True,
                data=f"Events matching '{query}':\n" + "\n".join(event_list)
            )

        except Exception as e:
            logger.error(f"Failed to search events: {e}")
            return ToolResult(
                success=False,
                data=None,
                error=str(e)
            )


class DeleteEventTool(BaseTool):
    """Tool for deleting calendar events."""

    def __init__(self, calendar_client: GoogleCalendarClient):
        self.calendar = calendar_client

    @property
    def name(self) -> str:
        return "delete_event"

    @property
    def description(self) -> str:
        return (
            "Delete calendar events by title or date. "
            "Use this when the user asks to cancel or remove events. "
            "Can delete a specific event by title, or all events on a date."
        )

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Title of the event to delete (optional if date is provided)"
                },
                "date": {
                    "type": "string",
                    "description": "Delete all events on this date (e.g., 'tomorrow', '2024-01-15')"
                }
            },
            "required": []
        }

    async def execute(self, title: str = None, date: str = None, **kwargs) -> ToolResult:
        """Delete events by title or date."""
        try:
            # Delete by date
            if date:
                try:
                    parsed_date = date_parser.parse(date)
                    time_min = parsed_date.replace(hour=0, minute=0, second=0, microsecond=0)
                    time_max = parsed_date.replace(hour=23, minute=59, second=59, microsecond=999999)

                    events = await self.calendar.list_events(
                        time_min=time_min,
                        time_max=time_max,
                        max_results=50
                    )

                    if not events:
                        return ToolResult(
                            success=True,
                            data=f"No events found for {date}."
                        )

                    deleted_count = 0
                    deleted_titles = []
                    for event in events:
                        event_id = event.get("id")
                        event_title = event.get("summary", "Untitled")
                        if await self.calendar.delete_event(event_id):
                            deleted_count += 1
                            deleted_titles.append(event_title)

                    if deleted_count > 0:
                        return ToolResult(
                            success=True,
                            data=f"Deleted {deleted_count} event(s) for {date}: {', '.join(deleted_titles)}"
                        )
                    else:
                        return ToolResult(
                            success=False,
                            data=None,
                            error="Failed to delete events"
                        )

                except Exception as e:
                    return ToolResult(
                        success=False,
                        data=None,
                        error=f"Could not parse date: {date}"
                    )

            # Delete by title
            if title:
                event = await self.calendar.get_event_by_title(title)

                if not event:
                    return ToolResult(
                        success=True,
                        data=f"No event found with title '{title}'."
                    )

                event_id = event.get("id")
                deleted = await self.calendar.delete_event(event_id)

                if deleted:
                    return ToolResult(
                        success=True,
                        data=f"Event '{title}' has been deleted."
                    )
                else:
                    return ToolResult(
                        success=False,
                        data=None,
                        error="Failed to delete event"
                    )

            return ToolResult(
                success=False,
                data=None,
                error="Please provide either a title or date to delete events."
            )

        except Exception as e:
            logger.error(f"Failed to delete event: {e}")
            return ToolResult(
                success=False,
                data=None,
                error=str(e)
            )
