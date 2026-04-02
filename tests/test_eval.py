from __future__ import annotations

import csv
import json
import shutil
import unittest
import uuid
from pathlib import Path

import torch
from torch import nn

from scripts.run_eval import derive_default_output_dir, resolve_safe_output_dir
from src.eval import (
    PAIRED_BREAST_LEVEL_PREDICTION_FIELDS,
    aggregate_prediction_rows,
    collect_paired_breast_prediction_rows,
    compute_binary_auroc,
    evaluate_breast_prediction_rows,
    evaluate_prediction_rows,
    write_evaluation_artifacts,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
TEST_TMP_ROOT = REPO_ROOT / "outputs" / "test_tmp"


class EvaluationTestCase(unittest.TestCase):
    def setUp(self) -> None:
        TEST_TMP_ROOT.mkdir(parents=True, exist_ok=True)
        self.root = TEST_TMP_ROOT / uuid.uuid4().hex
        self.root.mkdir(parents=True, exist_ok=False)

    def tearDown(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)

    def test_mean_aggregation_is_correct(self) -> None:
        rows = [
            self.make_prediction_row("A", "A_CC", 1, 0.2),
            self.make_prediction_row("A", "A_MLO", 1, 0.8),
        ]

        aggregated = aggregate_prediction_rows(rows, aggregation="mean")

        self.assertEqual(len(aggregated), 1)
        self.assertEqual(aggregated[0]["breast_id"], "A")
        self.assertEqual(aggregated[0]["target"], 1)
        self.assertAlmostEqual(aggregated[0]["prediction"], 0.5)
        self.assertEqual(aggregated[0]["num_items_aggregated"], 2)

    def test_max_aggregation_is_correct(self) -> None:
        rows = [
            self.make_prediction_row("A", "A_CC", 1, 0.2),
            self.make_prediction_row("A", "A_MLO", 1, 0.8),
        ]

        aggregated = aggregate_prediction_rows(rows, aggregation="max")

        self.assertEqual(len(aggregated), 1)
        self.assertAlmostEqual(aggregated[0]["prediction"], 0.8)

    def test_inconsistent_targets_raise(self) -> None:
        rows = [
            self.make_prediction_row("A", "A_CC", 1, 0.2),
            self.make_prediction_row("A", "A_MLO", 0, 0.8),
        ]

        with self.assertRaisesRegex(ValueError, "Inconsistent targets"):
            aggregate_prediction_rows(rows, aggregation="mean")

    def test_single_class_auroc_returns_none(self) -> None:
        auroc = compute_binary_auroc(targets=[0, 0, 0], predictions=[0.1, 0.2, 0.3])
        self.assertIsNone(auroc)

    def test_evaluation_artifacts_are_written(self) -> None:
        image_rows = [
            self.make_prediction_row("A", "A_CC", 1, 0.2),
            self.make_prediction_row("A", "A_MLO", 1, 0.8),
            self.make_prediction_row("B", "B_CC", 0, 0.1),
            self.make_prediction_row("B", "B_MLO", 0, 0.4),
        ]

        evaluation_result = evaluate_prediction_rows(image_rows, aggregation="mean")
        output_paths = write_evaluation_artifacts(
            output_dir=self.root / "eval_output",
            image_prediction_rows=evaluation_result["image_prediction_rows"],
            breast_prediction_rows=evaluation_result["breast_prediction_rows"],
            metrics=evaluation_result["metrics"],
        )

        self.assertTrue(output_paths["image_predictions"].exists())
        self.assertTrue(output_paths["breast_predictions"].exists())
        self.assertTrue(output_paths["metrics"].exists())

        breast_rows = self.read_csv(output_paths["breast_predictions"])
        metrics = json.loads(output_paths["metrics"].read_text(encoding="utf-8"))

        self.assertEqual(len(breast_rows), 2)
        self.assertEqual({row["breast_id"] for row in breast_rows}, {"A", "B"})
        self.assertTrue(metrics["auroc_available"])
        self.assertIsNotNone(metrics["breast_auroc"])

    def test_collect_paired_prediction_rows_preserves_order_and_probabilities(self) -> None:
        loader = [
            {
                "x_cc": torch.zeros((2, 3, 4, 4), dtype=torch.float32),
                "x_mlo": torch.ones((2, 3, 4, 4), dtype=torch.float32),
                "target": torch.tensor([0.0, 1.0], dtype=torch.float32),
                "breast_id": ["A_L", "B_R"],
                "image_id_cc": ["A_L_CC", "B_R_CC"],
                "image_id_mlo": ["A_L_MLO", "B_R_MLO"],
                "image_path_cc": [
                    "train_img/A_L/A_L_CC.jpg",
                    "train_img/B_R/B_R_CC.jpg",
                ],
                "image_path_mlo": [
                    "train_img/A_L/A_L_MLO.jpg",
                    "train_img/B_R/B_R_MLO.jpg",
                ],
            }
        ]

        prediction_rows = collect_paired_breast_prediction_rows(
            model=DummyPairedModel(logits=[0.0, 2.0]),
            loader=loader,
            device=torch.device("cpu"),
        )

        self.assertEqual(len(prediction_rows), 2)
        self.assertEqual(prediction_rows[0]["image_id_cc"], "A_L_CC")
        self.assertEqual(prediction_rows[0]["image_id_mlo"], "A_L_MLO")
        self.assertAlmostEqual(prediction_rows[0]["prediction"], 0.5, places=6)
        self.assertGreater(prediction_rows[1]["prediction"], 0.5)
        for row in prediction_rows:
            self.assertGreaterEqual(row["prediction"], 0.0)
            self.assertLessEqual(row["prediction"], 1.0)

    def test_paired_evaluation_artifacts_skip_image_level_csv(self) -> None:
        breast_rows = [
            {
                "breast_id": "A",
                "target": 1,
                "prediction": 0.75,
                "image_id_cc": "A_CC",
                "image_id_mlo": "A_MLO",
                "image_path_cc": "train_img/A/A_CC.jpg",
                "image_path_mlo": "train_img/A/A_MLO.jpg",
            },
            {
                "breast_id": "B",
                "target": 0,
                "prediction": 0.15,
                "image_id_cc": "B_CC",
                "image_id_mlo": "B_MLO",
                "image_path_cc": "train_img/B/B_CC.jpg",
                "image_path_mlo": "train_img/B/B_MLO.jpg",
            },
        ]

        evaluation_result = evaluate_breast_prediction_rows(breast_rows)
        output_paths = write_evaluation_artifacts(
            output_dir=self.root / "paired_eval_output",
            image_prediction_rows=None,
            breast_prediction_rows=evaluation_result["breast_prediction_rows"],
            metrics=evaluation_result["metrics"],
            breast_prediction_fieldnames=PAIRED_BREAST_LEVEL_PREDICTION_FIELDS,
        )

        self.assertIsNone(output_paths["image_predictions"])
        self.assertFalse((self.root / "paired_eval_output" / "image_level_predictions.csv").exists())
        self.assertTrue(output_paths["breast_predictions"].exists())
        self.assertTrue(output_paths["metrics"].exists())

        breast_rows_written = self.read_csv(output_paths["breast_predictions"])
        self.assertEqual(list(breast_rows_written[0].keys()), list(PAIRED_BREAST_LEVEL_PREDICTION_FIELDS))
        for row in breast_rows_written:
            self.assertGreaterEqual(float(row["prediction"]), 0.0)
            self.assertLessEqual(float(row["prediction"]), 1.0)

    def test_eval_output_dir_defaults_to_checkpoint_parent_when_checkpoint_is_explicit(self) -> None:
        checkpoint_path = self.root / "custom_run" / "best_model.pt"
        output_dir = derive_default_output_dir(
            checkpoint_path=checkpoint_path,
            fallback_output_dir=self.root / "fallback_eval",
            user_provided_checkpoint=True,
        )
        self.assertEqual(output_dir, checkpoint_path.parent / "eval")

    def test_eval_output_dir_preserves_existing_non_empty_directory(self) -> None:
        requested_output_dir = self.root / "eval_output"
        requested_output_dir.mkdir(parents=True, exist_ok=False)
        (requested_output_dir / "breast_level_metrics.json").write_text("{}", encoding="utf-8")

        actual_output_dir, redirected = resolve_safe_output_dir(requested_output_dir)

        self.assertTrue(redirected)
        self.assertNotEqual(actual_output_dir, requested_output_dir)
        self.assertEqual(actual_output_dir.parent, requested_output_dir.parent)
        self.assertTrue(actual_output_dir.name.startswith(f"{requested_output_dir.name}_"))

    def make_prediction_row(self, breast_id: str, image_id: str, target: int, prediction: float) -> dict[str, object]:
        view = "CC" if image_id.endswith("CC") else "MLO"
        return {
            "image_id": image_id,
            "breast_id": breast_id,
            "target": target,
            "prediction": prediction,
            "image_path": f"train_img/{breast_id}/{image_id}.jpg",
            "view": view,
        }

    def read_csv(self, path: Path) -> list[dict[str, str]]:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))


class DummyPairedModel(nn.Module):
    def __init__(self, logits: list[float]) -> None:
        super().__init__()
        self.register_buffer("logits", torch.tensor(logits, dtype=torch.float32))

    def forward(self, x_cc: torch.Tensor, x_mlo: torch.Tensor) -> torch.Tensor:
        return self.logits[: x_cc.shape[0]]


if __name__ == "__main__":
    unittest.main()
