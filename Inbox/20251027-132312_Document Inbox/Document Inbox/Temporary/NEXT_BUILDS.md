# Next Builds: Priority Queue

**Phase 1:** ✅ COMPLETE  
**Current State:** Thread titling + auto-promotion working  
**Decision:** What to build next?

---

## High-Value Builds (Immediate Impact)

### 1. **Portfolio Generator** ⭐ RECOMMENDED
**Impact:** Makes Documents/Archive actually useful  
**Effort:** 1-2 hours  
**Value:** High (showcase-ready portfolio page)

**What it does:**
- Scans Documents/Archive/
- Generates `Documents/PORTFOLIO.md` with:
  - Table of contents by date/type
  - One-line summaries per archive
  - Links to archives
  - Optional: Screenshots, stats
- Auto-updates on promotion

**Why now:**
- You have ~8 archives already in Documents/Archive
- Makes the curated collection browsable
- Client-ready showcase
- Low effort, high visibility

**Output example:**
```markdown
# Portfolio: Significant Work

## 2025-10-26
- **Worker 6: Arsenal Dashboard** - Real-time productivity tracking web app
- **RPI Calculator Implementation** - Performance index automation

## 2025-10-25
- **N5 Waitlist Site** - Landing page for product launch
...
```

---

### 2. **Manual Promotion Command** `/archive-promote`
**Impact:** Backfill portfolio with past work  
**Effort:** 1 hour  
**Value:** Medium-High (one-time utility)

**What it does:**
```bash
# Promote any past conversation
/archive-promote --convo-id con_XYZ

# Batch promote by tag
/archive-promote --tag worker --since 2025-10-01

# Preview before promoting
/archive-promote --dry-run --tag deliverable
```

**Why now:**
- Enable backfilling Documents/Archive with past significant work
- Fix misclassifications (promote forgotten archives)
- One-time tool, but unlocks portfolio quality

**Use case:**
- "I built 5 workers in October, let me promote them all"
- "That thread was actually significant, promote it retroactively"

---

## Medium-Value Builds (Smart Automation)

### 3. **Artifact-Based Detection** (Rule 4)
**Impact:** Reduce manual tagging from 15% → 5%  
**Effort:** 2-3 hours  
**Value:** Medium (automation improvement)

**Detection signals:**
- File count (>5 artifacts)
- Code volume (>500 LOC)
- Directory creation (new N5 commands, scripts)
- File types (presence of .py, .md, .sh)

**Auto-tag candidates:**
```python
if artifacts > 5 or code_lines > 500:
    suggest_tag("#deliverable")
```

**Why later:**
- Current system works (tagging is lightweight)
- Optimization, not critical path
- Can wait until promotion rate data available

---

### 4. **Duration/Complexity Detection** (Rule 5)
**Impact:** Catch long planning/strategy threads  
**Effort:** 1-2 hours  
**Value:** Medium (edge case handling)

**Detection signals:**
- Conversation duration >2 hours
- Message count >50
- Multi-phase work (detected in AAR)
- Session state complexity

**Why later:**
- Fewer than Rule 4 (rare long threads)
- Worker tagging covers most cases
- Nice-to-have, not must-have

---

## Low-Value Builds (Polish)

### 5. **Reclassification Tools**
**Impact:** Fix rare mistakes  
**Effort:** 1-2 hours  
**Value:** Low (infrequent need)

**Features:**
- Detect wrongly promoted archives
- Suggest demotions
- Confidence scoring

**Why last:**
- Low frequency (mistakes rare with good rules)
- Manual fix easy (just delete from Documents/Archive)
- Optimization of edge case

---

## My Recommendation

**Build Portfolio Generator next** (Option 1)

**Reasoning:**
1. **Immediate value** - Makes your curated archive useful NOW
2. **Client-ready** - Shareable portfolio page in 2 hours
3. **Low effort** - Simple scan + markdown generation
4. **Completes Phase 1** - Two-tier system is only valuable if tier 2 is browsable
5. **Motivating** - Seeing your work showcased is energizing

**Alternative:** Build manual promotion command (Option 2) FIRST if you want to backfill portfolio before generating the page.

**Optimal sequence:**
1. Manual promotion command (1 hr) → backfill portfolio
2. Portfolio generator (2 hrs) → make it browsable
3. Test with real usage for 1-2 weeks
4. Add smart detection (Rules 4-5) if promotion rate too low

---

## Decision Framework

**Choose Portfolio Generator if:**
- You want immediate showcase value
- Current archives are good enough
- You want to see the system in action

**Choose Manual Promotion if:**
- You want to backfill past significant work first
- You have 5-10 past conversations worth showcasing
- Portfolio completeness matters more than having it now

**Choose Smart Detection if:**
- You're forgetting to tag conversations
- Promotion rate <10% (too few promotions)
- You want maximum automation

---

## What Would I Build?

**My pick: Portfolio Generator** (Option 1)

Why? Because you already have 8+ archives in Documents/Archive. Making them browsable NOW gives immediate ROI. Manual promotion can come next week when you want to backfill.

**Estimated timeline:**
- Portfolio Generator: Tonight (1-2 hours)
- Manual Promotion: This weekend (1 hour)
- Smart Detection: Next week (2-3 hours)

**Total Phase 2:** ~5 hours spread over 1 week

---

**Your call!** What sounds most valuable to you right now?

