# ============================================
# EMBEDDINGS - OpenAI embeddings client
# ============================================

import logging
from typing import List

from openai import AsyncOpenAI

from constants import EMBEDDING_MODEL, EMBEDDING_DIMENSIONS

# Set up logging
logger = logging.getLogger(__name__)


class EmbeddingsClient:
    """
    Client for generating text embeddings using OpenAI API.

    Uses text-embedding-3-small model for cost efficiency.
    Embeddings are used for semantic search in MongoDB.
    """

    def __init__(self, api_key: str):
        """
        Initialize embeddings client.

        Args:
            api_key: OpenAI API key
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = EMBEDDING_MODEL

    async def get_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector (1536 dimensions)
        """
        try:
            # Clean text
            text = text.replace("\n", " ").strip()

            if not text:
                logger.warning("Empty text provided for embedding")
                return [0.0] * EMBEDDING_DIMENSIONS

            response = await self.client.embeddings.create(
                model=self.model,
                input=text
            )

            return response.data[0].embedding

        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.

        More efficient than calling get_embedding multiple times.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        try:
            # Clean texts
            cleaned = [t.replace("\n", " ").strip() for t in texts]

            # Filter empty strings
            non_empty_indices = [i for i, t in enumerate(cleaned) if t]
            non_empty_texts = [cleaned[i] for i in non_empty_indices]

            if not non_empty_texts:
                logger.warning("All texts were empty")
                return [[0.0] * EMBEDDING_DIMENSIONS] * len(texts)

            response = await self.client.embeddings.create(
                model=self.model,
                input=non_empty_texts
            )

            # Map embeddings back to original indices
            embeddings = [[0.0] * EMBEDDING_DIMENSIONS] * len(texts)
            for i, idx in enumerate(non_empty_indices):
                embeddings[idx] = response.data[i].embedding

            return embeddings

        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise
