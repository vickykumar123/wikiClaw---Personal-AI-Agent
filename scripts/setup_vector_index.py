# ============================================
# SETUP VECTOR INDEX - Create MongoDB Atlas Vector Search Indexes
# ============================================
#
# Run this script to create vector search indexes on collections.
# Requires MongoDB Atlas M10+ cluster or free tier with Vector Search enabled.
#
# Usage: python scripts/setup_vector_index.py

import os
import sys
import time

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from pymongo import MongoClient
from pymongo.operations import SearchIndexModel
from dotenv import load_dotenv

from constants import (
    COLLECTION_CONTEXT,
    COLLECTION_NOTES,
    VECTOR_INDEX_NAME,
    NOTES_INDEX_NAME,
    EMBEDDING_DIMENSIONS
)

# Load environment variables
load_dotenv()


def create_index(db, collection_name: str, index_name: str, filter_fields: list):
    """
    Create a vector search index on a collection.

    Args:
        db: MongoDB database
        collection_name: Name of the collection
        index_name: Name for the index
        filter_fields: List of fields to use as filters

    Returns:
        "created" if new index created
        "exists" if index already exists
        "error" if creation failed
    """
    collection = db[collection_name]

    # Ensure collection exists
    if collection_name not in db.list_collection_names():
        print(f"  Collection '{collection_name}' does not exist. Creating...")
        db.create_collection(collection_name)
        print(f"  Collection '{collection_name}' created.")

    # Check if index already exists
    existing_indexes = list(collection.list_search_indexes())
    for idx in existing_indexes:
        if idx.get("name") == index_name:
            print(f"  Index '{index_name}' already exists. Skipping.")
            return "exists"

    # Build fields definition
    fields = [
        {
            "type": "vector",
            "path": "embedding",
            "numDimensions": EMBEDDING_DIMENSIONS,
            "similarity": "cosine"
        }
    ]

    # Add filter fields
    for field in filter_fields:
        fields.append({
            "type": "filter",
            "path": field
        })

    # Define the vector search index
    search_index_model = SearchIndexModel(
        definition={"fields": fields},
        name=index_name,
        type="vectorSearch"
    )

    # Create the index
    print(f"  Creating index '{index_name}'...")
    print(f"    Dimensions: {EMBEDDING_DIMENSIONS}")
    print(f"    Filters: {', '.join(filter_fields)}")

    try:
        result = collection.create_search_index(model=search_index_model)
        print(f"  Index creation initiated: {result}")
        return "created"
    except Exception as e:
        print(f"  Error creating index: {e}")
        return "error"


def wait_for_indexes(db, indexes_to_check: list):
    """Wait for indexes to become ready."""
    print("\nWaiting for indexes to become ready...")
    max_wait = 120  # seconds
    waited = 0

    pending = indexes_to_check.copy()

    while waited < max_wait and pending:
        for collection_name, index_name in pending.copy():
            collection = db[collection_name]
            indexes = list(collection.list_search_indexes())

            for idx in indexes:
                if idx.get("name") == index_name:
                    status = idx.get("status", "unknown")
                    if status == "READY":
                        print(f"  {index_name}: READY")
                        pending.remove((collection_name, index_name))
                    else:
                        print(f"  {index_name}: {status}...")

        if pending:
            time.sleep(5)
            waited += 5

    if pending:
        print(f"\nSome indexes still building after {max_wait}s.")
        print("They will be available once status shows 'READY' in Atlas.")
    else:
        print("\nAll indexes ready!")


def main():
    """Create all vector search indexes."""
    # Get MongoDB URI
    mongodb_uri = os.getenv("MONGODB_URI")
    if not mongodb_uri:
        print("Error: MONGODB_URI not found in .env")
        sys.exit(1)

    # Connect to MongoDB
    print("Connecting to MongoDB Atlas...")
    client = MongoClient(mongodb_uri)
    db = client["agent_db"]
    print("Connected.\n")

    indexes_to_wait = []

    # 1. Create context index
    print(f"1. Setting up {COLLECTION_CONTEXT} collection...")
    result = create_index(
        db,
        COLLECTION_CONTEXT,
        VECTOR_INDEX_NAME,
        filter_fields=["user_id", "type"]
    )
    if result == "created":
        indexes_to_wait.append((COLLECTION_CONTEXT, VECTOR_INDEX_NAME))

    # 2. Create notes index
    print(f"\n2. Setting up {COLLECTION_NOTES} collection...")
    result = create_index(
        db,
        COLLECTION_NOTES,
        NOTES_INDEX_NAME,
        filter_fields=["user_id", "tags"]
    )
    if result == "created":
        indexes_to_wait.append((COLLECTION_NOTES, NOTES_INDEX_NAME))

    # Wait only for newly created indexes
    if indexes_to_wait:
        wait_for_indexes(db, indexes_to_wait)
    else:
        print("\nNo new indexes to create.")

    client.close()
    print("\nSetup complete!")


if __name__ == "__main__":
    main()
