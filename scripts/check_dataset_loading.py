"""Smoke-test dataset loading and optionally save preprocessing previews."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from torch.utils.data import DataLoader


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.data import (  # noqa: E402
    DEFAULT_ARCHIVE_PATH,
    DEFAULT_PAIRED_INDEX_PATH,
    DEFAULT_SINGLE_INDEX_PATH,
    PairedBreastDataset,
    SingleImageDataset,
    build_eval_transform,
    build_train_transform,
)


DEFAULT_PREVIEW_DIR = REPO_ROOT / "outputs" / "dataset_loading_preview"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", choices=("single", "paired"), default="single")
    parser.add_argument("--mode", choices=("train", "eval"), default="eval")
    parser.add_argument("--single-index", type=Path, default=REPO_ROOT / DEFAULT_SINGLE_INDEX_PATH)
    parser.add_argument("--paired-index", type=Path, default=REPO_ROOT / DEFAULT_PAIRED_INDEX_PATH)
    parser.add_argument("--archive-path", type=Path, default=REPO_ROOT / DEFAULT_ARCHIVE_PATH)
    parser.add_argument("--image-root", type=Path, default=None)
    parser.add_argument("--image-size", type=int, default=1024)
    parser.add_argument("--num-channels", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--num-batches", type=int, default=1)
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--save-preview", action="store_true")
    parser.add_argument("--preview-dir", type=Path, default=DEFAULT_PREVIEW_DIR)
    return parser.parse_args()


def build_dataset(args: argparse.Namespace):
    if args.mode == "train":
        transform = build_train_transform(
            image_size=args.image_size,
            num_channels=args.num_channels,
            enable_augmentation=False,
        )
    else:
        transform = build_eval_transform(
            image_size=args.image_size,
            num_channels=args.num_channels,
        )

    if args.dataset == "single":
        dataset = SingleImageDataset(
            index_csv_path=args.single_index,
            archive_path=args.archive_path,
            transform=transform,
            image_root=args.image_root,
        )
    else:
        dataset = PairedBreastDataset(
            index_csv_path=args.paired_index,
            archive_path=args.archive_path,
            transform=transform,
            image_root=args.image_root,
        )
    return dataset


def tensor_summary(name: str, tensor: torch.Tensor) -> str:
    return (
        f"{name}: shape={tuple(tensor.shape)} dtype={tensor.dtype} "
        f"min={tensor.min().item():.4f} max={tensor.max().item():.4f}"
    )


def save_preview(batch: dict[str, object], dataset_type: str, output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    saved_paths: list[Path] = []

    if dataset_type == "single":
        images = batch["image"]
        image_ids = batch["image_id"]
        for index in range(min(4, len(image_ids))):
            path = output_dir / f"single_{index}_{image_ids[index]}.png"
            image = tensor_to_image(images[index])
            image.save(path)
            saved_paths.append(path)
    else:
        x_cc = batch["x_cc"]
        x_mlo = batch["x_mlo"]
        breast_ids = batch["breast_id"]
        for index in range(min(4, len(breast_ids))):
            cc_image = tensor_to_image(x_cc[index])
            mlo_image = tensor_to_image(x_mlo[index])
            merged = Image.new("L", (cc_image.width + mlo_image.width, cc_image.height))
            merged.paste(cc_image, (0, 0))
            merged.paste(mlo_image, (cc_image.width, 0))
            path = output_dir / f"paired_{index}_{breast_ids[index]}.png"
            merged.save(path)
            saved_paths.append(path)

    return saved_paths


def tensor_to_image(tensor: torch.Tensor) -> Image.Image:
    array = tensor[0].detach().cpu().clamp(0, 1).mul(255).to(torch.uint8).numpy()
    return Image.fromarray(np.asarray(array))


def print_batch_summary(batch: dict[str, object], dataset_type: str) -> None:
    print(f"- keys: {list(batch.keys())}")
    if dataset_type == "single":
        print(f"- {tensor_summary('image', batch['image'])}")
        print(f"- {tensor_summary('target', batch['target'])}")
        print(f"- image_id sample: {batch['image_id'][:2]}")
        print(f"- breast_id sample: {batch['breast_id'][:2]}")
        print(f"- image_path sample: {batch['image_path'][:2]}")
    else:
        print(f"- {tensor_summary('x_cc', batch['x_cc'])}")
        print(f"- {tensor_summary('x_mlo', batch['x_mlo'])}")
        print(f"- {tensor_summary('target', batch['target'])}")
        print(f"- breast_id sample: {batch['breast_id'][:2]}")
        print(f"- image_path_cc sample: {batch['image_path_cc'][:2]}")
        print(f"- image_path_mlo sample: {batch['image_path_mlo'][:2]}")


def main() -> int:
    args = parse_args()
    dataset = build_dataset(args)
    print(f"Dataset: {args.dataset}")
    print(f"Mode: {args.mode}")
    print(f"Length: {len(dataset)}")

    loader = DataLoader(
        dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
    )

    saved_paths: list[Path] = []
    try:
        for batch_index, batch in enumerate(loader):
            if batch_index >= args.num_batches:
                break
            print(f"Batch {batch_index}")
            print_batch_summary(batch, args.dataset)
            if args.save_preview and not saved_paths:
                saved_paths = save_preview(batch, args.dataset, args.preview_dir)
    finally:
        dataset.close()

    if saved_paths:
        print(f"- saved preview files: {[str(path) for path in saved_paths]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

