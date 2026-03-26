"""Prediction collection and artifact writing helpers for Stage 1 evaluation."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import torch
from torch import nn
from torch.utils.data import DataLoader

from .aggregation import BREAST_LEVEL_PREDICTION_FIELDS, aggregate_prediction_rows
from .metrics import build_breast_level_metrics


IMAGE_LEVEL_PREDICTION_FIELDS = (
    "image_id",
    "breast_id",
    "target",
    "prediction",
    "image_path",
    "view",
)
IMAGE_LEVEL_PREDICTIONS_FILENAME = "image_level_predictions.csv"
BREAST_LEVEL_PREDICTIONS_FILENAME = "breast_level_predictions.csv"
BREAST_LEVEL_METRICS_FILENAME = "breast_level_metrics.json"


def collect_single_image_prediction_rows(
    model: nn.Module,
    loader: DataLoader[dict[str, Any]],
    device: torch.device,
) -> list[dict[str, Any]]:
    """Collect image-level prediction rows from a single-image validation loader."""

    model.eval()
    prediction_rows: list[dict[str, Any]] = []

    with torch.no_grad():
        for batch in loader:
            images = batch["image"].to(device)
            logits = model(images)
            probabilities = torch.sigmoid(logits).cpu().tolist()
            targets = batch["target"].cpu().tolist()

            for index, probability in enumerate(probabilities):
                prediction_rows.append(
                    {
                        "image_id": str(batch["image_id"][index]),
                        "breast_id": str(batch["breast_id"][index]),
                        "target": int(targets[index]),
                        "prediction": float(probability),
                        "image_path": str(batch["image_path"][index]),
                        "view": str(batch["view"][index]),
                    }
                )

    return prediction_rows


def evaluate_prediction_rows(
    prediction_rows: list[dict[str, Any]],
    aggregation: str = "mean",
    item_id_field: str | None = "image_id",
) -> dict[str, Any]:
    """Aggregate prediction rows and build the minimal breast-level metrics payload."""

    breast_prediction_rows = aggregate_prediction_rows(
        prediction_rows=prediction_rows,
        aggregation=aggregation,
        item_id_field=item_id_field,
    )
    metrics = build_breast_level_metrics(
        breast_prediction_rows=breast_prediction_rows,
        aggregation=aggregation,
    )
    return {
        "image_prediction_rows": prediction_rows,
        "breast_prediction_rows": breast_prediction_rows,
        "metrics": metrics,
    }


def write_evaluation_artifacts(
    output_dir: str | Path,
    breast_prediction_rows: list[dict[str, Any]],
    metrics: dict[str, Any],
    image_prediction_rows: list[dict[str, Any]] | None = None,
) -> dict[str, Path]:
    """Write evaluation artifacts to disk."""

    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)

    image_predictions_path = output_root / IMAGE_LEVEL_PREDICTIONS_FILENAME
    breast_predictions_path = output_root / BREAST_LEVEL_PREDICTIONS_FILENAME
    metrics_path = output_root / BREAST_LEVEL_METRICS_FILENAME

    if image_prediction_rows is not None:
        _write_csv_rows(
            path=image_predictions_path,
            fieldnames=IMAGE_LEVEL_PREDICTION_FIELDS,
            rows=image_prediction_rows,
        )
    _write_csv_rows(
        path=breast_predictions_path,
        fieldnames=BREAST_LEVEL_PREDICTION_FIELDS,
        rows=breast_prediction_rows,
    )
    with metrics_path.open("w", encoding="utf-8") as handle:
        json.dump(metrics, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    return {
        "image_predictions": image_predictions_path,
        "breast_predictions": breast_predictions_path,
        "metrics": metrics_path,
    }


def _write_csv_rows(
    path: Path,
    fieldnames: tuple[str, ...],
    rows: list[dict[str, Any]],
) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})
