from __future__ import annotations

import csv
import json
import shutil
import subprocess
import sys
import unittest
import uuid
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import numpy as np
import torch
from PIL import Image
from torch import nn

from src.data import SINGLE_IMAGE_FIELDS
from src.models.baseline import MinimalSingleImageCNN
from src.train.trainer import (
    build_single_image_loaders,
    fit,
    is_better_selection,
    resolve_selection_metric,
    validate_one_epoch,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
TEST_TMP_ROOT = REPO_ROOT / "outputs" / "test_tmp"


class TrainingSmokeTestCase(unittest.TestCase):
    def setUp(self) -> None:
        TEST_TMP_ROOT.mkdir(parents=True, exist_ok=True)
        self.root = TEST_TMP_ROOT / uuid.uuid4().hex
        self.root.mkdir(parents=True, exist_ok=False)

    def tearDown(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)

    def test_train_baseline_script_runs_end_to_end(self) -> None:
        train_split_path, val_split_path, archive_path = self.write_split_inputs(
            train_specs=[("A_L", 0), ("B_R", 1), ("C_L", 0), ("D_R", 1)],
            val_specs=[("E_L", 0), ("F_R", 1)],
        )
        output_dir = self.root / "baseline_output"

        completed = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "train_baseline.py"),
                "--train-split",
                str(train_split_path),
                "--val-split",
                str(val_split_path),
                "--archive-path",
                str(archive_path),
                "--image-size",
                "64",
                "--batch-size",
                "2",
                "--epochs",
                "1",
                "--output-dir",
                str(output_dir),
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn("Training finished successfully", completed.stdout)
        self.assertTrue((output_dir / "config.json").exists())
        self.assertTrue((output_dir / "metrics_summary.json").exists())
        self.assertTrue((output_dir / "best_model.pt").exists())

        metrics_summary = json.loads((output_dir / "metrics_summary.json").read_text(encoding="utf-8"))
        self.assertEqual(metrics_summary["best_epoch"], 1)
        self.assertEqual(metrics_summary["train_samples"], 8)
        self.assertEqual(metrics_summary["val_samples"], 4)
        self.assertEqual(metrics_summary["primary_selection_metric"], "breast_mean_auroc")
        self.assertEqual(metrics_summary["selection_mode"], "auto")
        self.assertEqual(metrics_summary["best_metric_name"], "breast_mean_auroc")
        self.assertIsNotNone(metrics_summary["best_metric_value"])
        self.assertFalse(metrics_summary["fallback_used"])
        self.assertEqual(metrics_summary["fallback_reason"], "")
        self.assertIn("image_accuracy", metrics_summary["best_metrics"])
        self.assertIn("breast_mean_accuracy", metrics_summary["best_metrics"])
        self.assertIsNotNone(metrics_summary["best_metrics"]["image_auroc"])
        self.assertIsNotNone(metrics_summary["best_metrics"]["breast_mean_auroc"])
        history_entry = metrics_summary["history"][0]
        self.assertEqual(history_entry["selection_metric_name"], "breast_mean_auroc")
        self.assertFalse(history_entry["selection_fallback_used"])
        self.assertEqual(history_entry["selection_fallback_reason"], "")

    def test_auto_selection_prefers_breast_mean_auroc(self) -> None:
        selection = resolve_selection_metric(
            {
                "val_loss": 0.8,
                "image_auroc": 0.63,
                "breast_mean_auroc": 0.71,
            },
            selection_metric="auto",
        )

        self.assertEqual(selection["metric_name"], "breast_mean_auroc")
        self.assertEqual(selection["metric_value"], 0.71)
        self.assertTrue(selection["higher_is_better"])
        self.assertFalse(selection["fallback_used"])
        self.assertEqual(selection["fallback_reason"], "")

    def test_auto_selection_falls_back_to_image_auroc(self) -> None:
        selection = resolve_selection_metric(
            {
                "val_loss": 0.8,
                "image_auroc": 0.63,
                "breast_mean_auroc": None,
            },
            selection_metric="auto",
        )

        self.assertEqual(selection["metric_name"], "image_auroc")
        self.assertEqual(selection["metric_value"], 0.63)
        self.assertTrue(selection["fallback_used"])
        self.assertIn("breast_mean_auroc unavailable", selection["fallback_reason"])

    def test_auto_selection_falls_back_to_val_loss(self) -> None:
        selection = resolve_selection_metric(
            {
                "val_loss": 0.42,
                "image_auroc": None,
                "breast_mean_auroc": None,
            },
            selection_metric="auto",
        )

        self.assertEqual(selection["metric_name"], "val_loss")
        self.assertEqual(selection["metric_value"], 0.42)
        self.assertFalse(selection["higher_is_better"])
        self.assertTrue(selection["fallback_used"])
        self.assertIn("image_auroc unavailable", selection["fallback_reason"])

    def test_higher_priority_selection_beats_lower_priority_metric(self) -> None:
        lower_priority = resolve_selection_metric(
            {
                "val_loss": 0.10,
                "image_auroc": 0.95,
                "breast_mean_auroc": None,
            },
            selection_metric="auto",
        )
        higher_priority = resolve_selection_metric(
            {
                "val_loss": 0.90,
                "image_auroc": 0.10,
                "breast_mean_auroc": 0.40,
            },
            selection_metric="auto",
        )

        self.assertTrue(is_better_selection(higher_priority, lower_priority))

    def test_validate_one_epoch_returns_none_for_single_class_auroc(self) -> None:
        train_split_path, val_split_path, archive_path = self.write_split_inputs(
            train_specs=[("A_L", 0), ("B_R", 1)],
            val_specs=[("C_L", 0), ("D_R", 0)],
        )
        loaders = build_single_image_loaders(
            train_split_csv_path=train_split_path,
            val_split_csv_path=val_split_path,
            archive_path=archive_path,
            image_size=64,
            batch_size=2,
            num_workers=0,
        )

        try:
            model = MinimalSingleImageCNN(in_channels=3)
            criterion = nn.BCEWithLogitsLoss()
            metrics = validate_one_epoch(
                model=model,
                loader=loaders.val_loader,
                criterion=criterion,
                device=torch.device("cpu"),
            )
        finally:
            loaders.close()

        self.assertIsNone(metrics["image_auroc"])
        self.assertIsNone(metrics["breast_mean_auroc"])
        self.assertEqual(metrics["num_val_images"], 4)
        self.assertEqual(metrics["num_val_breasts"], 2)

    def test_fit_raises_when_explicit_metric_is_unavailable_for_all_epochs(self) -> None:
        train_split_path, val_split_path, archive_path = self.write_split_inputs(
            train_specs=[("A_L", 0), ("B_R", 1)],
            val_specs=[("C_L", 0), ("D_R", 0)],
        )
        loaders = build_single_image_loaders(
            train_split_csv_path=train_split_path,
            val_split_csv_path=val_split_path,
            archive_path=archive_path,
            image_size=64,
            batch_size=2,
            num_workers=0,
        )

        try:
            model = MinimalSingleImageCNN(in_channels=3)
            criterion = nn.BCEWithLogitsLoss()
            optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
            with self.assertRaisesRegex(
                ValueError,
                "Selection metric 'image_auroc' was unavailable for every epoch",
            ):
                fit(
                    model=model,
                    train_loader=loaders.train_loader,
                    val_loader=loaders.val_loader,
                    optimizer=optimizer,
                    criterion=criterion,
                    device=torch.device("cpu"),
                    epochs=1,
                    output_dir=self.root / "explicit_metric_missing",
                    selection_metric="image_auroc",
                )
        finally:
            loaders.close()

    def write_split_inputs(
        self,
        train_specs: list[tuple[str, int]],
        val_specs: list[tuple[str, int]],
    ) -> tuple[Path, Path, Path]:
        archive_path = self.root / "train_img.zip"
        train_split_path = self.root / "train_split.csv"
        val_split_path = self.root / "val_split.csv"

        train_rows = self.build_rows(train_specs)
        val_rows = self.build_rows(val_specs)

        self.write_archive(archive_path, train_rows + val_rows)
        self.write_csv(train_split_path, train_rows)
        self.write_csv(val_split_path, val_rows)
        return train_split_path, val_split_path, archive_path

    def build_rows(self, specs: list[tuple[str, int]]) -> list[dict[str, str]]:
        rows: list[dict[str, str]] = []
        for breast_id, label in specs:
            laterality = breast_id.split("_")[-1]
            pathology = "M" if label == 1 else "N"
            birads = "4C" if label == 1 else "1"
            for view in ("CC", "MLO"):
                rows.append(
                    {
                        "image_id": f"{breast_id}_{view}",
                        "breast_id": breast_id,
                        "view": view,
                        "pathology": pathology,
                        "is_malignant": str(label),
                        "image_path": f"train_img/{breast_id}/{breast_id}_{view}.jpg",
                        "laterality": laterality,
                        "device": "HLG",
                        "lesion_type": "",
                        "birads": birads,
                        "difficult": "N",
                        "annotations": "[]",
                    }
                )
        return rows

    def write_archive(self, archive_path: Path, rows: list[dict[str, str]]) -> None:
        with ZipFile(archive_path, "w") as archive:
            for row in rows:
                label = int(row["is_malignant"])
                bright_left = row["view"] == "CC"
                pixels = self.make_rgb_image(width=32, height=40, label=label, bright_left=bright_left)
                archive.writestr(row["image_path"], self.encode_image(pixels))

    def write_csv(self, path: Path, rows: list[dict[str, str]]) -> None:
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=SINGLE_IMAGE_FIELDS)
            writer.writeheader()
            writer.writerows(rows)

    def make_rgb_image(self, width: int, height: int, label: int, bright_left: bool) -> np.ndarray:
        pixels = np.zeros((height, width), dtype=np.uint8)
        pixels[2:-2, 2:-2] = 30 if label == 0 else 150
        if bright_left:
            pixels[6:-6, 3 : width // 2] = 220 if label == 1 else 90
        else:
            pixels[6:-6, width // 2 : -3] = 220 if label == 1 else 90
        return np.repeat(pixels[:, :, None], 3, axis=2)

    def encode_image(self, rgb_pixels: np.ndarray) -> bytes:
        image = Image.fromarray(rgb_pixels)
        buffer = BytesIO()
        image.save(buffer, format="JPEG")
        return buffer.getvalue()


if __name__ == "__main__":
    unittest.main()
