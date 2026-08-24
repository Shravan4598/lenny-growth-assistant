from app.retrieval.chunker import chunk_transcript
from app.retrieval.models import Transcript


def test_chunk_transcript_preserves_metadata() -> None:
    """Chunks should preserve transcript source metadata."""

    transcript = Transcript(
        transcript_id="episode-001",
        title="Product Strategy",
        guest="Guest",
        date="2026-01-01",
        source_url="https://example.com",
        text=" ".join(["word"] * 100),
    )

    chunks = chunk_transcript(
        transcript,
        chunk_size=30,
        overlap=5,
    )

    assert len(chunks) > 1

    for chunk in chunks:
        assert chunk.transcript_id == "episode-001"
        assert chunk.title == "Product Strategy"
        assert chunk.source_url == "https://example.com"


def test_invalid_overlap_fails() -> None:
    """Overlap must be smaller than the chunk size."""

    transcript = Transcript(
        transcript_id="episode-001",
        title="Test",
        guest=None,
        date=None,
        source_url=None,
        text="some text",
    )

    try:
        chunk_transcript(
            transcript,
            chunk_size=10,
            overlap=10,
        )
    except ValueError:
        return

    raise AssertionError(
        "Expected ValueError for invalid overlap."
    )