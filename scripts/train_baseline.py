"""Train the minimal single-image Stage 1 baseline on reusable split artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import torch
from torch import nn


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.data.datasets import DEFAULT_ARCHIVE_PATH  # noqa: E402
from src.models.baseline import MinimalSingleImageCNN  # noqa: E402
from src.train.trainer import (  # noqa: E402
    build_single_image_loaders,
    compute_pos_weight,
    fit,
    set_random_seed,
)


DEFAULT_TRAIN_SPLIT = REPO_ROOT / "data" / "processed" / "splits" / "primary_single_image_split_train.csv"
DEFAULT_VAL_SPLIT = REPO_ROOT / "data" / "processed" / "splits" / "primary_single_image_split_val.csv"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "outputs" / "m1_baseline"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-split", type=Path, default=DEFAULT_TRAIN_SPLIT)
    parser.add_argument("--val-split", type=Path, default=DEFAULT_VAL_SPLIT)
    parser.add_argument("--archive-path", type=Path, default=REPO_ROOT / DEFAULT_ARCHIVE_PATH)
    parser.add_argument("--image-root", type=Path, default=None)
    parser.add_argument("--image-size", type=int, default=1024)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    set_random_seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    config = {
        "train_split": str(args.train_split),
        "val_split": str(args.val_split),
        "archive_path": str(args.archive_path),
        "image_root": None if args.image_root is None else str(args.image_root),
        "image_size": args.image_size,
        "batch_size": args.batch_size,
        "epochs": args.epochs,
        "lr": args.lr,
        "seed": args.seed,
        "num_workers": args.num_workers,
        "device": str(device),
        "model": "MinimalSingleImageCNN",
    }
    write_json(output_dir / "config.json", config)

    loader_bundle = build_single_image_loaders(
        train_split_csv_path=args.train_split,
        val_split_csv_path=args.val_split,
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
        )
    finally:
        loader_bundle.close()

    metrics_summary = {
        "config": config,
        "train_samples": len(loader_bundle.train_dataset),
        "val_samples": len(loader_bundle.val_dataset),
        "pos_weight": pos_weight,
        "best_epoch": fit_result["best_epoch"],
        "best_metrics": fit_result["best_metrics"],
        "history": fit_result["history"],
        "best_checkpoint_path": str(fit_result["best_checkpoint_path"]),
    }
    write_json(output_dir / "metrics_summary.json", metrics_summary)

    print("Training finished successfully")
    print(f"- best epoch: {fit_result['best_epoch']}")
    print(f"- best val loss: {fit_result['best_metrics']['val_loss']:.4f}")
    print(f"- wrote: {output_dir / 'config.json'}")
    print(f"- wrote: {output_dir / 'metrics_summary.json'}")
    print(f"- wrote: {fit_result['best_checkpoint_path']}")
    return 0


def write_json(path: Path, payload: dict[str, object]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


if __name__ == "__main__":
    raise SystemExit(main())
