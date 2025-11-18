---
created: 2025-11-15
last_edited: 2025-11-15
version: 1.0
---

# Meeting-Specific Script Consolidation - CORRECT VERSION

**Date**: 2025-11-15T10:19:00Z  
**Reason**: Consolidated 3 meeting-specific duplicate detection scripts  
**Orchestrator**: con_wkDPnaagydefZ4QH  
**Worker**: Worker 02 (con_jVhSit901SkcXhgH - Vibe Builder)

## What Was Wrong (First Attempt)

Initially created a "Frankenstein" by mixing:
- **duplicate_scanner.py** (general workspace file scanner) 
- **cleanup_duplicate_requests.py** (inbox cleanup, not file duplication)
- Meeting-specific scripts

This was incorrect because the first two are **general tools** not **meeting-specific**.

## Correct Consolidation

### Archived (Meeting-Specific Only)

1. **cleanup_duplicate_meeting_files.py** (47 lines)
   - Purpose: Clean lowercase intelligence files when UPPERCASE/B## equivalents exist
   - Pattern: Keep B08_STAKEHOLDER_INTELLIGENCE.md, remove stakeholder_intelligence.md
   - Consolidated into: `meeting_duplicate_detector.py`

2. **deduplicate_meetings.py** (74 lines)
   - Purpose: Prepare data for LLM-based semantic meeting deduplication
   - Uses: Prompts/deduplicate-meetings.md for intelligent analysis
   - Consolidated into: `meeting_duplicate_detector.py` (semantic scan mode)

3. **meeting_registry_deduplicate.py** (117 lines)
   - Purpose: Remove duplicate gdrive_id entries from meeting_registry.json
   - Strategy: Keep most complete record, remove duplicates
   - Consolidated into: `meeting_duplicate_detector.py`

### Kept Separate (General Tools)

1. **duplicate_scanner.py** (325 lines)
   - Purpose: General workspace file duplicate detection (entire /home/workspace)
   - Scope: Hash-based exact duplicates, vestigial patterns, tiny/empty files
   - Status: **RESTORED** - This is NOT meeting-specific, it's a general tool

2. **cleanup_duplicate_requests.py** (63 lines)
   - Purpose: Clean up AI request queue for already-processed meetings
   - Scope: N5/inbox/ai_requests management
   - Status: **RESTORED** - This is inbox management, not duplicate detection

### Did NOT Replace

- **meeting_ai_deduplicator.py** (303 lines) - Overlaps with meeting_duplicate_manager.py (canonical)

## New Canonical Tool

**`meeting_duplicate_detector.py`** - Handles ONLY meeting-related duplicates

Capabilities:
1. Intelligence file duplicates (lowercase vs UPPERCASE/B##)
2. Meeting registry duplicates (gdrive_id)
3. Semantic analysis prep (for LLM-based deduplication)

### Usage

```bash
# Scan all
python3 N5/scripts/meeting_duplicate_detector.py scan

# Scan specific
python3 N5/scripts/meeting_duplicate_detector.py scan --intelligence
python3 N5/scripts/meeting_duplicate_detector.py scan --registry
python3 N5/scripts/meeting_duplicate_detector.py scan --semantic

# Cleanup (dry run)
python3 N5/scripts/meeting_duplicate_detector.py cleanup --dry-run

# Cleanup (execute)
python3 N5/scripts/meeting_duplicate_detector.py cleanup
```

## Rollback

If needed:
```bash
cd /home/workspace/N5/scripts
cp .EXPUNGED/meeting-scripts-consolidated-2025-11-15/*.py ./
rm -f meeting_duplicate_detector.py
```

## Lessons Learned

1. **Read the actual scope** - Check if scripts are domain-specific or general before consolidating
2. **Test semantic understanding** - "Duplicate detection" doesn't mean all duplicates are the same domain
3. **Preserve working tools** - Don't consolidate things that work fine separately just to reduce count

