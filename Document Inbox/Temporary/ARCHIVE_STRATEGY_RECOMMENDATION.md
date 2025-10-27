# Archive Strategy: Decision Framework

**Date:** 2025-10-26  
**Decision:** Archive location and workflow design  
**Analyzed Options:** A, B, C + Variations

---

## TL;DR Recommendation

**🎯 Modified Option A: Two-Tier with Clear Automation Rules**

**Why:** Balances automation, curation, and SSOT while matching your current mental model and use cases.

---

## Key Factors for This Decision

### 1. Your Use Cases (Priority Order)

**Primary:**
- **Resume/continue work** - "What did we discuss about X?" → Need searchable AAR
- **Debug/learn** - "How did I solve Y last time?" → Need complete history
- **Worker orchestration** - Track spawned workers → Need structured metadata

**Secondary:**
- **Portfolio/showcase** - "Here's what I've built" → Need curated view
- **Client demos** - "Let me show you..." → Need polished presentation
- **Timeline** - "What happened when?" → Need chronological completeness

**Tertiary:**
- **Historical analysis** - Patterns, growth, system evolution → Need comprehensive data

### 2. Your Context

**Volume:**
- Multiple workers/day (high volume)
- Research sessions (medium volume)
- Planning conversations (medium volume)
- **Estimated:** 5-10 conversation closes/week = 250-500/year

**Workflow Preferences:**
- Strong automation bias (P15: Complete Before Claiming)
- Dislikes interruptions/prompts (conversation flow)
- Values consistency (P2: SSOT)
- Appreciates clear rules over case-by-case decisions

**Career Context:**
- Career coach + entrepreneur = need showcase-worthy portfolio
- Building in public = need polished artifacts for sharing
- Non-technical background = need human-readable organization

### 3. System Principles Applied

- **P2 (SSOT):** Single source of truth for all data
- **P1 (Human-Readable):** File structure should make sense to humans
- **P8 (Minimal Context):** Don't duplicate; reference
- **P20 (Modular):** Archive system should be independent component
- **P22 (Right Tool):** Different storage for different access patterns

---

## Option Analysis

### Option A: Two-Tier System
**Score: 8.5/10** ⭐

```
N5/logs/threads/           → Complete archive (SSOT)
Documents/Archive/         → Curated showcase (human-browsable)
```

**Pros:**
- ✅ Matches current mental model (already doing this)
- ✅ Clear separation of concerns (complete vs. curated)
- ✅ Human-browsable portfolio in Documents/
- ✅ N5/logs can be massive without clutter
- ✅ Can build unified search across both
- ✅ Automation-friendly with clear rules

**Cons:**
- ⚠️ Two locations to maintain (but automation handles this)
- ⚠️ Need clear classification rules (solvable)
- ⚠️ Potential for inconsistency (mitigated by automation)

**Best For:** Your use case (high volume + portfolio needs)

---

### Option B: Single Unified System
**Score: 7/10**

```
N5/logs/threads/           → Everything (SSOT)
  ├── metadata tags for "showcase"
  └── search/filter for important items
```

**Pros:**
- ✅ True SSOT (P2)
- ✅ No classification decisions
- ✅ Scales perfectly
- ✅ Easier unified search

**Cons:**
- ❌ No human-curated portfolio view
- ❌ Harder to browse casually ("show me my best work")
- ❌ Mixing routine + showcase dilutes impact
- ❌ Documents/Archive feels "wrong" to leave empty
- ❌ Harder to share specific projects (deep paths)

**Best For:** Pure research/learning (no showcase needs)

---

### Option C: Prompt-Based
**Score: 4/10**

```
At conversation-end: "Is this a major deliverable? (y/N)"
```

**Pros:**
- ✅ User maintains control
- ✅ Flexible for edge cases

**Cons:**
- ❌ Decision fatigue (5-10x/week)
- ❌ Interrupts flow at conversation close
- ❌ Inconsistent classifications guaranteed
- ❌ You'll skip/rush decisions
- ❌ Can't automate later
- ❌ Violates preference for automation

**Best For:** Low-volume users who want manual control

---

## Recommended Solution: Modified Option A

### Core Design

**1. Single Source of Truth:** N5/logs/threads/
- ALL conversations archived here (no exceptions)
- Standard AAR structure (v2.2)
- Automated via conversation-end
- Searchable, complete, chronological

**2. Curated Showcase:** Documents/Archive/
- SUBSET of N5/logs/threads
- Enhanced documentation (README, completion reports)
- Human-browsable, portfolio-ready
- Auto-promoted based on rules

**3. Clear Automation Rules:**

```python
# Auto-promote to Documents/Archive if ANY:
- Conversation tagged #worker
- Deliverable registry entry exists  
- Duration > 2 hours + significant artifacts (>10 files or >1MB)
- Manual promotion via /archive-promote command
```

### Implementation

**Phase 1: Core Flow (conversation-end)**
```
1. Generate AAR → N5/logs/threads/YYYY-MM-DD-HHMM_title_ID/
2. Generate thread title (FIXED)
3. Check promotion rules
4. IF promoted: Copy enhanced to Documents/Archive/YYYY-MM-DD-ProjectName/
5. Update registry
```

**Phase 2: Worker Flow (worker-complete)**
```
1. Validate worker objectives
2. Generate completion report
3. Run conversation-end (creates AAR in N5/logs/threads)
4. Auto-promote to Documents/Archive (worker rule)
5. Update orchestrator
```

