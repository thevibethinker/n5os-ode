# Calendar Tagging System — Complete Audit & Harmonization Plan

**Date:** 2025-10-11  
**Status:** Audit Complete — Ready for Harmonization  
**Audit Scope:** Entire N5 system

---

## Executive Summary

The calendar tagging system is **narrowly contained** with minimal spread. Current implementation is **clean and isolated** to the meeting prep digest system. The taxonomy is **ready for harmonization** without cascading changes across the system.

### Key Findings

✅ **Single source implementation** — Only used in `meeting_prep_digest.py`  
✅ **Two documentation files** — Complete reference doc + command doc  
⚠️ **Priority taxonomy inconsistency** — `high`, `protect`, `low` are on different scales  
✅ **No conflicts with stakeholder classifier** — Separate systems, no overlap  
✅ **Email detection rules** — Simple, non-conflicting taxonomy  
✅ **Ready for one-shot harmonization** — All changes can be made atomically

---

## Complete System Map

### 1. Implementation Files (CODE)

#### Primary Implementation
- **File:** `N5/scripts/meeting_prep_digest.py`
- **Lines:** 31-48 (constants), 75-103 (extraction), 254-275 (BLUF), 286-344 (output)
- **Version:** 2.0.0
- **Status:** Active, in production use

**Tag Constants:**
```python
STAKEHOLDER_TYPES = [
    "customer", "community", "partner", "investor", 
    "vendor", "job_seeker", "vc", "channel_partner"
]

MEETING_TYPES = [
    "discovery", "decision", "update", "follow-up",
    "coaching", "sales", "partnership", "fundraising"
]

# MISSING: PRIORITY_LEVELS constant
```

**Tag Extraction Function:**
```python
def extract_tags_from_description(description: str) -> Dict[str, List[str]]
```
- Returns: `{"stakeholders": [...], "types": [...], "priorities": [...]}`
- Validates stakeholders against `STAKEHOLDER_TYPES`
- Does NOT validate types or priorities

**Tag Usage Points:**
1. **Line 254** — BLUF generation (uses `types` for conditional logic)
2. **Line 286** — Section header display (shows stakeholders + types)
3. **Line 329** — Prep actions (uses `priorities` and `types` for suggestions)
4. **Line 484** — Tag extraction called during filtering

---

### 2. Documentation Files

#### Complete Reference (SOURCE OF TRUTH)
- **File:** `N5/docs/calendar-tagging-system-COMPLETE.md`
- **Lines:** 548 total
- **Status:** Single source of truth provided by user
- **Contains:** All code, examples, harmonization plan, open questions

#### User-Facing Documentation
- **File:** `N5/docs/calendar-tagging-system.md`
- **Lines:** ~350
- **Status:** Active user guide
- **Contains:** Tag taxonomy, usage examples, behavior descriptions

#### Command Documentation
- **File:** `N5/commands/meeting-prep-digest.md`
- **Lines:** ~200
- **Status:** Active command reference
- **Contains:** Tag taxonomy quick reference, usage patterns

---

### 3. Related Systems (NO DIRECT INTEGRATION)

#### Stakeholder Classifier System
- **File:** `N5/scripts/utils/stakeholder_classifier.py`
- **Function:** Classifies internal vs external (binary)
- **Domains:** `mycareerspan.com`, `theapply.ai`
- **Integration:** None — separate concern
- **Opportunity:** Could suggest stakeholder tags based on email domain

#### Email Detection Rules
- **File:** `Lists/detection_rules.md`
- **Current Taxonomy:**
  - Jobs/Tasks (keywords: task, job, follow-up, action)
  - Attachments (types: pdf, docx, xlsx, jpg, png, mp4)
  - Articles/Newsletters (patterns: http/https URLs, "newsletter")
- **Integration:** None — separate concern
- **Opportunity:** Could extend to classify stakeholder type from email threads

#### Block Templates System
- **File:** `N5/prefs/block_templates/external/stakeholder-profile.template.md`
- **Contains:** Template for stakeholder profiles
- **Integration:** None — no tag field in template
- **Opportunity:** Could add stakeholder type field to profile metadata

---

## Taxonomy Analysis

### Current State

#### Stakeholder Types (8 types) ✅
```
customer, community, partner, investor, 
vendor, job_seeker, vc, channel_partner
```
**Status:** CONSISTENT — All on same dimension (relationship type)

#### Meeting Types (8 types) ✅
```
discovery, decision, update, follow-up,
coaching, sales, partnership, fundraising
```
**Status:** CONSISTENT — All on same dimension (interaction purpose)

#### Priority Levels (3 levels) ⚠️
```
high, protect, low
```
**Status:** INCONSISTENT — Mixed scale dimensions
- `high` and `low` = importance scale
- `protect` = action directive (different dimension)

---

## The Priority Problem

### Issue Description

`#priority:protect` is not on the same scale as `#priority:high` and `#priority:low`.

- **High/Low** = Importance ranking (scalar)
- **Protect** = Action directive (boolean)

