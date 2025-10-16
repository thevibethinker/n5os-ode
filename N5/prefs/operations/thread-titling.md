# Thread Titling System

**Module:** Operations  
**Version:** 1.0.0  
**Date:** 2025-10-16

---

## Purpose

Defines the auto-generation system for thread titles with emoji prefixes, enabling consistent, scannable thread names that indicate status and linkage at a glance.

---

## Title Format

```
{emoji} {Entity} {Action/Type} {optional: #N}
```

**Structure:**
- **Entity-first** (noun): The primary subject (CRM, Email System, GTM, N5, etc.)
- **Action/descriptor**: Refactor, Setup, Discussion, Fix, Build, etc.
- **Sequence number**: #1, #2, #3 (for linked threads)

**Length constraints:**
- Target: 18-30 characters
- Hard limit: 35 characters (before UI truncation)
- Reason: Collapsed sidebar shows ~24 chars after `Oct 14 | 🔗 `

**Examples:**
- ✅ `✅ CRM Refactoring #1` (19 chars) ← Perfect
- ✅ `🔗 Email Scanner Discussion` (26 chars) ← Good
- ✅ `✅ Vibe Builder Persona Setup` (26 chars) ← Good
- ⚠️ `✅ Log File Cleanup and Implementation Discussion` (48 chars) ← Too long, truncates

## Title Length Guidelines

