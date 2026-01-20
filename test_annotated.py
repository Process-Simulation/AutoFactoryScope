#!/usr/bin/env python3
"""Quick test to get annotated image."""

import requests
import base64
from pathlib import Path
from datetime import datetime

PDF_PATH = r"C:\Users\georgem\source\repos\AutoFactoryScope_data\Layouts\OAK-B-01-8A-0001-26MY-P708-D-I- BASE_20250609.pdf"
API_URL = "http://localhost:8000"

print("Testing PDF detection with tuned parameters...")
print(f"Confidence threshold: 0.20")
print(f"NMS IoU threshold: 0.40")
print()

pdf_file = Path(PDF_PATH)
if not pdf_file.exists():
    print(f"Error: PDF not found")
    exit(1)

try:
    with open(pdf_file, 'rb') as f:
        files = {'file': (pdf_file.name, f, 'application/pdf')}
        params = {'include_annotated': 'true'}  # Request annotated image

        print("Uploading PDF...")
        response = requests.post(
            f"{API_URL}/detect",
            files=files,
            params=params,
            timeout=120
        )

    if response.status_code == 200:
        result = response.json()
        print(f"Success!")
        print(f"  Robots detected: {result['robot_count']}")
        print(f"  Image size: {result['image_size'][0]} x {result['image_size'][1]}")
        print(f"  Processing time: {result['processing_time_ms']:.0f} ms")
        print()

        # Save annotated image
        if result.get('annotated_image'):
            output_dir = Path("test_results")
            output_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = output_dir / f"tuned_detection_{timestamp}.png"

            image_bytes = base64.b64decode(result['annotated_image'])
            output_path.write_bytes(image_bytes)

            print(f"Annotated image saved to: {output_path}")
            print()

            # Show confidence distribution
            print("Confidence ranges:")
            confidences = [d['confidence'] for d in result['detections']]
            for threshold in [0.5, 0.4, 0.3, 0.2]:
                count = sum(1 for c in confidences if c >= threshold)
                print(f"  >={threshold*100:.0f}%: {count} detections")

            print()
            print(f"Opening image...")
            import subprocess
            subprocess.Popen(['start', str(output_path)], shell=True)

        print("Done!")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

except Exception as e:
    print(f"Error: {e}")
