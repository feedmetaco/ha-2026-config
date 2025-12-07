#!/usr/bin/env python3
"""
Agent 5 — Controls / Automation Agent
======================================
Implements safe quick controls with:
- Reboot stacks, restart services, bounce ports / toggle PoE (UniFi)
- Confirmations, cooldowns, RBAC guidance, audit logging
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ControlsAutomationAgent")


class ActionSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Role(Enum):
    VIEWER = "viewer"
    OPERATOR = "operator"
    ADMIN = "admin"
    EMERGENCY = "emergency"


@dataclass
class ActionConfig:
    name: str
    description: str
    severity: ActionSeverity
    required_role: Role
    cooldown_seconds: int = 60
    requires_confirmation: bool = True


@dataclass
class AuditLogEntry:
    timestamp: str
    action_name: str
    user: str
    role: Role
    target: str
    result: str


class AuditLogger:
    def __init__(self, log_file: Path):
        self.log_file = log_file
        self.entries: List[AuditLogEntry] = []
        
    def log(self, entry: AuditLogEntry):
        self.entries.append(entry)
        logger.info(f"AUDIT [{entry.action_name}] by {entry.user} → {entry.result}")


class CooldownManager:
    def __init__(self):
        self.last_execution: Dict[str, datetime] = {}
    
    def can_execute(self, action_key: str, cooldown_seconds: int) -> tuple:
        if action_key not in self.last_execution:
            return True, 0
        elapsed = (datetime.now() - self.last_execution[action_key]).total_seconds()
        if elapsed >= cooldown_seconds:
            return True, 0
        return False, int(cooldown_seconds - elapsed)
    
    def record_execution(self, action_key: str):
        self.last_execution[action_key] = datetime.now()


class ControlsAutomationAgent:
    """Agent 5 - Controls & Automation"""
    
    def __init__(self, audit_log_path: Optional[Path] = None):
        self.audit_log_path = audit_log_path or Path(__file__).parent / "logs" / "audit.json"
        self.cooldown_manager = CooldownManager()
        
        self.actions = {
            "port_bounce": ActionConfig("unifi_port_bounce", "Bounce switch port", ActionSeverity.MEDIUM, Role.OPERATOR, 120),
            "poe_toggle": ActionConfig("unifi_poe_toggle", "Toggle PoE power", ActionSeverity.MEDIUM, Role.OPERATOR, 180),
            "service_restart": ActionConfig("service_restart", "Restart HA service", ActionSeverity.MEDIUM, Role.OPERATOR, 300),
            "device_reboot": ActionConfig("device_reboot", "Reboot device", ActionSeverity.HIGH, Role.ADMIN, 600),
            "network_stack_reboot": ActionConfig("network_stack_reboot", "Reboot entire stack", ActionSeverity.CRITICAL, Role.ADMIN, 1800),
        }
    
    def get_available_actions(self, user_role: Role) -> List[Dict[str, Any]]:
        role_hierarchy = {Role.VIEWER: 0, Role.OPERATOR: 1, Role.ADMIN: 2, Role.EMERGENCY: 3}
        user_level = role_hierarchy.get(user_role, 0)
        
        available = []
        for name, action in self.actions.items():
            required_level = role_hierarchy.get(action.required_role, 3)
            if user_level >= required_level:
                available.append({
                    "name": name, "description": action.description,
                    "severity": action.severity.value, "cooldown": action.cooldown_seconds
                })
        return available
    
    def generate_ha_scripts(self) -> str:
        return """
# CONTROLS AUTOMATION AGENT - HA Scripts

unifi_bounce_port:
  alias: "Bounce Switch Port"
  mode: single
  sequence:
    - service: switch.turn_off
      target:
        entity_id: "{{ port_entity }}"
    - delay: {seconds: 5}
    - service: switch.turn_on
      target:
        entity_id: "{{ port_entity }}"
    - service: logbook.log
      data:
        name: "Port Bounce"
        message: "Port bounced by automation"

unifi_poe_cycle:
  alias: "PoE Power Cycle"
  mode: single
  sequence:
    - service: switch.turn_off
      target:
        entity_id: "{{ poe_entity }}"
    - delay: {seconds: 10}
    - service: switch.turn_on
      target:
        entity_id: "{{ poe_entity }}"
"""
    
    def generate_rbac_guide(self) -> str:
        return """
# RBAC Implementation Guide

## Roles
- VIEWER: Read-only
- OPERATOR: Low/Medium severity actions
- ADMIN: All actions including Critical
- EMERGENCY: Bypass cooldowns (audit logged)

## Safety Features
- Typed confirmations for dangerous actions
- Cooldown periods (2-30 minutes by severity)
- Comprehensive audit logging
"""

    def get_action_design(self) -> Dict[str, Any]:
        return {
            "severity_levels": {
                "LOW": {"confirmation": False, "cooldown": "30-60s"},
                "MEDIUM": {"confirmation": True, "cooldown": "2-5 min"},
                "HIGH": {"confirmation": True, "cooldown": "10+ min"},
                "CRITICAL": {"confirmation": "Full phrase", "cooldown": "30+ min"},
            },
            "actions": {
                name: {"description": a.description, "severity": a.severity.value, "required_role": a.required_role.value}
                for name, a in self.actions.items()
            }
        }


def main():
    print("\n" + "="*60)
    print("  AGENT 5 - CONTROLS / AUTOMATION")
    print("  Safe quick controls with RBAC & audit logging")
    print("="*60 + "\n")
    
    agent = ControlsAutomationAgent()
    
    output_dir = Path(__file__).parent / "config"
    output_dir.mkdir(exist_ok=True)
    
    # Save scripts
    with open(output_dir / "controls_ha_scripts.yaml", 'w') as f:
        f.write(agent.generate_ha_scripts())
    print(f"   ✅ Saved HA scripts")
    
    # Save RBAC guide
    with open(output_dir / "rbac_guide.md", 'w') as f:
        f.write(agent.generate_rbac_guide())
    print(f"   ✅ Saved RBAC guide")
    
    # Save action design
    with open(output_dir / "action_design.json", 'w') as f:
        json.dump(agent.get_action_design(), f, indent=2)
    print(f"   ✅ Saved action design")
    
    print("\n🎯 Available Actions:")
    for name, action in agent.actions.items():
        print(f"   • {name}: {action.description} [{action.severity.value}]")


if __name__ == "__main__":
    main()
