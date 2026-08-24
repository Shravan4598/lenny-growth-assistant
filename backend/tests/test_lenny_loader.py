import json

from app.retrieval.lenny_loader import (
    LennyRepositoryLoader,
)


def test_load_podcast_repository(
    tmp_path,
) -> None:
    """Podcast markdown and metadata should load correctly."""

    podcasts_dir = tmp_path / "podcasts"
    podcasts_dir.mkdir()

    transcript_file = podcasts_dir / "test-episode.md"

    transcript_file.write_text(
        "# Test Episode\n\n"
        "Product teams should prioritize customer impact.",
        encoding="utf-8",
    )

    index = [
        {
            "type": "podcast",
            "id": "001",
            "title": "Test Episode",
            "guest": "Test Guest",
            "date": "2026-01-01",
            "path": "podcasts/test-episode.md",
        }
    ]

    (tmp_path / "index.json").write_text(
        json.dumps(index),
        encoding="utf-8",
    )

    loader = LennyRepositoryLoader(
        repository_path=tmp_path,
        content_types={"podcasts"},
    )

    transcripts = loader.load()

    assert len(transcripts) == 1

    transcript = transcripts[0]

    assert transcript.transcript_id == "podcasts-001"
    assert transcript.title == "Test Episode"
    assert transcript.guest == "Test Guest"
    assert "prioritize customer impact" in transcript.text


def test_content_type_filter(
    tmp_path,
) -> None:
    """Newsletter records should be excluded when podcasts only."""

    podcasts_dir = tmp_path / "podcasts"
    newsletters_dir = tmp_path / "newsletters"

    podcasts_dir.mkdir()
    newsletters_dir.mkdir()

    (podcasts_dir / "episode.md").write_text(
        "Podcast content",
        encoding="utf-8",
    )

    (newsletters_dir / "post.md").write_text(
        "Newsletter content",
        encoding="utf-8",
    )

    index = [
        {
            "type": "podcast",
            "id": "podcast-1",
            "title": "Podcast",
            "path": "podcasts/episode.md",
        },
        {
            "type": "newsletter",
            "id": "newsletter-1",
            "title": "Newsletter",
            "path": "newsletters/post.md",
        },
    ]

    (tmp_path / "index.json").write_text(
        json.dumps(index),
        encoding="utf-8",
    )

    loader = LennyRepositoryLoader(
        repository_path=tmp_path,
        content_types={"podcasts"},
    )

    transcripts = loader.load()

    assert len(transcripts) == 1
    assert transcripts[0].title == "Podcast"