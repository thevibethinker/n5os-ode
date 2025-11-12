---
created: 2025-11-04
last_edited: 2025-11-04
version: 1.0
---
# Taxonomy Restructure: Risk/Reward Analysis

**Proposal:** Change from flat taxonomy to hierarchical (internal/external → subtypes)

---

## Current vs. Proposed Structure

### Current (Flat):
```
internal, external, coaching, partnership, sales, technical, workshop
```

Problem: These aren't equivalent categories. "coaching" is always external, "technical" could be internal or external.

### Proposed (Hierarchical):
```
external/
  - coaching      (Wisdom Partners, advisor sessions)
  - partnership   (Business partnerships, affiliates)
  - sales         (Prospect calls, customer meetings)
  - workshop      (External group learning)
  - discovery     (Intro calls, qualification)
  - general       (Catchall external)

internal/
  - standup       (Team syncs, daily standups)
  - technical     (Internal debugging, pair programming)
  - planning      (Strategy, war rooms)
  - cofounder     (1-1s with cofounders)
  - general       (Catchall internal)
```

---

## Risk Analysis

### LOW RISKS ✅

1. **Breaking existing functionality**
   - **Risk:** Could break scripts that reference meeting types
   - **Mitigation:** Folder naming strategy doesn't change structure (still 3 fields)
   - **Reversibility:** Can revert to flat taxonomy with simple script
   - **Impact:** LOW - We're building from scratch, minimal existing dependencies

2. **Classification errors**
   - **Risk:** AI might misclassify internal vs. external
   - **Mitigation:** B26_metadata already has clear signals ("Stakeholder Classification")
   - **Detection:** Easy to spot in dry-run review
   - **Impact:** LOW - Obvious from metadata, can fix individually

3. **Folder name collisions**
   - **Risk:** Two meetings same date/subtype/participant
   - **Mitigation:** Already planned numeric suffix handling
   - **Impact:** LOW - Collision detection already in design

### MEDIUM RISKS ⚠️

4. **Taxonomy maintenance overhead**
   - **Risk:** More complex taxonomy = more maintenance
   - **Reality:** Hierarchy actually reduces ambiguity (clearer decision tree)
   - **Impact:** MEDIUM - Slightly more complex but more accurate

5. **Migration complexity**
   - **Risk:** Existing meetings need reclassification
   - **Mitigation:** Script infers from B26 metadata automatically
   - **Testing:** Dry-run shows all classifications for review
   - **Impact:** MEDIUM - More work upfront, but atomic operation

---

## Reward Analysis

### HIGH VALUE REWARDS 🎯

1. **Conceptual clarity**
   - Internal/external is the **fundamental dimension** of meetings
   - Subtypes are **refinements** under that dimension
   - Aligns with how you actually think about meetings
   - **Value:** HIGH - Cognitive alignment

2. **Better greppability**
   ```bash
   # All external meetings
   grep "meeting_type: external" -r Personal/Meetings/
   
   # All coaching meetings
   grep "meeting_subtype: coaching" -r Personal/Meetings/
   
   # External coaching only
   grep -A1 "meeting_type: external" | grep "subtype: coaching"
   ```
   - **Value:** HIGH - More dimensions to query

3. **Accurate categorization**
   - No more ambiguity (is "technical" internal or external?)
   - Taxonomy reflects reality better
   - **Value:** HIGH - Semantic correctness

4. **Scalability**
   - Easy to add new subtypes under internal/external
   - Don't need to rethink top-level taxonomy
   - **Value:** HIGH - Future-proof

5. **CRM alignment**
   - External meetings already have stakeholder classifications in B26
   - Internal meetings already have team context
   - Natural fit with existing metadata structure
   - **Value:** HIGH - Leverages existing data

---

## Folder Naming Strategy

### Three Options:

#### Option A: Full Path in Name
```
2025-09-12_external-sales_allie-greenlight
2025-10-29_external-coaching_alex-wisdom
2025-11-03_internal-standup_team
```

**Pros:** Explicit, no ambiguity
**Cons:** Verbose, redundant (subtype often implies level)

