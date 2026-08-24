import numpy as np

from app.retrieval.models import TranscriptChunk
from app.retrieval.vector_store import FaissVectorStore


def test_vector_store_returns_metadata() -> None:
    """FAISS results should map back to source metadata."""

    chunks = [
        TranscriptChunk(
            chunk_id="chunk-1",
            transcript_id="episode-1",
            title="Prioritization",
            guest="Guest",
            date="2026-01-01",
            source_url="https://example.com/1",
            text="Product prioritization depends on customer impact.",
        ),
        TranscriptChunk(
            chunk_id="chunk-2",
            transcript_id="episode-2",
            title="Growth",
            guest="Guest 2",
            date="2026-02-01",
            source_url="https://example.com/2",
            text="Growth experiments should test explicit hypotheses.",
        ),
    ]

    embeddings = np.array(
        [
            [1.0, 0.0],
            [0.0, 1.0],
        ],
        dtype="float32",
    )

    store = FaissVectorStore(
        index_path="/tmp/test-lenny.faiss",
    )

    store.build(
        embeddings=embeddings,
        chunks=chunks,
    )

    query = np.array(
        [[1.0, 0.0]],
        dtype="float32",
    )

    results = store.search(
        query_embedding=query,
        top_k=1,
    )

    assert len(results) == 1

    assert results[0].chunk.chunk_id == "chunk-1"
    assert results[0].chunk.transcript_id == "episode-1"
    assert results[0].chunk.source_url == "https://example.com/1"
    assert results[0].score > 0.9