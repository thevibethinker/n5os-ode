---
description: 'Orchestrates the full Inbox processing workflow: analyze files, route
tool: true
  high-confidence items, generate review document for human oversight.'
tags: []
---
# inbox-process

**Category:** Automation  
**Version:** 1.0.0  
**Created:** 2025-10-27

---

## Purpose

Orchestrates the full Inbox processing workflow: analyze files, route high-confidence items, generate review document for human oversight.

---

## Prerequisites

- Inbox directory exists: `/home/workspace/Inbox/`
- Config exists: `file 'N5/config/routing_config.json'`
- Analysis script: `file 'N5/scripts/inbox_analyzer.py'`
- Router script: `file 'N5/scripts/inbox_router.py'`
- Review generator: `file 'N5/scripts/inbox_review_generator.py'`

---

## Execution

**Full workflow:**
```bash
# Step 1: Analyze all files in Inbox
python3 /home/workspace/N5/scripts/inbox_analyzer.py

# Step 2: Route high-confidence files (≥85%)
python3 /home/workspace/N5/scripts/inbox_router.py

# Step 3: Generate review document
python3 /home/workspace/N5/scripts/inbox_review_generator.py
```

**Dry-run mode (safe preview):**
```bash
python3 /home/workspace/N5/scripts/inbox_analyzer.py --dry-run
python3 /home/workspace/N5/scripts/inbox_router.py --dry-run
python3 /home/workspace/N5/scripts/inbox_review_generator.py --dry-run
```

---

## Workflow Steps

### Step 1: Analyze Files

**Script:** `inbox_analyzer.py`

- Scans all files in Inbox/
- Extracts metadata (size, type, modified date)
- Generates preview of content
- Calls LLM with analysis prompt
- Determines routing action based on confidence:
  - **≥85%:** Auto-route (high confidence)
  - **60-84%:** Suggest (medium confidence)
  - **<60%:** Manual only (low confidence)
- Logs results to `N5/logs/.inbox_analysis.jsonl`

### Step 2: Route High-Confidence Files

**Script:** `inbox_router.py`

- Reads analysis log
- Filters for `auto_route` action (confidence ≥85%)
- Validates destinations against whitelist
- Moves files to suggested destinations
- Updates analysis log with routing timestamp
- Logs all moves

### Step 3: Generate Review Document

**Script:** `inbox_review_generator.py`

- Reads unrouted analyses
- Groups by action type
- Checks for TTL violations (>14 days in Inbox)
- Generates `Inbox/REVIEW.md` with:
  - Summary statistics
  - TTL warnings
  - Auto-routed files list
  - Suggested routings (needs human decision)
  - Manual review items (low confidence)
  - Usage instructions

---

## Success Criteria

- All Inbox files analyzed
- High-confidence files (≥85%) automatically routed
- Medium/low confidence files flagged in REVIEW.md
- No invalid destinations used
- All operations logged
- Review document generated

---

## Error Handling

- **Analysis fails:** Logs error, continues with remaining files
- **Invalid destination:** Skips routing, logs error
- **File missing:** Warns and skips
- **LLM unavailable:** Falls back to heuristics (placeholder implementation)

---

## Configuration

**File:** `N5/config/routing_config.json`

**Key settings:**
- `confidence_thresholds.auto_route`: 0.85 (85% minimum for auto-routing)
- `confidence_thresholds.suggest`: 0.60 (60-84% for suggestions)
- `inbox_ttl_days`: 14 (alert if file older than 14 days)
- `valid_destinations`: Whitelist of allowed paths
- `analysis_model`: "gpt-5" (LLM model for analysis)

---

## Output Files

**Analysis log:** `N5/logs/.inbox_analysis.jsonl`
- One entry per file analyzed
- Includes destination, confidence, reasoning, action

**Review document:** `Inbox/REVIEW.md`
- Human-readable summary
- Grouped by confidence level
- TTL warnings
- Usage instructions

---

## Integration

**Part of clearinghouse workflow:**
1. **cleanup-root** → Moves files from root to Inbox/
2. **inbox-process** (this command) → Analyzes and routes
3. Human reviews `Inbox/REVIEW.md` and handles edge cases

**Scheduled:** Weekly on Sunday at 8pm ET

---

## Monitoring

**Health checks:**
- Inbox item count (alert if >50)
- TTL violations (alert if any >14 days)
- Routing accuracy (target: >95% correct)
- Error rate (target: <5%)

**Weekly review:** Check `Inbox/REVIEW.md` for items needing manual attention

---

## Related

- `file 'N5/commands/cleanup-root.md'` - Move root items to Inbox
- `file 'N5/commands/inbox-review.md'` - Generate review only
- `file 'N5/config/routing_config.json'` - Configuration
- `file 'Knowledge/architectural/planning_prompt.md'` - Design philosophy
