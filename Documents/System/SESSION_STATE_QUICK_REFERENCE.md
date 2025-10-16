# Session State System - Quick Reference

**One-page cheat sheet for common operations**

---

## Start New Conversation (Auto-Init)

Let Zo auto-classify and initialize:
```bash
python3 N5/scripts/session_state_manager.py init \
  --convo-id con_XXX \
  --message "YOUR FIRST MESSAGE HERE" \
  --load-system
```

Override with specific type:
```bash
python3 N5/scripts/session_state_manager.py init \
  --convo-id con_XXX \
  --type build \
  --mode implementation
```

---

## Distributed Build Flow

### 1. Start Orchestrator
```bash
# In orchestrator conversation
python3 N5/scripts/session_state_manager.py init \
  --convo-id con_ORCH \
  --type build \
  --mode orchestration
```

### 2. Assign Workers
```bash
python3 N5/scripts/orchestrator.py assign \
  --worker con_WORKER_1 \
  --task "Implement authentication module"

python3 N5/scripts/orchestrator.py assign \
  --worker con_WORKER_2 \
  --task "Implement database layer"
```

### 3. Monitor Progress
```bash
# Real-time dashboard
python3 N5/scripts/build_tracker.py --orchestrator con_ORCH --watch

# Single check
python3 N5/scripts/build_tracker.py --orchestrator con_ORCH
```

### 4. Quality Gates (When Worker Claims Complete)

**Run integration tests:**
```bash
python3 N5/scripts/integration_test_runner.py --worker-convo con_WORKER_1
```

**Check principle violations:**
```bash
python3 N5/scripts/principle_violation_detector.py --worker-convo con_WORKER_1
```

**Review reports:**
```bash
cat /home/.z/workspaces/con_WORKER_1/TEST_RESULTS.json
cat /home/.z/workspaces/con_WORKER_1/PRINCIPLE_VIOLATIONS.json
```

### 5. Visualize Dependencies
```bash
python3 N5/scripts/dependency_graph.py --orchestrator con_ORCH
# Creates: /home/.z/workspaces/con_ORCH/DEPENDENCY_GRAPH.d2
```

### 6. Approve & Merge
```bash
python3 N5/scripts/orchestrator.py review --worker con_WORKER_1
python3 N5/scripts/orchestrator.py approve --worker con_WORKER_1
```

---

## Common Commands

### Update Session State
```bash
python3 N5/scripts/session_state_manager.py update \
  --convo-id con_XXX \
  --field status \
  --value blocked
```

### Read Session State
```bash
python3 N5/scripts/session_state_manager.py read --convo-id con_XXX
```

### Send Message Between Conversations
```bash
python3 N5/scripts/message_queue.py send \
  --from con_ORCH \
  --to con_WORKER \
  --content "Need clarification on API design" \
  --type question
```

### Check Messages
```bash
python3 N5/scripts/message_queue.py check --convo-id con_WORKER
```

---

## Auto-Classification Examples

| User Message | Detected Type | Confidence |
|--------------|---------------|------------|
| "Build a REST API" | build | 1.0 |
| "Research JWT best practices" | research | 0.5 |
| "Create a roadmap for Q2" | planning | 0.67 |
| "What do you think about X?" | discussion | 0.5 |

---

## Test Framework Detection

**Auto-detected frameworks:**
- pytest (Python)
- bun test (Bun)
- jest (Node.js)
- go test (Go)
- cargo test (Rust)

**Usage:**
```bash
# Auto-detect and run
python3 N5/scripts/integration_test_runner.py --worker-convo con_XXX

# Specific test type
python3 N5/scripts/integration_test_runner.py \
  --worker-convo con_XXX \
  --test-type integration
```

---

## Principle Violations Detected

- **P15:** Claims complete but has open tasks
- **P16:** Invented API limits (e.g., "Gmail has 3-message limit")
- **P19:** Missing error handling (no try/except)

---

## File Locations

**Scripts:** file 'N5/scripts/'
- `session_state_manager.py` - State management
- `build_tracker.py` - Monitoring
- `orchestrator.py` - Coordination
- `message_queue.py` - Messaging
- `integration_test_runner.py` - Testing
- `dependency_graph.py` - Visualization
- `principle_violation_detector.py` - QA

**Docs:**
- file 'Documents/System/SESSION_STATE_SYSTEM.md' - Complete guide
- file 'Documents/System/SESSION_STATE_QUICK_REFERENCE.md' - This file

**Session States:** `/home/.z/workspaces/con_XXX/SESSION_STATE.md`

---

## Dry-Run Mode

All scripts support `--dry-run` to preview without executing:
```bash
python3 N5/scripts/integration_test_runner.py --worker-convo con_XXX --dry-run
python3 N5/scripts/dependency_graph.py --orchestrator con_ORCH --dry-run
python3 N5/scripts/principle_violation_detector.py --worker-convo con_XXX --dry-run
```

---

## Troubleshooting

**Issue:** SESSION_STATE.md not created  
**Fix:** Manually init: `python3 N5/scripts/session_state_manager.py init --convo-id con_XXX`

**Issue:** Tests not found  
**Fix:** Check discovery: `python3 N5/scripts/integration_test_runner.py --worker-convo con_XXX --dry-run`

**Issue:** Wrong classification  
**Fix:** Override: `--type build` instead of `--message`

---

## Quick Start: Your First Distributed Build

```bash
# 1. Orchestrator
python3 N5/scripts/session_state_manager.py init --convo-id con_ORCH --type build

# 2. Worker 1
python3 N5/scripts/orchestrator.py assign --worker con_W1 --task "Build feature X"

# 3. Worker completes work...

# 4. Quality check
python3 N5/scripts/integration_test_runner.py --worker-convo con_W1
python3 N5/scripts/principle_violation_detector.py --worker-convo con_W1

# 5. Review & approve
python3 N5/scripts/orchestrator.py approve --worker con_W1

# 6. Visualize
python3 N5/scripts/dependency_graph.py --orchestrator con_ORCH
```

---

*For complete documentation, see: file 'Documents/System/SESSION_STATE_SYSTEM.md'*

*Last Updated: 2025-10-16 06:16 EST*
