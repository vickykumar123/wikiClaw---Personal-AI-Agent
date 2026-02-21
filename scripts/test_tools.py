# ============================================
# TEST TOOLS - Test agent with tool calling
# ============================================
#
# Tests the hybrid approach: history automatic, memory as tools
#
# Usage: python scripts/test_tools.py

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


async def test_tools():
    """Test the agent with tool calling."""

    print("=" * 50)
    print("TESTING AGENT WITH TOOLS")
    print("=" * 50)

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
        embeddings_client=embeddings
    )
    print("   ✓ Agent initialized")

    # Test user
    test_user_id = "test_tool_user"
    test_chat_id = "test_chat"

    # 2. Test simple conversation (no tools needed)
    print("\n2. Testing simple conversation (no tools)...")
    print("-" * 40)

    message = Message(
        user_id=test_user_id,
        chat_id=test_chat_id,
        text="Hello, how are you?",
        platform="test"
    )

    print(f"   User: {message.text}")
    response = await agent.process_message(message)
    print(f"   Agent: {response}")

    # 3. Test save_memory tool
    print("\n3. Testing save_memory tool...")
    print("-" * 40)

    message = Message(
        user_id=test_user_id,
        chat_id=test_chat_id,
        text="My name is Alex and I work as a data scientist",
        platform="test"
    )

    print(f"   User: {message.text}")
    response = await agent.process_message(message)
    print(f"   Agent: {response}")

    # Wait for index to sync
    print("\n   (Waiting 5 seconds for vector index to sync...)")
    await asyncio.sleep(5)

    # 4. Test search_memory tool
    print("\n4. Testing search_memory tool...")
    print("-" * 40)

    message = Message(
        user_id=test_user_id,
        chat_id=test_chat_id,
        text="What is my name and what do I do for work?",
        platform="test"
    )

    print(f"   User: {message.text}")
    response = await agent.process_message(message)
    print(f"   Agent: {response}")

    # 5. Test another memory save
    print("\n5. Testing another save_memory...")
    print("-" * 40)

    message = Message(
        user_id=test_user_id,
        chat_id=test_chat_id,
        text="I prefer using Python and my favorite framework is FastAPI",
        platform="test"
    )

    print(f"   User: {message.text}")
    response = await agent.process_message(message)
    print(f"   Agent: {response}")

    await asyncio.sleep(5)

    # 6. Test search for preferences
    print("\n6. Testing search for preferences...")
    print("-" * 40)

    message = Message(
        user_id=test_user_id,
        chat_id=test_chat_id,
        text="What programming language do I like?",
        platform="test"
    )

    print(f"   User: {message.text}")
    response = await agent.process_message(message)
    print(f"   Agent: {response}")

    # 7. Cleanup
    print("\n7. Cleanup...")
    print("-" * 40)

    # Delete test context
    deleted_context = await db.delete_context(test_user_id)
    print(f"   Deleted {deleted_context} context entries")

    # Delete test messages
    messages_collection = db.db["messages"]
    result = await messages_collection.delete_many({"user_id": test_user_id})
    print(f"   Deleted {result.deleted_count} messages")

    await db.disconnect()

    print("\n" + "=" * 50)
    print("TEST COMPLETE")
    print("=" * 50)
    print("\nCheck the logs above to see if tools were called:")
    print("- save_memory: Should be called when user shares info")
    print("- search_memory: Should be called when user asks about themselves")


if __name__ == "__main__":
    asyncio.run(test_tools())
