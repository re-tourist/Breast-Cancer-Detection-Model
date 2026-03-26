"""Minimal training utilities for the Stage 1 single-image baseline."""

from __future__ import annotations

import random
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import torch
from sklearn.metrics import roc_auc_score
from torch import nn
from torch.utils.data import DataLoader

from src.data.datasets import DEFAULT_ARCHIVE_PATH, SingleImageDataset
from src.data.transforms import build_eval_transform, build_train_transform


@dataclass
class SingleImageLoaderBundle:
    """Own the datasets and dataloaders needed by the minimal train loop."""

    train_dataset: SingleImageDataset
    val_dataset: SingleImageDataset
    train_loader: DataLoader[dict[str, Any]]
    val_loader: DataLoader[dict[str, Any]]

    def close(self) -> None:
        self.train_dataset.close()
        self.val_dataset.close()


def set_random_seed(seed: int) -> None:
    """Set random seeds for the current process."""

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def build_single_image_loaders(
    train_split_csv_path: str | Path,
    val_split_csv_path: str | Path,
    archive_path: str | Path = DEFAULT_ARCHIVE_PATH,
    image_root: str | Path | None = None,
    image_size: int = 1024,
    batch_size: int = 8,
    num_workers: int = 0,
) -> SingleImageLoaderBundle:
    """Build train/val dataloaders from the reusable single-image split artifacts."""

    train_dataset = SingleImageDataset(
        index_csv_path=train_split_csv_path,
        archive_path=archive_path,
        transform=build_train_transform(image_size=image_size, num_channels=3, enable_augmentation=False),
        image_root=image_root,
    )
    val_dataset = SingleImageDataset(
        index_csv_path=val_split_csv_path,
        archive_path=archive_path,
        transform=build_eval_transform(image_size=image_size, num_channels=3),
        image_root=image_root,
    )
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
    )
    return SingleImageLoaderBundle(
        train_dataset=train_dataset,
        val_dataset=val_dataset,
        train_loader=train_loader,
        val_loader=val_loader,
    )


def compute_pos_weight(train_rows: list[dict[str, str]]) -> float:
    """Compute the positive-class weight from the training split."""

    labels = [int(row["is_malignant"]) for row in train_rows]
    positive_count = sum(labels)
    negative_count = len(labels) - positive_count
    if positive_count == 0:
        raise ValueError("Training split contains no positive samples; cannot compute pos_weight.")
    if negative_count == 0:
        raise ValueError("Training split contains no negative samples; cannot compute pos_weight.")
    return float(negative_count / positive_count)


def train_one_epoch(
    model: nn.Module,
    loader: DataLoader[dict[str, Any]],
    optimizer: torch.optim.Optimizer,
    criterion: nn.Module,
    device: torch.device,
) -> dict[str, float]:
    """Run one training epoch and return the average train loss."""

    model.train()
    total_loss = 0.0
    total_samples = 0

    for batch in loader:
        images = batch["image"].to(device)
        targets = batch["target"].to(device)

        optimizer.zero_grad(set_to_none=True)
        logits = model(images)
        loss = criterion(logits, targets)
        loss.backward()
        optimizer.step()

        batch_size = images.size(0)
        total_loss += loss.item() * batch_size
        total_samples += batch_size

    return {"train_loss": total_loss / max(total_samples, 1)}


def validate_one_epoch(
    model: nn.Module,
    loader: DataLoader[dict[str, Any]],
    criterion: nn.Module,
    device: torch.device,
) -> dict[str, Any]:
    """Run one validation epoch and return image-level and breast-level metrics."""

    model.eval()
    total_loss = 0.0
    total_samples = 0
    probabilities: list[float] = []
    targets: list[int] = []
    breast_ids: list[str] = []

    with torch.no_grad():
        for batch in loader:
            images = batch["image"].to(device)
            batch_targets = batch["target"].to(device)
            logits = model(images)
            loss = criterion(logits, batch_targets)

            batch_size = images.size(0)
            total_loss += loss.item() * batch_size
            total_samples += batch_size

            batch_probabilities = torch.sigmoid(logits).cpu().tolist()
            probabilities.extend(float(probability) for probability in batch_probabilities)
            targets.extend(int(value) for value in batch_targets.cpu().tolist())
            breast_ids.extend(str(breast_id) for breast_id in batch["breast_id"])

    breast_targets, breast_probabilities = _aggregate_breast_mean_predictions(
        probabilities=probabilities,
        targets=targets,
        breast_ids=breast_ids,
    )

    return {
        "val_loss": total_loss / max(total_samples, 1),
        "image_accuracy": _binary_accuracy(targets, probabilities),
        "image_auroc": _safe_auroc(targets, probabilities),
        "breast_mean_accuracy": _binary_accuracy(breast_targets, breast_probabilities),
        "breast_mean_auroc": _safe_auroc(breast_targets, breast_probabilities),
        "num_val_images": total_samples,
        "num_val_breasts": len(breast_targets),
    }


