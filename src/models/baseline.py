"""Minimal baseline model for Stage 1 training."""

from __future__ import annotations

import torch
from torch import nn


class ConvBlock(nn.Module):
    """Small downsampling block used by the baseline CNN."""

    def __init__(self, in_channels: int, out_channels: int) -> None:
        super().__init__()
        self.block = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=2, padding=1, bias=False),
            nn.GroupNorm(4, out_channels),
            nn.ReLU(inplace=True),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.block(x)


class MinimalSingleImageCNN(nn.Module):
    """A compact CNN baseline for image-level malignant classification."""

    def __init__(self, in_channels: int = 3) -> None:
        super().__init__()
        channels = (16, 32, 64, 128)
        self.features = nn.Sequential(
            ConvBlock(in_channels, channels[0]),
            ConvBlock(channels[0], channels[1]),
            ConvBlock(channels[1], channels[2]),
            ConvBlock(channels[2], channels[3]),
            nn.AdaptiveAvgPool2d(1),
        )
        self.classifier = nn.Linear(channels[-1], 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.features(x)
        x = torch.flatten(x, start_dim=1)
        return self.classifier(x).squeeze(1)
