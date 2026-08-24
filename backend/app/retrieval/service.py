from pathlib import Path

from app.core.exceptions import AppError
from app.retrieval.chunker import chunk_transcript
from app.retrieval.cleaner import clean_transcript
from app.retrieval.embeddings import embed_texts
from app.retrieval.lenny_loader import LennyRepositoryLoader
from app.retrieval.loader import load_transcripts
from app.retrieval.models import RetrievedChunk, Transcript
from app.retrieval.retriever import TranscriptRetriever
from app.retrieval.vector_store import FaissVectorStore


class RetrievalService:
    """High-level transcript ingestion and retrieval service."""

    def __init__(
        self,
        index_path: str | Path,
        retrieval_embedding_model: str = "all-MiniLM-L6-v2",
        min_score: float = 0.25,
    ) -> None:
        self.vector_store = FaissVectorStore(
            index_path=index_path,
        )

        self.retriever = TranscriptRetriever(
            vector_store=self.vector_store,
            retrieval_embedding_model=retrieval_embedding_model,
            min_score=min_score,
        )

    def ingest(
        self,
        source_path: str | Path,
    ) -> int:
        """Ingest transcripts from a JSON source."""

        transcripts = load_transcripts(source_path)

        return self._index_transcripts(transcripts)

    def ingest_lenny_repository(
        self,
        repository_path: str | Path,
        content_types: set[str] | None = None,
    ) -> int:
        """Ingest content from Lenny's Data repository."""

        loader = LennyRepositoryLoader(
            repository_path=repository_path,
            content_types=content_types,
        )

        transcripts = loader.load()

        return self._index_transcripts(transcripts)

    def _index_transcripts(
        self,
        transcripts: list[Transcript],
    ) -> int:
        """Clean, chunk, embed and index transcripts."""

        if not transcripts:
            raise AppError(
                status_code=400,
                code="NO_TRANSCRIPTS",
                message="No transcripts were provided for indexing.",
            )

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
            raise AppError(
                status_code=400,
                code="NO_SEARCHABLE_CHUNKS",
                message="No searchable transcript chunks were produced.",
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

        try:
            self.vector_store.load()

        except FileNotFoundError as exc:
            raise AppError(
                status_code=503,
                code="VECTOR_INDEX_NOT_FOUND",
                message=(
                    "Retrieval index is not available. "
                    "Build the index before using chat."
                ),
            ) from exc

        except ValueError as exc:
            raise AppError(
                status_code=500,
                code="INVALID_VECTOR_INDEX",
                message=(
                    "The retrieval index or metadata is invalid."
                ),
            ) from exc

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[RetrievedChunk]:
        """Retrieve relevant transcript chunks."""

        query = query.strip()

        if not query:
            raise AppError(
                status_code=400,
                code="INVALID_RETRIEVAL_QUERY",
                message="Retrieval query cannot be empty.",
            )

        if top_k <= 0:
            raise AppError(
                status_code=400,
                code="INVALID_TOP_K",
                message="top_k must be greater than zero.",
            )

        try:
            return self.retriever.retrieve(
                query=query,
                top_k=top_k,
            )

        except RuntimeError as exc:
            raise AppError(
                status_code=503,
                code="RETRIEVAL_SERVICE_UNAVAILABLE",
                message="Retrieval service is not available.",
            ) from exc