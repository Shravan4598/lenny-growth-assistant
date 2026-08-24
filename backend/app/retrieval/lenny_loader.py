from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.core.exceptions import AppError
from app.retrieval.models import Transcript


DEFAULT_CONTENT_TYPES = {"podcasts"}


class LennyRepositoryLoader:
    """Load Lenny's newsletter/podcast repository into normalized transcripts."""

    def __init__(
        self,
        repository_path: str | Path,
        content_types: set[str] | None = None,
    ) -> None:
        self.repository_path = Path(repository_path)

        self.content_types = {
            item.strip().lower()
            for item in (
                content_types or DEFAULT_CONTENT_TYPES
            )
            if item.strip()
        }

        if not self.content_types:
            raise AppError(
                status_code=400,
                code="INVALID_CONTENT_TYPES",
                message="At least one content type must be configured.",
            )

    def load(self) -> list[Transcript]:
        """Load supported content from the repository."""

        if not self.repository_path.exists():
            raise AppError(
                status_code=404,
                code="LENNY_REPOSITORY_NOT_FOUND",
                message=(
                    "Lenny repository not found: "
                    f"{self.repository_path}"
                ),
            )

        if not self.repository_path.is_dir():
            raise AppError(
                status_code=400,
                code="INVALID_LENNY_REPOSITORY_PATH",
                message=(
                    "Lenny repository path is not a directory: "
                    f"{self.repository_path}"
                ),
            )

        index_path = self.repository_path / "index.json"

        if not index_path.exists():
            raise AppError(
                status_code=404,
                code="LENNY_INDEX_NOT_FOUND",
                message=(
                    "Repository metadata file not found: "
                    f"{index_path}"
                ),
            )

        records = self._load_index(index_path)

        transcripts: list[Transcript] = []

        for content_type, record in records:
            if content_type not in self.content_types:
                continue

            relative_path = self._extract_file_path(
                record=record,
                content_type=content_type,
            )

            if not relative_path:
                continue

            source_path = (
                self.repository_path / relative_path
            )

            if not source_path.exists():
                print(
                    "Warning: transcript file not found: "
                    f"{source_path}"
                )
                continue

            if not source_path.is_file():
                continue

            try:
                text = source_path.read_text(
                    encoding="utf-8",
                ).strip()

            except UnicodeDecodeError:
                print(
                    "Warning: unable to decode file: "
                    f"{source_path}"
                )
                continue

            except OSError as exc:
                print(
                    "Warning: unable to read file: "
                    f"{source_path}. Error: {exc}"
                )
                continue

            if not text:
                continue

            transcript = Transcript(
                transcript_id=self._build_transcript_id(
                    record=record,
                    content_type=content_type,
                    relative_path=relative_path,
                ),
                title=self._extract_title(
                    record=record,
                    relative_path=relative_path,
                ),
                guest=self._extract_guest(record),
                date=self._extract_date(record),
                source_url=self._extract_source_url(
                    record=record,
                    content_type=content_type,
                    relative_path=relative_path,
                ),
                text=text,
            )

            transcripts.append(transcript)

        if not transcripts:
            raise AppError(
                status_code=404,
                code="NO_TRANSCRIPTS_FOUND",
                message=(
                    "No supported transcript records were loaded. "
                    f"Configured content types: "
                    f"{sorted(self.content_types)}. "
                    "Check repository layout and transcript files."
                ),
            )

        print(
            f"Loaded {len(transcripts)} transcripts "
            f"for content types: {sorted(self.content_types)}"
        )

        return transcripts

    @staticmethod
    def _load_index(
        index_path: Path,
    ) -> list[tuple[str, dict[str, Any]]]:
        """Load repository index."""

        try:
            with index_path.open(
                "r",
                encoding="utf-8",
            ) as file:
                data = json.load(file)

        except json.JSONDecodeError as exc:
            raise AppError(
                status_code=500,
                code="INVALID_LENNY_INDEX",
                message=(
                    "Repository index.json contains invalid JSON."
                ),
            ) from exc

        except OSError as exc:
            raise AppError(
                status_code=500,
                code="LENNY_INDEX_READ_FAILED",
                message=(
                    "Unable to read repository index.json."
                ),
            ) from exc

        results: list[tuple[str, dict[str, Any]]] = []

        # ---------------------------------------------------------
        # List format
        # ---------------------------------------------------------

        if isinstance(data, list):
            for record in data:
                if not isinstance(record, dict):
                    continue

                content_type = (
                    LennyRepositoryLoader._detect_content_type(
                        record
                    )
                )

                results.append(
                    (
                        content_type,
                        record,
                    )
                )

            return results

        if not isinstance(data, dict):
            raise AppError(
                status_code=500,
                code="INVALID_LENNY_INDEX_STRUCTURE",
                message=(
                    "Unsupported index.json structure. "
                    "Expected a JSON object or list."
                ),
            )

        # ---------------------------------------------------------
        # Actual Lenny repository format
        #
        # {
        #   "schema_version": "2.0",
        #   "generated_at": "...",
        #   "podcasts": [...],
        #   "newsletters": [...]
        # }
        # ---------------------------------------------------------

        for content_type in (
            "podcasts",
            "newsletters",
        ):
            value = data.get(content_type)

            if isinstance(value, list):
                for record in value:
                    if isinstance(record, dict):
                        results.append(
                            (
                                content_type,
                                record,
                            )
                        )

        if results:
            return results

        # ---------------------------------------------------------
        # Generic repository formats
        # ---------------------------------------------------------

        for key in (
            "items",
            "records",
            "data",
            "episodes",
            "content",
        ):
            value = data.get(key)

            if isinstance(value, list):
                for record in value:
                    if not isinstance(record, dict):
                        continue

                    content_type = (
                        LennyRepositoryLoader._detect_content_type(
                            record
                        )
                    )

                    results.append(
                        (
                            content_type,
                            record,
                        )
                    )

                if results:
                    return results

        raise AppError(
            status_code=500,
            code="UNSUPPORTED_LENNY_INDEX",
            message=(
                "Unsupported index.json structure. "
                "Expected 'podcasts'/'newsletters' arrays "
                "or a generic records/items/data structure."
            ),
        )

    @staticmethod
    def _detect_content_type(
        record: dict[str, Any],
    ) -> str:
        """Determine whether a record is a podcast or newsletter."""

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
            record.get("filename")
            or record.get("path")
            or record.get("file")
            or record.get("filepath")
            or ""
        ).lower()

        path = path.replace("\\", "/")

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
        """Extract the transcript file path."""

        for key in (
            "filename",
            "path",
            "file",
            "filepath",
        ):
            value = record.get(key)

            if not value:
                continue

            path = str(value).strip()

            if not path:
                continue

            path = path.replace("\\", "/")

            if "/" in path:
                return path

            return f"{content_type}/{path}"

        return None

    @staticmethod
    def _extract_title(
        record: dict[str, Any],
        relative_path: str,
    ) -> str:
        """Extract title from repository metadata."""

        for key in (
            "title",
            "name",
            "episode_title",
        ):
            value = record.get(key)

            if value:
                return str(value).strip()

        return (
            Path(relative_path)
            .stem
            .replace("-", " ")
            .replace("_", " ")
            .title()
        )

    @staticmethod
    def _extract_guest(
        record: dict[str, Any],
    ) -> str | None:
        """Extract guest/author information."""

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
        """Extract publication date."""

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
        """Extract original Lenny source URL."""

        for key in (
            "post_url",
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
        """Build a stable transcript identifier."""

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