import argparse
import sys
from pathlib import Path

from backend.app.retrieval.service import RetrievalService


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the Lenny Growth Assistant knowledge index."
    )

    parser.add_argument(
        "--source-type",
        choices=[
            "json",
            "lenny-repository",
        ],
        default="lenny-repository",
    )

    parser.add_argument(
        "--source",
        default="data/external/lennys-newsletterpodcastdata",
    )

    parser.add_argument(
        "--content-types",
        default="podcasts",
        help=(
            "Comma-separated content types. "
            "Example: podcasts,newsletters"
        ),
    )

    parser.add_argument(
        "--output",
        default="data/processed/lenny.faiss",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    content_types = {
        item.strip()
        for item in args.content_types.split(",")
        if item.strip()
    }

    service = RetrievalService(
        index_path=Path(args.output),
    )

    try:
        if args.source_type == "json":
            chunk_count = service.ingest(
                source_path=Path(args.source),
            )
        else:
            chunk_count = service.ingest_lenny_repository(
                repository_path=Path(args.source),
                content_types=content_types,
            )

    except Exception as exc:
        print(
            f"Ingestion failed: {exc}",
            file=sys.stderr,
        )
        raise SystemExit(1) from exc

    print(
        "Ingestion complete. "
        f"Created {chunk_count} searchable chunks."
    )


if __name__ == "__main__":
    main()