### UI Constraints
**Collapsed sidebar (V's normal mode):**
```
Oct 14 | 🔗 CRM Refactoring #1
         └─ 9 + 2 + 24 = 35 chars visible
```

**Expanded sidebar:**
- Full titles visible (~80+ chars)
- But optimize for collapsed (24 char window)

### Length Rules
1. **Ideal: 18-30 chars** - Fits perfectly in collapsed view
2. **Max: 35 chars** - Shows without truncation
3. **Over 35 chars** - Gets truncated with `...`

### Optimization Tips
- Front-load key noun (entity)
- Use short action words (Setup vs Configuration, Fix vs Troubleshooting)
- Save details for thread content, not title
- Sequential numbers (#1, #2) save space vs (Part 1, Part 2)

**Good:**
- "CRM Refactor #3" (16 chars)
- "Email System Setup" (18 chars)
- "GTM Integration Discussion" (26 chars)

**Too long:**
- "Refactoring the CRM System Components" (37 chars) ← Truncates
- "Discussion About Email Scanner Implementation" (45 chars) ← Truncates badly

---

## Emoji Legend

### Status Emojis (Auto-Selected at Thread End)

| Emoji | Meaning | When to Use |
|-------|---------|-------------|
| ✅ | Completed | Thread objectives fully achieved, no errors |
| ❌ | Failed/Error | Thread ended with unresolved errors or failures |
| 🚧 | In Progress | Thread paused mid-work, to be resumed |
| 🔗 | Linked/Sequential | Part of a series (add #N for sequence) |
| 📰 | Research/Articles | Knowledge gathering, article processing, insights |
| 🎯 | Strategy/Planning | Strategic work, GTM, positioning, planning |
| 📝 | Documentation | Pure documentation work |
| 🔧 | System/Infrastructure | N5 system improvements, infrastructure |
| 🐛 | Bug Fix | Debugging, troubleshooting, fixing issues |
| 💬 | Communication | Email work, message drafting, outreach |

**Priority order for auto-selection:**
1. Check for errors/failures → ❌
2. Check for explicit pause/resume context → 🚧
3. Check for link keywords → 🔗 (with #N if sequential)
4. Check primary category → assign category emoji
5. Default to ✅ if complete without errors

## Emoji Selection Reference

**Source of Truth:** `file 'N5/config/emoji-legend.json'`  
**Full Documentation:** `file 'N5/prefs/emoji-legend.md'`

The N5 system uses a centralized emoji legend maintained in JSON format. This ensures consistent emoji usage across threads, lists, commands, and all system components.

### Quick Reference (Thread-Specific)

**Status Emojis (Highest Priority):**
- ✅ **Completed** - Thread objectives fully achieved, no errors
- ❌ **Failed** - Thread ended with unresolved errors (Priority: 100)
- 🚧 **In Progress** - Thread paused mid-work, to be resumed
- 🔗 **Linked** - Part of a series (use with #N for sequence)

**Common Content Types:**
- 📰 **Research** - Articles, insights, knowledge gathering
- 🎯 **Strategy** - GTM, planning, positioning
- 📝 **Documentation** - Writing, guides, README files
- 🔧 **System** - N5 improvements, infrastructure, tooling
- 🐛 **Bug Fix** - Debugging, troubleshooting with resolution
- 💬 **Communication** - Email, messaging, outreach

**Full Legend:** See `file 'N5/prefs/emoji-legend.md'` for 25+ emojis with detection rules, keywords, and priority levels.

### Auto-Selection Priority

1. **Failures** (Priority: 100) → ❌
2. **In Progress** (Priority: 80) → 🚧  
3. **Sequential/Linked** (Priority: 70) → 🔗
4. **Bug Fixes** (Priority: 60) → 🐛
5. **Security** (Priority: 50) → 🔒
6. **Deployment** (Priority: 50) → 🚀
7. **Content Types** (Priority: 40) → 📰 🎯 📝 🔧 💬 etc.
8. **Default** (Priority: 10) → ✅

**Algorithm:** Check each priority tier sequentially. First match wins. If no matches, default to ✅ for complete threads.

---

## Detection Rules for Auto-Generation

### Failure Detection (❌)
**Triggers:**
- Unhandled exceptions in logs
- "error", "failed", "unsuccessful" in final messages
- Exit codes != 0
- Critical validation failures

### In-Progress Detection (🚧)
**Triggers:**
- User says: "pause", "continue later", "resume this"
- Incomplete objectives in AAR
- Status field = "in-progress"

### Sequential/Linked Detection (🔗)
**Triggers:**
- Thread title contains: "#N", "Phase N", "Part N", "v1.N"
- AAR mentions "continuation of", "follows thread", "previous thread"
- User explicitly mentions linking threads

**Sequential numbering:**
- Extract existing number from context
- Increment if clear continuation
- Add "#1" if starting new series

### Category Detection (All Others)
**Keywords by category:**

**📰 Research/Articles:**
- "article", "research", "insights", "knowledge", "reading", "analysis"

**🎯 Strategy/Planning:**
- "GTM", "strategy", "positioning", "planning", "roadmap", "vision"

**📝 Documentation:**
- "document", "write", "draft", "README", "guide", "notes"

**🔧 System/Infrastructure:**
- "N5", "system", "infrastructure", "commands", "scripts", "workflow"

**🐛 Bug Fix:**
- "bug", "fix", "debug", "troubleshoot", "issue", "error" (with resolution)

**💬 Communication:**
- "email", "message", "outreach", "communication", "response", "follow-up"

---

## Title Generation Algorithm

### Phase 1: Extract Core Topic
1. Analyze AAR title/description
2. Extract main entities (CRM, Meeting Digest, Email Scanner, etc.)
3. Extract action verbs (Implementation, Consolidation, Enhancement, etc.)
4. Combine: `{Entity} {Action}`

### Phase 2: Select Emoji
1. Run detection rules in priority order (failures → progress → links → category)
2. Select first matching emoji
3. Default to ✅ if no matches and status = complete

### Phase 3: Handle Sequential Numbering
1. Check for sequence indicators
2. If 🔗 selected and sequence detected:
   - Extract number from context
   - Append `#N` to title
3. If starting new series, append `#1`

### Phase 4: Format Title
1. Convert to Title Case (capitalize major words)
2. Remove redundant words ("Thread", "Conversation", "Export")
3. Cap at ~50 characters (abbreviate if needed)
4. Construct: `{emoji} {Formatted-Title}`

### Phase 5: User Review
1. Present generated title
2. Show detection reasoning
3. Offer options:
   - Accept as-is (Y)
   - Edit/modify (e)
   - Manual entry (m)

---

## Examples with Detection Reasoning

### Example 1: Completed Implementation
**Input AAR:**
- Title: "CRM Consolidation Phase 3 Complete"
- Status: Complete
- Artifacts: 5 scripts, integration tests passed
- No errors

**Detection:**
- ❌? No failures → Skip
- 🚧? Status = complete → Skip
- 🔗? No sequence indicators → Skip
- Category: "CRM", "system" keywords → 🔧
- BUT: "Complete" + no errors → ✅ (override)

**Generated Title:** `✅ CRM Consolidation Phase 3 Complete`

---

### Example 2: Sequential Work
**Input AAR:**
- Title: "Email Scanner Implementation continued from con_abc123"
- Status: Complete
- Previous thread: "Email Scanner Implementation #1"

**Detection:**
- ❌? No failures → Skip
- 🚧? Status = complete → Skip
- 🔗? "continued from", previous has "#1" → 🔗 #2
- Sequential: Found "#1" in previous → Increment to "#2"

**Generated Title:** `🔗 Email Scanner Implementation #2`

---

### Example 3: Research Thread
**Input AAR:**
- Title: "Article processing and insights extraction"
- Status: Complete
- Artifacts: 12 articles, knowledge entries

**Detection:**
- ❌? No failures → Skip
- 🚧? Status = complete → Skip
- 🔗? No sequence → Skip
- Category: "article", "insights" → 📰

**Generated Title:** `📰 Articles Insights and Knowledge Base`

---

### Example 4: Failed Execution
**Input AAR:**
- Title: "Python script dry-run testing"
- Status: Failed
- Errors: UnhandledPromiseRejection, exit code 1

**Detection:**
- ❌? Unhandled error, exit code 1 → ❌

**Generated Title:** `❌ Python Script Dry-Run Failed`

---

### Example 5: Paused Work
**Input AAR:**
- Title: "Meeting Digest System Enhancement"
- Status: In Progress
- User: "Let's pause here and resume tomorrow"

**Detection:**
- ❌? No critical failures → Skip
- 🚧? Status = in-progress, "pause" keyword → 🚧

**Generated Title:** `🚧 Meeting Digest System Enhancement`

---

## Integration with thread-export

### Invocation Options

**Standard (with title generation):**
```bash
N5: run thread-export --auto
```

**Skip title generation:**
```bash
N5: run thread-export --auto --no-title-gen
```

**Override title manually:**
```bash
N5: run thread-export --auto --title "Custom Title"
```

---

## Edge Cases & Fallbacks

### No Clear Category
**Fallback:** Default to ✅ (completed) or 🔗 (if linked)

### Multiple Categories Detected
**Priority:** Use highest-priority category:
1. ❌ Failures (always highest)
2. 🚧 In Progress
3. 🔗 Sequential
4. Category-specific emojis
5. ✅ Completed (default)

### Title Too Long
**Strategy:**
- Abbreviate middle words ("Implementation" → "Impl")
- Remove articles (a, an, the)
- Use acronyms for known terms (CRM, GTM, AAR)
- Max: 50 characters

### Ambiguous Sequences
**Strategy:**
- If unsure about number, omit #N
- User can add manually during review
- Prefer explicit over incorrect

---

## Future Enhancements

### Phase 2: Thread Pause Function
Create `thread-pause` command that:
1. Runs AAR generation
2. Auto-generates title with 🚧 emoji
3. Saves partial state
4. Enables clean resumption

### Phase 3: Mid-Thread Title Suggestions
Add command to generate title suggestions during active threads:
```bash
N5: suggest thread title
```

### Phase 4: Retroactive Title Cleanup
Script to scan existing threads and suggest title improvements:
```bash
N5: run thread-retitle --scan --dry-run
```

---

## Related Documents

- `file 'N5/commands/thread-export.md'` - Thread export command
- `file 'N5/scripts/n5_thread_export.py'` - Export script implementation
- `file 'N5/prefs/operations/conversation-end.md'` - Conversation end workflow
- `file 'N5/prefs/naming-conventions.md'` - General naming rules

---

## Version History

**1.0.0** (2025-10-16)
- Initial thread titling system
- Emoji legend with 10 status/category emojis
- Detection rules and priority algorithm
- Integration spec with thread-export
- Examples and edge case handling
