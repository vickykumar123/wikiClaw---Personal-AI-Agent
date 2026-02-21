# ============================================
# TEST HIERARCHICAL AGENTS
# ============================================
#
# Usage: python scripts/test_hierarchical.py
#
# Tests the hierarchical agent system with orchestrator and sub-agents.

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
from integrations.google.gmail import GmailClient

load_dotenv()


async def test_hierarchical():
    """Test hierarchical agent system."""

    print("=" * 60)
    print("TESTING HIERARCHICAL AGENTS")
    print("=" * 60)

    # 1. Initialize components
    print("\n1. Initializing components...")

    db = MongoDB(uri=os.getenv("MONGODB_URI"))
    await db.connect()
    print("   - MongoDB connected")

    embeddings = EmbeddingsClient(api_key=os.getenv("OPENAI_API_KEY"))
    print("   - Embeddings client ready")

    llm = OllamaClient(
        host=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
        model=os.getenv("OLLAMA_MODEL", "gpt-oss:120b-cloud")
    )

    if await llm.health_check():
        print(f"   - Ollama connected ({llm.model})")
    else:
        print("   - Ollama not reachable")
        await db.disconnect()
        return

    # Initialize Google Calendar & Gmail
    calendar_client = None
    gmail_client = None
    try:
        calendar_client = GoogleCalendarClient(
            credentials_path=os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json"),
            token_path=os.getenv("GOOGLE_TOKEN_PATH", "token.json")
        )
        if calendar_client.authenticate():
            print("   - Google Calendar authenticated")
            gmail_client = GmailClient(credentials=calendar_client.creds)
            print("   - Gmail client ready")
    except Exception as e:
        print(f"   - Google services not available: {e}")

    # Create Agent
    agent = Agent(
        llm_client=llm,
        db=db,
        embeddings_client=embeddings,
        calendar_client=calendar_client,
        gmail_client=gmail_client
    )
    print("   - Agent initialized with hierarchical sub-agents")

    # Test user
    test_user_id = "test_hierarchical_user"
    test_chat_id = "test_chat"

    # ==========================================
    # TEST 1: Simple greeting (no sub-agent)
    # ==========================================
    print("\n" + "=" * 60)
    print("TEST 1: Simple greeting (no sub-agent needed)")
    print("=" * 60)

    message = Message(
        user_id=test_user_id,
        chat_id=test_chat_id,
        text="Hello!",
        platform="test"
    )

    print(f"\nUser: {message.text}")
    print("-" * 40)
    response = await agent.process_message(message)
    print(f"Agent: {response}")

    # ==========================================
    # TEST 2: Memory agent
    # ==========================================
    print("\n" + "=" * 60)
    print("TEST 2: Memory agent (save memory)")
    print("=" * 60)

    message = Message(
        user_id=test_user_id,
        chat_id=test_chat_id,
        text="Remember that my favorite programming language is Python.",
        platform="test"
    )

    print(f"\nUser: {message.text}")
    print("-" * 40)
    response = await agent.process_message(message)
    print(f"Agent: {response}")

    # ==========================================
    # TEST 3: Web agent
    # ==========================================
    print("\n" + "=" * 60)
    print("TEST 3: Web agent (web search)")
    print("=" * 60)

    message = Message(
        user_id=test_user_id,
        chat_id=test_chat_id,
        text="Search for the top news about AI today.",
        platform="test"
    )

    print(f"\nUser: {message.text}")
    print("-" * 40)
    response = await agent.process_message(message)
    print(f"Agent: {response}")

    # ==========================================
    # TEST 4: Notes agent
    # ==========================================
    print("\n" + "=" * 60)
    print("TEST 4: Notes agent (create note)")
    print("=" * 60)

    message = Message(
        user_id=test_user_id,
        chat_id=test_chat_id,
        text="Make a note: Buy groceries - milk, eggs, bread",
        platform="test"
    )

    print(f"\nUser: {message.text}")
    print("-" * 40)
    response = await agent.process_message(message)
    print(f"Agent: {response}")

    # ==========================================
    # TEST 5: Calendar agent (if available)
    # ==========================================
    if calendar_client:
        print("\n" + "=" * 60)
        print("TEST 5: Calendar agent (list events)")
        print("=" * 60)

        message = Message(
            user_id=test_user_id,
            chat_id=test_chat_id,
            text="What's on my calendar today?",
            platform="test"
        )

        print(f"\nUser: {message.text}")
        print("-" * 40)
        response = await agent.process_message(message)
        print(f"Agent: {response}")

    # ==========================================
    # TEST 6: Multiple agents (memory + notes)
    # ==========================================
    print("\n" + "=" * 60)
    print("TEST 6: Multiple agents (memory + notes)")
    print("=" * 60)

    message = Message(
        user_id=test_user_id,
        chat_id=test_chat_id,
        text="Remember my birthday is January 15th and make a note about planning a party.",
        platform="test"
    )

    print(f"\nUser: {message.text}")
    print("-" * 40)
    response = await agent.process_message(message)
    print(f"Agent: {response}")

    # ==========================================
    # TEST 7: Multiple agents (calendar + email) - if available
    # ==========================================
    if calendar_client and gmail_client:
        print("\n" + "=" * 60)
        print("TEST 7: Multiple agents (calendar + email)")
        print("=" * 60)

        message = Message(
            user_id=test_user_id,
            chat_id=test_chat_id,
            text="Schedule a meeting for tomorrow at 3pm called 'Team Sync' and send an email to test@gmail.com about it.",
            platform="test"
        )

        print(f"\nUser: {message.text}")
        print("-" * 40)
        response = await agent.process_message(message)
        print(f"Agent: {response}")

    # ==========================================
    # CLEANUP
    # ==========================================
    print("\n" + "=" * 60)
    print("CLEANUP")
    print("=" * 60)

    # Delete test messages
    messages_collection = db.db["messages"]
    result = await messages_collection.delete_many({"user_id": test_user_id})
    print(f"Deleted {result.deleted_count} messages")

    # Delete test context
    context_collection = db.db["context"]
    result = await context_collection.delete_many({"user_id": test_user_id})
    print(f"Deleted {result.deleted_count} context entries")

    # Delete test notes
    notes_collection = db.db["notes"]
    result = await notes_collection.delete_many({"user_id": test_user_id})
    print(f"Deleted {result.deleted_count} notes")

    await db.disconnect()

    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_hierarchical())
