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
from PIL import Image

from src.data import SINGLE_IMAGE_FIELDS


REPO_ROOT = Path(__file__).resolve().parents[1]
TEST_TMP_ROOT = REPO_ROOT / "outputs" / "test_tmp"


class Stage1SmokeScriptTestCase(unittest.TestCase):
    def setUp(self) -> None:
        TEST_TMP_ROOT.mkdir(parents=True, exist_ok=True)
        self.root = TEST_TMP_ROOT / uuid.uuid4().hex
        self.root.mkdir(parents=True, exist_ok=False)

    def tearDown(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)

    def test_run_stage1_smoke_script_generates_report_and_key_artifacts(self) -> None:
        split_dir = self.root / "splits"
        split_dir.mkdir(parents=True, exist_ok=True)
        archive_path = self.root / "train_img.zip"
        train_split_path = split_dir / "primary_single_image_split_train.csv"
        val_split_path = split_dir / "primary_single_image_split_val.csv"
        output_dir = self.root / "smoke_output"

        train_rows = self.build_rows([("A_L", 0), ("B_R", 1), ("C_L", 0), ("D_R", 1)])
        val_rows = self.build_rows([("E_L", 0), ("F_R", 1)])

        self.write_archive(archive_path, train_rows + val_rows)
        self.write_csv(train_split_path, train_rows)
        self.write_csv(val_split_path, val_rows)
        self.write_split_summary(split_dir)

        completed = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "run_stage1_smoke.py"),
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

        self.assertIn("Stage 1 smoke test finished successfully", completed.stdout)

        report_path = output_dir / "stage1_smoke_report.md"
        train_metrics_path = output_dir / "train" / "metrics_summary.json"
        eval_metrics_path = output_dir / "eval" / "breast_level_metrics.json"
        image_predictions_path = output_dir / "eval" / "image_level_predictions.csv"
        breast_predictions_path = output_dir / "eval" / "breast_level_predictions.csv"

        self.assertTrue(report_path.exists())
        self.assertTrue(train_metrics_path.exists())
        self.assertTrue(eval_metrics_path.exists())
        self.assertTrue(image_predictions_path.exists())
        self.assertTrue(breast_predictions_path.exists())
        self.assertTrue((output_dir / "train_stdout.log").exists())
        self.assertTrue((output_dir / "eval_stdout.log").exists())

        report_text = report_path.read_text(encoding="utf-8")
        self.assertIn("# Stage 1 Smoke Report", report_text)
        self.assertIn("## Pipeline Coverage", report_text)
        self.assertIn("Current loop status:", report_text)
        self.assertIn("Main limitation:", report_text)
        self.assertIn(str(train_metrics_path), report_text)
        self.assertIn(str(eval_metrics_path), report_text)

        train_metrics = json.loads(train_metrics_path.read_text(encoding="utf-8"))
        eval_metrics = json.loads(eval_metrics_path.read_text(encoding="utf-8"))
        self.assertEqual(train_metrics["best_epoch"], 1)
        self.assertIn("breast_auroc", eval_metrics)
        self.assertIn("auroc_available", eval_metrics)

    def write_split_summary(self, split_dir: Path) -> None:
        summary = {
            "fold_assignment": {
                "val_fold": 0,
                "train_folds": [1, 2, 3, 4],
            },
            "paired": {
                "val": {
                    "label_counts": {"0": 1, "1": 1},
                }
            },
            "single": {
                "val": {
                    "label_counts": {"0": 2, "1": 2},
                }
            },
        }
        (split_dir / "primary_split_summary.json").write_text(
            json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

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
