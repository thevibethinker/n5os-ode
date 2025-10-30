# Export Spec 005: Telemetry & Tracking System

**System:** Structured Observability for System Operations  
**Version:** 2.0 (Production)  
**Maturity:** Battle-tested, integrated throughout N5 OS  
**Last Updated:** 2025-10-28

---

## 1. System Overview

### Purpose
Capture operational metrics, quality scores, and diagnostic data across system components. Enable data-driven improvement and issue detection.

### Core Concept
**Observe, measure, improve.**  
Every significant operation emits structured telemetry. Analytics surface patterns. System self-improves based on data.

### Key Innovation
- **Lightweight JSONL format** - append-only, no database required
- **Quality gates** - telemetry drives automatic decisions (BLOCK/ALLOW/PASS)
- **Phase handoff protocol** - standardized telemetry at component boundaries
- **Self-diagnostic** - system can analyze its own telemetry

---

## 2. Architecture

### Data Flow
```
Operation Executes
  ↓
Emit Telemetry (JSONL append)
  ↓
Telemetry Validator (optional real-time)
  ↓
Telemetry Collector (batch analysis)
  ↓
Analytics & Alerts
```

### Storage
**Format:** JSONL (one JSON object per line)  
**Location:** Typically `logs/telemetry/` or component-specific paths  
**Rotation:** Daily or size-based (configurable)  
**Retention:** Configurable (default 90 days)

---

## 3. Telemetry Schema

### Core Fields (Required)
```json
{
  "timestamp": "ISO-8601 datetime with timezone",
  "event_type": "operation|phase|error|metric",
  "component": "identifier of emitting component",
  "status": "SUCCESS|PARTIAL|FAILED|IN_PROGRESS"
}
```

### Extended Fields (Common)
```json
{
  "run_id": "unique identifier for this operation",
  "parent_id": "for hierarchical operations",
  "duration_ms": 1234,
  "input_size": 5678,
  "output_size": 9012,
  "metadata": {
    "arbitrary": "key-value pairs"
  }
}
```

### Phase Handoff Schema
```json
{
  "timestamp": "2025-10-28T12:34:56Z",
  "event_type": "phase",
  "component": "command-author-phase-3",
  "phase_id": 3,
  "phase_name": "generator",
  "status": "SUCCESS",
  "duration_ms": 2345,
  "artifacts": {
    "primary": {"type": "python", "path": "/path/to/script.py"},
    "secondary": [{"type": "json", "path": "/path/to/metadata.json"}]
  },
  "quality_scores": {
    "completeness": 0.95,
    "correctness": 1.0,
    "performance": 0.88
  },
  "warnings": ["minor issue noted"],
  "errors": [],
  "next_phase_ready": true,
  "metadata": {
    "lines_of_code": 142,
    "functions_generated": 5
  }
}
```

### Error Schema
```json
{
  "timestamp": "2025-10-28T12:34:56Z",
  "event_type": "error",
  "component": "lists-add",
  "status": "FAILED",
  "error_type": "ValidationError",
  "error_message": "Schema validation failed: missing required field 'title'",
  "stack_trace": "...",
  "input_data": {"sanitized": "version"},
  "recovery_action": "retry|skip|abort",
  "metadata": {}
}
```

### Metric Schema
```json
{
  "timestamp": "2025-10-28T12:34:56Z",
  "event_type": "metric",
  "component": "docgen",
  "metric_name": "generation_duration",
  "metric_value": 1234,
  "metric_unit": "milliseconds",
  "tags": {
    "mode": "recipes",
    "item_count": 136
  }
}
```

---

## 4. Quality Gates

### Purpose
Use telemetry data to make automatic go/no-go decisions at operation boundaries.

### Gate Levels
**BLOCK:** Operation cannot proceed, must fix issues  
**ALLOW:** Operation can proceed with warnings  
**PASS:** Operation meets all quality standards  

### Gate Evaluation
```python
def evaluate_quality_gate(telemetry):
    score = calculate_quality_score(telemetry)
    
    if score < 0.5:
        return "BLOCK"
    elif score < 0.8:
        return "ALLOW"  # with warnings
    else:
        return "PASS"
```

### Quality Dimensions
- **Completeness:** All required fields present?
- **Correctness:** Data validates against schema?
- **Performance:** Within acceptable time/resource bounds?
- **Consistency:** Matches expected patterns?

---

## 5. Telemetry Collector

### Purpose
Batch analysis of telemetry logs to surface patterns, anomalies, trends.

### Collection Operations
**1. Pattern Detection**
- Identify recurring errors
- Detect performance degradation
- Find correlation between events

**2. Aggregation**
- Success/failure rates by component
- Average duration by operation
- Resource usage trends

**3. Alerting**
- Threshold breaches
- Anomaly detection
- Error rate spikes

### Example Collector
```python
#!/usr/bin/env python3
import json
from pathlib import Path
from collections import Counter, defaultdict

def collect_telemetry(log_path):
    events = []
    for line in Path(log_path).read_text().splitlines():
        if line.strip():
            events.append(json.loads(line))
    
    # Aggregate by component and status
    component_stats = defaultdict(lambda: Counter())
    for event in events:
        component = event.get("component", "unknown")
        status = event.get("status", "unknown")
        component_stats[component][status] += 1
    
    # Calculate success rates
    report = {}
    for component, stats in component_stats.items():
        total = sum(stats.values())
        success = stats.get("SUCCESS", 0)
        report[component] = {
            "total_operations": total,
            "success_rate": success / total if total > 0 else 0,
            "failure_count": stats.get("FAILED", 0)
        }
    
    return report
```

