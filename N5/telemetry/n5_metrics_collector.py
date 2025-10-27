#!/usr/bin/env python3
"""
N5 Metrics Collector - Prometheus metrics exporter
Exposes n5OS health and principle adherence metrics
"""
import argparse
import json
import logging
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

from prometheus_client import Counter, Gauge, Histogram, start_http_server

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)

# ==================================================
# METRICS DEFINITIONS
# ==================================================

# Flow Efficiency Metrics
records_staging_count = Gauge(
    'n5_records_staging_count',
    'Number of files in Records/Temporary/'
)
records_stale_count = Gauge(
    'n5_records_stale_count',
    'Number of stale files (>7 days) in staging'
)
knowledge_files_total = Gauge(
    'n5_knowledge_files_total',
    'Total files in Knowledge/'
)
lists_pending_count = Gauge(
    'n5_lists_pending_count',
    'Number of pending items in Lists/'
)

# Principle Adherence Metrics
empty_files_count = Gauge(
    'n5_empty_files_count',
    'Number of empty (0-byte) files'
)
uncommitted_count = Gauge(
    'n5_uncommitted_count',
    'Number of uncommitted git changes'
)
readme_duplication = Gauge(
    'n5_readme_duplication',
    'Number of README files (SSOT violation indicator)'
)
script_complexity_avg = Gauge(
    'n5_script_complexity_avg',
    'Average lines of code per script'
)
script_count_total = Gauge(
    'n5_script_count_total',
    'Total number of Python scripts'
)

# Command Usage Metrics
command_invocations = Counter(
    'n5_command_invocations_total',
    'Total command invocations',
    ['command', 'status']
)
command_duration = Histogram(
    'n5_command_duration_seconds',
    'Command execution duration',
    ['command']
)

# System Health
health_check_success = Gauge(
    'n5_health_check_success',
    'Last health check success (1=success, 0=failure)'
)
last_health_check_timestamp = Gauge(
    'n5_last_health_check_timestamp',
    'Unix timestamp of last health check'
)

# ==================================================
# COLLECTORS
# ==================================================

def collect_flow_metrics(base_path: Path) -> Dict:
    """Collect flow efficiency metrics"""
    metrics = {}
    
    # Records staging
    staging = base_path / "Records/Temporary"
    if staging.exists():
        staging_files = list(staging.glob("**/*"))
        staging_files = [f for f in staging_files if f.is_file()]
        metrics['staging_count'] = len(staging_files)
        
        # Stale files (>7 days)
        cutoff = datetime.now() - timedelta(days=7)
        stale = [f for f in staging_files if datetime.fromtimestamp(f.stat().st_mtime) < cutoff]
        metrics['stale_count'] = len(stale)
    else:
        metrics['staging_count'] = 0
        metrics['stale_count'] = 0
    
    # Knowledge growth
    knowledge = base_path / "Knowledge"
    if knowledge.exists():
        knowledge_files = list(knowledge.glob("**/*.md"))
        metrics['knowledge_files'] = len(knowledge_files)
    else:
        metrics['knowledge_files'] = 0
    
    # Lists pending (simplified)
    lists_dir = base_path / "Lists"
    if lists_dir.exists():
        # Count [ ] in list files
        pending = 0
        for list_file in lists_dir.glob("*.md"):
            content = list_file.read_text()
            pending += content.count("- [ ]")
        metrics['pending_tasks'] = pending
    else:
        metrics['pending_tasks'] = 0
    
    return metrics


