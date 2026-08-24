from dataclasses import dataclass


@dataclass(frozen=True)
class Transcript:
    """Normalized transcript."""

    transcript_id: str
    title: str
    guest: str | None
    date: str | None
    source_url: str | None
    text: str


@dataclass(frozen=True)
class TranscriptChunk:
    """A searchable section of a transcript."""

    chunk_id: str
    transcript_id: str
    title: str
    guest: str | None
    date: str | None
    source_url: str | None
    text: str


@dataclass(frozen=True)
class RetrievedChunk:
    """Retrieved transcript chunk with similarity score."""

    chunk: TranscriptChunk
    score: float