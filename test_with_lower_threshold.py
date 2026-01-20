#!/usr/bin/env python3
"""
Test detection with lowered thresholds.

This modifies the backend settings temporarily via environment variables.
"""

import os
import sys

# Set environment variables BEFORE importing anything else
os.environ['AFS_CONFIDENCE_THRESHOLD'] = '0.20'  # Lower from 0.25
os.environ['AFS_NMS_IOU_THRESHOLD'] = '0.40'     # Lower from 0.50

# Now we can test
print("Testing with adjusted thresholds:")
print(f"  Confidence threshold: 0.20 (was 0.25)")
print(f"  NMS IoU threshold: 0.40 (was 0.50)")
print("")
print("NOTE: Backend needs to be restarted with these environment variables.")
print("Run this in PowerShell:")
print("")
print('$env:AFS_CONFIDENCE_THRESHOLD="0.20"')
print('$env:AFS_NMS_IOU_THRESHOLD="0.40"')
print('.\\scripts\\start_backend.ps1')
