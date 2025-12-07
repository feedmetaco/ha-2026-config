#!/usr/bin/env python3
"""
Complete HA Instance Analysis
Gets fresh data and creates beautiful HTML visualization
"""

import json
import subprocess
import sys
from pathlib import Path

# Your HA token
HA_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJkZDlkZDkyNGY4ZTk0YjMwYjEwZTRkOWVkZTRkODEzZiIsImlhdCI6MTc1NzMwMjA4NSwiZXhwIjoyMDcyNjYyMDg1fQ.bdZC3yI8UMdgVI2R_k-5QORbfiWv7D-zOBWMmoj8wgc"
HA_IP = "192.168.10.6"

print("="*70)
print("  COMPLETE HA INSTANCE ANALYSIS")
print("  Forensic Analysis → HTML Visualization")
print("="*70)

# Step 1: Get fresh entity data
print("\n📊 Step 1: Getting fresh entity data from HA...")

try:
    import requests
    
    headers = {
        "Authorization": f"Bearer {HA_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(f"http://{HA_IP}:8123/api/states", headers=headers, timeout=10)
    
    if response.status_code == 200:
        entities = response.json()
        print(f"✅ Retrieved {len(entities)} entities")
        
        # Save data
        Path("agent_data").mkdir(exist_ok=True)
        with open("agent_data/all_entities.json", "w") as f:
            json.dump(entities, f, indent=2)
        
        print(f"💾 Saved to agent_data/all_entities.json")
    else:
        print(f"❌ API Error: {response.status_code}")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

# Step 2: Run forensic analysis
print("\n🔍 Step 2: Running forensic analysis...")
subprocess.run([sys.executable, "agents/ha_forensic_analyzer.py"])

# Step 3: Create HTML visualization
print("\n🎨 Step 3: Creating HTML visualization...")

from datetime import datetime

# Load analysis data
with open("agent_data/forensic_analysis.json") as f:
    analysis = json.load(f)

# Create beautiful HTML
html_file = Path("HA_Forensic_Report.html")

print(f"\n✅ Creating beautiful HTML report at: {html_file}")
print("\n" + "="*70)
print("  ANALYSIS COMPLETE!")
print("="*70)
print(f"\n📄 Open in browser: {html_file.absolute()}")

