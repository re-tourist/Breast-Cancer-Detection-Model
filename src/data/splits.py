"""Build reusable breast_id-grouped train/val split artifacts for Stage 1 Issue 1.3."""

from __future__ import annotations

import csv
from collections import Counter
from math import isclose
from pathlib import Path
from typing import Any

from sklearn.model_selection import GroupShuffleSplit, StratifiedGroupKFold

from .index_builder import (
    PAIRED_BREAST_FIELDS,
    SINGLE_IMAGE_FIELDS,
    write_csv_rows,
    write_json_file,
)


DEFAULT_SPLIT_DIR = Path("data/processed/splits")
DEFAULT_VAL_RATIO = 0.2
DEFAULT_RANDOM_STATE = 42
PAIRED_SPLIT_FILENAMES = {
    "train": "primary_paired_breast_split_train.csv",
    "val": "primary_paired_breast_split_val.csv",
}
SINGLE_SPLIT_FILENAMES = {
    "train": "primary_single_image_split_train.csv",
    "val": "primary_single_image_split_val.csv",
}
SUMMARY_FILENAME = "primary_split_summary.json"
FOLD_ASSIGNMENT_FILENAME = "primary_fold_assignment.csv"
FOLD_SUMMARY_FILENAME = "primary_fold_summary.json"
FOLD_ASSIGNMENT_FIELDS = ("breast_id", "fold", "target", "num_images")
PAIRED_REQUIRED_COLUMNS = frozenset(PAIRED_BREAST_FIELDS)
SINGLE_REQUIRED_COLUMNS = frozenset(SINGLE_IMAGE_FIELDS)
PAIRED_CORE_FIELDS = ("breast_id", "image_id_cc", "image_id_mlo", "image_path_cc", "image_path_mlo")


