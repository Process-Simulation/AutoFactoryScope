#!/usr/bin/env python3
"""Compare detection results between models and thresholds."""

import requests
import base64
import shutil
from pathlib import Path
from datetime import datetime

PDF_PATH = r"C:\Users\georgem\source\repos\AutoFactoryScope_data\Layouts\OAK-B-01-8A-0001-26MY-P708-D-I- BASE_20250609.pdf"
API_URL = "http://localhost:8000"
EXPECTED_COUNT = 23  # Floor-mounted robots only (excludes track robot)

def test_detection(model_name="current", save_image=True):
    """Test PDF detection and return results."""
    pdf_file = Path(PDF_PATH)

    if not pdf_file.exists():
        print(f"Error: PDF not found at {PDF_PATH}")
        return None

    try:
        with open(pdf_file, 'rb') as f:
            files = {'file': (pdf_file.name, f, 'application/pdf')}
            params = {'include_annotated': 'true' if save_image else 'false'}

            response = requests.post(
                f"{API_URL}/detect",
                files=files,
                params=params,
                timeout=120
            )

        if response.status_code == 200:
            result = response.json()

            # Save annotated image if requested
            if save_image and result.get('annotated_image'):
                output_dir = Path("test_results")
                output_dir.mkdir(exist_ok=True)

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = output_dir / f"{model_name}_{timestamp}.png"

                image_bytes = base64.b64decode(result['annotated_image'])
                output_path.write_bytes(image_bytes)
                result['output_path'] = str(output_path)

            return result
        else:
            print(f"API Error: {response.status_code}")
            print(response.text)
            return None

    except Exception as e:
        print(f"Error: {e}")
        return None


def print_results(result, model_name, threshold):
    """Print detection results."""
    if not result:
        return

    count = result['robot_count']
    diff = count - EXPECTED_COUNT
    status = "✓ PERFECT" if count == EXPECTED_COUNT else f"{'➕' if diff > 0 else '➖'} {abs(diff)}"

    print(f"\n{'='*70}")
    print(f"Model: {model_name} | Threshold: {threshold}")
    print(f"{'='*70}")
    print(f"Detected: {count} robots | Expected: {EXPECTED_COUNT} | {status}")
    print(f"Image: {result['image_size'][0]}x{result['image_size'][1]}")
    print(f"Time: {result['processing_time_ms']:.0f}ms")

    if result.get('output_path'):
        print(f"Saved: {result['output_path']}")

    # Show confidence distribution
    detections = result['detections']
    if detections:
        confidences = [d['confidence'] for d in detections]
        print(f"\nConfidence range: {min(confidences)*100:.1f}% - {max(confidences)*100:.1f}%")
        print(f"  ≥50%: {sum(1 for c in confidences if c >= 0.5)} detections")
        print(f"  ≥40%: {sum(1 for c in confidences if c >= 0.4)} detections")
        print(f"  ≥30%: {sum(1 for c in confidences if c >= 0.3)} detections")
        print(f"  ≥20%: {sum(1 for c in confidences if c >= 0.2)} detections")


def main():
    """Run comparison tests."""
    print("\n" + "="*70)
    print("  Model Comparison Test")
    print("="*70)
    print(f"Target: {EXPECTED_COUNT} floor-mounted robots")
    print(f"PDF: {Path(PDF_PATH).name}")

    # Check API health
    try:
        health = requests.get(f"{API_URL}/health", timeout=5).json()
        print(f"\nAPI: {health['status']} | Model loaded: {health['model_loaded']}")
    except:
        print("\nAPI not responding! Start backend first:")
        print("  $env:AFS_CONFIDENCE_THRESHOLD=\"0.23\"")
        print("  $env:AFS_NMS_IOU_THRESHOLD=\"0.40\"")
        print("  .\\scripts\\start_backend.ps1")
        return

    # Get current config from API
    current_result = test_detection("threshold_0.23")

    if current_result:
        # Determine threshold from detections
        threshold = "0.23"  # User should have set this via env var
        print_results(current_result, "YOLOv11n (current)", threshold)

    print("\n" + "="*70)
    print("Summary")
    print("="*70)

    if current_result:
        count = current_result['robot_count']
        if count == EXPECTED_COUNT:
            print(f"✓ Perfect detection: {EXPECTED_COUNT}/{EXPECTED_COUNT} robots")
            print("\nRecommendation: Update config.py defaults")
            print("  confidence_threshold: 0.23")
            print("  nms_iou_threshold: 0.40")
        elif count < EXPECTED_COUNT:
            print(f"⚠ Missing {EXPECTED_COUNT - count} robots")
            print("  Try lowering threshold to 0.22 or 0.21")
        else:
            print(f"⚠ {count - EXPECTED_COUNT} extra detections (false positives)")
            print("  Try raising threshold to 0.24 or 0.25")

    print("\nTo test Cole's YOLOv8s model:")
    print("  1. Stop backend (Ctrl+C)")
    print("  2. cp models/robot_detector_cole.onnx models/robot_detector.onnx")
    print("  3. Restart backend with same env vars")
    print("  4. Run this script again")


if __name__ == "__main__":
    main()
