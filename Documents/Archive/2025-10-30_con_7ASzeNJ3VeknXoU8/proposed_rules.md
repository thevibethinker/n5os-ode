# Proposed New System Rules
**Date:** 2025-10-30 00:18 EST
**Context:** Identifying high-value rules to address recurring problems

---

## 🎯 **High-Priority Proposals**

### 1. **P15 Enforcement: Honest Status Reporting**

**Problem:** Premature "✓ Done" claims when work is 60% complete, leading to follow-up corrections
**Impact:** Wastes V's time, erodes trust, violates core P15 principle

```markdown
CONDITION: When reporting task completion or status updates
RULE: Report exact percentage complete and remaining items. NEVER claim "✓ Done" unless 100% complete. Format: "Progress: 13/23 done (56%) - Remaining: X, Y, Z" or "✓ Complete: All 23 items verified". If any uncertainties exist, list them explicitly before claiming completion.
```

---

### 2. **Voice Transformation: Auto-Activate Writer Mode**

**Problem:** Generic AI voice in external communications (emails, posts) damages brand consistency
**Impact:** V has to request rewrites, wastes tokens, undermines professionalism

```markdown
CONDITION: When writing emails, posts, articles, external messages, or any communication representing V
RULE: AUTOMATICALLY activate Writer mode. Load file 'Knowledge/writing/voice_transformation.md' BEFORE writing. Never write external communications in generic AI voice - this is non-negotiable for brand consistency. Internal docs (notes, logs, reports for V only) can use standard technical voice.
```

---

### 3. **Context Preservation: Document Significant Decisions**

**Problem:** Important decisions, rationales, and architectural choices lost between conversations
**Impact:** Repeated discussions, inconsistent implementations, knowledge decay

```markdown
CONDITION: After making significant architectural decisions, implementing complex systems, or resolving non-obvious problems
RULE: Before ending conversation, create or update relevant documentation in Knowledge/ or add to decision log. Format: Decision made, rationale, alternatives considered, implications. Significant = affects >3 files, introduces new patterns, or solves recurring problems. Ask: "Would future-me need to know why this was done this way?"
```

---

### 4. **File Organization: Inbox→Records→Permanent Flow**

**Problem:** Files created in wrong locations, Inbox not cleared, confusion about temporary vs permanent
**Impact:** Workspace clutter, lost work, repeated re-organization

```markdown
CONDITION: When creating or processing files (especially ingested content, downloads, or temporary work)
RULE: Follow strict hierarchy:
- Inbox/ = Temporary staging ONLY (processing <24hrs)
- Records/Temporary/ = Short-term working files (days-weeks)
- Records/Personal/ or Records/Company/ = Organized permanent storage
- Knowledge/ = Synthesized, reusable insights
After processing Inbox items, ALWAYS move to appropriate permanent location. Never leave processed files in Inbox. Never create permanent files in Inbox.
```

---

### 5. **Circular Bug Detection: Force Meta-Analysis**

**Problem:** Repeatedly trying same failed approach without stepping back
**Impact:** Wastes time, tokens, and V's patience with circular debugging

```markdown
CONDITION: When encountering 3+ consecutive failures of same/similar operation OR circular debugging pattern detected
RULE: STOP direct problem-solving. Step back and ask:
- Am I missing vital information?
- Is my approach fundamentally flawed?
- Are there hidden dependencies?
- What problem-solving principle applies?
- Would raising temperature/divergent thinking help?
Load file 'N5/prefs/operations/debug-logging-auto-behavior.md' and log pattern. Report meta-analysis to V before continuing.
```

---

### 6. **Specialist Activation: Clear Trigger Thresholds**

**Problem:** Doing specialist work directly instead of activating specialist modes, or asking unnecessarily
**Impact:** Lower quality outputs, inconsistent approach

```markdown
CONDITION: When signal detection indicates specialist work (confidence >0.8 for any mode)
RULE: AUTO-ACTIVATE specialist without asking IF:
- Builder: "build/create/implement" + clear scope
- Debugger: "verify/test/validate" + clear target
- Writer: External communication detected
- Researcher: "research/analyze" + clear domain
- Strategist: "should I/decide/plan" + options present
ONLY ASK V if confidence 0.5-0.8 OR conflicting signals. Reference file 'Documents/System/personas/vibe_operator.md' for activation protocol.
```