class SplitBuildError(RuntimeError):
    """Raised when train/val split artifacts cannot be built safely."""

    def __init__(self, message: str, split_result: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.split_result = split_result or {}


def build_train_val_split(
    paired_index_csv_path: str | Path,
    single_index_csv_path: str | Path,
    val_ratio: float = DEFAULT_VAL_RATIO,
    random_state: int = DEFAULT_RANDOM_STATE,
    stratified: bool = True,
) -> dict[str, Any]:
    """Build reusable paired and single-image split rows from normalized indexes."""

    if not 0 < val_ratio < 1:
        raise SplitBuildError(f"val_ratio must be between 0 and 1, got {val_ratio}.")

    paired_rows, paired_fieldnames = _load_csv_rows_with_fieldnames(Path(paired_index_csv_path))
    single_rows, single_fieldnames = _load_csv_rows_with_fieldnames(Path(single_index_csv_path))

    _validate_required_columns("Paired index", paired_fieldnames, PAIRED_REQUIRED_COLUMNS)
    _validate_required_columns("Single-image index", single_fieldnames, SINGLE_REQUIRED_COLUMNS)

    if not paired_rows:
        raise SplitBuildError("Paired index contains no rows.")
    if not single_rows:
        raise SplitBuildError("Single-image index contains no rows.")

    paired_labels = [_parse_binary_label(row["is_malignant"], row["breast_id"]) for row in paired_rows]
    paired_breast_ids = [row["breast_id"] for row in paired_rows]

    duplicate_paired_breast_ids = [
        breast_id
        for breast_id, count in sorted(Counter(paired_breast_ids).items())
        if count > 1
    ]
    if duplicate_paired_breast_ids:
        raise SplitBuildError(
            "Paired index contains duplicate breast_id values: "
            + ", ".join(duplicate_paired_breast_ids[:10])
        )

    invalid_paired_rows = _find_rows_with_empty_fields(paired_rows, PAIRED_CORE_FIELDS)
    if invalid_paired_rows:
        raise SplitBuildError(
            "Paired index contains rows with empty core fields.",
            {"invalid_paired_rows": invalid_paired_rows},
        )

    single_breast_ids = {row["breast_id"] for row in single_rows}
    missing_in_single = sorted(set(paired_breast_ids) - single_breast_ids)
    extra_in_single = sorted(single_breast_ids - set(paired_breast_ids))
    if missing_in_single or extra_in_single:
        raise SplitBuildError(
            "Single-image and paired indexes do not share the same breast_id set.",
            {
                "missing_in_single": missing_in_single,
                "extra_in_single": extra_in_single,
            },
        )

    selection_result = _select_split_indices(
        labels=paired_labels,
        breast_ids=paired_breast_ids,
        val_ratio=val_ratio,
        random_state=random_state,
        stratified=stratified,
    )

    train_indices = selection_result["train_indices"]
    val_indices = selection_result["val_indices"]
    split_strategy = selection_result["split_strategy"]
    fallback_info = selection_result["fallback"]
    fold_assignment_meta = selection_result["fold_assignment"]

    train_breast_ids = {paired_breast_ids[index] for index in train_indices}
    val_breast_ids = {paired_breast_ids[index] for index in val_indices}
    paired_train_rows = [row for row in paired_rows if row["breast_id"] in train_breast_ids]
    paired_val_rows = [row for row in paired_rows if row["breast_id"] in val_breast_ids]
    single_train_rows = [row for row in single_rows if row["breast_id"] in train_breast_ids]
    single_val_rows = [row for row in single_rows if row["breast_id"] in val_breast_ids]

    image_counts_by_breast = Counter(row["breast_id"] for row in single_rows)
    fold_assignment_rows = _build_fold_assignment_rows(
        paired_rows=paired_rows,
        paired_labels=paired_labels,
        image_counts_by_breast=image_counts_by_breast,
        fold_assignment_meta=fold_assignment_meta,
    )
    fold_summary = _build_fold_summary(
        fold_assignment_rows=fold_assignment_rows,
        num_folds=fold_assignment_meta["num_folds"],
        requested_stratified=stratified,
        fallback_info=fallback_info,
        val_fold=fold_assignment_meta["val_fold"],
        train_folds=fold_assignment_meta["train_folds"],
        train_val_derived_from_fold_assignment=fold_assignment_meta["train_val_derived_from_assignment"],
    )

    checks = _build_checks(
        paired_rows=paired_rows,
        single_rows=single_rows,
        paired_train_rows=paired_train_rows,
        paired_val_rows=paired_val_rows,
        single_train_rows=single_train_rows,
        single_val_rows=single_val_rows,
        train_breast_ids=train_breast_ids,
        val_breast_ids=val_breast_ids,
        requested_stratified=stratified,
        fallback_info=fallback_info,
        fold_assignment_meta=fold_assignment_meta,
        fold_assignment_rows=fold_assignment_rows,
        fold_summary=fold_summary,
    )
    _raise_on_failed_checks(checks)

    return {
        "config": {
            "random_state": int(random_state),
            "val_ratio": float(val_ratio),
            "requested_stratified": bool(stratified),
        },
        "split_strategy": split_strategy,
        "fallback": fallback_info,
        "paired": {
            "fieldnames": tuple(paired_fieldnames),
            "train_rows": paired_train_rows,
            "val_rows": paired_val_rows,
        },
        "single": {
            "fieldnames": tuple(single_fieldnames),
            "train_rows": single_train_rows,
            "val_rows": single_val_rows,
        },
        "breast_ids": {
            "train": sorted(train_breast_ids),
            "val": sorted(val_breast_ids),
        },
        "fold_assignment": {
            "fieldnames": FOLD_ASSIGNMENT_FIELDS,
            "rows": fold_assignment_rows,
            **fold_assignment_meta,
        },
        "fold_summary": fold_summary,
        "checks": checks,
    }


def write_split_artifacts(
    split_result: dict[str, Any],
    output_dir: str | Path = DEFAULT_SPLIT_DIR,
) -> dict[str, Path]:
    """Write reusable split CSVs, fold artifacts, and the JSON summary reports."""

    output_root = Path(output_dir)
    paired = split_result["paired"]
    single = split_result["single"]
    fold_assignment = split_result["fold_assignment"]

    paired_train_path = output_root / PAIRED_SPLIT_FILENAMES["train"]
    paired_val_path = output_root / PAIRED_SPLIT_FILENAMES["val"]
    single_train_path = output_root / SINGLE_SPLIT_FILENAMES["train"]
    single_val_path = output_root / SINGLE_SPLIT_FILENAMES["val"]
    summary_path = output_root / SUMMARY_FILENAME
    fold_assignment_path = output_root / FOLD_ASSIGNMENT_FILENAME
    fold_summary_path = output_root / FOLD_SUMMARY_FILENAME

    write_csv_rows(paired_train_path, paired["fieldnames"], paired["train_rows"])
    write_csv_rows(paired_val_path, paired["fieldnames"], paired["val_rows"])
    write_csv_rows(single_train_path, single["fieldnames"], single["train_rows"])
    write_csv_rows(single_val_path, single["fieldnames"], single["val_rows"])
    write_csv_rows(fold_assignment_path, fold_assignment["fieldnames"], fold_assignment["rows"])
    write_json_file(summary_path, build_split_summary(split_result))
    write_json_file(fold_summary_path, split_result["fold_summary"])

    return {
        "paired_train": paired_train_path,
        "paired_val": paired_val_path,
        "single_train": single_train_path,
        "single_val": single_val_path,
        "fold_assignment": fold_assignment_path,
        "fold_summary": fold_summary_path,
        "summary": summary_path,
    }


def build_split_summary(split_result: dict[str, Any]) -> dict[str, Any]:
    """Build the JSON summary stored next to the reusable split CSVs."""

    paired_train_rows = split_result["paired"]["train_rows"]
    paired_val_rows = split_result["paired"]["val_rows"]
    single_train_rows = split_result["single"]["train_rows"]
    single_val_rows = split_result["single"]["val_rows"]
    fold_assignment = split_result["fold_assignment"]

    return {
        "split_strategy": split_result["split_strategy"],
        "random_state": split_result["config"]["random_state"],
        "val_ratio": split_result["config"]["val_ratio"],
        "requested_stratified": split_result["config"]["requested_stratified"],
        "paired": {
            "train": {
                "num_breasts": len(split_result["breast_ids"]["train"]),
                "num_rows": len(paired_train_rows),
                "label_counts": _label_counts(paired_train_rows),
            },
            "val": {
                "num_breasts": len(split_result["breast_ids"]["val"]),
                "num_rows": len(paired_val_rows),
                "label_counts": _label_counts(paired_val_rows),
            },
        },
        "single": {
            "train": {
                "num_breasts": len({row["breast_id"] for row in single_train_rows}),
                "num_images": len(single_train_rows),
                "label_counts": _label_counts(single_train_rows),
            },
            "val": {
                "num_breasts": len({row["breast_id"] for row in single_val_rows}),
                "num_images": len(single_val_rows),
                "label_counts": _label_counts(single_val_rows),
            },
        },
        "fold_assignment": {
            "available": bool(fold_assignment["rows"]),
            "fieldnames": list(fold_assignment["fieldnames"]),
            "fold_count": fold_assignment["num_folds"],
            "val_fold": fold_assignment["val_fold"],
            "train_folds": list(fold_assignment["train_folds"]),
            "train_val_derived_from_fold_assignment": fold_assignment["train_val_derived_from_assignment"],
        },
        "fold_summary": split_result["fold_summary"],
        "checks": split_result["checks"],
    }


def _load_csv_rows_with_fieldnames(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])
    return rows, fieldnames


