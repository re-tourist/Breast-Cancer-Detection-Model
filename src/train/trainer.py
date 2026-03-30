"""Training utilities for the single-image fallback and Stage 2 paired baseline."""

from __future__ import annotations

import random
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import numpy as np
import torch
from sklearn.metrics import roc_auc_score
from torch import nn
from torch.utils.data import DataLoader

from src.data.datasets import DEFAULT_ARCHIVE_PATH, PairedBreastDataset, SingleImageDataset
from src.data.transforms import build_eval_transform, build_train_transform

SELECTION_METRIC_CHOICES = ("auto", "breast_auroc", "breast_mean_auroc", "image_auroc", "val_loss")
DEFAULT_SINGLE_AUTO_SELECTION_METRICS = ("breast_mean_auroc", "image_auroc", "val_loss")
DEFAULT_PAIRED_AUTO_SELECTION_METRICS = ("breast_auroc", "val_loss")
_SELECTION_PRIORITIES = {
    "breast_auroc": 4,
    "breast_mean_auroc": 3,
    "image_auroc": 2,
    "val_loss": 1,
}


@dataclass
class SingleImageLoaderBundle:
    """Own the datasets and dataloaders needed by the single-image train loop."""

    train_dataset: SingleImageDataset
    val_dataset: SingleImageDataset
    train_loader: DataLoader[dict[str, Any]]
    val_loader: DataLoader[dict[str, Any]]

    def close(self) -> None:
        self.train_dataset.close()
        self.val_dataset.close()


@dataclass
class PairedBreastLoaderBundle:
    """Own the datasets and dataloaders needed by the paired train loop."""

    train_dataset: PairedBreastDataset
    val_dataset: PairedBreastDataset
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


