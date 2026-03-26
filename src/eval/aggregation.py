"""Breast-level aggregation helpers for Stage 1 evaluation."""

from __future__ import annotations

from collections import defaultdict
from typing import Any


AGGREGATION_CHOICES = ("mean", "max")
BREAST_LEVEL_PREDICTION_FIELDS = (
    "breast_id",
    "target",
    "prediction",
    "num_items_aggregated",
    "item_ids",
)


def aggregate_prediction_rows(
    prediction_rows: list[dict[str, Any]],
    aggregation: str = "mean",
    group_field: str = "breast_id",
    target_field: str = "target",
    prediction_field: str = "prediction",
    item_id_field: str | None = "image_id",
) -> list[dict[str, Any]]:
    """Aggregate prediction rows into one breast-level prediction per breast_id."""

    if aggregation not in AGGREGATION_CHOICES:
        raise ValueError(
            f"Unsupported aggregation '{aggregation}'. Expected one of: {', '.join(AGGREGATION_CHOICES)}."
        )

    grouped_predictions: dict[str, list[float]] = defaultdict(list)
    grouped_targets: dict[str, list[int]] = defaultdict(list)
    grouped_item_ids: dict[str, list[str]] = defaultdict(list)

    for row in prediction_rows:
        breast_id = str(row[group_field])
        grouped_predictions[breast_id].append(float(row[prediction_field]))
        grouped_targets[breast_id].append(int(row[target_field]))
        if item_id_field and str(row.get(item_id_field, "")):
            grouped_item_ids[breast_id].append(str(row[item_id_field]))

    aggregated_rows: list[dict[str, Any]] = []
    for breast_id in sorted(grouped_predictions):
        target_values = grouped_targets[breast_id]
        if len(set(target_values)) != 1:
            raise ValueError(f"Inconsistent targets found for breast_id '{breast_id}'.")

        prediction_values = grouped_predictions[breast_id]
        if aggregation == "mean":
            aggregated_prediction = float(sum(prediction_values) / len(prediction_values))
        else:
            aggregated_prediction = float(max(prediction_values))

        unique_item_ids = sorted(set(grouped_item_ids[breast_id]))
        aggregated_rows.append(
            {
                "breast_id": breast_id,
                "target": target_values[0],
                "prediction": aggregated_prediction,
                "num_items_aggregated": len(prediction_values),
                "item_ids": "|".join(unique_item_ids),
            }
        )

    return aggregated_rows