def _validate_required_columns(stage: str, fieldnames: list[str], required_columns: frozenset[str]) -> None:
    missing = sorted(required_columns - set(fieldnames))
    if missing:
        raise SplitBuildError(f"{stage} is missing required columns: {', '.join(missing)}")


def _find_rows_with_empty_fields(
    rows: list[dict[str, str]],
    required_fields: tuple[str, ...],
) -> list[dict[str, Any]]:
    invalid_rows: list[dict[str, Any]] = []
    for row in rows:
        empty_fields = [field for field in required_fields if row.get(field, "").strip() == ""]
        if empty_fields:
            invalid_rows.append(
                {
                    "breast_id": row.get("breast_id", ""),
                    "empty_fields": empty_fields,
                }
            )
    return invalid_rows


def _parse_binary_label(raw_value: str, breast_id: str) -> int:
    try:
        label = int(raw_value)
    except ValueError as exc:
        raise SplitBuildError(
            f"Invalid is_malignant value '{raw_value}' for breast_id '{breast_id}'."
        ) from exc

    if label not in (0, 1):
        raise SplitBuildError(
            f"is_malignant must be 0 or 1, got '{raw_value}' for breast_id '{breast_id}'."
        )
    return label


def _select_split_indices(
    labels: list[int],
    breast_ids: list[str],
    val_ratio: float,
    random_state: int,
    stratified: bool,
) -> dict[str, Any]:
    fallback_info = {
        "requested_stratified": bool(stratified),
        "used_fallback": False,
        "reason": "",
    }
    empty_fold_assignment = {
        "available": False,
        "fold_by_index": {},
        "num_folds": 0,
        "val_fold": None,
        "train_folds": [],
        "train_val_derived_from_assignment": False,
    }

    if stratified:
        n_splits, reason = _infer_n_splits(val_ratio)
        class_counts = Counter(labels)
        if reason:
            fallback_info["used_fallback"] = True
            fallback_info["reason"] = reason
        elif len(labels) < n_splits or min(class_counts.values()) < n_splits:
            fallback_info["used_fallback"] = True
            fallback_info["reason"] = (
                f"StratifiedGroupKFold requires at least {n_splits} samples in each class; "
                f"got class counts {dict(class_counts)}."
            )
        else:
            try:
                fold_by_index = _materialize_stratified_group_folds(
                    labels=labels,
                    breast_ids=breast_ids,
                    n_splits=n_splits,
                    random_state=random_state,
                )
            except ValueError as exc:
                fallback_info["used_fallback"] = True
                fallback_info["reason"] = str(exc)
            else:
                val_fold = 0
                train_indices = sorted(index for index, fold in fold_by_index.items() if fold != val_fold)
                val_indices = sorted(index for index, fold in fold_by_index.items() if fold == val_fold)
                return {
                    "train_indices": train_indices,
                    "val_indices": val_indices,
                    "split_strategy": "stratified_group_holdout",
                    "fallback": fallback_info,
                    "fold_assignment": {
                        "available": True,
                        "fold_by_index": fold_by_index,
                        "num_folds": n_splits,
                        "val_fold": val_fold,
                        "train_folds": [fold for fold in range(n_splits) if fold != val_fold],
                        "train_val_derived_from_assignment": True,
                    },
                }

    splitter = GroupShuffleSplit(n_splits=1, test_size=val_ratio, random_state=random_state)
    try:
        train_indices, val_indices = next(
            splitter.split(X=[[0]] * len(labels), y=labels, groups=breast_ids)
        )
    except ValueError as exc:
        raise SplitBuildError(f"Failed to build group split: {exc}") from exc

    return {
        "train_indices": list(train_indices),
        "val_indices": list(val_indices),
        "split_strategy": "group_shuffle_holdout",
        "fallback": fallback_info,
        "fold_assignment": empty_fold_assignment,
    }


