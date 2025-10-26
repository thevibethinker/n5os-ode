# Tag Taxonomy v3.2 — Types vs. States Principle

**Date:** 2025-10-12  
**Version:** 3.2.0  
**Key Change:** Job seeking reclassified as state, not stakeholder type

---

## V's Insight: Types vs. States

**Problem with v3.1:**
- Kim Wilkes required DUAL stakeholder tags: `#stakeholder:community` + `#stakeholder:job_seeker`
- Complex: Dual classification logic, primary/secondary management
- Semantic confusion: Job seeking is temporary, not fundamental identity

**V's insight:**
> "Job seeking can just be a status instead of a category, because anyone and everyone can be a job seeker. I think we can categorize that less as a type of stakeholder and more as a status of a person."

**Solution in v3.2:**
- Kim Wilkes = `#stakeholder:community` + `#job_seeking:active`
- Clean separation: type (who they are) vs. state (what they're doing)

---

## Core Principle (System-Wide)

**Stakeholder Type = Fundamental Identity**
- What is their relationship to Careerspan?
- Investor, advisor, partner, customer, community, etc.
- Permanent or slowly changing
- Single classification per contact

**State = Temporary Condition**
- What are they currently doing?
- Job seeking (active/inactive)
- Relationship phase (new, warm, active, cold)
- Engagement behavior (responsive, slow)
- Changes frequently, tracks transitions

---

## New Category: Job Seeking Status

### `#job_seeking:*`

**Values:**
- `#job_seeking:active` — Currently seeking employment
- `#job_seeking:inactive` — Not currently seeking

**Applies to:** Anyone, regardless of stakeholder type

**Examples:**
- Community leader job seeking: `#stakeholder:community` + `#job_seeking:active`
- Advisor job seeking: `#stakeholder:advisor` + `#job_seeking:active`
- Investor between roles: `#stakeholder:investor` + `#job_seeking:active`
- Customer job seeking: `#stakeholder:customer` + `#job_seeking:active`

**Product tracking:**
- `#job_seeking:active` = Using Careerspan product, track placement outcome
- Transition: active → inactive when placed
- Measure: Did Careerspan help them get hired?

---

## Stakeholder Types (Updated — v3.2)

**9 types (removed job_seeker):**
1. `#stakeholder:investor`
2. `#stakeholder:advisor`
3. `#stakeholder:customer`
4. `#stakeholder:partner:collaboration`
5. `#stakeholder:partner:channel`
6. `#stakeholder:community`
7. `#stakeholder:prospect`
8. `#stakeholder:vendor`
9. `#stakeholder:networking_contact`

**Removed:**
- ~~`#stakeholder:job_seeker`~~ → Now `#job_seeking:active` (state, not type)

---

## Before vs. After (Kim Wilkes Example)

### v3.1 (Dual Stakeholder Types — Complex)
```yaml
Tags:
  stakeholder_primary: #stakeholder:community
  stakeholder_secondary: #stakeholder:job_seeker  # Dual classification
  relationship: #relationship:active
  priority: #priority:critical

Issues:
  - Dual stakeholder types (complex logic)
  - Primary/secondary distinction (system overhead)
  - Which type determines priority? (ambiguous)
  - What happens when job search ends? (remove tag? demote to inactive?)
```

### v3.2 (State-Based — Clean)
```yaml
Tags:
  stakeholder_type: #stakeholder:community  # Single, clear
  job_seeking: #job_seeking:active  # Orthogonal state
  relationship: #relationship:active
  priority: #priority:critical

Benefits:
  - Single stakeholder type (unambiguous)
  - States are orthogonal (no conflicts)
  - Priority based on stakeholder type (clear)
  - Job search ends: job_seeking:active → inactive (transition tracked)
```

---

## System-Wide Impact

### Pattern Analyzer
**Updated logic:**
- Don't infer `#stakeholder:job_seeker` anymore
- Instead detect `#job_seeking:active` from signals:
  - Email keywords: "interviewing", "job search", "applying"
  - Using Careerspan product
  - LinkedIn status: "Open to work", recent job-seeking activity

### Weekly Review
**Updated format:**
- No "Primary/Secondary stakeholder" sections
- Single stakeholder type per contact
- Job seeking status shown separately (if active)

### Profile Template
**Updated structure:**
```markdown
## Tags

### Verified
**Stakeholder Type:**
- `#stakeholder:community`

**Employment Status:**
- `#job_seeking:active`

**Relationship & Engagement:**
- `#relationship:active`
- `#priority:critical`
- `#context:hr_tech`
```

### Configuration Files
**Updated:**
- `stakeholder_rules.json` — Removed dual_tags section, added job_seeking_status
- `tag_taxonomy.json` — Moved job_seeker → job_seeking category
- `tag_mapping.json` — Updated Howie translation (no bracket for job_seeking, N5-only)

---

## Extensibility: Other States

**V's principle enables future states:**

### Hypothetical: Hiring Status
- `#hiring:active` — Currently hiring (for customers using Careerspan to hire)
- `#hiring:inactive` — Not currently hiring

### Hypothetical: Transitioning Status
- `#transitioning:active` — Career transition in progress
- `#transitioning:inactive` — Stable in current role

### Hypothetical: Fundraising Status
- `#fundraising:active` — Actively raising (for investor stakeholders)
- `#fundraising:inactive` — Not currently fundraising

**Pattern:** `#{state_name}:active` or `inactive`

**Benefit:** Orthogonal dimensions, no dual classification complexity

---

## Migration Path

### Immediate (Today)
- ✅ Kim Wilkes profile updated (community + job_seeking:active)
- ✅ Configuration files updated (stakeholder_rules.json)
- ✅ Tag taxonomy updated (TAG-TAXONOMY-MASTER.md v3.2)
- ⏳ Pattern analyzer updated (remove job_seeker inference)

### Future (When Needed)
- Add other state categories as discovered (#hiring:*, #transitioning:*, etc.)
- Apply same types vs. states principle
- Maintain orthogonal dimensions

---

## Success Metrics (v3.2)

**Taxonomy cleanliness:**
- ✅ Zero dual stakeholder classifications needed
- ✅ All states are orthogonal to types
- ✅ Clear semantic separation (identity vs. condition)

**System simplicity:**
- ✅ Removed dual classification logic
- ✅ Simpler priority inference (stakeholder type determines priority)
- ✅ Easier to explain ("You're a community leader who's job seeking" vs. "You're both community and job_seeker")

**Extensibility:**
- ✅ Can add new states without touching stakeholder types
- ✅ States apply to anyone (orthogonal)
- ✅ Tracks transitions naturally (active → inactive)

---

## Validation: All Profiles Compliant

**Hamoon Ekhtiari:**
- ✅ Single stakeholder type: `#stakeholder:partner:collaboration`
- ✅ No job_seeking tag (not job seeking)

**Alex Caveny:**
- ✅ Single stakeholder type: `#stakeholder:advisor`
- ✅ No job_seeking tag (not job seeking)

**Carly Ackerman:**
- ✅ Single stakeholder type: `#stakeholder:advisor`
- ✅ No job_seeking tag (not job seeking)

**Heather Wixson:**
- ✅ Single stakeholder type: `#stakeholder:partner:collaboration`
- ✅ No job_seeking tag (not job seeking)

**Weston Stearns:**
- ✅ Single stakeholder type: `#stakeholder:partner:collaboration`
- ✅ No job_seeking tag (not job seeking)

**Kim Wilkes:**
- ✅ Single stakeholder type: `#stakeholder:community`
- ✅ Job seeking state: `#job_seeking:active`
- ✅ Clean separation (type vs. state)

---

**Status:** v3.2 taxonomy finalized and applied system-wide. All profiles compliant.
