# ============================================
# TEST NOTES - Test notes tools
# ============================================
#
# Usage: python scripts/test_notes.py

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


async def test_notes():
    """Test the notes tools."""

    print("=" * 50)
    print("TESTING NOTES TOOLS")
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
    test_user_id = "test_notes_user"
    test_chat_id = "test_chat"

    # 2. Test create_note
    print("\n2. Testing create_note...")
    print("-" * 40)

    message = Message(
        user_id=test_user_id,
        chat_id=test_chat_id,
        text="Create a note titled 'Meeting Notes' with content: Discussed project timeline with team. Deadline is next Friday. Tag it as work and important.",
        platform="test"
    )

    print(f"   User: {message.text[:60]}...")
    response = await agent.process_message(message)
    print(f"   Agent: {response}")

    # Wait for index sync
    print("\n   (Waiting 5 seconds for index sync...)")
    await asyncio.sleep(5)

    # 3. Create another note
    print("\n3. Creating another note...")
    print("-" * 40)

    message = Message(
        user_id=test_user_id,
        chat_id=test_chat_id,
        text="Make a note: Shopping list - milk, eggs, bread, butter. Tag it as personal.",
        platform="test"
    )

    print(f"   User: {message.text}")
    response = await agent.process_message(message)
    print(f"   Agent: {response}")

    await asyncio.sleep(5)

    # 4. Test list_notes
    print("\n4. Testing list_notes...")
    print("-" * 40)

    message = Message(
        user_id=test_user_id,
        chat_id=test_chat_id,
        text="Show me all my notes",
        platform="test"
    )

    print(f"   User: {message.text}")
    response = await agent.process_message(message)
    print(f"   Agent: {response}")

    # 5. Test search_notes
    print("\n5. Testing search_notes...")
    print("-" * 40)

    message = Message(
        user_id=test_user_id,
        chat_id=test_chat_id,
        text="Find my note about the project deadline",
        platform="test"
    )

    print(f"   User: {message.text}")
    response = await agent.process_message(message)
    print(f"   Agent: {response}")

    # 6. Test delete_note
    print("\n6. Testing delete_note...")
    print("-" * 40)

    message = Message(
        user_id=test_user_id,
        chat_id=test_chat_id,
        text="Delete my shopping list note",
        platform="test"
    )

    print(f"   User: {message.text}")
    response = await agent.process_message(message)
    print(f"   Agent: {response}")

    # 7. Verify deletion
    print("\n7. Verifying deletion...")
    print("-" * 40)

    message = Message(
        user_id=test_user_id,
        chat_id=test_chat_id,
        text="List all my notes",
        platform="test"
    )

    print(f"   User: {message.text}")
    response = await agent.process_message(message)
    print(f"   Agent: {response}")

    # 8. Cleanup
    print("\n8. Cleanup...")
    print("-" * 40)

    # Delete test notes
    deleted_notes = await db.delete_all_notes(test_user_id)
    print(f"   Deleted {deleted_notes} notes")

    # Delete test context (from save_memory if used)
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


if __name__ == "__main__":
    asyncio.run(test_notes())
