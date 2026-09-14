"""Data augmentation utilities for AgriSmart crop disease image pipeline.

Provides configurable augmentation transforms for training, validation, and
test-time augmentation (TTA) workflows. Separates augmentation logic from
the training loop for reusability and experimentation.
"""

from __future__ import annotations

from typing import Any

from torchvision import transforms

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


# ---------------------------------------------------------------------------
# Training augmentation presets
# ---------------------------------------------------------------------------

def light_augmentation(img_size: int = 224) -> transforms.Compose:
    """Minimal augmentation for baseline comparison runs."""
    return transforms.Compose([
        transforms.RandomResizedCrop(img_size, scale=(0.85, 1.0)),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
    ])


def standard_augmentation(img_size: int = 224) -> transforms.Compose:
    """Standard field-grade augmentation with rotation, color jitter, and flip."""
    return transforms.Compose([
        transforms.RandomResizedCrop(img_size, scale=(0.7, 1.0)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(p=0.3),
        transforms.RandomRotation(25),
        transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.3),
        transforms.RandomAffine(degrees=0, translate=(0.05, 0.05), shear=8),
        transforms.ToTensor(),
        transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
    ])


def heavy_augmentation(img_size: int = 224) -> transforms.Compose:
    """Aggressive augmentation for maximum regularization and lab-to-field generalization."""
    return transforms.Compose([
        transforms.RandomResizedCrop(img_size, scale=(0.6, 1.0)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(p=0.4),
        transforms.RandomRotation(35),
        transforms.ColorJitter(brightness=0.4, contrast=0.4, saturation=0.4, hue=0.1),
        transforms.RandomAffine(degrees=0, translate=(0.08, 0.08), shear=12),
        transforms.RandomPerspective(distortion_scale=0.25, p=0.35),
        transforms.GaussianBlur(kernel_size=3, sigma=(0.1, 1.5)),
        transforms.ToTensor(),
        transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
        transforms.RandomErasing(p=0.25, scale=(0.02, 0.15)),
    ])


# ---------------------------------------------------------------------------
# Validation / inference transforms
# ---------------------------------------------------------------------------

def validation_transform(img_size: int = 224) -> transforms.Compose:
    """Deterministic center-crop transform for validation and holdout evaluation."""
    return transforms.Compose([
        transforms.Resize(int(img_size * 1.15)),
        transforms.CenterCrop(img_size),
        transforms.ToTensor(),
        transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
    ])


# ---------------------------------------------------------------------------
# Test-Time Augmentation (TTA)
# ---------------------------------------------------------------------------

def tta_transforms(img_size: int = 224, n_augments: int = 5) -> list[transforms.Compose]:
    """Generate a list of slightly varied transforms for test-time augmentation.

    Returns `n_augments` transforms that can be applied to the same image,
    with predictions averaged for improved robustness.
    """
    base_resize = int(img_size * 1.15)
    tta_list = [
        # Original center crop (deterministic baseline)
        validation_transform(img_size),
    ]

    variations = [
        transforms.Compose([
            transforms.Resize(base_resize),
            transforms.CenterCrop(img_size),
            transforms.RandomHorizontalFlip(p=1.0),
            transforms.ToTensor(),
            transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
        ]),
        transforms.Compose([
            transforms.Resize(base_resize),
            transforms.RandomCrop(img_size),
            transforms.ToTensor(),
            transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
        ]),
        transforms.Compose([
            transforms.Resize(base_resize),
            transforms.CenterCrop(img_size),
            transforms.RandomRotation(15),
            transforms.ToTensor(),
            transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
        ]),
        transforms.Compose([
            transforms.Resize(base_resize),
            transforms.CenterCrop(img_size),
            transforms.ColorJitter(brightness=0.2, contrast=0.2),
            transforms.ToTensor(),
            transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
        ]),
    ]

    for v in variations[:n_augments - 1]:
        tta_list.append(v)

    return tta_list


# ---------------------------------------------------------------------------
# Preset registry for CLI / config-driven selection
# ---------------------------------------------------------------------------

AUGMENTATION_PRESETS: dict[str, Any] = {
    "light": light_augmentation,
    "standard": standard_augmentation,
    "heavy": heavy_augmentation,
}


def get_augmentation(preset: str = "standard", img_size: int = 224) -> transforms.Compose:
    """Return an augmentation pipeline by preset name.

    Args:
        preset: One of 'light', 'standard', 'heavy'.
        img_size: Target image resolution (default 224 for EfficientNet-B0).

    Returns:
        A torchvision Compose transform pipeline.
    """
    factory = AUGMENTATION_PRESETS.get(preset)
    if factory is None:
        raise ValueError(f"Unknown augmentation preset '{preset}'. Choose from {list(AUGMENTATION_PRESETS.keys())}")
    return factory(img_size)
