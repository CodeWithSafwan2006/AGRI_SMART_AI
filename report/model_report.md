# AgriSmart AI — Model Report

## Task

Multi-class crop leaf disease classification from single RGB images, with precautionary guidance, weather-aware tips, and a grounded farmer chatbot in the web UI.

## Dataset & split

- **Source:** [PlantVillage Dataset](https://github.com/spMohanty/PlantVillage-Dataset) (`raw/color` only).
- **Classes:** 18 curated classes (tomato, potato, corn, apple, grape, bell pepper diseases + healthy).
- **Split:** Stratified by class — 80% train, 10% validation, 10% lab holdout (`holdout_lab_sample`).
- **Note:** Organizers’ field test set is separate; this model is trained on lab-style images and may underperform on field photos.

## Model / approach

- **Backbone:** EfficientNet-B0 (`timm`), ImageNet pretrained.
- **Training:** Freeze backbone → train classifier head (3 epochs) → unfreeze last blocks and fine-tune (6 epochs).
- **Loss / sampling:** Cross-entropy with `WeightedRandomSampler` for class imbalance.
- **Selection metric:** Best checkpoint by **validation macro-F1** (`model/weights/best.pt`).
- **Augmentation:** Random resized crop, flips, rotation, color jitter, affine/perspective, blur, random erasing.

## Metric & result

| Metric | Validation | Lab holdout |
|--------|------------|-------------|
| Macro-F1 | 0.8480 | ~0.85 (dev subset) |
| Accuracy | 0.8472 | ~0.85 (dev subset) |

_Dev subset: 120 images/class, MobileNetV3-Small @ 192px. Re-curate without `--max-per-class` and train EfficientNet on GPU for final submission._

- Per-class precision/recall: see `report/val_classification_report.txt` after training.
- Confusion matrix: `report/assets/confusion_matrix_val.png`

## Baseline

**Majority-class baseline** (validation, 120-img/class subset): macro-F1 **0.0058**, accuracy **0.0556** — see `report/baseline.txt`.

## Limitations

- Trained on PlantVillage lab images; expected **generalization gap** on field captures (lighting, background, partial leaves).
- Weather advice uses Open-Meteo forecast heuristics, not agronomic models.
- Chatbot is grounded in detection + rules; optional LLM only paraphrases provided facts.
