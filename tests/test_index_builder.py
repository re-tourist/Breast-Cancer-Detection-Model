from __future__ import annotations

import csv
import shutil
import unittest
import uuid
from pathlib import Path
from zipfile import ZipFile

from src.data.index_builder import (
    DatasetIndexError,
    build_index_report,
    build_paired_breast_index,
    build_single_image_index,
)


FIELDNAMES = [
    "image_path",
    "breast_id",
    "l_r",
    "device",
    "cc_mlo",
    "lesion_type",
    "birads",
    "pathology",
    "difficult",
    "annotations",
]
REPO_ROOT = Path(__file__).resolve().parents[1]
TEST_TMP_ROOT = REPO_ROOT / "outputs" / "test_tmp"


class IndexBuilderTestCase(unittest.TestCase):
    def setUp(self) -> None:
        TEST_TMP_ROOT.mkdir(parents=True, exist_ok=True)
        self.root = TEST_TMP_ROOT / uuid.uuid4().hex
        self.root.mkdir(parents=True, exist_ok=False)

    def tearDown(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)

    def test_build_single_and_paired_index_success(self) -> None:
        rows = [
            self.make_row("train_img/00001_L/00001_L_MLO.jpg", "00001_L", "L", "MLO", "B", "3"),
            self.make_row("train_img/00001_L/00001_L_CC.jpg", "00001_L", "L", "CC", "B", "3"),
            self.make_row("train_img/00002_R/00002_R_MLO.jpg", "00002_R", "R", "MLO", "M", "4C"),
            self.make_row("train_img/00002_R/00002_R_CC.jpg", "00002_R", "R", "CC", "M", "4C"),
        ]
        csv_path, archive_path = self.write_dataset(rows)

        single_rows, single_validation = build_single_image_index(csv_path, archive_path, strict=True)
        paired_rows, paired_validation = build_paired_breast_index(single_rows, strict=True)
        report = build_index_report(
            single_rows,
            paired_rows,
            {
                "status": "ok",
                "error_counts": {
                    **single_validation["error_counts"],
                    **paired_validation["error_counts"],
                },
            },
        )

        self.assertEqual([row["view"] for row in single_rows[:2]], ["CC", "MLO"])
        self.assertEqual(len(single_rows), 4)
        self.assertEqual(len(paired_rows), 2)
        self.assertEqual(paired_rows[0]["image_id_cc"], "00001_L_CC")
        self.assertEqual(paired_rows[0]["image_id_mlo"], "00001_L_MLO")
        self.assertEqual(paired_rows[1]["is_malignant"], 1)
        self.assertEqual(report["summary"]["total_images"], 4)
        self.assertEqual(report["summary"]["paired_success_count"], 2)
        self.assertEqual(report["summary"]["image_level_pathology_distribution"], {"B": 2, "M": 2})
        self.assertEqual(report["summary"]["breast_level_is_malignant_distribution"], {"0": 1, "1": 1})

    def test_duplicate_image_id_raises(self) -> None:
        rows = [
            self.make_row("train_img/a/dup.jpg", "A_L", "L", "CC", "N", "1"),
            self.make_row("train_img/b/dup.jpg", "A_L", "L", "MLO", "N", "1"),
        ]
        csv_path, archive_path = self.write_dataset(rows)

        with self.assertRaises(DatasetIndexError) as context:
            build_single_image_index(csv_path, archive_path, strict=True)

        self.assertIn("duplicate_image_ids", str(context.exception))

    def test_invalid_view_set_raises(self) -> None:
        rows = [
            self.make_row("train_img/a/A_L_CC_1.jpg", "A_L", "L", "CC", "N", "1"),
            self.make_row("train_img/a/A_L_CC_2.jpg", "A_L", "L", "CC", "N", "1"),
        ]
        csv_path, archive_path = self.write_dataset(rows)

        with self.assertRaises(DatasetIndexError) as context:
            build_single_image_index(csv_path, archive_path, strict=True)

        self.assertIn("invalid_breast_view_pairs", str(context.exception))

    def test_inconsistent_pathology_raises(self) -> None:
        rows = [
            self.make_row("train_img/a/A_L_CC.jpg", "A_L", "L", "CC", "B", "3"),
            self.make_row("train_img/a/A_L_MLO.jpg", "A_L", "L", "MLO", "M", "4C"),
        ]
        csv_path, archive_path = self.write_dataset(rows)

        with self.assertRaises(DatasetIndexError) as context:
            build_single_image_index(csv_path, archive_path, strict=True)

        self.assertIn("inconsistent_breast_pathology", str(context.exception))

    def test_missing_archive_member_raises(self) -> None:
        rows = [
            self.make_row("train_img/a/A_L_CC.jpg", "A_L", "L", "CC", "N", "1"),
            self.make_row("train_img/a/A_L_MLO.jpg", "A_L", "L", "MLO", "N", "1"),
        ]
        csv_path, archive_path = self.write_dataset(rows, missing_archive_paths={"train_img/a/A_L_MLO.jpg"})

        with self.assertRaises(DatasetIndexError) as context:
            build_single_image_index(csv_path, archive_path, strict=True)

        self.assertIn("missing_archive_paths", str(context.exception))

    def test_paired_builder_rejects_missing_pair(self) -> None:
        single_rows = [
            {
                "image_id": "A_L_CC",
                "breast_id": "A_L",
                "view": "CC",
                "pathology": "N",
                "is_malignant": 0,
                "image_path": "train_img/a/A_L_CC.jpg",
                "laterality": "L",
                "device": "HLG",
                "lesion_type": "",
                "birads": "1",
                "difficult": "N",
                "annotations": "[]",
            }
        ]

        with self.assertRaises(DatasetIndexError) as context:
            build_paired_breast_index(single_rows, strict=True)

        self.assertIn("invalid_paired_samples", str(context.exception))

    def make_row(
        self,
        image_path: str,
        breast_id: str,
        laterality: str,
        view: str,
        pathology: str,
        birads: str,
    ) -> dict[str, str]:
        return {
            "image_path": image_path,
            "breast_id": breast_id,
            "l_r": laterality,
            "device": "HLG",
            "cc_mlo": view,
            "lesion_type": "",
            "birads": birads,
            "pathology": pathology,
            "difficult": "N",
            "annotations": "[]",
        }

    def write_dataset(
        self,
        rows: list[dict[str, str]],
        missing_archive_paths: set[str] | None = None,
    ) -> tuple[Path, Path]:
        csv_path = self.root / "train.csv"
        archive_path = self.root / "train_img.zip"
        missing_archive_paths = missing_archive_paths or set()

        with csv_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(rows)

        with ZipFile(archive_path, "w") as archive:
            for row in rows:
                if row["image_path"] in missing_archive_paths:
                    continue
                archive.writestr(row["image_path"], b"test")

        return csv_path, archive_path


if __name__ == "__main__":
    unittest.main()
