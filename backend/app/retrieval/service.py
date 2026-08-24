from pathlib import Path

from app.retrieval.cleaner import clean_transcript
from app.retrieval.chunker import chunk_transcript
from app.retrieval.embeddings import embed_texts
from app.retrieval.loader import load_transcripts
from app.retrieval.models import RetrievedChunk
from app.retrieval.retriever import TranscriptRetriever
from app.retrieval.vector_store import FaissVectorStore


class RetrievalService:
    """High-level transcript ingestion and retrieval service."""

    def __init__(
        self,
        index_path: str | Path,
        embedding_model: str = "all-MiniLM-L6-v2",
        min_score: float = 0.25,
    ) -> None:
        self.vector_store = FaissVectorStore(
            index_path=index_path,
        )

        self.retriever = TranscriptRetriever(
            vector_store=self.vector_store,
            embedding_model=embedding_model,
            min_score=min_score,
        )

    def ingest(
        self,
        source_path: str | Path,
    ) -> int:
        """Load, clean, chunk, embed and index transcripts."""

        transcripts = load_transcripts(source_path)

        cleaned = [
            clean_transcript(transcript)
            for transcript in transcripts
        ]

        chunks = []

        for transcript in cleaned:
            chunks.extend(
                chunk_transcript(transcript)
            )

        if not chunks:
            raise ValueError(
                "No searchable transcript chunks were produced."
            )

        embeddings = embed_texts(
            [chunk.text for chunk in chunks],
            model_name=self.retriever.embedding_model,
        )

        self.vector_store.build(
            embeddings=embeddings,
            chunks=chunks,
        )

        self.vector_store.save()

        return len(chunks)

    def load(self) -> None:
        """Load an existing persisted index."""

        self.vector_store.load()

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[RetrievedChunk]:
        """Retrieve relevant transcript chunks."""

        return self.retriever.retrieve(
            query=query,
            top_k=top_k,
        )