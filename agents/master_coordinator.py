#!/usr/bin/env python3
"""
Master Agent Coordinator
Orchestrates 5 specialized sub-agents for complete HA optimization
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [MASTER] - %(levelname)s - %(message)s'
)
logger = logging.getLogger("MasterCoordinator")


class MasterCoordinator:
    """Master Agent that coordinates all sub-agents."""
    
    def __init__(self):
        self.agents_dir = Path(__file__).parent
        self.reports_dir = self.agents_dir / "reports"
        self.reports_dir.mkdir(exist_ok=True)
        
        self.agents = {
            "agent3_collector": self.agents_dir / "collector_agent.py",
            "agent4_dashboard": self.agents_dir / "dashboard_ux_agent.py",
            "agent5_controls": self.agents_dir / "controls_automation_agent.py",
            "agent6_unifi": self.agents_dir / "unifi_api_agent.py",
            "agent7_qa": self.agents_dir / "qa_validation_agent.py",
        }
        
        self.phase_results = {}
        self.master_log = []
        
    def log_phase(self, phase: str, status: str, details: str):
        """Log phase completion."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "phase": phase,
            "status": status,
            "details": details
        }
        self.master_log.append(entry)
        logger.info(f"📋 {phase}: {status}")
        
    def execute_agent(self, agent_name: str, phase: str) -> dict:
        """Execute a sub-agent and wait for completion."""
        
        agent_script = self.agents.get(agent_name)
        if not agent_script or not agent_script.exists():
            logger.error(f"Agent not found: {agent_name}")
            return {"success": False, "error": "Agent not found"}
        
        logger.info(f"🚀 Executing {agent_name} for {phase}")
        
        try:
            result = subprocess.run(
                [sys.executable, str(agent_script)],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            output = {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
            
            # Save agent report
            report_file = self.reports_dir / f"{agent_name}_report.txt"
            with open(report_file, 'w') as f:
                f.write(f"Agent: {agent_name}\n")
                f.write(f"Phase: {phase}\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                f.write(f"Status: {'SUCCESS' if output['success'] else 'FAILED'}\n")
                f.write(f"\nOutput:\n{result.stdout}\n")
                if result.stderr:
                    f.write(f"\nErrors:\n{result.stderr}\n")
            
            logger.info(f"✅ {agent_name} completed")
            return output
            
        except Exception as e:
            logger.error(f"❌ {agent_name} failed: {e}")
            return {"success": False, "error": str(e)}
    
    def run_coordination(self):
        """Run complete multi-agent coordination."""
        
        print("\n" + "="*70)
        print("  MASTER AGENT COORDINATOR")
        print("  Orchestrating 5 Sub-Agents for Complete HA Optimization")
        print("="*70 + "\n")
        
        # Track overall status
        phases = []
        
        # Phase 1: Database Optimization (Master handles)
        print("\n📊 PHASE 1: Database Optimization (Master Agent)")
        self.log_phase("Phase 1", "STARTED", "SSH database optimization")
        phases.append("phase1_db_optimization")
        
        # Phase 2: Data Collection Setup (Agent 3)
        print("\n📡 PHASE 2: Data Collection Setup (Agent 3 - Collector)")
        self.log_phase("Phase 2", "STARTED", "Executing Agent 3")
        result_agent3 = self.execute_agent("agent3_collector", "Phase 2")
        self.phase_results["agent3"] = result_agent3
        self.log_phase("Phase 2", "COMPLETED" if result_agent3["success"] else "FAILED", 
                      "Agent 3 collection setup")
        phases.append("phase2_data_collection")
        
        # Phase 3: Dashboard Design (Agent 4)
        print("\n🎨 PHASE 3: Grafana Dashboard Design (Agent 4 - Dashboard UX)")
        self.log_phase("Phase 3", "STARTED", "Executing Agent 4")
        result_agent4 = self.execute_agent("agent4_dashboard", "Phase 3")
        self.phase_results["agent4"] = result_agent4
        self.log_phase("Phase 3", "COMPLETED" if result_agent4["success"] else "FAILED",
                      "Agent 4 dashboard design")
        phases.append("phase3_dashboard_design")
        
        # Phase 4: Grafana Installation (Master handles)
        print("\n🚀 PHASE 4: Grafana Installation (Master Agent)")
        self.log_phase("Phase 4", "STARTED", "Grafana installation and deployment")
        phases.append("phase4_grafana_install")
        
        # Phase 5: Safety Controls (Agent 5)
        print("\n⚙️ PHASE 5: Automation Safety Controls (Agent 5 - Controls)")
        self.log_phase("Phase 5", "STARTED", "Executing Agent 5")
        result_agent5 = self.execute_agent("agent5_controls", "Phase 5")
        self.phase_results["agent5"] = result_agent5
        self.log_phase("Phase 5", "COMPLETED" if result_agent5["success"] else "FAILED",
                      "Agent 5 safety controls")
        phases.append("phase5_safety_controls")
        
        # Phase 6: UniFi Integration (Agent 6)
        print("\n🌐 PHASE 6: UniFi Integration (Agent 6 - UniFi API)")
        self.log_phase("Phase 6", "STARTED", "Executing Agent 6")
        result_agent6 = self.execute_agent("agent6_unifi", "Phase 6")
        self.phase_results["agent6"] = result_agent6
        self.log_phase("Phase 6", "COMPLETED" if result_agent6["success"] else "FAILED",
                      "Agent 6 UniFi integration")
        phases.append("phase6_unifi_integration")
        
        # Phase 7: QA Validation (Agent 7)
        print("\n🔍 PHASE 7: QA Validation (Agent 7 - Validation)")
        self.log_phase("Phase 7", "STARTED", "Executing Agent 7")
        result_agent7 = self.execute_agent("agent7_qa", "Phase 7")
        self.phase_results["agent7"] = result_agent7
        self.log_phase("Phase 7", "COMPLETED" if result_agent7["success"] else "FAILED",
                      "Agent 7 QA validation")
        phases.append("phase7_qa_validation")
        
        # Save master log
        self.save_master_log()
        
        # Generate summary
        self.print_summary()
        
        return self.phase_results
    
    def save_master_log(self):
        """Save complete master coordination log."""
        
        log_file = self.reports_dir / "master_coordination_log.json"
        
        log_data = {
            "coordination_start": self.master_log[0]["timestamp"] if self.master_log else None,
            "coordination_end": datetime.now().isoformat(),
            "total_phases": len(self.master_log),
            "phase_log": self.master_log,
            "agent_results": {
                agent: {"success": result["success"]}
                for agent, result in self.phase_results.items()
            }
        }
        
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        logger.info(f"💾 Master log saved: {log_file}")
    
    def print_summary(self):
        """Print coordination summary."""
        
        print("\n" + "="*70)
        print("  COORDINATION SUMMARY")
        print("="*70)
        
        total_phases = len(self.master_log)
        completed = sum(1 for entry in self.master_log if entry["status"] == "COMPLETED")
        failed = sum(1 for entry in self.master_log if entry["status"] == "FAILED")
        
        print(f"\nTotal Phases: {total_phases}")
        print(f"Completed: {completed}")
        print(f"Failed: {failed}")
        
        print("\nAgent Results:")
        for agent, result in self.phase_results.items():
            status = "✅" if result["success"] else "❌"
            print(f"  {status} {agent}: {'SUCCESS' if result['success'] else 'FAILED'}")
        
        print("\n📄 Reports saved to: agents/reports/")
        print("\n" + "="*70)


def main():
    coordinator = MasterCoordinator()
    results = coordinator.run_coordination()
    
    # Return exit code based on results
    if all(r["success"] for r in results.values()):
        print("\n🎉 ALL AGENTS COMPLETED SUCCESSFULLY!")
        return 0
    else:
        print("\n⚠️ SOME AGENTS ENCOUNTERED ISSUES - Check reports/")
        return 1


if __name__ == "__main__":
    sys.exit(main())

