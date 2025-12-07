#!/usr/bin/env python3
"""
HA Sync & SSH Agent
Syncs Samba share and provides SSH access to Home Assistant
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
import paramiko
import yaml

class HASyncAgent:
    """Agent to sync HA config and access via SSH."""
    
    def __init__(self, ha_ip="192.168.10.6", samba_share=r"\\homeassistant.local\config", local_path=r"c:\Users\Sami\Documents\ha-config"):
        self.ha_ip = ha_ip
        self.samba_share = samba_share
        self.local_path = Path(local_path)
        self.ssh_client = None
        
    def sync_from_samba(self):
        """Sync Samba share to local directory using robocopy."""
        
        print(f"🔄 Syncing from Samba share to local directory...")
        print(f"   Source: {self.samba_share}")
        print(f"   Destination: {self.local_path}")
        
        # Ensure local directory exists
        self.local_path.mkdir(parents=True, exist_ok=True)
        
        # Build robocopy command - mirror the share
        cmd = [
            "robocopy",
            self.samba_share,
            str(self.local_path),
            "/MIR",  # Mirror mode
            "/R:3",  # Retry 3 times
            "/W:5",  # Wait 5 seconds between retries
            # Exclude directories
            "/XD", ".storage", "deps", "tts", "__pycache__", ".git", "backups",
            # Exclude files
            "/XF", "*.db", "*.db-shm", "*.db-wal", "*.log", "*.log.*", "home-assistant.log.fault",
            "/NP",   # No progress (less verbose)
            "/NFL",  # No file list
            "/NDL",  # No directory list
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Robocopy exit codes: 0-7 are success, 8+ are errors
            if result.returncode < 8:
                print("✅ Sync completed successfully!")
                print(f"   Files synced to: {self.local_path}")
                return True
            else:
                print(f"❌ Sync failed with exit code: {result.returncode}")
                print(f"   Error: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Sync error: {e}")
            return False
    
    def setup_ssh_key(self):
        """Setup SSH key for Home Assistant access."""
        
        print(f"\n🔐 Setting up SSH access to {self.ha_ip}...")
        
        ssh_dir = Path.home() / ".ssh"
        ssh_dir.mkdir(exist_ok=True)
        
        key_file = ssh_dir / "ha_rsa"
        
        if key_file.exists():
            print(f"✅ SSH key already exists: {key_file}")
            return str(key_file)
        
        print(f"📝 Generating new SSH key...")
        
        try:
            # Generate SSH key using ssh-keygen
            subprocess.run([
                "ssh-keygen",
                "-t", "rsa",
                "-b", "4096",
                "-f", str(key_file),
                "-N", "",  # No passphrase
                "-C", "ha-sync-agent"
            ], check=True, capture_output=True)
            
            print(f"✅ SSH key generated: {key_file}")
            print(f"\n📋 To enable SSH access, copy this public key to your HA:")
            print(f"   1. Go to HA Settings → System → Network")
            print(f"   2. Enable 'Advanced Mode' in your HA user profile")
            print(f"   3. Or use Terminal & SSH add-on and add this key:")
            
            with open(f"{key_file}.pub", "r") as f:
                public_key = f.read().strip()
                print(f"\n   {public_key}\n")
            
            return str(key_file)
            
        except Exception as e:
            print(f"❌ Key generation failed: {e}")
            return None
    
    def connect_ssh(self, username="root", key_file=None, password=None):
        """Connect to HA via SSH."""
        
        print(f"\n🔌 Connecting to {self.ha_ip} via SSH...")
        
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            if key_file and Path(key_file).exists():
                # Try key-based authentication
                self.ssh_client.connect(
                    hostname=self.ha_ip,
                    username=username,
                    key_filename=key_file,
                    timeout=10,
                    look_for_keys=False,
                    allow_agent=False
                )
                print(f"✅ Connected via SSH key authentication")
                
            elif password:
                # Try password authentication
                self.ssh_client.connect(
                    hostname=self.ha_ip,
                    username=username,
                    password=password,
                    timeout=10,
                    look_for_keys=False,
                    allow_agent=False
                )
                print(f"✅ Connected via password authentication")
                
            else:
                # Try default authentication methods
                self.ssh_client.connect(
                    hostname=self.ha_ip,
                    username=username,
                    timeout=10
                )
                print(f"✅ Connected via default authentication")
            
            return True
            
        except paramiko.AuthenticationException:
            print(f"❌ SSH authentication failed!")
            print(f"   Please ensure SSH is enabled on your HA instance")
            print(f"   Try: Settings → Add-ons → Terminal & SSH")
            return False
            
        except Exception as e:
            print(f"❌ SSH connection failed: {e}")
            return False
    
    def get_devices_and_entities(self):
        """Get all devices and entities from HA via SSH."""
        
        if not self.ssh_client:
            print("❌ Not connected to SSH")
            return None
        
        print(f"\n📊 Pulling device and entity information...")
        
        try:
            # Execute command to get HA state
            stdin, stdout, stderr = self.ssh_client.exec_command(
                "ha core info --format json"
            )
            
            core_info = json.loads(stdout.read().decode())
            
            # Get all states via API call
            stdin, stdout, stderr = self.ssh_client.exec_command(
                'curl -s -H "Authorization: Bearer $(cat /config/.storage/auth | jq -r \'.data.refresh_tokens[0].token\')" '
                'http://localhost:8123/api/states'
            )
            
            states = json.loads(stdout.read().decode())
            
            # Process entity information
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
            output_dir = self.local_path / "agent_data"
            output_dir.mkdir(exist_ok=True)
            
            # Save all entities
            with open(output_dir / "all_entities.json", "w") as f:
                json.dump(all_entities, f, indent=2)
            
            # Save devices by domain
            with open(output_dir / "devices_by_domain.json", "w") as f:
                json.dump(devices_by_domain, f, indent=2)
            
            # Save summary
            summary = {
                "total_entities": len(all_entities),
                "domains": list(devices_by_domain.keys()),
                "entities_by_domain": {domain: len(entities) for domain, entities in devices_by_domain.items()},
                "ha_version": core_info.get("version"),
                "retrieved_at": datetime.now().isoformat()
            }
            
            with open(output_dir / "summary.json", "w") as f:
                json.dump(summary, f, indent=2)
            
            print(f"✅ Retrieved {len(all_entities)} entities from HA!")
            print(f"\n📊 Summary:")
            print(f"   Total Entities: {summary['total_entities']}")
            print(f"   HA Version: {summary['ha_version']}")
            print(f"\n   Entities by Domain:")
            
            for domain, count in sorted(summary['entities_by_domain'].items(), key=lambda x: -x[1])[:10]:
                print(f"      {domain}: {count}")
            
            print(f"\n💾 Data saved to: {output_dir}")
            
            return summary
            
        except Exception as e:
            print(f"❌ Failed to get device info: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_live_sensors(self):
        """Get live sensor data from HA."""
        
        if not self.ssh_client:
            print("❌ Not connected to SSH")
            return None
        
        print(f"\n📡 Getting live sensor data...")
        
        try:
            # Get sensor states
            stdin, stdout, stderr = self.ssh_client.exec_command(
                'ha core state'
            )
            
            output = stdout.read().decode()
            
            print("✅ Live sensor data retrieved")
            print(output[:500])  # Print first 500 chars
            
            return output
            
        except Exception as e:
            print(f"❌ Failed to get live sensors: {e}")
            return None
    
    def close(self):
        """Close SSH connection."""
        if self.ssh_client:
            self.ssh_client.close()
            print("\n🔌 SSH connection closed")


def main():
    parser = argparse.ArgumentParser(description="HA Sync & SSH Agent")
    parser.add_argument("--ip", default="192.168.10.6", help="HA IP address")
    parser.add_argument("--sync", action="store_true", help="Sync from Samba share")
    parser.add_argument("--ssh", action="store_true", help="Connect via SSH and pull data")
    parser.add_argument("--username", default="root", help="SSH username")
    parser.add_argument("--password", help="SSH password (if not using key)")
    parser.add_argument("--all", action="store_true", help="Do everything (sync + ssh)")
    
    args = parser.parse_args()
    
    # Create agent
    agent = HASyncAgent(ha_ip=args.ip)
    
    try:
        # Sync from Samba if requested
        if args.sync or args.all:
            agent.sync_from_samba()
        
        # SSH operations if requested
        if args.ssh or args.all:
            # Setup SSH key (if needed)
            key_file = agent.setup_ssh_key()
            
            # Try to connect
            connected = agent.connect_ssh(
                username=args.username,
                key_file=key_file,
                password=args.password
            )
            
            if connected:
                # Get device and entity information
                agent.get_devices_and_entities()
                
                # Get live sensor data
                agent.get_live_sensors()
        
        if not (args.sync or args.ssh or args.all):
            print("Please specify --sync, --ssh, or --all")
            print("Example: python ha_sync_agent.py --all")
    
    finally:
        agent.close()


if __name__ == "__main__":
    main()

