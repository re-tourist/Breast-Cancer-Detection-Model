"""Metrics helpers for Stage 1 evaluation."""

from __future__ import annotations

from collections import Counter
from typing import Any, Sequence

from sklearn.metrics import roc_auc_score


def compute_binary_auroc(targets: Sequence[int], predictions: Sequence[float]) -> float | None:
    """Compute AUROC with safe single-class fallback."""

    if len(set(int(target) for target in targets)) < 2:
        return None
    return float(roc_auc_score(list(targets), list(predictions)))


def build_breast_level_metrics(
    breast_prediction_rows: list[dict[str, Any]],
    aggregation: str,
) -> dict[str, Any]:
    """Build the minimal breast-level metrics summary."""

    targets = [int(row["target"]) for row in breast_prediction_rows]
    predictions = [float(row["prediction"]) for row in breast_prediction_rows]
    breast_auroc = compute_binary_auroc(targets, predictions)

    return {
        "aggregation": aggregation,
        "num_breasts": len(breast_prediction_rows),
        "label_counts": {
            str(label): count
            for label, count in sorted(Counter(targets).items())
        },
        "breast_auroc": breast_auroc,
        "auroc_available": breast_auroc is not None,
        "auroc_reason": "" if breast_auroc is not None else "Only one target class present in breast-level predictions.",
    }
