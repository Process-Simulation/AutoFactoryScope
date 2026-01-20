#!/usr/bin/env python3
"""
Test multiple thresholds to find the sweet spot for exactly 23 detections.
"""

import requests
from pathlib import Path

API_URL = "http://localhost:8000"
PDF_PATH = r"C:\Users\georgem\source\repos\AutoFactoryScope_data\Layouts\OAK-B-01-8A-0001-26MY-P708-D-I- BASE_20250609.pdf"

def get_detections():
    """Get all detections from API."""
    pdf_file = Path(PDF_PATH)

    if not pdf_file.exists():
        print(f"Error: PDF not found at {PDF_PATH}")
        return None

    try:
        with open(pdf_file, 'rb') as f:
            files = {'file': (pdf_file.name, f, 'application/pdf')}
            params = {'include_annotated': 'false'}

            response = requests.post(
                f"{API_URL}/detect",
                files=files,
                params=params,
                timeout=120
            )

        if response.status_code == 200:
            return response.json()['detections']
        else:
            print(f"API Error: {response.status_code}")
            return None

    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    print("=" * 70)
    print("Testing Thresholds to Find Optimal Value")
    print("=" * 70)
    print()

    # Get all detections
    print("Fetching detections from API...")
    detections = get_detections()

    if not detections:
        print("Failed to get detections")
        return

    # Sort by confidence
    detections_sorted = sorted(detections, key=lambda d: d['confidence'])

    print(f"Total detections: {len(detections)}")
    print(f"Target: 23 floor robots")
    print()

    # Show all confidences
    print("All detections sorted by confidence (lowest to highest):")
    print("-" * 70)
    for i, det in enumerate(detections_sorted, 1):
        conf_pct = det['confidence'] * 100
        x1, y1, x2, y2 = det['bbox']
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2

        marker = ""
        if i <= 3:  # Lowest 3 (potential false positives)
            marker = " ← SUSPECT"
        if i == 24:  # 24th detection (cutoff for 23)
            marker = " ← CUTOFF (keep 23, reject above this)"

        print(f"{i:2d}. {conf_pct:6.2f}% at ({center_x:5.0f}, {center_y:5.0f}){marker}")

    print()
    print("=" * 70)
    print("THRESHOLD ANALYSIS")
    print("=" * 70)

    # Test different thresholds
    thresholds = [0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60]

    for threshold in thresholds:
        count = sum(1 for d in detections if d['confidence'] >= threshold)
        status = "✓" if count == 23 else "✗"
        diff = count - 23
        diff_str = f"({diff:+d})" if diff != 0 else ""
        print(f"Threshold {threshold:.2f}: {count:2d} detections {diff_str} {status}")

    print()
    print("=" * 70)
    print("RECOMMENDATION")
    print("=" * 70)

    # Find threshold that gives exactly 23
    for threshold in [t/100 for t in range(20, 70, 1)]:  # 0.20 to 0.69
        count = sum(1 for d in detections if d['confidence'] >= threshold)
        if count == 23:
            print(f"✓ Threshold {threshold:.2f} gives exactly 23 detections!")
            print()
            print("Update config.py:")
            print(f"  confidence_threshold: float = {threshold:.2f}")
            break
    else:
        print("⚠ No single threshold gives exactly 23 detections")
        print()
        print("This suggests the model needs retraining or we need to accept")
        print("either some false positives or some missed robots.")

if __name__ == "__main__":
    main()
