"""Build the reusable Stage 1 dataset indexes from the raw course data."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.data import (  # noqa: E402
    PAIRED_BREAST_FIELDS,
    SINGLE_IMAGE_FIELDS,
    build_index_report,
    build_paired_breast_index,
    build_single_image_index,
)
from src.data.index_builder import (  # noqa: E402
    DatasetIndexError,
    combine_validation_reports,
    write_csv_rows,
    write_json_file,
)


DEFAULT_TRAIN_CSV = REPO_ROOT / "data" / "raw" / "primary" / "train.csv"
DEFAULT_TRAIN_ARCHIVE = REPO_ROOT / "data" / "raw" / "primary" / "train_img.zip"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "data" / "processed" / "metadata"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-csv", type=Path, default=DEFAULT_TRAIN_CSV)
    parser.add_argument("--train-archive", type=Path, default=DEFAULT_TRAIN_ARCHIVE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--no-strict",
        action="store_true",
        help="Collect validation issues without raising immediately.",
    )
    return parser.parse_args()


def format_distribution(distribution: dict[str, int]) -> str:
    return ", ".join(f"{key}={distribution[key]}" for key in sorted(distribution))


def main() -> int:
    args = parse_args()
    strict = not args.no_strict

    try:
        single_rows, single_validation = build_single_image_index(
            train_csv_path=args.train_csv,
            train_archive_path=args.train_archive,
            strict=strict,
        )
        paired_rows, paired_validation = build_paired_breast_index(
            single_image_rows=single_rows,
            strict=strict,
        )
    except DatasetIndexError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    validation_report = combine_validation_reports(single_validation, paired_validation)
    index_report = build_index_report(single_rows, paired_rows, validation_report)

    output_dir = args.output_dir
    single_index_path = output_dir / "primary_single_image_index.csv"
    paired_index_path = output_dir / "primary_paired_breast_index.csv"
    report_path = output_dir / "primary_index_report.json"

    write_csv_rows(single_index_path, SINGLE_IMAGE_FIELDS, single_rows)
    write_csv_rows(paired_index_path, PAIRED_BREAST_FIELDS, paired_rows)
    write_json_file(report_path, index_report)

    summary = index_report["summary"]
    print("Dataset indexes built successfully")
    print(f"- single-image rows: {summary['total_images']}")
    print(f"- paired breast rows: {summary['paired_success_count']}")
    print(
        "- image-level pathology: "
        f"{format_distribution(summary['image_level_pathology_distribution'])}"
    )
    print(
        "- breast-level pathology: "
        f"{format_distribution(summary['breast_level_pathology_distribution'])}"
    )
    print(
        "- image-level is_malignant: "
        f"{format_distribution(summary['image_level_is_malignant_distribution'])}"
    )
    print(
        "- breast-level is_malignant: "
        f"{format_distribution(summary['breast_level_is_malignant_distribution'])}"
    )
    print(f"- anomaly counts: {summary['anomaly_counts']}")
    print(f"- wrote: {single_index_path}")
    print(f"- wrote: {paired_index_path}")
    print(f"- wrote: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
