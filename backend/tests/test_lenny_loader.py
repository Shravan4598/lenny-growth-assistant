from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.retrieval.models import Transcript


class LennyRepositoryLoader:
    """Load Lenny's Data markdown content into normalized transcripts."""

    def __init__(
        self,
        repository_path: str | Path,
        content_types: set[str] | None = None,
    ) -> None:
        self.repository_path = Path(repository_path)
        self.content_types = content_types or {"podcasts"}

    def load(self) -> list[Transcript]:
        """Load supported content from the repository."""

        if not self.repository_path.exists():
            raise FileNotFoundError(
                f"Lenny repository not found: {self.repository_path}"
            )

        index_path = self.repository_path / "index.json"

        if not index_path.exists():
            raise FileNotFoundError(
                f"Repository metadata file not found: {index_path}"
            )

        records = self._load_index(index_path)

        transcripts: list[Transcript] = []

        for record in records:
            content_type = self._detect_content_type(record)

            if content_type not in self.content_types:
                continue

            relative_path = self._extract_file_path(
                record,
                content_type,
            )

            if not relative_path:
                continue

            source_path = self.repository_path / relative_path

            if not source_path.exists():
                continue

            text = source_path.read_text(
                encoding="utf-8",
            ).strip()

            if not text:
                continue

            transcript = Transcript(
                transcript_id=self._build_transcript_id(
                    record=record,
                    content_type=content_type,
                    relative_path=relative_path,
                ),
                title=self._extract_title(
                    record,
                    relative_path,
                ),
                guest=self._extract_guest(record),
                date=self._extract_date(record),
                source_url=self._extract_source_url(
                    record,
                    content_type,
                    relative_path,
                ),
                text=text,
            )

            transcripts.append(transcript)

        if not transcripts:
            raise ValueError(
                "No supported transcript records were loaded. "
                "Check repository layout and configured content types."
            )

        return transcripts

    @staticmethod
    def _load_index(
        index_path: Path,
    ) -> list[dict[str, Any]]:
        with index_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        if isinstance(data, list):
            return [
                record
                for record in data
                if isinstance(record, dict)
            ]

        if isinstance(data, dict):
            for key in (
                "items",
                "records",
                "data",
                "episodes",
                "content",
            ):
                value = data.get(key)

                if isinstance(value, list):
                    return [
                        record
                        for record in value
                        if isinstance(record, dict)
                    ]

        raise ValueError(
            "Unsupported index.json structure."
        )

    @staticmethod
    def _detect_content_type(
        record: dict[str, Any],
    ) -> str:
        value = (
            record.get("type")
            or record.get("content_type")
            or record.get("category")
            or ""
        )

        value = str(value).lower().strip()

        if "podcast" in value:
            return "podcasts"

        if "newsletter" in value:
            return "newsletters"

        path = str(
            record.get("path")
            or record.get("file")
            or record.get("filepath")
            or ""
        ).lower()

        if "podcasts/" in path:
            return "podcasts"

        if "newsletters/" in path:
            return "newsletters"

        return "unknown"

    @staticmethod
    def _extract_file_path(
        record: dict[str, Any],
        content_type: str,
    ) -> str | None:
        for key in (
            "path",
            "file",
            "filepath",
            "filename",
        ):
            value = record.get(key)

            if value:
                path = str(value).strip()

                if "/" in path:
                    return path

                return f"{content_type}/{path}"

        return None

    @staticmethod
    def _extract_title(
        record: dict[str, Any],
        relative_path: str,
    ) -> str:
        for key in (
            "title",
            "name",
            "episode_title",
        ):
            value = record.get(key)

            if value:
                return str(value).strip()

        return Path(relative_path).stem.replace(
            "-",
            " ",
        ).replace(
            "_",
            " ",
        ).title()

    @staticmethod
    def _extract_guest(
        record: dict[str, Any],
    ) -> str | None:
        for key in (
            "guest",
            "guests",
            "author",
        ):
            value = record.get(key)

            if value:
                return str(value).strip()

        return None

    @staticmethod
    def _extract_date(
        record: dict[str, Any],
    ) -> str | None:
        for key in (
            "date",
            "published_at",
            "published",
        ):
            value = record.get(key)

            if value:
                return str(value).strip()

        return None

    @staticmethod
    def _extract_source_url(
        record: dict[str, Any],
        content_type: str,
        relative_path: str,
    ) -> str | None:
        for key in (
            "source_url",
            "url",
            "link",
        ):
            value = record.get(key)

            if value:
                return str(value).strip()

        return (
            "https://github.com/LennysNewsletter/"
            "lennys-newsletterpodcastdata/blob/main/"
            f"{relative_path}"
        )

    @staticmethod
    def _build_transcript_id(
        record: dict[str, Any],
        content_type: str,
        relative_path: str,
    ) -> str:
        for key in (
            "id",
            "transcript_id",
            "slug",
        ):
            value = record.get(key)

            if value:
                return f"{content_type}-{value}"

        return (
            f"{content_type}-"
            f"{Path(relative_path).stem}"
        )