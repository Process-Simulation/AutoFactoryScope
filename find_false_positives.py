#!/usr/bin/env python3
"""
Find the confidence values of the 2 false positive detections.
This will help us set the right threshold to get exactly 23 detections.
"""

import requests
import json
from pathlib import Path

API_URL = "http://localhost:8000"
PDF_PATH = r"C:\Users\georgem\source\repos\AutoFactoryScope_data\Layouts\OAK-B-01-8A-0001-26MY-P708-D-I- BASE_20250609.pdf"

def main():
    pdf_file = Path(PDF_PATH)

    if not pdf_file.exists():
        print(f"Error: PDF not found at {PDF_PATH}")
        return

    print("=" * 70)
    print("Finding False Positive Confidence Values")
    print("=" * 70)

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

        if response.status_code != 200:
            print(f"API Error: {response.status_code}")
            print(response.text)
            return

        result = response.json()
        detections = result['detections']

        # Sort by confidence (lowest first)
        detections_sorted = sorted(detections, key=lambda d: d['confidence'])

        print(f"\nTotal detections: {len(detections)}")
        print(f"Expected: 23 floor robots")
        print(f"False positives: {len(detections) - 23} (the 2 lowest confidence)")
        print()

        print("Bottom 5 detections (lowest confidence - likely false positives):")
        print("-" * 70)
        for i, det in enumerate(detections_sorted[:5], 1):
            conf_pct = det['confidence'] * 100
            x1, y1, x2, y2 = det['bbox']
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2

            marker = " ← FALSE POSITIVE" if i <= 2 else ""
            print(f"{i}. Confidence: {conf_pct:6.2f}% at ({center_x:5.0f}, {center_y:5.0f}){marker}")

        print()
        print("All detections sorted by confidence:")
        print("-" * 70)
        for i, det in enumerate(detections_sorted, 1):
            conf_pct = det['confidence'] * 100
            marker = " ← FALSE POSITIVE" if i <= 2 else ""
            marker += " ← CUTOFF (23rd robot)" if i == 3 else ""
            print(f"{i:2d}. {conf_pct:6.2f}%{marker}")

        print()
        print("=" * 70)
        print("THRESHOLD RECOMMENDATION")
        print("=" * 70)

        # The threshold should be just above the 2nd lowest (2nd false positive)
        # but below the 3rd lowest (23rd real robot)
        if len(detections) >= 3:
            fp2_conf = detections_sorted[1]['confidence'] * 100  # 2nd detection (2nd FP)
            real23_conf = detections_sorted[2]['confidence'] * 100  # 3rd detection (23rd real robot)

            print(f"2nd false positive: {fp2_conf:.2f}%")
            print(f"23rd real robot:    {real23_conf:.2f}%")
            print()

            # Suggest threshold in between
            suggested = (fp2_conf + real23_conf) / 2
            print(f"Suggested threshold: {suggested:.2f}% ({suggested/100:.4f})")
            print()
            print("Update config.py:")
            print(f"  confidence_threshold: float = {suggested/100:.2f}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
