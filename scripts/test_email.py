# ============================================
# TEST EMAIL - Test sending email via Gmail
# ============================================
#
# Usage: python scripts/test_email.py

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


async def test_email():
    """Test sending email."""

    print("=" * 60)
    print("TESTING EMAIL")
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

    # Initialize Google Calendar & Gmail
    calendar_client = GoogleCalendarClient(
        credentials_path=os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json"),
        token_path=os.getenv("GOOGLE_TOKEN_PATH", "token.json")
    )

    gmail_client = None
    if calendar_client.authenticate():
        print("   ✓ Google authenticated")
        gmail_client = GmailClient(credentials=calendar_client.creds)
        print("   ✓ Gmail client ready")
    else:
        print("   ✗ Google auth failed")
        await db.disconnect()
        return

    agent = Agent(
        llm_client=llm,
        db=db,
        embeddings_client=embeddings,
        calendar_client=calendar_client,
        gmail_client=gmail_client
    )
    print("   ✓ Agent initialized")

    # Test user
    test_user_id = "test_email_user"
    test_chat_id = "test_chat"

    # ==========================================
    # TEST: Send email
    # ==========================================
    print("\n" + "=" * 60)
    print("TEST: Send email")
    print("=" * 60)

    message = Message(
        user_id=test_user_id,
        chat_id=test_chat_id,
        text="Send an email to venomvvk@gmail.com with subject 'Test from AI Agent' and body 'Hello! This is a test email sent from your personal AI agent. It is working!'",
        platform="test"
    )

    print(f"\nUser: {message.text}")
    print("-" * 40)
    response = await agent.process_message(message)
    print(f"\nAgent: {response}")

    # Cleanup
    print("\n" + "=" * 60)
    print("CLEANUP")
    print("=" * 60)

    messages_collection = db.db["messages"]
    result = await messages_collection.delete_many({"user_id": test_user_id})
    print(f"Deleted {result.deleted_count} messages")

    await db.disconnect()

    print("\n" + "=" * 60)
    print("TEST COMPLETE - Check your inbox!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_email())
