"""Evaluate best checkpoint on val or holdout_lab_sample."""

import argparse
import sys
from pathlib import Path

import torch
from torch.utils.data import DataLoader
from torchvision import datasets

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from model.config import load_training_meta
from model.train import evaluate, val_transforms
from model.model_def import build_model


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--split", choices=("val", "holdout_lab_sample"), default="val")
    p.add_argument("--data-root", type=Path, default=ROOT / "data")
    p.add_argument("--weights", type=Path, default=ROOT / "model" / "weights" / "best.pt")
    args = p.parse_args()

    backbone, img_size = load_training_meta()
    split_dir = args.data_root / args.split
    ds = datasets.ImageFolder(str(split_dir), transform=val_transforms(img_size))
    loader = DataLoader(ds, batch_size=32, shuffle=False)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = build_model(len(ds.classes), backbone=backbone, pretrained=False)
    model.load_state_dict(torch.load(args.weights, map_location=device, weights_only=True))
    model.to(device)
    loss, macro_f1, acc, y_true, y_pred = evaluate(model, loader, device)
    print(f"Split: {args.split}  macro-F1={macro_f1:.4f}  accuracy={acc:.4f}  loss={loss:.4f}")


if __name__ == "__main__":
    main()
