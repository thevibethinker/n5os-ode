---
title: "Worker: Meeting System Cleanup"
description: "Execute Phase 0-6 of pre-build checklist v2.0 for meeting system consolidation and cleanup. Follow rigorously, report back to orchestrator."
tags:
  - worker
  - cleanup
  - meeting-system
  - execution
tool: true
version: 1.0
created: 2025-11-15
---

# Worker Thread: Meeting System Cleanup & Consolidation

**Orchestrator Thread**: con_z6F09rhM12C9kJDZ  
**Pre-Build Protocol**: v2.0 (file 'Prompts/pre-build-checklist.prompt.md')  
**Status**: 🚀 READY FOR EXECUTION

---

## ⚠️ CRITICAL: FOLLOW v2.0 PROTOCOL RIGOROUSLY

**You MUST complete ALL phases before ANY building or cleanup:**

### **Execute in Order:**

1. **PHASE 0**: Load architectural DNA + declare context
2. **PHASE 1**: Grok the problem (understand BEFORE searching)
3. **PHASE 2**: Comprehensive discovery (multi-method)
4. **PHASE 3**: Generate structured PRD with self-healing
5. **PHASE 4**: Calculate rubric score (must be ≥8.0)
6. **PHASE 5**: Get explicit approval from orchestrator
7. **PHASE 6**: Execute cleanup (ONLY after approval)

---

## 🎯 SCOPE: Meeting System Cleanup

**Based on audit findings** (file '/home/.z/workspaces/con_z6F09rhM12C9kJDZ/MEETING_SYSTEM_AUDIT.md'):

**Phase 6 Execution Tasks** (AFTER approval):

1. **Delete empty databases** (7 files, ~0KB each):
   - `/home/workspace/N5/data/meetings_registry.db`
   - `/home/workspace/N5/registry/meeting_processing_registry.db`
   - `/home/workspace/N5/data/meeting_pipeline/meeting_queue.db`
   - Plus 4 others from audit

2. **Consolidate duplicate detection scripts** (5 scripts → 1):
   - Analyze: `find_fuzzy_duplicates.py`, `duplicate_detector.py`, etc.
   - Create unified: `/home/workspace/N5/scripts/meeting_duplicate_detector.py`
   - Preserve best algorithm from each

3. **Fix metadata generation bug**:
   - Transcript processor creates `.md` files with wrong folder paths
   - Update `transcript_processor_v4.py` metadata generation
   - Backfill correct metadata for 12 affected meetings

4. **Document sync strategy**:
   - Registry (JSONL) ↔ Pipeline DB sync
   - Registry → Filesystem sync
   - On-conflict resolution rules

---

## 📊 DELIVERABLES (Report to Orchestrator)

**After EACH phase, report findings back to con_z6F09rhM12C9kJDZ**:

### Phase 0-3 Report:
- Problem statement
- Discovery summary (what you found)
- Full PRD document (paste it)
- Rubric scores (all 6 dimensions)
- Total score calculation

### Phase 4 Report:
- **Total Score: X.X/10**
- If <8.0: What needs improvement? (iterate)
- If ≥8.0: Ready for approval

### Phase 5 Report:
- **Orchestrator approval received**: [YES/NO]
- Approval timestamp: 
- Any conditions or modifications:

### Phase 6 Report:
- **Cleanup executed**: [date/time]
- **Items completed**: [list]
- **Validation results**: [how you verified]

---

## 🛑 HARD STOPS (Checklist)

**STOP and return to orchestrator IMMEDIATELY if**:

- ❌ Discovery reveals scope is larger than audit suggested
- ❌ Can't achieve rubric score ≥8.0 after 2 iterations
- ❌ PRD reveals need for architectural changes (not just cleanup)
- ❌ Find .n5protected files in cleanup paths
- ❌ Sync strategies are more complex than expected
- ❌ Any destructive operation affects >10 files (show dry-run first)

---

## ✅ SUCCESS CRITERIA

**Minimum success** (8.0/10 rubric):
- Empty databases deleted
- Duplicate scripts consolidated
- Metadata bug fixed + backfilled
- Sync strategy documented

**Excellent success** (9.0/10 rubric):
- Above + performance improved (10x faster processing)
- Above + one self-healing mechanism implemented (health check, auto-sync, etc.)
- Above + comprehensive tests written

**Exceptional success** (10/10 rubric):
- Above + architectural simplification (remove 1+ overlapping systems)
- Above + monitoring/alerting implemented

---

**Begin with Phase 0. Execute sequentially. Report back after Phase 3 for approval.**

**Orchestrator is watching: con_z6F09rhM12C9kJDZ**

---

*Worker spawn: 2025-11-15 03:53 ET*