**This creates logical inconsistencies:**
- Can a meeting be `high` AND `protect`? (Currently can't express this)
- Is `protect` higher than `high`? (Unclear)
- What if something is `low` priority but still `protect`? (Can't express)

### Current Code Impact

```python
# Line 329 in meeting_prep_digest.py
if 'high' in tags.get('priorities', []) or 'protect' in tags.get('priorities', []):
    section += "1. ⚠️ Protect this time block — reschedule conflicts\n"
```

Code treats them as equivalent, but semantically they're different concepts.

---

## Harmonization Options

### Option A: Numeric Scale (Recommended)
```python
PRIORITY_LEVELS = {
    "critical": 1,  # Was: protect
    "high": 2,      # Was: high
    "medium": 3,    # New: default
    "low": 4        # Was: low
}
```

**Pros:**
- Clear ranking
- Extensible
- Maps to urgency/importance frameworks

**Cons:**
- Requires user to learn new tags
- "critical" less intuitive than "protect"

---

### Option B: Action-Based (Alternative)
```python
PRIORITY_LEVELS = [
    "protect",    # Do not move
    "prefer",     # Avoid conflicts if possible
    "flexible"    # Can reschedule
]
```

**Pros:**
- Action-oriented (matches user mental model)
- "Protect" is intuitive
- Clear scheduling guidance

**Cons:**
- Not a traditional priority scale
- Doesn't capture urgency separate from flexibility

---

### Option C: Dual-Tag System (Complex)
```python
# Separate concerns
#priority:high|medium|low     # Importance
#flexible:yes|no              # Reschedulability
```

**Pros:**
- Separates orthogonal dimensions
- Maximum expressiveness

**Cons:**
- More complex for users
- Requires two tags to express current "protect" concept
- Over-engineering for current needs

---

## Recommended Harmonization: Option A

### Rationale
1. **Simplicity** — Single scale, clear ranking
2. **Familiarity** — P1/P2/P3 style priority common in product/engineering
3. **Extensibility** — Easy to add P0 (emergency) if needed
4. **Code simplicity** — Conditional logic becomes cleaner

### Proposed New Taxonomy

```python
PRIORITY_LEVELS = ["critical", "high", "medium", "low"]

# Tag usage:
#priority:critical  # Do not reschedule (was: protect)
#priority:high      # Important, avoid conflicts
#priority:medium    # Normal priority (new default)
#priority:low       # Can reschedule freely
```

### Migration Path

**For existing users:**
1. `#priority:protect` → `#priority:critical`
2. `#priority:high` → `#priority:high` (no change)
3. `#priority:low` → `#priority:low` (no change)
4. No tags → Treated as `medium` (implicit default)

**No backward compatibility needed** — Tags are in calendar descriptions (user-managed), not in code/data.

---

## Complete Harmonization Checklist

### Phase 1: Code Changes

- [ ] **1.1** Add `PRIORITY_LEVELS` constant to `meeting_prep_digest.py` (after line 42)
  ```python
  PRIORITY_LEVELS = ["critical", "high", "medium", "low"]
  ```

- [ ] **1.2** Update tag extraction validation (line 120)
  ```python
  priority_matches = re.findall(r'#priority:(\w+)', description, re.IGNORECASE)
  tags["priorities"] = [m.lower() for m in priority_matches if m.lower() in PRIORITY_LEVELS]
  ```

- [ ] **1.3** Update prep action logic (line 329-331)
  ```python
  if 'critical' in tags.get('priorities', []) or 'high' in tags.get('priorities', []):
      section += "1. ⚠️ Protect this time block — reschedule conflicts\n"
  ```

- [ ] **1.4** Add priority to BLUF generation (optional enhancement)
  ```python
  if 'critical' in tags.get('priorities', []):
      bluf = f"🚨 CRITICAL: {bluf}"
  ```

### Phase 2: Documentation Updates

- [ ] **2.1** Update `N5/docs/calendar-tagging-system-COMPLETE.md`
  - Lines 22-30: Update priority taxonomy
  - Lines 329-344: Update prep action examples
  - Line 548+: Add change log entry

- [ ] **2.2** Update `N5/docs/calendar-tagging-system.md`
  - Priority levels section
  - Usage examples
  - Add migration note for existing users

- [ ] **2.3** Update `N5/commands/meeting-prep-digest.md`
  - Line 75-82: Update priority levels table
  - Add migration note

### Phase 3: Validation & Testing

- [ ] **3.1** Test tag extraction with new priority levels
  ```bash
  python3 N5/scripts/meeting_prep_digest.py --dry-run
  ```

- [ ] **3.2** Verify backward compatibility (untagged meetings still work)

- [ ] **3.3** Verify invalid tags are silently ignored

- [ ] **3.4** Test all priority levels in calendar descriptions
  - `#priority:critical` → Shows warning
  - `#priority:high` → Shows warning
  - `#priority:medium` → No warning
  - `#priority:low` → No warning
  - No tag → No warning (treated as medium)

### Phase 4: User Communication (Optional)

- [ ] **4.1** Create migration guide for existing users
- [ ] **4.2** Update any scheduled task instructions that reference tags
- [ ] **4.3** Add to next digest as "System Update" note

---

## Files Requiring Changes

### Code Files (1)
1. `N5/scripts/meeting_prep_digest.py`
   - Add constant (1 line after line 42)
   - Update validation (1 line at line 120)
   - Update conditional (1 line at line 329)
   - **Total:** 3 line changes

### Documentation Files (3)
1. `N5/docs/calendar-tagging-system-COMPLETE.md`
   - Update priority section (~8 lines)
   - Update examples (~4 lines)
   - Add change log entry (~3 lines)
   - **Total:** ~15 line changes

2. `N5/docs/calendar-tagging-system.md`
   - Update priority section (~8 lines)
   - Update examples (~4 lines)
   - Add migration note (~3 lines)
   - **Total:** ~15 line changes

3. `N5/commands/meeting-prep-digest.md`
   - Update priority table (~8 lines)
   - Add migration note (~2 lines)
   - **Total:** ~10 line changes

---

## No Changes Required

### Systems That Don't Need Updates

1. **Stakeholder Classifier** (`N5/scripts/utils/stakeholder_classifier.py`)
   - Separate concern, no integration

2. **Email Detection Rules** (`Lists/detection_rules.md`)
   - Separate concern, no conflicts

3. **Block Templates** (`N5/prefs/block_templates/`)
   - No tag fields in templates

4. **Meeting Processing System** (`N5/scripts/meeting_*`)
   - Only digest uses tags

5. **Command Registry** (`N5/config/commands.jsonl`)
   - Command definition unchanged

6. **Incantum Triggers** (`N5/config/incantum_triggers.json`)
   - Trigger unchanged

---

## Future Enhancement Opportunities

### 1. Extend Email Detection Rules
Add stakeholder classification to email routing:

```markdown
## Stakeholders (NEW)
- From domain patterns → Auto-suggest stakeholder type
- VC domains → #stakeholder:vc
- .edu domains → #stakeholder:community or #stakeholder:job_seeker
```

**Files affected:** `Lists/detection_rules.md`

### 2. Stakeholder Classifier Enhancement
Extend binary classifier to suggest tags:

```python
def suggest_stakeholder_tag(email: str, context: str) -> Optional[str]:
    """Suggest stakeholder tag based on email domain and context."""
    # VC domains → "vc"
    # Partner domains → "partner"
    # Past meeting tags → Reuse
```

**Files affected:** `N5/scripts/utils/stakeholder_classifier.py`

### 3. Block Template Integration
Add stakeholder type field to profile template:

```markdown
## Stakeholder Classification
- **Type:** [customer/partner/investor/etc]
- **Relationship Stage:** [discovery/active/maintenance]
```

**Files affected:** `N5/prefs/block_templates/external/stakeholder-profile.template.md`

### 4. Gmail API Integration
Replace mock email search with real Gmail API:

```python
def get_last_3_interactions(email: str) -> List[Dict[str, str]]:
    # Use use_app_gmail instead of mock data
    results = use_app_gmail(
        tool_name="gmail-search-messages",
        configured_props={"q": f"from:{email} OR to:{email}", "maxResults": 3}
    )
```

**Files affected:** `N5/scripts/meeting_prep_digest.py` line 184-212

---

## Risk Assessment

### Low Risk Changes ✅
- Adding `PRIORITY_LEVELS` constant
- Updating documentation
- Tag validation logic

### Zero Risk (No Code Changes) ✅
- Calendar descriptions (user-managed)
- Existing untagged meetings (still work)
- Related systems (no integration)

### Testing Required ⚠️
- Dry-run digest generation
- Priority conditional logic
- Invalid tag handling

---

## Timeline Estimate

**Total harmonization time:** ~30 minutes

- Code changes: 5 minutes (3 lines)
- Documentation updates: 15 minutes (3 files)
- Testing: 10 minutes (dry-run + validation)

---

## Open Questions (From Complete Reference Doc)

1. **Priority scale:** Numeric, adjective-based, or action-based?
   - **ANSWER:** Adjective-based (critical/high/medium/low)

2. **Tag namespacing:** Should we support custom namespaces?
   - **ANSWER:** Not needed for current use case

3. **Tag inheritance:** Should tags from past meetings carry forward?
   - **ANSWER:** Future enhancement, not MVP

4. **Tag suggestions:** Should system auto-suggest tags?
   - **ANSWER:** Future enhancement, not MVP

5. **Tag validation:** Strict (reject) or permissive (ignore)?
   - **ANSWER:** Permissive (already implemented)

6. **Tag analytics:** Track tag usage over time?
   - **ANSWER:** Future enhancement, not MVP

---

## Summary

**Current state:** Clean, isolated implementation with one taxonomy inconsistency  
**Harmonization scope:** 4 files, ~43 lines of changes  
**Risk level:** Low (isolated system, no dependencies)  
**Time estimate:** 30 minutes  
**Recommendation:** Proceed with Option A (critical/high/medium/low)

The calendar tagging system is **ready for harmonization** with minimal disruption.
