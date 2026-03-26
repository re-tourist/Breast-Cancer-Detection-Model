from __future__ import annotations

import csv
import json
import shutil
import unittest
import uuid
from pathlib import Path

from src.eval import aggregate_prediction_rows, compute_binary_auroc, evaluate_prediction_rows, write_evaluation_artifacts


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


if __name__ == "__main__":
    unittest.main()