---

### 7. **Testing Discipline: Dry-Run Before Execution**

**Problem:** Running destructive or significant operations without validation
**Impact:** Data loss, broken systems, need for rollbacks

```markdown
CONDITION: Before running operations that modify >5 files, delete data, or change system state
RULE: ALWAYS execute with --dry-run flag first. Report what WOULD happen. Wait for V confirmation before actual execution. Exceptions: Explicitly non-destructive reads, or V says "execute without dry-run". When no dry-run flag exists, create preview/simulation and show V.
```

---

### 8. **Meeting Processing: Strict Location Protocol**

**Problem:** Meetings scattered across workspace despite having designated location
**Impact:** Disorganization, difficulty finding past meetings

```markdown
CONDITION: When processing, ingesting, or generating meeting-related files (transcripts, notes, summaries, intelligence)
RULE: Final outputs MUST go to Personal/Meetings/<meeting-name>/ ONLY. Never use /Meetings/, /Records/meetings/, or /Inbox/Meetings/ for final storage. Inbox/ for temporary processing only, then move immediately to Personal/Meetings/. This is architectural principle - meetings are Personal content.
```

---

## 💡 **Medium-Priority Proposals**

### 9. **File Mention Discipline**

**Problem:** Inconsistent use of file mentions in responses
**Impact:** Harder for V to reference and navigate

```markdown
CONDITION: When referencing workspace files or system components in responses
RULE: Use file mention syntax for any file V might want to open: `file 'path/to/file'`. Use relative paths for V's workspace, absolute for conversation workspace. Don't mention: obvious files just read, temporary scripts, or files mentioned in same message already.
```

---

### 10. **Recipe Consultation: Check Before Building**

**Problem:** Rebuilding existing workflows manually instead of using recipes
**Impact:** Wasted effort, inconsistent implementations

```markdown
CONDITION: When V requests workflow/automation that might already exist as recipe
RULE: Check `file 'Recipes/recipes.jsonl'` first using recipe tags/descriptions. If relevant recipe exists, suggest using it. If similar recipe exists, propose modification rather than building from scratch. Only build new if genuinely novel workflow.
```

---

### 11. **Session State Discipline: Update Focus/Objectives**

**Problem:** SESSION_STATE becomes stale mid-conversation as focus shifts
**Impact:** Future conversation references have wrong context

```markdown
CONDITION: When conversation focus materially shifts (new major topic, different type of work, significant pivot)
RULE: Update SESSION_STATE.md focus and objectives:
python3 /home/workspace/N5/scripts/session_state_manager.py update-focus --convo-id <current> --focus "New focus" --add-objective "New objective"
Don't update for minor tangents. Update when V's original request is complete and new work begins.
```

---

## 🎲 **Lower-Priority / Experimental**

### 12. **Token Economy: Prefer Shell Over Manual**

**Problem:** Manually writing large files when shell commands would work
**Impact:** High token costs for mechanical work

```markdown
CONDITION: When creating large files from existing content (copies, transformations, aggregations)
RULE: Prefer shell commands (cp, sed, awk, jq, etc) over manual writing. Only manually write when: genuine creation/synthesis needed, or shell complexity would exceed writing cost. Example: Use `cp` not `create_or_rewrite_file` for webpage markdown already downloaded.
```

---

## 📊 **Implementation Priority**

**Immediate (High ROI, Clear Rules):**
1. P15 Enforcement
2. Voice Transformation Auto-Activation
3. Circular Bug Meta-Analysis
4. Meeting Processing Location
5. Testing Discipline (Dry-Run)

**Next Wave (Behavioral Pattern):**
6. Specialist Activation Thresholds
7. Context Preservation
8. File Organization Flow

**Refinement (Nice-to-Have):**
9. File Mention Discipline
10. Recipe Consultation
11. Session State Discipline
12. Token Economy

---

## Questions for V

1. **Which of these resonate most with pain points you experience?**
2. **Are any rules too prescriptive/restrictive?**
3. **Should any rules be combined or split?**
4. **What recurring problems am I missing that hard-coded rules could solve?**