def build_paired_breast_loaders(
    train_split_csv_path: str | Path,
    val_split_csv_path: str | Path,
    archive_path: str | Path = DEFAULT_ARCHIVE_PATH,
    image_root: str | Path | None = None,
    image_size: int = 1024,
    batch_size: int = 8,
    num_workers: int = 0,
) -> PairedBreastLoaderBundle:
    """Build train/val dataloaders from the reusable paired split artifacts."""

    train_dataset = PairedBreastDataset(
        index_csv_path=train_split_csv_path,
        archive_path=archive_path,
        transform=build_train_transform(image_size=image_size, num_channels=3, enable_augmentation=False),
        image_root=image_root,
    )
    val_dataset = PairedBreastDataset(
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
    return PairedBreastLoaderBundle(
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
    """Run one training epoch for the single-image baseline."""

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


def train_one_epoch_paired(
    model: nn.Module,
    loader: DataLoader[dict[str, Any]],
    optimizer: torch.optim.Optimizer,
    criterion: nn.Module,
    device: torch.device,
) -> dict[str, float]:
    """Run one training epoch for the paired breast-level baseline."""

    model.train()
    total_loss = 0.0
    total_samples = 0

    for batch in loader:
        x_cc = batch["x_cc"].to(device)
        x_mlo = batch["x_mlo"].to(device)
        targets = batch["target"].to(device)

        optimizer.zero_grad(set_to_none=True)
        logits = model(x_cc, x_mlo)
        loss = criterion(logits, targets)
        loss.backward()
        optimizer.step()

        batch_size = x_cc.size(0)
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


def validate_one_epoch_paired(
    model: nn.Module,
    loader: DataLoader[dict[str, Any]],
    criterion: nn.Module,
    device: torch.device,
) -> dict[str, Any]:
    """Run one validation epoch for the paired breast-level baseline."""

    model.eval()
    total_loss = 0.0
    total_samples = 0
    probabilities: list[float] = []
    targets: list[int] = []

    with torch.no_grad():
        for batch in loader:
            x_cc = batch["x_cc"].to(device)
            x_mlo = batch["x_mlo"].to(device)
            batch_targets = batch["target"].to(device)
            logits = model(x_cc, x_mlo)
            loss = criterion(logits, batch_targets)

            batch_size = x_cc.size(0)
            total_loss += loss.item() * batch_size
            total_samples += batch_size

            probabilities.extend(float(value) for value in torch.sigmoid(logits).cpu().tolist())
            targets.extend(int(value) for value in batch_targets.cpu().tolist())

    return {
        "val_loss": total_loss / max(total_samples, 1),
        "breast_accuracy": _binary_accuracy(targets, probabilities),
        "breast_auroc": _safe_auroc(targets, probabilities),
        "num_val_breasts": total_samples,
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
    selection_metric: str = "auto",
) -> dict[str, Any]:
    """Run the single-image train/val loop and save the best checkpoint."""

    return _fit_loop(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        optimizer=optimizer,
        criterion=criterion,
        device=device,
        epochs=epochs,
        output_dir=output_dir,
        selection_metric=selection_metric,
        train_epoch_fn=train_one_epoch,
        validate_epoch_fn=validate_one_epoch,
        auto_metric_preferences=DEFAULT_SINGLE_AUTO_SELECTION_METRICS,
        metric_display_order=(
            ("image_accuracy", "image_acc"),
            ("image_auroc", "image_auroc"),
            ("breast_mean_accuracy", "breast_mean_acc"),
            ("breast_mean_auroc", "breast_mean_auroc"),
        ),
    )


def fit_paired(
    model: nn.Module,
    train_loader: DataLoader[dict[str, Any]],
    val_loader: DataLoader[dict[str, Any]],
    optimizer: torch.optim.Optimizer,
    criterion: nn.Module,
    device: torch.device,
    epochs: int,
    output_dir: str | Path,
    selection_metric: str = "auto",
) -> dict[str, Any]:
    """Run the paired train/val loop and save the best checkpoint."""

    return _fit_loop(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        optimizer=optimizer,
        criterion=criterion,
        device=device,
        epochs=epochs,
        output_dir=output_dir,
        selection_metric=selection_metric,
        train_epoch_fn=train_one_epoch_paired,
        validate_epoch_fn=validate_one_epoch_paired,
        auto_metric_preferences=DEFAULT_PAIRED_AUTO_SELECTION_METRICS,
        metric_display_order=(
            ("breast_accuracy", "breast_acc"),
            ("breast_auroc", "breast_auroc"),
        ),
    )


def _fit_loop(
    model: nn.Module,
    train_loader: DataLoader[dict[str, Any]],
    val_loader: DataLoader[dict[str, Any]],
    optimizer: torch.optim.Optimizer,
    criterion: nn.Module,
    device: torch.device,
    epochs: int,
    output_dir: str | Path,
    selection_metric: str,
    train_epoch_fn: Callable[..., dict[str, Any]],
    validate_epoch_fn: Callable[..., dict[str, Any]],
    auto_metric_preferences: tuple[str, ...],
    metric_display_order: tuple[tuple[str, str], ...],
) -> dict[str, Any]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    checkpoint_path = output_path / "best_model.pt"

    history: list[dict[str, Any]] = []
    best_epoch = -1
    best_metrics: dict[str, Any] | None = None
    best_selection: dict[str, Any] | None = None
    selection_mode = "auto" if selection_metric == "auto" else "explicit"
    primary_selection_metric = (
        auto_metric_preferences[0] if selection_metric == "auto" else selection_metric
    )

    for epoch in range(1, epochs + 1):
        train_metrics = train_epoch_fn(model, train_loader, optimizer, criterion, device)
        val_metrics = validate_epoch_fn(model, val_loader, criterion, device)
        epoch_metrics = {"epoch": epoch, **train_metrics, **val_metrics}
        selection_info = resolve_selection_metric(
            epoch_metrics,
            selection_metric=selection_metric,
            auto_metric_preferences=auto_metric_preferences,
        )
        epoch_metrics.update(
            {
                "selection_metric_name": selection_info["metric_name"],
                "selection_metric_value": selection_info["metric_value"],
                "selection_fallback_used": selection_info["fallback_used"],
                "selection_fallback_reason": selection_info["fallback_reason"],
            }
        )
        history.append(epoch_metrics)
        print(
            _format_epoch_summary(epoch, epochs, epoch_metrics, selection_info, metric_display_order),
            flush=True,
        )

        if is_better_selection(selection_info, best_selection):
            best_epoch = epoch
            best_metrics = dict(epoch_metrics)
            best_selection = dict(selection_info)
            torch.save(model.state_dict(), checkpoint_path)

    if best_epoch == -1:
        if selection_mode == "explicit":
            raise ValueError(
                f"Selection metric '{selection_metric}' was unavailable for every epoch. "
                "Use --selection-metric auto or val_loss."
            )
        raise RuntimeError("Training finished without producing any epoch metrics.")

    if best_metrics is None or best_selection is None:
        raise RuntimeError("Training finished without a valid best checkpoint selection.")

    return {
        "history": history,
        "best_epoch": best_epoch,
        "best_metrics": best_metrics,
        "best_checkpoint_path": checkpoint_path,
        "primary_selection_metric": primary_selection_metric,
        "selection_mode": selection_mode,
        "best_metric_name": best_selection["metric_name"],
        "best_metric_value": best_selection["metric_value"],
        "fallback_used": best_selection["fallback_used"],
        "fallback_reason": best_selection["fallback_reason"],
    }


def resolve_selection_metric(
    epoch_metrics: dict[str, Any],
    selection_metric: str = "auto",
    auto_metric_preferences: tuple[str, ...] = DEFAULT_SINGLE_AUTO_SELECTION_METRICS,
) -> dict[str, Any]:
    """Resolve the metric used for best-checkpoint selection for one epoch."""

    if selection_metric not in SELECTION_METRIC_CHOICES:
        raise ValueError(
            f"Unsupported selection_metric '{selection_metric}'. "
            f"Expected one of: {', '.join(SELECTION_METRIC_CHOICES)}."
        )

    if selection_metric == "auto":
        unavailable_metrics: list[str] = []
        for metric_name in auto_metric_preferences:
            metric_value = epoch_metrics.get(metric_name)
            if metric_value is None:
                unavailable_metrics.append(metric_name)
                continue

            fallback_used = bool(unavailable_metrics)
            fallback_reason = ""
            if fallback_used:
                fallback_reason = f"{_join_metric_names(unavailable_metrics)} unavailable for this epoch."
            return _build_selection_info(
                metric_name=metric_name,
                metric_value=metric_value,
                higher_is_better=metric_name != "val_loss",
                fallback_used=fallback_used,
                fallback_reason=fallback_reason,
            )

        raise RuntimeError(
            "Auto selection metrics were all unavailable and no fallback metric could be resolved."
        )

    metric_value = epoch_metrics.get(selection_metric)
    return _build_selection_info(
        metric_name=selection_metric,
        metric_value=metric_value,
        higher_is_better=selection_metric != "val_loss",
        fallback_used=False,
        fallback_reason="",
    )


def is_better_selection(
    candidate: dict[str, Any],
    current_best: dict[str, Any] | None,
) -> bool:
    """Compare two candidate best-checkpoint selections."""

    candidate_value = candidate["metric_value"]
    if candidate_value is None:
        return False
    if current_best is None:
        return True

    if candidate["priority_rank"] != current_best["priority_rank"]:
        return candidate["priority_rank"] > current_best["priority_rank"]

    current_best_value = current_best["metric_value"]
    if current_best_value is None:
        return True
    if candidate["higher_is_better"]:
        return candidate_value > current_best_value
    return candidate_value < current_best_value


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


def _build_selection_info(
    metric_name: str,
    metric_value: float | None,
    higher_is_better: bool,
    fallback_used: bool,
    fallback_reason: str,
) -> dict[str, Any]:
    return {
        "metric_name": metric_name,
        "metric_value": None if metric_value is None else float(metric_value),
        "higher_is_better": higher_is_better,
        "fallback_used": fallback_used,
        "fallback_reason": fallback_reason,
        "priority_rank": _SELECTION_PRIORITIES[metric_name],
    }


def _join_metric_names(metric_names: list[str] | tuple[str, ...]) -> str:
    names = list(metric_names)
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} and {names[1]}"
    return f"{', '.join(names[:-1])}, and {names[-1]}"


def _format_epoch_summary(
    epoch: int,
    epochs: int,
    epoch_metrics: dict[str, Any],
    selection_info: dict[str, Any],
    metric_display_order: tuple[tuple[str, str], ...],
) -> str:
    summary_parts = [
        f"Epoch {epoch}/{epochs}",
        f"train_loss={epoch_metrics['train_loss']:.4f}",
        f"val_loss={epoch_metrics['val_loss']:.4f}",
    ]
    for metric_name, label in metric_display_order:
        if metric_name in epoch_metrics:
            summary_parts.append(f"{label}={_format_metric_value(epoch_metrics[metric_name])}")
    summary_parts.append(
        f"selection={selection_info['metric_name']}:{_format_metric_value(selection_info['metric_value'])}"
    )
    return " ".join(summary_parts)
