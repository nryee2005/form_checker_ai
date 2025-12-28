#!/usr/bin/env python3
"""
Check for orphaned temporary video files

Run this occasionally to verify no temp files are leaking.
These files should be auto-cleaned by the API, but this script
helps verify that cleanup is working correctly.
"""

import os
import time
from pathlib import Path
from datetime import datetime

def check_temp_files():
    """Check /tmp for orphaned video files from our API"""

    tmp_dir = Path("/tmp")

    # Find potential orphaned files
    mp4_files = list(tmp_dir.glob("*.mp4"))
    tmp_mp4_files = list(tmp_dir.glob("tmp*.mp4"))

    all_temp_videos = mp4_files + tmp_mp4_files

    if not all_temp_videos:
        print("✅ No orphaned temp video files found!")
        return

    print(f"⚠️  Found {len(all_temp_videos)} temp video file(s):\n")

    total_size = 0
    for file in all_temp_videos:
        try:
            stats = file.stat()
            size_mb = stats.st_size / (1024 * 1024)
            modified = datetime.fromtimestamp(stats.st_mtime)
            age_minutes = (time.time() - stats.st_mtime) / 60

            print(f"  {file.name}")
            print(f"    Size: {size_mb:.1f} MB")
            print(f"    Modified: {modified}")
            print(f"    Age: {age_minutes:.1f} minutes")
            print()

            total_size += size_mb
        except Exception as e:
            print(f"  {file.name} - Error reading: {e}")

    print(f"Total size: {total_size:.1f} MB")
    print(f"\nℹ️  Files older than 5 minutes are likely orphaned")
    print(f"ℹ️  Recent files (<1 minute) might be currently processing")

if __name__ == "__main__":
    check_temp_files()
