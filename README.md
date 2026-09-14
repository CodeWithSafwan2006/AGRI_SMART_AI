# AgriSmart AI

Crop disease detection for farmers: upload a leaf photo, get a disease label with confidence, precautionary guidance, weather-based tips, and a grounded chatbot explanation.

## Modules built

| Module | Status |
|--------|--------|
| **Core** — disease detection + precautions + web UI | Yes |
| **Bonus C** — weather intelligence ([Open-Meteo](https://open-meteo.com/)) | Yes |
| **Bonus E** — farmer chatbot (template + optional OpenAI paraphrase) | Yes |
| Bonus A, B, D, F, G | **Not built** (24h scope) |

## Step-by-step execution (24h roadmap)

Run from `D:\SIH2` in PowerShell.

**Step 0 — Environment**

```powershell
py -3 -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
git init
```

**Step 1 — PlantVillage dataset**

```powershell
git clone --depth 1 https://github.com/spMohanty/PlantVillage-Dataset.git external/PlantVillage-Dataset
```

Or run the full automated chain:

```powershell
.\scripts\run_pipeline.ps1
```

**Step 2 — Curate 18 classes + 80/10/10 split**

```powershell
# Full dataset (submission):
.\.venv\Scripts\python scripts/curate_and_split.py --source external/PlantVillage-Dataset/raw/color
# Fast local dev (120 images/class — already used if you followed agent setup):
.\.venv\Scripts\python scripts/curate_and_split.py --source external/PlantVillage-Dataset/raw/color --max-per-class 120
```

**Step 3 — Baseline (for report)**

```powershell
.\.venv\Scripts\python scripts/baseline.py
```

**Step 4 — Train** (GPU recommended; Colab T4 ~1–2 h)

```powershell
.\scripts\train_local.ps1
# Or full EfficientNet on GPU:
.\.venv\Scripts\python model/train.py
```

**Step 5 — Evaluate + sync report**

```powershell
.\.venv\Scripts\python scripts/evaluate_holdout.py --split val
.\.venv\Scripts\python scripts/evaluate_holdout.py --split holdout_lab_sample
.\.venv\Scripts\python scripts/sync_report_metrics.py
```

**Step 6 — CLI smoke test (judging interface)**

```powershell
.\.venv\Scripts\python model/predict.py --image path\to\leaf.jpg
```

**Step 7 — Web UI** (custom field-diary layout per product design)

```powershell
.\.venv\Scripts\streamlit run app/app.py
```

**Step 8 — Demo video + optional Streamlit Cloud deploy**

**Step 9 — Repro check:** fresh venv, `pip install`, `predict.py` + Streamlit in under ~10 minutes (weights present).

## Setup (short)

```powershell
cd D:\SIH2
py -3 -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env   # optional OPENAI_API_KEY for chatbot paraphrase
```

## Dataset

- [spMohanty/PlantVillage-Dataset](https://github.com/spMohanty/PlantVillage-Dataset) — `raw/color` only, 18 curated classes in `model/labels.py`.
- Train on lab images; organizer field set is separate — document the lab→field gap in `report/model_report.md`.

## Metrics

| Metric | Value |
|--------|-------|
| Val macro-F1 | see `report/training_log.csv` / `report/model_report.md` |
| Val accuracy | same |
| Baseline macro-F1 | `report/baseline.txt` |

Confusion matrix: [report/assets/confusion_matrix_val.png](report/assets/confusion_matrix_val.png) (after training)

## Architecture

- **Vision:** EfficientNet-B0 (`timm`), weighted sampling, val macro-F1 checkpoint.
- **Weather:** Open-Meteo geocoding + hourly forecast heuristics.
- **UI:** Streamlit + `app/theme.py` — Lora + IBM Plex Sans, monsoon field palette (not generic SaaS cards).
- **Chatbot:** Grounded templates (EN/HI/GU); optional LLM rephrases only provided facts.

## Demo & deployment

- Demo video: _YouTube unlisted link_
- Live app: _Streamlit Community Cloud / Hugging Face Spaces_

## Originality

- Internal 24h execution roadmap; PlantVillage citation above.
- _List tutorials/notebooks referenced during training._

## Layout

```
README.md
requirements.txt
app/app.py
app/theme.py
model/predict.py
model/train.py
model/weights/best.pt
report/model_report.md
scripts/
```
