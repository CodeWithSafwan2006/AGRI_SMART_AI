# AgriSmart — run in order (PowerShell)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

$py = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $py)) {
    py -3 -m venv .venv
    .\.venv\Scripts\pip install -r requirements.txt
}

$pv = ".\external\PlantVillage-Dataset\raw\color"
if (-not (Test-Path $pv)) {
    Write-Host "Step 1: Clone PlantVillage (large download)..."
    New-Item -ItemType Directory -Force -Path external | Out-Null
    git clone --depth 1 https://github.com/spMohanty/PlantVillage-Dataset.git external/PlantVillage-Dataset
}

Write-Host "Step 2: Curate classes + split..."
& $py scripts/curate_and_split.py --source $pv

Write-Host "Step 3: Baseline..."
& $py scripts/baseline.py

Write-Host "Step 4: Train (GPU recommended)..."
& $py model/train.py @args

Write-Host "Step 5: Holdout eval..."
& $py scripts/evaluate_holdout.py --split holdout_lab_sample

Write-Host "Step 6: Smoke predict on one val image..."
$sample = Get-ChildItem -Recurse .\data\val -Include *.jpg,*.JPG,*.jpeg | Select-Object -First 1
if ($sample) { & $py model/predict.py --image $sample.FullName }

Write-Host "Done. Launch UI: python server.py"
