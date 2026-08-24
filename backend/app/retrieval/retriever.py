import numpy as np

from app.retrieval.embeddings import embed_texts
from app.retrieval.models import RetrievedChunk
from app.retrieval.vector_store import FaissVectorStore


class TranscriptRetriever:
    """Retrieve transcript chunks relevant to a user query."""

    def __init__(
        self,
        vector_store: FaissVectorStore,
        embedding_model: str = "all-MiniLM-L6-v2",
        min_score: float = 0.25,
    ) -> None:
        self.vector_store = vector_store
        self.embedding_model = embedding_model
        self.min_score = min_score

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[RetrievedChunk]:
        """Retrieve chunks above the minimum relevance threshold."""

        query = query.strip()

        if not query:
            return []

        embedding = embed_texts(
            [query],
            model_name=self.embedding_model,
        )

        results = self.vector_store.search(
            embedding,
            top_k=top_k,
        )

        return [
            result
            for result in results
            if result.score >= self.min_score
        ]