#!/usr/bin/env python3
"""
Agent 6 — UniFi API Specialist
==============================
Read/write capability map for UniFi device and switch port controls:
- Per-port status, PoE power, enable/disable
- Client mapping, auth approach, safe implementation patterns
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("UniFiAPIAgent")


class PoEMode(Enum):
    OFF = "off"
    AUTO = "auto"
    PASSIVE24V = "pasv24"


@dataclass
class UniFiCredentials:
    host: str
    username: str
    password: str
    port: int = 443
    site: str = "default"
    verify_ssl: bool = False


class UniFiAPIEndpoints:
    LOGIN = "/api/auth/login"
    DEVICES = "/proxy/network/api/s/{site}/stat/device"
    CLIENTS = "/proxy/network/api/s/{site}/stat/sta"
    HEALTH = "/proxy/network/api/s/{site}/stat/health"
    CMD_DEVMGR = "/proxy/network/api/s/{site}/cmd/devmgr"


class UniFiCapabilityMap:
    """Complete UniFi API Capability Reference"""
    
    @staticmethod
    def get_full_capability_map() -> Dict[str, Any]:
        return {
            "meta": {"title": "UniFi API Capability Map", "version": "1.0.0"},
            
            "authentication": {
                "methods": [{"name": "Local Admin", "endpoint": "/api/auth/login", "recommended": True}],
                "best_practices": [
                    "Create dedicated API user",
                    "Use local authentication (not SSO)",
                    "Store credentials in secrets.yaml"
                ]
            },
            
            "read_capabilities": {
                "devices": ["Device info (name, model, MAC, IP)", "Uptime and load", "Port table with statistics", "PoE power per port"],
                "switch_ports": ["Port status (up/down)", "Speed and duplex", "PoE mode and power (watts)", "RX/TX stats"],
                "clients": ["MAC and IP addresses", "Connected switch port", "TX/RX rates"]
            },
            
            "write_capabilities": {
                "port_control": {
                    "enable_disable_port": {"field": "port_overrides[].port_security_enabled", "safe": True},
                    "set_poe_mode": {"field": "port_overrides[].poe_mode", "values": ["off", "auto", "pasv24"], "safe": True},
                },
                "device_control": {
                    "restart": {"cmd": "restart", "mac": "<device_mac>"},
                }
            },
            
            "safe_patterns": {
                "rate_limiting": "Max 1 write/second",
                "error_handling": "Exponential backoff",
                "validation": "Always verify target exists before write"
            }
        }
    
    @staticmethod
    def get_ha_integration_guide() -> str:
        return """
# UniFi API Integration for Home Assistant

## REST Commands for Port Control
```yaml
rest_command:
  unifi_set_poe:
    url: "https://{{ host }}/proxy/network/api/s/{{ site }}/rest/device/{{ device_id }}"
    method: PUT
    verify_ssl: false
    payload: '{"port_overrides":[{"port_idx":{{ port }},"poe_mode":"{{ mode }}"}]}'
```

## Quick Start
```bash
# Test UniFi API connection
curl -k -X POST https://192.168.1.1/api/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{"username":"admin","password":"password"}' \\
  -c cookies.txt
```
"""


class UniFiAPIAgent:
    """Agent 6 - UniFi API Specialist"""
    
    def __init__(self, credentials: Optional[UniFiCredentials] = None):
        self.credentials = credentials
        self.capability_map = UniFiCapabilityMap()
    
    def get_capability_reference(self) -> Dict[str, Any]:
        return self.capability_map.get_full_capability_map()
    
    def get_ha_integration_guide(self) -> str:
        return self.capability_map.get_ha_integration_guide()
    
    def generate_ha_config(self) -> str:
        return """
# UniFi NOC Integration Configuration

rest_command:
  unifi_set_poe:
    url: "https://{{ host }}/proxy/network/api/s/{{ site }}/rest/device/{{ device_id }}"
    method: PUT
    verify_ssl: false
    payload: '{"port_overrides":[{"port_idx":{{ port }},"poe_mode":"{{ mode }}"}]}'

  unifi_restart_device:
    url: "https://{{ host }}/proxy/network/api/s/{{ site }}/cmd/devmgr"
    method: POST
    verify_ssl: false
    payload: '{"cmd":"restart","mac":"{{ mac }}"}'

script:
  unifi_toggle_poe:
    alias: "Toggle PoE on Port"
    sequence:
      - service: rest_command.unifi_set_poe
        data:
          host: !secret unifi_host
          site: "default"
          device_id: !secret unifi_switch_id
          port: "{{ port }}"
          mode: "{{ mode }}"
"""

    def generate_port_sensors(self, num_ports: int = 24) -> str:
        return f"""
# UniFi Switch Port Monitoring Sensors

template:
  - sensor:
      - name: "UniFi Switch Total PoE Power"
        unique_id: unifi_switch_total_poe_power
        unit_of_measurement: "W"
        device_class: power
        state: >
          {{{{ states.sensor 
             | selectattr('entity_id', 'search', 'unifi_port_.*_poe_power')
             | map(attribute='state')
             | map('float', 0)
             | sum | round(1) }}}}
"""


def main():
    print("\n" + "="*60)
    print("  AGENT 6 - UNIFI API SPECIALIST")
    print("  Per-port control and monitoring")
    print("="*60 + "\n")
    
    agent = UniFiAPIAgent()
    
    output_dir = Path(__file__).parent / "config"
    output_dir.mkdir(exist_ok=True)
    
    # Save capability map
    with open(output_dir / "unifi_capability_map.json", 'w') as f:
        json.dump(agent.get_capability_reference(), f, indent=2)
    print(f"   ✅ Saved capability map")
    
    # Save HA config
    with open(output_dir / "unifi_ha_config.yaml", 'w') as f:
        f.write(agent.generate_ha_config())
    print(f"   ✅ Saved HA config")
    
    # Save integration guide
    with open(output_dir / "unifi_ha_integration.md", 'w') as f:
        f.write(agent.get_ha_integration_guide())
    print(f"   ✅ Saved integration guide")
    
    print("""
🔍 READ Capabilities:
   ✅ Device info, uptime, firmware
   ✅ Per-port status (speed, duplex)
   ✅ PoE power per port (watts)
   ✅ Client list with port mapping

✏️ WRITE Capabilities:
   ✅ Enable/disable ports
   ✅ Set PoE mode (off, auto, pasv24)
   ✅ Restart devices
""")


if __name__ == "__main__":
    main()
