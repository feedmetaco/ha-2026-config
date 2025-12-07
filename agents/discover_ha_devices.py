#!/usr/bin/env python3
"""
HA SSH Device Discovery Agent
Connects to HA via SSH and pulls live device/entity data
"""

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime

def test_ssh_connection(ha_ip="192.168.10.6"):
    """Test basic SSH connectivity."""
    print(f"\n🔌 Testing SSH connection to {ha_ip}...")
    
    try:
        # Try simple SSH command
        result = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=5", f"root@{ha_ip}", "echo 'Connection successful'"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print(f"✅ SSH connection successful!")
            return True
        else:
            print(f"❌ SSH connection failed")
            print(f"   Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ SSH test failed: {e}")
        return False

def get_ha_devices_via_api(ha_ip="192.168.10.6"):
    """Get devices and entities from HA using REST API."""
    print(f"\n📊 Fetching devices and entities from HA at {ha_ip}...")
    
    import requests
    
    # You'll need to add your HA token here
    print("\n⚠️  Note: For API access, you need a Long-Lived Access Token")
    print("   Create one at: http://{}/profile".format(ha_ip))
    print("   Or add it to config/secrets.yaml as HA_TOKEN")
    
    token = input("\nEnter your HA Long-Lived Access Token (or press Enter to skip): ").strip()
    
    if not token:
        print("⏭️  Skipping API access")
        return None
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Get all states (entities)
        response = requests.get(f"http://{ha_ip}:8123/api/states", headers=headers, timeout=10)
        
        if response.status_code == 200:
            states = response.json()
            
            # Process entities
            devices_by_domain = {}
            all_entities = []
            
            for state in states:
                entity_id = state.get("entity_id", "")
                domain = entity_id.split(".")[0] if "." in entity_id else "unknown"
                
                entity_info = {
                    "entity_id": entity_id,
                    "state": state.get("state"),
                    "friendly_name": state.get("attributes", {}).get("friendly_name", entity_id),
                    "domain": domain,
                    "last_updated": state.get("last_updated"),
                    "attributes": state.get("attributes", {})
                }
                
                all_entities.append(entity_info)
                
                if domain not in devices_by_domain:
                    devices_by_domain[domain] = []
                devices_by_domain[domain].append(entity_info)
            
            # Save to files
            output_dir = Path("agent_data")
            output_dir.mkdir(exist_ok=True)
            
            # Save all entities
            with open(output_dir / "all_entities.json", "w") as f:
                json.dump(all_entities, f, indent=2)
            
            # Save devices by domain
            with open(output_dir / "devices_by_domain.json", "w") as f:
                json.dump(devices_by_domain, f, indent=2)
            
            # Create summary
            summary = {
                "total_entities": len(all_entities),
                "domains": list(devices_by_domain.keys()),
                "entities_by_domain": {domain: len(entities) for domain, entities in devices_by_domain.items()},
                "retrieved_at": datetime.now().isoformat(),
                "ha_ip": ha_ip
            }
            
            with open(output_dir / "summary.json", "w") as f:
                json.dump(summary, f, indent=2)
            
            # Create human-readable entity list
            with open(output_dir / "entity_list.txt", "w") as f:
                f.write(f"Home Assistant Entity List\n")
                f.write(f"Retrieved: {summary['retrieved_at']}\n")
                f.write(f"Total Entities: {summary['total_entities']}\n")
                f.write(f"=" * 80 + "\n\n")
                
                for domain in sorted(devices_by_domain.keys()):
                    f.write(f"\n{domain.upper()} ({len(devices_by_domain[domain])} entities)\n")
                    f.write("-" * 80 + "\n")
                    
                    for entity in sorted(devices_by_domain[domain], key=lambda x: x['entity_id']):
                        f.write(f"  {entity['entity_id']}\n")
                        f.write(f"    Name: {entity['friendly_name']}\n")
                        f.write(f"    State: {entity['state']}\n")
                        f.write(f"\n")
            
            print(f"\n✅ Retrieved {len(all_entities)} entities from HA!")
            print(f"\n📊 Summary:")
            print(f"   Total Entities: {summary['total_entities']}")
            print(f"\n   Top Domains:")
            
            for domain, count in sorted(summary['entities_by_domain'].items(), key=lambda x: -x[1])[:15]:
                print(f"      {domain}: {count}")
            
            print(f"\n💾 Data saved to: {output_dir.absolute()}")
            print(f"   - all_entities.json (complete entity data)")
            print(f"   - devices_by_domain.json (organized by domain)")
            print(f"   - entity_list.txt (human-readable list)")
            print(f"   - summary.json (quick overview)")
            
            return summary
            
        else:
            print(f"❌ API request failed with status {response.status_code}")
            print(f"   {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Failed to get device info: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print("=" * 60)
    print("  HA SSH Device Discovery Agent")
    print("=" * 60)
    
    ha_ip = "192.168.10.6"
    
    # Test SSH connectivity
    ssh_working = test_ssh_connection(ha_ip)
    
    if not ssh_working:
        print("\n⚠️  SSH connection not available yet.")
        print("   To enable SSH on Home Assistant:")
        print("   1. Install 'Terminal & SSH' add-on from the Add-on Store")
        print("   2. Configure it with a password or SSH key")
        print("   3. Start the add-on")
        print("\n   For now, we'll use the REST API instead...")
    
    # Get devices via API
    get_ha_devices_via_api(ha_ip)
    
    print("\n" + "=" * 60)
    print("  Discovery Complete!")
    print("=" * 60)

if __name__ == "__main__":
    # Check if requests is installed
    try:
        import requests
    except ImportError:
        print("Installing required package: requests")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "--user"])
        import requests
    
    main()