def _materialize_stratified_group_folds(
    labels: list[int],
    breast_ids: list[str],
    n_splits: int,
    random_state: int,
) -> dict[int, int]:
    splitter = StratifiedGroupKFold(
        n_splits=n_splits,
        shuffle=True,
        random_state=random_state,
    )
    fold_by_index: dict[int, int] = {}
    for fold_index, (_, val_indices) in enumerate(
        splitter.split(X=[[0]] * len(labels), y=labels, groups=breast_ids)
    ):
        for val_index in val_indices:
            fold_by_index[int(val_index)] = fold_index

    if len(fold_by_index) != len(labels):
        raise SplitBuildError(
            "StratifiedGroupKFold did not assign every breast_id to a fold.",
            {
                "assigned": len(fold_by_index),
                "expected": len(labels),
            },
        )
    return fold_by_index


def _build_fold_assignment_rows(
    paired_rows: list[dict[str, str]],
    paired_labels: list[int],
    image_counts_by_breast: Counter[str],
    fold_assignment_meta: dict[str, Any],
) -> list[dict[str, str]]:
    if not fold_assignment_meta["available"]:
        return []

    rows: list[dict[str, str]] = []
    fold_by_index = fold_assignment_meta["fold_by_index"]
    for index, row in enumerate(paired_rows):
        breast_id = row["breast_id"]
        rows.append(
            {
                "breast_id": breast_id,
                "fold": str(fold_by_index[index]),
                "target": str(paired_labels[index]),
                "num_images": str(int(image_counts_by_breast[breast_id])),
            }
        )

    rows.sort(key=lambda item: item["breast_id"])
    return rows


