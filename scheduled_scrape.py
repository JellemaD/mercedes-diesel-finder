#!/usr/bin/env python3
"""
Scheduled scrape script for PythonAnywhere
Run this daily via PythonAnywhere Tasks tab
"""

import sys
import os

# Set working directory to script location
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Add to path
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

print("=" * 60)
print("PYTHONANYWHERE SCHEDULED SCRAPE")
print("=" * 60)

# Run the scrapers
try:
    print("\n[1/2] Running fetch_real_data.py...")
    import fetch_real_data
    fetch_real_data.main()
except Exception as e:
    print(f"Error in fetch_real_data: {e}")

try:
    print("\n[2/2] Running scrape_extra_sources.py...")
    import scrape_extra_sources
    scrape_extra_sources.main()
except Exception as e:
    print(f"Error in scrape_extra_sources: {e}")

print("\n" + "=" * 60)
print("SCRAPE COMPLETED")
print("=" * 60)
