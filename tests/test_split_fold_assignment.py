from __future__ import annotations

import csv
import json
import shutil
import unittest
import uuid
from pathlib import Path

from src.data import FOLD_ASSIGNMENT_FIELDS, PAIRED_BREAST_FIELDS, SINGLE_IMAGE_FIELDS
from src.data.splits import build_train_val_split, write_split_artifacts


REPO_ROOT = Path(__file__).resolve().parents[1]
TEST_TMP_ROOT = REPO_ROOT / "outputs" / "test_tmp"


class SplitFoldAssignmentTestCase(unittest.TestCase):
    def setUp(self) -> None:
        TEST_TMP_ROOT.mkdir(parents=True, exist_ok=True)
        self.root = TEST_TMP_ROOT / uuid.uuid4().hex
        self.root.mkdir(parents=True, exist_ok=False)

    def tearDown(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)

    def test_fold_assignment_has_unique_breast_ids_and_complete_fold_range(self) -> None:
        paired_path, single_path = self.write_split_inputs(num_negative=5, num_positive=5)

        split_result = build_train_val_split(
            paired_index_csv_path=paired_path,
            single_index_csv_path=single_path,
            val_ratio=0.2,
            random_state=42,
            stratified=True,
        )
        fold_assignment = split_result["fold_assignment"]
        assignment_rows = fold_assignment["rows"]

        self.assertTrue(fold_assignment["available"])
        self.assertEqual(len(assignment_rows), 10)
        self.assertEqual(len({row["breast_id"] for row in assignment_rows}), 10)
        self.assertEqual(sorted({int(row["fold"]) for row in assignment_rows}), [0, 1, 2, 3, 4])
        self.assertTrue(all(row["target"] in {"0", "1"} for row in assignment_rows))
        self.assertTrue(all(int(row["num_images"]) == 2 for row in assignment_rows))

    def test_train_val_split_matches_fold_zero_assignment_and_artifacts_are_written(self) -> None:
        paired_path, single_path = self.write_split_inputs(num_negative=5, num_positive=5)

        split_result = build_train_val_split(
            paired_index_csv_path=paired_path,
            single_index_csv_path=single_path,
            val_ratio=0.2,
            random_state=42,
            stratified=True,
        )
        output_paths = write_split_artifacts(split_result, output_dir=self.root / "splits")

        assignment_rows = self.read_csv(output_paths["fold_assignment"])
        fold_summary = json.loads(output_paths["fold_summary"].read_text(encoding="utf-8"))

        self.assertEqual(tuple(assignment_rows[0].keys()), FOLD_ASSIGNMENT_FIELDS)
        val_ids = {row["breast_id"] for row in assignment_rows if int(row["fold"]) == 0}
        train_ids = {row["breast_id"] for row in assignment_rows if int(row["fold"]) != 0}
        self.assertEqual(val_ids, set(split_result["breast_ids"]["val"]))
        self.assertEqual(train_ids, set(split_result["breast_ids"]["train"]))
        self.assertTrue(val_ids.isdisjoint(train_ids))
        self.assertEqual(fold_summary["fold_count"], 5)
        self.assertEqual(fold_summary["val_fold"], 0)
        self.assertTrue(fold_summary["train_val_derived_from_fold_assignment"])
        self.assertEqual(fold_summary["total_breasts"], 10)
        self.assertFalse(fold_summary["used_fallback"])

    def write_split_inputs(self, num_negative: int, num_positive: int) -> tuple[Path, Path]:
        paired_path = self.root / "paired.csv"
        single_path = self.root / "single.csv"
        paired_rows = []
        single_rows = []

        index = 0
        for label in [0] * num_negative + [1] * num_positive:
            breast_id = f"{index:03d}_{'L' if index % 2 == 0 else 'R'}"
            paired_rows.append(self.make_paired_row(breast_id, label))
            single_rows.append(self.make_single_row(breast_id, "CC", label))
            single_rows.append(self.make_single_row(breast_id, "MLO", label))
            index += 1

        self.write_csv(paired_path, PAIRED_BREAST_FIELDS, paired_rows)
        self.write_csv(single_path, SINGLE_IMAGE_FIELDS, single_rows)
        return paired_path, single_path

    def make_paired_row(self, breast_id: str, label: int) -> dict[str, str]:
        laterality = breast_id.split("_")[-1]
        pathology = "M" if label == 1 else "N"
        birads = "4C" if label == 1 else "1"
        return {
            "breast_id": breast_id,
            "pathology": pathology,
            "is_malignant": str(label),
            "image_id_cc": f"{breast_id}_CC",
            "image_id_mlo": f"{breast_id}_MLO",
            "image_path_cc": f"train_img/{breast_id}/{breast_id}_CC.jpg",
            "image_path_mlo": f"train_img/{breast_id}/{breast_id}_MLO.jpg",
            "laterality": laterality,
            "device": "HLG",
            "birads": birads,
        }

    def make_single_row(self, breast_id: str, view: str, label: int) -> dict[str, str]:
        laterality = breast_id.split("_")[-1]
        pathology = "M" if label == 1 else "N"
        birads = "4C" if label == 1 else "1"
        return {
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

    def write_csv(self, path: Path, fieldnames: tuple[str, ...], rows: list[dict[str, str]]) -> None:
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def read_csv(self, path: Path) -> list[dict[str, str]]:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))


if __name__ == "__main__":
    unittest.main()
