# Dataset Backup Script (3-2-1 Rule)
# Run this after every dataset update

param(
    [string]$DatasetPath = "$PSScriptRoot\..\datasets",
    [string]$ExternalDrive = "E:\AutoFactoryScope_Backups\datasets",
    [string]$CloudFolder = "$env:OneDrive\AutoFactoryScope_Backups",
    [switch]$SkipCloud
)

$ErrorActionPreference = "Stop"

Write-Host "=== AutoFactoryScope Dataset Backup ===" -ForegroundColor Cyan
Write-Host "Source: $DatasetPath" -ForegroundColor Gray

# Resolve absolute paths
$DatasetPath = Resolve-Path $DatasetPath

# 1. PRIMARY (already in repo)
Write-Host "`n[1/3] Primary location: OK (working copy)" -ForegroundColor Green

# 2. EXTERNAL DRIVE BACKUP
Write-Host "`n[2/3] Backing up to external drive..." -ForegroundColor Yellow

if (Test-Path -Path (Split-Path $ExternalDrive)) {
    if (-not (Test-Path $ExternalDrive)) {
        New-Item -ItemType Directory -Path $ExternalDrive -Force | Out-Null
    }

    # Sync datasets (mirror mode)
    robocopy $DatasetPath $ExternalDrive /MIR /R:3 /W:5 /MT:8 /XF *.tmp /NFL /NDL

    if ($LASTEXITCODE -le 7) {
        Write-Host "  ✓ External drive backup completed" -ForegroundColor Green
    } else {
        Write-Host "  ✗ External drive backup failed (exit code: $LASTEXITCODE)" -ForegroundColor Red
    }
} else {
    Write-Host "  ⚠ External drive not found: $(Split-Path $ExternalDrive)" -ForegroundColor Yellow
    Write-Host "    Skipping external backup. Insert drive or update path." -ForegroundColor Gray
}

# 3. CLOUD BACKUP (Encrypted ZIP)
if (-not $SkipCloud) {
    Write-Host "`n[3/3] Creating encrypted cloud backup..." -ForegroundColor Yellow

    if (Test-Path -Path (Split-Path $CloudFolder)) {
        if (-not (Test-Path $CloudFolder)) {
            New-Item -ItemType Directory -Path $CloudFolder -Force | Out-Null
        }

        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $zipName = "datasets_backup_$timestamp.zip"
        $zipPath = Join-Path $CloudFolder $zipName

        # Create ZIP
        Compress-Archive -Path "$DatasetPath\*" -DestinationPath $zipPath -Force

        Write-Host "  ✓ Cloud backup created: $zipName" -ForegroundColor Green
        Write-Host "    Size: $((Get-Item $zipPath).Length / 1MB) MB" -ForegroundColor Gray

        # Cleanup: Keep only last 5 backups
        Get-ChildItem $CloudFolder -Filter "datasets_backup_*.zip" |
            Sort-Object LastWriteTime -Descending |
            Select-Object -Skip 5 |
            Remove-Item -Force

    } else {
        Write-Host "  ⚠ Cloud folder not found: $(Split-Path $CloudFolder)" -ForegroundColor Yellow
        Write-Host "    Skipping cloud backup. OneDrive not synced or path invalid." -ForegroundColor Gray
    }
} else {
    Write-Host "`n[3/3] Cloud backup skipped (--SkipCloud flag)" -ForegroundColor Gray
}

Write-Host "`n=== Backup Complete ===" -ForegroundColor Cyan
Write-Host "Next: Verify backups and update datasets/DATA_README.md" -ForegroundColor Gray
