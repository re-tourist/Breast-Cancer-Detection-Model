"""Minimal mammography preprocessing transforms for Stage 1 Issue 1.2."""

from __future__ import annotations

import random
from dataclasses import dataclass

import numpy as np
import torch
from PIL import Image, ImageEnhance, ImageOps


@dataclass(slots=True)
class MammographyTransform:
    """Apply the minimal preprocessing pipeline for mammography images."""

    image_size: int = 1024
    num_channels: int = 3
    foreground_threshold: int = 5
    enable_augmentation: bool = False
    brightness_jitter: float = 0.05
    contrast_jitter: float = 0.05

    def __post_init__(self) -> None:
        if self.image_size <= 0:
            raise ValueError("image_size must be positive.")
        if self.num_channels not in (1, 3):
            raise ValueError("num_channels must be 1 or 3.")

    def __call__(self, image: Image.Image, laterality: str = "") -> torch.Tensor:
        image = image.convert("L")
        image = self._crop_foreground(image)

        if laterality.upper() == "R":
            image = ImageOps.mirror(image)

        if self.enable_augmentation:
            image = self._apply_light_augmentation(image)

        image = self._resize_and_pad(image)
        return self._to_tensor(image)

    def _crop_foreground(self, image: Image.Image) -> Image.Image:
        pixels = np.asarray(image)
        foreground = np.argwhere(pixels > self.foreground_threshold)
        if foreground.size == 0:
            return image

        top, left = foreground.min(axis=0)
        bottom, right = foreground.max(axis=0)
        return image.crop((int(left), int(top), int(right) + 1, int(bottom) + 1))

    def _apply_light_augmentation(self, image: Image.Image) -> Image.Image:
        brightness_factor = random.uniform(
            1.0 - self.brightness_jitter,
            1.0 + self.brightness_jitter,
        )
        contrast_factor = random.uniform(
            1.0 - self.contrast_jitter,
            1.0 + self.contrast_jitter,
        )
        image = ImageEnhance.Brightness(image).enhance(brightness_factor)
        image = ImageEnhance.Contrast(image).enhance(contrast_factor)
        return image

    def _resize_and_pad(self, image: Image.Image) -> Image.Image:
        width, height = image.size
        scale = min(self.image_size / width, self.image_size / height)
        resized_width = max(1, int(round(width * scale)))
        resized_height = max(1, int(round(height * scale)))

        resized = image.resize(
            (resized_width, resized_height),
            resample=Image.Resampling.BILINEAR,
        )
        canvas = Image.new("L", (self.image_size, self.image_size), color=0)
        offset_x = (self.image_size - resized_width) // 2
        offset_y = (self.image_size - resized_height) // 2
        canvas.paste(resized, (offset_x, offset_y))
        return canvas

    def _to_tensor(self, image: Image.Image) -> torch.Tensor:
        pixels = np.asarray(image, dtype=np.float32) / 255.0
        tensor = torch.from_numpy(pixels).unsqueeze(0)
        if self.num_channels == 3:
            tensor = tensor.repeat(3, 1, 1)
        return tensor.to(dtype=torch.float32)


def build_train_transform(
    image_size: int = 1024,
    num_channels: int = 3,
    enable_augmentation: bool = False,
) -> MammographyTransform:
    """Build the minimal training transform."""

    return MammographyTransform(
        image_size=image_size,
        num_channels=num_channels,
        enable_augmentation=enable_augmentation,
    )


def build_eval_transform(
    image_size: int = 1024,
    num_channels: int = 3,
) -> MammographyTransform:
    """Build the deterministic evaluation transform."""

    return MammographyTransform(
        image_size=image_size,
        num_channels=num_channels,
        enable_augmentation=False,
    )
