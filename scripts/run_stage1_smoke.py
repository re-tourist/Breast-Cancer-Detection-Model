"""Run one Stage 1 end-to-end smoke test and record sanity findings."""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TRAIN_SPLIT = REPO_ROOT / "data" / "processed" / "splits" / "primary_single_image_split_train.csv"
DEFAULT_VAL_SPLIT = REPO_ROOT / "data" / "processed" / "splits" / "primary_single_image_split_val.csv"
DEFAULT_ARCHIVE_PATH = REPO_ROOT / "data" / "raw" / "primary" / "train_img.zip"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "outputs" / "m1_smoke"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-split", type=Path, default=DEFAULT_TRAIN_SPLIT)
    parser.add_argument("--val-split", type=Path, default=DEFAULT_VAL_SPLIT)
    parser.add_argument("--archive-path", type=Path, default=DEFAULT_ARCHIVE_PATH)
    parser.add_argument("--image-root", type=Path, default=None)
    parser.add_argument("--image-size", type=int, default=512)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--selection-metric", type=str, default="auto")
    parser.add_argument("--aggregation", type=str, default="mean")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir
    train_output_dir = output_dir / "train"
    eval_output_dir = output_dir / "eval"
    report_path = output_dir / "stage1_smoke_report.md"
    output_dir.mkdir(parents=True, exist_ok=True)

    train_command = build_train_command(args, train_output_dir)
    train_result = run_and_log(
        command=train_command,
        stdout_path=output_dir / "train_stdout.log",
        stderr_path=output_dir / "train_stderr.log",
    )
    if train_result.returncode != 0:
        print("Smoke test failed during training.", file=sys.stderr)
        print(f"- train stdout: {output_dir / 'train_stdout.log'}", file=sys.stderr)
        print(f"- train stderr: {output_dir / 'train_stderr.log'}", file=sys.stderr)
        return train_result.returncode

    eval_command = build_eval_command(args, train_output_dir / "best_model.pt", eval_output_dir)
    eval_result = run_and_log(
        command=eval_command,
        stdout_path=output_dir / "eval_stdout.log",
        stderr_path=output_dir / "eval_stderr.log",
    )
    if eval_result.returncode != 0:
        print("Smoke test failed during evaluation.", file=sys.stderr)
        print(f"- eval stdout: {output_dir / 'eval_stdout.log'}", file=sys.stderr)
        print(f"- eval stderr: {output_dir / 'eval_stderr.log'}", file=sys.stderr)
        return eval_result.returncode

    train_config = read_json(train_output_dir / "config.json")
    train_metrics = read_json(train_output_dir / "metrics_summary.json")
    eval_metrics = read_json(eval_output_dir / "breast_level_metrics.json")
    image_prediction_rows = read_csv_rows(eval_output_dir / "image_level_predictions.csv")
    breast_prediction_rows = read_csv_rows(eval_output_dir / "breast_level_predictions.csv")

    split_context = resolve_split_context(args.train_split, args.val_split)
    val_image_label_counts = count_split_image_labels(args.val_split)
    val_breast_label_counts = count_split_breast_labels(args.val_split)
    image_prediction_stats = summarize_predictions(image_prediction_rows)
    breast_prediction_stats = summarize_predictions(breast_prediction_rows)
    report = build_report(
        args=args,
        train_output_dir=train_output_dir,
        eval_output_dir=eval_output_dir,
        train_config=train_config,
        train_metrics=train_metrics,
        eval_metrics=eval_metrics,
        val_image_label_counts=val_image_label_counts,
        val_breast_label_counts=val_breast_label_counts,
        image_prediction_stats=image_prediction_stats,
        breast_prediction_stats=breast_prediction_stats,
        split_context=split_context,
    )
    report_path.write_text(report, encoding="utf-8")

    print("Stage 1 smoke test finished successfully")
    print(f"- output dir: {output_dir}")
    print(f"- report: {report_path}")
    print(f"- train metrics: {train_output_dir / 'metrics_summary.json'}")
    print(f"- eval metrics: {eval_output_dir / 'breast_level_metrics.json'}")
    print(f"- breast auroc: {format_metric_value(eval_metrics['breast_auroc'])}")
    print(f"- collapse suspected: {breast_prediction_stats['collapse_suspected']}")
    return 0


