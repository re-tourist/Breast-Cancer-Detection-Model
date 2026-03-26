"""Build reusable breast_id-grouped train/val split artifacts for Stage 1."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.data import (  # noqa: E402
    DEFAULT_PAIRED_INDEX_PATH,
    DEFAULT_SINGLE_INDEX_PATH,
    build_train_val_split,
    build_split_summary,
    write_split_artifacts,
)
from src.data.splits import (  # noqa: E402
    DEFAULT_RANDOM_STATE,
    DEFAULT_SPLIT_DIR,
    DEFAULT_VAL_RATIO,
    SplitBuildError,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paired-index", type=Path, default=REPO_ROOT / DEFAULT_PAIRED_INDEX_PATH)
    parser.add_argument("--single-index", type=Path, default=REPO_ROOT / DEFAULT_SINGLE_INDEX_PATH)
    parser.add_argument("--output-dir", type=Path, default=REPO_ROOT / DEFAULT_SPLIT_DIR)
    parser.add_argument("--val-ratio", type=float, default=DEFAULT_VAL_RATIO)
    parser.add_argument("--seed", type=int, default=DEFAULT_RANDOM_STATE)
    parser.add_argument(
        "--disable-stratified",
        action="store_true",
        help="Use plain group shuffle split instead of stratified group holdout.",
    )
    return parser.parse_args()


def format_distribution(distribution: dict[str, int]) -> str:
    return ", ".join(f"{key}={distribution[key]}" for key in sorted(distribution))


def main() -> int:
    args = parse_args()

    try:
        split_result = build_train_val_split(
            paired_index_csv_path=args.paired_index,
            single_index_csv_path=args.single_index,
            val_ratio=args.val_ratio,
            random_state=args.seed,
            stratified=not args.disable_stratified,
        )
    except SplitBuildError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    summary = build_split_summary(split_result)
    output_paths = write_split_artifacts(split_result, output_dir=args.output_dir)

    print("Split artifacts built successfully")
    print(f"- split strategy: {summary['split_strategy']}")
    print(f"- random_state: {summary['random_state']}")
    print(f"- val_ratio: {summary['val_ratio']}")
    print(
        f"- paired train: {summary['paired']['train']['num_breasts']} breasts, "
        f"{summary['paired']['train']['num_rows']} rows, "
        f"labels {format_distribution(summary['paired']['train']['label_counts'])}"
    )
    print(
        f"- paired val: {summary['paired']['val']['num_breasts']} breasts, "
        f"{summary['paired']['val']['num_rows']} rows, "
        f"labels {format_distribution(summary['paired']['val']['label_counts'])}"
    )
    print(
        f"- single train: {summary['single']['train']['num_breasts']} breasts, "
        f"{summary['single']['train']['num_images']} images, "
        f"labels {format_distribution(summary['single']['train']['label_counts'])}"
    )
    print(
        f"- single val: {summary['single']['val']['num_breasts']} breasts, "
        f"{summary['single']['val']['num_images']} images, "
        f"labels {format_distribution(summary['single']['val']['label_counts'])}"
    )
    print(
        "- leakage check: "
        f"overlap_count={summary['checks']['breast_id_leakage']['overlap_count']}"
    )
    print(
        "- fallback: "
        f"used={summary['checks']['strategy_fallback']['used_fallback']} "
        f"reason={summary['checks']['strategy_fallback']['reason']!r}"
    )
    print(f"- wrote: {output_paths['paired_train']}")
    print(f"- wrote: {output_paths['paired_val']}")
    print(f"- wrote: {output_paths['single_train']}")
    print(f"- wrote: {output_paths['single_val']}")
    print(f"- wrote: {output_paths['summary']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
