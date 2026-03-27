"""Minimal evaluation interface for Stage 1 breast-level aggregation."""

from .aggregation import AGGREGATION_CHOICES, BREAST_LEVEL_PREDICTION_FIELDS, aggregate_prediction_rows
from .metrics import build_breast_level_metrics, compute_binary_auroc
from .pipeline import (
    BREAST_LEVEL_METRICS_FILENAME,
    BREAST_LEVEL_PREDICTIONS_FILENAME,
    IMAGE_LEVEL_PREDICTIONS_FILENAME,
    IMAGE_LEVEL_PREDICTION_FIELDS,
    PAIRED_BREAST_LEVEL_PREDICTION_FIELDS,
    collect_paired_breast_prediction_rows,
    collect_single_image_prediction_rows,
    evaluate_breast_prediction_rows,
    evaluate_prediction_rows,
    write_evaluation_artifacts,
)

__all__ = [
    "AGGREGATION_CHOICES",
    "BREAST_LEVEL_PREDICTION_FIELDS",
    "IMAGE_LEVEL_PREDICTION_FIELDS",
    "PAIRED_BREAST_LEVEL_PREDICTION_FIELDS",
    "IMAGE_LEVEL_PREDICTIONS_FILENAME",
    "BREAST_LEVEL_PREDICTIONS_FILENAME",
    "BREAST_LEVEL_METRICS_FILENAME",
    "aggregate_prediction_rows",
    "compute_binary_auroc",
    "build_breast_level_metrics",
    "collect_paired_breast_prediction_rows",
    "collect_single_image_prediction_rows",
    "evaluate_breast_prediction_rows",
    "evaluate_prediction_rows",
    "write_evaluation_artifacts",
]
