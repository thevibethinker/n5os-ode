# N5 Telemetry System

**Created:** 2025-10-26  
**Purpose:** Track system health, flow efficiency, and principle adherence

---

## Components

### 1. Health Check (`n5_health_check.py`)
Daily system health monitoring:
- Stale files in Records/Temporary/
- Empty files across N5/Knowledge/Documents
- Uncommitted git changes
- Orphaned tasks in Lists

**Usage:**
```bash
python3 N5/telemetry/n5_health_check.py
python3 N5/telemetry/n5_health_check.py --dry-run
python3 N5/telemetry/n5_health_check.py --email
```

### 2. Usage Tracker (`usage_tracker.py`)
Lightweight command usage logging to `usage.jsonl`

**Integration:**
Add to command entry points:
```python
from N5.telemetry.usage_tracker import track_usage
track_usage("meeting-process", status="success", duration_ms=1234)
```

### 3. Daily Digest
Scheduled task (8am ET) that runs health check and emails summary

---

## Metrics Storage

- `usage.jsonl` - Command usage logs (append-only)
- `health_history.jsonl` - Daily health check snapshots
- `daily_report.md` - Latest health check (human-readable)

---

## Future: Prometheus Integration

When ready for full telemetry:
- Custom collectors export metrics to Prometheus format
- Grafana Cloud dashboards visualize trends
- Alerts on threshold violations
