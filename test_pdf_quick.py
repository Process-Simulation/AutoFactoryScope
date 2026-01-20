#!/usr/bin/env python3
"""Quick PDF detection test using Python requests."""

import requests
import sys
from pathlib import Path

# PDF files to test
PDF_FILES = [
    r"C:\Users\georgem\source\repos\AutoFactoryScope_data\Layouts\OAK-B-01-8A-0001-26MY-P708-D-I- BASE_20250609.pdf",
    r"C:\Users\georgem\source\repos\AutoFactoryScope_data\Layouts\OHP-B-01-9X-0001-26MY-V801-PRO-IMPBASE_20251014_27JPH 1.pdf"
]

API_URL = "http://localhost:8000"


def test_pdf(pdf_path: str):
    """Test PDF detection."""
    pdf_file = Path(pdf_path)

    if not pdf_file.exists():
        print(f"❌ PDF not found: {pdf_path}")
        return False

    print(f"\n{'='*60}")
    print(f"Testing: {pdf_file.name}")
    print(f"Size: {pdf_file.stat().st_size / 1024 / 1024:.2f} MB")
    print(f"{'='*60}\n")

    try:
        # Upload PDF
        with open(pdf_file, 'rb') as f:
            files = {'file': (pdf_file.name, f, 'application/pdf')}
            params = {'include_annotated': 'false'}  # Don't download annotated image

            print("Uploading to API...")
            response = requests.post(
                f"{API_URL}/detect",
                files=files,
                params=params,
                timeout=120
            )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Detection successful!")
            print(f"   Robots detected: {result['robot_count']}")
            print(f"   Image size: {result['image_width']} x {result['image_height']}")
            print(f"   Processing time: {result['processing_time_ms']:.2f} ms")

            if result['robot_count'] > 0:
                print(f"\n   Detections:")
                for i, det in enumerate(result['detections'][:5], 1):
                    print(f"     [{i}] Confidence: {det['confidence']*100:.1f}% "
                          f"at ({det['x']:.0f}, {det['y']:.0f})")

            return True
        else:
            error = response.json()
            print(f"❌ API Error ({response.status_code})")
            print(f"   Code: {error.get('error', {}).get('code', 'Unknown')}")
            print(f"   Message: {error.get('error', {}).get('message', 'Unknown')}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Is the backend running?")
        print("   Start it with: .\\scripts\\start_backend.ps1")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run tests."""
    print("\n" + "="*60)
    print("  AutoFactoryScope - PDF Detection Test")
    print("="*60)

    # Check API health
    try:
        health = requests.get(f"{API_URL}/health", timeout=5).json()
        print(f"\nAPI Status: {health['status']}")
        print(f"Model Loaded: {health['model_loaded']}")
    except:
        print("\n❌ API not responding!")
        print("Please restart the backend with PDF support:")
        print("  1. Stop current backend (Ctrl+C)")
        print("  2. Run: .\\scripts\\start_backend.ps1")
        sys.exit(1)

    # Test each PDF
    results = []
    for pdf_path in PDF_FILES:
        if Path(pdf_path).exists():
            success = test_pdf(pdf_path)
            results.append((Path(pdf_path).name, success))
        else:
            print(f"\n⚠ Skipping (not found): {Path(pdf_path).name}")

    # Summary
    print(f"\n{'='*60}")
    print("Test Summary:")
    print(f"{'='*60}")
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} - {name}")

    print()


if __name__ == "__main__":
    main()