**Phase 3: Registry (N5/.state/archive_registry.jsonl)**
```jsonl
{"id": "abc123", "date": "2025-10-26", "title": "Worker6-Dashboard", "location": "both", "type": "worker", "tags": ["web", "productivity"], "duration_hours": 0.25}
```

### File Structure

**Standard Archive (N5/logs/threads):**
```
2025-10-26-1549_Oct-26-✅-RPI-Calculator_8427/
├── aar-2025-10-26.json        # Machine-readable
├── aar-2025-10-26.md          # Human-readable
└── artifacts/                  # Conversation files
    ├── script.py
    └── notes.md
```

**Showcase Archive (Documents/Archive):**
```
2025-10-26-Worker6-Dashboard/
├── README.md                   # Enhanced, human-friendly
├── COMPLETION_REPORT.md        # Worker-specific
├── artifacts/                  # Key deliverables only
│   └── dashboard-screenshot.png
└── .archive_metadata.json      # Links back to N5/logs/threads
```

---

## Why This Solution Wins

### 1. Matches Your Behavior
- You're already doing two-tier informally
- Formalizing = less cognitive load
- Automation handles 95% of decisions

### 2. Solves Your Use Cases

| Use Case | Solution |
|----------|----------|
| Resume work | AAR in N5/logs (always there) |
| Showcase | Documents/Archive (curated) |
| Debug | Search both (unified command) |
| Portfolio | Documents/Archive (human-browsable) |
| Timeline | N5/logs (chronological, complete) |
| Worker tracking | Registry + dual archives |

### 3. Scales Well
- **10 conversations:** Both locations manageable
- **100 conversations:** N5/logs comprehensive, Documents curated (15-20 items)
- **1000 conversations:** N5/logs searchable, Documents curated (50-100 items)

### 4. Low Maintenance
- Default: Automated
- Exception: Rule-based promotion (automated)
- Manual override: Available but rare
- Future: AI can reclassify

### 5. SSOT Compliant
- N5/logs/threads = source of truth
- Documents/Archive = view/index
- No data duplication (artifacts copied, not moved)
- Registry tracks relationship

---

## Alternative Considered: Symbolic Links

**Idea:** Everything in N5/logs, symlinks in Documents/Archive

**Rejected Because:**
- Breaks across sync tools (Syncthing, Drive, Dropbox)
- Not Windows-compatible
- Harder to share (links break)
- Confusing for non-technical users (you)
- File protections complicate this

**Actual Copy** is better:
- Works everywhere
- Sharable
- Clear ownership
- Minor duplication acceptable (artifacts ~1-5MB each)

---

## Implementation Priority

### Must Have (Phase 1)
1. ✅ Fix thread titling (DONE)
2. ⬜ Document promotion rules in N5/prefs
3. ⬜ Update conversation-end to check rules
4. ⬜ Auto-copy to Documents/Archive when triggered

### Should Have (Phase 2)
5. ⬜ Create worker-complete command
6. ⬜ Build archive registry
7. ⬜ Add /archive-promote command
8. ⬜ Enhanced README generation

### Nice to Have (Phase 3)
9. ⬜ Unified archive search (/archive-search)
10. ⬜ Archive analytics (time spent, outcomes)
11. ⬜ Portfolio export (for website/resume)
12. ⬜ AI reclassification (review past, suggest promotions)

---

## Decision Checklist

Before implementing, confirm:

- [x] Matches current mental model?  
- [x] Low cognitive load (automated)?  
- [x] SSOT maintained?  
- [x] Scales to 500+ conversations?  
- [x] Portfolio use case solved?  
- [x] Worker workflow clear?  
- [x] Search across both locations possible?  
- [x] Can change mind later (reclassify)?  
- [x] Human-readable structure?  
- [x] Principles-compliant?

**All checks passed ✅**

---

## Risk Analysis

### Low Risk
- Data loss: No (SSOT in N5/logs always)
- Duplication: Minor (artifacts copied, ~1-5MB)
- Inconsistency: Low (automation + rules)
- Maintainability: High (clear structure)

### Medium Risk
- Rule complexity: Need clear thresholds (mitigated by starting simple)
- Edge cases: Some conversations ambiguous (manual override available)

### Mitigation
- Start with conservative promotion rules (under-promote vs. over-promote)
- Add /archive-promote for manual override
- Review promoted items monthly (first 3 months)
- Adjust rules based on patterns

---

## Estimated Effort

**Phase 1 (Core):** 2-3 hours
- Update conversation-end.py (promotion logic)
- Document rules
- Test with recent conversations

**Phase 2 (Worker):** 3-4 hours
- Create worker-complete command
- Build registry system
- Integration testing

**Phase 3 (Polish):** 4-6 hours
- Unified search
- Enhanced README generation
- Portfolio export

**Total:** 9-13 hours over 2-3 sessions

---

## Final Recommendation

**Go with Modified Option A: Two-Tier with Automation**

**Why:** It's the goldilocks solution - not too simple (Option B loses curation), not too complex (Option C adds friction), just right for your volume, use cases, and workflow preferences.

**Next Step:** Confirm promotion rules, then implement Phase 1.

**Confidence:** 95% - This matches your behavior, principles, and scales well.

