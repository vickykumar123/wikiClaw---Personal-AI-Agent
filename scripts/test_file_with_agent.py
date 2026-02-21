# ============================================
# TEST FILE WITH AGENT
# ============================================
#
# Usage: python scripts/test_file_with_agent.py
#
# Tests file processing + LLM analysis.

import asyncio
import os
import sys
import tempfile

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
from utils.file_processor import process_file

load_dotenv()


async def test_file_with_agent():
    """Test file processing with LLM analysis."""

    print("=" * 60)
    print("TESTING FILE PROCESSING WITH AGENT")
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

    # Create Agent (without calendar/gmail for this test)
    agent = Agent(
        llm_client=llm,
        db=db,
        embeddings_client=embeddings,
        calendar_client=None,
        gmail_client=None
    )
    print("   - Agent initialized")

    # Test user
    test_user_id = "test_file_user"
    test_chat_id = "test_chat"

    # ==========================================
    # TEST 1: Text file analysis
    # ==========================================
    print("\n" + "=" * 60)
    print("TEST 1: Text File Analysis")
    print("=" * 60)

    # Create test text file
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".txt",
        delete=False
    ) as f:
        f.write("Meeting Notes - Project Alpha\n")
        f.write("Date: February 21, 2026\n\n")
        f.write("Attendees: John, Sarah, Mike\n\n")
        f.write("Discussion Points:\n")
        f.write("1. Project timeline needs to be extended by 2 weeks\n")
        f.write("2. Budget approved for additional resources\n")
        f.write("3. Next milestone: Complete testing by March 15\n\n")
        f.write("Action Items:\n")
        f.write("- John: Update project schedule\n")
        f.write("- Sarah: Hire 2 more developers\n")
        f.write("- Mike: Prepare test environment\n")
        tmp_path = f.name

    # Process file
    result = process_file(tmp_path)
    os.unlink(tmp_path)

    if result.success:
        # Build message like Telegram bot does
        file_context = f"[File: meeting_notes.txt]\n\n{result.text}\n\nUser request: Summarize this file."

        message = Message(
            user_id=test_user_id,
            chat_id=test_chat_id,
            text=file_context,
            platform="test"
        )

        print(f"\nFile content:\n{result.text[:200]}...")
        print("-" * 40)
        print("User request: Summarize this file.")
        print("-" * 40)

        response = await agent.process_message(message)
        print(f"\nAgent: {response}")

    # ==========================================
    # TEST 2: CSV data analysis
    # ==========================================
    print("\n" + "=" * 60)
    print("TEST 2: CSV Data Analysis")
    print("=" * 60)

    # Create test CSV file
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".csv",
        delete=False
    ) as f:
        f.write("Product,Sales,Revenue\n")
        f.write("Laptop,150,225000\n")
        f.write("Phone,300,180000\n")
        f.write("Tablet,80,48000\n")
        f.write("Watch,200,60000\n")
        f.write("Headphones,450,45000\n")
        tmp_path = f.name

    # Process file
    result = process_file(tmp_path)
    os.unlink(tmp_path)

    if result.success:
        file_context = f"[File: sales_data.csv]\n\n{result.text}\n\nUser request: Which product has the highest revenue?"

        message = Message(
            user_id=test_user_id,
            chat_id=test_chat_id,
            text=file_context,
            platform="test"
        )

        print(f"\nFile content:\n{result.text}")
        print("-" * 40)
        print("User request: Which product has the highest revenue?")
        print("-" * 40)

        response = await agent.process_message(message)
        print(f"\nAgent: {response}")

    # ==========================================
    # TEST 3: Code explanation
    # ==========================================
    print("\n" + "=" * 60)
    print("TEST 3: Code Explanation")
    print("=" * 60)

    # Create test Python file
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".py",
        delete=False
    ) as f:
        f.write("def fibonacci(n):\n")
        f.write("    if n <= 1:\n")
        f.write("        return n\n")
        f.write("    return fibonacci(n-1) + fibonacci(n-2)\n\n")
        f.write("# Calculate first 10 fibonacci numbers\n")
        f.write("for i in range(10):\n")
        f.write("    print(fibonacci(i))\n")
        tmp_path = f.name

    # Process file
    result = process_file(tmp_path)
    os.unlink(tmp_path)

    if result.success:
        file_context = f"[File: fibonacci.py]\n\n{result.text}\n\nUser request: Explain what this code does."

        message = Message(
            user_id=test_user_id,
            chat_id=test_chat_id,
            text=file_context,
            platform="test"
        )

        print(f"\nFile content:\n{result.text}")
        print("-" * 40)
        print("User request: Explain what this code does.")
        print("-" * 40)

        response = await agent.process_message(message)
        print(f"\nAgent: {response}")

    # ==========================================
    # CLEANUP
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
    asyncio.run(test_file_with_agent())