def collect_principle_metrics(base_path: Path) -> Dict:
    """Collect principle adherence metrics"""
    metrics = {}
    
    # Empty files (P1: Human-Readable)
    empty_files = []
    for pattern in ["N5/**/*", "Knowledge/**/*", "Documents/**/*"]:
        for f in base_path.glob(pattern):
            if f.is_file() and f.stat().st_size == 0:
                empty_files.append(f)
    metrics['empty_files'] = len(empty_files)
    
    # Git uncommitted (P5: Anti-Overwrite)
    try:
        result = subprocess.run(
            ["git", "-C", str(base_path), "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=5
        )
        uncommitted = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
        metrics['uncommitted'] = uncommitted
    except Exception as e:
        logger.warning(f"Git check failed: {e}")
        metrics['uncommitted'] = -1
    
    # README duplication (P2: SSOT)
    readmes = list(base_path.glob("**/README*.md"))
    readmes = [r for r in readmes if "node_modules" not in str(r)]
    metrics['readme_count'] = len(readmes)
    
    # Script complexity (P8: Minimal Context)
    scripts = list((base_path / "N5/scripts").glob("*.py"))
    if scripts:
        total_loc = 0
        for script in scripts:
            try:
                loc = len(script.read_text().split('\n'))
                total_loc += loc
            except:
                pass
        metrics['script_avg_loc'] = total_loc // len(scripts) if scripts else 0
        metrics['script_count'] = len(scripts)
    else:
        metrics['script_avg_loc'] = 0
        metrics['script_count'] = 0
    
    return metrics


def collect_command_usage_metrics(base_path: Path) -> Dict:
    """Collect command usage from usage.jsonl"""
    metrics = {'commands': {}}
    
    usage_log = base_path / "N5/telemetry/usage.jsonl"
    if not usage_log.exists():
        return metrics
    
    try:
        with usage_log.open() as f:
            for line in f:
                entry = json.loads(line.strip())
                cmd = entry['command']
                status = entry['status']
                duration_ms = entry.get('duration_ms', 0)
                
                if cmd not in metrics['commands']:
                    metrics['commands'][cmd] = {'success': 0, 'error': 0, 'durations': []}
                
                metrics['commands'][cmd][status] = metrics['commands'][cmd].get(status, 0) + 1
                metrics['commands'][cmd]['durations'].append(duration_ms / 1000.0)
    except Exception as e:
        logger.warning(f"Failed to parse usage log: {e}")
    
    return metrics


def update_metrics(base_path: Path):
    """Update all Prometheus metrics"""
    try:
        # Flow metrics
        flow = collect_flow_metrics(base_path)
        records_staging_count.set(flow['staging_count'])
        records_stale_count.set(flow['stale_count'])
        knowledge_files_total.set(flow['knowledge_files'])
        lists_pending_count.set(flow['pending_tasks'])
        
        # Principle metrics
        principles = collect_principle_metrics(base_path)
        empty_files_count.set(principles['empty_files'])
        uncommitted_count.set(principles['uncommitted'])
        readme_duplication.set(principles['readme_count'])
        script_complexity_avg.set(principles['script_avg_loc'])
        script_count_total.set(principles['script_count'])
        
        # Command usage
        usage = collect_command_usage_metrics(base_path)
        for cmd, stats in usage.get('commands', {}).items():
            for status in ['success', 'error']:
                count = stats.get(status, 0)
                command_invocations.labels(command=cmd, status=status).inc(count)
            
            for duration in stats.get('durations', []):
                command_duration.labels(command=cmd).observe(duration)
        
        # Health check metadata
        health_check_success.set(1)
        last_health_check_timestamp.set(time.time())
        
        logger.info("✓ Metrics updated successfully")
        
    except Exception as e:
        logger.error(f"Metrics collection failed: {e}")
        health_check_success.set(0)


def main(port: int = 8000, interval: int = 60):
    """Run metrics collector"""
    base_path = Path("/home/workspace")
    
    logger.info(f"Starting N5 Metrics Collector on port {port}...")
    logger.info(f"Update interval: {interval}s")
    
    # Start HTTP server for Prometheus scraping
    start_http_server(port)
    logger.info(f"✓ Metrics endpoint: http://localhost:{port}/metrics")
    
    # Collect metrics in loop
    while True:
        update_metrics(base_path)
        time.sleep(interval)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="N5 Metrics Collector")
    parser.add_argument("--port", type=int, default=8000, help="HTTP port for metrics endpoint")
    parser.add_argument("--interval", type=int, default=60, help="Collection interval (seconds)")
    
    args = parser.parse_args()
    
    try:
        main(port=args.port, interval=args.interval)
    except KeyboardInterrupt:
        logger.info("\n✓ Metrics collector stopped")
