import json

import pytest

from app.retrieval.loader import load_transcripts


def test_load_transcripts(tmp_path) -> None:
    """Valid transcript data should load correctly."""

    source = tmp_path / "transcripts.json"

    source.write_text(
        json.dumps(
            [
                {
                    "transcript_id": "test-001",
                    "title": "Test Episode",
                    "guest": "Test Guest",
                    "date": "2026-01-01",
                    "source_url": "https://example.com",
                    "transcript": "Some useful transcript text.",
                }
            ]
        ),
        encoding="utf-8",
    )

    transcripts = load_transcripts(source)

    assert len(transcripts) == 1
    assert transcripts[0].transcript_id == "test-001"
    assert transcripts[0].title == "Test Episode"


def test_missing_required_field_fails(tmp_path) -> None:
    """Invalid transcript records should fail validation."""

    source = tmp_path / "transcripts.json"

    source.write_text(
        json.dumps(
            [
                {
                    "transcript_id": "test-001",
                    "title": "Test Episode",
                }
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        load_transcripts(source)