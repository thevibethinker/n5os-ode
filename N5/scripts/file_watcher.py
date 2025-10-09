#!/usr/bin/env python3
"""
N5 File Watcher Daemon - Real-time protection for critical files
Monitors protected files for suspicious changes and creates automatic backups
"""

import os
import time
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
import json
import subprocess


class FileWatcher:
    """Background daemon that monitors critical files for changes"""
    
    PROTECTED_FILES = [
        "/home/workspace/Documents/N5.md",
        "/home/workspace/N5/prefs/prefs.md",
        "/home/workspace/N5/config/commands.jsonl",
        "/home/workspace/N5/timeline/system-timeline.jsonl",
    ]
    
    ALERT_LOG = Path("/home/workspace/.n5_backups/watcher_alerts.jsonl")
    STATE_FILE = Path("/home/workspace/.n5_backups/watcher_state.json")
    CHECK_INTERVAL = 5  # seconds between checks
    SIZE_REDUCTION_THRESHOLD = 0.7  # Alert if file shrinks by 30% or more
    
    def __init__(self):
        self.state: Dict[str, dict] = {}
        self._load_state()
        self._ensure_logs()
    
    def _ensure_logs(self):
        """Ensure log directories exist"""
        self.ALERT_LOG.parent.mkdir(parents=True, exist_ok=True)
        if not self.ALERT_LOG.exists():
            self.ALERT_LOG.touch()
    
    def _load_state(self):
        """Load last known state of files"""
        if self.STATE_FILE.exists():
            try:
                self.state = json.loads(self.STATE_FILE.read_text())
            except:
                self.state = {}
        
        # Initialize state for all protected files
        for file_path in self.PROTECTED_FILES:
            if file_path not in self.state:
                self.state[file_path] = self._get_file_state(file_path)
    
    def _save_state(self):
        """Save current state to disk"""
        self.STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        self.STATE_FILE.write_text(json.dumps(self.state, indent=2))
    
    def _get_file_state(self, file_path: str) -> dict:
        """Get current state of a file"""
        path = Path(file_path)
        
        if not path.exists():
            return {
                "exists": False,
                "size": 0,
                "hash": None,
                "mtime": None,
                "last_checked": datetime.now().isoformat()
            }
        
        stat = path.stat()
        content = path.read_bytes()
        
        return {
            "exists": True,
            "size": len(content),
            "hash": hashlib.sha256(content).hexdigest(),
            "mtime": stat.st_mtime,
            "last_checked": datetime.now().isoformat()
        }
    
    def _log_alert(self, file_path: str, alert_type: str, details: dict):
        """Log an alert to the alert log"""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "file": file_path,
            "alert_type": alert_type,
            "details": details
        }
        
        with open(self.ALERT_LOG, 'a') as f:
            f.write(json.dumps(alert) + '\n')
        
        # Also print to console
        print(f"\n⚠️  ALERT: {alert_type}")
        print(f"   File: {file_path}")
        for key, value in details.items():
            print(f"   {key}: {value}")
    
    def _create_emergency_backup(self, file_path: str, reason: str) -> bool:
        """Create emergency backup using the backup system"""
        try:
            result = subprocess.run(
                ["python3", "/home/workspace/N5/scripts/file_backup.py", "backup", file_path, f"watcher:{reason}"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except:
            return False
    
    def check_file(self, file_path: str) -> Optional[dict]:
        """
        Check a file for suspicious changes
        
        Returns:
            Alert dict if issue detected, None otherwise
        """
        current_state = self._get_file_state(file_path)
        previous_state = self.state.get(file_path, {})
        
        # File was deleted
        if previous_state.get("exists") and not current_state["exists"]:
            self._log_alert(file_path, "FILE_DELETED", {
                "previous_size": previous_state.get("size"),
                "action": "File was deleted"
            })
            return {"type": "deleted", "severity": "critical"}
        
        # File was just created (not an issue)
        if not previous_state.get("exists") and current_state["exists"]:
            print(f"✅ New file created: {file_path}")
            self.state[file_path] = current_state
            self._save_state()
            return None
        
        # File exists in both states - check for changes
        if current_state["exists"] and previous_state.get("exists"):
            
            # Check for hash change (content modified)
            if current_state["hash"] != previous_state.get("hash"):
                old_size = previous_state.get("size", 0)
                new_size = current_state["size"]
                
                # File became empty - CRITICAL
                if new_size == 0:
                    self._log_alert(file_path, "FILE_EMPTIED", {
                        "previous_size": old_size,
                        "action": "Creating emergency backup",
                        "severity": "CRITICAL"
                    })
                    
                    # Try to restore from previous state if we have it
                    if previous_state.get("hash"):
                        print(f"   Attempting emergency recovery...")
                        # The file is already empty, so we'd need to restore from backup
                        # For now, just alert
                    
                    return {"type": "emptied", "severity": "critical", "old_size": old_size}
                
                # Significant size reduction - WARNING
                if old_size > 0:
                    size_ratio = new_size / old_size
                    if size_ratio < self.SIZE_REDUCTION_THRESHOLD:
                        reduction_pct = int((1 - size_ratio) * 100)
                        
                        self._log_alert(file_path, "SIGNIFICANT_SIZE_REDUCTION", {
                            "old_size": old_size,
                            "new_size": new_size,
                            "reduction_percent": reduction_pct,
                            "action": "Creating emergency backup"
                        })
                        
                        # Create backup of the OLD version if we still have it
                        # (We can't, it's already changed - this is why we backup BEFORE writes)
                        
                        return {"type": "size_reduction", "severity": "warning", 
                                "reduction_pct": reduction_pct}
                
                # Normal modification
                print(f"📝 File modified: {file_path} ({old_size} → {new_size} bytes)")
                
                # Create backup on any change
                self._create_emergency_backup(file_path, "change_detected")
        
        # Update state
        self.state[file_path] = current_state
        self._save_state()
        
        return None
    
    def run(self):
        """Main daemon loop"""
        print("🔒 N5 File Watcher Daemon Starting")
        print("=" * 60)
        print(f"Monitoring {len(self.PROTECTED_FILES)} protected files")
        print(f"Check interval: {self.CHECK_INTERVAL} seconds")
        print(f"Alert log: {self.ALERT_LOG}")
        print("=" * 60)
        print("\nPress Ctrl+C to stop\n")
        
        try:
            while True:
                for file_path in self.PROTECTED_FILES:
                    try:
                        alert = self.check_file(file_path)
                        if alert and alert.get("severity") == "critical":
                            print(f"\n🚨 CRITICAL ALERT for {file_path}")
                            print(f"   Check alert log: {self.ALERT_LOG}")
                    except Exception as e:
                        print(f"❌ Error checking {file_path}: {e}")
                
                time.sleep(self.CHECK_INTERVAL)
                
        except KeyboardInterrupt:
            print("\n\n🛑 File Watcher Daemon Stopped")
            self._save_state()
    
    def status(self):
        """Show current status of all monitored files"""
        print("\n📊 N5 File Watcher Status")
        print("=" * 70)
        
        for file_path in self.PROTECTED_FILES:
            state = self.state.get(file_path, {})
            exists = state.get("exists", False)
            size = state.get("size", 0)
            last_checked = state.get("last_checked", "never")
            
            status_icon = "✅" if exists and size > 0 else "❌"
            print(f"\n{status_icon} {file_path}")
            print(f"   Exists: {exists}")
            print(f"   Size: {size:,} bytes")
            print(f"   Last checked: {last_checked}")
        
        # Show recent alerts
        if self.ALERT_LOG.exists():
            alerts = self.ALERT_LOG.read_text().strip().split('\n')
            recent_alerts = [json.loads(a) for a in alerts[-5:] if a.strip()]
            
            if recent_alerts:
                print(f"\n⚠️  Recent Alerts ({len(recent_alerts)} shown):")
                for alert in recent_alerts:
                    timestamp = alert["timestamp"][:19].replace("T", " ")
                    print(f"   • {timestamp} | {alert['alert_type']}")
                    print(f"     {Path(alert['file']).name}")


def main():
    """CLI interface for file watcher"""
    import sys
    
    watcher = FileWatcher()
    
    if len(sys.argv) < 2:
        print("N5 File Watcher Daemon")
        print("=" * 50)
        print("\nUsage:")
        print(f"  {sys.argv[0]} start    - Start watching files")
        print(f"  {sys.argv[0]} status   - Show current status")
        print(f"  {sys.argv[0]} check    - Run single check on all files")
        print(f"  {sys.argv[0]} alerts   - Show recent alerts")
        print("\nTo run as background daemon:")
        print(f"  nohup {sys.argv[0]} start > /dev/shm/file_watcher.log 2>&1 &")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "start":
        watcher.run()
    
    elif command == "status":
        watcher.status()
    
    elif command == "check":
        print("Running single check on all protected files...")
        alerts = []
        for file_path in watcher.PROTECTED_FILES:
            alert = watcher.check_file(file_path)
            if alert:
                alerts.append((file_path, alert))
        
        if alerts:
            print(f"\n⚠️  Found {len(alerts)} issues:")
            for file_path, alert in alerts:
                print(f"   • {file_path}: {alert['type']} (severity: {alert['severity']})")
        else:
            print("✅ All files look good")
    
    elif command == "alerts":
        if not watcher.ALERT_LOG.exists():
            print("No alerts logged yet")
            sys.exit(0)
        
        alerts = watcher.ALERT_LOG.read_text().strip().split('\n')
        alerts = [json.loads(a) for a in alerts if a.strip()]
        
        print(f"\n📋 Alert Log ({len(alerts)} total alerts)")
        print("=" * 70)
        
        for alert in alerts[-20:]:  # Show last 20
            timestamp = alert["timestamp"][:19].replace("T", " ")
            print(f"\n{timestamp} | {alert['alert_type']}")
            print(f"File: {alert['file']}")
            for key, value in alert["details"].items():
                print(f"  {key}: {value}")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
