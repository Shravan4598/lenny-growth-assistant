from app.retrieval.models import Transcript, TranscriptChunk


DEFAULT_CHUNK_WORDS = 450
DEFAULT_OVERLAP_WORDS = 75


def chunk_transcript(
    transcript: Transcript,
    chunk_size: int = DEFAULT_CHUNK_WORDS,
    overlap: int = DEFAULT_OVERLAP_WORDS,
) -> list[TranscriptChunk]:
    """Split a transcript into overlapping word-based chunks."""

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    if overlap < 0:
        raise ValueError("overlap cannot be negative.")

    if overlap >= chunk_size:
        raise ValueError(
            "overlap must be smaller than chunk_size."
        )

    words = transcript.text.split()

    if not words:
        return []

    chunks: list[TranscriptChunk] = []

    step = chunk_size - overlap

    for start in range(0, len(words), step):
        end = min(start + chunk_size, len(words))

        chunk_words = words[start:end]

        if not chunk_words:
            continue

        chunk_number = len(chunks) + 1

        chunks.append(
            TranscriptChunk(
                chunk_id=(
                    f"{transcript.transcript_id}"
                    f"-chunk-{chunk_number:04d}"
                ),
                transcript_id=transcript.transcript_id,
                title=transcript.title,
                guest=transcript.guest,
                date=transcript.date,
                source_url=transcript.source_url,
                text=" ".join(chunk_words),
            )
        )

        if end >= len(words):
            break

    return chunks