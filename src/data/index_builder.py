"""Build reusable dataset indexes for Stage 1 Issue 1.1."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
from zipfile import ZipFile


SINGLE_IMAGE_FIELDS = (
    "image_id",
    "breast_id",
    "view",
    "pathology",
    "is_malignant",
    "image_path",
    "laterality",
    "device",
    "lesion_type",
    "birads",
    "difficult",
    "annotations",
)

PAIRED_BREAST_FIELDS = (
    "breast_id",
    "pathology",
    "is_malignant",
    "image_id_cc",
    "image_id_mlo",
    "image_path_cc",
    "image_path_mlo",
    "laterality",
    "device",
    "birads",
)

REQUIRED_TRAIN_COLUMNS = frozenset({"image_path", "breast_id", "cc_mlo", "pathology"})
ALLOWED_PATHOLOGY = frozenset({"M", "B", "N"})
ALLOWED_VIEWS = frozenset({"CC", "MLO"})
PAIR_METADATA_FIELDS = ("pathology", "is_malignant", "laterality", "device", "birads")
VIEW_SORT_ORDER = {"CC": 0, "MLO": 1}


class DatasetIndexError(RuntimeError):
    """Raised when the dataset cannot be indexed under the current rules."""

    def __init__(self, message: str, validation_report: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.validation_report = validation_report or {}


def build_single_image_index(
    train_csv_path: str | Path,
    train_archive_path: str | Path,
    strict: bool = True,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Build the normalized single-image index from the raw training metadata."""

    csv_path = Path(train_csv_path)
    archive_path = Path(train_archive_path)
    raw_rows = _load_csv_rows(csv_path)
    validation_report = _new_single_validation_report(strict=strict)

    if not raw_rows:
        raise DatasetIndexError("train.csv contains no data rows.", validation_report)

    missing_columns = sorted(REQUIRED_TRAIN_COLUMNS - set(raw_rows[0].keys()))
    validation_report["checks"]["required_columns"]["missing"] = missing_columns
    validation_report["checks"]["required_columns"]["ok"] = not missing_columns

    if missing_columns:
        validation_report["status"] = "failed"
        validation_report["error_counts"]["missing_required_columns"] = len(missing_columns)
        raise DatasetIndexError(
            _format_validation_failure("Single-image index", validation_report),
            validation_report,
        )

    archive_members = _load_archive_members(archive_path)

    single_rows: list[dict[str, Any]] = []
    invalid_pathology_rows: list[dict[str, Any]] = []

    for row_number, raw_row in enumerate(raw_rows, start=2):
        image_path = raw_row["image_path"].strip()
        pathology = raw_row["pathology"].strip()
        view = raw_row["cc_mlo"].strip()

        if pathology not in ALLOWED_PATHOLOGY:
            invalid_pathology_rows.append(
                {
                    "row_number": row_number,
                    "image_path": image_path,
                    "pathology": pathology,
                }
            )

        single_rows.append(
            {
                "image_id": Path(image_path).stem,
                "breast_id": raw_row["breast_id"].strip(),
                "view": view,
                "pathology": pathology,
                "is_malignant": int(pathology == "M"),
                "image_path": image_path,
                "laterality": raw_row.get("l_r", "").strip(),
                "device": raw_row.get("device", "").strip(),
                "lesion_type": raw_row.get("lesion_type", "").strip(),
                "birads": raw_row.get("birads", "").strip(),
                "difficult": raw_row.get("difficult", "").strip(),
                "annotations": raw_row.get("annotations", "").strip(),
            }
        )

    duplicate_image_ids = [
        {"image_id": image_id, "count": count}
        for image_id, count in sorted(Counter(row["image_id"] for row in single_rows).items())
        if count > 1
    ]
    validation_report["checks"]["pathology_values"]["invalid_rows"] = invalid_pathology_rows
    validation_report["checks"]["pathology_values"]["ok"] = not invalid_pathology_rows
    validation_report["checks"]["duplicate_image_ids"]["duplicates"] = duplicate_image_ids
    validation_report["checks"]["duplicate_image_ids"]["ok"] = not duplicate_image_ids

    rows_by_breast: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in single_rows:
        rows_by_breast[str(row["breast_id"])].append(row)

    invalid_image_counts: list[dict[str, Any]] = []
    invalid_view_sets: list[dict[str, Any]] = []
    inconsistent_pathology: list[dict[str, Any]] = []

    for breast_id in sorted(rows_by_breast):
        group = rows_by_breast[breast_id]
        if len(group) != 2:
            invalid_image_counts.append({"breast_id": breast_id, "image_count": len(group)})

        views = sorted({str(row["view"]) for row in group})
        if set(views) != ALLOWED_VIEWS:
            invalid_view_sets.append({"breast_id": breast_id, "views": views})

        pathology_values = sorted({str(row["pathology"]) for row in group})
        if len(pathology_values) != 1:
            inconsistent_pathology.append({"breast_id": breast_id, "pathology_values": pathology_values})

    missing_archive_paths = sorted(
        row["image_path"]
        for row in single_rows
        if str(row["image_path"]) not in archive_members
    )

    validation_report["checks"]["breast_image_count"]["invalid_breast_ids"] = invalid_image_counts
    validation_report["checks"]["breast_image_count"]["ok"] = not invalid_image_counts
    validation_report["checks"]["breast_view_pairs"]["invalid_breast_ids"] = invalid_view_sets
    validation_report["checks"]["breast_view_pairs"]["ok"] = not invalid_view_sets
    validation_report["checks"]["breast_pathology_consistency"]["invalid_breast_ids"] = inconsistent_pathology
    validation_report["checks"]["breast_pathology_consistency"]["ok"] = not inconsistent_pathology
    validation_report["checks"]["archive_paths_exist"]["missing_paths"] = missing_archive_paths
    validation_report["checks"]["archive_paths_exist"]["ok"] = not missing_archive_paths

    validation_report["error_counts"] = {
        "missing_required_columns": len(missing_columns),
        "invalid_pathology_values": len(invalid_pathology_rows),
        "duplicate_image_ids": len(duplicate_image_ids),
        "invalid_breast_image_count": len(invalid_image_counts),
        "invalid_breast_view_pairs": len(invalid_view_sets),
        "inconsistent_breast_pathology": len(inconsistent_pathology),
        "missing_archive_paths": len(missing_archive_paths),
    }
    validation_report["status"] = "failed" if _has_errors(validation_report["error_counts"]) else "ok"

    single_rows.sort(
        key=lambda row: (
            str(row["breast_id"]),
            VIEW_SORT_ORDER.get(str(row["view"]), 99),
            str(row["image_id"]),
        )
    )

    if strict and validation_report["status"] == "failed":
        raise DatasetIndexError(
            _format_validation_failure("Single-image index", validation_report),
            validation_report,
        )

    return single_rows, validation_report


