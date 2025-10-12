#!/usr/bin/env python3
"""
Performance Dashboard - Priority 4
Generate performance metrics dashboard for meeting monitor.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import pytz


class DashboardGenerator:
    """Generate performance dashboard for meeting monitor."""
    
    def __init__(self, days=7):
        self.base_dir = Path(__file__).parent.parent
        self.et_tz = pytz.timezone('America/New_York')
        self.days = days
        
    def load_state(self):
        """Load state file."""
        state_file = self.base_dir / 'records' / 'meetings' / '.processed.json'
        
        if not state_file.exists():
            return None
        
        with open(state_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def analyze_log_file(self):
        """Analyze log file for metrics."""
        log_file = self.base_dir / 'logs' / 'meeting_monitor.log'
        
        if not log_file.exists():
            return None
        
        metrics = {
            'total_cycles': 0,
            'successful_cycles': 0,
            'errors': 0,
            'warnings': 0,
            'cycle_times': [],
            'events_by_day': defaultdict(int),
            'urgent_by_day': defaultdict(int)
        }
        
        current_cycle_start = None
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    # Count cycles
                    if 'Cycle' in line and 'started' in line:
                        metrics['total_cycles'] += 1
                        current_cycle_start = line
                    
                    # Count completions
                    if 'Cycle complete' in line:
                        metrics['successful_cycles'] += 1
                        
                        # Extract event counts
                        if 'events checked' in line:
                            # Parse: "2 events checked, 1 new, ..."
                            parts = line.split(',')
                            for part in parts:
                                if 'new' in part and 'events' not in part:
                                    try:
                                        count = int(part.split()[0])
                                        date = line.split()[0]  # Get date from log
                                        metrics['events_by_day'][date] += count
                                    except:
                                        pass
                                
                                if 'urgent' in part:
                                    try:
                                        count = int(part.split()[0])
                                        date = line.split()[0]
                                        metrics['urgent_by_day'][date] += count
                                    except:
                                        pass
                    
                    # Count errors and warnings
                    if '[ERROR]' in line:
                        metrics['errors'] += 1
                    if '[WARNING]' in line:
                        metrics['warnings'] += 1
                    
                    # Extract cycle times
                    if 'Cycle duration:' in line:
                        try:
                            duration = float(line.split('duration:')[1].split('s')[0].strip())
                            metrics['cycle_times'].append(duration)
                        except:
                            pass
        
        except Exception as e:
            print(f"Error analyzing logs: {e}")
            return None
        
        return metrics
    
    def count_profiles(self):
        """Count stakeholder profiles."""
        meetings_dir = self.base_dir / 'records' / 'meetings'
        
        if not meetings_dir.exists():
            return 0
        
        profiles = [
            d for d in meetings_dir.iterdir()
            if d.is_dir() and not d.name.startswith('.')
        ]
        
        return len(profiles)
    
    def calculate_statistics(self, metrics):
        """Calculate statistical summaries."""
        if not metrics or not metrics['cycle_times']:
            return {}
        
        cycle_times = metrics['cycle_times']
        
        stats = {
            'avg_cycle_time': sum(cycle_times) / len(cycle_times) if cycle_times else 0,
            'min_cycle_time': min(cycle_times) if cycle_times else 0,
            'max_cycle_time': max(cycle_times) if cycle_times else 0,
            'success_rate': (
                metrics['successful_cycles'] / metrics['total_cycles'] * 100
                if metrics['total_cycles'] > 0 else 0
            ),
            'error_rate': (
                metrics['errors'] / metrics['total_cycles']
                if metrics['total_cycles'] > 0 else 0
            )
        }
        
        return stats
    
    def generate_markdown_dashboard(self, metrics, stats, profile_count):
        """Generate markdown dashboard."""
        lines = []
        
        timestamp = datetime.now(self.et_tz).strftime('%Y-%m-%d %I:%M %p ET')
        
        lines.append("# Meeting Monitor Performance Dashboard")
        lines.append("")
        lines.append(f"**Generated:** {timestamp}")
        lines.append(f"**Period:** Last {self.days} days")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Overall metrics
        lines.append("## 📊 Overall Metrics")
        lines.append("")
        
        if metrics:
            lines.append(f"- **Total Cycles:** {metrics['total_cycles']}")
            lines.append(f"- **Successful Cycles:** {metrics['successful_cycles']}")
            lines.append(f"- **Success Rate:** {stats.get('success_rate', 0):.1f}%")
            lines.append(f"- **Errors:** {metrics['errors']}")
            lines.append(f"- **Warnings:** {metrics['warnings']}")
        else:
            lines.append("*No metrics available yet - system may not have run*")
        
        lines.append("")
        
        # Meeting metrics
        lines.append("## 📅 Meeting Processing")
        lines.append("")
        lines.append(f"- **Stakeholder Profiles:** {profile_count}")
        
        if metrics:
            total_events = sum(metrics['events_by_day'].values())
            total_urgent = sum(metrics['urgent_by_day'].values())
            
            lines.append(f"- **Total Events Processed:** {total_events}")
            lines.append(f"- **Urgent Meetings:** {total_urgent}")
            
            if total_events > 0:
                urgent_pct = (total_urgent / total_events * 100)
                lines.append(f"- **Urgent Rate:** {urgent_pct:.1f}%")
        
        lines.append("")
        
        # Performance metrics
        if stats and metrics and metrics['cycle_times']:
            lines.append("## ⚡ Performance")
            lines.append("")
            lines.append(f"- **Average Cycle Time:** {stats['avg_cycle_time']:.2f}s")
            lines.append(f"- **Min Cycle Time:** {stats['min_cycle_time']:.2f}s")
            lines.append(f"- **Max Cycle Time:** {stats['max_cycle_time']:.2f}s")
            lines.append("")
        
        # Daily breakdown
        if metrics and metrics['events_by_day']:
            lines.append("## 📈 Daily Breakdown")
            lines.append("")
            lines.append("| Date | Events | Urgent |")
            lines.append("|------|--------|--------|")
            
            for date in sorted(metrics['events_by_day'].keys(), reverse=True)[:7]:
                events = metrics['events_by_day'][date]
                urgent = metrics['urgent_by_day'].get(date, 0)
                lines.append(f"| {date} | {events} | {urgent} |")
            
            lines.append("")
        
        # Health status
        lines.append("## 🏥 Health Status")
        lines.append("")
        
        if metrics:
            if metrics['errors'] == 0:
                lines.append("✅ **Status:** Healthy (no errors)")
            elif metrics['errors'] < 5:
                lines.append("⚠️  **Status:** Minor issues (few errors)")
            else:
                lines.append("🔴 **Status:** Issues detected (multiple errors)")
            
            if metrics['total_cycles'] > 0:
                expected_cycles = self.days * 24 * 4  # 4 per hour * 24 hours * days
                coverage = (metrics['total_cycles'] / expected_cycles * 100)
                lines.append(f"- **Coverage:** {coverage:.1f}% ({metrics['total_cycles']}/{expected_cycles} expected cycles)")
        else:
            lines.append("⚪ **Status:** System not active yet")
        
        lines.append("")
        
        # Recommendations
        lines.append("## 💡 Recommendations")
        lines.append("")
        
        recommendations = []
        
        if metrics:
            if metrics['errors'] > 5:
                recommendations.append("Investigate error causes in log file")
            
            if stats.get('avg_cycle_time', 0) > 10:
                recommendations.append("Cycle time is high - consider optimization")
            
            if metrics['total_cycles'] < self.days * 24 * 4 * 0.9:
                recommendations.append("Missing cycles - check scheduled task is running")
            
            if stats.get('success_rate', 100) < 95:
                recommendations.append("Low success rate - review error patterns")
        
        if not recommendations:
            recommendations.append("System is performing well - no actions needed")
        
        for rec in recommendations:
            lines.append(f"- {rec}")
        
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("*Dashboard auto-generated by Priority 4 monitoring system*")
        lines.append("")
        
        return '\n'.join(lines)
    
    def save_dashboard(self, content):
        """Save dashboard to file."""
        dashboard_dir = self.base_dir / 'records' / 'dashboards'
        dashboard_dir.mkdir(parents=True, exist_ok=True)
        
        # Save latest
        latest_file = dashboard_dir / 'latest-dashboard.md'
        with open(latest_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Save dated version
        date_str = datetime.now(self.et_tz).strftime('%Y-%m-%d')
        dated_file = dashboard_dir / f'dashboard-{date_str}.md'
        with open(dated_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return latest_file, dated_file
    
    def generate(self):
        """Generate complete dashboard."""
        print("=" * 60)
        print("Generating Performance Dashboard")
        print("=" * 60)
        print()
        
        # Collect data
        print("Collecting metrics...")
        metrics = self.analyze_log_file()
        stats = self.calculate_statistics(metrics) if metrics else {}
        profile_count = self.count_profiles()
        
        print("✓ Metrics collected")
        print()
        
        # Generate dashboard
        print("Generating dashboard...")
        content = self.generate_markdown_dashboard(metrics, stats, profile_count)
        print("✓ Dashboard generated")
        print()
        
        # Save dashboard
        print("Saving dashboard...")
        latest, dated = self.save_dashboard(content)
        print(f"✓ Saved: {latest.name}")
        print(f"✓ Saved: {dated.name}")
        print()
        
        # Display dashboard
        print("=" * 60)
        print(content)
        print("=" * 60)
        
        return content


def main():
    """Generate dashboard."""
    generator = DashboardGenerator(days=7)
    generator.generate()
    sys.exit(0)


if __name__ == '__main__':
    main()
