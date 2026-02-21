# ============================================
# TEST CALENDAR - Test Google Calendar tools
# ============================================
#
# Usage: python scripts/test_calendar.py

import asyncio
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from dotenv import load_dotenv

from database.mongodb import MongoDB
from memory.embeddings import EmbeddingsClient
from agent.llm import OllamaClient
from agent.core import Agent
from integrations.base import Message
from integrations.google.calendar import GoogleCalendarClient

load_dotenv()


async def test_calendar():
    """Test the calendar tools."""

    print("=" * 60)
    print("TESTING CALENDAR TOOLS")
    print("=" * 60)

    # 1. Initialize components
    print("\n1. Initializing components...")

    db = MongoDB(uri=os.getenv("MONGODB_URI"))
    await db.connect()
    print("   ✓ MongoDB connected")

    embeddings = EmbeddingsClient(api_key=os.getenv("OPENAI_API_KEY"))
    print("   ✓ Embeddings client ready")

    llm = OllamaClient(
        host=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
        model=os.getenv("OLLAMA_MODEL", "gpt-oss:120b-cloud")
    )

    if await llm.health_check():
        print(f"   ✓ Ollama connected ({llm.model})")
    else:
        print("   ✗ Ollama not reachable")
        await db.disconnect()
        return

    # Initialize Google Calendar
    calendar_client = GoogleCalendarClient(
        credentials_path=os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json"),
        token_path=os.getenv("GOOGLE_TOKEN_PATH", "token.json")
    )

    if calendar_client.authenticate():
        print("   ✓ Google Calendar authenticated")
    else:
        print("   ✗ Google Calendar auth failed")
        await db.disconnect()
        return

    agent = Agent(
        llm_client=llm,
        db=db,
        embeddings_client=embeddings,
        calendar_client=calendar_client
    )
    print("   ✓ Agent initialized")

    # Test user
    test_user_id = "test_calendar_user"
    test_chat_id = "test_chat"

    # ==========================================
    # TEST 1: Create event
    # ==========================================
    print("\n" + "=" * 60)
    print("TEST 1: Create a calendar event")
    print("=" * 60)

    message = Message(
        user_id=test_user_id,
        chat_id=test_chat_id,
        text="Schedule a meeting with John tomorrow at 3pm for 30 minutes",
        platform="test"
    )

    print(f"\nUser: {message.text}")
    print("-" * 40)
    response = await agent.process_message(message)
    print(f"\nAgent: {response}")

    # ==========================================
    # TEST 2: List events
    # ==========================================
    print("\n" + "=" * 60)
    print("TEST 2: List upcoming events")
    print("=" * 60)

    message = Message(
        user_id=test_user_id,
        chat_id=test_chat_id,
        text="What's on my calendar?",
        platform="test"
    )

    print(f"\nUser: {message.text}")
    print("-" * 40)
    response = await agent.process_message(message)
    print(f"\nAgent: {response}")

    # ==========================================
    # TEST 3: Search events
    # ==========================================
    print("\n" + "=" * 60)
    print("TEST 3: Search for specific event")
    print("=" * 60)

    message = Message(
        user_id=test_user_id,
        chat_id=test_chat_id,
        text="Do I have any meetings with John?",
        platform="test"
    )

    print(f"\nUser: {message.text}")
    print("-" * 40)
    response = await agent.process_message(message)
    print(f"\nAgent: {response}")

    # ==========================================
    # TEST 4: Delete event
    # ==========================================
    print("\n" + "=" * 60)
    print("TEST 4: Delete an event")
    print("=" * 60)

    message = Message(
        user_id=test_user_id,
        chat_id=test_chat_id,
        text="Cancel my meeting with John",
        platform="test"
    )

    print(f"\nUser: {message.text}")
    print("-" * 40)
    response = await agent.process_message(message)
    print(f"\nAgent: {response}")

    # ==========================================
    # Cleanup
    # ==========================================
    print("\n" + "=" * 60)
    print("CLEANUP")
    print("=" * 60)

    # Delete test messages
    messages_collection = db.db["messages"]
    result = await messages_collection.delete_many({"user_id": test_user_id})
    print(f"Deleted {result.deleted_count} messages")

    await db.disconnect()

    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print("\nNote: Check your Google Calendar to verify events were created/deleted.")


if __name__ == "__main__":
    asyncio.run(test_calendar())
