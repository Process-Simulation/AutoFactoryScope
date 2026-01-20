# Docker-Free Annotation Tools for Windows

**Requirement**: Replace CVAT (Docker-only) with Windows-native labeling tools.

---

## Recommended Tools

### 1️⃣ Label Studio (RECOMMENDED) ⭐

**Why:**
- ✅ pip-installable (no Docker)
- ✅ Modern web UI (runs locally)
- ✅ YOLO export format built-in
- ✅ Supports bounding boxes, polygons, keypoints
- ✅ Pre-labeling support (import model predictions)
- ✅ Active development (2024+)

**Limitations:**
- ❌ No native OBB (oriented bounding box) support
- ⚠️ Requires Python 3.8-3.11 (not 3.12+ yet)

**Installation:**

```powershell
# Create dedicated venv
python -m venv C:\LabelStudio\venv
C:\LabelStudio\venv\Scripts\Activate.ps1

# Install
pip install label-studio

# Run
label-studio start
```

**URL**: http://localhost:8080

**YOLO Export**:
- Export format: "YOLO v8" (built-in)
- Compatible with your current `data.yaml` structure

---

### 2️⃣ Roboflow Annotate (Web-based, Free Tier)

**Why:**
- ✅ No installation needed
- ✅ YOLO export
- ✅ Supports OBB (rotated boxes)
- ✅ Team collaboration features

**Limitations:**
- ❌ Requires internet connection
- ❌ Free tier: uploads to Roboflow (privacy concern)
- ⚠️ Max 10,000 images on free tier

**Use Case**: Only if you don't mind cloud storage and need OBB support.

**Note**: You're already using Roboflow, so this is an option for NEW annotations only.

---

### 3️⃣ LabelImg (Desktop, Lightweight)

**Why:**
- ✅ Standalone Windows .exe (no Python needed)
- ✅ YOLO format support
- ✅ Very fast for simple bounding boxes
- ✅ Tiny footprint (<10 MB)

**Limitations:**
- ❌ No OBB support
- ❌ No web UI (desktop only)
- ❌ No pre-labeling workflow
- ⚠️ Less actively maintained (last update 2021)

**Installation:**

```powershell
# Download from GitHub releases
# https://github.com/HumanSignal/labelImg/releases

# Or via pip
pip install labelImg
labelImg
```

**Use Case**: Quick annotations for small datasets (<100 images).

---

## Comparison Table

| Feature | Label Studio | Roboflow Annotate | LabelImg |
|---------|--------------|-------------------|----------|
| **Installation** | `pip install` | Web browser | .exe or pip |
| **UI** | Modern web UI | Modern web UI | Qt desktop |
| **Bounding Boxes** | ✅ | ✅ | ✅ |
| **OBB (Rotated)** | ❌ | ✅ | ❌ |
| **Polygons** | ✅ | ✅ | ❌ |
| **YOLO Export** | ✅ | ✅ | ✅ |
| **Pre-labeling** | ✅ | ✅ | ❌ |
| **Privacy** | ✅ Local | ⚠️ Cloud | ✅ Local |
| **Team Features** | ⚠️ Enterprise | ✅ Free | ❌ |
| **Speed** | Fast | Moderate | Very fast |
| **Active Dev** | ✅ | ✅ | ⚠️ Stale |

---

## SELECTED TOOL: Label Studio

**Setup Instructions:**

### Step 1: Install Label Studio

```powershell
# Navigate to scripts folder
cd c:\Users\georgem\source\repos\AutoFactoryScope\scripts

# Create Label Studio environment
python -m venv ..\.labelstudio_env
..\.labelstudio_env\Scripts\Activate.ps1

# Install
pip install label-studio

# Verify
label-studio --version
```

### Step 2: Create Label Studio Project

```powershell
# Start server
label-studio start --port 8080

# Browser opens at http://localhost:8080
# Create new project: "AutoFactoryScope Annotations"
```

### Step 3: Import Existing Dataset

1. **Upload Images**:
   - Settings → Import → Upload Files
   - Select: `datasets/v2_roboflow_export/train/images/*.jpg`

2. **Import Existing Labels** (Optional):
   - Settings → Import → Upload Files
   - Format: YOLO (will auto-convert from existing `.txt` files)

3. **Configure Labeling Interface**:

```xml
<View>
  <Image name="image" value="$image"/>
  <RectangleLabels name="label" toName="image">
    <Label value="robot" background="red"/>
    <Label value="weld_gun" background="blue"/>
    <Label value="fixture" background="green"/>
    <Label value="conveyor" background="yellow"/>
    <Label value="gate" background="purple"/>
  </RectangleLabels>
</View>
```

### Step 4: Export YOLO Format

```powershell
# From Label Studio UI:
# Export → YOLO

# Output structure matches your existing format:
# - images/
# - labels/
# - notes.json (metadata)
```

---

## Active Learning Workflow

1. **Train model** on existing dataset (v2)
2. **Run inference** on new unlabeled images
3. **Import predictions** to Label Studio as pre-labels
4. **Human correction** (faster than labeling from scratch)
5. **Export corrected labels** to `datasets/v3_active_learning/`
6. **Retrain** with expanded dataset

**Script**: `scripts/prelabel_with_model.py` (created later in this guide)

---

## Next Steps

- [ ] Install Label Studio (5 minutes)
- [ ] Import v2 dataset (10 minutes)
- [ ] Test annotation workflow (15 minutes)
- [ ] Set up pre-labeling pipeline (after model training)

---

**Last Updated**: 2026-01-20
