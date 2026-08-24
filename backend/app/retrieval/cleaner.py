import re

from app.retrieval.models import Transcript


_WHITESPACE_RE = re.compile(r"\s+")
_BRACKET_RE = re.compile(r"\[[^\]]*\]")


def clean_text(text: str) -> str:
    """Normalize transcript text for retrieval."""

    text = _BRACKET_RE.sub(" ", text)

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    text = _WHITESPACE_RE.sub(" ", text)

    return text.strip()


def clean_transcript(transcript: Transcript) -> Transcript:
    """Return a cleaned copy of a transcript."""

    return Transcript(
        transcript_id=transcript.transcript_id,
        title=transcript.title.strip(),
        guest=transcript.guest.strip()
        if transcript.guest
        else None,
        date=transcript.date,
        source_url=transcript.source_url,
        text=clean_text(transcript.text),
    )