#### Option B: Subtype Only (Recommended)
```
2025-09-12_sales_allie-greenlight
2025-10-29_coaching_alex-wisdom
2025-11-03_standup_team
```

**Pros:** Clean, human-readable, subtype implies level
**Cons:** Must look at frontmatter to know internal/external explicitly

#### Option C: Hybrid (Generic uses full path)
```
2025-09-12_sales_allie-greenlight
2025-10-29_coaching_alex-wisdom
2025-11-03_internal_team-planning
2025-09-12_external_unknown-org
```

**Pros:** Concise for specific types, clear for generic
**Cons:** Inconsistent format

### Recommendation: Option B

**Rationale:**
- Most human-readable
- Subtype already implies internal/external (coaching = external, standup = internal)
- Frontmatter has both fields for queries
- Folder name stays concise
- Aligns with "readable but machine-optimized" goal

**Frontmatter tracks both:**
```yaml
meeting_type: external
meeting_subtype: sales
```

---

## Implementation: Atomic & Reversible

### Phase 0: Define Taxonomy (30 min)

**File:** `N5/schemas/meeting_taxonomy.yaml`

```yaml
taxonomy_version: 2.0

external:
  coaching:
    description: "1-1 coaching or advisory sessions"
    keywords: [wisdom partners, coaching, advisor]
  partnership:
    description: "Business partnerships, affiliate discussions"
    keywords: [partnership, affiliate, integration]
  sales:
    description: "Sales calls, demos, customer meetings"
    keywords: [sales, demo, prospect, customer, discovery]
  workshop:
    description: "External group learning sessions"
    keywords: [workshop, training, webinar]
  discovery:
    description: "Qualification, intro calls"
    keywords: [intro, discovery, qualification]
  general:
    description: "Other external meetings"
    keywords: []

internal:
  standup:
    description: "Team syncs, daily standups"
    keywords: [standup, daily, sync]
  technical:
    description: "Internal debugging, implementation"
    keywords: [debugging, implementation, technical, build]
  planning:
    description: "Strategy sessions, war rooms"
    keywords: [strategy, planning, war room]
  cofounder:
    description: "1-1s with cofounders"
    keywords: [cofounder, 1-1, one-on-one]
  general:
    description: "Other internal meetings"
    keywords: []
```

### Phase 1: Update Frontmatter Schema (15 min)

**Change:**
```yaml
# Old
meeting_type: coaching

# New
meeting_type: external
meeting_subtype: coaching
```

**Backward compatible:** Scripts check for both fields

### Phase 2: Build Inference Logic (1 hour)

**File:** `N5/scripts/infer_meeting_taxonomy.py`

**Logic:**
```python
def infer_taxonomy(metadata: dict) -> tuple[str, str]:
    """Returns (type, subtype) from B26 metadata."""
    
    # Check Stakeholder Classification field
    if "external" in stakeholder_classification.lower():
        type = "external"
        # Infer subtype from CRM tags, themes, participants
        subtype = infer_external_subtype(metadata)
    else:
        type = "internal"
        # Infer subtype from meeting context
        subtype = infer_internal_subtype(metadata)
    
    return type, subtype
```

**Signals for inference:**
- **External:** Stakeholder Classification mentions "client", "customer", "partner", "external"
- **Internal:** Participants are all Careerspan team, or meeting purpose is internal
- **Subtype:** Match keywords from taxonomy against meeting title, themes, CRM tags

### Phase 3: Test Inference on Sample Meetings (30 min)

**Test set:**
```
1. bdr-rjwf-ehc-transcript-2025-11-03T08-34-24.986Z
   Expected: internal/technical (Nafisa N5OS install)

2. 2025-09-08_alex-caveny-wisdom-partners_coaching
   Expected: external/coaching (Wisdom Partners session)

3. Allie Cialeo and Vrijen Attawar + Logan Currie-transcript-2025-09-12T15-33-45.590Z
   Expected: external/sales (Customer discovery/demo)

4. Daily_team_stand-up-transcript-2025-10-29T14-38-58.996Z
   Expected: internal/standup

5. Acquisition War Room-transcript-2025-11-03T19-48-05.399Z
   Expected: internal/planning (Strategy war room)
```

