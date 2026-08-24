import json
from pathlib import Path

from app.retrieval.models import Transcript


REQUIRED_FIELDS = {
    "transcript_id",
    "title",
    "transcript",
}


def load_transcripts(path: str | Path) -> list[Transcript]:
    """Load transcripts from a JSON file."""

    source_path = Path(path)

    if not source_path.exists():
        raise FileNotFoundError(
            f"Transcript file not found: {source_path}"
        )

    with source_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        records = json.load(file)

    if not isinstance(records, list):
        raise ValueError("Transcript source must contain a JSON list.")

    transcripts: list[Transcript] = []

    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ValueError(
                f"Transcript record {index} must be an object."
            )

        missing = REQUIRED_FIELDS - record.keys()

        if missing:
            raise ValueError(
                f"Transcript record {index} is missing fields: "
                f"{sorted(missing)}"
            )

        text = str(record["transcript"]).strip()

        if not text:
            raise ValueError(
                f"Transcript record {index} contains empty transcript text."
            )

        transcripts.append(
            Transcript(
                transcript_id=str(record["transcript_id"]),
                title=str(record["title"]).strip(),
                guest=(
                    str(record["guest"]).strip()
                    if record.get("guest")
                    else None
                ),
                date=(
                    str(record["date"]).strip()
                    if record.get("date")
                    else None
                ),
                source_url=(
                    str(record["source_url"]).strip()
                    if record.get("source_url")
                    else None
                ),
                text=text,
            )
        )

    return transcripts