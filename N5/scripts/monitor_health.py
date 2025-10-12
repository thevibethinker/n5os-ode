#!/usr/bin/env python3
"""
Health Monitoring - Priority 4
Check meeting monitor system health and alert on issues.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
import pytz


class HealthMonitor:
    """Monitor meeting monitor system health."""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.et_tz = pytz.timezone('America/New_York')
        self.issues = []
        self.warnings = []
        self.info = []
        
        # Load configuration
        self.config = self.load_config()
    
    def load_config(self):
        """Load monitoring configuration."""
        config_file = self.base_dir / 'config' / 'meeting_monitor_config.json'
        
        default_config = {
            'health_checks': {
                'max_cycle_gap_minutes': 60,
                'max_errors_per_day': 10,
                'max_api_failures': 5
            }
        }
        
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return default_config
    
    def check_last_cycle(self):
        """Check when the last monitoring cycle ran."""
        state_file = self.base_dir / 'records' / 'meetings' / '.processed.json'
        
        if not state_file.exists():
            self.issues.append("State file does not exist - system not initialized")
            return False
        
        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            last_poll = state.get('last_poll')
            
            if not last_poll:
                self.warnings.append("No cycles have run yet")
                return True
            
            last_poll_time = datetime.fromisoformat(last_poll)
            now = datetime.now(self.et_tz)
            
            # Remove timezone info for comparison if present
            if last_poll_time.tzinfo:
                last_poll_time = last_poll_time.replace(tzinfo=None)
            if now.tzinfo:
                now = now.replace(tzinfo=None)
            
            gap = (now - last_poll_time).total_seconds() / 60
            max_gap = self.config['health_checks']['max_cycle_gap_minutes']
            
            if gap > max_gap:
                self.issues.append(
                    f"Last cycle was {gap:.0f} minutes ago (max: {max_gap})"
                )
                return False
            else:
                self.info.append(
                    f"✓ Last cycle: {gap:.0f} minutes ago"
                )
                return True
                
        except Exception as e:
            self.issues.append(f"Error reading state file: {str(e)}")
            return False
    
    def check_log_file(self):
        """Check if log file exists and is being written to."""
        log_file = self.base_dir / 'logs' / 'meeting_monitor.log'
        
        if not log_file.exists():
            self.warnings.append("Log file does not exist yet")
            return True
        
        try:
            # Check file size
            size = log_file.stat().st_size
            if size == 0:
                self.warnings.append("Log file is empty")
                return True
            
            # Check last modification time
            mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            now = datetime.now()
            gap = (now - mtime).total_seconds() / 60
            
            if gap > 60:
                self.warnings.append(
                    f"Log file not updated in {gap:.0f} minutes"
                )
            else:
                self.info.append(
                    f"✓ Log file active (updated {gap:.0f} min ago)"
                )
            
            return True
            
        except Exception as e:
            self.issues.append(f"Error checking log file: {str(e)}")
            return False
    
    def check_error_rate(self):
        """Check for excessive errors in logs."""
        log_file = self.base_dir / 'logs' / 'meeting_monitor.log'
        
        if not log_file.exists():
            return True
        
        try:
            # Read last 24 hours of logs
            now = datetime.now(self.et_tz)
            cutoff = now - timedelta(days=1)
            
            error_count = 0
            warning_count = 0
            
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if '[ERROR]' in line:
                        error_count += 1
                    elif '[WARNING]' in line:
                        warning_count += 1
            
            max_errors = self.config['health_checks']['max_errors_per_day']
            
            if error_count > max_errors:
                self.issues.append(
                    f"High error rate: {error_count} errors in last 24h (max: {max_errors})"
                )
                return False
            elif error_count > 0:
                self.warnings.append(
                    f"{error_count} errors in last 24h"
                )
            else:
                self.info.append("✓ No errors in last 24h")
            
            if warning_count > 0:
                self.info.append(f"{warning_count} warnings in last 24h")
            
            return True
            
        except Exception as e:
            self.issues.append(f"Error analyzing logs: {str(e)}")
            return False
    
    def check_disk_space(self):
        """Check available disk space."""
        try:
            import shutil
            
            total, used, free = shutil.disk_usage(self.base_dir)
            
            free_gb = free / (1024 ** 3)
            
            if free_gb < 1:
                self.issues.append(
                    f"Low disk space: {free_gb:.1f} GB free"
                )
                return False
            elif free_gb < 5:
                self.warnings.append(
                    f"Disk space getting low: {free_gb:.1f} GB free"
                )
            else:
                self.info.append(f"✓ Disk space: {free_gb:.1f} GB free")
            
            return True
            
        except Exception as e:
            self.warnings.append(f"Could not check disk space: {str(e)}")
            return True
    
    def check_profiles_directory(self):
        """Check if profiles are being created."""
        meetings_dir = self.base_dir / 'records' / 'meetings'
        
        if not meetings_dir.exists():
            self.issues.append("Meetings directory does not exist")
            return False
        
        # Count profile directories (exclude .processed.json)
        profiles = [
            d for d in meetings_dir.iterdir()
            if d.is_dir() and not d.name.startswith('.')
        ]
        
        if len(profiles) == 0:
            self.info.append("No profiles created yet (waiting for meetings)")
        else:
            self.info.append(f"✓ {len(profiles)} stakeholder profiles created")
        
        return True
    
    def run_all_checks(self):
        """Run all health checks."""
        checks = [
            ("Last Cycle Time", self.check_last_cycle),
            ("Log File Status", self.check_log_file),
            ("Error Rate", self.check_error_rate),
            ("Disk Space", self.check_disk_space),
            ("Profiles", self.check_profiles_directory)
        ]
        
        results = {}
        
        for check_name, check_func in checks:
            try:
                results[check_name] = check_func()
            except Exception as e:
                self.issues.append(f"{check_name} check failed: {str(e)}")
                results[check_name] = False
        
        return results
    
    def generate_report(self, results):
        """Generate health report."""
        lines = []
        
        lines.append("=" * 60)
        lines.append("Meeting Monitor Health Report")
        lines.append("=" * 60)
        
        timestamp = datetime.now(self.et_tz).strftime('%Y-%m-%d %I:%M %p ET')
        lines.append(f"Generated: {timestamp}")
        lines.append("")
        
        # Overall status
        has_issues = len(self.issues) > 0
        has_warnings = len(self.warnings) > 0
        
        if has_issues:
            status = "🔴 CRITICAL ISSUES"
        elif has_warnings:
            status = "🟡 WARNINGS"
        else:
            status = "🟢 HEALTHY"
        
        lines.append(f"Status: {status}")
        lines.append("")
        
        # Check results
        lines.append("Check Results:")
        lines.append("-" * 60)
        
        for check_name, passed in results.items():
            symbol = "✓" if passed else "✗"
            lines.append(f"  {symbol} {check_name}")
        
        lines.append("")
        
        # Issues
        if self.issues:
            lines.append("Critical Issues:")
            lines.append("-" * 60)
            for issue in self.issues:
                lines.append(f"  ⚠️  {issue}")
            lines.append("")
        
        # Warnings
        if self.warnings:
            lines.append("Warnings:")
            lines.append("-" * 60)
            for warning in self.warnings:
                lines.append(f"  ⚠  {warning}")
            lines.append("")
        
        # Info
        if self.info:
            lines.append("Information:")
            lines.append("-" * 60)
            for info_item in self.info:
                lines.append(f"  {info_item}")
            lines.append("")
        
        # Recommendations
        if has_issues or has_warnings:
            lines.append("Recommendations:")
            lines.append("-" * 60)
            
            if has_issues:
                lines.append("  • Investigate critical issues immediately")
                lines.append("  • Check logs: N5/logs/meeting_monitor.log")
                lines.append("  • Verify scheduled task is running")
            
            if has_warnings:
                lines.append("  • Monitor warnings for escalation")
                lines.append("  • Consider addressing warnings if persistent")
            
            lines.append("")
        
        lines.append("=" * 60)
        
        return '\n'.join(lines)
    
    def save_report(self, report_text):
        """Save health report to file."""
        log_dir = self.base_dir / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / 'health_check.log'
        timestamp = datetime.now(self.et_tz).strftime('%Y-%m-%d %I:%M:%S %p ET')
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"Health Check: {timestamp}\n")
            f.write(f"{'='*60}\n")
            f.write(report_text)
            f.write("\n\n")
    
    def run(self):
        """Execute health monitoring."""
        results = self.run_all_checks()
        report = self.generate_report(results)
        
        print(report)
        
        # Save to log file
        self.save_report(report)
        
        # Return exit code based on health
        if self.issues:
            return 1  # Critical issues
        else:
            return 0  # Healthy or warnings only


def main():
    """Run health monitoring."""
    monitor = HealthMonitor()
    exit_code = monitor.run()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
