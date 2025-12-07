#!/usr/bin/env python3
"""
Agent 4 — Dashboard / UX Agent
==============================
Grafana dashboard designer for NOCv3 information architecture:
- 30k overview → section drilldowns → device drilldowns → UniFi switch port drilldowns
- Uses variables and consistent navigation
- Prioritizes charts and historical context, plus "live now" panels
"""

import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Any
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DashboardUXAgent")


class PanelType(Enum):
    STAT = "stat"
    GAUGE = "gauge"
    TIMESERIES = "timeseries"
    TABLE = "table"
    BAR_GAUGE = "bargauge"
    PIE_CHART = "piechart"
    STATE_TIMELINE = "state-timeline"


class DrilldownLevel(Enum):
    OVERVIEW = "30k_overview"
    SECTION = "section_drilldown"
    DEVICE = "device_drilldown"
    PORT = "port_drilldown"


@dataclass
class Panel:
    title: str
    type: PanelType
    description: str = ""
    width: int = 6
    height: int = 8
    links: List[Dict[str, str]] = field(default_factory=list)


@dataclass
class Row:
    title: str
    panels: List[Panel] = field(default_factory=list)
    collapsed: bool = False


@dataclass
class Dashboard:
    title: str
    uid: str
    level: DrilldownLevel
    description: str = ""
    tags: List[str] = field(default_factory=list)
    refresh: str = "30s"
    rows: List[Row] = field(default_factory=list)
    links: List[Dict[str, str]] = field(default_factory=list)


