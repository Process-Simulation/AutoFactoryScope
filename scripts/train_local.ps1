# Train YOLO11 Locally on Your Quadro P4000 GPU
# No Colab needed!

$ErrorActionPreference = "Stop"

Write-Host "╔══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║      AutoFactoryScope - Local GPU Training          ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

# Check GPU
Write-Host "[1/6] Checking GPU..." -ForegroundColor Yellow
$GPU = nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>&1
if ($GPU -match "Quadro P4000") {
    Write-Host "  ✓ GPU: $GPU" -ForegroundColor Green
} else {
    Write-Host "  ⚠ GPU not detected. Training will be SLOW on CPU." -ForegroundColor Yellow
}

# Activate backend venv
Write-Host "`n[2/6] Activating Python environment..." -ForegroundColor Yellow
$VenvPath = "src\backend\autofactoryscope_api\.venv\Scripts\Activate.ps1"
& $VenvPath
Write-Host "  ✓ Virtual environment activated" -ForegroundColor Green

# Install ultralytics
Write-Host "`n[3/6] Installing Ultralytics YOLO11..." -ForegroundColor Yellow
$HasUltralytics = python -c "import ultralytics; print('OK')" 2>&1
if ($HasUltralytics -notmatch "OK") {
    Write-Host "  Installing ultralytics + torch..." -ForegroundColor Gray
    pip install ultralytics torch torchvision -q
    Write-Host "  ✓ Ultralytics installed" -ForegroundColor Green
} else {
    Write-Host "  ✓ Ultralytics already installed" -ForegroundColor Green
}

# Prepare dataset
Write-Host "`n[4/6] Preparing dataset..." -ForegroundColor Yellow

# Use local extracted dataset from Downloads
$DatasetSource = "C:\Users\georgem\Downloads\robot_detection_layouts.v2i.yolov8 (1)"
$DatasetDest = "datasets\v2_local_training"

if (-not (Test-Path $DatasetSource)) {
    Write-Host "  ✗ Dataset not found: $DatasetSource" -ForegroundColor Red
    Write-Host "    Please verify the dataset location." -ForegroundColor Gray
    exit 1
}

# Copy to repo datasets folder for training
Write-Host "  Copying dataset to training location..." -ForegroundColor Gray
if (Test-Path $DatasetDest) {
    Remove-Item $DatasetDest -Recurse -Force
}
Copy-Item $DatasetSource -Destination $DatasetDest -Recurse

Write-Host "  ✓ Dataset ready: $DatasetDest" -ForegroundColor Green

# Fix data.yaml paths
Write-Host "`n[5/6] Configuring data.yaml..." -ForegroundColor Yellow

$DataYamlPath = "$DatasetDest\data.yaml"
$DataYamlContent = Get-Content $DataYamlPath -Raw

# Update paths to absolute
$AbsDatasetPath = (Resolve-Path $DatasetDest).Path
$DataYamlContent = $DataYamlContent -replace "train: ../train/images", "train: $AbsDatasetPath\train\images"
$DataYamlContent = $DataYamlContent -replace "val: ../valid/images", "val: $AbsDatasetPath\valid\images"
$DataYamlContent = $DataYamlContent -replace "test: ../test/images", "test: $AbsDatasetPath\test\images"

$DataYamlContent | Set-Content $DataYamlPath -Encoding UTF8

Write-Host "  ✓ data.yaml configured" -ForegroundColor Green

# Start training
Write-Host "`n[6/6] Starting training..." -ForegroundColor Yellow
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║              TRAINING IN PROGRESS                    ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "Configuration:" -ForegroundColor Gray
Write-Host "  Dataset: v2 (138 images)" -ForegroundColor Gray
Write-Host "  Model: YOLO11n (nano)" -ForegroundColor Gray
Write-Host "  Epochs: 50" -ForegroundColor Gray
Write-Host "  Image Size: 512x512" -ForegroundColor Gray
Write-Host "  Batch Size: 8 (safe for 8GB GPU)" -ForegroundColor Gray
Write-Host "  Device: GPU (Quadro P4000)" -ForegroundColor Gray
Write-Host ""
Write-Host "Estimated time: 20-30 minutes" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop training (NOT recommended)" -ForegroundColor Gray
Write-Host ""

# Convert path to forward slashes (Python handles this on Windows)
$DataYamlPathForPython = $DataYamlPath -replace '\\', '/'

$TrainingScript = @"
from ultralytics import YOLO
from pathlib import Path
import torch

if __name__ == '__main__':
    # Verify GPU
    print(f'CUDA available: {torch.cuda.is_available()}')
    if torch.cuda.is_available():
        print(f'GPU: {torch.cuda.get_device_name(0)}')
        print(f'GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB')

    # Load YOLO11 nano model
    print('\nLoading YOLO11n...')
    model = YOLO('yolo11n.pt')

    # Train
    print('\nStarting training...\n')
    results = model.train(
        data='$DataYamlPathForPython',
        epochs=50,
        imgsz=512,
        batch=8,  # Safe for 8GB GPU

        # Augmentation
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
        degrees=10.0,
        translate=0.1,
        scale=0.5,
        flipud=0.5,
        fliplr=0.5,
        mosaic=1.0,

        # Optimizer
        optimizer='AdamW',
        lr0=0.001,
        warmup_epochs=3,

        # Settings
        patience=10,
        save=True,
        save_period=10,
        cache=True,
        device=0,  # GPU
        workers=4,
        project='runs/train',
        name='robot_detector_local',
        exist_ok=True,
        verbose=True
    )

    # Validate
    print('\n\nValidating model...')
    metrics = model.val()

    print('\n' + '='*60)
    print('TRAINING COMPLETE!')
    print('='*60)
    print(f'mAP50:     {metrics.box.map50:.3f}')
    print(f'mAP50-95:  {metrics.box.map:.3f}')
    print(f'Precision: {metrics.box.p.mean():.3f}')
    print(f'Recall:    {metrics.box.r.mean():.3f}')
    print('='*60)

    # Copy best model to models folder
    import shutil
    # The actual path includes 'detect/runs' subdirectories
    best_model = Path('runs/detect/runs/train/robot_detector_local/weights/best.pt')
    dest_model = Path('models/best.pt')
    dest_model.parent.mkdir(exist_ok=True)
    shutil.copy(best_model, dest_model)

    print(f'\n✓ Best model saved to: {dest_model}')
    print('\nNext steps:')
    print('  1. Run: .\\scripts\\export_onnx.ps1')
    print('  2. Run: .\\scripts\\start_backend.ps1')
    print('  3. Test your model!')
"@

# Save training script to temporary file (required for multiprocessing on Windows)
$TempScriptPath = "datasets\v2_local_training\train_script.py"
$TrainingScript | Set-Content $TempScriptPath -Encoding UTF8

# Run training
python $TempScriptPath

# Clean up
Remove-Item $TempScriptPath -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║         ✓ TRAINING COMPLETE!                         ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

deactivate
