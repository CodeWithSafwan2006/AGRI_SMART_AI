"""Model export utility for ONNX and TorchScript deployment formats.

Converts trained AgriSmart crop disease models to optimized inference
formats suitable for edge deployment, mobile inference, and cloud serving.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from model.config import load_training_meta
from model.labels import CLASS_NAMES
from model.model_def import build_model


def export_torchscript(
    weights_path: Path,
    output_path: Path | None = None,
    img_size: int = 224,
) -> Path:
    """Export model to TorchScript format for C++ inference.

    Args:
        weights_path: Path to the trained .pt checkpoint.
        output_path: Destination path. Defaults to weights_dir/model_scripted.pt.
        img_size: Input image resolution.

    Returns:
        Path to the exported TorchScript file.
    """
    backbone, meta_img_size = load_training_meta()
    img_size = meta_img_size or img_size
    num_classes = len(CLASS_NAMES)

    model = build_model(num_classes=num_classes, backbone=backbone)

    state = torch.load(str(weights_path), map_location="cpu", weights_only=True)
    model.load_state_dict(state)
    model.eval()

    dummy_input = torch.randn(1, 3, img_size, img_size)

    scripted = torch.jit.trace(model, dummy_input)

    if output_path is None:
        output_path = weights_path.parent / "model_scripted.pt"

    scripted.save(str(output_path))
    print(f"✅ TorchScript model exported to: {output_path}")
    print(f"   Input shape: (1, 3, {img_size}, {img_size})")
    print(f"   Output classes: {num_classes}")

    return output_path


def export_onnx(
    weights_path: Path,
    output_path: Path | None = None,
    img_size: int = 224,
    opset_version: int = 17,
) -> Path:
    """Export model to ONNX format for cross-platform inference.

    Args:
        weights_path: Path to the trained .pt checkpoint.
        output_path: Destination path. Defaults to weights_dir/model.onnx.
        img_size: Input image resolution.
        opset_version: ONNX opset version (default 17).

    Returns:
        Path to the exported ONNX file.
    """
    try:
        import onnx  # noqa: F401
    except ImportError:
        print("❌ ONNX package not installed. Run: pip install onnx onnxruntime")
        raise

    backbone, meta_img_size = load_training_meta()
    img_size = meta_img_size or img_size
    num_classes = len(CLASS_NAMES)

    model = build_model(num_classes=num_classes, backbone=backbone)

    state = torch.load(str(weights_path), map_location="cpu", weights_only=True)
    model.load_state_dict(state)
    model.eval()

    dummy_input = torch.randn(1, 3, img_size, img_size)

    if output_path is None:
        output_path = weights_path.parent / "model.onnx"

    torch.onnx.export(
        model,
        dummy_input,
        str(output_path),
        export_params=True,
        opset_version=opset_version,
        do_constant_folding=True,
        input_names=["leaf_image"],
        output_names=["disease_logits"],
        dynamic_axes={
            "leaf_image": {0: "batch_size"},
            "disease_logits": {0: "batch_size"},
        },
    )

    # Validate exported model
    onnx_model = onnx.load(str(output_path))
    onnx.checker.check_model(onnx_model)

    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"✅ ONNX model exported to: {output_path}")
    print(f"   Opset version: {opset_version}")
    print(f"   File size: {file_size_mb:.1f} MB")
    print(f"   Input: leaf_image (1, 3, {img_size}, {img_size})")
    print(f"   Output: disease_logits ({num_classes} classes)")

    return output_path


def get_model_info(weights_path: Path) -> dict:
    """Get metadata about a trained model checkpoint.

    Returns:
        Dict with backbone, img_size, num_classes, num_params, and file_size_mb.
    """
    backbone, img_size = load_training_meta()
    num_classes = len(CLASS_NAMES)

    model = build_model(num_classes=num_classes, backbone=backbone)
    state = torch.load(str(weights_path), map_location="cpu", weights_only=True)
    model.load_state_dict(state)

    num_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    file_size_mb = weights_path.stat().st_size / (1024 * 1024)

    return {
        "backbone": backbone,
        "img_size": img_size,
        "num_classes": num_classes,
        "class_names": CLASS_NAMES,
        "total_params": num_params,
        "trainable_params": trainable_params,
        "file_size_mb": round(file_size_mb, 2),
    }


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export AgriSmart model to deployment formats")
    parser.add_argument(
        "--weights",
        type=str,
        default=str(ROOT / "model" / "weights" / "best.pt"),
        help="Path to trained model weights (.pt file)",
    )
    parser.add_argument(
        "--format",
        choices=["onnx", "torchscript", "info"],
        default="info",
        help="Export format or 'info' to display model metadata",
    )
    parser.add_argument("--output", type=str, default=None, help="Output file path")

    args = parser.parse_args()
    weights = Path(args.weights)

    if not weights.exists():
        print(f"❌ Weights file not found: {weights}")
        sys.exit(1)

    if args.format == "info":
        info = get_model_info(weights)
        print("\n🌿 AgriSmart Model Checkpoint Info")
        print("=" * 40)
        for k, v in info.items():
            if k != "class_names":
                print(f"  {k}: {v}")
        print(f"  classes: {', '.join(info['class_names'][:5])}... ({info['num_classes']} total)")
    elif args.format == "onnx":
        export_onnx(weights, Path(args.output) if args.output else None)
    elif args.format == "torchscript":
        export_torchscript(weights, Path(args.output) if args.output else None)
