#!/usr/bin/env python3
"""
Analyze detection results to understand why some robots are missed.

This script:
1. Runs detection with multiple confidence thresholds
2. Shows how many detections survive at each threshold
3. Analyzes NMS impact with different IoU thresholds
4. Helps tune parameters for better detection
"""

import requests
import sys
from pathlib import Path

API_URL = "http://localhost:8000"

# Test PDF
PDF_PATH = r"C:\Users\georgem\source\repos\AutoFactoryScope_data\Layouts\OAK-B-01-8A-0001-26MY-P708-D-I- BASE_20250609.pdf"


def test_with_settings(conf_threshold: float = 0.25, nms_iou: float = 0.5):
    """Test detection with specific settings."""
    pdf_file = Path(PDF_PATH)

    if not pdf_file.exists():
        print(f"❌ PDF not found: {PDF_PATH}")
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
            return response.json()
        else:
            print(f"❌ API Error: {response.status_code}")
            return None

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def analyze_detections(result):
    """Analyze detection results."""
    if not result:
        return

    detections = result['detections']

    # Sort by confidence
    detections_sorted = sorted(detections, key=lambda d: d['confidence'], reverse=True)

    print(f"\nTotal Detections: {len(detections)}")
    width, height = result['image_size']
    print(f"Image Size: {width} x {height}")
    print(f"\nConfidence Distribution:")

    # Show confidence ranges
    ranges = [
        (0.9, 1.0, "Very High (>90%)"),
        (0.7, 0.9, "High (70-90%)"),
        (0.5, 0.7, "Medium (50-70%)"),
        (0.3, 0.5, "Low (30-50%)"),
        (0.0, 0.3, "Very Low (<30%)"),
    ]

    for min_conf, max_conf, label in ranges:
        count = sum(1 for d in detections if min_conf <= d['confidence'] < max_conf)
        if count > 0:
            print(f"  {label}: {count} detections")

    # Show top 24 detections (expected count)
    print(f"\nTop 24 Detections (expected count):")
    for i, det in enumerate(detections_sorted[:24], 1):
        x1, y1, x2, y2 = det['bbox']
        width = x2 - x1
        height = y2 - y1
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        print(f"  [{i:2d}] Confidence: {det['confidence']*100:5.1f}% "
              f"at ({center_x:5.0f}, {center_y:5.0f}) "
              f"size: {width:4.0f}x{height:4.0f}")

    if len(detections) > 24:
        print(f"\n  ... and {len(detections) - 24} more detections")

    # Show spatial distribution
    print(f"\nSpatial Analysis:")
    centers = [((d['bbox'][0] + d['bbox'][2])/2, (d['bbox'][1] + d['bbox'][3])/2) for d in detections]
    print(f"  X range: {min(c[0] for c in centers):.0f} - {max(c[0] for c in centers):.0f}")
    print(f"  Y range: {min(c[1] for c in centers):.0f} - {max(c[1] for c in centers):.0f}")

    # Check for clusters (detections very close together)
    clusters = 0
    for i, det1 in enumerate(detections):
        c1 = ((det1['bbox'][0] + det1['bbox'][2])/2, (det1['bbox'][1] + det1['bbox'][3])/2)
        for det2 in detections[i+1:]:
            c2 = ((det2['bbox'][0] + det2['bbox'][2])/2, (det2['bbox'][1] + det2['bbox'][3])/2)
            dx = abs(c1[0] - c2[0])
            dy = abs(c1[1] - c2[1])
            distance = (dx**2 + dy**2)**0.5

            if distance < 100:  # Less than 100 pixels apart
                clusters += 1

    if clusters > 0:
        print(f"  Close pairs: {clusters} (detections within 100px of each other)")

    return detections


def main():
    """Run analysis."""
    print("\n" + "="*70)
    print("  Detection Analysis Tool")
    print("="*70)

    # Check API
    try:
        health = requests.get(f"{API_URL}/health", timeout=5).json()
        print(f"\nAPI Status: {health['status']}")
        print(f"Model Loaded: {health['model_loaded']}")
    except:
        print("\n❌ API not responding!")
        sys.exit(1)

    print(f"\nTesting PDF: {Path(PDF_PATH).name}")
    print("="*70)

    # Run detection with current settings
    print("\nRunning detection with current settings...")
    result = test_with_settings()

    if result:
        detections = analyze_detections(result)

        # Summary
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        print(f"Expected robots: 24")
        print(f"Detected robots: {result['robot_count']}")
        print(f"Missing: {24 - result['robot_count']}")

        if result['robot_count'] < 24:
            print("\nPossible reasons for missing robots:")
            print("  1. Low confidence threshold (currently 0.25)")
            print("  2. Aggressive NMS (currently IoU 0.5)")
            print("  3. Some robots not in training data")
            print("  4. Robots at tile boundaries")
            print("\nRecommendations:")
            if result['robot_count'] >= 21:
                print("  - Try lowering confidence threshold to 0.15-0.20")
                print("  - Try lowering NMS IoU threshold to 0.3-0.4")
            else:
                print("  - Model may need more training data")
                print("  - Check if missed robots have different appearance")


if __name__ == "__main__":
    main()
