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

    train_indices, val_indices, split_strategy, fallback_info = _select_split_indices(
        labels=paired_labels,
        breast_ids=paired_breast_ids,
        val_ratio=val_ratio,
        random_state=random_state,
        stratified=stratified,
    )

    train_breast_ids = {paired_breast_ids[index] for index in train_indices}
    val_breast_ids = {paired_breast_ids[index] for index in val_indices}
    paired_train_rows = [row for row in paired_rows if row["breast_id"] in train_breast_ids]
    paired_val_rows = [row for row in paired_rows if row["breast_id"] in val_breast_ids]
    single_train_rows = [row for row in single_rows if row["breast_id"] in train_breast_ids]
    single_val_rows = [row for row in single_rows if row["breast_id"] in val_breast_ids]

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
        "checks": checks,
    }


def write_split_artifacts(
    split_result: dict[str, Any],
    output_dir: str | Path = DEFAULT_SPLIT_DIR,
) -> dict[str, Path]:
    """Write reusable split CSVs and the JSON summary report."""

    output_root = Path(output_dir)
    paired = split_result["paired"]
    single = split_result["single"]

    paired_train_path = output_root / PAIRED_SPLIT_FILENAMES["train"]
    paired_val_path = output_root / PAIRED_SPLIT_FILENAMES["val"]
    single_train_path = output_root / SINGLE_SPLIT_FILENAMES["train"]
    single_val_path = output_root / SINGLE_SPLIT_FILENAMES["val"]
    summary_path = output_root / SUMMARY_FILENAME

    write_csv_rows(paired_train_path, paired["fieldnames"], paired["train_rows"])
    write_csv_rows(paired_val_path, paired["fieldnames"], paired["val_rows"])
    write_csv_rows(single_train_path, single["fieldnames"], single["train_rows"])
    write_csv_rows(single_val_path, single["fieldnames"], single["val_rows"])
    write_json_file(summary_path, build_split_summary(split_result))

    return {
        "paired_train": paired_train_path,
        "paired_val": paired_val_path,
        "single_train": single_train_path,
        "single_val": single_val_path,
        "summary": summary_path,
    }


def build_split_summary(split_result: dict[str, Any]) -> dict[str, Any]:
    """Build the JSON summary stored next to the reusable split CSVs."""

    paired_train_rows = split_result["paired"]["train_rows"]
    paired_val_rows = split_result["paired"]["val_rows"]
    single_train_rows = split_result["single"]["train_rows"]
    single_val_rows = split_result["single"]["val_rows"]

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
) -> tuple[list[int], list[int], str, dict[str, Any]]:
    fallback_info = {
        "requested_stratified": bool(stratified),
        "used_fallback": False,
        "reason": "",
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
            splitter = StratifiedGroupKFold(
                n_splits=n_splits,
                shuffle=True,
                random_state=random_state,
            )
            try:
                train_indices, val_indices = next(
                    splitter.split(X=[[0]] * len(labels), y=labels, groups=breast_ids)
                )
                return (
                    list(train_indices),
                    list(val_indices),
                    "stratified_group_holdout",
                    fallback_info,
                )
            except ValueError as exc:
                fallback_info["used_fallback"] = True
                fallback_info["reason"] = str(exc)

    splitter = GroupShuffleSplit(n_splits=1, test_size=val_ratio, random_state=random_state)
    try:
        train_indices, val_indices = next(
            splitter.split(X=[[0]] * len(labels), y=labels, groups=breast_ids)
        )
    except ValueError as exc:
        raise SplitBuildError(f"Failed to build group split: {exc}") from exc

    return list(train_indices), list(val_indices), "group_shuffle_holdout", fallback_info


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
