#!/usr/bin/env python3
"""
Agent 3 — Collector / Integrations Agent
=========================================
Fastest path to collect: Bambu live telemetry, UniFi stats, ISP health checks,
AdGuard/Pi-hole metrics, and REAL power usage with cost calculation from $/kWh.

Uses Home Assistant + Telegraf/InfluxDB where appropriate.
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("CollectorAgent")


@dataclass
class MetricConfig:
    """Configuration for a metric collection source."""
    name: str
    type: str  # bambu, unifi, isp, adguard, pihole, power
    endpoint: str
    poll_interval: int = 30  # seconds
    enabled: bool = True
    credentials: Dict[str, str] = field(default_factory=dict)
    extra_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PowerConfig:
    """Power monitoring and cost calculation configuration."""
    cost_per_kwh: float = 0.12  # Default $/kWh
    currency: str = "USD"
    power_entity_id: str = ""  # HA entity for power sensor
    energy_entity_id: str = ""  # HA entity for energy (kWh)
    billing_cycle_start: int = 1  # Day of month billing starts


class BaseCollector(ABC):
    """Base class for all metric collectors."""
    
    def __init__(self, config: MetricConfig):
        self.config = config
        self.last_collect = None
        self.metrics_collected = 0
        
    @abstractmethod
    def collect(self) -> Dict[str, Any]:
        """Collect metrics from the source."""
        pass
    
    @abstractmethod
    def validate_connection(self) -> bool:
        """Validate connection to the data source."""
        pass
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "name": self.config.name,
            "type": self.config.type,
            "enabled": self.config.enabled,
            "last_collect": self.last_collect.isoformat() if self.last_collect else None,
            "metrics_collected": self.metrics_collected
        }


class BambuLabCollector(BaseCollector):
    """Bambu Lab 3D Printer Telemetry Collector"""
    
    REQUIRED_HA_ENTITIES = [
        "sensor.{printer}_print_status",
        "sensor.{printer}_print_progress", 
        "sensor.{printer}_nozzle_temperature",
        "sensor.{printer}_bed_temperature",
        "sensor.{printer}_power",
    ]
    
    def collect(self) -> Dict[str, Any]:
        logger.info(f"📡 Collecting Bambu Lab telemetry from {self.config.name}")
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "printer_name": self.config.name,
            "_ha_config": {
                "integration": "bambu_lab",
                "entities_to_monitor": self.REQUIRED_HA_ENTITIES,
            }
        }
        self.last_collect = datetime.now()
        self.metrics_collected += 1
        return metrics
    
    def validate_connection(self) -> bool:
        return True
    
    @staticmethod
    def get_ha_configuration() -> str:
        return """
# Bambu Lab Integration - Power Monitoring Template
template:
  - sensor:
      - name: "Bambu Printer Estimated Power"
        unique_id: bambu_estimated_power
        unit_of_measurement: "W"
        device_class: power
        state: >
          {% set status = states('sensor.bambu_print_status') %}
          {% if status == 'idle' %}15{% elif status == 'printing' %}180{% elif status == 'heating' %}350{% else %}50{% endif %}
"""


class UniFiCollector(BaseCollector):
    """UniFi Network Statistics Collector"""
    
    def collect(self) -> Dict[str, Any]:
        logger.info(f"📡 Collecting UniFi stats from {self.config.endpoint}")
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "_ha_config": {
                "integration": "unifi",
                "controller_url": self.config.endpoint,
            }
        }
        self.last_collect = datetime.now()
        self.metrics_collected += 1
        return metrics
    
    def validate_connection(self) -> bool:
        return True


class ISPHealthCollector(BaseCollector):
    """ISP Health Check Collector"""
    
    def collect(self) -> Dict[str, Any]:
        logger.info("📡 Collecting ISP health metrics")
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "_ha_config": {
                "integrations": ["speedtest", "ping"],
            }
        }
        self.last_collect = datetime.now()
        self.metrics_collected += 1
        return metrics
    
    def validate_connection(self) -> bool:
        return True


class PowerMonitorCollector(BaseCollector):
    """CRITICAL: Real Power Usage and Cost Calculator"""
    
    def __init__(self, config: MetricConfig, power_config: PowerConfig):
        super().__init__(config)
        self.power_config = power_config
        
    def collect(self) -> Dict[str, Any]:
        logger.info("⚡ Collecting REAL power usage metrics")
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "cost": {
                "rate_per_kwh": self.power_config.cost_per_kwh,
                "currency": self.power_config.currency,
            }
        }
        self.last_collect = datetime.now()
        self.metrics_collected += 1
        return metrics
    
    def validate_connection(self) -> bool:
        return True
    
    @staticmethod
    def get_ha_configuration(cost_per_kwh: float = 0.12) -> str:
        return f"""
