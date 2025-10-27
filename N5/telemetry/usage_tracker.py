#!/usr/bin/env python3
"""
N5 Usage Tracker - Lightweight command usage logging
Simple append-only JSONL logging for command invocations
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

TELEMETRY_DIR = Path("/home/workspace/N5/telemetry")
USAGE_LOG = TELEMETRY_DIR / "usage.jsonl"


def track_usage(
    command: str,
    status: str = "success",
    duration_ms: int = 0,
    metadata: Optional[dict] = None
) -> None:
    """
    Track command usage to JSONL log
    
    Args:
        command: Command name (e.g., "meeting-process", "thread-export")
        status: "success", "error", "timeout"
        duration_ms: Execution time in milliseconds
        metadata: Optional additional context (dict)
    """
    try:
        # Ensure telemetry directory exists
        TELEMETRY_DIR.mkdir(parents=True, exist_ok=True)
        
        # Build log entry
        entry = {
            "timestamp": datetime.now().isoformat(),
            "command": command,
            "status": status,
            "duration_ms": duration_ms
        }
        
        # Add metadata if provided
        if metadata:
            entry["metadata"] = metadata
        
        # Append to log file
        with USAGE_LOG.open('a') as f:
            f.write(json.dumps(entry) + "\n")
        
        logger.debug(f"Tracked: {command} ({status}, {duration_ms}ms)")
        
    except Exception as e:
        # Don't fail command execution if tracking fails
        logger.warning(f"Failed to track usage for {command}: {e}")


def get_usage_stats(days: int = 7) -> dict:
    """
    Get usage statistics for the past N days
    
    Returns:
        Dictionary with command counts, success rates, avg duration
    """
    try:
        if not USAGE_LOG.exists():
            return {"error": "No usage data found"}
        
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=days)
        
        # Parse log entries
        entries = []
        with USAGE_LOG.open('r') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    entry_time = datetime.fromisoformat(entry["timestamp"])
                    if entry_time >= cutoff:
                        entries.append(entry)
                except Exception as e:
                    logger.warning(f"Failed to parse log entry: {e}")
        
        if not entries:
            return {"message": f"No entries in past {days} days"}
        
        # Calculate statistics
        command_counts = {}
        command_durations = {}
        command_errors = {}
        
        for entry in entries:
            cmd = entry["command"]
            
            # Count invocations
            command_counts[cmd] = command_counts.get(cmd, 0) + 1
            
            # Track durations
            if cmd not in command_durations:
                command_durations[cmd] = []
            command_durations[cmd].append(entry.get("duration_ms", 0))
            
            # Track errors
            if entry["status"] != "success":
                command_errors[cmd] = command_errors.get(cmd, 0) + 1
        
        # Calculate averages
        stats = {
            "period_days": days,
            "total_invocations": len(entries),
            "unique_commands": len(command_counts),
            "commands": {}
        }
        
        for cmd in command_counts:
            durations = command_durations[cmd]
            avg_duration = sum(durations) / len(durations) if durations else 0
            error_count = command_errors.get(cmd, 0)
            success_rate = ((command_counts[cmd] - error_count) / command_counts[cmd]) * 100
            
            stats["commands"][cmd] = {
                "count": command_counts[cmd],
                "avg_duration_ms": round(avg_duration, 2),
                "success_rate": round(success_rate, 2),
                "errors": error_count
            }
        
        return stats
        
    except Exception as e:
        logger.error(f"Error calculating usage stats: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    # Test tracking
    import argparse
    
    parser = argparse.ArgumentParser(description="N5 Usage Tracker")
    parser.add_argument("--test", action="store_true", help="Test tracking")
    parser.add_argument("--stats", action="store_true", help="Show usage stats")
    parser.add_argument("--days", type=int, default=7, help="Days to analyze")
    
    args = parser.parse_args()
    
    if args.test:
        print("Testing usage tracker...")
        track_usage("test-command", status="success", duration_ms=123)
        print(f"✓ Logged to {USAGE_LOG}")
    
    if args.stats:
        stats = get_usage_stats(days=args.days)
        print(json.dumps(stats, indent=2))