def build_paired_breast_index(
    single_image_rows: list[dict[str, Any]],
    strict: bool = True,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Build the paired breast-level index from normalized single-image rows."""

    validation_report = _new_paired_validation_report(strict=strict)
    rows_by_breast: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in single_image_rows:
        rows_by_breast[str(row.get("breast_id", ""))].append(row)

    paired_rows: list[dict[str, Any]] = []
    invalid_pairs: list[dict[str, Any]] = []
    inconsistent_metadata: list[dict[str, Any]] = []

    for breast_id in sorted(rows_by_breast):
        group = rows_by_breast[breast_id]
        view_map: dict[str, dict[str, Any]] = {}
        duplicate_views: list[str] = []

        for row in group:
            view = str(row.get("view", ""))
            if view in view_map:
                duplicate_views.append(view)
            else:
                view_map[view] = row

        missing_views = sorted(ALLOWED_VIEWS - set(view_map))
        unexpected_views = sorted(view for view in view_map if view not in ALLOWED_VIEWS)

        if len(group) != 2 or missing_views or duplicate_views or unexpected_views:
            invalid_pairs.append(
                {
                    "breast_id": breast_id,
                    "image_count": len(group),
                    "missing_views": missing_views,
                    "duplicate_views": sorted(duplicate_views),
                    "unexpected_views": unexpected_views,
                }
            )
            continue

        metadata_conflicts: dict[str, list[Any]] = {}
        for field in PAIR_METADATA_FIELDS:
            values = sorted({row.get(field, "") for row in group})
            if len(values) != 1:
                metadata_conflicts[field] = values

        if metadata_conflicts:
            inconsistent_metadata.append(
                {
                    "breast_id": breast_id,
                    "conflicts": metadata_conflicts,
                }
            )
            continue

        cc_row = view_map["CC"]
        mlo_row = view_map["MLO"]
        paired_rows.append(
            {
                "breast_id": breast_id,
                "pathology": cc_row["pathology"],
                "is_malignant": cc_row["is_malignant"],
                "image_id_cc": cc_row["image_id"],
                "image_id_mlo": mlo_row["image_id"],
                "image_path_cc": cc_row["image_path"],
                "image_path_mlo": mlo_row["image_path"],
                "laterality": cc_row["laterality"],
                "device": cc_row["device"],
                "birads": cc_row["birads"],
            }
        )

    paired_rows.sort(key=lambda row: str(row["breast_id"]))

    duplicate_paired_breast_ids = [
        {"breast_id": breast_id, "count": count}
        for breast_id, count in sorted(Counter(row["breast_id"] for row in paired_rows).items())
        if count > 1
    ]

    empty_paired_fields: list[dict[str, Any]] = []
    for row in paired_rows:
        empty_fields = [field for field in PAIRED_BREAST_FIELDS if row.get(field, "") in ("", None)]
        if empty_fields:
            empty_paired_fields.append(
                {
                    "breast_id": row["breast_id"],
                    "empty_fields": empty_fields,
                }
            )

    validation_report["checks"]["paired_missing_or_duplicate"]["invalid_breast_ids"] = invalid_pairs
    validation_report["checks"]["paired_missing_or_duplicate"]["ok"] = not invalid_pairs
    validation_report["checks"]["duplicate_paired_breast_ids"]["duplicates"] = duplicate_paired_breast_ids
    validation_report["checks"]["duplicate_paired_breast_ids"]["ok"] = not duplicate_paired_breast_ids
    validation_report["checks"]["empty_paired_fields"]["invalid_rows"] = empty_paired_fields
    validation_report["checks"]["empty_paired_fields"]["ok"] = not empty_paired_fields
    validation_report["checks"]["paired_metadata_consistency"]["invalid_breast_ids"] = inconsistent_metadata
    validation_report["checks"]["paired_metadata_consistency"]["ok"] = not inconsistent_metadata
    validation_report["error_counts"] = {
        "invalid_paired_samples": len(invalid_pairs),
        "duplicate_paired_breast_ids": len(duplicate_paired_breast_ids),
        "empty_paired_fields": len(empty_paired_fields),
        "inconsistent_paired_metadata": len(inconsistent_metadata),
    }
    validation_report["status"] = "failed" if _has_errors(validation_report["error_counts"]) else "ok"

    if strict and validation_report["status"] == "failed":
        raise DatasetIndexError(
            _format_validation_failure("Paired breast index", validation_report),
            validation_report,
        )

    return paired_rows, validation_report


def combine_validation_reports(
    single_validation_report: dict[str, Any],
    paired_validation_report: dict[str, Any],
) -> dict[str, Any]:
    """Combine single-image and paired-index validation results into one report."""

    combined_error_counts = dict(single_validation_report.get("error_counts", {}))
    combined_error_counts.update(paired_validation_report.get("error_counts", {}))

    return {
        "strict_mode": bool(single_validation_report.get("strict_mode", True)),
        "status": "failed"
        if single_validation_report.get("status") == "failed"
        or paired_validation_report.get("status") == "failed"
        else "ok",
        "error_counts": combined_error_counts,
        "single_image_checks": single_validation_report.get("checks", {}),
        "paired_checks": paired_validation_report.get("checks", {}),
    }


def build_index_report(
    single_image_rows: list[dict[str, Any]],
    paired_rows: list[dict[str, Any]],
    validation_report: dict[str, Any],
) -> dict[str, Any]:
    """Build the JSON report stored next to the generated index files."""

    return {
        "summary": {
            "total_images": len(single_image_rows),
            "total_breasts": len({str(row["breast_id"]) for row in single_image_rows}),
            "paired_success_count": len(paired_rows),
            "image_level_pathology_distribution": _counter_to_dict(
                Counter(str(row["pathology"]) for row in single_image_rows)
            ),
            "breast_level_pathology_distribution": _counter_to_dict(
                Counter(str(row["pathology"]) for row in paired_rows)
            ),
            "image_level_is_malignant_distribution": _counter_to_dict(
                Counter(int(row["is_malignant"]) for row in single_image_rows)
            ),
            "breast_level_is_malignant_distribution": _counter_to_dict(
                Counter(int(row["is_malignant"]) for row in paired_rows)
            ),
            "anomaly_counts": dict(validation_report.get("error_counts", {})),
        },
        "validation": validation_report,
    }


def write_csv_rows(path: str | Path, fieldnames: tuple[str, ...], rows: list[dict[str, Any]]) -> None:
    """Write a row-oriented CSV file with a stable column order."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_json_file(path: str | Path, payload: dict[str, Any]) -> None:
    """Write a JSON file with stable formatting."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def _load_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _load_archive_members(path: Path) -> set[str]:
    with ZipFile(path) as archive:
        return {member.filename for member in archive.infolist() if not member.is_dir()}


def _new_single_validation_report(strict: bool) -> dict[str, Any]:
    return {
        "strict_mode": strict,
        "status": "ok",
        "error_counts": {},
        "checks": {
            "required_columns": {"ok": True, "missing": []},
            "pathology_values": {"ok": True, "invalid_rows": []},
            "duplicate_image_ids": {"ok": True, "duplicates": []},
            "breast_image_count": {"ok": True, "invalid_breast_ids": []},
            "breast_view_pairs": {"ok": True, "invalid_breast_ids": []},
            "breast_pathology_consistency": {"ok": True, "invalid_breast_ids": []},
            "archive_paths_exist": {"ok": True, "missing_paths": []},
        },
    }


def _new_paired_validation_report(strict: bool) -> dict[str, Any]:
    return {
        "strict_mode": strict,
        "status": "ok",
        "error_counts": {},
        "checks": {
            "paired_missing_or_duplicate": {"ok": True, "invalid_breast_ids": []},
            "duplicate_paired_breast_ids": {"ok": True, "duplicates": []},
            "empty_paired_fields": {"ok": True, "invalid_rows": []},
            "paired_metadata_consistency": {"ok": True, "invalid_breast_ids": []},
        },
    }


def _has_errors(error_counts: dict[str, int]) -> bool:
    return any(count > 0 for count in error_counts.values())


def _format_validation_failure(stage: str, validation_report: dict[str, Any]) -> str:
    lines = [f"{stage} validation failed."]
    for error_name, count in validation_report.get("error_counts", {}).items():
        if count:
            lines.append(f"- {error_name}: {count}")
    return "\n".join(lines)


def _counter_to_dict(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): counter[key] for key in sorted(counter)}
