# Local CPU-friendly training (use Colab/GPU for full accuracy)
Set-Location $PSScriptRoot\..
$py = ".\.venv\Scripts\python.exe"
& $py scripts/baseline.py
& $py model/train.py `
  --backbone mobilenetv3_small_100 `
  --img-size 192 `
  --batch-size 16 `
  --head-epochs 2 `
  --finetune-epochs 4 `
  --workers 0
& $py scripts/evaluate_holdout.py --split val
& $py scripts/evaluate_holdout.py --split holdout_lab_sample
& $py scripts/sync_report_metrics.py
$sample = Get-ChildItem -Recurse .\data\val -Include *.jpg,*.jpeg | Select-Object -First 1
if ($sample) { & $py model/predict.py --image $sample.FullName }
