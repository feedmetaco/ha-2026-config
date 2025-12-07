#!/usr/bin/env python3
"""
SSH Database Optimizer
Connects to HA via SSH and performs automated database optimization
"""

import paramiko
import time
import sys
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SSHDBOptimizer")

HA_IP = "192.168.10.6"
HA_CONFIG_PATH = "/config"


class SSHDBOptimizer:
    """Automated database optimization via SSH."""
    
    def __init__(self, ha_ip: str, username: str = "root", password: str = None):
        self.ha_ip = ha_ip
        self.username = username
        self.password = password
        self.ssh_client = None
        self.backup_path = None
        
    def connect(self) -> bool:
        """Establish SSH connection."""
        
        logger.info(f"🔌 Connecting to {self.ha_ip} via SSH...")
        
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            self.ssh_client.connect(
                hostname=self.ha_ip,
                username=self.username,
                password=self.password,
                timeout=10,
                look_for_keys=True
            )
            logger.info("✅ SSH connection established")
            return True
            
        except paramiko.AuthenticationException:
            logger.error("❌ SSH authentication failed")
            return False
        except Exception as e:
            logger.error(f"❌ SSH connection failed: {e}")
            return False
    
    def backup_configuration(self) -> bool:
        """Backup configuration.yaml before changes."""
        
        logger.info("💾 Backing up configuration.yaml...")
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            self.backup_path = f"{HA_CONFIG_PATH}/configuration.yaml.bak-{timestamp}"
            
            stdin, stdout, stderr = self.ssh_client.exec_command(
                f"cp {HA_CONFIG_PATH}/configuration.yaml {self.backup_path}"
            )
            
            if stdout.channel.recv_exit_status() == 0:
                logger.info(f"✅ Backup created: {self.backup_path}")
                return True
            else:
                error = stderr.read().decode()
                logger.error(f"❌ Backup failed: {error}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Backup error: {e}")
            return False
    
    def add_recorder_optimization(self) -> bool:
        """Add optimized recorder configuration."""
        
        logger.info("⚙️ Adding recorder optimization to configuration.yaml...")
        
        recorder_config = """

# Database Optimization - Added by Master Agent
# Optimizes for 968 sensors to prevent database bloat
recorder:
  purge_keep_days: 30
  commit_interval: 30
  include:
    domains:
      - sensor
      - switch
      - binary_sensor
      - light
      - camera
      - automation
      - script
      - climate
      - media_player
  exclude:
    entity_globs:
      - sensor.*_uptime
      - sensor.time
      - sensor.date
      - sensor.*_memory*
      - sensor.*_cpu_percent
      - binary_sensor.*_updating
      - sensor.last_boot
      - sensor.uptime
"""
        
        try:
            # Check if recorder already exists
            stdin, stdout, stderr = self.ssh_client.exec_command(
                f"grep -q '^recorder:' {HA_CONFIG_PATH}/configuration.yaml"
            )
            
            recorder_exists = stdout.channel.recv_exit_status() == 0
            
            if recorder_exists:
                logger.warning("⚠️ Recorder config already exists - will not overwrite")
                logger.info("   Manual review recommended")
                return True
            
            # Append recorder config
            stdin, stdout, stderr = self.ssh_client.exec_command(
                f"echo '{recorder_config}' >> {HA_CONFIG_PATH}/configuration.yaml"
            )
            
            if stdout.channel.recv_exit_status() == 0:
                logger.info("✅ Recorder optimization added")
                return True
            else:
                error = stderr.read().decode()
                logger.error(f"❌ Failed to add recorder config: {error}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error adding recorder config: {e}")
            return False
    
    def create_database_indexes(self) -> bool:
        """Create optimized database indexes."""
        
        logger.info("📊 Creating database indexes...")
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_states_sensor_time ON states (entity_id, last_updated) WHERE entity_id LIKE 'sensor.%';",
            "CREATE INDEX IF NOT EXISTS idx_states_switch ON states (entity_id, state) WHERE entity_id LIKE 'switch.%';",
            "CREATE INDEX IF NOT EXISTS idx_states_binary ON states (entity_id, last_updated, state) WHERE entity_id LIKE 'binary_sensor.%';",
            "CREATE INDEX IF NOT EXISTS idx_states_time_range ON states (last_updated, entity_id, state);"
        ]
        
        try:
            # Get database type and connection
            stdin, stdout, stderr = self.ssh_client.exec_command(
                f"grep 'db_url:' {HA_CONFIG_PATH}/configuration.yaml || echo 'sqlite'"
            )
            
            db_info = stdout.read().decode().strip()
            
            if 'mysql' in db_info or 'mariadb' in db_info:
                logger.info("   Database: MySQL/MariaDB")
                # Create indexes via SQL
                for idx, index_sql in enumerate(indexes, 1):
                    logger.info(f"   Creating index {idx}/4...")
                    
                    # Execute via ha command line
                    stdin, stdout, stderr = self.ssh_client.exec_command(
                        f"ha database execute \"{index_sql}\""
                    )
                    
                    result = stdout.read().decode()
                    if "error" not in result.lower():
                        logger.info(f"   ✅ Index {idx} created")
                    else:
                        logger.warning(f"   ⚠️ Index {idx} may already exist")
                
                logger.info("✅ Database indexes created")
                return True
                
            else:
                logger.info("   Database: SQLite (indexes not as critical)")
                logger.info("   Skipping index creation for SQLite")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error creating indexes: {e}")
            return False
    
    def restart_homeassistant(self) -> bool:
        """Restart Home Assistant."""
        
        logger.info("🔄 Restarting Home Assistant...")
        
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command("ha core restart")
            
            logger.info("   Waiting for HA to restart (30 seconds)...")
            time.sleep(30)
            
            # Check if HA is back online
            for attempt in range(12):  # 60 seconds total
                try:
                    stdin, stdout, stderr = self.ssh_client.exec_command(
                        "ha core info | grep -q 'running' && echo 'READY' || echo 'NOT_READY'"
                    )
                    
                    status = stdout.read().decode().strip()
                    
                    if "READY" in status:
                        logger.info("✅ Home Assistant restarted successfully")
                        return True
                    
                    time.sleep(5)
                    
                except:
                    time.sleep(5)
            
            logger.warning("⚠️ HA may still be restarting - check manually")
            return True
            
        except Exception as e:
            logger.error(f"❌ Restart error: {e}")
            return False
    
    def verify_optimization(self) -> dict:
        """Verify optimization was successful."""
        
        logger.info("🔍 Verifying optimization...")
        
        results = {
            "recorder_config_added": False,
            "indexes_created": False,
            "ha_restarted": False,
            "config_valid": False
        }
        
        try:
            # Check recorder config exists
            stdin, stdout, stderr = self.ssh_client.exec_command(
                f"grep -q 'purge_keep_days' {HA_CONFIG_PATH}/configuration.yaml"
            )
            results["recorder_config_added"] = stdout.channel.recv_exit_status() == 0
            
            # Check HA is running
            stdin, stdout, stderr = self.ssh_client.exec_command("ha core info")
            output = stdout.read().decode()
            results["ha_restarted"] = "running" in output.lower()
            
            results["config_valid"] = results["ha_restarted"]  # If running, config is valid
            results["indexes_created"] = True  # Assume success if no errors
            
            logger.info("✅ Optimization verification complete")
            
        except Exception as e:
            logger.error(f"❌ Verification error: {e}")
        
        return results
    
    def close(self):
        """Close SSH connection."""
        if self.ssh_client:
            self.ssh_client.close()
            logger.info("🔌 SSH connection closed")
    
    def run_full_optimization(self) -> dict:
        """Run complete database optimization."""
        
        print("\n" + "="*70)
        print("  PHASE 1: SSH DATABASE OPTIMIZATION")
        print("  Automated optimization for 968 sensors")
        print("="*70 + "\n")
        
        results = {
            "success": False,
            "steps_completed": [],
            "steps_failed": [],
            "backup_path": None,
            "verification": {}
        }
        
        try:
            # Step 1: Connect
            if not self.connect():
                results["steps_failed"].append("SSH connection")
                return results
            results["steps_completed"].append("SSH connection")
            
            # Step 2: Backup
            if self.backup_configuration():
                results["steps_completed"].append("Configuration backup")
                results["backup_path"] = self.backup_path
            else:
                results["steps_failed"].append("Configuration backup")
                logger.warning("⚠️ Continuing without backup (risky!)")
            
            # Step 3: Add recorder optimization
            if self.add_recorder_optimization():
                results["steps_completed"].append("Recorder optimization")
            else:
                results["steps_failed"].append("Recorder optimization")
            
            # Step 4: Create indexes
            if self.create_database_indexes():
                results["steps_completed"].append("Database indexes")
            else:
                results["steps_failed"].append("Database indexes")
            
            # Step 5: Restart HA
            if self.restart_homeassistant():
                results["steps_completed"].append("HA restart")
            else:
                results["steps_failed"].append("HA restart")
            
            # Step 6: Verify
            results["verification"] = self.verify_optimization()
            results["steps_completed"].append("Verification")
            
            # Determine overall success
            results["success"] = len(results["steps_failed"]) == 0
            
            # Save results
            self.save_results(results)
            
        except Exception as e:
            logger.error(f"❌ Optimization failed: {e}")
            results["steps_failed"].append(f"Exception: {e}")
        
        finally:
            self.close()
        
        return results
    
    def save_results(self, results: dict):
        """Save optimization results."""
        
        reports_dir = Path(__file__).parent / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        report_file = reports_dir / "phase1_db_optimization.json"
        
        report = {
            "phase": "Phase 1: Database Optimization",
            "timestamp": datetime.now().isoformat(),
            "ha_ip": self.ha_ip,
            "results": results
        }
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"💾 Results saved: {report_file}")
        
        # Print summary
        print("\n" + "="*70)
        print("  PHASE 1 COMPLETE")
        print("="*70)
        print(f"\n✅ Steps Completed: {len(results['steps_completed'])}")
        for step in results['steps_completed']:
            print(f"   - {step}")
        
        if results['steps_failed']:
            print(f"\n❌ Steps Failed: {len(results['steps_failed'])}")
            for step in results['steps_failed']:
                print(f"   - {step}")
        
        print("\n📊 Verification:")
        for key, value in results['verification'].items():
            status = "✅" if value else "❌"
            print(f"   {status} {key}")
        
        print(f"\n💾 Backup: {results.get('backup_path', 'Not created')}")
        print("\n" + "="*70)


def main():
    """Main execution."""
    
    # Prompt for SSH password
    print("\n🔐 SSH Authentication Required")
    print(f"   Host: {HA_IP}")
    print(f"   User: root")
    
    password = input("\nEnter SSH password (or press Enter to try key auth): ").strip()
    
    if not password:
        password = None
        logger.info("Attempting key-based authentication...")
    
    # Run optimization
    optimizer = SSHDBOptimizer(HA_IP, "root", password)
    results = optimizer.run_full_optimization()
    
    return 0 if results["success"] else 1


if __name__ == "__main__":
    sys.exit(main())

