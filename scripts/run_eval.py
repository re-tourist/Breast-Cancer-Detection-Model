"""Run minimal breast-level evaluation from a validation split and checkpoint."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import torch
from torch.utils.data import DataLoader


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.data.datasets import (  # noqa: E402
    DEFAULT_ARCHIVE_PATH,
    PairedBreastDataset,
    SingleImageDataset,
)
from src.data.transforms import build_eval_transform  # noqa: E402
from src.eval import (  # noqa: E402
    AGGREGATION_CHOICES,
    PAIRED_BREAST_LEVEL_PREDICTION_FIELDS,
    collect_paired_breast_prediction_rows,
    collect_single_image_prediction_rows,
    evaluate_breast_prediction_rows,
    evaluate_prediction_rows,
    write_evaluation_artifacts,
)
from src.models.baseline import MinimalSingleImageCNN, PairedEfficientNetB2Baseline  # noqa: E402


DEFAULT_SINGLE_CHECKPOINT_PATH = REPO_ROOT / "outputs" / "m1_baseline" / "best_model.pt"
DEFAULT_SINGLE_VAL_SPLIT = REPO_ROOT / "data" / "processed" / "splits" / "primary_single_image_split_val.csv"
DEFAULT_SINGLE_OUTPUT_DIR = REPO_ROOT / "outputs" / "m1_baseline" / "eval"
DEFAULT_PAIRED_CHECKPOINT_PATH = REPO_ROOT / "outputs" / "m2_baseline" / "best_model.pt"
DEFAULT_PAIRED_VAL_SPLIT = REPO_ROOT / "data" / "processed" / "splits" / "primary_paired_breast_split_val.csv"
DEFAULT_PAIRED_OUTPUT_DIR = REPO_ROOT / "outputs" / "m2_baseline" / "eval"
PAIRED_AGGREGATION_LABEL = "paired_direct"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", choices=("single", "paired"), default="single")
    parser.add_argument("--checkpoint", type=Path, default=None)
    parser.add_argument("--val-split", type=Path, default=None)
    parser.add_argument("--archive-path", type=Path, default=REPO_ROOT / DEFAULT_ARCHIVE_PATH)
    parser.add_argument("--image-root", type=Path, default=None)
    parser.add_argument("--image-size", type=int, default=1024)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--aggregation", choices=AGGREGATION_CHOICES, default="mean")
    parser.add_argument("--output-dir", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    checkpoint_path, val_split_path, output_dir = resolve_runtime_paths(args)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    if args.dataset == "single":
        evaluation_result, output_paths = run_single_evaluation(
            checkpoint_path=checkpoint_path,
            val_split_path=val_split_path,
            archive_path=args.archive_path,
            image_root=args.image_root,
            image_size=args.image_size,
            batch_size=args.batch_size,
            num_workers=args.num_workers,
            aggregation=args.aggregation,
            output_dir=output_dir,
            device=device,
        )
        print("Evaluation finished successfully")
        print(f"- dataset: {args.dataset}")
        print(f"- checkpoint: {checkpoint_path}")
        print(f"- aggregation: {args.aggregation}")
        print(f"- image predictions: {len(evaluation_result['image_prediction_rows'])}")
        print(f"- breast predictions: {len(evaluation_result['breast_prediction_rows'])}")
        print(f"- breast auroc: {format_metric_value(evaluation_result['metrics']['breast_auroc'])}")
        print(f"- auroc available: {evaluation_result['metrics']['auroc_available']}")
        print(f"- wrote: {output_paths['image_predictions']}")
        print(f"- wrote: {output_paths['breast_predictions']}")
        print(f"- wrote: {output_paths['metrics']}")
        return 0

    evaluation_result, output_paths = run_paired_evaluation(
        checkpoint_path=checkpoint_path,
        val_split_path=val_split_path,
        archive_path=args.archive_path,
        image_root=args.image_root,
        image_size=args.image_size,
        batch_size=args.batch_size,
        num_workers=args.num_workers,
        output_dir=output_dir,
        device=device,
    )
    print("Evaluation finished successfully")
    print(f"- dataset: {args.dataset}")
    print(f"- checkpoint: {checkpoint_path}")
    print(f"- aggregation: {PAIRED_AGGREGATION_LABEL}")
    print(f"- breast predictions: {len(evaluation_result['breast_prediction_rows'])}")
    print(f"- breast auroc: {format_metric_value(evaluation_result['metrics']['breast_auroc'])}")
    print(f"- auroc available: {evaluation_result['metrics']['auroc_available']}")
    print("- image predictions: not generated for paired evaluation")
    print(f"- wrote: {output_paths['breast_predictions']}")
    print(f"- wrote: {output_paths['metrics']}")
    return 0


def resolve_runtime_paths(args: argparse.Namespace) -> tuple[Path, Path, Path]:
    if args.dataset == "single":
        checkpoint_path = args.checkpoint or DEFAULT_SINGLE_CHECKPOINT_PATH
        val_split_path = args.val_split or DEFAULT_SINGLE_VAL_SPLIT
        output_dir = args.output_dir or DEFAULT_SINGLE_OUTPUT_DIR
        return checkpoint_path, val_split_path, output_dir

    checkpoint_path = args.checkpoint or DEFAULT_PAIRED_CHECKPOINT_PATH
    val_split_path = args.val_split or DEFAULT_PAIRED_VAL_SPLIT
    output_dir = args.output_dir or DEFAULT_PAIRED_OUTPUT_DIR
    return checkpoint_path, val_split_path, output_dir


def run_single_evaluation(
    checkpoint_path: Path,
    val_split_path: Path,
    archive_path: Path,
    image_root: Path | None,
    image_size: int,
    batch_size: int,
    num_workers: int,
    aggregation: str,
    output_dir: Path,
    device: torch.device,
) -> tuple[dict[str, object], dict[str, Path | None]]:
    dataset = SingleImageDataset(
        index_csv_path=val_split_path,
        archive_path=archive_path,
        transform=build_eval_transform(image_size=image_size, num_channels=3),
        image_root=image_root,
    )
    loader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
    )

    try:
        model = MinimalSingleImageCNN(in_channels=3).to(device)
        state_dict = torch.load(checkpoint_path, map_location=device)
        model.load_state_dict(state_dict)

        image_prediction_rows = collect_single_image_prediction_rows(
            model=model,
            loader=loader,
            device=device,
        )
        evaluation_result = evaluate_prediction_rows(
            prediction_rows=image_prediction_rows,
            aggregation=aggregation,
            item_id_field="image_id",
        )
        output_paths = write_evaluation_artifacts(
            output_dir=output_dir,
            image_prediction_rows=evaluation_result["image_prediction_rows"],
            breast_prediction_rows=evaluation_result["breast_prediction_rows"],
            metrics=evaluation_result["metrics"],
        )
    finally:
        dataset.close()

    return evaluation_result, output_paths


def run_paired_evaluation(
    checkpoint_path: Path,
    val_split_path: Path,
    archive_path: Path,
    image_root: Path | None,
    image_size: int,
    batch_size: int,
    num_workers: int,
    output_dir: Path,
    device: torch.device,
) -> tuple[dict[str, object], dict[str, Path | None]]:
    dataset = PairedBreastDataset(
        index_csv_path=val_split_path,
        archive_path=archive_path,
        transform=build_eval_transform(image_size=image_size, num_channels=3),
        image_root=image_root,
    )
    loader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
    )

    try:
        model = PairedEfficientNetB2Baseline(weights=None).to(device)
        state_dict = torch.load(checkpoint_path, map_location=device)
        model.load_state_dict(state_dict)

        breast_prediction_rows = collect_paired_breast_prediction_rows(
            model=model,
            loader=loader,
            device=device,
        )
        evaluation_result = evaluate_breast_prediction_rows(
            breast_prediction_rows=breast_prediction_rows,
            aggregation=PAIRED_AGGREGATION_LABEL,
        )
        output_paths = write_evaluation_artifacts(
            output_dir=output_dir,
            image_prediction_rows=None,
            breast_prediction_rows=evaluation_result["breast_prediction_rows"],
            metrics=evaluation_result["metrics"],
            breast_prediction_fieldnames=PAIRED_BREAST_LEVEL_PREDICTION_FIELDS,
        )
    finally:
        dataset.close()

    return evaluation_result, output_paths


def format_metric_value(value: float | None) -> str:
    if value is None:
        return "None"
    return f"{value:.4f}"


if __name__ == "__main__":
    raise SystemExit(main())
