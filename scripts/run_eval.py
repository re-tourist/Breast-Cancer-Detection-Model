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
    DEFAULT_SINGLE_INDEX_PATH,
    SingleImageDataset,
)
from src.data.transforms import build_eval_transform  # noqa: E402
from src.eval import (  # noqa: E402
    AGGREGATION_CHOICES,
    collect_single_image_prediction_rows,
    evaluate_prediction_rows,
    write_evaluation_artifacts,
)
from src.models.baseline import MinimalSingleImageCNN  # noqa: E402


DEFAULT_CHECKPOINT_PATH = REPO_ROOT / "outputs" / "m1_baseline" / "best_model.pt"
DEFAULT_VAL_SPLIT = REPO_ROOT / "data" / "processed" / "splits" / "primary_single_image_split_val.csv"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "outputs" / "m1_baseline" / "eval"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, default=DEFAULT_CHECKPOINT_PATH)
    parser.add_argument("--val-split", type=Path, default=DEFAULT_VAL_SPLIT)
    parser.add_argument("--archive-path", type=Path, default=REPO_ROOT / DEFAULT_ARCHIVE_PATH)
    parser.add_argument("--image-root", type=Path, default=None)
    parser.add_argument("--image-size", type=int, default=1024)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--aggregation", choices=AGGREGATION_CHOICES, default="mean")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    dataset = SingleImageDataset(
        index_csv_path=args.val_split,
        archive_path=args.archive_path,
        transform=build_eval_transform(image_size=args.image_size, num_channels=3),
        image_root=args.image_root,
    )
    loader = DataLoader(
        dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
    )

    try:
        model = MinimalSingleImageCNN(in_channels=3).to(device)
        state_dict = torch.load(args.checkpoint, map_location=device)
        model.load_state_dict(state_dict)

        image_prediction_rows = collect_single_image_prediction_rows(
            model=model,
            loader=loader,
            device=device,
        )
        evaluation_result = evaluate_prediction_rows(
            prediction_rows=image_prediction_rows,
            aggregation=args.aggregation,
            item_id_field="image_id",
        )
        output_paths = write_evaluation_artifacts(
            output_dir=args.output_dir,
            image_prediction_rows=evaluation_result["image_prediction_rows"],
            breast_prediction_rows=evaluation_result["breast_prediction_rows"],
            metrics=evaluation_result["metrics"],
        )
    finally:
        dataset.close()

    print("Evaluation finished successfully")
    print(f"- checkpoint: {args.checkpoint}")
    print(f"- aggregation: {args.aggregation}")
    print(f"- image predictions: {len(evaluation_result['image_prediction_rows'])}")
    print(f"- breast predictions: {len(evaluation_result['breast_prediction_rows'])}")
    print(f"- breast auroc: {format_metric_value(evaluation_result['metrics']['breast_auroc'])}")
    print(f"- auroc available: {evaluation_result['metrics']['auroc_available']}")
    print(f"- wrote: {output_paths['image_predictions']}")
    print(f"- wrote: {output_paths['breast_predictions']}")
    print(f"- wrote: {output_paths['metrics']}")
    return 0


def format_metric_value(value: float | None) -> str:
    if value is None:
        return "None"
    return f"{value:.4f}"


if __name__ == "__main__":
    raise SystemExit(main())
