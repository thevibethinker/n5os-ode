#!/usr/bin/env python3
"""
N5OS Health Sentinel
====================
Monitors system health every 30 minutes, detecting:
- Emergency cascades (CPU/mem/disk, crash loops, runaway logs)
- Degradation/drift warnings (for daily digest)

SMS alerting is gated for development (config: alerting.sms_disabled)

Usage:
    python3 health_sentinel.py [--dry-run] [--verbose] [--check-only]

Version: 1.0.0
Created: 2025-12-16
"""

import argparse
import json
import logging
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import yaml

# ============================================================================
# CONFIGURATION
# ============================================================================

SCRIPT_DIR = Path(__file__).parent
N5_ROOT = Path("/home/workspace/N5")
CONFIG_PATH = N5_ROOT / "config" / "health_sentinel.yaml"

# Setup logging
LOG_DIR = N5_ROOT / "logs" / "maintenance" / "health"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class Alert:
    """Represents a single alert."""
    level: str  # "emergency" or "degradation"
    category: str  # cpu, memory, disk, crash_loop, log_growth, process, service, database
    message: str
    value: float
    threshold: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    service_name: Optional[str] = None
    
    def to_dict(self):
        return asdict(self)


@dataclass 
class HealthReport:
    """Aggregated health report."""
    timestamp: str
    status: str  # "healthy", "degraded", "emergency"
    emergencies: list
    degradations: list
    metrics: dict
    
    def to_dict(self):
        return {
            "timestamp": self.timestamp,
            "status": self.status,
            "emergencies": [a.to_dict() if hasattr(a, 'to_dict') else a for a in self.emergencies],
            "degradations": [a.to_dict() if hasattr(a, 'to_dict') else a for a in self.degradations],
            "metrics": self.metrics
        }


# ============================================================================
# CONFIG LOADING
# ============================================================================

def load_config() -> dict:
    """Load and validate configuration."""
    if not CONFIG_PATH.exists():
        logger.error(f"Config file not found: {CONFIG_PATH}")
        sys.exit(1)
    
    with open(CONFIG_PATH, 'r') as f:
        config = yaml.safe_load(f)
    
    return config


# ============================================================================
# STATE MANAGEMENT (for rate limiting and dedup)
# ============================================================================

def load_state(state_file: Path) -> dict:
    """Load alert state for rate limiting and dedup."""
    if state_file.exists():
        try:
            return json.loads(state_file.read_text())
        except json.JSONDecodeError:
            logger.warning("Corrupted state file, starting fresh")
    
    return {
        "last_alerts": {},
        "alerts_this_hour": 0,
        "hour_started": datetime.now().isoformat()
    }


def save_state(state_file: Path, state: dict):
    """Save alert state."""
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps(state, indent=2))


def should_alert(state: dict, alert: Alert, config: dict) -> bool:
    """Check if alert should fire based on rate limiting and dedup."""
    alerting_config = config.get("alerting", {})
    
    # Check circuit breaker
    max_alerts = alerting_config.get("max_alerts_per_hour", 10)
    hour_started = datetime.fromisoformat(state.get("hour_started", datetime.now().isoformat()))
    
    if datetime.now() - hour_started > timedelta(hours=1):
        # Reset hourly counter
        state["alerts_this_hour"] = 0
        state["hour_started"] = datetime.now().isoformat()
    
    if state["alerts_this_hour"] >= max_alerts:
        logger.warning(f"Circuit breaker triggered: {max_alerts} alerts/hour limit reached")
        return False
    
    # Check dedup window
    dedup_minutes = alerting_config.get("dedup_window_minutes", 15)
    alert_key = f"{alert.level}:{alert.category}:{alert.service_name or 'system'}"
    
    last_alert_time = state.get("last_alerts", {}).get(alert_key)
    if last_alert_time:
        last_time = datetime.fromisoformat(last_alert_time)
        if datetime.now() - last_time < timedelta(minutes=dedup_minutes):
            logger.debug(f"Dedup: skipping duplicate alert {alert_key}")
            return False
    
    # Check rate limiting
    rate_limit_minutes = alerting_config.get("rate_limit_minutes", 30)
    if last_alert_time:
        last_time = datetime.fromisoformat(last_alert_time)
        if datetime.now() - last_time < timedelta(minutes=rate_limit_minutes):
            logger.debug(f"Rate limited: {alert_key}")
            return False
    
    return True


