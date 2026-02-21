# ============================================
# TEST PARALLEL TOOLS - Test multiple tool calls in one turn
# ============================================
#
# Usage: python scripts/test_parallel_tools.py

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


async def test_parallel_tools():
    """Test multiple tool calls in a single turn."""

    print("=" * 60)
    print("TESTING PARALLEL TOOL CALLS")
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
        embeddings_client=embeddings
    )
    print("   ✓ Agent initialized")

    # Test user
    test_user_id = "test_parallel_user"
    test_chat_id = "test_chat"

    # ==========================================
    # TEST 1: Save memory + Create note
    # ==========================================
    print("\n" + "=" * 60)
    print("TEST 1: Save memory AND create note (same message)")
    print("=" * 60)

    message = Message(
        user_id=test_user_id,
        chat_id=test_chat_id,
        text="My name is Sarah and I'm a software engineer. Also create a note titled 'Career Info' with content: I work at a tech startup.",
        platform="test"
    )

    print(f"\nUser: {message.text}")
    print("\nExpected tools: save_memory + create_note")
    print("-" * 40)
    response = await agent.process_message(message)
    print(f"\nAgent: {response}")

    await asyncio.sleep(5)

    # ==========================================
    # TEST 2: Search memory + Search notes
    # ==========================================
    print("\n" + "=" * 60)
    print("TEST 2: Search memory AND search notes")
    print("=" * 60)

    message = Message(
        user_id=test_user_id,
        chat_id=test_chat_id,
        text="What do you know about me and what notes do I have about my career?",
        platform="test"
    )

    print(f"\nUser: {message.text}")
    print("\nExpected tools: search_memory + search_notes")
    print("-" * 40)
    response = await agent.process_message(message)
    print(f"\nAgent: {response}")

    # ==========================================
    # TEST 3: Multiple saves
    # ==========================================
    print("\n" + "=" * 60)
    print("TEST 3: Save multiple pieces of info")
    print("=" * 60)

    message = Message(
        user_id=test_user_id,
        chat_id=test_chat_id,
        text="Remember these things: I prefer Python, I live in San Francisco, and my favorite food is sushi.",
        platform="test"
    )

    print(f"\nUser: {message.text}")
    print("\nExpected: Multiple save_memory calls")
    print("-" * 40)
    response = await agent.process_message(message)
    print(f"\nAgent: {response}")

    await asyncio.sleep(5)

    # ==========================================
    # TEST 4: Create multiple notes
    # ==========================================
    print("\n" + "=" * 60)
    print("TEST 4: Create multiple notes at once")
    print("=" * 60)

    message = Message(
        user_id=test_user_id,
        chat_id=test_chat_id,
        text="Create two notes: First one titled 'Todo' with content 'Buy groceries', and second one titled 'Ideas' with content 'Build a chatbot'.",
        platform="test"
    )

    print(f"\nUser: {message.text}")
    print("\nExpected: Two create_note calls")
    print("-" * 40)
    response = await agent.process_message(message)
    print(f"\nAgent: {response}")

    await asyncio.sleep(3)

    # ==========================================
    # Verify data saved
    # ==========================================
    print("\n" + "=" * 60)
    print("VERIFICATION")
    print("=" * 60)

    # Check notes
    notes = await db.get_notes(test_user_id)
    print(f"\nNotes created: {len(notes)}")
    for note in notes:
        print(f"  - {note.title}: {note.content[:40]}...")

    # Check context
    from constants import COLLECTION_CONTEXT
    context_collection = db.db[COLLECTION_CONTEXT]
    context_count = await context_collection.count_documents({"user_id": test_user_id})
    print(f"\nMemory entries saved: {context_count}")

    # ==========================================
    # Cleanup
    # ==========================================
    print("\n" + "=" * 60)
    print("CLEANUP")
    print("=" * 60)

    deleted_notes = await db.delete_all_notes(test_user_id)
    print(f"Deleted {deleted_notes} notes")

    deleted_context = await db.delete_context(test_user_id)
    print(f"Deleted {deleted_context} context entries")

    messages_collection = db.db["messages"]
    result = await messages_collection.delete_many({"user_id": test_user_id})
    print(f"Deleted {result.deleted_count} messages")

    await db.disconnect()

    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print("\nNote: Whether tools are called in parallel depends on the LLM.")
    print("Some models call tools sequentially even when multiple are needed.")


if __name__ == "__main__":
    asyncio.run(test_parallel_tools())
