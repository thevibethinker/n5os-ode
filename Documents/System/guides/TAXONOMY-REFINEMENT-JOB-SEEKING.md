# Tag Taxonomy Refinement: Job Seeking as Status

**Date:** 2025-10-12 18:48 ET  
**Change Type:** Semantic improvement  
**Impact:** Simplifies taxonomy, removes dual stakeholder classification

---

## V's Insight

> "Job seeker can just be a status instead of a category, because anyone and everyone can be a job seeker, right? So I think we can categorize that less as a type of stakeholder and more as a status of a person."

**Why this is brilliant:**
- Job seeking is a **temporary state**, not a fundamental identity
- Anyone can be job seeking regardless of their core stakeholder type
- Avoids complex dual classification logic
- Tracks employment lifecycle cleanly

---

## Change Summary

### Before (Complex)
**Problem:** Kim Wilkes required dual stakeholder classification

```
Tags:
- #stakeholder:community (PRIMARY)
- #stakeholder:job_seeker (SECONDARY - dual tag)
```

**Issues:**
- Dual classification complexity
- Which is "primary"? 
- System needs dual tag logic
- Doesn't scale (what if 3 types apply?)

---

### After (Clean)
**Solution:** Job seeking is a separate status dimension

```
Tags:
- #stakeholder:community (WHO she is)
- #job_seeking_status:active (WHAT she's doing)
```

**Benefits:**
- ✅ **Orthogonal dimensions:** Type (community) vs. State (job seeking)
- ✅ **No dual classification:** Single stakeholder type + status
- ✅ **Lifecycle tracking:** active → placed → inactive
- ✅ **Universal applicability:** Anyone can have job-seeking status
- ✅ **Product correlation:** Track Careerspan usage and placement outcomes

---

## New Tag Category: Job-Seeking Status

### `#job_seeking_status:*` (3 values)

**Active:** Currently seeking employment
- Interviewing, applying, open to opportunities
- Using Careerspan product (or should be)
- Track: Interview progress, Careerspan engagement, placement outcome

**Inactive:** Not seeking employment
- Happily employed, not in market
- Not using Careerspan for job search
- May still use Careerspan for other reasons (networking, advisory)

**Placed:** Recently placed (successful outcome)
- Got new job (via Careerspan or other means)
- Track: Placement source, satisfaction, testimonial opportunity
- Transition to inactive after 90 days

---

## Real-World Examples

### Example 1: Kim Wilkes (Community Leader, Job Seeking)

**Old approach (dual stakeholder):**
```
#stakeholder:community (PRIMARY)
#stakeholder:job_seeker (SECONDARY)
#relationship:active
#priority:critical
```

**New approach (status dimension):**
```
#stakeholder:community
#job_seeking_status:active
#relationship:active
#priority:critical
```

**Clarity improvement:**
- WHO: Community leader (strategic network access)
- STATE: Currently job seeking (using Careerspan product)
- Clean separation, no "primary/secondary" confusion

---

### Example 2: Advisor Who Gets Laid Off (Hypothetical)

**Scenario:** Alex Caveny (advisor) loses job, starts job seeking

**Old approach:** What stakeholder type? Advisor or job_seeker?
- Confusing: He WAS advisor, now IS job seeker?
- Do we change stakeholder type? Lose advisory context?

**New approach:** Simple status update
```
#stakeholder:advisor (unchanged - still provides advisory value)
#job_seeking_status:active (NEW - now also job seeking)
#relationship:active
#priority:critical
```

**Clarity:** He's STILL an advisor AND happens to be job seeking (both true simultaneously)

---

### Example 3: Customer Success Story (Future)

**Scenario:** Careerspan customer gets placed, writes testimonial

**Tags track full lifecycle:**
```
Week 1:
#stakeholder:customer
#job_seeking_status:active
#priority:critical

Week 8 (placed via Careerspan):
#stakeholder:customer
#job_seeking_status:placed
#priority:critical

Week 20 (happily employed, advocates for Careerspan):
#stakeholder:customer
#job_seeking_status:inactive
#priority:critical
(Could also add #stakeholder:advisor if they provide insights)
```

**Product tracking:** Correlate `job_seeking_status:placed` with Careerspan usage → measure success rate

---

## System Impact

