# Vibe Debugger Design Summary

**Date:** 2025-10-26  
**Conversation:** con_SyBlpCrnA0ZGVg8a  
**Objective:** Design a specialized persona for thorough debugging and verification

---

## What We Built

**Vibe Debugger** — A specialized Zo persona for systematic verification, debugging, and quality assurance.

**Location:** `file 'Knowledge/personas/vibe_debugger.md'`  
**Documentation:** `file 'Knowledge/personas/README.md'`

---

## Key Design Decisions

### 1. **Two Operating Modes**

**Mode A: End-of-Conversation Debug**
- Context: Long conversation, token budget constrained
- Approach: Minimal context loading, targeted verification
- Use case: "We just built X, verify it works"

**Mode B: Fresh-Thread Debug**
- Context: New conversation, debugging old system
- Approach: Full context reconstruction from registry
- Use case: "Debug the meeting digest system from last week"

### 2. **Systematic Methodology (5 Phases)**

1. **Understand:** Context reconstruction
2. **Verify Structure:** Static analysis against principles
3. **Verify Behavior:** Dynamic testing (happy path + edges + errors)
4. **Verify Integration:** System-wide testing
5. **Document Findings:** Structured debug report

### 3. **Token Efficiency by Design**

**Rule-of-Two (P0, P8):** Never load more than 2 implementation files at once

**Selective Principle Loading:** Load only relevant modules:
- Safety issues? → `safety.md`
- Quality issues? → `quality.md`
- Design issues? → `design.md`

**Lazy File Reading:** Start with listings, load files only when needed

**Incremental Verification:** Test one layer at a time

### 4. **Context Reconstruction via Registry**

**Conversation Registry Integration:**
```sql
SELECT id, title, type, focus, objective, workspace_path, aar_path 
FROM conversations 
WHERE tags LIKE '%[tag]%' OR focus LIKE '%[keyword]%'
```

**Artifact Discovery:**
- Conversation workspace: `/home/.z/workspaces/[convo_id]/`
- Thread exports (AARs): `/home/workspace/N5/logs/threads/`
- Final locations: User workspace

**Reverse Engineering:** Use Worker/Orchestrator pattern to understand system architecture

### 5. **Structured Debug Reports**

**Standard format:**
- Executive summary (status, critical issues, warnings)
- What was built (components, objectives)
- Findings (critical, warnings, passes)
- Principle compliance matrix
- Test results (happy path, edge cases, errors, integration)
- Recommendations (prioritized)
- Verification checklist

### 6. **Principle-Driven Verification**

**Checks against:**
- SSOT (P2)
- Safety (P5, P7, P11, P19)
- Quality (P15, P16, P18, P21)
- Design (P8, P20, P22)
- Operations (P12, P17)

### 7. **Collaboration with Vibe Builder**

**Clear division:**
- **Vibe Builder:** Builds systems (optimistic engineer)
- **Vibe Debugger:** Verifies systems (skeptical tester)

**Handoff pattern:**
1. Builder: "System complete"
2. V invokes Debugger
3. Debugger: Test → Report
4. If issues: Debugger fixes (minor) or hands back to Builder (major)

---

## Design Alignment with Requirements

### ✅ **Target-ish situations with functionality issues**
- Mode A: Debug at end of build conversation
- Systematic testing catches functionality gaps

### ✅ **Double-check and thoroughly test built systems**
- 5-phase methodology (structure → behavior → integration)
- Principle compliance matrix
- Comprehensive test categories

### ✅ **Built for diligence**
- Skeptical mindset
- "Verify, don't assume"
- Critical anti-patterns (false positives, testing theater)

### ✅ **Memory/token optimal (end of long conversation)**
- Rule-of-Two: Max 2 files loaded
- Selective principle loading
- Lazy file reading
- Incremental verification

### ✅ **Reference old conversations in new thread**
- Mode B: Fresh-thread debugging
- Query conversation registry
- Discover artifacts from AAR/workspace
- Reverse-engineer via Worker/Orchestrator

### ✅ **Maximal alignment with system and architectural principles**
- Pre-flight loads all relevant principle modules
- Verification explicitly checks principle compliance
- Structured reports map findings to principles
- Token efficiency follows P0, P8, P20

