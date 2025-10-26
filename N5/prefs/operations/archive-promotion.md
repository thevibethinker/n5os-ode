---
date: "2025-10-26T00:00:00Z"
version: 1.0
category: operations
priority: high
---

# Archive Promotion Protocol

**Version**: 1.0  
**Purpose**: Automated promotion of significant conversations from N5/logs/threads to Documents/Archive  
**Status**: Active

---

## Two-Tier Archive System

### Tier 1: Complete Archive (SSOT)
**Location**: `N5/logs/threads/`  
**Scope**: 100% of conversations (automated by conversation-end)  
**Purpose**: Complete historical record, searchability, debugging, resume work

### Tier 2: Curated Portfolio  
**Location**: `Documents/Archive/`  
**Scope**: ~20% of conversations (auto-promoted based on rules)  
**Purpose**: Showcase work, client artifacts, major deliverables, human-browsable portfolio

---

## Promotion Rules (v1.0)

A conversation is **automatically promoted** from `N5/logs/threads/` to `Documents/Archive/` if it meets **ANY** of these criteria:

### 1. Worker Completion
```yaml
trigger: Conversation tagged with #worker
rationale: Worker conversations are assigned tasks with clear deliverables
detection: Check conversation_registry for tags containing 'worker'
```

### 2. Explicit Deliverable
```yaml
trigger: Conversation tagged with #deliverable
rationale: User explicitly marked as important
detection: Check conversation_registry for tags containing 'deliverable'
```

### 3. Registry Entry
```yaml
trigger: Entry exists in deliverables registry
rationale: Formal deliverable tracking indicates significance
detection: Query deliverables registry for conversation_id
```

### 4. Manual Override
```yaml
trigger: User runs /archive-promote command
rationale: User judgment on significance
detection: Command execution
implementation: Phase 2
```

### 5. Major System Changes (Optional - Phase 2)
```yaml
trigger: >10 files modified OR new command created OR schema changes
rationale: Significant system modifications warrant showcase
detection: Analyze AAR artifacts count and types
implementation: Phase 2 (tune threshold based on usage)
```

---

## Implementation Phases

### Phase 1 (Current): Rules 1-3
- Auto-detect based on tags and registry
- Copy (not move) from N5/logs to Documents/Archive
- Preserve links in conversation_registry
- Update README with promotion metadata

### Phase 2 (Future): Rule 4-5 + Enhancements
- `/archive-promote` command (manual override)
- Artifact-based detection (file count, types)
- Reclassification tool
- AI-suggested promotions

### Phase 3 (Nice-to-have): Portfolio Tools
- Unified search across both locations
- Portfolio export/sharing
- Enhanced README generation
- Client-ready packaging

---

## Decision Framework

### Auto-Promote (No User Action)
- ✅ Worker completions
- ✅ Tagged deliverables
- ✅ Registry entries

### User Decides Later
- ⏸️ Borderline cases
- ⏸️ Uncertain significance
- ⏸️ Wait for retrospective review

### Stay in N5/logs Only
- 📋 Research sessions
- 📋 Planning conversations
- 📋 Routine queries
- 📋 Debug sessions
- 📋 Small fixes

---

## Technical Details

### Copy, Not Move
**Rationale**: N5/logs remains SSOT (P2, ZT5)
- Source: `N5/logs/threads/[timestamp]_[title]_[suffix]/`
- Target: `Documents/Archive/[date]-[cleaned-title]/`
- Operation: Recursive copy with symlinks preserved
- Registry: Both paths recorded

### README Enhancement
When promoted, update `Documents/Archive/[dir]/README.md`:
```markdown
---
promoted_from: N5/logs/threads/[original]
promoted_date: [timestamp]
promotion_reason: [rule that triggered]
conversation_id: [con_xxx]
---
```

### Idempotency
- Check if destination exists before copy
- Skip if already promoted (avoid duplicates)
- Log promotion events to conversation_registry

---

## Monitoring & Tuning

### Success Metrics
- Promotion rate: Target ~15-25% of conversations
- False positives: Check monthly, adjust rules
- User overrides: Track manual promotions to identify pattern gaps

### Review Cadence
- Weekly: Check promotion rate
- Monthly: Review promoted items for quality
- Quarterly: Adjust rules based on usage patterns

---

## Rollback Plan

If promotion system causes issues:
1. Disable in conversation-end.py (set `ARCHIVE_PROMOTION_ENABLED = False`)
2. N5/logs remains unaffected (SSOT preserved)
3. Manually promoted items stay in Documents/Archive
4. Re-enable after fixes

---

## Related Files

- `N5/scripts/n5_conversation_end.py` - Implementation
- `N5/data/conversations.db` - Registry with tags
- `Knowledge/architectural/principles/core.md` - SSOT principle (P2)

---

**Principle Compliance**: P2 (SSOT), ZT3 (Organization shouldn't exist), ZT5 (SSOT Always), P1 (Human-Readable)

**v1.0 | 2025-10-26**