### Taxonomy Simplification
- **Removed:** `#stakeholder:job_seeker` from stakeholder types (9 types now, was 10)
- **Added:** `#job_seeking_status:*` category (3 values)
- **Result:** Cleaner, more logical structure

### Dual Classification Eliminated
- **Before:** Needed "primary" and "secondary" stakeholder logic
- **After:** Single stakeholder type + orthogonal statuses
- **Code simplification:** No dual tag special cases

### Lifecycle Tracking Enabled
- Track employment transitions: active → placed → inactive
- Measure Careerspan placement success
- Identify testimonial opportunities (placed contacts)
- Correlate product usage with outcomes

---

## Configuration Updates Needed

### 1. Update `tag_taxonomy.json`
```json
{
  "stakeholder": {
    "tags": {
      // Remove "job_seeker" from here
    }
  },
  "job_seeking_status": {
    "prefix": "#job_seeking_status:",
    "description": "Current employment seeking state",
    "n5_only": true,
    "tags": {
      "active": "Currently seeking employment",
      "inactive": "Not seeking employment",
      "placed": "Recently placed (successful outcome)"
    }
  }
}
```

### 2. Update `stakeholder_rules.json`
```json
{
  "priority_auto_inheritance": {
    "investor": "critical",
    "advisor": "critical",
    "customer": "critical",
    // Remove "job_seeker" from here
    "community": "non-critical",
    "prospect": "non-critical"
  }
}
```

### 3. Update `pattern_analyzer.py`
- Remove job_seeker detection from stakeholder type inference
- Add job-seeking status detection (email keywords: "interview", "job search", "using careerspan")
- Suggest `#job_seeking_status:active` if signals present

---

## Migration Plan

### Existing Profiles (Updated)
**Kim Wilkes:** ✅ Already updated to use `#job_seeking_status:active`

**Future contacts:**
- All new profiles use new structure
- Old "job_seeker" stakeholder type deprecated
- Pattern analyzer suggests job-seeking status separately

### Historical Profiles (When Reactivated)
- If old profile has `#stakeholder:job_seeker` → Convert to `#job_seeking_status:active` + infer real stakeholder type
- Example: "Jane Doe - job seeker" reactivates → Analyze context → Actually community leader → `#stakeholder:community` + `#job_seeking_status:active`

---

## Benefits Summary

### 1. Cleaner Taxonomy
- Type (WHO they are) vs. State (WHAT they're doing)
- Orthogonal dimensions, no overlap
- 9 stakeholder types instead of 10 with confusing dual role

### 2. Better Product Tracking
- `#job_seeking_status:active` = using Careerspan
- `#job_seeking_status:placed` = successful outcome
- `#job_seeking_status:inactive` = not using product
- Clear product usage signal

### 3. Lifecycle Visibility
- Track employment transitions over time
- Identify successful placements
- Measure Careerspan impact
- Testimonial pipeline (placed contacts)

### 4. Universal Applicability
- Investors can be job seeking (rare but possible)
- Advisors can be job seeking (Alex hypothetical)
- Community leaders can be job seeking (Kim actual)
- Customers can be job seeking (common)
- No stakeholder type is excluded

### 5. Simpler Code
- No dual classification logic
- No "primary/secondary" handling
- Straightforward tag combinations
- Easier to explain and understand

---

## Updated Tag Count

**Total tag categories:** 13 (was 12)
- Stakeholder types: 9 (was 10 with job_seeker)
- Job-seeking status: 3 (NEW category)
- All others: Unchanged

**Taxonomy version:** 3.2.0 (job-seeking status refactoring)

---

## Validation

**Real-world test:** Kim Wilkes profile
- ✅ Community stakeholder (WHO)
- ✅ Job-seeking status active (WHAT)
- ✅ Clean, clear, no confusion
- ✅ Tracks both partnership value AND product usage

**Hypothetical test:** What if Kim gets placed?
- ✅ Update: `#job_seeking_status:active` → `#job_seeking_status:placed`
- ✅ Keep: `#stakeholder:community` (unchanged)
- ✅ Result: Still community stakeholder, now successfully placed (testimonial opportunity!)

---

**Status:** Taxonomy refinement complete, Kim's profile updated, ready to update config files

**Next:** Update all config files to reflect job-seeking status change
