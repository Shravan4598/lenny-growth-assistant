import json
from pathlib import Path

import faiss
import numpy as np

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

        if len(chunks) == 0:
            raise ValueError("Cannot build index with no chunks.")

        if embeddings.shape[0] != len(chunks):
            raise ValueError(
                "Number of embeddings must equal number of chunks."
            )

        dimension = embeddings.shape[1]

        index = faiss.IndexFlatIP(dimension)

        index.add(embeddings)

        self.index = index
        self.chunks = chunks

    def save(self) -> None:
        """Persist FAISS index and chunk metadata."""

        if self.index is None:
            raise RuntimeError(
                "Cannot save an uninitialized FAISS index."
            )

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

        self.index = faiss.read_index(
            str(self.index_path)
        )

        with self.metadata_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            metadata = json.load(file)

        self.chunks = [
            TranscriptChunk(**item)
            for item in metadata
        ]

        if self.index.ntotal != len(self.chunks):
            raise ValueError(
                "FAISS index and metadata contain different "
                "numbers of records."
            )

    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
    ) -> list[RetrievedChunk]:
        """Return the most similar chunks."""

        if self.index is None:
            raise RuntimeError(
                "Vector index has not been initialized."
            )

        if self.index.ntotal == 0:
            return []

        top_k = min(
            max(top_k, 1),
            self.index.ntotal,
        )

        scores, indices = self.index.search(
            query_embedding,
            top_k,
        )

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