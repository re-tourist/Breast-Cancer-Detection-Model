"""Minimal dataset loaders for Stage 1 Issue 1.2."""

from __future__ import annotations

import csv
from io import BytesIO
from pathlib import Path
from typing import Any, Callable
from zipfile import ZipFile

import torch
from PIL import Image
from torch.utils.data import Dataset


DEFAULT_SINGLE_INDEX_PATH = Path("data/processed/metadata/primary_single_image_index.csv")
DEFAULT_PAIRED_INDEX_PATH = Path("data/processed/metadata/primary_paired_breast_index.csv")
DEFAULT_ARCHIVE_PATH = Path("data/raw/primary/train_img.zip")
PAIRED_REQUIRED_FIELDS = ("breast_id", "image_id_cc", "image_id_mlo", "image_path_cc", "image_path_mlo")


class ArchiveImageReader:
    """Read course images from an extracted root or directly from the zip archive."""

    def __init__(self, archive_path: str | Path, image_root: str | Path | None = None) -> None:
        self.archive_path = Path(archive_path)
        self.image_root = Path(image_root) if image_root else None
        self._archive: ZipFile | None = None

    def read(self, image_path: str) -> Image.Image:
        filesystem_path = self._resolve_filesystem_path(image_path)
        if filesystem_path is not None and filesystem_path.exists():
            with Image.open(filesystem_path) as image:
                return image.convert("RGB")

        archive = self._get_archive()
        with archive.open(image_path) as handle:
            data = handle.read()
        with Image.open(BytesIO(data)) as image:
            return image.convert("RGB")

    def close(self) -> None:
        if self._archive is not None:
            self._archive.close()
            self._archive = None

    def _resolve_filesystem_path(self, image_path: str) -> Path | None:
        if self.image_root is None:
            return None
        return self.image_root / image_path

    def _get_archive(self) -> ZipFile:
        if self._archive is None:
            self._archive = ZipFile(self.archive_path)
        return self._archive

    def __del__(self) -> None:
        self.close()


class SingleImageDataset(Dataset[dict[str, Any]]):
    """Load single-image mammography samples from the normalized index."""

    def __init__(
        self,
        index_csv_path: str | Path,
        archive_path: str | Path,
        transform: Callable[[Image.Image, str], torch.Tensor],
        image_root: str | Path | None = None,
    ) -> None:
        self.index_csv_path = Path(index_csv_path)
        self.transform = transform
        self.rows = _load_index_rows(self.index_csv_path)
        self.image_reader: ArchiveImageReader | None = None
        self.image_reader = ArchiveImageReader(archive_path=archive_path, image_root=image_root)

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, index: int) -> dict[str, Any]:
        row = self.rows[index]
        image = self.image_reader.read(row["image_path"])
        tensor = self.transform(image, laterality=row.get("laterality", ""))
        target = torch.tensor(float(row["is_malignant"]), dtype=torch.float32)
        return {
            "image": tensor,
            "target": target,
            "image_id": row["image_id"],
            "breast_id": row["breast_id"],
            "view": row["view"],
            "image_path": row["image_path"],
            "laterality": row.get("laterality", ""),
        }

    def close(self) -> None:
        if self.image_reader is not None:
            self.image_reader.close()
            self.image_reader = None

    def __del__(self) -> None:
        self.close()


class PairedBreastDataset(Dataset[dict[str, Any]]):
    """Load paired CC/MLO breast-level samples from the normalized index."""

    def __init__(
        self,
        index_csv_path: str | Path,
        archive_path: str | Path,
        transform: Callable[[Image.Image, str], torch.Tensor],
        image_root: str | Path | None = None,
    ) -> None:
        self.index_csv_path = Path(index_csv_path)
        self.transform = transform
        self.rows = _load_index_rows(self.index_csv_path)
        self.image_reader: ArchiveImageReader | None = None
        _validate_paired_rows(self.rows, self.index_csv_path)
        self.image_reader = ArchiveImageReader(archive_path=archive_path, image_root=image_root)

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, index: int) -> dict[str, Any]:
        row = self.rows[index]
        laterality = row.get("laterality", "")
        cc_image = self.image_reader.read(row["image_path_cc"])
        mlo_image = self.image_reader.read(row["image_path_mlo"])
        x_cc = self.transform(cc_image, laterality=laterality)
        x_mlo = self.transform(mlo_image, laterality=laterality)
        target = torch.tensor(float(row["is_malignant"]), dtype=torch.float32)
        return {
            "x_cc": x_cc,
            "x_mlo": x_mlo,
            "target": target,
            "breast_id": row["breast_id"],
            "image_path_cc": row["image_path_cc"],
            "image_path_mlo": row["image_path_mlo"],
            "image_id_cc": row["image_id_cc"],
            "image_id_mlo": row["image_id_mlo"],
            "laterality": laterality,
        }

    def close(self) -> None:
        if self.image_reader is not None:
            self.image_reader.close()
            self.image_reader = None

    def __del__(self) -> None:
        self.close()


def _load_index_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _validate_paired_rows(rows: list[dict[str, str]], index_csv_path: Path) -> None:
    invalid_rows: list[str] = []
    for row_index, row in enumerate(rows, start=2):
        empty_fields = [field for field in PAIRED_REQUIRED_FIELDS if not str(row.get(field, "")).strip()]
        if empty_fields:
            invalid_rows.append(
                f"row {row_index} breast_id={row.get('breast_id', '')}: empty fields {', '.join(empty_fields)}"
            )
            continue
        if str(row["image_id_cc"]) == str(row["image_id_mlo"]):
            invalid_rows.append(
                f"row {row_index} breast_id={row['breast_id']}: image_id_cc and image_id_mlo must differ"
            )
        if str(row["image_path_cc"]) == str(row["image_path_mlo"]):
            invalid_rows.append(
                f"row {row_index} breast_id={row['breast_id']}: image_path_cc and image_path_mlo must differ"
            )
        if not _matches_expected_view(str(row["image_id_cc"]), expected_view="CC"):
            invalid_rows.append(
                f"row {row_index} breast_id={row['breast_id']}: image_id_cc does not encode CC semantics"
            )
        if not _matches_expected_view(str(row["image_id_mlo"]), expected_view="MLO"):
            invalid_rows.append(
                f"row {row_index} breast_id={row['breast_id']}: image_id_mlo does not encode MLO semantics"
            )
        if not _matches_expected_view(str(row["image_path_cc"]), expected_view="CC"):
            invalid_rows.append(
                f"row {row_index} breast_id={row['breast_id']}: image_path_cc does not encode CC semantics"
            )
        if not _matches_expected_view(str(row["image_path_mlo"]), expected_view="MLO"):
            invalid_rows.append(
                f"row {row_index} breast_id={row['breast_id']}: image_path_mlo does not encode MLO semantics"
            )

    if invalid_rows:
        preview = "; ".join(invalid_rows[:3])
        raise ValueError(
            "PairedBreastDataset requires strict complete `(CC, MLO)` rows. "
            f"Found {len(invalid_rows)} invalid row(s) in '{index_csv_path}': {preview}"
        )


def _matches_expected_view(value: str, expected_view: str) -> bool:
    normalized = Path(value).stem.upper()
    suffix = f"_{expected_view.upper()}"
    return normalized.endswith(suffix)
