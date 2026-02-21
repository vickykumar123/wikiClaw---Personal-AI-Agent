# ============================================
# TEST WEB SEARCH - Test DuckDuckGo search tools
# ============================================
#
# Usage: python scripts/test_websearch.py

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

load_dotenv()


async def test_websearch():
    """Test the web search tools."""

    print("=" * 60)
    print("TESTING WEB SEARCH TOOLS")
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

    agent = Agent(
        llm_client=llm,
        db=db,
        embeddings_client=embeddings,
        calendar_client=None  # No calendar for this test
    )
    print("   ✓ Agent initialized")

    # Test user
    test_user_id = "test_websearch_user"
    test_chat_id = "test_chat"

    # ==========================================
    # TEST 1: Web search
    # ==========================================
    print("\n" + "=" * 60)
    print("TEST 1: General web search")
    print("=" * 60)

    message = Message(
        user_id=test_user_id,
        chat_id=test_chat_id,
        text="What is the current population of India?",
        platform="test"
    )

    print(f"\nUser: {message.text}")
    print("-" * 40)
    response = await agent.process_message(message)
    print(f"\nAgent: {response}")

    # ==========================================
    # TEST 2: News search
    # ==========================================
    print("\n" + "=" * 60)
    print("TEST 2: News search")
    print("=" * 60)

    message = Message(
        user_id=test_user_id,
        chat_id=test_chat_id,
        text="What's the latest news about artificial intelligence?",
        platform="test"
    )

    print(f"\nUser: {message.text}")
    print("-" * 40)
    response = await agent.process_message(message)
    print(f"\nAgent: {response}")

    # ==========================================
    # TEST 3: Specific lookup
    # ==========================================
    print("\n" + "=" * 60)
    print("TEST 3: Specific fact lookup")
    print("=" * 60)

    message = Message(
        user_id=test_user_id,
        chat_id=test_chat_id,
        text="Who won the FIFA World Cup 2022?",
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

    messages_collection = db.db["messages"]
    result = await messages_collection.delete_many({"user_id": test_user_id})
    print(f"Deleted {result.deleted_count} messages")

    await db.disconnect()

    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_websearch())
