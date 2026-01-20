# Restart Backend with PDF Support

The PDF processing code has been added, but the backend needs to be restarted to load it.

## Steps:

### 1. Stop Current Backend
In the terminal running the backend, press **Ctrl+C**

### 2. Restart Backend
```powershell
.\scripts\start_backend.ps1
```

The backend will now support PDF uploads!

### 3. Test PDF Detection

**Option A: PowerShell Script**
```powershell
.\scripts\test_pdf_detection.ps1
```

**Option B: Python Script**
```powershell
python test_pdf_quick.py
```

**Option C: Web Interface**
1. Go to http://localhost:8000/docs
2. Click on `/detect` endpoint
3. Click "Try it out"
4. Upload one of these PDFs:
   - `C:\Users\georgem\source\repos\AutoFactoryScope_data\Layouts\OAK-B-01-8A-0001-26MY-P708-D-I- BASE_20250609.pdf`
   - `C:\Users\georgem\source\repos\AutoFactoryScope_data\Layouts\OHP-B-01-9X-0001-26MY-V801-PRO-IMPBASE_20251014_27JPH 1.pdf`

## What Changed:

✅ Added `pdf2image` and `PyMuPDF` libraries
✅ Created PDF conversion utilities
✅ Updated `/detect` endpoint to accept PDFs
✅ Auto-converts PDF pages to 300 DPI images
✅ Processes first page of PDF (multi-page support coming soon)

## Expected Results:

The API will:
1. Detect the PDF file type
2. Convert the first page to a high-quality image (300 DPI)
3. Run robot detection on the converted image
4. Return bounding boxes and confidence scores
5. Optionally return an annotated image

Enjoy detecting robots in your PDF factory layouts! 🤖
