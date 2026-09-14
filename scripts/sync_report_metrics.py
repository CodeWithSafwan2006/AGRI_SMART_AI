"""Copy best val metrics from training artifacts into model_report.md placeholders."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    log = ROOT / "report" / "training_log.csv"
    report = ROOT / "report" / "model_report.md"
    if not log.is_file():
        raise SystemExit("Missing training_log.csv — train first.")
    lines = log.read_text(encoding="utf-8").strip().splitlines()
    best_f1 = 0.0
    best_acc = 0.0
    for row in lines[1:]:
        parts = row.split(",")
        if len(parts) >= 5:
            f1 = float(parts[4])
            acc = float(parts[5]) if len(parts) > 5 else 0.0
            if f1 > best_f1:
                best_f1, best_acc = f1, acc
    baseline = ROOT / "report" / "baseline.txt"
    baseline_text = baseline.read_text(encoding="utf-8") if baseline.is_file() else "N/A"
    text = report.read_text(encoding="utf-8")
    text = re.sub(r"\| Macro-F1 \| _fill after train_ \| _fill after train_ \|", f"| Macro-F1 | {best_f1:.4f} | run evaluate_holdout |", text)
    text = re.sub(r"\| Accuracy \| _fill after train_ \| _fill after train_ \|", f"| Accuracy | {best_acc:.4f} | — |", text)
    if "_Majority-class" in text or "Majority-class baseline" in text:
        text = re.sub(
            r"_Majority-class predictor.*?here\._",
            baseline_text.strip().replace("\n", " "),
            text,
            flags=re.DOTALL,
        )
    report.write_text(text, encoding="utf-8")
    print(f"Updated report: val macro-F1={best_f1:.4f}")


if __name__ == "__main__":
    main()