class NOCv3Architecture:
    """NOCv3 Information Architecture Designer"""
    
    COLORS = {
        "ok": "#73BF69", "warning": "#FADE2A", "critical": "#F2495C",
        "info": "#5794F2", "offline": "#9D70F9", "power": "#FF9830"
    }
    
    THRESHOLDS = {
        "percentage": {"steps": [{"value": 0, "color": "green"}, {"value": 80, "color": "yellow"}, {"value": 95, "color": "red"}]},
        "latency_ms": {"steps": [{"value": 0, "color": "green"}, {"value": 50, "color": "yellow"}, {"value": 100, "color": "red"}]},
    }
    
    def __init__(self):
        self.dashboards: Dict[str, Dashboard] = {}
        
    def create_overview_dashboard(self) -> Dashboard:
        dashboard = Dashboard(
            title="🏠 NOC Overview", uid="noc-overview", level=DrilldownLevel.OVERVIEW,
            description="30k foot view", tags=["noc", "overview"], refresh="30s"
        )
        
        status_row = Row(title="📊 System Status", panels=[
            Panel(title="Overall Health", type=PanelType.STAT, width=4, height=4),
            Panel(title="Active Alerts", type=PanelType.STAT, width=4, height=4),
            Panel(title="Network Status", type=PanelType.STAT, width=4, height=4, links=[{"title": "→ Network", "url": "/d/noc-network"}]),
            Panel(title="Power Usage NOW", type=PanelType.GAUGE, width=4, height=4, links=[{"title": "→ Power", "url": "/d/noc-power"}]),
            Panel(title="ISP Status", type=PanelType.STAT, width=4, height=4, links=[{"title": "→ ISP", "url": "/d/noc-isp"}]),
            Panel(title="Printer Status", type=PanelType.STAT, width=4, height=4, links=[{"title": "→ Printer", "url": "/d/noc-printer"}]),
        ])
        
        live_row = Row(title="🔴 LIVE NOW", panels=[
            Panel(title="Network Traffic", type=PanelType.TIMESERIES, width=8, height=6),
            Panel(title="Power Draw", type=PanelType.TIMESERIES, width=8, height=6),
            Panel(title="Active Devices", type=PanelType.STAT, width=4, height=3),
            Panel(title="Print Progress", type=PanelType.GAUGE, width=4, height=3),
        ])
        
        dashboard.rows = [status_row, live_row]
        dashboard.links = [
            {"title": "🌐 Network", "url": "/d/noc-network"},
            {"title": "⚡ Power", "url": "/d/noc-power"},
            {"title": "🖨️ Printer", "url": "/d/noc-printer"},
        ]
        
        self.dashboards["overview"] = dashboard
        return dashboard
    
    def create_network_dashboard(self) -> Dashboard:
        dashboard = Dashboard(
            title="🌐 Network - NOC", uid="noc-network", level=DrilldownLevel.SECTION,
            tags=["noc", "network", "unifi"], refresh="10s"
        )
        
        status_row = Row(title="🔴 Network Status", panels=[
            Panel(title="Gateway Status", type=PanelType.STAT, width=4, height=4),
            Panel(title="Switch Status", type=PanelType.STAT, width=4, height=4),
            Panel(title="Total Clients", type=PanelType.STAT, width=4, height=4),
            Panel(title="PoE Power Total", type=PanelType.GAUGE, width=4, height=4),
        ])
        
        dashboard.rows = [status_row]
        self.dashboards["network"] = dashboard
        return dashboard
    
    def create_power_dashboard(self) -> Dashboard:
        dashboard = Dashboard(
            title="⚡ Power - NOC", uid="noc-power", level=DrilldownLevel.SECTION,
            tags=["noc", "power", "energy", "cost"], refresh="10s"
        )
        
        current_row = Row(title="🔴 POWER NOW", panels=[
            Panel(title="Total Power Draw", type=PanelType.GAUGE, width=6, height=6),
            Panel(title="By Device", type=PanelType.PIE_CHART, width=6, height=6),
            Panel(title="Power History (1h)", type=PanelType.TIMESERIES, width=12, height=6),
        ])
        
        cost_row = Row(title="💰 Cost Tracking", panels=[
            Panel(title="Today's Cost", type=PanelType.STAT, width=4, height=4),
            Panel(title="This Month", type=PanelType.STAT, width=4, height=4),
            Panel(title="Projected Monthly", type=PanelType.STAT, width=4, height=4),
        ])
        
        dashboard.rows = [current_row, cost_row]
        self.dashboards["power"] = dashboard
        return dashboard
    
    def create_printer_dashboard(self) -> Dashboard:
        dashboard = Dashboard(
            title="🖨️ Bambu Lab - NOC", uid="noc-printer", level=DrilldownLevel.DEVICE,
            tags=["noc", "printer", "bambu"], refresh="5s"
        )
        
        live_row = Row(title="🔴 PRINT STATUS NOW", panels=[
            Panel(title="Print Status", type=PanelType.STAT, width=4, height=4),
            Panel(title="Progress", type=PanelType.GAUGE, width=4, height=4),
            Panel(title="ETA", type=PanelType.STAT, width=4, height=4),
            Panel(title="Current Cost", type=PanelType.STAT, width=4, height=4),
        ])
        
        temp_row = Row(title="🌡️ Temperatures", panels=[
            Panel(title="Nozzle Temp", type=PanelType.GAUGE, width=6, height=5),
            Panel(title="Bed Temp", type=PanelType.GAUGE, width=6, height=5),
        ])
        
        dashboard.rows = [live_row, temp_row]
        self.dashboards["printer"] = dashboard
        return dashboard
    
    def build_all_dashboards(self) -> Dict[str, Dashboard]:
        logger.info("🎨 Building NOCv3 Dashboard Suite...")
        self.create_overview_dashboard()
        self.create_network_dashboard()
        self.create_power_dashboard()
        self.create_printer_dashboard()
        logger.info(f"✅ Built {len(self.dashboards)} dashboards")
        return self.dashboards
    
    def export_blueprint(self) -> Dict[str, Any]:
        blueprint = {
            "meta": {"name": "NOCv3 Dashboard Suite", "version": "1.0.0", "generated": datetime.now().isoformat()},
            "architecture": {
                "levels": [level.value for level in DrilldownLevel],
                "hierarchy": {"overview": ["network", "power", "printer"]},
            },
            "design_principles": [
                "30k overview at top level",
                "Progressive drilldowns",
                "LIVE NOW sections at top",
                "Historical context (collapsed)",
                "Consistent color coding",
            ],
            "dashboards": {
                name: {
                    "title": d.title, "uid": d.uid, "level": d.level.value,
                    "panel_count": sum(len(row.panels) for row in d.rows),
                }
                for name, d in self.dashboards.items()
            }
        }
        return blueprint


class DashboardUXAgent:
    """Agent 4 - Dashboard/UX Designer"""
    
    def __init__(self):
        self.architecture = NOCv3Architecture()
        
    def design_complete_suite(self) -> Dict[str, Any]:
        self.architecture.build_all_dashboards()
        blueprint = self.architecture.export_blueprint()
        return {"blueprint": blueprint, "total_dashboards": len(self.architecture.dashboards)}


def main():
    print("\n" + "="*60)
    print("  AGENT 4 - DASHBOARD / UX DESIGNER")
    print("  NOCv3 Information Architecture")
    print("="*60 + "\n")
    
    agent = DashboardUXAgent()
    result = agent.design_complete_suite()
    
    output_dir = Path(__file__).parent / "config"
    output_dir.mkdir(exist_ok=True)
    
    blueprint_file = output_dir / "nocv3_blueprint.json"
    with open(blueprint_file, 'w') as f:
        json.dump(result["blueprint"], f, indent=2)
    print(f"   ✅ Blueprint saved to: {blueprint_file}")
    
    print(f"\nDashboards Created: {result['total_dashboards']}")
    print("""
Dashboard Hierarchy:
├── 🏠 NOC Overview (30k view)
│   ├── 🌐 Network Drilldown
│   ├── ⚡ Power Drilldown
│   └── 🖨️ Printer Drilldown
""")


if __name__ == "__main__":
    main()
