# ============================================
# TEST CALENDAR CREATE - Create event and keep it
# ============================================
#
# Usage: python scripts/test_calendar_create.py

import asyncio
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from dotenv import load_dotenv
from integrations.google.calendar import GoogleCalendarClient
from datetime import datetime, timedelta

load_dotenv()


async def test_create():
    """Create a test event and keep it."""

    print("=" * 50)
    print("CREATE CALENDAR EVENT (will NOT be deleted)")
    print("=" * 50)

    # Initialize Google Calendar
    calendar_client = GoogleCalendarClient(
        credentials_path=os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json"),
        token_path=os.getenv("GOOGLE_TOKEN_PATH", "token.json")
    )

    if not calendar_client.authenticate():
        print("Google Calendar auth failed")
        return

    print("✓ Google Calendar authenticated\n")

    # Create event for tomorrow
    tomorrow = datetime.now() + timedelta(days=1)
    start_time = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(hours=1)

    print(f"Creating event:")
    print(f"  Title: Test Event from Agent")
    print(f"  Time: {start_time.strftime('%B %d, %Y at %I:%M %p')}")
    print(f"  Duration: 1 hour")

    result = await calendar_client.create_event(
        title="Test Event from Agent",
        start_time=start_time,
        end_time=end_time,
        description="This is a test event created by the AI agent"
    )

    if result:
        print(f"\n✓ Event created!")
        print(f"  Event ID: {result.get('id')}")
        print(f"  Link: {result.get('htmlLink')}")
        print("\n→ Check your Google Calendar - you should see it!")
    else:
        print("\n✗ Failed to create event")


if __name__ == "__main__":
    asyncio.run(test_create())
