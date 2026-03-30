"""Train the single-image fallback or the Stage 2 paired baseline on reusable split artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import torch
from torch import nn
from torchvision import models


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.data.datasets import DEFAULT_ARCHIVE_PATH  # noqa: E402
from src.models.baseline import MinimalSingleImageCNN, PairedEfficientNetB2Baseline  # noqa: E402
from src.train.trainer import (  # noqa: E402
    SELECTION_METRIC_CHOICES,
    build_paired_breast_loaders,
    build_single_image_loaders,
    compute_pos_weight,
    fit,
    fit_paired,
    set_random_seed,
)


DEFAULT_SINGLE_TRAIN_SPLIT = REPO_ROOT / "data" / "processed" / "splits" / "primary_single_image_split_train.csv"
DEFAULT_SINGLE_VAL_SPLIT = REPO_ROOT / "data" / "processed" / "splits" / "primary_single_image_split_val.csv"
DEFAULT_PAIRED_TRAIN_SPLIT = REPO_ROOT / "data" / "processed" / "splits" / "primary_paired_breast_split_train.csv"
DEFAULT_PAIRED_VAL_SPLIT = REPO_ROOT / "data" / "processed" / "splits" / "primary_paired_breast_split_val.csv"
DEFAULT_SINGLE_OUTPUT_DIR = REPO_ROOT / "outputs" / "m1_baseline"
DEFAULT_PAIRED_OUTPUT_DIR = REPO_ROOT / "outputs" / "m2_baseline"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", choices=("single", "paired"), default="single")
    parser.add_argument("--train-split", type=Path, default=None)
    parser.add_argument("--val-split", type=Path, default=None)
    parser.add_argument("--archive-path", type=Path, default=REPO_ROOT / DEFAULT_ARCHIVE_PATH)
    parser.add_argument("--image-root", type=Path, default=None)
    parser.add_argument("--image-size", type=int, default=1024)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--selection-metric", choices=SELECTION_METRIC_CHOICES, default="auto")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    train_split, val_split, requested_output_dir = resolve_runtime_paths(args)
    output_dir, output_redirected = resolve_safe_output_dir(requested_output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    set_random_seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    config = {
        "dataset": args.dataset,
        "train_split": str(train_split),
        "val_split": str(val_split),
        "archive_path": str(args.archive_path),
        "image_root": None if args.image_root is None else str(args.image_root),
        "image_size": args.image_size,
        "batch_size": args.batch_size,
        "epochs": args.epochs,
        "lr": args.lr,
        "seed": args.seed,
        "num_workers": args.num_workers,
        "device": str(device),
        "device_description": describe_device(device),
        "selection_metric": args.selection_metric,
        "output_dir": str(output_dir),
    }

    print("Starting training", flush=True)
    print(f"- dataset: {args.dataset}", flush=True)
    print(f"- device: {describe_device(device)}", flush=True)
    print(f"- train split: {train_split}", flush=True)
    print(f"- val split: {val_split}", flush=True)
    if output_redirected:
        print(f"- requested output dir preserved: {requested_output_dir}", flush=True)
    print(f"- output dir: {output_dir}", flush=True)

    if args.dataset == "single":
        config["model"] = "MinimalSingleImageCNN"
        write_json(output_dir / "config.json", config)
        loader_bundle = build_single_image_loaders(
            train_split_csv_path=train_split,
            val_split_csv_path=val_split,
            archive_path=args.archive_path,
            image_root=args.image_root,
            image_size=args.image_size,
            batch_size=args.batch_size,
            num_workers=args.num_workers,
        )
        try:
            pos_weight = compute_pos_weight(loader_bundle.train_dataset.rows)
            model = MinimalSingleImageCNN(in_channels=3).to(device)
            criterion = nn.BCEWithLogitsLoss(
                pos_weight=torch.tensor(pos_weight, dtype=torch.float32, device=device)
            )
            optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
            fit_result = fit(
                model=model,
                train_loader=loader_bundle.train_loader,
                val_loader=loader_bundle.val_loader,
                optimizer=optimizer,
                criterion=criterion,
                device=device,
                epochs=args.epochs,
                output_dir=output_dir,
                selection_metric=args.selection_metric,
            )
        finally:
            loader_bundle.close()
    else:
        backbone_weights = models.EfficientNet_B2_Weights.DEFAULT
        config["model"] = "PairedEfficientNetB2Baseline"
        config["backbone_weights"] = backbone_weights.name
        write_json(output_dir / "config.json", config)
        loader_bundle = build_paired_breast_loaders(
            train_split_csv_path=train_split,
            val_split_csv_path=val_split,
            archive_path=args.archive_path,
            image_root=args.image_root,
            image_size=args.image_size,
            batch_size=args.batch_size,
            num_workers=args.num_workers,
        )
        try:
            pos_weight = compute_pos_weight(loader_bundle.train_dataset.rows)
            model = PairedEfficientNetB2Baseline(weights=backbone_weights).to(device)
            criterion = nn.BCEWithLogitsLoss(
                pos_weight=torch.tensor(pos_weight, dtype=torch.float32, device=device)
            )
            optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
            fit_result = fit_paired(
                model=model,
                train_loader=loader_bundle.train_loader,
                val_loader=loader_bundle.val_loader,
                optimizer=optimizer,
                criterion=criterion,
                device=device,
                epochs=args.epochs,
                output_dir=output_dir,
                selection_metric=args.selection_metric,
            )
        finally:
            loader_bundle.close()

    metrics_summary = {
        "config": config,
        "train_samples": len(loader_bundle.train_dataset),
        "val_samples": len(loader_bundle.val_dataset),
        "train_unit": "image" if args.dataset == "single" else "breast",
        "pos_weight": pos_weight,
        "primary_selection_metric": fit_result["primary_selection_metric"],
        "selection_mode": fit_result["selection_mode"],
        "best_epoch": fit_result["best_epoch"],
        "best_metric_name": fit_result["best_metric_name"],
        "best_metric_value": fit_result["best_metric_value"],
        "fallback_used": fit_result["fallback_used"],
        "fallback_reason": fit_result["fallback_reason"],
        "best_metrics": fit_result["best_metrics"],
        "history": fit_result["history"],
        "best_checkpoint_path": str(fit_result["best_checkpoint_path"]),
    }
    write_json(output_dir / "metrics_summary.json", metrics_summary)

    print("Training finished successfully")
    print(f"- dataset: {args.dataset}", flush=True)
    print(f"- device: {describe_device(device)}", flush=True)
    print(f"- primary selection metric: {fit_result['primary_selection_metric']}", flush=True)
    print(f"- best epoch: {fit_result['best_epoch']}", flush=True)
    print(
        f"- best metric: {fit_result['best_metric_name']}={format_metric_value(fit_result['best_metric_value'])}",
        flush=True,
    )
    print(f"- fallback used: {fit_result['fallback_used']}", flush=True)
    print(f"- fallback reason: {fit_result['fallback_reason'] or 'None'}", flush=True)
    print(f"- wrote: {output_dir / 'config.json'}", flush=True)
    print(f"- wrote: {output_dir / 'metrics_summary.json'}", flush=True)
    print(f"- wrote: {fit_result['best_checkpoint_path']}", flush=True)
    return 0


def resolve_runtime_paths(args: argparse.Namespace) -> tuple[Path, Path, Path]:
    if args.dataset == "single":
        train_split = args.train_split or DEFAULT_SINGLE_TRAIN_SPLIT
        val_split = args.val_split or DEFAULT_SINGLE_VAL_SPLIT
        output_dir = args.output_dir or DEFAULT_SINGLE_OUTPUT_DIR
        return train_split, val_split, output_dir

    train_split = args.train_split or DEFAULT_PAIRED_TRAIN_SPLIT
    val_split = args.val_split or DEFAULT_PAIRED_VAL_SPLIT
    output_dir = args.output_dir or DEFAULT_PAIRED_OUTPUT_DIR
    return train_split, val_split, output_dir


def resolve_safe_output_dir(requested_output_dir: Path) -> tuple[Path, bool]:
    if requested_output_dir.exists() and requested_output_dir.is_file():
        raise ValueError(f"Requested output dir '{requested_output_dir}' is a file, not a directory.")
    if not requested_output_dir.exists():
        return requested_output_dir, False
    if not any(requested_output_dir.iterdir()):
        return requested_output_dir, False

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    candidate = requested_output_dir.parent / f"{requested_output_dir.name}_{timestamp}"
    suffix = 1
    while candidate.exists():
        candidate = requested_output_dir.parent / f"{requested_output_dir.name}_{timestamp}_{suffix:02d}"
        suffix += 1
    return candidate, True


def describe_device(device: torch.device) -> str:
    if device.type == "cuda":
        device_index = 0 if device.index is None else device.index
        device_name = torch.cuda.get_device_name(device_index)
        return f"gpu (cuda:{device_index}, {device_name})"
    return device.type


def write_json(path: Path, payload: dict[str, object]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def format_metric_value(value: float | None) -> str:
    if value is None:
        return "None"
    return f"{value:.4f}"


if __name__ == "__main__":
    raise SystemExit(main())
