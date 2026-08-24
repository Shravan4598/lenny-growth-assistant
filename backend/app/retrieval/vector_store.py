import json
from pathlib import Path

import faiss
import numpy as np

from app.core.exceptions import AppError
from app.retrieval.models import RetrievedChunk, TranscriptChunk


class FaissVectorStore:
    """Local FAISS vector store with JSON metadata."""

    def __init__(self, index_path: str | Path) -> None:
        self.index_path = Path(index_path)

        self.metadata_path = self.index_path.with_suffix(
            ".metadata.json"
        )

        self.index: faiss.Index | None = None
        self.chunks: list[TranscriptChunk] = []

    def build(
        self,
        embeddings: np.ndarray,
        chunks: list[TranscriptChunk],
    ) -> None:
        """Build an in-memory FAISS index."""

        if not chunks:
            raise AppError(
                status_code=400,
                code="EMPTY_VECTOR_INDEX",
                message="Cannot build index with no chunks.",
            )

        if embeddings.ndim != 2:
            raise AppError(
                status_code=400,
                code="INVALID_EMBEDDINGS",
                message="Embeddings must be a 2-dimensional array.",
            )

        if embeddings.shape[0] != len(chunks):
            raise AppError(
                status_code=400,
                code="EMBEDDING_CHUNK_MISMATCH",
                message=(
                    "Number of embeddings must equal "
                    "number of transcript chunks."
                ),
            )

        if embeddings.shape[1] <= 0:
            raise AppError(
                status_code=400,
                code="INVALID_EMBEDDING_DIMENSION",
                message="Embedding dimension must be greater than zero.",
            )

        dimension = embeddings.shape[1]

        index = faiss.IndexFlatIP(dimension)

        index.add(embeddings)

        self.index = index
        self.chunks = chunks

    def save(self) -> None:
        """Persist FAISS index and chunk metadata."""

        if self.index is None:
            raise AppError(
                status_code=500,
                code="VECTOR_INDEX_NOT_INITIALIZED",
                message="Cannot save an uninitialized FAISS index.",
            )

        try:
            self.index_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            faiss.write_index(
                self.index,
                str(self.index_path),
            )

            metadata = [
                {
                    "chunk_id": chunk.chunk_id,
                    "transcript_id": chunk.transcript_id,
                    "title": chunk.title,
                    "guest": chunk.guest,
                    "date": chunk.date,
                    "source_url": chunk.source_url,
                    "text": chunk.text,
                }
                for chunk in self.chunks
            ]

            with self.metadata_path.open(
                "w",
                encoding="utf-8",
            ) as file:
                json.dump(
                    metadata,
                    file,
                    ensure_ascii=False,
                    indent=2,
                )

        except OSError as exc:
            raise AppError(
                status_code=500,
                code="VECTOR_INDEX_SAVE_FAILED",
                message="Failed to save the retrieval index.",
            ) from exc

        except (ValueError, TypeError) as exc:
            raise AppError(
                status_code=500,
                code="VECTOR_METADATA_SAVE_FAILED",
                message="Failed to save vector metadata.",
            ) from exc

    def load(self) -> None:
        """Load a persisted FAISS index and metadata."""

        if not self.index_path.exists():
            raise FileNotFoundError(
                f"FAISS index not found: {self.index_path}"
            )

        if not self.metadata_path.exists():
            raise FileNotFoundError(
                f"Metadata file not found: {self.metadata_path}"
            )

        try:
            self.index = faiss.read_index(
                str(self.index_path)
            )

            with self.metadata_path.open(
                "r",
                encoding="utf-8",
            ) as file:
                metadata = json.load(file)

        except OSError as exc:
            raise AppError(
                status_code=500,
                code="VECTOR_INDEX_LOAD_FAILED",
                message="Failed to load the retrieval index.",
            ) from exc

        except (ValueError, json.JSONDecodeError) as exc:
            raise AppError(
                status_code=500,
                code="INVALID_VECTOR_METADATA",
                message="Vector metadata is invalid.",
            ) from exc

        if not isinstance(metadata, list):
            raise AppError(
                status_code=500,
                code="INVALID_VECTOR_METADATA",
                message="Vector metadata must contain a JSON list.",
            )

        try:
            self.chunks = [
                TranscriptChunk(**item)
                for item in metadata
            ]

        except (TypeError, ValueError) as exc:
            raise AppError(
                status_code=500,
                code="INVALID_TRANSCRIPT_METADATA",
                message=(
                    "Stored transcript metadata has an invalid format."
                ),
            ) from exc

        if self.index is None:
            raise AppError(
                status_code=500,
                code="VECTOR_INDEX_LOAD_FAILED",
                message="FAISS index could not be initialized.",
            )

        if self.index.ntotal != len(self.chunks):
            raise AppError(
                status_code=500,
                code="VECTOR_METADATA_MISMATCH",
                message=(
                    "FAISS index and metadata contain different "
                    "numbers of records."
                ),
            )

    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
    ) -> list[RetrievedChunk]:
        """Return the most similar chunks."""

        if self.index is None:
            raise AppError(
                status_code=503,
                code="VECTOR_INDEX_NOT_INITIALIZED",
                message="Vector index has not been initialized.",
            )

        if self.index.ntotal == 0:
            return []

        if query_embedding.ndim != 2:
            raise AppError(
                status_code=400,
                code="INVALID_QUERY_EMBEDDING",
                message=(
                    "Query embedding must be a 2-dimensional array."
                ),
            )

        if query_embedding.shape[1] != self.index.d:
            raise AppError(
                status_code=400,
                code="EMBEDDING_DIMENSION_MISMATCH",
                message=(
                    "Query embedding dimension does not match "
                    "the vector index."
                ),
            )

        if top_k <= 0:
            raise AppError(
                status_code=400,
                code="INVALID_TOP_K",
                message="top_k must be greater than zero.",
            )

        top_k = min(
            top_k,
            self.index.ntotal,
        )

        try:
            scores, indices = self.index.search(
                query_embedding,
                top_k,
            )

        except (RuntimeError, ValueError) as exc:
            raise AppError(
                status_code=503,
                code="VECTOR_SEARCH_FAILED",
                message="Vector search failed.",
            ) from exc

        results: list[RetrievedChunk] = []

        for score, index in zip(
            scores[0],
            indices[0],
        ):
            if index < 0:
                continue

            results.append(
                RetrievedChunk(
                    chunk=self.chunks[index],
                    score=float(score),
                )
            )

        return results