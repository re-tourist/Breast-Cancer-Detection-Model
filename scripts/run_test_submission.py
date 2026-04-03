"""Generate a test-set submission CSV from a paired checkpoint."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from zipfile import ZipFile

import torch
from torch.utils.data import DataLoader, Dataset


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.data.datasets import ArchiveImageReader  # noqa: E402
from src.data.transforms import build_eval_transform  # noqa: E402
from src.models.baseline import PairedEfficientNetB2Baseline  # noqa: E402


DEFAULT_CHECKPOINT_PATH = REPO_ROOT / "outputs" / "m2_baseline_bs2_lr1e4" / "best_model.pt"
DEFAULT_TEST_ARCHIVE_PATH = REPO_ROOT / "data" / "raw" / "primary" / "test_img.zip"
DEFAULT_SUBMISSION_TEMPLATE_PATH = REPO_ROOT / "data" / "raw" / "primary" / "name_sid_submission.csv"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "outputs" / "m2_baseline_bs2_lr1e4" / "submission"
SUBMISSION_FILENAME = "name_sid_submission.csv"
SUBMISSION_CONFIG_FILENAME = "submission_config.json"
REQUIRED_TEMPLATE_FIELDS = ("breast_id", "pred_score")


class TestPairedBreastDataset(Dataset[dict[str, object]]):
    """Load strict `(CC, MLO)` test-time paired rows for submission inference."""

    def __init__(
        self,
        rows: list[dict[str, str]],
        archive_path: str | Path,
        transform,
        image_root: str | Path | None = None,
    ) -> None:
        self.rows = rows
        self.transform = transform
        self.image_reader = ArchiveImageReader(archive_path=archive_path, image_root=image_root)

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, index: int) -> dict[str, object]:
        row = self.rows[index]
        laterality = row.get("laterality", "")
        cc_image = self.image_reader.read(row["image_path_cc"])
        mlo_image = self.image_reader.read(row["image_path_mlo"])
        return {
            "x_cc": self.transform(cc_image, laterality=laterality),
            "x_mlo": self.transform(mlo_image, laterality=laterality),
            "breast_id": row["breast_id"],
            "image_id_cc": row["image_id_cc"],
            "image_id_mlo": row["image_id_mlo"],
            "image_path_cc": row["image_path_cc"],
            "image_path_mlo": row["image_path_mlo"],
            "laterality": laterality,
        }

    def close(self) -> None:
        self.image_reader.close()

    def __del__(self) -> None:
        self.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, default=DEFAULT_CHECKPOINT_PATH)
    parser.add_argument("--submission-template", type=Path, default=DEFAULT_SUBMISSION_TEMPLATE_PATH)
    parser.add_argument("--archive-path", type=Path, default=DEFAULT_TEST_ARCHIVE_PATH)
    parser.add_argument("--image-root", type=Path, default=None)
    parser.add_argument("--image-size", type=int, default=1024)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Only run the first N submission rows. Intended for smoke/debug, not final submission.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ensure_file_exists(args.checkpoint, label="Checkpoint")
    ensure_file_exists(args.submission_template, label="Submission template")
    ensure_file_exists(args.archive_path, label="Test archive")

    output_dir = args.output_dir or derive_default_output_dir(checkpoint_path=args.checkpoint)
    output_dir, output_redirected = resolve_safe_output_dir(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    template_rows, template_fieldnames = load_submission_template(args.submission_template)
    archive_members = load_archive_members(args.archive_path)
    submission_rows = build_submission_rows(
        template_rows=template_rows,
        archive_members=archive_members,
        limit=args.limit,
    )

    dataset = TestPairedBreastDataset(
        rows=submission_rows,
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
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config_path = output_dir / SUBMISSION_CONFIG_FILENAME
    submission_path = output_dir / SUBMISSION_FILENAME

    write_json(
        config_path,
        build_submission_config(
            args=args,
            output_dir=output_dir,
            device=device,
            num_submission_rows=len(submission_rows),
        ),
    )

    print("Starting test submission inference", flush=True)
    print(f"- device: {describe_device(device)}", flush=True)
    print(f"- checkpoint: {args.checkpoint}", flush=True)
    print(f"- submission template: {args.submission_template}", flush=True)
    print(f"- test archive: {args.archive_path}", flush=True)
    print(f"- submission rows: {len(submission_rows)}", flush=True)
    if args.limit is not None:
        print(f"- limit: {args.limit}", flush=True)
    if output_redirected:
        print(f"- requested output dir preserved: {args.output_dir or derive_default_output_dir(args.checkpoint)}", flush=True)
    print(f"- output dir: {output_dir}", flush=True)

    try:
        model = PairedEfficientNetB2Baseline(weights=None).to(device)
        state_dict = torch.load(args.checkpoint, map_location=device)
        model.load_state_dict(state_dict)
        predictions_by_breast = predict_submission_scores(
            model=model,
            loader=loader,
            device=device,
        )
    finally:
        dataset.close()

    submission_output_rows = build_submission_output_rows(
        template_rows=template_rows,
        template_fieldnames=template_fieldnames,
        predictions_by_breast=predictions_by_breast,
        limit=args.limit,
    )
    write_submission_csv(
        path=submission_path,
        fieldnames=tuple(template_fieldnames),
        rows=submission_output_rows,
    )

    print("Submission inference finished successfully", flush=True)
    print(f"- device: {describe_device(device)}", flush=True)
    print(f"- wrote: {config_path}", flush=True)
    print(f"- wrote: {submission_path}", flush=True)
    return 0


def ensure_file_exists(path: Path, label: str) -> None:
    if path.exists() and path.is_file():
        return
    raise FileNotFoundError(f"{label} not found: {path}")


def derive_default_output_dir(checkpoint_path: Path) -> Path:
    return checkpoint_path.parent / "submission"


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


def load_submission_template(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"Submission template '{path}' has no header row.")
        missing_fields = [field for field in REQUIRED_TEMPLATE_FIELDS if field not in reader.fieldnames]
        if missing_fields:
            raise ValueError(
                f"Submission template '{path}' is missing required field(s): {', '.join(missing_fields)}"
            )
        rows = list(reader)

    duplicate_breast_ids = [
        breast_id
        for breast_id, count in Counter(row["breast_id"] for row in rows).items()
        if count > 1
    ]
    if duplicate_breast_ids:
        preview = ", ".join(sorted(duplicate_breast_ids)[:5])
        raise ValueError(f"Submission template '{path}' contains duplicate breast_id values: {preview}")

    return rows, list(reader.fieldnames)


def load_archive_members(path: Path) -> set[str]:
    with ZipFile(path) as archive:
        return {member.filename for member in archive.infolist() if not member.is_dir()}


def build_submission_rows(
    template_rows: list[dict[str, str]],
    archive_members: set[str],
    limit: int | None = None,
) -> list[dict[str, str]]:
    if limit is not None and limit <= 0:
        raise ValueError("limit must be positive when provided.")

    selected_rows = template_rows if limit is None else template_rows[:limit]
    submission_rows: list[dict[str, str]] = []
    missing_paths: list[str] = []

    for template_row in selected_rows:
        breast_id = template_row["breast_id"].strip()
        laterality = breast_id.rsplit("_", 1)[-1] if "_" in breast_id else ""
        image_id_cc = f"{breast_id}_CC"
        image_id_mlo = f"{breast_id}_MLO"
        image_path_cc = f"test_img/{breast_id}/{image_id_cc}.jpg"
        image_path_mlo = f"test_img/{breast_id}/{image_id_mlo}.jpg"

        for image_path in (image_path_cc, image_path_mlo):
            if image_path not in archive_members:
                missing_paths.append(image_path)

        submission_rows.append(
            {
                "breast_id": breast_id,
                "image_id_cc": image_id_cc,
                "image_id_mlo": image_id_mlo,
                "image_path_cc": image_path_cc,
                "image_path_mlo": image_path_mlo,
                "laterality": laterality,
            }
        )

    if missing_paths:
        preview = ", ".join(missing_paths[:4])
        raise ValueError(
            "Submission inference requires strict complete `(CC, MLO)` test rows. "
            f"Missing {len(missing_paths)} expected archive path(s): {preview}"
        )

    return submission_rows


def predict_submission_scores(
    model: torch.nn.Module,
    loader: DataLoader[dict[str, object]],
    device: torch.device,
) -> dict[str, float]:
    model.eval()
    predictions_by_breast: dict[str, float] = {}
    total_batches = len(loader)
    report_interval = 1 if total_batches <= 20 else max(1, total_batches // 20)

    with torch.no_grad():
        for batch_index, batch in enumerate(loader, start=1):
            x_cc = batch["x_cc"].to(device)
            x_mlo = batch["x_mlo"].to(device)
            logits = model(x_cc, x_mlo)
            probabilities = torch.sigmoid(logits).view(-1).cpu().tolist()

            for row_index, probability in enumerate(probabilities):
                breast_id = str(batch["breast_id"][row_index])
                predictions_by_breast[breast_id] = float(probability)

            if batch_index == 1 or batch_index == total_batches or batch_index % report_interval == 0:
                processed = len(predictions_by_breast)
                total = len(loader.dataset)
                print(
                    f"  progress: batch {batch_index}/{total_batches} breasts={processed}/{total}",
                    flush=True,
                )

    return predictions_by_breast


def build_submission_output_rows(
    template_rows: list[dict[str, str]],
    template_fieldnames: list[str],
    predictions_by_breast: dict[str, float],
    limit: int | None = None,
) -> list[dict[str, object]]:
    selected_rows = template_rows if limit is None else template_rows[:limit]
    output_rows: list[dict[str, object]] = []

    for template_row in selected_rows:
        breast_id = template_row["breast_id"]
        if breast_id not in predictions_by_breast:
            raise ValueError(f"Missing prediction for breast_id '{breast_id}'.")
        row = {field: template_row.get(field, "") for field in template_fieldnames}
        row["pred_score"] = predictions_by_breast[breast_id]
        output_rows.append(row)

    return output_rows


def build_submission_config(
    args: argparse.Namespace,
    output_dir: Path,
    device: torch.device,
    num_submission_rows: int,
) -> dict[str, object]:
    return {
        "checkpoint": str(args.checkpoint),
        "submission_template": str(args.submission_template),
        "archive_path": str(args.archive_path),
        "image_root": None if args.image_root is None else str(args.image_root),
        "image_size": args.image_size,
        "batch_size": args.batch_size,
        "num_workers": args.num_workers,
        "device": str(device),
        "device_description": describe_device(device),
        "output_dir": str(output_dir),
        "requested_output_dir": None if args.output_dir is None else str(args.output_dir),
        "num_submission_rows": num_submission_rows,
        "limit": args.limit,
    }


def write_submission_csv(path: Path, fieldnames: tuple[str, ...], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


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


if __name__ == "__main__":
    raise SystemExit(main())
