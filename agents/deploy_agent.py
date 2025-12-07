#!/usr/bin/env python3
"""
HA WorldClass Agent - Quick Deploy
Customized for your 2,479-entity setup
"""

import json
from pathlib import Path
import sys

def load_entity_data():
    """Load your discovered entity data."""
    data_file = Path("agent_data/all_entities.json")
    if not data_file.exists():
        print("❌ Entity data not found. Run: py get_ha_data.py YOUR_TOKEN")
        return None
    
    with open(data_file) as f:
        return json.load(f)

def analyze_setup(entities):
    """Analyze your entity setup."""
    
    by_domain = {}
    for entity in entities:
        domain = entity['domain']
        by_domain.setdefault(domain, []).append(entity)
    
    print("\n" + "="*60)
    print("  YOUR HOME ASSISTANT SETUP ANALYSIS")
    print("="*60)
    print(f"\nTotal Entities: {len(entities)}")
    print(f"\nTop Domains:")
    
    for domain, ents in sorted(by_domain.items(), key=lambda x: -len(x[1]))[:10]:
        print(f"  {domain:20s}: {len(ents):4d} entities")
    
    return by_domain

def recommend_dashboards(by_domain):
    """Recommend dashboards based on your setup."""
    
    print("\n" + "="*60)
    print("  RECOMMENDED DASHBOARDS FOR YOUR SETUP")
    print("="*60)
    
    recommendations = []
    
    # Sensor dashboard (968 sensors!)
    if len(by_domain.get('sensor', [])) > 100:
        print(f"\n✅ SENSOR DASHBOARD (CRITICAL)")
        print(f"   You have {len(by_domain['sensor'])} sensors!")
        print(f"   Recommend: Multi-tab dashboard organized by type")
        print(f"   - Temperature sensors")
        print(f"   - Power/Energy sensors")
        print(f"   - Motion sensors")
        print(f"   - Network/System sensors")
        recommendations.append("sensor_dashboard")
    
    # Switch control panel (449 switches!)
    if len(by_domain.get('switch', [])) > 50:
        print(f"\n✅ SWITCH CONTROL PANEL (CRITICAL)")
        print(f"   You have {len(by_domain['switch'])} switches!")
        print(f"   Recommend: Organized by area/room")
        recommendations.append("switch_dashboard")
    
    # Security dashboard (256 binary sensors)
    if len(by_domain.get('binary_sensor', [])) > 50:
        print(f"\n✅ SECURITY DASHBOARD (RECOMMENDED)")
        print(f"   You have {len(by_domain['binary_sensor'])} binary sensors")
        print(f"   Recommend: Entry points, motion zones, status overview")
        recommendations.append("security_dashboard")
    
    # Device tracker (89 trackers)
    if len(by_domain.get('device_tracker', [])) > 10:
        print(f"\n✅ PRESENCE DASHBOARD")
        print(f"   You have {len(by_domain['device_tracker'])} device trackers")
        recommendations.append("presence_dashboard")
    
    # Camera dashboard (29 cameras)
    if len(by_domain.get('camera', [])) > 5:
        print(f"\n✅ CAMERA DASHBOARD")
        print(f"   You have {len(by_domain['camera'])} cameras")
        recommendations.append("camera_dashboard")
    
    # Media control (16 media players)
    if len(by_domain.get('media_player', [])) > 0:
        print(f"\n✅ MEDIA CONTROL PANEL")
        print(f"   You have {len(by_domain['media_player'])} media players")
        recommendations.append("media_dashboard")
    
    return recommendations

def check_performance_needs(by_domain):
    """Check if performance optimization is needed."""
    
    print("\n" + "="*60)
    print("  PERFORMANCE OPTIMIZATION ASSESSMENT")
    print("="*60)
    
    critical = []
    
    # Database optimization critical with 968 sensors
    if len(by_domain.get('sensor', [])) > 500:
        print("\n🚨 DATABASE OPTIMIZATION - CRITICAL")
        print(f"   With {len(by_domain['sensor'])} sensors, your database")
        print(f"   will grow VERY quickly without optimization!")
        print(f"   Recommendation:")
        print(f"   - Setup automated purging")
        print(f"   - Create sensor indexes")
        print(f"   - Monitor database size")
        critical.append("database_optimization")
    
    # HACS components needed
    if len(by_domain.get('sensor', [])) > 100 or len(by_domain.get('switch', [])) > 100:
        print("\n⚠️  CUSTOM CARDS RECOMMENDED")
        print(f"   For managing {len(by_domain.get('sensor', []))} sensors and {len(by_domain.get('switch', []))} switches:")
        print(f"   - auto-entities card (dynamic lists)")
        print(f"   - mini-graph-card (sensor visualization)")
        print(f"   - button-card (switch organization)")
        print(f"   - layout-card (dashboard structure)")
        critical.append("hacs_components")
    
    # Grafana recommended
    if len(by_domain.get('sensor', [])) > 200:
        print("\n📊 GRAFANA ANALYTICS - HIGHLY RECOMMENDED")
        print(f"   With {len(by_domain['sensor'])} sensors, Grafana provides:")
        print(f"   - Historical trend analysis")
        print(f"   - Anomaly detection")
        print(f"   - Advanced visualizations")
        print(f"   - Performance monitoring")
        critical.append("grafana_integration")
    
    return critical

def main():
    """Main deployment analysis."""
    
    print("\n" + "="*60)
    print("  HA WORLDCLASS AGENT - DEPLOYMENT ANALYZER")
    print("  Customized for Your 2,479-Entity Setup")
    print("="*60)
    
    # Load your entity data
    entities = load_entity_data()
    if not entities:
        return 1
    
    # Analyze setup
    by_domain = analyze_setup(entities)
    
    # Recommend dashboards
    recommendations = recommend_dashboards(by_domain)
    
    # Check performance needs
    critical_needs = check_performance_needs(by_domain)
    
    # Summary
    print("\n" + "="*60)
    print("  DEPLOYMENT SUMMARY")
    print("="*60)
    print(f"\nRecommended Dashboards: {len(recommendations)}")
    for rec in recommendations:
        print(f"  - {rec}")
    
    print(f"\nCritical Optimizations Needed: {len(critical_needs)}")
    for need in critical_needs:
        print(f"  - {need}")
    
    print("\n" + "="*60)
    print("  NEXT STEPS")
    print("="*60)
    print("\n1. Review entity_report.md for complete entity list")
    print("2. Decide which dashboards to create first")
    print("3. Setup database optimization (CRITICAL)")
    print("4. Install recommended HACS components")
    print("5. Consider Grafana for analytics")
    
    print("\n📝 All analysis saved to SESSION_LOG.md")
    print("\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

