#!/usr/bin/env python3
"""Test different confidence thresholds."""

import os
import sys

# Set the threshold BEFORE importing anything
threshold = sys.argv[1] if len(sys.argv) > 1 else "0.22"
os.environ['AFS_CONFIDENCE_THRESHOLD'] = threshold
os.environ['AFS_NMS_IOU_THRESHOLD'] = '0.40'

print(f"Testing with confidence threshold: {threshold}")
print(f"NMS IoU threshold: 0.40")
print()
print("NOTE: Start backend with these settings first:")
print(f'  $env:AFS_CONFIDENCE_THRESHOLD="{threshold}"')
print('  $env:AFS_NMS_IOU_THRESHOLD="0.40"')
print('  .\\scripts\\start_backend.ps1')
print()
print("Then run: python test_annotated.py")
