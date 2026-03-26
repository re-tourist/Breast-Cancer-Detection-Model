from __future__ import annotations

import csv
import json
import shutil
import unittest
import uuid
from pathlib import Path

from src.data import PAIRED_BREAST_FIELDS, SINGLE_IMAGE_FIELDS
from src.data.splits import (
    SplitBuildError,
    build_split_summary,
    build_train_val_split,
    write_split_artifacts,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
TEST_TMP_ROOT = REPO_ROOT / "outputs" / "test_tmp"


class SplitBuilderTestCase(unittest.TestCase):
    def setUp(self) -> None:
        TEST_TMP_ROOT.mkdir(parents=True, exist_ok=True)
        self.root = TEST_TMP_ROOT / uuid.uuid4().hex
        self.root.mkdir(parents=True, exist_ok=False)

    def tearDown(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)

    def test_build_train_val_split_is_reproducible_and_leak_free(self) -> None:
        paired_path, single_path = self.write_split_inputs(num_negative=5, num_positive=5)

        split_a = build_train_val_split(paired_path, single_path, val_ratio=0.2, random_state=42, stratified=True)
        split_b = build_train_val_split(paired_path, single_path, val_ratio=0.2, random_state=42, stratified=True)
        summary = build_split_summary(split_a)

        self.assertEqual(split_a["breast_ids"], split_b["breast_ids"])
        self.assertEqual(summary["split_strategy"], "stratified_group_holdout")
        self.assertFalse(summary["checks"]["strategy_fallback"]["used_fallback"])
        self.assertEqual(summary["paired"]["train"]["num_breasts"], 8)
        self.assertEqual(summary["paired"]["val"]["num_breasts"], 2)
        self.assertEqual(summary["single"]["train"]["num_images"], 16)
        self.assertEqual(summary["single"]["val"]["num_images"], 4)
        self.assertEqual(summary["checks"]["breast_id_leakage"]["overlap_count"], 0)
        self.assertEqual(
            {row["breast_id"] for row in split_a["single"]["train_rows"]},
            set(split_a["breast_ids"]["train"]),
        )
        self.assertEqual(
            {row["breast_id"] for row in split_a["single"]["val_rows"]},
            set(split_a["breast_ids"]["val"]),
        )

    def test_write_split_artifacts_preserves_schema_and_core_fields(self) -> None:
        paired_path, single_path = self.write_split_inputs(num_negative=5, num_positive=5)
        split_result = build_train_val_split(paired_path, single_path, random_state=42, stratified=True)

        output_dir = self.root / "splits"
        output_paths = write_split_artifacts(split_result, output_dir=output_dir)

        paired_train_rows = self.read_csv(output_paths["paired_train"])
        paired_val_rows = self.read_csv(output_paths["paired_val"])
        single_train_rows = self.read_csv(output_paths["single_train"])
        summary = json.loads(output_paths["summary"].read_text(encoding="utf-8"))

        self.assertEqual(tuple(paired_train_rows[0].keys()), PAIRED_BREAST_FIELDS)
        self.assertEqual(tuple(single_train_rows[0].keys()), SINGLE_IMAGE_FIELDS)
        for row in paired_train_rows + paired_val_rows:
            self.assertTrue(row["image_id_cc"])
            self.assertTrue(row["image_id_mlo"])
            self.assertTrue(row["image_path_cc"])
            self.assertTrue(row["image_path_mlo"])
        self.assertEqual(summary["paired"]["train"]["num_rows"], len(paired_train_rows))
        self.assertEqual(summary["paired"]["val"]["num_rows"], len(paired_val_rows))

    def test_duplicate_paired_breast_id_raises(self) -> None:
        paired_path, single_path = self.write_split_inputs(num_negative=5, num_positive=5)
        paired_rows = self.read_csv(paired_path)
        paired_rows.append(dict(paired_rows[0]))
        self.write_csv(paired_path, PAIRED_BREAST_FIELDS, paired_rows)

        with self.assertRaises(SplitBuildError) as context:
            build_train_val_split(paired_path, single_path)

        self.assertIn("duplicate breast_id", str(context.exception))

    def test_missing_required_column_raises(self) -> None:
        paired_path, single_path = self.write_split_inputs(num_negative=5, num_positive=5)
        paired_rows = self.read_csv(paired_path)
        reduced_fieldnames = tuple(field for field in PAIRED_BREAST_FIELDS if field != "image_path_mlo")
        self.write_csv(
            paired_path,
            reduced_fieldnames,
            [{field: row[field] for field in reduced_fieldnames} for row in paired_rows],
        )

        with self.assertRaises(SplitBuildError) as context:
            build_train_val_split(paired_path, single_path)

        self.assertIn("missing required columns", str(context.exception))

    def test_unmapped_single_breast_id_raises(self) -> None:
        paired_path, single_path = self.write_split_inputs(num_negative=5, num_positive=5)
        single_rows = self.read_csv(single_path)
        single_rows.extend(
            [
                self.make_single_row("EXTRA_R", "CC", 0),
                self.make_single_row("EXTRA_R", "MLO", 0),
            ]
        )
        self.write_csv(single_path, SINGLE_IMAGE_FIELDS, single_rows)

        with self.assertRaises(SplitBuildError) as context:
            build_train_val_split(paired_path, single_path)

        self.assertIn("do not share the same breast_id set", str(context.exception))

    def test_stratified_fallback_is_reported(self) -> None:
        paired_path, single_path = self.write_split_inputs(num_negative=2, num_positive=2)

        split_result = build_train_val_split(paired_path, single_path, val_ratio=0.2, random_state=42, stratified=True)
        summary = build_split_summary(split_result)

        self.assertEqual(summary["split_strategy"], "group_shuffle_holdout")
        self.assertTrue(summary["checks"]["strategy_fallback"]["used_fallback"])
        self.assertIn("requires at least 5 samples", summary["checks"]["strategy_fallback"]["reason"])

    def test_empty_split_raises(self) -> None:
        paired_path, single_path = self.write_split_inputs(num_negative=1, num_positive=0)

        with self.assertRaises(SplitBuildError) as context:
            build_train_val_split(paired_path, single_path, val_ratio=0.2, random_state=42, stratified=False)

        self.assertIn("Failed to build group split", str(context.exception))

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
