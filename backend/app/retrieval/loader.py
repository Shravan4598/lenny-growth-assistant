import json
from pathlib import Path

from app.core.exceptions import AppError
from app.retrieval.models import Transcript


REQUIRED_FIELDS = {
    "transcript_id",
    "title",
    "transcript",
}


def load_transcripts(
    path: str | Path,
) -> list[Transcript]:
    """Load transcripts from a JSON file."""

    source_path = Path(path)

    if not source_path.exists():
        raise AppError(
            status_code=404,
            code="TRANSCRIPT_FILE_NOT_FOUND",
            message=(
                f"Transcript file not found: {source_path}"
            ),
        )

    if not source_path.is_file():
        raise AppError(
            status_code=400,
            code="INVALID_TRANSCRIPT_PATH",
            message=(
                f"Transcript path is not a file: {source_path}"
            ),
        )

    try:
        with source_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            records = json.load(file)

    except json.JSONDecodeError as exc:
        raise AppError(
            status_code=500,
            code="INVALID_TRANSCRIPT_JSON",
            message=(
                f"Transcript file contains invalid JSON: "
                f"{source_path}"
            ),
        ) from exc

    except OSError as exc:
        raise AppError(
            status_code=500,
            code="TRANSCRIPT_FILE_READ_FAILED",
            message=(
                f"Unable to read transcript file: "
                f"{source_path}"
            ),
        ) from exc

    if not isinstance(records, list):
        raise AppError(
            status_code=500,
            code="INVALID_TRANSCRIPT_STRUCTURE",
            message=(
                "Transcript source must contain a JSON list."
            ),
        )

    transcripts: list[Transcript] = []

    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise AppError(
                status_code=500,
                code="INVALID_TRANSCRIPT_RECORD",
                message=(
                    f"Transcript record {index} must be an object."
                ),
            )

        missing = REQUIRED_FIELDS - record.keys()

        if missing:
            raise AppError(
                status_code=500,
                code="MISSING_TRANSCRIPT_FIELDS",
                message=(
                    f"Transcript record {index} is missing fields: "
                    f"{sorted(missing)}"
                ),
            )

        transcript_id = str(
            record["transcript_id"]
        ).strip()

        title = str(
            record["title"]
        ).strip()

        text = str(
            record["transcript"]
        ).strip()

        if not transcript_id:
            raise AppError(
                status_code=500,
                code="INVALID_TRANSCRIPT_ID",
                message=(
                    f"Transcript record {index} "
                    "contains an empty transcript_id."
                ),
            )

        if not title:
            raise AppError(
                status_code=500,
                code="INVALID_TRANSCRIPT_TITLE",
                message=(
                    f"Transcript record {index} "
                    "contains an empty title."
                ),
            )

        if not text:
            raise AppError(
                status_code=500,
                code="EMPTY_TRANSCRIPT",
                message=(
                    f"Transcript record {index} "
                    "contains empty transcript text."
                ),
            )

        transcripts.append(
            Transcript(
                transcript_id=transcript_id,
                title=title,
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

    if not transcripts:
        raise AppError(
            status_code=404,
            code="NO_TRANSCRIPTS_FOUND",
            message=(
                "No transcripts were found in the source file."
            ),
        )

    return transcripts