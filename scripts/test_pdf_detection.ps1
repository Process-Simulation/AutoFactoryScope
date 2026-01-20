# Test PDF Detection on Factory Layouts
# Tests the API with actual PDF files

$ErrorActionPreference = "Stop"

param(
    [string]$PdfPath = "",
    [string]$ApiUrl = "http://localhost:8000"
)

Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host "  AutoFactoryScope - PDF Detection Test" -ForegroundColor Cyan
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host ""

# Check if API is running
Write-Host "Checking API availability..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$ApiUrl/health" -Method Get -ErrorAction Stop
    Write-Host "  API Status: $($health.status)" -ForegroundColor Green
    Write-Host "  Model Loaded: $($health.model_loaded)" -ForegroundColor $(if ($health.model_loaded) { "Green" } else { "Red" })
} catch {
    Write-Host "  ERROR: API not responding at $ApiUrl" -ForegroundColor Red
    Write-Host "  Please start the backend first: .\scripts\start_backend.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Get PDF path
if (-not $PdfPath) {
    Write-Host "Available test PDFs:" -ForegroundColor Cyan
    Write-Host "  1. OAK-B-01-8A-0001 (Base)" -ForegroundColor Gray
    Write-Host "  2. OHP-B-01-9X-0001 (PRO-IMP)" -ForegroundColor Gray
    Write-Host ""

    $choice = Read-Host "Select PDF (1 or 2)"

    if ($choice -eq "1") {
        $PdfPath = "C:\Users\georgem\source\repos\AutoFactoryScope_data\Layouts\OAK-B-01-8A-0001-26MY-P708-D-I- BASE_20250609.pdf"
    } elseif ($choice -eq "2") {
        $PdfPath = "C:\Users\georgem\source\repos\AutoFactoryScope_data\Layouts\OHP-B-01-9X-0001-26MY-V801-PRO-IMPBASE_20251014_27JPH 1.pdf"
    } else {
        Write-Host "Invalid choice" -ForegroundColor Red
        exit 1
    }
}

# Check PDF exists
if (-not (Test-Path $PdfPath)) {
    Write-Host "ERROR: PDF not found: $PdfPath" -ForegroundColor Red
    exit 1
}

$PdfName = Split-Path -Leaf $PdfPath
$PdfSize = (Get-Item $PdfPath).Length / 1MB

Write-Host "Testing PDF:" -ForegroundColor Cyan
Write-Host "  File: $PdfName" -ForegroundColor Gray
Write-Host "  Size: $([math]::Round($PdfSize, 2)) MB" -ForegroundColor Gray
Write-Host ""

# Upload and detect
Write-Host "Uploading to API..." -ForegroundColor Yellow

try {
    # Read PDF as bytes
    $pdfBytes = [System.IO.File]::ReadAllBytes($PdfPath)

    # Create multipart form data
    $boundary = [System.Guid]::NewGuid().ToString()
    $LF = "`r`n"

    $bodyLines = (
        "--$boundary",
        "Content-Disposition: form-data; name=`"file`"; filename=`"$PdfName`"",
        "Content-Type: application/pdf$LF",
        [System.Text.Encoding]::GetEncoding("iso-8859-1").GetString($pdfBytes),
        "--$boundary--$LF"
    ) -join $LF

    # Send request
    $response = Invoke-RestMethod `
        -Uri "$ApiUrl/detect?include_annotated=true" `
        -Method Post `
        -ContentType "multipart/form-data; boundary=$boundary" `
        -Body $bodyLines `
        -TimeoutSec 120

    Write-Host "Detection complete!" -ForegroundColor Green
    Write-Host ""

    # Display results
    Write-Host "===========================================================" -ForegroundColor Green
    Write-Host "  DETECTION RESULTS" -ForegroundColor Green
    Write-Host "===========================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Robots Detected: $($response.robot_count)" -ForegroundColor Cyan
    Write-Host "  Image Size: $($response.image_width) x $($response.image_height)" -ForegroundColor Gray
    Write-Host "  Processing Time: $([math]::Round($response.processing_time_ms, 2)) ms" -ForegroundColor Gray
    Write-Host ""

    if ($response.robot_count -gt 0) {
        Write-Host "Detected Robots:" -ForegroundColor Yellow
        $i = 1
        foreach ($detection in $response.detections) {
            Write-Host "  [$i] Confidence: $([math]::Round($detection.confidence * 100, 1))%" -ForegroundColor Gray
            Write-Host "      Position: ($([math]::Round($detection.x)), $([math]::Round($detection.y)))" -ForegroundColor Gray
            Write-Host "      Size: $([math]::Round($detection.width)) x $([math]::Round($detection.height))" -ForegroundColor Gray
            $i++
        }
    } else {
        Write-Host "No robots detected in this layout." -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "===========================================================" -ForegroundColor Green

    # Save annotated image if available
    if ($response.annotated_image) {
        $outputDir = "test_results"
        if (-not (Test-Path $outputDir)) {
            New-Item -ItemType Directory -Path $outputDir | Out-Null
        }

        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $outputPath = Join-Path $outputDir "detection_${timestamp}.png"

        # Decode base64 and save
        $imageBytes = [Convert]::FromBase64String($response.annotated_image)
        [System.IO.File]::WriteAllBytes($outputPath, $imageBytes)

        Write-Host ""
        Write-Host "Annotated image saved to: $outputPath" -ForegroundColor Cyan

        # Open image
        Write-Host "Opening image..." -ForegroundColor Gray
        Start-Process $outputPath
    }

} catch {
    Write-Host "ERROR during detection:" -ForegroundColor Red
    Write-Host "  $($_.Exception.Message)" -ForegroundColor Red

    if ($_.ErrorDetails.Message) {
        $errorDetail = $_.ErrorDetails.Message | ConvertFrom-Json
        Write-Host "  Code: $($errorDetail.error.code)" -ForegroundColor Yellow
        Write-Host "  Message: $($errorDetail.error.message)" -ForegroundColor Yellow
    }

    exit 1
}

Write-Host ""
Write-Host "Test complete!" -ForegroundColor Green