def _build_fold_summary(
    fold_assignment_rows: list[dict[str, str]],
    num_folds: int,
    requested_stratified: bool,
    fallback_info: dict[str, Any],
    val_fold: int | None,
    train_folds: list[int],
    train_val_derived_from_fold_assignment: bool,
) -> dict[str, Any]:
    if not fold_assignment_rows:
        warning = "Fold assignment unavailable because split used fallback group holdout."
        if not fallback_info["used_fallback"]:
            warning = "Fold assignment unavailable for the current split configuration."
        return {
            "total_breasts": 0,
            "fold_count": 0,
            "is_stratified": False,
            "used_fallback": bool(fallback_info["used_fallback"]),
            "fallback_reason": fallback_info["reason"],
            "val_fold": val_fold,
            "train_folds": list(train_folds),
            "train_val_derived_from_fold_assignment": train_val_derived_from_fold_assignment,
            "folds": [],
            "warnings": [warning],
        }

    folds: list[dict[str, Any]] = []
    warnings: list[str] = []
    rows_by_fold: dict[int, list[dict[str, str]]] = {fold: [] for fold in range(num_folds)}
    for row in fold_assignment_rows:
        rows_by_fold[int(row["fold"])].append(row)

    for fold in range(num_folds):
        fold_rows = rows_by_fold[fold]
        breast_count = len(fold_rows)
        image_count = sum(int(row["num_images"]) for row in fold_rows)
        malignant_count = sum(int(row["target"]) for row in fold_rows)
        non_malignant_count = breast_count - malignant_count
        malignant_ratio = None if breast_count == 0 else float(malignant_count / breast_count)
        fold_warnings: list[str] = []
        if breast_count == 0:
            fold_warnings.append(f"Fold {fold} is empty.")
        if breast_count > 0 and (malignant_count == 0 or non_malignant_count == 0):
            fold_warnings.append(f"Fold {fold} has an extremely imbalanced label distribution.")
        warnings.extend(fold_warnings)
        folds.append(
            {
                "fold": fold,
                "breast_count": breast_count,
                "image_count": image_count,
                "malignant_count": malignant_count,
                "non_malignant_count": non_malignant_count,
                "malignant_ratio": malignant_ratio,
                "warnings": fold_warnings,
            }
        )

    return {
        "total_breasts": len(fold_assignment_rows),
        "fold_count": num_folds,
        "is_stratified": requested_stratified and not fallback_info["used_fallback"],
        "used_fallback": bool(fallback_info["used_fallback"]),
        "fallback_reason": fallback_info["reason"],
        "val_fold": val_fold,
        "train_folds": list(train_folds),
        "train_val_derived_from_fold_assignment": train_val_derived_from_fold_assignment,
        "folds": folds,
        "warnings": warnings,
    }


def _infer_n_splits(val_ratio: float) -> tuple[int | None, str]:
    reciprocal = round(1.0 / val_ratio)
    if reciprocal < 2:
        return None, f"val_ratio={val_ratio} does not support a valid StratifiedGroupKFold split."
    if not isclose(val_ratio, 1.0 / reciprocal, rel_tol=0.0, abs_tol=1e-9):
        return (
            None,
            "StratifiedGroupKFold requires val_ratio to be the reciprocal of an integer "
            f"(got {val_ratio}).",
        )
    return reciprocal, ""