def build_train_command(args: argparse.Namespace, train_output_dir: Path) -> list[str]:
    command = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "train_baseline.py"),
        "--train-split",
        str(args.train_split),
        "--val-split",
        str(args.val_split),
        "--archive-path",
        str(args.archive_path),
        "--image-size",
        str(args.image_size),
        "--batch-size",
        str(args.batch_size),
        "--epochs",
        str(args.epochs),
        "--lr",
        str(args.lr),
        "--seed",
        str(args.seed),
        "--num-workers",
        str(args.num_workers),
        "--selection-metric",
        str(args.selection_metric),
        "--output-dir",
        str(train_output_dir),
    ]
    if args.image_root is not None:
        command.extend(["--image-root", str(args.image_root)])
    return command


def build_eval_command(args: argparse.Namespace, checkpoint_path: Path, eval_output_dir: Path) -> list[str]:
    command = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "run_eval.py"),
        "--checkpoint",
        str(checkpoint_path),
        "--val-split",
        str(args.val_split),
        "--archive-path",
        str(args.archive_path),
        "--image-size",
        str(args.image_size),
        "--batch-size",
        str(args.batch_size),
        "--num-workers",
        str(args.num_workers),
        "--aggregation",
        str(args.aggregation),
        "--output-dir",
        str(eval_output_dir),
    ]
    if args.image_root is not None:
        command.extend(["--image-root", str(args.image_root)])
    return command


def run_and_log(command: list[str], stdout_path: Path, stderr_path: Path) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    stdout_path.write_text(completed.stdout, encoding="utf-8")
    stderr_path.write_text(completed.stderr, encoding="utf-8")
    return completed


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def count_split_image_labels(path: Path) -> dict[str, int]:
    rows = read_csv_rows(path)
    return {
        str(label): count
        for label, count in sorted(Counter(int(row["is_malignant"]) for row in rows).items())
    }


def count_split_breast_labels(path: Path) -> dict[str, int]:
    rows = read_csv_rows(path)
    grouped_targets: dict[str, int] = {}
    for row in rows:
        breast_id = str(row["breast_id"])
        target = int(row["is_malignant"])
        if breast_id in grouped_targets and grouped_targets[breast_id] != target:
            raise ValueError(f"Inconsistent targets found in split CSV for breast_id '{breast_id}'.")
        grouped_targets[breast_id] = target
    return {
        str(label): count
        for label, count in sorted(Counter(grouped_targets.values()).items())
    }


def summarize_predictions(rows: list[dict[str, str]]) -> dict[str, Any]:
    predictions = [float(row["prediction"]) for row in rows]
    if not predictions:
        return {
            "count": 0,
            "min": None,
            "max": None,
            "mean": None,
            "std": None,
            "range": None,
            "collapse_suspected": True,
        }

    prediction_min = min(predictions)
    prediction_max = max(predictions)
    prediction_std = statistics.pstdev(predictions) if len(predictions) > 1 else 0.0
    prediction_range = prediction_max - prediction_min
    collapse_suspected = prediction_std < 0.02 or prediction_range < 0.05
    return {
        "count": len(predictions),
        "min": prediction_min,
        "max": prediction_max,
        "mean": float(sum(predictions) / len(predictions)),
        "std": prediction_std,
        "range": prediction_range,
        "collapse_suspected": collapse_suspected,
    }


def resolve_split_context(train_split: Path, val_split: Path) -> dict[str, Any]:
    split_summary_path = val_split.parent / "primary_split_summary.json"
    if not split_summary_path.exists():
        return {
            "summary_path": None,
            "val_fold": None,
            "train_folds": [],
            "paired_val_label_counts": None,
            "single_val_label_counts": None,
        }

    split_summary = read_json(split_summary_path)
    fold_assignment = split_summary.get("fold_assignment", {})
    paired = split_summary.get("paired", {})
    single = split_summary.get("single", {})
    return {
        "summary_path": str(split_summary_path),
        "val_fold": fold_assignment.get("val_fold"),
        "train_folds": fold_assignment.get("train_folds", []),
        "paired_val_label_counts": paired.get("val", {}).get("label_counts"),
        "single_val_label_counts": single.get("val", {}).get("label_counts"),
    }


