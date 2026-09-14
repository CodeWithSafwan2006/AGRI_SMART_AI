"""Train EfficientNet-B0 on curated PlantVillage classes. Saves best.pt by val macro-F1."""

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import torch
import torch.nn as nn
from sklearn.metrics import classification_report, confusion_matrix, f1_score
from torch.utils.data import DataLoader, WeightedRandomSampler
from torchvision import datasets, transforms

ROOT = Path(__file__).resolve().parents[1]
import sys

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from model.config import save_training_meta
from model.labels import CLASS_NAMES
from model.model_def import build_model, unfreeze_last_blocks

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


def train_transforms(img_size=224):
    return transforms.Compose(
        [
            transforms.RandomResizedCrop(img_size, scale=(0.7, 1.0)),
            transforms.RandomHorizontalFlip(),
            transforms.RandomVerticalFlip(p=0.3),
            transforms.RandomRotation(25),
            transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.3),
            transforms.RandomAffine(degrees=0, translate=(0.05, 0.05), shear=8),
            transforms.RandomPerspective(distortion_scale=0.2, p=0.3),
            transforms.GaussianBlur(kernel_size=3, sigma=(0.1, 1.0)),
            transforms.ToTensor(),
            transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
            transforms.RandomErasing(p=0.2),
        ]
    )


def val_transforms(img_size=224):
    return transforms.Compose(
        [
            transforms.Resize((img_size, img_size)),
            transforms.ToTensor(),
            transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
        ]
    )


def make_sampler(dataset: datasets.ImageFolder):
    targets = np.array(dataset.targets)
    class_counts = np.bincount(targets, minlength=len(dataset.classes))
    class_weights = 1.0 / np.maximum(class_counts, 1)
    sample_weights = class_weights[targets]
    return WeightedRandomSampler(sample_weights, num_samples=len(sample_weights), replacement=True)


@torch.no_grad()
def evaluate(model, loader, device):
    model.eval()
    all_preds, all_labels = [], []
    total_loss = 0.0
    criterion = nn.CrossEntropyLoss()
    for x, y in loader:
        x, y = x.to(device), y.to(device)
        logits = model(x)
        total_loss += criterion(logits, y).item() * x.size(0)
        preds = logits.argmax(dim=1)
        all_preds.extend(preds.cpu().tolist())
        all_labels.extend(y.cpu().tolist())
    macro_f1 = f1_score(all_labels, all_preds, average="macro", zero_division=0)
    acc = np.mean(np.array(all_preds) == np.array(all_labels))
    return total_loss / len(loader.dataset), macro_f1, acc, all_labels, all_preds


def run_epoch(model, loader, optimizer, device, train=True):
    model.train(train)
    criterion = nn.CrossEntropyLoss()
    total_loss = 0.0
    for x, y in loader:
        x, y = x.to(device), y.to(device)
        if train:
            optimizer.zero_grad()
        logits = model(x)
        loss = criterion(logits, y)
        if train:
            loss.backward()
            optimizer.step()
        total_loss += loss.item() * x.size(0)
    return total_loss / len(loader.dataset)


def save_confusion_matrix(y_true, y_pred, class_names, out_path):
    cm = confusion_matrix(y_true, y_pred, labels=list(range(len(class_names))))
    plt.figure(figsize=(12, 10))
    sns.heatmap(cm, xticklabels=class_names, yticklabels=class_names, annot=False, fmt="d", cmap="Blues")
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.xticks(rotation=90, fontsize=7)
    plt.yticks(rotation=0, fontsize=7)
    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, default=ROOT / "data")
    parser.add_argument("--backbone", default="efficientnet_b0")
    parser.add_argument("--img-size", type=int, default=224)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--head-epochs", type=int, default=3)
    parser.add_argument("--finetune-epochs", type=int, default=6)
    parser.add_argument("--lr-head", type=float, default=1e-3)
    parser.add_argument("--lr-finetune", type=float, default=1e-4)
    parser.add_argument("--workers", type=int, default=2)
    args = parser.parse_args()

    train_dir = args.data_root / "train"
    val_dir = args.data_root / "val"
    if not train_dir.is_dir():
        raise SystemExit(f"Missing {train_dir}. Run scripts/curate_and_split.py first.")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    train_ds = datasets.ImageFolder(str(train_dir), transform=train_transforms(args.img_size))
    val_ds = datasets.ImageFolder(str(val_dir), transform=val_transforms(args.img_size))

    if train_ds.classes != CLASS_NAMES:
        print("Warning: folder class order differs from labels.py")
        print("Train folders:", train_ds.classes)

    sampler = make_sampler(train_ds)
    pin = torch.cuda.is_available()
    train_loader = DataLoader(
        train_ds, batch_size=args.batch_size, sampler=sampler, num_workers=args.workers, pin_memory=pin
    )
    val_loader = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False, num_workers=args.workers)

    model = build_model(len(train_ds.classes), backbone=args.backbone, pretrained=True).to(device)
    for p in model.parameters():
        p.requires_grad = False
    classifier = model.get_classifier() if hasattr(model, "get_classifier") else model.classifier
    for p in classifier.parameters():
        p.requires_grad = True

    weights_dir = ROOT / "model" / "weights"
    weights_dir.mkdir(parents=True, exist_ok=True)
    log_path = ROOT / "report" / "training_log.csv"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    best_f1 = -1.0
    rows = []

    def train_phase(epochs, lr, phase_name, use_scheduler=False):
        nonlocal best_f1, model
        optimizer = torch.optim.AdamW(filter(lambda p: p.requires_grad, model.parameters()), lr=lr, weight_decay=1e-4)
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=lr * 0.1) if use_scheduler else None
        for epoch in range(1, epochs + 1):
            tr_loss = run_epoch(model, train_loader, optimizer, device, train=True)
            val_loss, macro_f1, acc, _, _ = evaluate(model, val_loader, device)
            if scheduler:
                scheduler.step()
            row = {
                "phase": phase_name,
                "epoch": epoch,
                "train_loss": tr_loss,
                "val_loss": val_loss,
                "val_macro_f1": macro_f1,
                "val_accuracy": acc,
            }
            rows.append(row)
            print(f"[{phase_name}] epoch {epoch}/{epochs}  loss={tr_loss:.4f}  val_f1={macro_f1:.4f}  acc={acc:.4f}")
            if macro_f1 > best_f1:
                best_f1 = macro_f1
                torch.save(model.state_dict(), weights_dir / "best.pt")

    train_phase(args.head_epochs, args.lr_head, "head", use_scheduler=False)
    unfreeze_last_blocks(model, args.backbone)
    train_phase(args.finetune_epochs, args.lr_finetune, "finetune", use_scheduler=True)

    with open(log_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    # Load best saved checkpoint for final evaluation report
    if (weights_dir / "best.pt").is_file():
        model.load_state_dict(torch.load(weights_dir / "best.pt", map_location=device, weights_only=True))

    _, macro_f1, acc, y_true, y_pred = evaluate(model, val_loader, device)
    report = classification_report(y_true, y_pred, target_names=val_ds.classes, zero_division=0)
    report_path = ROOT / "report" / "val_classification_report.txt"
    report_path.write_text(report, encoding="utf-8")
    save_confusion_matrix(y_true, y_pred, val_ds.classes, ROOT / "report" / "assets" / "confusion_matrix_val.png")
    save_training_meta(args.backbone, args.img_size)
    print(f"\nFinal Best val macro-F1: {best_f1:.4f} (Accuracy: {acc:.4f})")
    print(report)


if __name__ == "__main__":
    main()
