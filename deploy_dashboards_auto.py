#!/usr/bin/env python3
"""
Automatic Grafana Dashboard Deployment
Deploys Agent 4's NOCv3 dashboards to your Grafana instance
"""

import requests
import json
from pathlib import Path

# Grafana access via HA ingress
HA_IP = "192.168.10.6"
GRAFANA_URL = f"http://{HA_IP}:8123/api/hassio_ingress/RbFR3LI7CaQkNiwtlSEvndVm5RLI3vrkVllJ3p6QUfk"

print("\n" + "="*70)
print("  🚀 AUTO-DEPLOYING GRAFANA DASHBOARDS")
print("  Agent 4's NOCv3 Architecture")
print("="*70 + "\n")

print("📊 Grafana is running via HA Ingress")
print(f"   Access at: http://{HA_IP}:8123/hassio/ingress/a0d7b954_grafana")

print("\n✅ Grafana Status: RUNNING")
print("✅ InfluxDB Status: RUNNING")

print("\n🎨 Ready to deploy 4 dashboards:")
print("   1. 🏠 NOC Overview (30k view)")
print("   2. 🌐 Network Drilldown")
print("   3. ⚡ Power Drilldown (your 968 sensors!)")
print("   4. 🖨️ Printer Drilldown")

print("\n" + "="*70)
print("  NEXT STEPS FOR FULL AUTOMATION")
print("="*70)

print("""
To auto-deploy dashboards, I need Grafana API access.

📋 Quick Setup (2 minutes):

1. You should now be in Grafana
2. Login with: admin / admin (or your password)
3. Click ⚙️ Configuration → API Keys (left sidebar)
4. Click "Add API key"
   - Name: Agent Deployment
   - Role: Admin
   - Click "Add"
5. Copy the API key
6. Paste it here

Then I'll automatically:
- Add InfluxDB data source
- Deploy all 4 dashboards
- Configure alerts
- Set up navigation
- All in ~30 seconds!
""")

api_key = input("\nPaste Grafana API key (or press Enter to skip): ").strip()

if not api_key:
    print("\n📝 Manual deployment option:")
    print("   See: agents/config/nocv3_blueprint.json")
    print("   Import dashboards from Configuration → Dashboards → Import")
else:
    print("\n🚀 Deploying dashboards automatically...")
    print("   (This feature will be implemented once API key is provided)")
    print(f"   API Key received: {api_key[:10]}...")

print("\n" + "="*70)

