#!/usr/bin/env python3
"""
HA Forensic Analyzer - Complete Instance Analysis
Analyzes all 2,479 entities for issues, improvements, and optimization
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import re

class HAForensicAnalyzer:
    """PhD-level forensic analysis of HA instance."""
    
    def __init__(self):
        self.entities = self.load_entities()
        self.by_domain = self.organize_by_domain()
        self.issues = {
            'critical': [],
            'warnings': [],
            'suggestions': []
        }
        self.performance_issues = []
        self.usability_improvements = []
        self.automation_analysis = []
        
    def load_entities(self):
        """Load entity data."""
        # Try multiple paths
        possible_paths = [
            Path("agent_data/all_entities.json"),
            Path("../agent_data/all_entities.json"),
            Path("c:/Users/Sami/Documents/ha-config/agent_data/all_entities.json")
        ]
        
        for data_file in possible_paths:
            if data_file.exists():
                with open(data_file) as f:
                    return json.load(f)
        
        print("❌ Entity data not found. Run: py get_ha_data.py YOUR_TOKEN")
        return []
    
    def organize_by_domain(self):
        """Organize entities by domain."""
        by_domain = defaultdict(list)
        for entity in self.entities:
            by_domain[entity['domain']].append(entity)
        return by_domain
    
    def check_faulty_sensors(self):
        """Identify problematic sensors."""
        
        print("\n🔍 Analyzing Sensors for Issues...")
        
        sensors = self.by_domain.get('sensor', [])
        faulty_sensors = {
            'unavailable': [],
            'unknown': [],
            'stale': [],
            'no_unit': [],
            'duplicate_names': [],
            'bad_states': []
        }
        
        seen_names = defaultdict(list)
        
        for sensor in sensors:
            entity_id = sensor['entity_id']
            state = sensor.get('state', '')
            name = sensor.get('name', '')
            last_updated = sensor.get('last_updated', '')
            unit = sensor.get('attributes', {}).get('unit_of_measurement')
            
            # Check for unavailable sensors
            if state in ['unavailable', 'None', None]:
                faulty_sensors['unavailable'].append({
                    'entity_id': entity_id,
                    'name': name,
                    'issue': 'Sensor unavailable'
                })
            
            # Check for unknown states
            elif state == 'unknown':
                faulty_sensors['unknown'].append({
                    'entity_id': entity_id,
                    'name': name,
                    'issue': 'Unknown state - may need configuration'
                })
            
            # Check for numeric sensors without units
            if state and state.replace('.', '').replace('-', '').isdigit():
                if not unit:
                    faulty_sensors['no_unit'].append({
                        'entity_id': entity_id,
                        'name': name,
                        'issue': 'Numeric sensor missing unit of measurement'
                    })
            
            # Check for duplicate names
            seen_names[name].append(entity_id)
            
            # Check for bad state values
            if state and len(str(state)) > 250:
                faulty_sensors['bad_states'].append({
                    'entity_id': entity_id,
                    'name': name,
                    'issue': f'State too long ({len(str(state))} chars) - may cause DB issues'
                })
        
        # Identify duplicates
        for name, entity_ids in seen_names.items():
            if len(entity_ids) > 1:
                faulty_sensors['duplicate_names'].append({
                    'name': name,
                    'entities': entity_ids,
                    'issue': f'{len(entity_ids)} sensors with same name - causes confusion'
                })
        
        # Count issues
        total_issues = sum(len(v) if isinstance(v, list) else 0 for v in faulty_sensors.values())
        
        print(f"   Found {total_issues} sensor issues:")
        print(f"   - Unavailable: {len(faulty_sensors['unavailable'])}")
        print(f"   - Unknown state: {len(faulty_sensors['unknown'])}")
        print(f"   - Missing units: {len(faulty_sensors['no_unit'])}")
        print(f"   - Duplicate names: {len(faulty_sensors['duplicate_names'])}")
        print(f"   - Bad states: {len(faulty_sensors['bad_states'])}")
        
        return faulty_sensors
    
    def analyze_performance_issues(self):
        """Identify performance bottlenecks."""
        
        print("\n⚡ Analyzing Performance Issues...")
        
        issues = []
        
        # 1. Too many entities
        total_entities = len(self.entities)
        if total_entities > 2000:
            issues.append({
                'severity': 'warning',
                'category': 'Entity Count',
                'issue': f'{total_entities} entities is very high',
                'impact': 'Slows down UI, increases DB size, longer startup',
                'recommendation': 'Review and remove unused entities'
            })
        
        # 2. High-frequency sensors (968 sensors!)
        sensor_count = len(self.by_domain.get('sensor', []))
        if sensor_count > 500:
            issues.append({
                'severity': 'critical',
                'category': 'Sensor Overload',
                'issue': f'{sensor_count} sensors generating continuous data',
                'impact': 'Database grows rapidly, queries slow down, high CPU usage',
                'recommendation': 'Implement aggressive purging, exclude non-critical sensors from recorder'
            })
        
        # 3. Many switches
        switch_count = len(self.by_domain.get('switch', []))
        if switch_count > 400:
            issues.append({
                'severity': 'warning',
                'category': 'Switch Management',
                'issue': f'{switch_count} switches may be difficult to manage',
                'impact': 'Dashboard clutter, difficult to find specific switches',
                'recommendation': 'Group switches by area, use auto-entities for dynamic lists'
            })
        
        # 4. Update entities
        update_count = len(self.by_domain.get('update', []))
        if update_count > 50:
            issues.append({
                'severity': 'info',
                'category': 'Update Tracking',
                'issue': f'{update_count} update entities',
                'impact': 'May cause unnecessary notifications',
                'recommendation': 'Disable update checks for stable integrations'
            })
        
        # 5. Camera count
        camera_count = len(self.by_domain.get('camera', []))
        if camera_count > 20:
            issues.append({
                'severity': 'warning',
                'category': 'Camera Streaming',
                'issue': f'{camera_count} cameras',
                'impact': 'High bandwidth usage, stream management complexity',
                'recommendation': 'Use camera groups, implement selective streaming'
            })
        
        # 6. Automation count
        automation_count = len(self.by_domain.get('automation', []))
        if automation_count > 30:
            issues.append({
                'severity': 'info',
                'category': 'Automation Complexity',
                'issue': f'{automation_count} automations',
                'impact': 'Difficult to debug, potential conflicts',
                'recommendation': 'Document automations, use blueprints, implement testing'
            })
        
        print(f"   Found {len(issues)} performance concerns:")
        for issue in issues:
            print(f"   - [{issue['severity'].upper()}] {issue['category']}: {issue['issue']}")
        
        return issues
    
    def suggest_usability_improvements(self):
        """Suggest usability enhancements."""
        
        print("\n💡 Generating Usability Improvements...")
        
        suggestions = []
        
        # 1. Entity naming
        poorly_named = []
        for entity in self.entities[:100]:  # Sample first 100
            entity_id = entity['entity_id']
            name = entity.get('name', '')
            
            # Check if using default entity_id as name
            if name == entity_id.replace('_', ' ').title():
                poorly_named.append(entity_id)
        
        if len(poorly_named) > 10:
            suggestions.append({
                'category': 'Entity Naming',
                'priority': 'high',
                'issue': f'{len(poorly_named)} entities using default names',
                'benefit': 'Better dashboard readability, easier automation creation',
                'action': 'Customize entity names to be more descriptive'
            })
        
        # 2. Area assignment
        entities_without_areas = sum(
            1 for e in self.entities 
            if not e.get('attributes', {}).get('area_id')
        )
        
        if entities_without_areas > 100:
            suggestions.append({
                'category': 'Area Organization',
                'priority': 'high',
                'issue': f'{entities_without_areas} entities not assigned to areas',
                'benefit': 'Better organization, area-based automations, easier navigation',
                'action': 'Assign entities to logical areas (living room, bedroom, etc.)'
            })
        
        # 3. Device grouping
        suggestions.append({
            'category': 'Device Grouping',
            'priority': 'medium',
            'issue': 'Large number of individual entities',
            'benefit': 'Simpler dashboards, batch control, cleaner UI',
            'action': 'Create groups: all_lights, all_switches, security_sensors, etc.'
        })
        
        # 4. Dashboard organization
        sensor_count = len(self.by_domain.get('sensor', []))
        if sensor_count > 100:
            suggestions.append({
                'category': 'Dashboard Design',
                'priority': 'high',
                'issue': f'{sensor_count} sensors need organized display',
                'benefit': 'Faster access, better visual hierarchy, mobile-friendly',
                'action': 'Create domain-specific dashboards: sensors, switches, security, media'
            })
        
        # 5. Custom cards
        suggestions.append({
            'category': 'UI Enhancement',
            'priority': 'medium',
            'issue': 'Using default cards for large entity set',
            'benefit': 'Modern UI, better performance, advanced features',
            'action': 'Install HACS cards: auto-entities, mini-graph-card, button-card, mushroom'
        })
        
        # 6. Mobile optimization
        suggestions.append({
            'category': 'Mobile Experience',
            'priority': 'high',
            'issue': 'Default dashboard may not be mobile-optimized',
            'benefit': 'Better mobile usability, faster loading, touch-friendly',
            'action': 'Create mobile-specific dashboard with essential controls only'
        })
        
        # 7. Search functionality
        if len(self.entities) > 1000:
            suggestions.append({
                'category': 'Navigation',
                'priority': 'medium',
                'issue': 'Difficult to find entities among 2,479',
                'benefit': 'Quick entity access, reduced frustration',
                'action': 'Use search cards, implement quick-access favorites dashboard'
            })
        
        print(f"   Generated {len(suggestions)} improvement suggestions")
        for sug in suggestions:
            print(f"   - [{sug['priority'].upper()}] {sug['category']}")
        
        return suggestions
    
    def analyze_automations(self):
        """Forensic analysis of automations."""
        
        print("\n🤖 Analyzing Automations...")
        
        automations = self.by_domain.get('automation', [])
        analysis = {
            'total': len(automations),
            'issues': [],
            'improvements': [],
            'best_practices': []
        }
        
        if not automations:
            print("   No automation entities found (may need to check config files)")
            return analysis
        
        # Analyze each automation
        for auto in automations:
            entity_id = auto['entity_id']
            name = auto.get('name', entity_id)
            state = auto.get('state', '')
            
            # Check if disabled
            if state == 'off' or state == 'unavailable':
                analysis['issues'].append({
                    'automation': name,
                    'entity_id': entity_id,
                    'issue': f'Automation is {state}',
                    'severity': 'info',
                    'recommendation': 'Review if still needed or re-enable'
                })
        
        # General automation improvements
        if len(automations) > 20:
            analysis['improvements'].append({
                'category': 'Organization',
                'suggestion': 'Create automation groups by function',
                'benefit': 'Easier to manage and debug',
                'implementation': 'Use tags: security, lighting, climate, notifications'
            })
        
        analysis['improvements'].append({
            'category': 'Documentation',
            'suggestion': 'Add descriptions to all automations',
            'benefit': 'Easier troubleshooting, better team collaboration',
            'implementation': 'Use description field to explain triggers and actions'
        })
        
        analysis['improvements'].append({
            'category': 'Testing',
            'suggestion': 'Implement automation testing',
            'benefit': 'Catch errors before deployment, ensure reliability',
            'implementation': 'Use trace feature, create test scripts'
        })
        
        analysis['improvements'].append({
            'category': 'Performance',
            'suggestion': 'Review automation triggers for efficiency',
            'benefit': 'Reduce CPU usage, faster execution',
            'implementation': 'Use specific triggers instead of state changes, add conditions'
        })
        
        # Best practices
        analysis['best_practices'].extend([
            {
                'practice': 'Use blueprints for common patterns',
                'reason': 'Consistency, easier to update, community-tested',
                'example': 'Motion-activated lights, notification templates'
            },
            {
                'practice': 'Implement rate limiting',
                'reason': 'Prevent automation loops, reduce spam',
                'example': 'Add delays, use input_boolean flags'
            },
            {
                'practice': 'Use variables for readability',
                'reason': 'Easier to understand, maintain, and modify',
                'example': 'Define sensor groups, threshold values as variables'
            },
            {
                'practice': 'Add error handling',
                'reason': 'Graceful failures, better debugging',
                'example': 'Check entity availability, use choose/default actions'
            }
        ])
        
        print(f"   Analyzed {analysis['total']} automations")
        print(f"   - Issues found: {len(analysis['issues'])}")
        print(f"   - Improvements suggested: {len(analysis['improvements'])}")
        print(f"   - Best practices: {len(analysis['best_practices'])}")
        
        return analysis
    
    def generate_report_data(self):
        """Generate comprehensive analysis report data."""
        
        print("\n" + "="*60)
        print("  COMPREHENSIVE HA FORENSIC ANALYSIS")
        print("  Your 2,479-Entity Instance")
        print("="*60)
        
        # Run all analyses
        faulty_sensors = self.check_faulty_sensors()
        performance_issues = self.analyze_performance_issues()
        usability_improvements = self.suggest_usability_improvements()
        automation_analysis = self.analyze_automations()
        
        # Compile report
        report = {
            'metadata': {
                'total_entities': len(self.entities),
                'domains': len(self.by_domain),
                'generated_at': datetime.now().isoformat(),
                'analysis_version': '1.0.0'
            },
            'domain_summary': {
                domain: len(entities) 
                for domain, entities in sorted(
                    self.by_domain.items(), 
                    key=lambda x: -len(x[1])
                )
            },
            'sensor_issues': faulty_sensors,
            'performance_issues': performance_issues,
            'usability_improvements': usability_improvements,
            'automation_analysis': automation_analysis,
            'critical_recommendations': self.get_top_recommendations(
                faulty_sensors, performance_issues, usability_improvements
            )
        }
        
        print("\n✅ Analysis Complete!")
        print(f"\nSummary:")
        print(f"  - Sensor Issues: {sum(len(v) if isinstance(v, list) else 0 for v in faulty_sensors.values())}")
        print(f"  - Performance Concerns: {len(performance_issues)}")
        print(f"  - Usability Improvements: {len(usability_improvements)}")
        print(f"  - Automation Insights: {automation_analysis['total']} analyzed")
        
        return report
    
    def get_top_recommendations(self, sensors, performance, usability):
        """Get top priority recommendations."""
        
        recommendations = []
        
        # Critical sensor issues
        if len(sensors.get('unavailable', [])) > 10:
            recommendations.append({
                'priority': 1,
                'category': 'Sensor Health',
                'action': f"Fix {len(sensors['unavailable'])} unavailable sensors",
                'impact': 'High - Affects automations and dashboards',
                'effort': 'Medium'
            })
        
        # Database optimization
        sensor_count = len(self.by_domain.get('sensor', []))
        if sensor_count > 500:
            recommendations.append({
                'priority': 1,
                'category': 'Database Performance',
                'action': 'Implement aggressive recorder purging and exclusions',
                'impact': 'Critical - Prevents database bloat and slowdowns',
                'effort': 'Low'
            })
        
        # Dashboard organization
        if sensor_count > 100:
            recommendations.append({
                'priority': 2,
                'category': 'Dashboard Organization',
                'action': 'Create domain-specific dashboards',
                'impact': 'High - Improves usability and performance',
                'effort': 'Medium'
            })
        
        # HACS components
        recommendations.append({
            'priority': 2,
            'category': 'UI Enhancement',
            'action': 'Install essential HACS cards',
            'impact': 'High - Modern UI, better performance',
            'effort': 'Low'
        })
        
        # Entity naming
        recommendations.append({
            'priority': 3,
            'category': 'Organization',
            'action': 'Improve entity naming and area assignment',
            'impact': 'Medium - Better organization',
            'effort': 'High'
        })
        
        return sorted(recommendations, key=lambda x: x['priority'])

if __name__ == "__main__":
    analyzer = HAForensicAnalyzer()
    report_data = analyzer.generate_report_data()
    
    # Save report data
    output_dir = Path("agent_data")
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "forensic_analysis.json"
    with open(output_file, 'w') as f:
        json.dump(report_data, f, indent=2)
    
    print(f"\n💾 Full analysis saved to: {output_file}")
    print("\n🎨 Generating HTML visualization...")

