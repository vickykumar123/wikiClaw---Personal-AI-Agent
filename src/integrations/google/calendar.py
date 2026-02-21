# ============================================
# GOOGLE CALENDAR - Calendar API client
# ============================================

import logging
import os
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

# OAuth scopes
SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/gmail.send"
]


class GoogleCalendarClient:
    """
    Client for Google Calendar API.

    Handles OAuth authentication and calendar operations.
    """

    def __init__(
        self,
        credentials_path: str = "credentials.json",
        token_path: str = "token.json"
    ):
        """
        Initialize Google Calendar client.

        Args:
            credentials_path: Path to OAuth credentials file
            token_path: Path to store/load access token
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        self.creds = None

    def authenticate(self) -> bool:
        """
        Authenticate with Google Calendar API.

        Uses existing token if valid, otherwise initiates OAuth flow.

        Returns:
            True if authenticated successfully
        """
        try:
            # Load existing token
            if os.path.exists(self.token_path):
                self.creds = Credentials.from_authorized_user_file(
                    self.token_path, SCOPES
                )

            # Refresh or get new credentials
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    logger.info("Refreshing expired credentials...")
                    self.creds.refresh(Request())
                else:
                    if not os.path.exists(self.credentials_path):
                        logger.error(f"Credentials file not found: {self.credentials_path}")
                        return False

                    logger.info("Starting OAuth flow...")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, SCOPES
                    )
                    self.creds = flow.run_local_server(port=0)

                # Save credentials
                with open(self.token_path, "w") as token:
                    token.write(self.creds.to_json())
                logger.info("Credentials saved")

            # Build service
            self.service = build("calendar", "v3", credentials=self.creds)
            logger.info("Google Calendar authenticated")
            return True

        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False

    def _ensure_authenticated(self) -> bool:
        """Ensure we have a valid service."""
        if not self.service:
            return self.authenticate()
        return True

    async def create_event(
        self,
        title: str,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        description: Optional[str] = None,
        location: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a calendar event.

        Args:
            title: Event title
            start_time: Start datetime
            end_time: End datetime (defaults to 1 hour after start)
            description: Event description
            location: Event location

        Returns:
            Created event data or None if failed
        """
        if not self._ensure_authenticated():
            return None

        try:
            # Default end time to 1 hour after start
            if end_time is None:
                end_time = start_time + timedelta(hours=1)

            event = {
                "summary": title,
                "start": {
                    "dateTime": start_time.isoformat(),
                    "timeZone": "UTC"
                },
                "end": {
                    "dateTime": end_time.isoformat(),
                    "timeZone": "UTC"
                }
            }

            if description:
                event["description"] = description
            if location:
                event["location"] = location

            result = self.service.events().insert(
                calendarId="primary",
                body=event
            ).execute()

            logger.info(f"Event created: {result.get('id')}")
            return result

        except Exception as e:
            logger.error(f"Failed to create event: {e}")
            return None

    async def list_events(
        self,
        max_results: int = 10,
        time_min: Optional[datetime] = None,
        time_max: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        List upcoming calendar events.

        Args:
            max_results: Maximum events to return
            time_min: Start time for search (defaults to now)
            time_max: End time for search (optional)

        Returns:
            List of events
        """
        if not self._ensure_authenticated():
            return []

        try:
            if time_min is None:
                time_min = datetime.now(timezone.utc)

            params = {
                "calendarId": "primary",
                "timeMin": time_min.isoformat() + "Z",
                "maxResults": max_results,
                "singleEvents": True,
                "orderBy": "startTime"
            }

            if time_max:
                params["timeMax"] = time_max.isoformat() + "Z"

            events_result = self.service.events().list(**params).execute()

            events = events_result.get("items", [])
            logger.info(f"Found {len(events)} events")
            return events

        except Exception as e:
            logger.error(f"Failed to list events: {e}")
            return []

    async def search_events(
        self,
        query: str,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search calendar events by query.

        Args:
            query: Search query
            max_results: Maximum events to return

        Returns:
            List of matching events
        """
        if not self._ensure_authenticated():
            return []

        try:
            events_result = self.service.events().list(
                calendarId="primary",
                timeMin=datetime.now(timezone.utc).isoformat() + "Z",
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
                q=query
            ).execute()

            events = events_result.get("items", [])
            logger.info(f"Found {len(events)} events matching '{query}'")
            return events

        except Exception as e:
            logger.error(f"Failed to search events: {e}")
            return []

    async def delete_event(self, event_id: str) -> bool:
        """
        Delete a calendar event.

        Args:
            event_id: Event ID to delete

        Returns:
            True if deleted successfully
        """
        if not self._ensure_authenticated():
            return False

        try:
            self.service.events().delete(
                calendarId="primary",
                eventId=event_id
            ).execute()

            logger.info(f"Event deleted: {event_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete event: {e}")
            return False

    async def get_event_by_title(self, title: str) -> Optional[Dict[str, Any]]:
        """
        Find an event by title.

        Args:
            title: Event title to search for

        Returns:
            Event data or None if not found
        """
        events = await self.search_events(title, max_results=5)

        for event in events:
            if event.get("summary", "").lower() == title.lower():
                return event

        return None
