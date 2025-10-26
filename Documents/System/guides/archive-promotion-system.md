---
date: "2025-10-26T00:00:00Z"
version: 1.0
category: documentation
priority: high
related: "['N5/prefs/operations/archive-promotion.md', 'N5/scripts/n5_conversation_end.py']"
---

# Archive Promotion System Documentation

**Version**: 1.0  
**Implemented**: 2025-10-26  
**Status**: Production Ready  
**Philosophy**: Zero-Touch (ZT3: Organization Step Shouldn't Exist)

---

## Overview

Two-tier archive system that automatically promotes significant conversations from `N5/logs/threads/` (complete archive, SSOT) to `Documents/Archive/` (curated portfolio) based on metadata tags.

**Zero-Touch Alignment**: Organization happens as artifact of metadata, not manual filing decision.

---

## Architecture

### Information Flow

```
conversation-end
    ↓
N5/logs/threads/ (100% conversations, SSOT)
    ↓ [check promotion rules]
    ↓
Documents/Archive/ (~20% promoted, curated)
    ↓
Portfolio/Resume/Client showcase
```

### Key Principles

1. **P2 (SSOT)**: N5/logs/threads is canonical, Documents/Archive is derived view
2. **ZT3 (No Organization Step)**: Promotion triggered by tags, not manual decision
3. **ZT8 (Minimal Touch)**: Auto-copy, human only tags conversations
4. **P18 (State Verification)**: Confirms copy succeeded before reporting

---

## Promotion Rules (Phase 1)

Conversations auto-promote if tagged with:

| Tag | Meaning | Typical % |
|-----|---------|-----------|
| `#worker` | Spawned worker completion | 10-15% |
| `#deliverable` | Major client/public deliverable | 5-10% |
| `#shipped` | Production code/system deployed | 3-5% |

**Target promotion rate**: 15-25% of conversations

---

## Implementation

### Phase 1 Components

**1. Protocol Documentation**
- `file 'N5/prefs/operations/archive-promotion.md'`
- Defines rules, future phases, principles

**2. Automated Logic**
- `N5/scripts/n5_conversation_end.py::archive_promotion()`
- Phase 6 in conversation-end flow
- Runs after registry closure

**3. Testing**
- `N5/scripts/test_archive_promotion.py`
- Command: `/archive-promotion-test`
- Validates: rules, detection, copy simulation

### How It Works

```python
def archive_promotion():
    1. Get conversation from registry
    2. Check tags against promotion rules
    3. If match:
       a. Find archive in N5/logs/threads
       b. Copy to Documents/Archive
       c. Verify copy succeeded
       d. Report promotion
    4. If no match: silently skip
```

**Runtime**: <1 second  
**Impact**: Zero friction, no user decision required

---

## Usage

### Automatic (Default)

Simply run conversation-end as normal:

```bash
python3 N5/scripts/n5_conversation_end.py
```

If conversation has promotion tags, archive auto-copies to Documents/Archive.

### Manual Testing

```bash
# Test promotion logic without running conversation-end
python3 N5/scripts/test_archive_promotion.py
```

### Tagging Conversations

Tag via registry (typically done by spawn_worker or manual tagging):

```python
from conversation_registry import ConversationRegistry
registry = ConversationRegistry()
registry.update("con_XYZ", tags=["worker", "shipped"])
```

---

## Directory Structure

### Before Promotion

```
N5/logs/threads/
  └── 2025-10-26-1337_Worker6-Dashboard_XYZ/
      ├── aar-2025-10-26.json
      ├── INDEX.md
      └── artifacts/
```

### After Promotion

```
N5/logs/threads/  [SSOT remains unchanged]
  └── 2025-10-26-1337_Worker6-Dashboard_XYZ/

Documents/Archive/  [Copy created]
  └── 2025-10-26-Worker6-Dashboard/
      ├── aar-2025-10-26.json
      ├── INDEX.md
      └── artifacts/
```

**Note**: Conversation ID suffix removed from Documents/Archive name for readability.

---

## Monitoring & Metrics

### Weekly Review (5 min)

Check promotion rate:

```bash
# Count promotions this week
ls -lt Documents/Archive/ | head -10

# Typical rate: 2-3 per week (assuming ~15 conversations/week)
```

### Monthly Health Check (15 min)

1. Promotion rate in target range? (15-25%)
2. Any wrongly promoted? (should be ~0%)
3. Any missed promotions? (review N5/logs for candidates)
4. Adjust rules if needed

### Red Flags

⚠️ **>40% promotion rate**: Rules too broad, losing curation benefit  
⚠️ **<5% promotion rate**: Rules too strict, missing showcase value  
⚠️ **Manual re-filing**: Symptom of wrong rule or missing tag

---

## Phase 2 Roadmap (Future)

### 1. Manual Override Command

```bash
# Promote any conversation retroactively
python3 N5/scripts/n5_archive_promote.py --convo-id con_XYZ
```

### 2. Rule 4-5 Implementation

- **Rule 4**: Artifact detection (>5 files, >50KB code)
- **Rule 5**: Duration/complexity (>2 hours, multi-phase)

### 3. Reclassification

- Detect wrongly promoted archives
- Suggest demotion (copy back only)
- Update promotion confidence scores

### 4. Portfolio Generation

- Auto-generate portfolio page from Documents/Archive
- Markdown index with summaries
- Filter by type/tag

---

## Troubleshooting

### Issue: Conversation not promoted despite tags

**Check:**
1. Tags in registry? `registry.get("con_XYZ")`
2. Archive exists in N5/logs? `ls N5/logs/threads/*_XYZ`
3. Run test script: `python3 N5/scripts/test_archive_promotion.py`

### Issue: Promoted but wrong conversation

**Fix:**
1. Delete from Documents/Archive
2. Update registry tags
3. Re-run conversation-end if needed

### Issue: Test script fails

**Debug:**
```bash
python3 N5/scripts/test_archive_promotion.py
# Review error output
# Check: registry access, archive detection, file paths
```

---

## Integration Points

### Spawned Workers

Worker spawning automatically tags:

```python
# In spawn_worker.py
registry.create(
    convo_id=worker_id,
    type="build",
    tags=["worker", parent_phase]
)
```

Worker completion triggers conversation-end → auto-promotion.

### Manual Deliverables

For non-worker significant work:

```python
# At conversation end
registry.update(
    convo_id=current_convo,
    tags=["deliverable", "client-facing"]
)
```

Then run conversation-end.

---

## File Locations

| Component | Path | Purpose |
|-----------|------|---------|
| Protocol | `N5/prefs/operations/archive-promotion.md` | Rules & philosophy |
| Implementation | `N5/scripts/n5_conversation_end.py` | Phase 6 logic |
| Tests | `N5/scripts/test_archive_promotion.py` | Validation |
| Documentation | `N5/docs/archive-promotion-system.md` | This file |
| Command Registry | `N5/config/commands.jsonl` | Test command trigger |

---

## Success Metrics (3-Month Target)

- ✅ **95%+ conversations** have complete AAR in N5/logs
- ✅ **15-25% conversations** promoted to Documents/Archive
- ✅ **<5% correction rate** (wrongly promoted/missed)
- ✅ **0% manual filing** (all via tags + automation)
- ✅ **<2 min** to find any conversation (search both archives)

---

## Principles Compliance

| Principle | How Satisfied |
|-----------|---------------|
| **P2 (SSOT)** | N5/logs is canonical ✅ |
| **ZT3 (No Org Step)** | Tags drive promotion ✅ |
| **ZT8 (Minimal Touch)** | Auto-copy, no decision ✅ |
| **P18 (State Verify)** | Confirms copy success ✅ |
| **P7 (Dry-Run)** | Test script available ✅ |
| **P20 (Modular)** | Separate function, testable ✅ |

---

## Version History

**v1.0 (2025-10-26)**
- Initial implementation
- Rules 1-3 (worker, deliverable, shipped)
- Test framework
- Documentation

**Future (v1.1)**
- Manual promotion command
- Rules 4-5 (artifact-based)
- Portfolio generation
- Reclassification tools

---

**See Also:**
- `file 'N5/prefs/operations/archive-promotion.md'` - Protocol details
- `file 'Documents/zero_touch_manifesto.md'` - Philosophical foundation
- `file 'Knowledge/architectural/architectural_principles.md'` - System principles

**Maintained by:** Vibe Builder persona  
**Questions/Issues:** Test with `/archive-promotion-test` first

*v1.0 | 2025-10-26*
