---
description: 'Command: lists-health-check'
tool: true
tags:
- lists
- monitoring
- health
- phase3
---
# `lists-health-check`

**Version:** 1.0.0

**Summary:** Check list system health and detect Phase 3 implementation triggers

**Workflow:** lists

**Tags:** lists, monitoring, health, phase3

## Description

## Inputs
(None)

Monitors the N5 lists system health and automatically detects conditions that warrant Phase 3 implementation:

- **List Count Monitoring:** Tracks total list count against thresholds
  - Warning: 15+ lists (approaching threshold)
  - Critical: 20+ lists (Phase 3.1 recommended)
  - Urgent: 30+ lists (Phase 3 strongly recommended)

- **Similarity Detection:** Identifies lists with high overlap that may benefit from merging
  - Analyzes title keyword overlap
  - Compares tag similarity
  - Reports potential merge candidates

- **Automatic Alerting:** Creates system-upgrade alerts when conditions are met
  - Only creates alert once per trigger event
  - Links to implementation documentation
  - Prioritized by urgency level

## Outputs

- `report` : text — Health status report with recommendations
- `exit_code` : integer — 0 = healthy, 1 = warning, 2 = action recommended

## Usage

### Manual Check
```bash
python N5/scripts/n5_lists_health_check.py
```

### In Automation
```bash
# Run health check and act on exit code
if python N5/scripts/n5_lists_health_check.py; then
    echo "All good"
elif [ $? -eq 1 ]; then
    echo "Warning level - monitoring"
elif [ $? -eq 2 ]; then
    echo "Action recommended - Phase 3"
fi
```

## Examples

### Healthy Status
```
Current Status:
   List Count: 4
   Status: OK
   Urgency: NONE
   Phase 3 Recommended: NO

✅ No action needed. List system health is good.
```

### Warning Status (15+ lists)
```
Current Status:
   List Count: 18
   Status: WARNING
   Urgency: LOW
   Phase 3 Recommended: NO

ℹ️ INFO: 18 lists detected. Approaching Phase 3 threshold. Monitor list growth.
```

### Critical Status (20+ lists)
```
Current Status:
   List Count: 22
   Status: CRITICAL
   Urgency: MEDIUM
   Phase 3 Recommended: YES

⚠️ WARNING: 22 lists detected. Consider implementing Phase 3.1 (Similarity Scanner).

✅ Phase 3 alert added to system-upgrades list
```

### Similar Lists Detected
```
⚠️ MERGE OPPORTUNITY: 2 pairs of similar lists detected.

🔍 Similar Lists Detected:
   • project-ideas ↔ feature-ideas (75% similar)
   • reading-list ↔ articles-to-read (68% similar)
```

## Side Effects

- May append to: `Lists/system-upgrades.jsonl` (when Phase 3 trigger detected)
- Does not modify any list data
- Read-only for all list files

## Related Commands

- `lists-add` — Add items to lists
- `lists-find` — Search lists
- `n5_lists_monitor.py` — Check list data integrity

## Thresholds Configuration

Thresholds are defined in `n5_lists_health_check.py`:

```python
THRESHOLDS = {
    "list_count_warning": 15,      # Start paying attention
    "list_count_critical": 20,     # Phase 3.1 recommended
    "list_count_urgent": 30,       # Phase 3 strongly recommended
    "similar_list_threshold": 0.6  # 60% title/tag overlap
}
```

Adjust these values based on your usage patterns.

## Phase 3 Reference

When Phase 3 is triggered, refer to:
- **Implementation Plan:** `con_iCXGjocGU0NRU0B3/n5_lists_improvement_plan.md`
- **Status Report:** `con_pQh91lSEsCkaqLRz/list_system_implementation_status.md`

Phase 3 includes:
- **3.1:** List Similarity Detection & Merge Analyzer
- **3.2:** Semi-Automated List Merging Tool
- **3.3:** Enhanced Auto-Correction Engine

## Notes

- Health check is non-destructive and safe to run anytime
- Exit codes enable integration with automation workflows
- Alert deduplication prevents spam in system-upgrades
- Similarity detection uses simple keyword/tag overlap (no LLM required)

## Implementation

**Script:** `N5/scripts/n5_lists_health_check.py`

**Dependencies:** None (uses only Python stdlib)

**Runtime:** <1 second for typical list counts

## Incantum Triggers

**Primary:** `incantum: check list system health`  
**Aliases:**
- `incantum: assess list maintenance`
- `incantum: list health status`
- `incantum: check lists for phase 3`

**Magical Variations:**
- `incantum: reveal the health of my list realm`
- `incantum: conjure list system diagnostics`

These natural language triggers can be used in conversation instead of the shell command.