def fit(
    model: nn.Module,
    train_loader: DataLoader[dict[str, Any]],
    val_loader: DataLoader[dict[str, Any]],
    optimizer: torch.optim.Optimizer,
    criterion: nn.Module,
    device: torch.device,
    epochs: int,
    output_dir: str | Path,
) -> dict[str, Any]:
    """Run the minimal train/val loop and save the best checkpoint by val loss."""

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    checkpoint_path = output_path / "best_model.pt"

    history: list[dict[str, Any]] = []
    best_epoch = -1
    best_val_loss = float("inf")

    for epoch in range(1, epochs + 1):
        train_metrics = train_one_epoch(model, train_loader, optimizer, criterion, device)
        val_metrics = validate_one_epoch(model, val_loader, criterion, device)
        epoch_metrics = {
            "epoch": epoch,
            **train_metrics,
            **val_metrics,
        }
        history.append(epoch_metrics)
        print(
            "Epoch "
            f"{epoch}/{epochs} "
            f"train_loss={epoch_metrics['train_loss']:.4f} "
            f"val_loss={epoch_metrics['val_loss']:.4f} "
            f"image_acc={epoch_metrics['image_accuracy']:.4f} "
            f"image_auroc={_format_metric_value(epoch_metrics['image_auroc'])} "
            f"breast_mean_acc={epoch_metrics['breast_mean_accuracy']:.4f} "
            f"breast_mean_auroc={_format_metric_value(epoch_metrics['breast_mean_auroc'])}"
        )

        if val_metrics["val_loss"] < best_val_loss:
            best_val_loss = float(val_metrics["val_loss"])
            best_epoch = epoch
            torch.save(model.state_dict(), checkpoint_path)

    if best_epoch == -1:
        raise RuntimeError("Training finished without producing any epoch metrics.")

    best_metrics = next(metric for metric in history if metric["epoch"] == best_epoch)
    return {
        "history": history,
        "best_epoch": best_epoch,
        "best_metrics": best_metrics,
        "best_checkpoint_path": checkpoint_path,
    }


def _binary_accuracy(targets: list[int], probabilities: list[float]) -> float:
    if not targets:
        return 0.0
    predictions = [1 if probability >= 0.5 else 0 for probability in probabilities]
    correct = sum(int(prediction == target) for prediction, target in zip(predictions, targets))
    return float(correct / len(targets))


def _safe_auroc(targets: list[int], probabilities: list[float]) -> float | None:
    if len(set(targets)) < 2:
        return None
    return float(roc_auc_score(targets, probabilities))


def _format_metric_value(value: float | None) -> str:
    if value is None:
        return "None"
    return f"{value:.4f}"


def _aggregate_breast_mean_predictions(
    probabilities: list[float],
    targets: list[int],
    breast_ids: list[str],
) -> tuple[list[int], list[float]]:
    grouped_probabilities: dict[str, list[float]] = defaultdict(list)
    grouped_targets: dict[str, list[int]] = defaultdict(list)

    for probability, target, breast_id in zip(probabilities, targets, breast_ids):
        grouped_probabilities[breast_id].append(probability)
        grouped_targets[breast_id].append(target)

    mean_targets: list[int] = []
    mean_probabilities: list[float] = []
    for breast_id in sorted(grouped_probabilities):
        target_values = grouped_targets[breast_id]
        if len(set(target_values)) != 1:
            raise ValueError(f"Inconsistent targets found for breast_id '{breast_id}'.")
        mean_targets.append(target_values[0])
        mean_probabilities.append(float(sum(grouped_probabilities[breast_id]) / len(grouped_probabilities[breast_id])))

    return mean_targets, mean_probabilities
