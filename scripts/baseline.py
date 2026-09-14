"""Majority-class baseline macro-F1 on validation split."""

import sys
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.metrics import f1_score
from torchvision import datasets

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from model.train import val_transforms


def main():
    val_dir = ROOT / "data" / "val"
    if not val_dir.is_dir():
        raise SystemExit("Run curate_and_split.py first.")
    ds = datasets.ImageFolder(str(val_dir), transform=val_transforms())
    counts = Counter(ds.targets)
    majority = counts.most_common(1)[0][0]
    preds = np.full(len(ds.targets), majority)
    macro_f1 = f1_score(ds.targets, preds, average="macro", zero_division=0)
    acc = np.mean(np.array(preds) == np.array(ds.targets))
    out = ROOT / "report" / "baseline.txt"
    text = f"Majority class index: {majority} ({ds.classes[majority]})\nmacro-F1: {macro_f1:.4f}\naccuracy: {acc:.4f}\n"
    out.write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
