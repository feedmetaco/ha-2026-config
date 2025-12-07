#!/usr/bin/env python3
"""Check actual status of HA add-ons"""

import requests
import json

HA_IP = "192.168.10.6"
HA_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJkZDlkZDkyNGY4ZTk0YjMwYjEwZTRkOWVkZTRkODEzZiIsImlhdCI6MTc1NzMwMjA4NSwiZXhwIjoyMDcyNjYyMDg1fQ.bdZC3yI8UMdgVI2R_k-5QORbfiWv7D-zOBWMmoj8wgc"

headers = {"Authorization": f"Bearer {HA_TOKEN}"}

print("\n🔍 Checking ALL installed add-ons...\n")

try:
    response = requests.get(
        f"http://{HA_IP}:8123/api/hassio/addons",
        headers=headers,
        timeout=10
    )
    
    if response.status_code == 200:
        addons = response.json().get("data", {}).get("addons", [])
        
        print(f"Found {len(addons)} installed add-ons:\n")
        
        grafana_found = False
        influx_found = False
        
        for addon in addons:
            name = addon.get("name", "Unknown")
            state = addon.get("state", "unknown")
            version = addon.get("version", "")
            slug = addon.get("slug", "")
            
            # Highlight Grafana and InfluxDB
            if "grafana" in name.lower():
                print(f"📊 GRAFANA:")
                print(f"   Name: {name}")
                print(f"   State: {state}")
                print(f"   Version: {version}")
                print(f"   Slug: {slug}")
                print()
                grafana_found = True
                
                if state != "started":
                    print(f"   ⚠️ Grafana is {state} - needs to be STARTED")
                    print(f"   Go to: http://{HA_IP}:8123/hassio/addon/{slug}")
                    print()
            
            if "influx" in name.lower():
                print(f"💾 INFLUXDB:")
                print(f"   Name: {name}")
                print(f"   State: {state}")
                print(f"   Version: {version}")
                print(f"   Slug: {slug}")
                print()
                influx_found = True
        
        # Summary
        print("="*60)
        print("SUMMARY:")
        print(f"  Grafana: {'✅ Found' if grafana_found else '❌ Not found'}")
        print(f"  InfluxDB: {'✅ Found' if influx_found else '❌ Not found'}")
        print("="*60)
        
        if grafana_found and influx_found:
            print("\n🎉 Both services detected!")
            print("\nIf Grafana state is 'started', we can auto-deploy dashboards!")
        
    else:
        print(f"❌ API Error: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ Error: {e}")

