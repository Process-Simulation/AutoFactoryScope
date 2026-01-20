# Production Deployment Runbook (Windows, No Docker)

**Environment**: Windows Server or Windows 10/11 Pro

**Goal**: Deploy AutoFactoryScope API as a persistent Windows service.

---

## Deployment Options

### Option 1: NSSM (Recommended) ⭐

**Pros:**
- GUI + CLI configuration
- Automatic restart on failure
- Easy log management
- Windows Event Log integration

**Installation:**

```powershell
# Download NSSM
# https://nssm.cc/download

# Extract to C:\Tools\nssm

# Add to PATH
$env:Path += ";C:\Tools\nssm\win64"

# Install service
cd C:\Users\georgem\source\repos\AutoFactoryScope\src\backend\autofactoryscope_api

nssm install AutoFactoryScope `
    "C:\Users\georgem\source\repos\AutoFactoryScope\src\backend\autofactoryscope_api\.venv\Scripts\python.exe" `
    "-m uvicorn autofactoryscope_api.main:app --host 0.0.0.0 --port 8000"

# Set working directory
nssm set AutoFactoryScope AppDirectory "C:\Users\georgem\source\repos\AutoFactoryScope\src\backend\autofactoryscope_api"

# Set environment variables
nssm set AutoFactoryScope AppEnvironmentExtra "AFS_LOG_LEVEL=INFO" "AFS_MODEL_PATH=C:\Users\georgem\source\repos\AutoFactoryScope\models\robot_detector.onnx"

# Set stdout/stderr logging
nssm set AutoFactoryScope AppStdout "C:\Logs\AutoFactoryScope\stdout.log"
nssm set AutoFactoryScope AppStderr "C:\Logs\AutoFactoryScope\stderr.log"

# Start service
nssm start AutoFactoryScope

# Check status
nssm status AutoFactoryScope
```

**Management:**

```powershell
# Stop service
nssm stop AutoFactoryScope

# Restart service
nssm restart AutoFactoryScope

# Remove service
nssm remove AutoFactoryScope confirm
```

---

### Option 2: Windows Task Scheduler

**Pros:**
- Built-in (no downloads)
- Simple setup

**Cons:**
- Less robust than NSSM
- Manual restart on failure

**Setup:**

```powershell
# Create startup script
$StartupScript = @"
cd C:\Users\georgem\source\repos\AutoFactoryScope\src\backend\autofactoryscope_api
.\.venv\Scripts\Activate.ps1
uvicorn autofactoryscope_api.main:app --host 0.0.0.0 --port 8000
"@

$StartupScript | Out-File -FilePath "C:\AutoFactoryScope\start_api.ps1"

# Create scheduled task
$Action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-File C:\AutoFactoryScope\start_api.ps1"
$Trigger = New-ScheduledTaskTrigger -AtStartup
$Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -RunLevel Highest
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)

Register-ScheduledTask -TaskName "AutoFactoryScope API" -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings

# Start task
Start-ScheduledTask -TaskName "AutoFactoryScope API"
```

---

### Option 3: pythonw.exe (Background Process)

**Pros:**
- No installation required
- Simple for development

**Cons:**
- No auto-restart
- No service management

**Usage:**

```powershell
# Create startup shortcut
$WScript = New-Object -ComObject WScript.Shell
$Shortcut = $WScript.CreateShortcut("C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp\AutoFactoryScope.lnk")
$Shortcut.TargetPath = "C:\Users\georgem\source\repos\AutoFactoryScope\src\backend\autofactoryscope_api\.venv\Scripts\pythonw.exe"
$Shortcut.Arguments = "-m uvicorn autofactoryscope_api.main:app --host 0.0.0.0 --port 8000"
$Shortcut.WorkingDirectory = "C:\Users\georgem\source\repos\AutoFactoryScope\src\backend\autofactoryscope_api"
$Shortcut.Save()
```

---

## Performance Optimization

### 1. ONNX Runtime Session Reuse

