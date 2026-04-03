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

from scripts.run_test_submission import build_submission_rows
from src.models.baseline import PairedEfficientNetB2Baseline


REPO_ROOT = Path(__file__).resolve().parents[1]
TEST_TMP_ROOT = REPO_ROOT / "outputs" / "test_tmp"


class SubmissionScriptTestCase(unittest.TestCase):
    def setUp(self) -> None:
        TEST_TMP_ROOT.mkdir(parents=True, exist_ok=True)
        self.root = TEST_TMP_ROOT / uuid.uuid4().hex
        self.root.mkdir(parents=True, exist_ok=False)

    def tearDown(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)

    def test_build_submission_rows_maps_template_to_strict_test_paths(self) -> None:
        template_rows = [{"breast_id": "00213_R", "pred_score": ""}]
        archive_members = {
            "test_img/00213_R/00213_R_CC.jpg",
            "test_img/00213_R/00213_R_MLO.jpg",
        }

        submission_rows = build_submission_rows(template_rows=template_rows, archive_members=archive_members)

        self.assertEqual(len(submission_rows), 1)
        row = submission_rows[0]
        self.assertEqual(row["breast_id"], "00213_R")
        self.assertEqual(row["image_id_cc"], "00213_R_CC")
        self.assertEqual(row["image_id_mlo"], "00213_R_MLO")
        self.assertEqual(row["image_path_cc"], "test_img/00213_R/00213_R_CC.jpg")
        self.assertEqual(row["image_path_mlo"], "test_img/00213_R/00213_R_MLO.jpg")
        self.assertEqual(row["laterality"], "R")

    def test_run_test_submission_script_generates_submission_and_preserves_existing_output_dir(self) -> None:
        archive_path = self.root / "test_img.zip"
        checkpoint_path = self.root / "best_model.pt"
        template_path = self.root / "name_sid_submission.csv"
        requested_output_dir = self.root / "submission"
        requested_output_dir.mkdir(parents=True, exist_ok=False)
        (requested_output_dir / "sentinel.txt").write_text("keep", encoding="utf-8")

        breast_ids = ["A_L", "B_R"]
        self.write_submission_template(template_path, breast_ids)
        self.write_test_archive(archive_path, breast_ids)
        self.write_checkpoint(checkpoint_path)

        completed = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "run_test_submission.py"),
                "--checkpoint",
                str(checkpoint_path),
                "--submission-template",
                str(template_path),
                "--archive-path",
                str(archive_path),
                "--image-size",
                "64",
                "--batch-size",
                "1",
                "--output-dir",
                str(requested_output_dir),
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn("Starting test submission inference", completed.stdout)
        self.assertIn("requested output dir preserved", completed.stdout)
        self.assertIn("progress: batch 1/2", completed.stdout)
        self.assertIn("progress: batch 2/2", completed.stdout)
        self.assertIn("Submission inference finished successfully", completed.stdout)

        actual_output_dir = self.parse_output_dir(completed.stdout)
        self.assertNotEqual(actual_output_dir, requested_output_dir)
        self.assertTrue(actual_output_dir.exists())

        submission_path = actual_output_dir / "name_sid_submission.csv"
        config_path = actual_output_dir / "submission_config.json"
        self.assertTrue(submission_path.exists())
        self.assertTrue(config_path.exists())
        self.assertTrue((requested_output_dir / "sentinel.txt").exists())

        with submission_path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 2)
        for row in rows:
            self.assertIn(row["breast_id"], breast_ids)
            self.assertNotEqual(row["pred_score"], "")
            prediction = float(row["pred_score"])
            self.assertGreaterEqual(prediction, 0.0)
            self.assertLessEqual(prediction, 1.0)

        config = json.loads(config_path.read_text(encoding="utf-8"))
        self.assertEqual(config["checkpoint"], str(checkpoint_path))
        self.assertEqual(config["output_dir"], str(actual_output_dir))
        self.assertEqual(config["num_submission_rows"], 2)

    def write_submission_template(self, path: Path, breast_ids: list[str]) -> None:
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=("breast_id", "pred_score"))
            writer.writeheader()
            for breast_id in breast_ids:
                writer.writerow({"breast_id": breast_id, "pred_score": ""})

    def write_test_archive(self, archive_path: Path, breast_ids: list[str]) -> None:
        with ZipFile(archive_path, "w") as archive:
            for breast_id in breast_ids:
                for view in ("CC", "MLO"):
                    image_path = f"test_img/{breast_id}/{breast_id}_{view}.jpg"
                    archive.writestr(image_path, self.encode_image(self.make_rgb_image()))

    def write_checkpoint(self, checkpoint_path: Path) -> None:
        model = PairedEfficientNetB2Baseline(weights=None)
        checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        torch.save(model.state_dict(), checkpoint_path)

    def make_rgb_image(self, width: int = 24, height: int = 24) -> np.ndarray:
        pixels = np.zeros((height, width), dtype=np.uint8)
        pixels[3:-3, 3:-3] = 180
        return np.repeat(pixels[:, :, None], 3, axis=2)

    def encode_image(self, rgb_pixels: np.ndarray) -> bytes:
        image = Image.fromarray(rgb_pixels)
        buffer = BytesIO()
        image.save(buffer, format="JPEG")
        return buffer.getvalue()

    def parse_output_dir(self, stdout: str) -> Path:
        for line in stdout.splitlines():
            if line.startswith("- output dir: "):
                return Path(line.split(": ", 1)[1].strip())
        self.fail(f"Could not find output dir in stdout:\n{stdout}")


if __name__ == "__main__":
    unittest.main()