---

## 6. Telemetry Validator

### Purpose
Real-time validation of emitted telemetry to ensure schema compliance and quality.

### Validation Rules
**Schema Compliance:**
- Required fields present
- Correct data types
- Valid enum values

**Logical Consistency:**
- Timestamps in order
- Phase sequences valid
- Status transitions valid

**Quality Standards:**
- Error messages are actionable
- Metadata is relevant
- No sensitive data leaked

### Validation Gates
```python
def validate_telemetry(event):
    issues = []
    
    # Required fields
    required = ["timestamp", "event_type", "component", "status"]
    for field in required:
        if field not in event:
            issues.append(f"Missing required field: {field}")
    
    # Valid status
    valid_statuses = ["SUCCESS", "PARTIAL", "FAILED", "IN_PROGRESS"]
    if event.get("status") not in valid_statuses:
        issues.append(f"Invalid status: {event.get('status')}")
    
    # Quality gate
    if issues:
        return {"valid": False, "issues": issues, "gate": "BLOCK"}
    else:
        return {"valid": True, "gate": "PASS"}
```

---

## 7. Integration Points

### With Command Authoring
Each pipeline phase emits standardized telemetry with phase handoff data.

### With Lists
List operations log telemetry for CRUD operations, validation, and health checks.

### With Timeline
Timeline additions can be logged as telemetry events for audit trail.

### With Docgen
Documentation generation emits telemetry on processing time, item counts, validation results.

---

## 8. Analytics & Reporting

### Key Metrics
**Operational:**
- Operations per hour/day
- Success/failure rates
- Average duration by operation
- Error frequency by type

**Quality:**
- Quality score trends
- Validation failure rates
- Schema compliance percentage

**Performance:**
- P50, P95, P99 latencies
- Resource utilization
- Bottleneck identification

### Example Reports
**Daily Summary:**
- Total operations: 1,234
- Success rate: 98.5%
- Top errors: [ValidationError: 8, TimeoutError: 4]
- Slowest operations: [docgen: 2.3s, command-author: 5.1s]

**Trend Analysis:**
- Success rate: ▲ 2.1% vs last week
- Average duration: ▼ 150ms vs last week
- Error rate: ▼ 0.5% vs last week

---

## 9. Privacy & Security

### Data Sanitization
**Always sanitize before logging:**
- Remove credentials, tokens, API keys
- Truncate large inputs/outputs
- Hash PII (emails, names)
- Redact sensitive paths

### Storage Security
- Telemetry logs: read-only after write
- Rotation and cleanup policies
- Access control on analytics
- No telemetry in git repositories

---

## 10. Operational Considerations

### Performance Impact
- JSONL append: <1ms overhead
- Validation (if enabled): <5ms overhead
- Collector (batch): runs offline

### Storage Requirements
- Typical: 1-10 MB/day per component
- Retention: 90 days = ~1GB max
- Rotation: automatic, configurable

### Error Handling
**Telemetry emission failures:**
- Never block main operation
- Log to stderr
- Fall back to no-op

---

## 11. Example Implementation

### Telemetry Emitter
```python
#!/usr/bin/env python3
import json
from datetime import datetime, timezone
from pathlib import Path

class TelemetryEmitter:
    def __init__(self, log_path, component_name):
        self.log_path = Path(log_path)
        self.component = component_name
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
    
    def emit(self, event_type, status, **kwargs):
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "component": self.component,
            "status": status,
            **kwargs
        }
        
        try:
            with self.log_path.open('a') as f:
                f.write(json.dumps(event) + '\n')
        except Exception as e:
            # Never block on telemetry failure
            print(f"Telemetry emit failed: {e}", file=sys.stderr)
    
    def operation(self, operation_name):
        """Context manager for operation telemetry"""
        return OperationTelemetry(self, operation_name)

class OperationTelemetry:
    def __init__(self, emitter, operation_name):
        self.emitter = emitter
        self.operation = operation_name
        self.start = None
    
    def __enter__(self):
        self.start = datetime.now(timezone.utc)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now(timezone.utc) - self.start).total_seconds() * 1000
        status = "FAILED" if exc_type else "SUCCESS"
        
        self.emitter.emit(
            event_type="operation",
            status=status,
            operation=self.operation,
            duration_ms=duration,
            error=str(exc_val) if exc_val else None
        )

# Usage
telemetry = TelemetryEmitter("/var/log/n5/telemetry.jsonl", "lists-add")

with telemetry.operation("add_item"):
    # Do work
    pass

# Manual emission
telemetry.emit(
    event_type="metric",
    status="SUCCESS",
    metric_name="items_processed",
    metric_value=42
)
```

---

## 12. Testing Strategy

### Unit Tests
- Schema validation
- Sanitization logic
- Aggregation calculations
- Quality gate evaluation

### Integration Tests
- End-to-end telemetry emission
- Collector processing
- Alert triggering
- Storage rotation

### Load Tests
- High-frequency emission
- Large log file processing
- Collector performance

---

## Implementation Checklist

- [ ] Define telemetry schemas
- [ ] Implement JSONL emitter
- [ ] Build telemetry validator (optional)
- [ ] Create quality gate evaluator
- [ ] Implement telemetry collector
- [ ] Add sanitization logic
- [ ] Create analytics reports
- [ ] Set up storage rotation
- [ ] Write integration hooks for components
- [ ] Add unit tests
- [ ] Document custom event types
- [ ] Create example dashboards (optional)

---

*Export specification format v1.0*