def record_alert(state: dict, alert: Alert):
    """Record that an alert was sent."""
    alert_key = f"{alert.level}:{alert.category}:{alert.service_name or 'system'}"
    
    if "last_alerts" not in state:
        state["last_alerts"] = {}
    
    state["last_alerts"][alert_key] = datetime.now().isoformat()
    state["alerts_this_hour"] = state.get("alerts_this_hour", 0) + 1


# ============================================================================
# SYSTEM METRICS COLLECTION
# ============================================================================

def get_cpu_percent() -> float:
    """Get current CPU usage percentage."""
    try:
        # Use /proc/stat for CPU info
        result = subprocess.run(
            ["grep", "cpu ", "/proc/stat"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            values = result.stdout.split()[1:]
            values = [int(v) for v in values]
            idle = values[3]
            total = sum(values)
            # Store for delta calculation
            state_file = Path("/tmp/health_sentinel_cpu_state")
            
            if state_file.exists():
                prev = json.loads(state_file.read_text())
                prev_idle = prev.get("idle", idle)
                prev_total = prev.get("total", total)
                
                idle_delta = idle - prev_idle
                total_delta = total - prev_total
                
                if total_delta > 0:
                    cpu_percent = 100.0 * (1.0 - idle_delta / total_delta)
                else:
                    cpu_percent = 0.0
            else:
                cpu_percent = 0.0  # First run, no delta
            
            state_file.write_text(json.dumps({"idle": idle, "total": total}))
            return round(cpu_percent, 1)
    except Exception as e:
        logger.warning(f"Failed to get CPU percent: {e}")
    
    return 0.0


def get_memory_percent() -> tuple[float, dict]:
    """Get memory usage percentage and details."""
    try:
        result = subprocess.run(["free", "-b"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            mem_line = lines[1].split()
            total = int(mem_line[1])
            used = int(mem_line[2])
            available = int(mem_line[6])
            
            percent = 100.0 * (total - available) / total
            details = {
                "total_gb": round(total / (1024**3), 1),
                "used_gb": round(used / (1024**3), 1),
                "available_gb": round(available / (1024**3), 1)
            }
            return round(percent, 1), details
    except Exception as e:
        logger.warning(f"Failed to get memory stats: {e}")
    
    return 0.0, {}


def get_disk_percent() -> tuple[float, dict]:
    """Get root filesystem usage percentage."""
    try:
        result = subprocess.run(["df", "-B1", "/"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            parts = lines[1].split()
            total = int(parts[1])
            used = int(parts[2])
            available = int(parts[3])
            
            percent = 100.0 * used / total
            details = {
                "total_gb": round(total / (1024**3), 1),
                "used_gb": round(used / (1024**3), 1),
                "available_gb": round(available / (1024**3), 1)
            }
            return round(percent, 1), details
    except Exception as e:
        logger.warning(f"Failed to get disk stats: {e}")
    
    return 0.0, {}


def get_process_count() -> int:
    """Get total number of processes."""
    try:
        result = subprocess.run(["ps", "aux"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return len(result.stdout.strip().split('\n')) - 1  # Minus header
    except Exception as e:
        logger.warning(f"Failed to get process count: {e}")
    return 0


def get_load_average() -> tuple[float, float, float]:
    """Get 1, 5, 15 minute load averages."""
    try:
        with open("/proc/loadavg", 'r') as f:
            parts = f.read().split()
            return float(parts[0]), float(parts[1]), float(parts[2])
    except Exception as e:
        logger.warning(f"Failed to get load average: {e}")
    return 0.0, 0.0, 0.0


# ============================================================================
# SERVICE MONITORING
# ============================================================================

def check_service_crash_loops(services: list, config: dict) -> list[Alert]:
    """Check for services in crash loop state."""
    alerts = []
    crash_config = config.get("emergency", {}).get("crash_loop", {})
    threshold = crash_config.get("restart_count_threshold", 3)
    window_minutes = crash_config.get("window_minutes", 10)
    
    for service in services:
        service_name = service.get("name")
        log_file = Path(f"/dev/shm/{service_name}.log")
        err_file = Path(f"/dev/shm/{service_name}_err.log")
        
        # Check for restart patterns in logs
        restart_count = 0
        cutoff_time = datetime.now() - timedelta(minutes=window_minutes)
        
        for log_path in [log_file, err_file]:
            if log_path.exists():
                try:
                    # Check recent log lines for restart indicators
                    result = subprocess.run(
                        ["tail", "-100", str(log_path)],
                        capture_output=True, text=True, timeout=5
                    )
                    if result.returncode == 0:
                        content = result.stdout.lower()
                        restart_patterns = ["starting", "listening on", "server started", "initialized"]
                        for pattern in restart_patterns:
                            restart_count += content.count(pattern)
                except Exception as e:
                    logger.debug(f"Error checking {log_path}: {e}")
        
        # Normalize (multiple patterns per restart)
        restart_count = restart_count // 3
        
        if restart_count >= threshold:
            alerts.append(Alert(
                level="emergency",
                category="crash_loop",
                message=f"Service {service_name} appears to be in crash loop ({restart_count} restarts in {window_minutes}min)",
                value=restart_count,
                threshold=threshold,
                service_name=service_name
            ))
    
    return alerts


def check_log_growth(services: list, config: dict) -> list[Alert]:
    """Check for runaway log growth."""
    alerts = []
    degradation_config = config.get("degradation", {})
    emergency_config = config.get("emergency", {})
    
    size_warning_mb = degradation_config.get("log_file_size_warning_mb", 50)
    growth_rate_threshold = emergency_config.get("log_growth_rate_mb_per_hour", 100)
    
    # Track log sizes for rate calculation
    state_file = Path("/tmp/health_sentinel_log_sizes")
    current_sizes = {}
    
    for service in services:
        service_name = service.get("name")
        log_file = Path(f"/dev/shm/{service_name}.log")
        err_file = Path(f"/dev/shm/{service_name}_err.log")
        
        for log_path in [log_file, err_file]:
            if log_path.exists():
                try:
                    size_mb = log_path.stat().st_size / (1024 * 1024)
                    current_sizes[str(log_path)] = {
                        "size_mb": size_mb,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    # Check absolute size
                    if size_mb > size_warning_mb:
                        alerts.append(Alert(
                            level="degradation",
                            category="log_growth",
                            message=f"Log file {log_path.name} is large ({size_mb:.1f}MB)",
                            value=size_mb,
                            threshold=size_warning_mb,
                            service_name=service_name
                        ))
                except Exception as e:
                    logger.debug(f"Error checking {log_path}: {e}")
    
    # Check growth rate if we have previous data
    if state_file.exists():
        try:
            prev_sizes = json.loads(state_file.read_text())
            for log_path, current in current_sizes.items():
                if log_path in prev_sizes:
                    prev = prev_sizes[log_path]
                    prev_time = datetime.fromisoformat(prev["timestamp"])
                    hours_elapsed = (datetime.now() - prev_time).total_seconds() / 3600
                    
                    if hours_elapsed > 0.1:  # At least 6 minutes
                        growth_mb = current["size_mb"] - prev["size_mb"]
                        growth_rate = growth_mb / hours_elapsed
                        
                        if growth_rate > growth_rate_threshold:
                            alerts.append(Alert(
                                level="emergency",
                                category="log_growth",
                                message=f"Runaway log growth: {Path(log_path).name} growing at {growth_rate:.1f}MB/hour",
                                value=growth_rate,
                                threshold=growth_rate_threshold
                            ))
        except Exception as e:
            logger.debug(f"Error reading previous log sizes: {e}")
    
    state_file.write_text(json.dumps(current_sizes))
    
    return alerts


def check_stale_services(services: list, config: dict) -> list[Alert]:
    """Check for services with no recent log activity."""
    alerts = []
    stale_minutes = config.get("degradation", {}).get("stale_service_minutes", 60)
    cutoff_time = datetime.now() - timedelta(minutes=stale_minutes)
    
    for service in services:
        service_name = service.get("name")
        log_file = Path(f"/dev/shm/{service_name}.log")
        
        if log_file.exists():
            try:
                mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                if mtime < cutoff_time:
                    minutes_stale = int((datetime.now() - mtime).total_seconds() / 60)
                    alerts.append(Alert(
                        level="degradation",
                        category="service",
                        message=f"Service {service_name} appears stale (no log writes for {minutes_stale}min)",
                        value=minutes_stale,
                        threshold=stale_minutes,
                        service_name=service_name
                    ))
            except Exception as e:
                logger.debug(f"Error checking {log_file}: {e}")
        else:
            # Log file doesn't exist - service may not be running
            alerts.append(Alert(
                level="degradation",
                category="service",
                message=f"Service {service_name} log not found (may not be running)",
                value=0,
                threshold=0,
                service_name=service_name
            ))
    
    return alerts


# ============================================================================
# DATABASE MONITORING
# ============================================================================

def check_database_sizes(databases: list, config: dict) -> list[Alert]:
    """Check database file sizes."""
    alerts = []
    size_warning_mb = config.get("degradation", {}).get("db_size_warning_mb", 500)
    
    for db in databases:
        db_path = Path(db.get("path"))
        db_name = db.get("name")
        is_critical = db.get("critical", False)
        
        if db_path.exists():
            try:
                size_mb = db_path.stat().st_size / (1024 * 1024)
                
                if size_mb > size_warning_mb:
                    alerts.append(Alert(
                        level="degradation",
                        category="database",
                        message=f"Database {db_name} is large ({size_mb:.1f}MB)",
                        value=size_mb,
                        threshold=size_warning_mb,
                        service_name=db_name
                    ))
            except Exception as e:
                logger.debug(f"Error checking {db_path}: {e}")
        elif is_critical:
            alerts.append(Alert(
                level="emergency",
                category="database",
                message=f"Critical database {db_name} not found: {db_path}",
                value=0,
                threshold=0,
                service_name=db_name
            ))
    
    return alerts


# ============================================================================
# RESOURCE THRESHOLDS
# ============================================================================

def check_resource_thresholds(config: dict) -> tuple[list[Alert], dict]:
    """Check CPU, memory, disk against thresholds."""
    alerts = []
    metrics = {}
    
    emergency = config.get("emergency", {})
    degradation = config.get("degradation", {})
    
    # CPU
    cpu_percent = get_cpu_percent()
    metrics["cpu_percent"] = cpu_percent
    
    if cpu_percent >= emergency.get("cpu_percent_threshold", 90):
        alerts.append(Alert(
            level="emergency",
            category="cpu",
            message=f"CPU usage critical: {cpu_percent}%",
            value=cpu_percent,
            threshold=emergency.get("cpu_percent_threshold", 90)
        ))
    elif cpu_percent >= degradation.get("cpu_percent_warning", 70):
        alerts.append(Alert(
            level="degradation",
            category="cpu",
            message=f"CPU usage elevated: {cpu_percent}%",
            value=cpu_percent,
            threshold=degradation.get("cpu_percent_warning", 70)
        ))
    
    # Memory
    mem_percent, mem_details = get_memory_percent()
    metrics["memory_percent"] = mem_percent
    metrics["memory_details"] = mem_details
    
    if mem_percent >= emergency.get("memory_percent_threshold", 95):
        alerts.append(Alert(
            level="emergency",
            category="memory",
            message=f"Memory usage critical: {mem_percent}% ({mem_details.get('available_gb', 0)}GB available)",
            value=mem_percent,
            threshold=emergency.get("memory_percent_threshold", 95)
        ))
    elif mem_percent >= degradation.get("memory_percent_warning", 80):
        alerts.append(Alert(
            level="degradation",
            category="memory",
            message=f"Memory usage elevated: {mem_percent}%",
            value=mem_percent,
            threshold=degradation.get("memory_percent_warning", 80)
        ))
    
    # Disk
    disk_percent, disk_details = get_disk_percent()
    metrics["disk_percent"] = disk_percent
    metrics["disk_details"] = disk_details
    
    if disk_percent >= emergency.get("disk_percent_threshold", 95):
        alerts.append(Alert(
            level="emergency",
            category="disk",
            message=f"Disk usage critical: {disk_percent}% ({disk_details.get('available_gb', 0)}GB available)",
            value=disk_percent,
            threshold=emergency.get("disk_percent_threshold", 95)
        ))
    elif disk_percent >= degradation.get("disk_percent_warning", 80):
        alerts.append(Alert(
            level="degradation",
            category="disk",
            message=f"Disk usage elevated: {disk_percent}%",
            value=disk_percent,
            threshold=degradation.get("disk_percent_warning", 80)
        ))
    
    # Process count
    process_count = get_process_count()
    metrics["process_count"] = process_count
    
    max_processes = emergency.get("max_process_count", 500)
    if process_count >= max_processes:
        alerts.append(Alert(
            level="emergency",
            category="process",
            message=f"Process count high: {process_count} (threshold: {max_processes})",
            value=process_count,
            threshold=max_processes
        ))
    
    # Load average
    load1, load5, load15 = get_load_average()
    metrics["load_average"] = {"1min": load1, "5min": load5, "15min": load15}
    
    return alerts, metrics


# ============================================================================
# ALERTING
# ============================================================================

def send_emergency_sms(alerts: list[Alert], config: dict, dry_run: bool = False):
    """Send SMS for emergency alerts (gated for development)."""
    alerting = config.get("alerting", {})
    
    if alerting.get("sms_disabled", True):
        logger.info("📱 SMS is GATED (sms_disabled=true). Would send:")
        for alert in alerts:
            logger.info(f"  🚨 {alert.message}")
        return
    
    if dry_run:
        logger.info("[DRY RUN] Would send SMS:")
        for alert in alerts:
            logger.info(f"  🚨 {alert.message}")
        return
    
    # Compose SMS message
    message_lines = ["🚨 N5OS EMERGENCY 🚨"]
    for alert in alerts[:3]:  # Max 3 alerts in SMS
        message_lines.append(f"• {alert.category.upper()}: {alert.message}")
    
    if len(alerts) > 3:
        message_lines.append(f"+ {len(alerts) - 3} more alerts")
    
    message = "\n".join(message_lines)
    
    # Use the existing SMS notification script
    try:
        result = subprocess.run(
            ["python3", "/home/workspace/N5/scripts/send_sms_notification.py", message],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            logger.info("✅ Emergency SMS sent")
        else:
            logger.error(f"❌ SMS send failed: {result.stderr}")
    except Exception as e:
        logger.error(f"❌ SMS send error: {e}")


# ============================================================================
# DIGEST INTEGRATION
# ============================================================================

def write_digest_file(report: HealthReport, config: dict):
    """Write degradation report for daily digest inclusion."""
    digest_file = Path(config.get("output", {}).get("digest_file", "/home/workspace/N5/data/health_sentinel_digest.json"))
    digest_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Format for digest consumption
    digest_data = {
        "generated": report.timestamp,
        "status": report.status,
        "metrics": report.metrics,
        "warnings": [
            {
                "category": d.category if hasattr(d, 'category') else d.get('category'),
                "message": d.message if hasattr(d, 'message') else d.get('message'),
                "value": d.value if hasattr(d, 'value') else d.get('value'),
                "threshold": d.threshold if hasattr(d, 'threshold') else d.get('threshold')
            }
            for d in report.degradations
        ],
        "emergencies": [
            {
                "category": e.category if hasattr(e, 'category') else e.get('category'),
                "message": e.message if hasattr(e, 'message') else e.get('message')
            }
            for e in report.emergencies
        ]
    }
    
    digest_file.write_text(json.dumps(digest_data, indent=2))
    logger.info(f"✓ Digest file written: {digest_file}")


def generate_markdown_summary(report: HealthReport) -> str:
    """Generate a markdown summary for manual review or daily report inclusion."""
    lines = [
        f"## 🏥 Health Sentinel Report",
        f"*Generated: {report.timestamp}*",
        f"",
        f"**Status: {report.status.upper()}**",
        f"",
        "### Metrics",
        f"- CPU: {report.metrics.get('cpu_percent', 0)}%",
        f"- Memory: {report.metrics.get('memory_percent', 0)}%",
        f"- Disk: {report.metrics.get('disk_percent', 0)}%",
        f"- Processes: {report.metrics.get('process_count', 0)}",
        ""
    ]
    
    if report.emergencies:
        lines.append("### 🚨 Emergencies")
        for e in report.emergencies:
            msg = e.message if hasattr(e, 'message') else e.get('message', str(e))
            lines.append(f"- {msg}")
        lines.append("")
    
    if report.degradations:
        lines.append("### ⚠️ Warnings")
        for d in report.degradations:
            msg = d.message if hasattr(d, 'message') else d.get('message', str(d))
            lines.append(f"- {msg}")
        lines.append("")
    
    if not report.emergencies and not report.degradations:
        lines.append("*All systems nominal.*")
    
    return "\n".join(lines)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def run_sentinel(dry_run: bool = False, verbose: bool = False, check_only: bool = False) -> HealthReport:
    """Main sentinel execution."""
    logger.info("=" * 60)
    logger.info("N5OS Health Sentinel Starting")
    logger.info("=" * 60)
    
    config = load_config()
    
    all_emergencies = []
    all_degradations = []
    
    # Check resource thresholds
    logger.info("Checking resource thresholds...")
    resource_alerts, metrics = check_resource_thresholds(config)
    
    for alert in resource_alerts:
        if alert.level == "emergency":
            all_emergencies.append(alert)
        else:
            all_degradations.append(alert)
    
    # Check services
    services = config.get("monitored_services", [])
    
    logger.info(f"Checking {len(services)} services for crash loops...")
    crash_alerts = check_service_crash_loops(services, config)
    all_emergencies.extend([a for a in crash_alerts if a.level == "emergency"])
    all_degradations.extend([a for a in crash_alerts if a.level == "degradation"])
    
    logger.info("Checking log growth...")
    log_alerts = check_log_growth(services, config)
    all_emergencies.extend([a for a in log_alerts if a.level == "emergency"])
    all_degradations.extend([a for a in log_alerts if a.level == "degradation"])
    
    logger.info("Checking service staleness...")
    stale_alerts = check_stale_services(services, config)
    all_degradations.extend(stale_alerts)
    
    # Check databases
    databases = config.get("monitored_databases", [])
    logger.info(f"Checking {len(databases)} databases...")
    db_alerts = check_database_sizes(databases, config)
    all_emergencies.extend([a for a in db_alerts if a.level == "emergency"])
    all_degradations.extend([a for a in db_alerts if a.level == "degradation"])
    
    # Determine overall status
    if all_emergencies:
        status = "emergency"
    elif all_degradations:
        status = "degraded"
    else:
        status = "healthy"
    
    report = HealthReport(
        timestamp=datetime.now().isoformat(),
        status=status,
        emergencies=all_emergencies,
        degradations=all_degradations,
        metrics=metrics
    )
    
    # Log summary
    logger.info("-" * 40)
    logger.info(f"Status: {status.upper()}")
    logger.info(f"Emergencies: {len(all_emergencies)}")
    logger.info(f"Degradations: {len(all_degradations)}")
    logger.info(f"CPU: {metrics.get('cpu_percent', 0)}%")
    logger.info(f"Memory: {metrics.get('memory_percent', 0)}%")
    logger.info(f"Disk: {metrics.get('disk_percent', 0)}%")
    logger.info("-" * 40)
    
    if check_only:
        logger.info("[CHECK ONLY] No alerts sent, no digest written.")
        print(generate_markdown_summary(report))
        return report
    
    # Handle emergencies
    if all_emergencies:
        state_file = Path(config.get("output", {}).get("state_file", "/home/workspace/N5/data/health_sentinel_state.json"))
        state = load_state(state_file)
        
        alerts_to_send = []
        for alert in all_emergencies:
            if should_alert(state, alert, config):
                alerts_to_send.append(alert)
                record_alert(state, alert)
        
        save_state(state_file, state)
        
        if alerts_to_send:
            send_emergency_sms(alerts_to_send, config, dry_run=dry_run)
    
    # Write digest file for daily integration
    write_digest_file(report, config)
    
    # Print summary
    if verbose:
        print(generate_markdown_summary(report))
    
    logger.info("N5OS Health Sentinel Complete")
    return report


def main():
    parser = argparse.ArgumentParser(
        description="N5OS Health Sentinel - System health monitoring",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python3 health_sentinel.py              # Normal run
    python3 health_sentinel.py --dry-run    # Preview without alerting
    python3 health_sentinel.py --check-only # Just check and print status
    python3 health_sentinel.py --verbose    # Show full report
        """
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview alerts without sending SMS"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print full markdown report"
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Check status only, no alerts or digest output"
    )
    
    args = parser.parse_args()
    
    report = run_sentinel(
        dry_run=args.dry_run,
        verbose=args.verbose,
        check_only=args.check_only
    )
    
    # Exit code based on status
    if report.status == "emergency":
        return 2
    elif report.status == "degraded":
        return 1
    else:
        return 0


if __name__ == "__main__":
    sys.exit(main())

