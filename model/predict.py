import argparse
import sys
from pathlib import Path

import torch
from PIL import Image
from torchvision import transforms

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from model.config import load_training_meta
from model.labels import CLASS_NAMES
from model.model_def import build_model

DEFAULT_WEIGHTS = ROOT / "model" / "weights" / "best.pt"

def _transform(img_size: int):
    return transforms.Compose(
        [
            transforms.Resize((img_size, img_size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )


def load_model(weights_path=None, device=None):
    weights_path = Path(weights_path or DEFAULT_WEIGHTS)
    if not weights_path.is_file():
        raise FileNotFoundError(
            f"Weights not found at {weights_path}. Train with model/train.py or download from release."
        )
    device = device or torch.device("cpu")
    backbone, img_size = load_training_meta()
    model = build_model(num_classes=len(CLASS_NAMES), backbone=backbone, pretrained=False)
    state = torch.load(weights_path, map_location=device, weights_only=True)
    model.load_state_dict(state)
    model.to(device)
    model.eval()
    model._agrismart_img_size = img_size  # noqa: SLF001 — cache for predict()
    return model


def predict(image_path, model=None, device=None):
    device = device or torch.device("cpu")
    model = model or load_model(device=device)
    img_size = getattr(model, "_agrismart_img_size", load_training_meta()[1])
    img = Image.open(image_path).convert("RGB")
    x = _transform(img_size)(img).unsqueeze(0).to(device)
    with torch.no_grad():
        logits = model(x)
        probs = torch.softmax(logits, dim=1)
        idx = probs.argmax(dim=1).item()
    return CLASS_NAMES[idx], float(probs[0, idx].item())


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="AgriSmart crop disease prediction")
    p.add_argument("--image", required=True, help="Path to leaf image")
    p.add_argument("--weights", default=str(DEFAULT_WEIGHTS), help="Checkpoint path")
    args = p.parse_args()
    label, conf = predict(args.image, model=load_model(args.weights))
    print(f"{label} (confidence: {conf:.2f})")
