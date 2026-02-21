# ============================================
# TEST VECTOR SEARCH - Verify MongoDB + Embeddings working
# ============================================
#
# Usage: python scripts/test_vector_search.py

import asyncio
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from dotenv import load_dotenv

from database.mongodb import MongoDB
from memory.embeddings import EmbeddingsClient
from schemas.context import ContextSchema

load_dotenv()


async def test_vector_search():
    """Test saving context and searching with vector similarity."""

    # 1. Connect to MongoDB
    print("1. Connecting to MongoDB...")
    db = MongoDB(uri=os.getenv("MONGODB_URI"))
    await db.connect()

    # 2. Create embeddings client
    print("2. Creating embeddings client...")
    embeddings = EmbeddingsClient(api_key=os.getenv("OPENAI_API_KEY"))

    test_user_id = "test_user_123"

    # 3. Check if test data already exists
    collection = db.db["context"]
    existing_count = await collection.count_documents({"user_id": test_user_id})

    if existing_count > 0:
        print(f"3. Test data already exists ({existing_count} documents). Skipping save.")
    else:
        print("3. Saving test context entries...")

        test_contexts = [
            ("profile", "My name is John and I am a software developer"),
            ("preference", "I prefer Python over JavaScript"),
            ("fact", "I have a dog named Max"),
            ("fact", "I live in New York City"),
            ("preference", "I like to drink coffee in the morning"),
        ]

        for context_type, value in test_contexts:
            # Generate embedding
            embedding = await embeddings.get_embedding(value)

            # Create and save context
            context = ContextSchema(
                user_id=test_user_id,
                type=context_type,
                value=value,
                embedding=embedding
            )
            doc_id = await db.save_context(context)
            print(f"   Saved: [{context_type}] {value[:40]}... (id: {doc_id[:8]}...)")

    # 4. Verify documents exist
    print("\n4. Verifying documents in collection...")
    count = await collection.count_documents({"user_id": test_user_id})
    print(f"   Found {count} documents for user {test_user_id}")

    # 5. Wait for index to sync new documents
    print("\n5. Waiting 15 seconds for index to sync new documents...")
    await asyncio.sleep(15)

    # 6. Test raw vector search (debug)
    print("\n6. Testing raw vector search (without user filter)...")
    test_query = "What is my name?"
    query_embedding = await embeddings.get_embedding(test_query)

    # Raw pipeline without filter
    pipeline = [
        {
            "$vectorSearch": {
                "index": "context_index",
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": 50,
                "limit": 5
            }
        },
        {
            "$project": {
                "user_id": 1,
                "type": 1,
                "value": 1,
                "score": {"$meta": "vectorSearchScore"}
            }
        }
    ]

    cursor = collection.aggregate(pipeline)
    raw_results = await cursor.to_list(length=5)
    print(f"   Raw results: {len(raw_results)}")
    for doc in raw_results:
        print(f"   - [{doc.get('type')}] {doc.get('value')[:50]}... (score: {doc.get('score', 'N/A')})")

    # 7. Test vector search with filter
    print("\n7. Testing vector search with user filter...")

    test_queries = [
        "What is my name?",
        "Do I have any pets?",
        "What programming language do I use?",
        "Where do I live?",
    ]

    for query in test_queries:
        print(f"\n   Query: '{query}'")

        # Generate query embedding
        query_embedding = await embeddings.get_embedding(query)

        # Search for similar context
        results = await db.search_context(test_user_id, query_embedding, limit=2)

        if results:
            for i, ctx in enumerate(results, 1):
                print(f"   Result {i}: [{ctx.type}] {ctx.value}")
        else:
            print("   No results found")

    # 8. Cleanup (optional - comment out to keep test data)
    # print("\n8. Cleanup...")
    # deleted = await db.delete_context(test_user_id)
    # print(f"   Deleted {deleted} test documents")
    print("\n8. Skipping cleanup (keeping test data for verification)")

    # Disconnect
    await db.disconnect()
    print("\nTest complete!")


if __name__ == "__main__":
    asyncio.run(test_vector_search())