**Output:** Dry-run report showing inferred classification for each

### Phase 4: Update Folder Naming Logic (30 min)

**Change:** Use subtype in folder name, track type in frontmatter

```python
# Folder name uses subtype
folder_name = f"{date}_{subtype}_{participant}"

# Frontmatter tracks both
frontmatter = {
    "meeting_type": type,
    "meeting_subtype": subtype,
    ...
}
```

### Phase 5: Full Dry-Run (15 min)

**Output:** Complete mapping for all existing meetings

```
OLD NAME → NEW NAME (TYPE/SUBTYPE)

Alex x Vrijen - Wisdom Partners Coaching-transcript-2025-08-27T18-03-03.024Z
→ 2025-08-27_coaching_alex-wisdom (external/coaching)

Daily_team_stand-up-transcript-2025-10-29T14-38-58.996Z
→ 2025-10-29_standup_team (internal/standup)

Allie Cialeo and Vrijen Attawar + Logan Currie-transcript-2025-09-12T15-33-45.590Z
→ 2025-09-12_sales_allie-greenlight (external/sales)

bdr-rjwf-ehc-transcript-2025-11-03T08-34-24.986Z
→ 2025-11-03_technical_nafisa-n5os (internal/technical)

Acquisition War Room-transcript-2025-11-03T19-48-05.399Z
→ 2025-11-03_planning_acquisition (internal/planning)
```

**Review:** V approves classification for each meeting

### Phase 6: Execute (30 min)

**Actions:**
1. Add hierarchical frontmatter to all B*.md files
2. Rename folders using subtype
3. Log all changes to `taxonomy_migration_log.json`

### Phase 7: Validation (15 min)

**Tests:**
```bash
# Verify all external meetings
grep -r "meeting_type: external" Personal/Meetings/ | wc -l

# Verify all coaching meetings
grep -r "meeting_subtype: coaching" Personal/Meetings/ | wc -l

# Verify folder names match subtypes
ls Personal/Meetings/*_coaching_*

# Check for errors in frontmatter
python3 validate_taxonomy.py --all
```

---

## Rollback Procedure

### If Issues Found:

**Step 1:** Revert folder names
```bash
python3 N5/scripts/rename_meeting_folders.py --rollback taxonomy_migration_log.json
```

**Step 2:** Revert frontmatter
```bash
python3 N5/scripts/revert_taxonomy.py --flatten
```
Converts hierarchical back to flat (combines type+subtype into single field)

**Step 3:** Verify
```bash
python3 validate_taxonomy.py --flat-only
```

---

## Risk/Reward Verdict

### RISK SCORE: **LOW** ✅

- All changes are atomic and reversible
- Inference can be tested before execution
- Dry-run shows V exactly what will happen
- Existing meeting folders stay intact during development
- No dependencies to break (building from scratch)

### REWARD SCORE: **HIGH** 🎯

- Conceptual clarity (aligns with how you think)
- Better greppability (two dimensions: type + subtype)
- Accurate categorization (no ambiguity)
- Scalable (easy to extend)
- Semantic correctness (reflects reality)

### **RECOMMENDATION: PROCEED** ✅

This change is worth making because:
1. **Low technical risk** - Atomic, reversible, testable
2. **High conceptual value** - Much clearer taxonomy
3. **Better long-term** - More scalable and accurate
4. **Aligns with your mental model** - Internal/external is the primary dimension

Total implementation time: ~4 hours (including testing)

---

## Next Steps

**If approved:**
1. Define taxonomy (you review/approve categories)
2. Build inference logic
3. Test on 5 sample meetings
4. Show you dry-run results
5. Execute migration
6. Integrate into pipeline

**Questions to finalize:**
1. Review proposed subtypes (add/remove/change any?)
2. Folder naming: Confirm Option B (subtype only)?
3. Any edge cases in your meetings I'm missing?

---

**READY TO BUILD IF APPROVED**
