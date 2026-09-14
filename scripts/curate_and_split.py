"""
Copy selected PlantVillage raw/color classes into stratified 80/10/10 splits.

Usage:
  python scripts/curate_and_split.py --source external/PlantVillage-Dataset/raw/color
"""

import argparse
import random
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT))
from model.labels import CLASS_NAMES, SOURCE_DIR_BY_CLASS


def list_images(folder: Path):
    seen = set()
    out = []
    for ext in ("*.jpg", "*.jpeg", "*.png", "*.JPG", "*.JPEG", "*.PNG"):
        for p in folder.glob(ext):
            key = str(p.resolve()).lower()
            if key not in seen:
                seen.add(key)
                out.append(p)
    return out


def stratified_split(files, train_ratio=0.8, val_ratio=0.1, seed=42):
    rng = random.Random(seed)
    files = list(files)
    rng.shuffle(files)
    n = len(files)
    n_train = int(n * train_ratio)
    n_val = int(n * val_ratio)
    train = files[:n_train]
    val = files[n_train : n_train + n_val]
    holdout = files[n_train + n_val :]
    return train, val, holdout


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True, help="PlantVillage raw/color directory")
    parser.add_argument("--data-root", type=Path, default=ROOT / "data")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-per-class", type=int, default=0, help="Cap images per class (0 = all)")
    args = parser.parse_args()

    if not args.source.is_dir():
        raise SystemExit(f"Source not found: {args.source}")

    for split in ("train", "val", "holdout_lab_sample"):
        split_dir = args.data_root / split
        if split_dir.exists():
            shutil.rmtree(split_dir)

    for class_name in CLASS_NAMES:
        src_name = SOURCE_DIR_BY_CLASS.get(class_name, class_name)
        src = args.source / src_name
        if not src.is_dir():
            print(f"SKIP missing class folder: {src}", flush=True)
            continue
        images = list_images(src)
        if args.max_per_class and len(images) > args.max_per_class:
            random.Random(args.seed).shuffle(images)
            images = images[: args.max_per_class]
        tr, va, ho = stratified_split(images, seed=args.seed)
        for subset, split_name in ((tr, "train"), (va, "val"), (ho, "holdout_lab_sample")):
            dest = args.data_root / split_name / class_name
            dest.mkdir(parents=True, exist_ok=True)
            for img in subset:
                shutil.copy2(img, dest / img.name)
        print(f"{class_name}: {len(images)} images -> train {len(tr)} val {len(va)} holdout {len(ho)}", flush=True)

    print("Done. Splits under", args.data_root, flush=True)


if __name__ == "__main__":
    main()