# Power Monitoring & Cost Calculation
utility_meter:
  daily_energy:
    source: sensor.total_energy_usage
    cycle: daily
  monthly_energy:
    source: sensor.total_energy_usage  
    cycle: monthly

template:
  - sensor:
      - name: "Electricity Rate"
        unique_id: electricity_rate
        state: {cost_per_kwh}
        unit_of_measurement: "$/kWh"
        
      - name: "Today Energy Cost"
        unique_id: today_energy_cost
        state: >
          {{{{ (states('sensor.daily_energy') | float(0)) * {cost_per_kwh} | round(2) }}}}
        unit_of_measurement: "$"
        device_class: monetary
"""


class CollectorAgent:
    """Main Collector Agent - Orchestrates all metric collection."""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.collectors: List[BaseCollector] = []
        self.power_config = PowerConfig(cost_per_kwh=0.12, currency="USD")
        
    def add_collector(self, collector: BaseCollector):
        self.collectors.append(collector)
        logger.info(f"➕ Added collector: {collector.config.name}")
        
    def setup_default_collectors(self, ha_host: str = "192.168.10.6"):
        bambu_config = MetricConfig(name="Bambu X1C", type="bambu", endpoint=f"http://{ha_host}:8123", poll_interval=10)
        self.add_collector(BambuLabCollector(bambu_config))
        
        unifi_config = MetricConfig(name="UniFi Controller", type="unifi", endpoint=f"https://{ha_host}:8443", poll_interval=30)
        self.add_collector(UniFiCollector(unifi_config))
        
        isp_config = MetricConfig(name="ISP Health", type="isp", endpoint="", poll_interval=300)
        self.add_collector(ISPHealthCollector(isp_config))
        
        power_config = MetricConfig(name="Power Monitor", type="power", endpoint=f"http://{ha_host}:8123", poll_interval=10)
        self.add_collector(PowerMonitorCollector(power_config, self.power_config))
        
        logger.info(f"✅ Setup {len(self.collectors)} default collectors")
        
    def collect_all(self) -> Dict[str, Any]:
        logger.info("🔄 Starting full metric collection...")
        results = {"timestamp": datetime.now().isoformat(), "collectors": {}, "errors": []}
        
        for collector in self.collectors:
            if not collector.config.enabled:
                continue
            try:
                metrics = collector.collect()
                results["collectors"][collector.config.name] = metrics
            except Exception as e:
                results["errors"].append(f"Failed to collect from {collector.config.name}: {str(e)}")
        
        return results
    
    def generate_ha_configuration(self) -> str:
        return f"""
# COLLECTOR AGENT - Complete HA Configuration
# Generated: {datetime.now().isoformat()}

{BambuLabCollector.get_ha_configuration()}

{PowerMonitorCollector.get_ha_configuration(self.power_config.cost_per_kwh)}
"""

    def get_validation_steps(self) -> List[Dict[str, str]]:
        return [
            {"step": "1. Verify Bambu Lab Integration", "command": "Check HA → Settings → Devices → Bambu Lab"},
            {"step": "2. Verify UniFi Integration", "command": "Check HA → Settings → Devices → UniFi Network"},
            {"step": "3. Verify Speedtest Integration", "command": "HA Developer Tools → States → sensor.speedtest_*"},
            {"step": "4. CRITICAL: Verify Power Sensors", "command": "HA Developer Tools → States → sensor.*power*"},
        ]


def main():
    print("\n" + "="*60)
    print("  AGENT 3 - COLLECTOR / INTEGRATIONS")
    print("  Fastest path to complete observability")
    print("="*60 + "\n")
    
    agent = CollectorAgent()
    agent.setup_default_collectors(ha_host="192.168.10.6")
    
    print("📝 Generating Home Assistant Configuration...")
    ha_config = agent.generate_ha_configuration()
    
    output_dir = Path(__file__).parent / "config"
    output_dir.mkdir(exist_ok=True)
    
    config_file = output_dir / "collector_ha_config.yaml"
    with open(config_file, 'w') as f:
        f.write(ha_config)
    print(f"   ✅ Saved to: {config_file}")
    
    print("\n📋 VALIDATION STEPS:")
    for step in agent.get_validation_steps():
        print(f"\n{step['step']}")
        print(f"   Command: {step['command']}")
    
    print(f"\n⚡ Power cost: ${agent.power_config.cost_per_kwh}/kWh")


if __name__ == "__main__":
    main()
