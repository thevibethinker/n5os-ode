---
created: 2026-01-30
last_edited: 2026-01-30
version: 1.0
type: build_plan
status: complete
---

# Plan: Port Conflict Detector

**Objective:** Build a runtime conflict detection system that monitors port allocations across services, zosites, and actual listeners, alerting V when conflicts are detected.

**Trigger:** Recurring port conflicts (most recently 8766, 8847) that the advisory-only registry system failed to prevent.

**Key Design Principle:** Simple over complex. Detect and alert, don't try to enforce at platform level.

---

## Open Questions

<!-- Surface unknowns HERE at the TOP. Resolve before proceeding. -->
- [x] Should this run as a scheduled agent or a long-running service? → **Scheduled agent** (simpler, no port needed)
- [x] What's the right polling interval? → **Every 10 minutes** (balance between responsiveness and noise)
- [x] Should it auto-resolve conflicts or just alert? → **Alert only** (V makes resolution decisions)

---

## Checklist

### Phase 1: Core Detection Script
- ☑ Create `N5/scripts/port_conflict_detector.py` with detection logic
- ☑ Implement three-way comparison: registry vs services API vs lsof
- ☑ Classify conflicts by severity (duplicate registration vs zombie vs drift)
- ☑ Test: Manual execution produces accurate conflict report

### Phase 2: Scheduled Agent + Alerting
- ☑ Create scheduled agent running every 10 minutes
- ☑ Implement SMS alerting for detected conflicts
- ☑ Add cooldown logic (don't spam same conflict repeatedly)
- ☑ Test: Intentionally create conflict, verify SMS alert received

---

## Phase 1: Core Detection Script

### Affected Files
- `N5/scripts/port_conflict_detector.py` - CREATE - Main detection script
- `N5/config/PORT_REGISTRY.md` - READ - Source of intended allocations

### Changes

**1.1 Detection Logic:**

The script will perform a three-way comparison:

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   PORT_REGISTRY.md  │    │  list_user_services │    │   lsof (runtime)    │
│   (intended state)  │    │   (registered)      │    │   (actual state)    │
└─────────┬───────────┘    └─────────┬───────────┘    └─────────┬───────────┘
          │                          │                          │
          └──────────────────────────┼──────────────────────────┘
                                     ▼
                          ┌─────────────────────┐
                          │  Conflict Detection │
                          │                     │
                          │  1. Duplicate ports │
                          │  2. Zombies         │
                          │  3. Registry drift  │
                          └─────────────────────┘
```

**Conflict Types:**
1. **DUPLICATE_REGISTRATION:** Two services registered on same port (highest severity)
2. **ZOMBIE_PORT:** Port in registry/services but nothing listening (medium)
3. **UNREGISTERED_LISTENER:** Something listening on a port not in registry (low)
4. **REGISTRY_DRIFT:** Service exists but not in registry (low)

**1.2 CLI Interface:**

```bash
# Check for conflicts
python3 N5/scripts/port_conflict_detector.py check

# Check and return exit code (0=clean, 1=conflicts)
python3 N5/scripts/port_conflict_detector.py check --exit-code

# JSON output for programmatic use
python3 N5/scripts/port_conflict_detector.py check --json
```

**1.3 Output Format:**

Human-readable:
```
=== PORT CONFLICT REPORT ===
Timestamp: 2026-01-30 12:45:00 ET

🔴 CRITICAL - Duplicate Registrations:
   Port 8847:
   - careerspan-webhook (svc_KbYAmjjz8QA)
   - careerspan-wh (svc_TArEMhXNEcI)
   
🟡 WARNING - Registry Drift:
   Port 50005: build-tracker registered but not in PORT_REGISTRY.md

✅ Ports scanned: 62
✅ Conflicts found: 2
```

### Unit Tests
- Create mock conflict scenario → Script detects and reports correctly
- Run on clean state → Script reports no conflicts
- JSON output is valid and parseable

---

## Phase 2: Scheduled Agent + Alerting

### Affected Files
- `N5/scripts/port_conflict_detector.py` - UPDATE - Add alerting integration
- `N5/data/port_conflict_state.json` - CREATE - Track alert cooldowns

### Changes

**2.1 Scheduled Agent:**

Create agent with:
- **Schedule:** Every 10 minutes (`FREQ=MINUTELY;INTERVAL=10`)
- **Instruction:** Run port conflict detector, SMS V if new conflicts found
- **Cooldown:** Don't re-alert for same conflict within 2 hours

**2.2 Alert Cooldown Logic:**

Store state in `N5/data/port_conflict_state.json`:
```json
{
  "last_check": "2026-01-30T17:45:00Z",
  "known_conflicts": {
    "8847": {
      "first_seen": "2026-01-30T17:35:00Z",
      "last_alerted": "2026-01-30T17:35:00Z",
      "type": "DUPLICATE_REGISTRATION"
    }
  }
}
```

Only alert if:
- Conflict is new (not in known_conflicts)
- OR last_alerted > 2 hours ago (recurring unresolved conflict)

**2.3 SMS Alert Format:**

```
🔴 Port Conflict Detected

Port 8847 has duplicate services:
- careerspan-webhook
- careerspan-wh

Fix: Delete one service or reassign port.
```

### Unit Tests
- Test cooldown logic prevents spam
- Test new conflict triggers SMS
- Test resolved conflict clears from state

---

## MECE Validation

This is a **single-worker build** (small scope, sequential phases). No multi-worker orchestration needed.

| Scope Item | Owner | Status |
|------------|-------|--------|
| `port_conflict_detector.py` | Single worker | ✓ |
| `port_conflict_state.json` | Single worker | ✓ |
| Scheduled agent | Single worker | ✓ |

---

## Success Criteria

1. **Detection accuracy:** Script correctly identifies all conflict types from test scenarios
2. **No false positives:** Clean system reports zero conflicts
3. **Alerting works:** Creating a test conflict results in SMS within 10 minutes
4. **Cooldown works:** Same conflict doesn't spam (only alerts every 2 hours)
5. **Exit code useful:** Can be used in CI/pre-service-registration checks

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Alert spam if many conflicts | Cooldown logic + batch reporting (one SMS per check, not per conflict) |
| lsof permission issues | Script runs as root in Zo, should have access |
| list_user_services API changes | Minimal dependency on API structure; degrade gracefully |

---

## Alternatives Considered

| Option | Description | Verdict |
|--------|-------------|---------|
| **A: Reactive Monitor (CHOSEN)** | Scheduled detection + SMS alerts | Simple, no platform changes, immediate value |
| **B: Pre-registration Hook** | Stricter rule enforcement | Still advisory, doesn't catch all paths |
| **C: Runtime Guardian Service** | Long-running interceptor | Over-engineered, complects with platform |

---

## Level Upper Review

*Not invoked for this build—scope is clear and simple.*

---

## Handoff

This build is ready for **single-worker execution**. No Pulse orchestration needed.

**Recommended approach:**
1. Route to Builder
2. Builder executes Phase 1 → Phase 2 sequentially
3. Create scheduled agent at end

**Alternative:** V can review this plan and approve before execution begins.