Already implemented in [inference.py:264-285](../src/backend/autofactoryscope_api/inference.py#L264-L285).

**Key**: Global model instance ensures session is loaded once and reused.

---

### 2. Parallel Tile Inference

**Current**: Sequential tile processing
**Improvement**: Parallel processing with `asyncio` + threadpool

**Example** (to implement):

```python
# In inference.py

import asyncio
from concurrent.futures import ThreadPoolExecutor

async def predict_tiles_parallel(
    self,
    tiling_result: TilingResult,
    max_workers: int = 4,
) -> list[Detection]:
    """Run inference on all tiles in parallel."""
    loop = asyncio.get_event_loop()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        tasks = [
            loop.run_in_executor(executor, self.predict, tile.data)
            for tile in tiling_result.tiles
        ]

        tile_results = await asyncio.gather(*tasks)

    # Merge results (same as sequential)
    all_detections = []
    for tile, detections in zip(tiling_result.tiles, tile_results):
        for det in detections:
            global_bbox = tile_bbox_to_global(tile, det.bbox)
            all_detections.append(Detection(...))

    return all_detections
```

**Expected Speedup**: 2-4x on 4-core CPU.

---

### 3. INT8 Quantization (Optional)

**Goal**: Reduce model size and increase inference speed (~2x).

**Trade-off**: Slight accuracy drop (<1% mAP typically).

**Script** (`scripts/quantize_int8.py`):

```python
import onnx
from onnxruntime.quantization import quantize_dynamic, QuantType

model_fp32 = 'models/robot_detector.onnx'
model_int8 = 'models/robot_detector_int8.onnx'

quantize_dynamic(
    model_fp32,
    model_int8,
    weight_type=QuantType.QUInt8,
    optimize_model=True,
)

print(f"Quantized model saved: {model_int8}")

# Validate accuracy (compare mAP before/after)
# ... (run validation dataset through both models)
```

**Usage**: Update `config.py` to point to `robot_detector_int8.onnx`.

---

## Monitoring

### Health Check

```powershell
# Check if API is running
curl http://localhost:8000/health

# Expected response:
# {"status": "healthy", "model_loaded": true, "uptime_seconds": 123.45}
```

### Metrics

```powershell
# Prometheus metrics
curl http://localhost:8000/metrics

# Key metrics:
# - inference_duration_seconds (histogram)
# - detection_count_total (counter)
# - http_requests_total (counter)
```

### Logs

```powershell
# View logs (NSSM)
Get-Content C:\Logs\AutoFactoryScope\stdout.log -Tail 50 -Wait

# View logs (structlog JSON)
Get-Content C:\Logs\AutoFactoryScope\stdout.log | jq '.level, .event, .duration_ms'
```

---

## Backup & Recovery

### Model Backup

```powershell
# Backup current model before updating
Copy-Item models\robot_detector.onnx models\robot_detector_$(Get-Date -Format 'yyyyMMdd_HHmmss').onnx.bak

# Restore if needed
Copy-Item models\robot_detector_20260120_123456.onnx.bak models\robot_detector.onnx

# Restart service
nssm restart AutoFactoryScope
```

### Dataset Backup

See [../datasets/DATA_README.md](../datasets/DATA_README.md) for 3-2-1 backup strategy.

---

## Troubleshooting

### Service Won't Start

```powershell
# Check NSSM logs
Get-Content C:\Logs\AutoFactoryScope\stderr.log

# Common issues:
# 1. Model file not found → Check AFS_MODEL_PATH
# 2. Port 8000 in use → Change port or kill process
# 3. venv not activated → Check AppDirectory and exe path
```

### Slow Inference

```powershell
# Check tile size (smaller = slower but more detections)
# Edit config: AFS_TILE_SIZE=640 (default: 512)

# Check overlap (more overlap = more tiles)
# Edit config: AFS_TILE_OVERLAP=0.05 (default: 0.1)

# Enable INT8 quantization (see above)
```

### High Memory Usage

```powershell
# Limit concurrent requests (FastAPI)
# Add to main.py:
# app.state.limiter = Limiter(max_concurrency=2)

# Reduce tile batch size (if implementing parallel inference)
```

---

## Security

### Network Access

```powershell
# Restrict to localhost only (dev)
uvicorn autofactoryscope_api.main:app --host 127.0.0.1 --port 8000

# Allow LAN access (prod)
uvicorn autofactoryscope_api.main:app --host 0.0.0.0 --port 8000

# Firewall rule
New-NetFirewallRule -DisplayName "AutoFactoryScope API" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

### Authentication

**Current**: None (internal tool)

**Future**: Add API key middleware

```python
# middleware.py
async def api_key_middleware(request: Request, call_next):
    api_key = request.headers.get("X-API-Key")
    if api_key != settings.api_key:
        raise HTTPException(401, "Invalid API key")
    return await call_next(request)
```

---

## Updates

### Updating Model

1. Train new model
2. Export to ONNX
3. Backup old model
4. Replace `models/robot_detector.onnx`
5. Restart service
6. Validate with test images

### Updating Code

```powershell
# Pull changes
git pull origin main

# Update dependencies
cd src\backend\autofactoryscope_api
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt --upgrade

# Restart service
nssm restart AutoFactoryScope
```

---

**Last Updated**: 2026-01-20
