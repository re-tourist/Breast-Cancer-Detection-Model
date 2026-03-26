"""Public data indexing and loading interface for Stage 1."""

from .datasets import (
    DEFAULT_ARCHIVE_PATH,
    DEFAULT_PAIRED_INDEX_PATH,
    DEFAULT_SINGLE_INDEX_PATH,
    PairedBreastDataset,
    SingleImageDataset,
)
from .index_builder import (
    PAIRED_BREAST_FIELDS,
    SINGLE_IMAGE_FIELDS,
    build_index_report,
    build_paired_breast_index,
    build_single_image_index,
)
from .splits import (
    DEFAULT_SPLIT_DIR,
    FOLD_ASSIGNMENT_FIELDS,
    SplitBuildError,
    build_split_summary,
    build_train_val_split,
    write_split_artifacts,
)
from .transforms import MammographyTransform, build_eval_transform, build_train_transform

__all__ = [
    "SINGLE_IMAGE_FIELDS",
    "PAIRED_BREAST_FIELDS",
    "FOLD_ASSIGNMENT_FIELDS",
    "build_single_image_index",
    "build_paired_breast_index",
    "build_index_report",
    "MammographyTransform",
    "build_train_transform",
    "build_eval_transform",
    "SingleImageDataset",
    "PairedBreastDataset",
    "DEFAULT_SINGLE_INDEX_PATH",
    "DEFAULT_PAIRED_INDEX_PATH",
    "DEFAULT_ARCHIVE_PATH",
    "DEFAULT_SPLIT_DIR",
    "SplitBuildError",
    "build_train_val_split",
    "build_split_summary",
    "write_split_artifacts",
]