def build_report(
    args: argparse.Namespace,
    train_output_dir: Path,
    eval_output_dir: Path,
    train_config: dict[str, Any],
    train_metrics: dict[str, Any],
    eval_metrics: dict[str, Any],
    val_image_label_counts: dict[str, int],
    val_breast_label_counts: dict[str, int],
    image_prediction_stats: dict[str, Any],
    breast_prediction_stats: dict[str, Any],
    split_context: dict[str, Any],
) -> str:
    best_metrics = train_metrics["best_metrics"]
    label_alignment_ok = val_breast_label_counts == eval_metrics["label_counts"]
    finite_losses = all(
        value == value and value not in (float("inf"), float("-inf"))
        for value in [best_metrics["train_loss"], best_metrics["val_loss"]]
    )
    loss_observation = (
        "Loss computed successfully and remained finite."
        if finite_losses
        else "Loss shows NaN/inf or another numerical issue."
    )
    label_observation = (
        "Breast-level label counts from the validation split match the evaluation output, so labels look structurally aligned."
        if label_alignment_ok
        else "Breast-level label counts from the validation split do not match the evaluation output; labels need inspection."
    )
    collapse_observation = (
        "Breast-level predictions are tightly clustered, so there is a clear near-constant output / collapse risk."
        if breast_prediction_stats["collapse_suspected"]
        else "Prediction spread is not collapsed by the current heuristic."
    )
    eval_observation = (
        f"Breast-level AUROC was computed successfully: {format_metric_value(eval_metrics['breast_auroc'])}."
        if eval_metrics["auroc_available"]
        else f"Breast-level AUROC was not available: {eval_metrics['auroc_reason']}"
    )
    overall_observation = "This run should be treated as a runnable pipeline sanity check, not as evidence of a strong baseline."
    conclusion = "The end-to-end M1 loop is established: data loading, training, validation, and breast-level evaluation all completed successfully."
    main_limitation = "The current baseline still shows near-constant breast-level predictions, so model quality is not yet reliable."
    next_risk = "The main risk before M2 is carrying a structurally correct but weak single-image baseline forward without addressing output collapse and the gap to the breast-level main task."

    return f"""# Stage 1 Smoke Report

## Minimal Configuration
- Train split: `{args.train_split}`
- Val split: `{args.val_split}`
- Split summary: `{split_context['summary_path']}`
- Val fold: `{split_context['val_fold']}`
- Train folds: `{split_context['train_folds']}`
- Epochs: `{args.epochs}`
- Batch size: `{args.batch_size}`
- Image size: `{args.image_size}`
- Device: `{train_config['device']}`
- Selection metric: `{train_config['selection_metric']}`
- Aggregation: `{args.aggregation}`
- Train output dir: `{train_output_dir}`
- Eval output dir: `{eval_output_dir}`
- Checkpoint: `{train_output_dir / 'best_model.pt'}`

## Pipeline Coverage
- Data loading: passed
- Training: passed
- Validation: passed
- Breast-level aggregation evaluation: passed

## Key Artifact Paths
- Train config: `{train_output_dir / 'config.json'}`
- Train metrics summary: `{train_output_dir / 'metrics_summary.json'}`
- Best checkpoint: `{train_output_dir / 'best_model.pt'}`
- Image-level predictions: `{eval_output_dir / 'image_level_predictions.csv'}`
- Breast-level predictions: `{eval_output_dir / 'breast_level_predictions.csv'}`
- Breast-level metrics: `{eval_output_dir / 'breast_level_metrics.json'}`
- Train stdout log: `{args.output_dir / 'train_stdout.log'}`
- Train stderr log: `{args.output_dir / 'train_stderr.log'}`
- Eval stdout log: `{args.output_dir / 'eval_stdout.log'}`
- Eval stderr log: `{args.output_dir / 'eval_stderr.log'}`

## Key Observations
- Validation split image labels: `{val_image_label_counts}`
- Validation split breast labels: `{val_breast_label_counts}`
- Evaluation breast labels: `{eval_metrics['label_counts']}`
- Label alignment: {label_observation}
- Loss behavior: {loss_observation}
- Image prediction spread: count=`{image_prediction_stats['count']}`, min=`{format_metric_value(image_prediction_stats['min'])}`, max=`{format_metric_value(image_prediction_stats['max'])}`, std=`{format_metric_value(image_prediction_stats['std'])}`
- Breast prediction spread: count=`{breast_prediction_stats['count']}`, min=`{format_metric_value(breast_prediction_stats['min'])}`, max=`{format_metric_value(breast_prediction_stats['max'])}`, std=`{format_metric_value(breast_prediction_stats['std'])}`
- Output collapse check: {collapse_observation}
- Evaluation result: {eval_observation}
- Overall reading: {overall_observation}

## Sanity Conclusion
- Current loop status: {conclusion}
- Main limitation: {main_limitation}
- Main M2 risk: {next_risk}
"""


def format_metric_value(value: float | None) -> str:
    if value is None:
        return "None"
    return f"{value:.4f}"


if __name__ == "__main__":
    raise SystemExit(main())
