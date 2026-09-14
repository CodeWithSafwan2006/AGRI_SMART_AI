# AgriSmart AI — Field Pathology & Microclimate Intelligence

AgriSmart AI is a grounded crop pathology diagnostic, atmospheric microclimate intelligence, and grower advisory platform. It enables farmers to upload leaf photography to detect plant pathogens with confidence scores, receive actionable agronomic precautionary advice, monitor microclimate metrics, and consult an AI Agronomy Advisor.

---

## 7.1 Required Repository Structure

```
├── README.md                 # Entry point documentation & system overview
├── app/                      # Source code (web application backend, auth, chatbot, weather intelligence)
│   ├── app.py                # Streamlit application entry point
│   ├── auth.py               # SQLite user authentication & profile management
│   ├── chatbot.py            # AI Agronomy Advisor & multi-lingual query handling
│   ├── weather.py            # Geocoding & microclimate weather intelligence
│   ├── precautions.py        # Agronomic protocols & disease treatment database
│   ├── crop_calendar.py     # Seasonal crop calendar & advisory rules
│   ├── pest_knowledge.py     # Pest identification & remedies database
│   └── validators.py         # Request validation & input sanitization
├── model/                    # ML training/inference code & Section 4.1 predict interface
│   ├── predict.py            # Standard predict interface & CLI evaluation
│   ├── train.py              # Model training pipeline & checkpointing
│   ├── model_def.py          # PyTorch model definitions & backbones (MobileNetV3 / EfficientNet)
│   ├── augmentation.py       # Computer vision augmentation pipelines
│   ├── export.py             # TorchScript / ONNX export utilities
│   ├── labels.py             # Class mappings (18 curated crop disease classes)
│   ├── config.py             # Model hyperparameter & metadata configuration
│   └── weights/              # Trained model checkpoints (best.pt)
├── report/                   # One-page model report & evaluation artifacts
│   ├── model_report.md       # Comprehensive 1-page model report
│   ├── baseline.txt          # Baseline evaluation benchmark metrics
│   ├── training_log.csv      # Per-epoch training & validation logs
│   └── val_classification_report.txt # Detailed holdout classification metrics
├── frontend/                 # Static web client (HTML5/CSS3/JavaScript)
│   ├── index.html            # Main Web UI dashboard
│   ├── style.css             # Vanilla CSS styling & design system
│   └── app.js                # Frontend state management & API integration
├── scripts/                  # Dataset curation, evaluation, & pipeline automation scripts
│   ├── test_model_inference.py # Unit tests for model inference
│   ├── curate_and_split.py   # Dataset partitioning & curation utility
│   ├── evaluate_holdout.py   # Model holdout validation script
│   └── run_pipeline.ps1      # Automated build & evaluation pipeline
├── server.py                 # FastAPI application server launcher
└── requirements.txt          # Environment dependencies specification
```

---

## 4.1 Model Predict Interface

The `/model` directory contains the required prediction module (`model/predict.py`) which exposes both a programmatic Python interface and a command-line interface.

### Python API Usage
```python
from model.predict import load_model, predict

# Load model weights (defaults to model/weights/best.pt)
model = load_model()

# Run inference on a target leaf specimen image
label, confidence = predict("path/to/leaf_specimen.jpg", model=model)

print(f"Diagnosed Pathology: {label}")
print(f"Confidence Score: {confidence:.2%}")
```

### CLI Inference Command
```powershell
python model/predict.py --image path/to/leaf_specimen.jpg --weights model/weights/best.pt
```

---

## 7.3 Model Report Summary

A complete one-page model report is located at [`report/model_report.md`](file:///d:/SIH2/report/model_report.md).

- **Task**: Multi-class crop leaf pathology identification from single RGB imagery across 18 curated plant disease & healthy baseline classes.
- **Architecture**: Lightweight MobileNetV3-Small / EfficientNet-B0 backbone fine-tuned with weighted cross-entropy sampling for class imbalance.
- **Performance**:
  - **Validation Macro-F1**: `0.8480`
  - **Validation Accuracy**: `84.72%`
  - **Baseline Comparison**: Outperforms majority-class baseline (Macro-F1 `0.0058`).
- **Known Limitations**: Model trained primarily on PlantVillage lab conditions; lighting and background variations in natural field captures may produce a generalization gap.

---

## Environment Setup & Clear Run Instructions

### 1. Prerequisites & Virtual Environment

Ensure Python 3.9+ is installed. Clone the repository and initialize a virtual environment:

```powershell
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\activate

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies

Install all required Python packages from `requirements.txt`:

```powershell
pip install -r requirements.txt
```

### 3. Environment Configuration (Optional)

Copy `.env.example` to `.env` to configure optional parameters (such as an OpenAI API key for advanced LLM agronomy rephrasing):

```powershell
copy .env.example .env
```

### 4. Running the Application Server & Web UI

Launch the FastAPI application server (serves REST endpoints and static Web UI):

```powershell
python server.py
```

Open your browser and navigate to:
👉 **`http://127.0.0.1:8000`**

### 5. Running the Alternative Streamlit App

You can also run the Streamlit dashboard interface:

```powershell
streamlit run app/app.py
```

### 6. Model Training & Evaluation (Optional)

To curate datasets, train models, or execute evaluation suites:

```powershell
# Curate PlantVillage dataset (18 classes)
python scripts/curate_and_split.py --source external/PlantVillage-Dataset/raw/color

# Train vision model
python model/train.py

# Evaluate model performance on validation holdout
python scripts/evaluate_holdout.py --split holdout_lab_sample
```
