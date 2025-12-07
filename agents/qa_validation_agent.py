#!/usr/bin/env python3
"""
Agent 7 — QA / Validation Agent
===============================
Quality assurance for observability:
- Verification checklist for charts (units, timezones, gaps)
- Drilldown resolution testing
- Control safety verification
- "Known good" sanity thresholds
- Alarms for missing data
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Any
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("QAValidationAgent")


class CheckStatus(Enum):
    PASS = "pass"
    FAIL = "fail"
    WARN = "warning"


class CheckCategory(Enum):
    CHART_ACCURACY = "chart_accuracy"
    DATA_QUALITY = "data_quality"
    DRILLDOWN = "drilldown"
    CONTROL_SAFETY = "control_safety"


@dataclass
class ValidationResult:
    check_id: str
    name: str
    category: CheckCategory
    status: CheckStatus
    message: str
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SanityThreshold:
    name: str
    entity_id: str
    min_value: float = None
    max_value: float = None
    expected_unit: str = None
    critical: bool = False


class QAValidationAgent:
    """Agent 7 - QA / Validation"""
    
    def __init__(self):
        self.thresholds = self._get_default_thresholds()
    
    def _get_default_thresholds(self) -> List[SanityThreshold]:
        return [
            SanityThreshold("Total Power", "sensor.total_power", 0, 10000, "W", True),
            SanityThreshold("Printer Power", "sensor.bambu_printer_power", 0, 500, "W"),
            SanityThreshold("Internet Ping", "sensor.speedtest_ping", 0, 200, "ms"),
            SanityThreshold("Download Speed", "sensor.speedtest_download", 0, 10000, "Mbit/s"),
            SanityThreshold("Daily Cost", "sensor.daily_energy_cost", 0, 100, "$"),
        ]
    
    def generate_checklist(self) -> str:
        return """
# NOC Observability QA Checklist

## 📊 Chart Accuracy
- [ ] All power sensors show "W" or "kW"
- [ ] All energy sensors show "Wh" or "kWh"
- [ ] Temperature sensors show "°C" or "°F"
- [ ] Network speeds show "Mbps" or "Gbps"
- [ ] Cost values show "$" or currency symbol

## 🔍 Timezone Consistency
- [ ] HA timezone matches local timezone
- [ ] Grafana timezone set correctly
- [ ] No unexpected time shifts in data

## 📈 Data Gaps
- [ ] No sensors stuck in "unavailable"
- [ ] No sensors with stale data (>1 hour old)
- [ ] Missing data alerts configured

## 🔗 Drilldowns
- [ ] All dashboard links resolve correctly
- [ ] Variables pass through drilldowns
- [ ] Back navigation works

## ⚙️ Control Safety
- [ ] Dangerous actions require confirmation
- [ ] Cooldown periods enforced
- [ ] All actions audit logged

## 🚨 Known-Good Thresholds
| Metric | Min | Max | Unit | Critical |
|--------|-----|-----|------|----------|
| Total Power | 0 | 10000 | W | Yes |
| Printer Power | 0 | 500 | W | No |
| Internet Ping | 0 | 200 | ms | Yes |
| Download Speed | 10 | 10000 | Mbps | Yes |
| Daily Cost | 0 | 100 | $ | No |
"""
    
    def generate_alert_config(self) -> str:
        return """
# Missing Data Alert Configuration

automation:
  - alias: "Alert - Critical Sensor Unavailable"
    trigger:
      - platform: state
        entity_id:
          - sensor.total_power
          - sensor.speedtest_download
        to: 'unavailable'
        for:
          minutes: 5
    action:
      - service: notify.notify
        data:
          title: "🚨 Critical Sensor Unavailable"
          message: "{{ trigger.entity_id }} unavailable for 5 minutes"

  - alias: "Alert - Network Offline"
    trigger:
      - platform: state
        entity_id: binary_sensor.internet_connection
        to: 'off'
        for:
          minutes: 2
    action:
      - service: notify.notify
        data:
          title: "🔴 Internet Offline"
          message: "Internet connection lost"
"""
    
    def get_summary(self) -> Dict[str, Any]:
        return {
            "validation_categories": [c.value for c in CheckCategory],
            "default_thresholds": len(self.thresholds),
            "checks": [
                "Chart units verification",
                "Timezone consistency",
                "Data gaps detection",
                "Drilldown resolution",
                "Control safety verification",
                "Missing data alarms"
            ]
        }


def main():
    print("\n" + "="*60)
    print("  AGENT 7 - QA / VALIDATION")
    print("  Observability verification & sanity checks")
    print("="*60 + "\n")
    
    agent = QAValidationAgent()
    
    output_dir = Path(__file__).parent / "config"
    output_dir.mkdir(exist_ok=True)
    
    # Save checklist
    with open(output_dir / "qa_checklist.md", 'w', encoding='utf-8') as f:
        f.write(agent.generate_checklist())
    print(f"   ✅ Saved QA checklist")
    
    # Save alert config
    with open(output_dir / "qa_alerts.yaml", 'w', encoding='utf-8') as f:
        f.write(agent.generate_alert_config())
    print(f"   ✅ Saved alert config")
    
    # Save thresholds
    thresholds = {
        "thresholds": [
            {"name": t.name, "entity_id": t.entity_id, "min": t.min_value, "max": t.max_value, "unit": t.expected_unit, "critical": t.critical}
            for t in agent.thresholds
        ]
    }
    with open(output_dir / "qa_thresholds.json", 'w') as f:
        json.dump(thresholds, f, indent=2)
    print(f"   ✅ Saved thresholds")
    
    print("""
🔍 Validation Categories:
   📊 Chart Accuracy - Units, timezones, gaps
   📈 Data Quality - Sanity thresholds
   🔗 Drilldowns - Link resolution
   ⚙️ Control Safety - Confirmations, cooldowns
   🚨 Alert Health - Missing data alarms

📋 Default Sanity Thresholds:
""")
    for t in agent.thresholds:
        flag = "🔴" if t.critical else "🟢"
        print(f"   {flag} {t.name}: {t.min_value}-{t.max_value} {t.expected_unit or ''}")


if __name__ == "__main__":
    main()