def _build_checks(
    paired_rows: list[dict[str, str]],
    single_rows: list[dict[str, str]],
    paired_train_rows: list[dict[str, str]],
    paired_val_rows: list[dict[str, str]],
    single_train_rows: list[dict[str, str]],
    single_val_rows: list[dict[str, str]],
    train_breast_ids: set[str],
    val_breast_ids: set[str],
    requested_stratified: bool,
    fallback_info: dict[str, Any],
    fold_assignment_meta: dict[str, Any],
    fold_assignment_rows: list[dict[str, str]],
    fold_summary: dict[str, Any],
) -> dict[str, Any]:
    overlap = sorted(train_breast_ids & val_breast_ids)
    covered_paired_ids = train_breast_ids | val_breast_ids
    all_paired_ids = {row["breast_id"] for row in paired_rows}
    single_train_ids = {row["breast_id"] for row in single_train_rows}
    single_val_ids = {row["breast_id"] for row in single_val_rows}
    mapped_single_ids = single_train_ids | single_val_ids
    invalid_paired_rows = _find_rows_with_empty_fields(paired_train_rows + paired_val_rows, PAIRED_CORE_FIELDS)

    empty_sides = []
    if not paired_train_rows or not single_train_rows:
        empty_sides.append("train")
    if not paired_val_rows or not single_val_rows:
        empty_sides.append("val")

    if fold_assignment_rows:
        assignment_breast_ids = [row["breast_id"] for row in fold_assignment_rows]
        duplicate_assignment_ids = [
            breast_id
            for breast_id, count in sorted(Counter(assignment_breast_ids).items())
            if count > 1
        ]
        assigned_fold_values = sorted({int(row["fold"]) for row in fold_assignment_rows})
        expected_fold_values = list(range(fold_assignment_meta["num_folds"]))
        empty_folds = [fold for fold in expected_fold_values if fold not in assigned_fold_values]
        expected_val_ids = {
            row["breast_id"]
            for row in fold_assignment_rows
            if int(row["fold"]) == fold_assignment_meta["val_fold"]
        }
        expected_train_ids = {
            row["breast_id"]
            for row in fold_assignment_rows
            if int(row["fold"]) != fold_assignment_meta["val_fold"]
        }
    else:
        duplicate_assignment_ids = []
        assigned_fold_values = []
        expected_fold_values = []
        empty_folds = []
        expected_val_ids = set()
        expected_train_ids = set()

    return {
        "breast_id_leakage": {
            "ok": not overlap,
            "overlap_count": len(overlap),
            "overlap_breast_ids": overlap,
        },
        "paired_split_coverage": {
            "ok": covered_paired_ids == all_paired_ids and len(paired_train_rows) + len(paired_val_rows) == len(paired_rows),
            "total_breasts": len(all_paired_ids),
            "covered_breasts": len(covered_paired_ids),
            "total_rows": len(paired_rows),
            "covered_rows": len(paired_train_rows) + len(paired_val_rows),
            "missing_breast_ids": sorted(all_paired_ids - covered_paired_ids),
        },
        "single_split_mapping": {
            "ok": mapped_single_ids == all_paired_ids and not (train_breast_ids & single_val_ids) and not (val_breast_ids & single_train_ids),
            "total_single_rows": len(single_rows),
            "covered_single_rows": len(single_train_rows) + len(single_val_rows),
            "train_breasts": len(single_train_ids),
            "val_breasts": len(single_val_ids),
            "unmapped_breast_ids": sorted(all_paired_ids - mapped_single_ids),
            "unexpected_breast_ids": sorted(mapped_single_ids - all_paired_ids),
        },
        "paired_core_fields_complete": {
            "ok": not invalid_paired_rows,
            "invalid_rows": invalid_paired_rows,
        },
        "non_empty_split": {
            "ok": not empty_sides,
            "empty_sides": empty_sides,
        },
        "fold_assignment_unique": {
            "ok": not duplicate_assignment_ids and (not fold_assignment_rows or len(assignment_breast_ids) == len(all_paired_ids)),
            "available": bool(fold_assignment_rows),
            "duplicate_breast_ids": duplicate_assignment_ids,
            "assigned_breasts": len(fold_assignment_rows),
            "expected_breasts": len(all_paired_ids),
        },
        "fold_distribution_non_empty": {
            "ok": not fold_assignment_rows or not empty_folds,
            "available": bool(fold_assignment_rows),
            "assigned_folds": assigned_fold_values,
            "expected_folds": expected_fold_values,
            "empty_folds": empty_folds,
        },
        "train_val_matches_fold_assignment": {
            "ok": not fold_assignment_rows or (expected_train_ids == train_breast_ids and expected_val_ids == val_breast_ids),
            "available": bool(fold_assignment_rows),
            "val_fold": fold_assignment_meta["val_fold"],
            "train_folds": list(fold_assignment_meta["train_folds"]),
            "train_val_derived_from_fold_assignment": fold_assignment_meta["train_val_derived_from_assignment"],
        },
        "fold_label_distribution": {
            "ok": True,
            "available": bool(fold_assignment_rows),
            "warnings": list(fold_summary["warnings"]),
        },
        "strategy_fallback": {
            "ok": True,
            "requested_stratified": requested_stratified,
            "used_fallback": bool(fallback_info["used_fallback"]),
            "reason": fallback_info["reason"],
        },
    }


def _raise_on_failed_checks(checks: dict[str, Any]) -> None:
    failed_checks = [name for name, payload in checks.items() if not payload.get("ok", False)]
    if failed_checks:
        lines = ["Split validation failed."]
        for check_name in failed_checks:
            lines.append(f"- {check_name}")
        raise SplitBuildError("\n".join(lines), {"checks": checks})


def _label_counts(rows: list[dict[str, str]]) -> dict[str, int]:
    return {str(key): count for key, count in sorted(Counter(int(row["is_malignant"]) for row in rows).items())}
