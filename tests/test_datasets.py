from __future__ import annotations

import csv
import shutil
import unittest
import uuid
from pathlib import Path
from zipfile import ZipFile

import numpy as np
import torch
from PIL import Image
from torch.utils.data import DataLoader

from src.data import PAIRED_BREAST_FIELDS, SINGLE_IMAGE_FIELDS
from src.data.datasets import PairedBreastDataset, SingleImageDataset
from src.data.transforms import build_eval_transform


REPO_ROOT = Path(__file__).resolve().parents[1]
TEST_TMP_ROOT = REPO_ROOT / "outputs" / "test_tmp"


class DatasetTransformTestCase(unittest.TestCase):
    def setUp(self) -> None:
        TEST_TMP_ROOT.mkdir(parents=True, exist_ok=True)
        self.root = TEST_TMP_ROOT / uuid.uuid4().hex
        self.root.mkdir(parents=True, exist_ok=False)

    def tearDown(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)

    def test_transform_outputs_float32_three_channel_tensor(self) -> None:
        pixels = np.zeros((6, 8), dtype=np.uint8)
        pixels[1:5, 2:6] = 180
        image = Image.fromarray(pixels).convert("RGB")
        transform = build_eval_transform(image_size=8, num_channels=3)

        tensor = transform(image, laterality="L")

        self.assertEqual(tensor.shape, (3, 8, 8))
        self.assertEqual(tensor.dtype, torch.float32)
        self.assertTrue(torch.allclose(tensor[0], tensor[1]))
        self.assertTrue(torch.allclose(tensor[1], tensor[2]))

    def test_right_laterality_is_horizontally_flipped(self) -> None:
        pixels = np.full((6, 8), 10, dtype=np.uint8)
        pixels[:, :4] = 220
        image = Image.fromarray(pixels).convert("RGB")
        transform = build_eval_transform(image_size=8, num_channels=1)

        left_tensor = transform(image, laterality="L")
        right_tensor = transform(image, laterality="R")

        self.assertTrue(torch.allclose(right_tensor[0], torch.flip(left_tensor[0], dims=[1])))

    def test_empty_foreground_falls_back_to_original_image(self) -> None:
        image = Image.fromarray(np.zeros((5, 7), dtype=np.uint8)).convert("RGB")
        transform = build_eval_transform(image_size=8, num_channels=1)

        tensor = transform(image, laterality="L")

        self.assertEqual(tensor.shape, (1, 8, 8))
        self.assertEqual(float(tensor.sum().item()), 0.0)

    def test_single_image_dataset_and_dataloader(self) -> None:
        single_index_path, paired_index_path, archive_path = self.create_dataset_files()
        dataset = SingleImageDataset(
            index_csv_path=single_index_path,
            archive_path=archive_path,
            transform=build_eval_transform(image_size=16, num_channels=3),
        )

        sample = dataset[0]
        self.assertEqual(
            set(sample.keys()),
            {"image", "target", "image_id", "breast_id", "view", "image_path", "laterality"},
        )
        self.assertEqual(sample["image"].shape, (3, 16, 16))
        self.assertEqual(sample["target"].dtype, torch.float32)

        loader = DataLoader(dataset, batch_size=2, shuffle=False, num_workers=0)
        batch = next(iter(loader))
        self.assertEqual(batch["image"].shape, (2, 3, 16, 16))
        self.assertEqual(batch["target"].shape, (2,))
        dataset.close()

    def test_paired_dataset_and_dataloader(self) -> None:
        single_index_path, paired_index_path, archive_path = self.create_dataset_files()
        dataset = PairedBreastDataset(
            index_csv_path=paired_index_path,
            archive_path=archive_path,
            transform=build_eval_transform(image_size=16, num_channels=3),
        )

        sample = dataset[0]
        self.assertEqual(
            set(sample.keys()),
            {
                "x_cc",
                "x_mlo",
                "target",
                "breast_id",
                "image_path_cc",
                "image_path_mlo",
                "image_id_cc",
                "image_id_mlo",
                "laterality",
            },
        )
        self.assertEqual(sample["x_cc"].shape, (3, 16, 16))
        self.assertEqual(sample["x_mlo"].shape, (3, 16, 16))

        loader = DataLoader(dataset, batch_size=1, shuffle=False, num_workers=0)
        batch = next(iter(loader))
        self.assertEqual(batch["x_cc"].shape, (1, 3, 16, 16))
        self.assertEqual(batch["x_mlo"].shape, (1, 3, 16, 16))
        self.assertEqual(batch["target"].shape, (1,))
        dataset.close()

    def test_paired_dataset_preserves_cc_then_mlo_order(self) -> None:
        _, paired_index_path, archive_path = self.create_dataset_files()
        dataset = PairedBreastDataset(
            index_csv_path=paired_index_path,
            archive_path=archive_path,
            transform=build_eval_transform(image_size=16, num_channels=1),
        )

        sample = dataset[0]
        cc_left_mean, cc_right_mean = self.split_half_means(sample["x_cc"][0])
        mlo_left_mean, mlo_right_mean = self.split_half_means(sample["x_mlo"][0])

        self.assertGreater(cc_left_mean, cc_right_mean)
        self.assertGreater(mlo_right_mean, mlo_left_mean)
        self.assertEqual(sample["image_id_cc"], "A_L_CC")
        self.assertEqual(sample["image_id_mlo"], "A_L_MLO")
        dataset.close()

    def test_paired_dataset_rejects_invalid_rows(self) -> None:
        archive_path = self.root / "invalid_train_img.zip"
        paired_index_path = self.root / "invalid_paired.csv"
        self.write_archive(archive_path)
        rows = [
            {
                "breast_id": "BROKEN",
                "pathology": "M",
                "is_malignant": "1",
                "image_id_cc": "BROKEN_CC",
                "image_id_mlo": "",
                "image_path_cc": "train_img/B_R/B_R_CC.jpg",
                "image_path_mlo": "train_img/B_R/B_R_CC.jpg",
                "laterality": "R",
                "device": "HLG",
                "birads": "4C",
            }
        ]
        self.write_csv(paired_index_path, PAIRED_BREAST_FIELDS, rows)

        with self.assertRaisesRegex(ValueError, "strict complete"):
            PairedBreastDataset(
                index_csv_path=paired_index_path,
                archive_path=archive_path,
                transform=build_eval_transform(image_size=16, num_channels=3),
            )

    def test_paired_dataset_rejects_view_semantic_mismatch(self) -> None:
        archive_path = self.root / "mismatched_train_img.zip"
        paired_index_path = self.root / "mismatched_paired.csv"
        self.write_archive(archive_path)
        rows = [
            {
                "breast_id": "SWAPPED",
                "pathology": "N",
                "is_malignant": "0",
                "image_id_cc": "A_L_MLO",
                "image_id_mlo": "A_L_CC",
                "image_path_cc": "train_img/A_L/A_L_MLO.jpg",
                "image_path_mlo": "train_img/A_L/A_L_CC.jpg",
                "laterality": "L",
                "device": "HLG",
                "birads": "1",
            }
        ]
        self.write_csv(paired_index_path, PAIRED_BREAST_FIELDS, rows)

        with self.assertRaisesRegex(ValueError, "CC semantics"):
            PairedBreastDataset(
                index_csv_path=paired_index_path,
                archive_path=archive_path,
                transform=build_eval_transform(image_size=16, num_channels=3),
            )

    def create_dataset_files(self) -> tuple[Path, Path, Path]:
        archive_path = self.root / "train_img.zip"
        single_index_path = self.root / "single.csv"
        paired_index_path = self.root / "paired.csv"

        self.write_archive(archive_path)
        self.write_single_index(single_index_path)
        self.write_paired_index(paired_index_path)
        return single_index_path, paired_index_path, archive_path

    def write_archive(self, archive_path: Path) -> None:
        left_cc = self.make_rgb_image(8, 10, bright_left=True)
        left_mlo = self.make_rgb_image(8, 10, bright_left=False)
        right_cc = self.make_rgb_image(8, 10, bright_left=True)
        right_mlo = self.make_rgb_image(8, 10, bright_left=False)

        with ZipFile(archive_path, "w") as archive:
            archive.writestr("train_img/A_L/A_L_CC.jpg", self.encode_image(left_cc))
            archive.writestr("train_img/A_L/A_L_MLO.jpg", self.encode_image(left_mlo))
            archive.writestr("train_img/B_R/B_R_CC.jpg", self.encode_image(right_cc))
            archive.writestr("train_img/B_R/B_R_MLO.jpg", self.encode_image(right_mlo))

    def write_single_index(self, path: Path) -> None:
        rows = [
            {
                "image_id": "A_L_CC",
                "breast_id": "A_L",
                "view": "CC",
                "pathology": "N",
                "is_malignant": "0",
                "image_path": "train_img/A_L/A_L_CC.jpg",
                "laterality": "L",
                "device": "HLG",
                "lesion_type": "",
                "birads": "1",
                "difficult": "N",
                "annotations": "[]",
            },
            {
                "image_id": "A_L_MLO",
                "breast_id": "A_L",
                "view": "MLO",
                "pathology": "N",
                "is_malignant": "0",
                "image_path": "train_img/A_L/A_L_MLO.jpg",
                "laterality": "L",
                "device": "HLG",
                "lesion_type": "",
                "birads": "1",
                "difficult": "N",
                "annotations": "[]",
            },
            {
                "image_id": "B_R_CC",
                "breast_id": "B_R",
                "view": "CC",
                "pathology": "M",
                "is_malignant": "1",
                "image_path": "train_img/B_R/B_R_CC.jpg",
                "laterality": "R",
                "device": "HLG",
                "lesion_type": "",
                "birads": "4C",
                "difficult": "N",
                "annotations": "[]",
            },
            {
                "image_id": "B_R_MLO",
                "breast_id": "B_R",
                "view": "MLO",
                "pathology": "M",
                "is_malignant": "1",
                "image_path": "train_img/B_R/B_R_MLO.jpg",
                "laterality": "R",
                "device": "HLG",
                "lesion_type": "",
                "birads": "4C",
                "difficult": "N",
                "annotations": "[]",
            },
        ]
        self.write_csv(path, SINGLE_IMAGE_FIELDS, rows)

    def write_paired_index(self, path: Path) -> None:
        rows = [
            {
                "breast_id": "A_L",
                "pathology": "N",
                "is_malignant": "0",
                "image_id_cc": "A_L_CC",
                "image_id_mlo": "A_L_MLO",
                "image_path_cc": "train_img/A_L/A_L_CC.jpg",
                "image_path_mlo": "train_img/A_L/A_L_MLO.jpg",
                "laterality": "L",
                "device": "HLG",
                "birads": "1",
            },
            {
                "breast_id": "B_R",
                "pathology": "M",
                "is_malignant": "1",
                "image_id_cc": "B_R_CC",
                "image_id_mlo": "B_R_MLO",
                "image_path_cc": "train_img/B_R/B_R_CC.jpg",
                "image_path_mlo": "train_img/B_R/B_R_MLO.jpg",
                "laterality": "R",
                "device": "HLG",
                "birads": "4C",
            },
        ]
        self.write_csv(path, PAIRED_BREAST_FIELDS, rows)

    def write_csv(self, path: Path, fieldnames: tuple[str, ...], rows: list[dict[str, str]]) -> None:
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def split_half_means(self, tensor: torch.Tensor) -> tuple[float, float]:
        midpoint = tensor.shape[1] // 2
        left_mean = float(tensor[:, :midpoint].mean().item())
        right_mean = float(tensor[:, midpoint:].mean().item())
        return left_mean, right_mean

    def make_rgb_image(self, width: int, height: int, bright_left: bool) -> np.ndarray:
        pixels = np.zeros((height, width), dtype=np.uint8)
        pixels[1:-1, 1:-1] = 20
        if bright_left:
            pixels[2:-2, 1: width // 2] = 220
        else:
            pixels[2:-2, width // 2 : -1] = 200
        return np.repeat(pixels[:, :, None], 3, axis=2)

    def encode_image(self, rgb_pixels: np.ndarray) -> bytes:
        image = Image.fromarray(rgb_pixels)
        from io import BytesIO

        buffer = BytesIO()
        image.save(buffer, format="JPEG")
        return buffer.getvalue()


if __name__ == "__main__":
    unittest.main()

