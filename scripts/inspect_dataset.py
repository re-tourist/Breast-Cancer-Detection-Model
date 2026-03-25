"""Print a compact Stage 0 summary of the primary course dataset."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
from zipfile import ZipFile


REPO_ROOT = Path(__file__).resolve().parents[1]
PRIMARY_DATA_DIR = REPO_ROOT / "data" / "raw" / "primary"
REQUIRED_FILES = (
    "train.csv",
    "train_img.zip",
    "test_img.zip",
    "name_sid_submission.csv",
)


def require_file(name: str) -> Path:
    """Return a required repo-relative path or fail loudly."""
    path = PRIMARY_DATA_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Missing required dataset file: {path}")
    return path


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    """Load a CSV file using the expected encoding for the provided data."""
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def normalize_lesion_type(value: str) -> str:
    """Make lesion type values easier to read in summaries."""
    cleaned = value.replace("'", "").replace(" ", "")
    return cleaned if cleaned else "<empty>"


def format_counter(counter: Counter[str]) -> str:
    """Format a counter in key=count form with stable ordering."""
    return ", ".join(f"{key}={counter[key]}" for key in sorted(counter))


def main() -> None:
    """Load the current dataset and print the summary used by Stage 0 docs."""
    required_paths = {name: require_file(name) for name in REQUIRED_FILES}
    train_csv = required_paths["train.csv"]
    train_zip_path = required_paths["train_img.zip"]
    test_zip_path = required_paths["test_img.zip"]
    submission_csv = required_paths["name_sid_submission.csv"]

    train_rows = load_csv_rows(train_csv)
    submission_rows = load_csv_rows(submission_csv)

    rows_by_breast: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in train_rows:
        rows_by_breast[row["breast_id"]].append(row)

    views_per_breast = Counter(len(rows) for rows in rows_by_breast.values())
    breast_pathology = Counter()
    problems: list[str] = []

    for breast_id, rows in rows_by_breast.items():
        pathology_values = {row["pathology"] for row in rows}
        view_values = {row["cc_mlo"] for row in rows}
        if len(pathology_values) != 1:
            problems.append(f"{breast_id}: inconsistent pathology values {sorted(pathology_values)}")
        if view_values != {"CC", "MLO"}:
            problems.append(f"{breast_id}: unexpected view set {sorted(view_values)}")
        breast_pathology[next(iter(pathology_values))] += 1

    image_pathology = Counter(row["pathology"] for row in train_rows)
    birads = Counter(row["birads"] for row in train_rows)
    difficult = Counter(row["difficult"] for row in train_rows)
    lesion_type = Counter(normalize_lesion_type(row["lesion_type"]) for row in train_rows)
    annotated_rows = sum(1 for row in train_rows if row["annotations"] and row["annotations"] != "[]")

    train_zip = ZipFile(train_zip_path)
    test_zip = ZipFile(test_zip_path)
    try:
        train_members = {
            member.filename
            for member in train_zip.infolist()
            if not member.is_dir()
        }
        test_members = [
            member.filename
            for member in test_zip.infolist()
            if not member.is_dir()
        ]
    finally:
        train_zip.close()
        test_zip.close()

    expected_train_paths = {row["image_path"] for row in train_rows}
    missing_train_paths = sorted(expected_train_paths - train_members)

    submission_breast_ids = [row["breast_id"] for row in submission_rows]
    duplicate_submission_ids = [
        breast_id
        for breast_id, count in Counter(submission_breast_ids).items()
        if count > 1
    ]

    if missing_train_paths:
        problems.append(
            f"{len(missing_train_paths)} train.csv image paths are missing from train_img.zip"
        )
    if duplicate_submission_ids:
        problems.append(
            f"{len(duplicate_submission_ids)} duplicate breast_id values found in the submission template"
        )

    print("Primary dataset summary")
    print(f"- train rows: {len(train_rows)}")
    print(f"- unique breast_id values: {len(rows_by_breast)}")
    print(f"- views per breast: {format_counter(views_per_breast)}")
    print(f"- image-level pathology: {format_counter(image_pathology)}")
    print(f"- breast-level pathology: {format_counter(breast_pathology)}")
    print(f"- BIRADS: {format_counter(birads)}")
    print(f"- lesion_type: {format_counter(lesion_type)}")
    print(f"- difficult: {format_counter(difficult)}")
    print(f"- annotated image rows: {annotated_rows}")
    print(f"- empty annotation rows: {len(train_rows) - annotated_rows}")
    print(f"- train images in archive: {len(train_members)}")
    print(f"- test images in archive: {len(test_members)}")
    print(f"- submission rows: {len(submission_rows)}")
    print(f"- missing train paths in archive: {len(missing_train_paths)}")

    if problems:
        print("Validation checks: FAILED")
        for problem in problems:
            print(f"  - {problem}")
        raise SystemExit(1)

    print("Validation checks: OK")


if __name__ == "__main__":
    main()
