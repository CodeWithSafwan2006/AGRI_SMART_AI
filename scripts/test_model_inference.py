"""Unit tests for AgriSmart model inference pipeline.

Tests model loading, prediction output format, confidence scoring,
label validity, and augmentation pipeline correctness.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from model.labels import CLASS_NAMES
from model.config import load_training_meta, DEFAULT_BACKBONE, DEFAULT_IMG_SIZE


# ---------------------------------------------------------------------------
# Test utilities
# ---------------------------------------------------------------------------

def _print_result(test_name: str, passed: bool, detail: str = ""):
    status = "✅ PASS" if passed else "❌ FAIL"
    msg = f"  {status} | {test_name}"
    if detail:
        msg += f" — {detail}"
    print(msg)
    return passed


# ---------------------------------------------------------------------------
# Test: Class label integrity
# ---------------------------------------------------------------------------

def test_class_labels():
    """Verify CLASS_NAMES list is properly configured."""
    results = []

    results.append(_print_result(
        "CLASS_NAMES is non-empty",
        len(CLASS_NAMES) > 0,
        f"{len(CLASS_NAMES)} classes defined",
    ))

    results.append(_print_result(
        "Expected 18 classes",
        len(CLASS_NAMES) == 18,
        f"got {len(CLASS_NAMES)}",
    ))

    # Check no duplicates
    unique = set(CLASS_NAMES)
    results.append(_print_result(
        "No duplicate class names",
        len(unique) == len(CLASS_NAMES),
    ))

    # Check format: should contain '___'
    has_separator = all("___" in name for name in CLASS_NAMES)
    results.append(_print_result(
        "All labels use crop___disease format",
        has_separator,
    ))

    # Check for healthy classes
    healthy = [c for c in CLASS_NAMES if "healthy" in c.lower()]
    results.append(_print_result(
        "Contains healthy baseline classes",
        len(healthy) > 0,
        f"{len(healthy)} healthy classes found",
    ))

    return all(results)


# ---------------------------------------------------------------------------
# Test: Model config consistency
# ---------------------------------------------------------------------------

def test_model_config():
    """Verify model configuration is consistent."""
    results = []

    backbone, img_size = load_training_meta()

    results.append(_print_result(
        "Backbone is valid string",
        isinstance(backbone, str) and len(backbone) > 0,
        f"backbone='{backbone}'",
    ))

    results.append(_print_result(
        "Image size is positive integer",
        isinstance(img_size, int) and img_size > 0,
        f"img_size={img_size}",
    ))

    results.append(_print_result(
        "Image size is power-of-2 friendly",
        img_size in (96, 128, 160, 192, 224, 256, 288, 320, 384, 448, 512),
        f"img_size={img_size}",
    ))

    return all(results)


# ---------------------------------------------------------------------------
# Test: Augmentation presets
# ---------------------------------------------------------------------------

def test_augmentation_presets():
    """Verify augmentation module presets are accessible and valid."""
    results = []

    try:
        from model.augmentation import (
            light_augmentation,
            standard_augmentation,
            heavy_augmentation,
            validation_transform,
            get_augmentation,
            AUGMENTATION_PRESETS,
        )
        results.append(_print_result("Augmentation module imports", True))
    except ImportError as e:
        results.append(_print_result("Augmentation module imports", False, str(e)))
        return False

    results.append(_print_result(
        "AUGMENTATION_PRESETS has 3 entries",
        len(AUGMENTATION_PRESETS) == 3,
        f"got {len(AUGMENTATION_PRESETS)}",
    ))

    for preset_name in ["light", "standard", "heavy"]:
        try:
            t = get_augmentation(preset_name, img_size=224)
            results.append(_print_result(
                f"Preset '{preset_name}' builds successfully",
                t is not None,
            ))
        except Exception as e:
            results.append(_print_result(
                f"Preset '{preset_name}' builds successfully",
                False, str(e),
            ))

    # Validation transform
    try:
        vt = validation_transform(224)
        results.append(_print_result(
            "Validation transform builds",
            vt is not None,
        ))
    except Exception as e:
        results.append(_print_result("Validation transform builds", False, str(e)))

    return all(results)


# ---------------------------------------------------------------------------
# Test: Model loading (if weights exist)
# ---------------------------------------------------------------------------

def test_model_loading():
    """Test model loading if pre-trained weights are available."""
    results = []
    weights_path = ROOT / "model" / "weights" / "best.pt"

    if not weights_path.exists():
        _print_result(
            "Model weights exist",
            False,
            f"Skipping: {weights_path} not found (training required)",
        )
        return True  # Not a failure, just skip

    results.append(_print_result("Model weights file exists", True, f"{weights_path.stat().st_size / 1024:.0f} KB"))

    try:
        from model.predict import load_model
        model = load_model()
        results.append(_print_result("Model loads without error", True))
    except Exception as e:
        results.append(_print_result("Model loads without error", False, str(e)))
        return False

    # Verify model has expected output size
    try:
        import torch
        model.eval()
        dummy = torch.randn(1, 3, 224, 224)
        with torch.no_grad():
            output = model(dummy)
        num_outputs = output.shape[-1]
        results.append(_print_result(
            "Output matches CLASS_NAMES count",
            num_outputs == len(CLASS_NAMES),
            f"output_dim={num_outputs}, expected={len(CLASS_NAMES)}",
        ))
    except Exception as e:
        results.append(_print_result("Forward pass succeeds", False, str(e)))

    return all(results)


# ---------------------------------------------------------------------------
# Test: Precautions coverage
# ---------------------------------------------------------------------------

def test_precautions_coverage():
    """Verify precautions are defined for all disease classes."""
    results = []

    from app.precautions import PRECAUTIONS, display_name, precaution_for

    covered = sum(1 for c in CLASS_NAMES if c in PRECAUTIONS)
    results.append(_print_result(
        "Precautions coverage",
        covered == len(CLASS_NAMES),
        f"{covered}/{len(CLASS_NAMES)} classes have precautions",
    ))

    # Test display_name function
    for cls in CLASS_NAMES[:3]:
        dn = display_name(cls)
        results.append(_print_result(
            f"display_name('{cls[:20]}...')",
            "___" not in dn and len(dn) > 0,
            f"→ '{dn}'",
        ))

    # Test fallback
    fallback = precaution_for("Unknown___Disease")
    results.append(_print_result(
        "Fallback precaution works",
        len(fallback) > 0,
    ))

    return all(results)


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def main():
    print("\n🌿 AgriSmart Model Inference Test Suite")
    print("=" * 50)

    all_passed = True

    print("\n📋 Class Label Tests:")
    all_passed &= test_class_labels()

    print("\n⚙️ Model Config Tests:")
    all_passed &= test_model_config()

    print("\n🔄 Augmentation Tests:")
    all_passed &= test_augmentation_presets()

    print("\n🧠 Model Loading Tests:")
    all_passed &= test_model_loading()

    print("\n🛡️ Precautions Coverage Tests:")
    all_passed &= test_precautions_coverage()

    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed. Review output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
