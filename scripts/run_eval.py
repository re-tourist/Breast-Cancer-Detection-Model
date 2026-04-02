"""Run minimal breast-level evaluation from a validation split and checkpoint."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
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
EVAL_CONFIG_FILENAME = "eval_config.json"


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
    checkpoint_path, val_split_path, requested_output_dir = resolve_runtime_paths(args)
    output_dir, output_redirected = resolve_safe_output_dir(requested_output_dir)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    ensure_checkpoint_exists(checkpoint_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    eval_config_path = output_dir / EVAL_CONFIG_FILENAME
    write_json(
        eval_config_path,
        build_eval_config(
            args=args,
            checkpoint_path=checkpoint_path,
            val_split_path=val_split_path,
            output_dir=output_dir,
            device=device,
        ),
    )

    print("Starting evaluation", flush=True)
    print(f"- dataset: {args.dataset}", flush=True)
    print(f"- device: {describe_device(device)}", flush=True)
    print(f"- checkpoint: {checkpoint_path}", flush=True)
    print(f"- val split: {val_split_path}", flush=True)
    if output_redirected:
        print(f"- requested output dir preserved: {requested_output_dir}", flush=True)
    print(f"- output dir: {output_dir}", flush=True)

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
        print(f"- wrote: {eval_config_path}")
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
    print(f"- wrote: {eval_config_path}")
    print(f"- wrote: {output_paths['breast_predictions']}")
    print(f"- wrote: {output_paths['metrics']}")
    return 0


def resolve_runtime_paths(args: argparse.Namespace) -> tuple[Path, Path, Path]:
    if args.dataset == "single":
        checkpoint_path = args.checkpoint or DEFAULT_SINGLE_CHECKPOINT_PATH
        val_split_path = args.val_split or DEFAULT_SINGLE_VAL_SPLIT
        output_dir = args.output_dir or derive_default_output_dir(
            checkpoint_path=checkpoint_path,
            fallback_output_dir=DEFAULT_SINGLE_OUTPUT_DIR,
            user_provided_checkpoint=args.checkpoint is not None,
        )
        return checkpoint_path, val_split_path, output_dir

    checkpoint_path = args.checkpoint or DEFAULT_PAIRED_CHECKPOINT_PATH
    val_split_path = args.val_split or DEFAULT_PAIRED_VAL_SPLIT
    output_dir = args.output_dir or derive_default_output_dir(
        checkpoint_path=checkpoint_path,
        fallback_output_dir=DEFAULT_PAIRED_OUTPUT_DIR,
        user_provided_checkpoint=args.checkpoint is not None,
    )
    return checkpoint_path, val_split_path, output_dir


def derive_default_output_dir(
    checkpoint_path: Path,
    fallback_output_dir: Path,
    user_provided_checkpoint: bool,
) -> Path:
    if not user_provided_checkpoint:
        return fallback_output_dir
    return checkpoint_path.parent / "eval"


def build_eval_config(
    args: argparse.Namespace,
    checkpoint_path: Path,
    val_split_path: Path,
    output_dir: Path,
    device: torch.device,
) -> dict[str, object]:
    return {
        "dataset": args.dataset,
        "checkpoint": str(checkpoint_path),
        "val_split": str(val_split_path),
        "archive_path": str(args.archive_path),
        "image_root": None if args.image_root is None else str(args.image_root),
        "image_size": args.image_size,
        "batch_size": args.batch_size,
        "num_workers": args.num_workers,
        "aggregation": args.aggregation if args.dataset == "single" else PAIRED_AGGREGATION_LABEL,
        "device": str(device),
        "device_description": describe_device(device),
        "output_dir": str(output_dir),
        "requested_output_dir": None if args.output_dir is None else str(args.output_dir),
    }


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


def ensure_checkpoint_exists(checkpoint_path: Path) -> None:
    if checkpoint_path.exists() and checkpoint_path.is_file():
        return
    raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")


def describe_device(device: torch.device) -> str:
    if device.type == "cuda":
        device_index = 0 if device.index is None else device.index
        device_name = torch.cuda.get_device_name(device_index)
        return f"gpu (cuda:{device_index}, {device_name})"
    return device.type


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


def write_json(path: Path, payload: dict[str, object]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


if __name__ == "__main__":
    raise SystemExit(main())