---

## Zero-Touch Integration

**Philosophy alignment:**
- **ZT1 (Context + State):** Debugger verifies state management (P23)
- **ZT2 (Flow vs. Pools):** Tests information flow design (P24)
- **ZT4 (Maintenance > Organization):** Builds maintenance culture through verification
- **ZT7 (AIR Pattern):** Ensures Assess-Intervene-Review working correctly
- **ZT8 (Minimal Touch):** Verifies Human-in-Loop design

**Principle embodiment:**
- Uses P8 (Minimal Context) in its own operation
- Follows P20 (Modular Design) as a loadable persona
- Enforces P15 (Complete Before Claiming) through thorough testing
- Checks P18 (State Verification) in every system it debugs

---

## Implementation Details

**File structure:**
```
Knowledge/
└── personas/
    ├── README.md          # Persona index and comparison
    └── vibe_debugger.md   # Full persona specification
```

**Key sections in persona doc:**
- Core Identity & Pre-Flight (mandatory loading)
- Two Operating Modes (A vs B)
- Systematic Debugging Methodology (5 phases)
- Critical Anti-Patterns
- Integration with N5 System (registry queries, artifact discovery)
- Token Efficiency Strategies
- Self-Check Before Reporting
- Example Invocations

**Documentation:**
- Persona comparison table (Builder vs Debugger)
- Usage patterns (Sequential, Independent, Continuous)
- Design philosophy (why personas exist)

---

## Example Invocations

**Mode A (end of conversation):**
> "Load Vibe Debugger. We just built a reflection ingestion pipeline. Verify it works correctly and follows principles. Focus on error handling and state verification."

**Mode B (fresh thread):**
> "Load Vibe Debugger. Find the conversation where we built the meeting digest system (look for 'digest' in focus/tags from Oct 20-25). Reconstruct what was built and thoroughly test it against production data."

**Targeted verification:**
> "Load Vibe Debugger. Check if `N5/scripts/cleanup_manager.py` follows safety principles (P5, P7, P19). Test dry-run mode and error paths."

---

## Next Steps (If Needed)

**Persona is complete and ready to use**, but potential enhancements:

1. **Create automated testing scripts** that Debugger can invoke
2. **Build debug report templates** for common system types
3. **Add metrics tracking** (how many issues found per principle over time)
4. **Create principle violation library** (common patterns to watch for)
5. **Build automated principle compliance checker** (static analysis tool)

---

## Questions Answered

**Q: Do I need a persona that can do that?**  
**A:** Yes, and we built it. The persona packages the debugging methodology, principle knowledge, and token-efficient strategies into a loadable module.

**Q: How does it leverage worker/orchestrator model?**  
**A:** Mode B includes "Reverse Engineer via Worker/Orchestrator Pattern" — it looks at individual components (worker view) and how they integrate (orchestrator view) to understand system architecture.

**Q: How does it reference old conversations?**  
**A:** Via conversation registry queries:
```sql
SELECT id, focus, objective, workspace_path, aar_path 
FROM conversations 
WHERE focus LIKE '%keyword%'
```
Then discovers artifacts from workspace paths and AAR locations.

**Q: How is it token-optimal?**  
**A:** 
- Rule-of-Two: Max 2 files loaded simultaneously
- Selective principle module loading (not all at once)
- Lazy file reading (listings first, content only when needed)
- Incremental verification (one layer at a time)

**Q: How does it align with architectural principles?**  
**A:**
- Pre-flight loads principle modules
- 5-phase methodology checks principle compliance
- Structured reports map findings to specific principles (P2, P5, P15, etc.)
- Persona itself follows P8, P20 (modular, minimal context)

---

## Deliverables

✅ **Vibe Debugger Persona** (`Knowledge/personas/vibe_debugger.md`)  
✅ **Personas Index** (`Knowledge/personas/README.md`)  
✅ **Design Summary** (this document)

**Status:** Complete and ready to use

---

*Created by: Vibe Builder persona*  
*Version: 1.0*  
*Date: 2025-10-26*
