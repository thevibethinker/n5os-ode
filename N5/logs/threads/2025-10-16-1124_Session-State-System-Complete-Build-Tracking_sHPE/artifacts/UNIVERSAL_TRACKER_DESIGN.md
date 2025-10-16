# Universal Tracker Architecture
**Date:** 2025-10-16  
**Context:** Generalized conversation management system

---

## Core Concept

**Every conversation has SESSION_STATE.md** tracking what matters for quality conversation:
- Type, focus, progress
- Insights, decisions, questions
- Outputs, relationships
- Quality metrics

**Trackers filter and display** relevant subsets:
- Build Tracker → type=build, status=active
- Research Tracker → type=research, active last 7 days
- Discussion Tracker → type=discussion, tag=strategy
- All Activity Tracker → everything, sorted by recency

---

## How It Works

### **1. Auto-Initialize SESSION_STATE.md**

**Option A: Hard-coded rule** (V's suggestion)
Add to user_rules:
```
CONDITION: On conversation start -> RULE: 
Create SESSION_STATE.md in conversation workspace
```

**Option B: Command trigger**
First message to any conversation:
```
> Hi, I want to...
< Creating session state... [auto-generated]
< Ready! What would you like to work on?
```

**Option C: Lazy init**
First time tracker scans conversation without state file → creates it

**Recommendation:** Option A (hard-coded rule) - most reliable, zero friction

---

### **2. Continuous Updates**

**Auto-update triggers:**
- File created/modified → Update "Outputs & Artifacts"
- User says "I've decided..." → Prompt to log in "Decisions Made"
- Conversation exceeds 30 min → Prompt quality check
- User says "done" or "complete" → Update status

**Manual updates:**
- `update session state` - Refresh all fields
- `mark insight: <text>` - Add to insights
- `set status: <status>` - Change conversation status

---

### **3. Tracker Filtering**

**Base tracker** (`refresh tracker`):
Shows all conversations with recent activity

**Filtered trackers:**
- `build tracker` → type=build, status ≠ complete
- `research tracker` → type=research, status=active
- `discussion tracker` → type=discussion
- `active work` → status=active, any type
- `blocked work` → has blockers
- `needs attention` → quality indicators flagged

**Filter syntax:**
```bash
python3 N5/scripts/tracker.py refresh \
  --filter-type build,research \
  --filter-status active,paused \
  --filter-tags high-priority \
  --max-age 7d
```

---

## Tracker Views

### **Build Tracker View**
```markdown
# Build Activity Tracker

## Active Builds (3)

🔵 con_ABC - Auth System Refactor
   Focus: JWT implementation
   Progress: 70% | Tests: passing | Blocked: No
   Branch: worker-a-auth | 3 commits staged
   Quality: clarity=high, completeness=70%
   
🔵 con_XYZ - Schema Design
   Focus: User model updates
   Progress: 50% | Tests: N/A | Blocked: No
   Files: N5/schemas/user.schema.json
   Quality: clarity=med, completeness=50%

🟡 con_DEF - API Endpoints
   Focus: User CRUD endpoints
   Progress: 30% | Tests: failing | Blocked: YES
   Blocker: Waiting for schema from con_XYZ
   Quality: clarity=high, completeness=30%

## Recently Completed (2)
✅ con_GHI - Build Companion System (completed 1h ago)
✅ con_JKL - Distributed Architecture Design (completed 30m ago)
```

### **Research Tracker View**
```markdown
# Research Activity Tracker

## Active Research (2)

📚 con_MNO - AI Orchestration Patterns
   Focus: Literature review on multi-agent systems
   Sources: 15 reviewed, 3 key papers identified
   Synthesis: 60% complete
   Quality: depth=moderate, diversity=broad
   Insights: 7 key insights logged
   
📚 con_PQR - Zo Architecture Analysis  
   Focus: Understanding distributed conversation model
   Sources: 8 docs reviewed
   Synthesis: 30% complete
   Questions: 4 open questions
   Quality: depth=deep, diversity=narrow

## Synthesis Ready (1)
✅ con_STU - Career coaching methodologies (synthesis 90%)
```

### **Discussion Tracker View**
```markdown
# Discussion Activity Tracker

## Active Discussions (2)

💬 con_VWX - Strategy: Careerspan GTM
   Topic: Hiring manager outreach approach
   Convergence: 70% consensus
   Decisions: 3 made, 2 pending
   Open questions: 2
   Quality: clarity=high, depth=moderate
   
💬 con_YZA - Design: N5 Refactor Approach
   Topic: Architectural patterns for system rebuild
   Convergence: 50% consensus
   Arguments: thesis + 2 counter explored
   Quality: clarity=med, depth=deep

## Resolved (1)
✅ con_BCD - Decision: Build tracker architecture (concluded 2h ago)
```

---

## Use Cases

### **For Technical Work**
V opens Build Tracker conversation:
- Sees all active builds
- Notices con_DEF blocked
- Opens Orchestrator conversation
- Assigns unblocking work
- Returns to Build Tracker to monitor

### **For Research**
V opens Research Tracker:
- Sees synthesis at 60%
- Opens that conversation
- Completes synthesis
- Marks complete
- Research Tracker shows it in "Ready" section

### **For Strategy Discussions**
V opens Discussion Tracker:
- Sees 2 active strategy conversations
- Notices one at 70% consensus
- Opens it to finalize
- Makes final decision
- Updates state to complete

### **For Unified View**
V opens All Activity Tracker:
- Sees builds, research, discussions
- Identifies highest priority (tags, status)
- Decides what to focus on next
- Opens relevant conversation

---

## Integration with Existing System

### **Commands**
```bash
# Universal
refresh tracker [--filter-type X] [--filter-status Y]
update session state
mark insight: <text>
mark decision: <text>
set status: active|paused|complete

# Build-specific (already exist)
track task <name>
working on <task>
done with <task>

# Research-specific (new)
add source: <title> | <key points>
mark synthesis progress: <percent>
add open question: <question>

# Discussion-specific (new)
log argument: <thesis>
mark convergence: <percent>
add decision: <choice> | <rationale>
```

### **File Structure**
```
/home/workspace/
├── N5/
│   ├── scripts/
│   │   ├── tracker.py          # Universal tracker
│   │   ├── build_tracker.py    # Build-specific (alias to tracker)
│   │   └── orchestrator.py     # Future
│   ├── config/
│   │   └── commands.jsonl      # All commands
│   └── .state/
│       ├── tracker_active.json # Which tracker conversation
│       └── conversation_registry.json # All conversations index

/home/.z/workspaces/con_*/
└── SESSION_STATE.md            # Every conversation has one
```

---

## Implementation Plan

### **Phase 1.5: Universal Session State**
1. Create SESSION_STATE.md template
2. Add auto-init (hard-coded rule or lazy init)
3. Add update commands
4. Test across conversation types

### **Phase 2: Filtered Trackers**
1. Update tracker.py to support filters
2. Create tracker view templates (build, research, discussion)
3. Add filter commands
4. Test multi-tracker workflow

### **Phase 3: Advanced Features**
1. Cross-conversation synthesis
2. Automatic relationship detection
3. Quality-based prioritization
4. ML-based conversation classification

---

## Benefits

### **For V**
- One system for all conversation types
- Clear visibility into all active work
- Quality tracking (not just task tracking)
- Flexible filtering for different contexts
- Unified approach to conversation management

### **For AI**
- Explicit conversation state → better context
- Quality metrics → self-improvement
- Cross-conversation awareness → better suggestions
- Relationship tracking → fewer redundant discussions

### **For System**
- Scalable (100s of conversations)
- Type-agnostic (works for any conversation)
- Extensible (new types, new filters, new metrics)
- Composable (trackers can aggregate other trackers)

---

## Example: Multi-Tracker Workflow

**Monday morning:**
1. V opens "All Activity Tracker"
2. Sees: 3 builds active, 2 research ongoing, 1 strategy discussion
3. Filters to high-priority: 1 build, 1 discussion
4. Opens build tracker → delegates to orchestrator
5. Opens discussion tracker → makes final decision
6. Returns to all activity → sees progress updates
7. Closes 2 items, both move to "completed"

**Result:** Single unified system manages technical and intellectual work equally well.

---

## Next Step

Build Phase 1.5:
1. Implement universal SESSION_STATE.md
2. Add auto-init mechanism
3. Update tracker.py for filtering
4. Test with this conversation (mark as tracker)

**Ready to implement?**
