# Design Decisions - Thread Titling System

**Date:** 2025-10-16  
**Thread:** con_lTIsBYYVApM9pBHm

---

## Key Design Decisions

### 1. Centralized Emoji Legend (SSOT)

**Decision:** Use JSON as single source of truth for all emoji meanings

**Rationale:**
- Apply P2 (SSOT) architectural principle
- Machine-readable for programmatic access
- Human-readable docs auto-generated from source
- Easy to extend without touching multiple files
- Consistent emoji usage across threads, lists, commands, files

**Alternatives Considered:**
- ❌ Hardcoded emoji meanings in each module → Would violate SSOT
- ❌ Markdown as primary source → Hard to parse programmatically
- ❌ Database storage → Overkill for 25 emojis

**Trade-offs:**
- ✅ Single update point
- ✅ Version controlled
- ⚠️ Requires sync script (minimal overhead)

---

### 2. Noun-First Title Structure

**Decision:** Format titles as `{Entity} {Action}` not `{Action} {Entity}`

**Rationale:**
- UI constraint: Only ~24 chars visible after date/emoji in collapsed sidebar
- Front-loading entity ensures scannable titles
- User feedback: "CRM Refactor" > "Refactoring CRM"
- Real-world testing with user's actual UI layout

**Examples:**
- ✅ "CRM Refactor #2" → See "CRM" immediately
- ❌ "Refactoring CRM System" → See "Refactoring", entity truncated

**Impact:** All title generation logic prioritizes noun extraction

---

### 3. Dual Title Generation

**Decision:** Generate both current thread title AND next thread title

**Rationale:**
- User workflow: Manually loads RESUME.md to start new thread
- Sequential numbering needs to be tracked (#1 → #2 → #3)
- Chain emoji (🔗) needs consistent application
- Reduces cognitive load on user

**Implementation:**
- Current title: Interactive selection or auto-select
- Next title: Auto-generate with incremented number
- Both stored in RESUME.md + terminal display

---

### 4. Priority-Based Emoji Selection

**Decision:** Use numeric priority (10-90) with algorithm: highest priority wins

**Rationale:**
- Failures (❌) should override everything → Priority 90
- Links (🔗) nearly as important → Priority 85
- Status (✅, 🚧) more important than category → Priority 60-80
- Categories (📰, 🎯) lowest priority → Priority 40

**Algorithm:**
```
1. Check failure keywords → ❌ (90)
2. Check linked/sequential → 🔗 (85)
3. Check in-progress → 🚧 (70)
4. Check bug fix → 🐛 (60)
5. Check categories → 📰 🎯 etc (40)
6. Default → ✅ (10)
```

**Trade-off:** Simple, deterministic, easy to understand and modify

---

### 5. Length Constraints

**Decision:** Target 18-30 chars, hard limit 35 chars

**Rationale:**
- Based on real UI measurements from user's screenshots
- `Oct 14 | 🔗 ` = 11 chars overhead
- Collapsed sidebar shows ~35 chars total
- Leaves ~24 chars for actual title
- Comfortable range: 18-30 chars

**Validation:** Analyzed user's existing thread names for patterns

---

### 6. Sequence Number Handling

**Decision:** No number = treat as #1, auto-increment from there

**Rationale:**
- User feedback: Starting a series should get #1 automatically
- Second thread gets #2, third gets #3, etc.
- User manually adds 🔗 emoji when intentionally creating sequence
- System preserves 🔗 for all continuations

**Edge Cases:**
- Single thread, no number → Don't add #1 (not a series yet)
- Thread with #5 → Next is #6 (respect existing numbering)

---

### 7. Integration Point

**Decision:** Integrate into thread-export script, not separate command

**Rationale:**
- Natural workflow: Title needed during export
- Avoid extra step (export, then title separately)
- Can use AAR data for smarter title generation
- Title available for directory naming immediately

**Alternative Considered:**
- ❌ Separate command to generate titles → Extra workflow step
- ❌ Post-export rename → Directory already created

---

### 8. Auto-Select in Automation Mode

**Decision:** When `--yes` flag used, auto-select first title option

**Rationale:**
- Automation mode = non-interactive
- First option is usually best (highest confidence)
- User can still manually rename if needed
- Falls back to timestamp only if generation fails completely

**Bug Fixed:** Initial implementation skipped generation entirely in --yes mode

---

### 9. Title Storage

**Decision:** Store next thread title in RESUME.md + terminal display

**Rationale:**
- RESUME.md: User manually loads this to continue work
- Terminal: Copy/paste convenience
- Thread metadata: Experimental (may not always work)

**Trade-off:** Not fully automated, but reliable

---

### 10. Modular Components

**Decision:** Separate title generator from export script

**Rationale:**
- Apply P20 (Modular Components)
- Reusable in other contexts (mid-thread suggestions, retroactive cleanup)
- Easier to test independently
- Clear interfaces and boundaries

**Structure:**
- `n5_title_generator.py` - Pure title generation logic
- `n5_thread_export.py` - Integration and workflow
- `emoji-legend.json` - Data source

---

## Rejected Alternatives

### 1. LLM-Based Title Generation

**Why Rejected:**
- I AM the LLM - no need for external API
- Would violate P16 (No Invented Limits)
- Added complexity and latency
- Less deterministic and controllable

### 2. Verb-First Title Structure

**Why Rejected:**
- User feedback: Noun-first is more scannable
- UI constraints favor front-loading important info
- Doesn't match user's existing naming patterns

### 3. Manual Emoji Selection

**Why Rejected:**
- Slows down workflow
- Inconsistent emoji usage
- User wanted automation
- Priority-based algorithm works well

### 4. Single Title Generation

**Why Rejected:**
- User explicitly wanted next thread title too
- Maintaining sequences manually is error-prone
- Dual generation fits workflow better

---

## Lessons Learned

### What Worked Well

✅ **Loading principles first** - Clear constraints from start  
✅ **Real UI measurements** - Designed for actual constraints  
✅ **User feedback loop** - Adjusted design based on workflow  
✅ **SSOT approach** - Single JSON source eliminated inconsistencies  
✅ **Modular design** - Easy to test and extend

### What Could Be Improved

⚠️ **Initial automation bug** - Should have tested --yes mode earlier  
⚠️ **Next title auto-load** - Experimental, may need refinement  
⚠️ **Entity extraction** - Could be more sophisticated (future ML?)

---

## Future Considerations

**Phase 3 Enhancements:**
- Mid-thread title suggestions
- Retroactive title cleanup for existing threads
- Better entity extraction with NLP
- Auto-load next title from metadata (if reliable)
- ML-based emoji selection (if patterns emerge)

**Scalability:**
- Current design handles 25-50 emojis comfortably
- Beyond 50: May need category hierarchy
- JSON → YAML if human editing becomes common
- Add schema validation if structure gets complex

---

**Conclusion:** Design balances automation, flexibility, and user control while respecting architectural principles and real-world constraints.

---

*Archived: 2025-10-16 02:56 ET*
