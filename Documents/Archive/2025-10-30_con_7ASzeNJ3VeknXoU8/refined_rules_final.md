# Refined Rules: Creativity + State Management
**Date:** 2025-10-30 01:56 EST
**Focus:** (1) Enhanced divergent thinking, (2) Session state hygiene, (3) Debug log discipline

---

## ✅ **Rule 1: Divergent Thinking with Cross-Domain Inspiration**

**CONDITION:** When stuck after 2 attempts OR when creative/novel approaches requested

**INSTRUCTION:**
```markdown
Activate divergent thinking with cross-domain exploration:

1. Generate 3 alternatives from different paradigms:
   - Technical (code/automation)
   - Process (workflow/recipe)
   - Integration (existing tools/services)

2. Draw inspiration from other domains:
   - "How would [systems thinking/design/engineering] solve this?"
   - "What analogies from [biology/architecture/game design] apply?"
   - "What if we inverted the problem?"

3. Leverage system capabilities:
   - Check Recipes/ for existing workflows
   - Check Knowledge/ for relevant principles
   - Consider app integrations (Gmail, Calendar, Drive, Notion)

4. For creative work: Present 2-3 distinct options before executing

Signal: "🎨 Exploring alternative approaches..."
```

---

## ✅ **Rule 2: Session State Hygiene**

**CONDITION:** (Always applied)

**INSTRUCTION:**
```markdown
Maintain SESSION_STATE.md actively:

1. Update every 3-5 exchanges OR after significant progress:
   - Update Focus if conversation pivots
   - Add to Progress/Covered after completing work
   - Update Topics as new themes emerge

2. Artifact management BEFORE creating files:
   - Declare in Artifacts section
   - Specify classification (temporary/permanent)
   - Include target path and rationale

3. Cleanup discipline:
   - Remove obsolete temporary artifacts
   - Archive completed work to user workspace
   - Keep Artifacts section current

Use: python3 /home/workspace/N5/scripts/session_state_manager.py update --convo-id <id> --field <field> --value "<value>"
```

---

## ✅ **Rule 3: Debug Log Enforcement (Strengthened)**

**CONDITION:** When DEBUG_LOG.jsonl exists in conversation workspace

**INSTRUCTION:**
```markdown
MANDATORY debug logging:

1. AFTER every fix attempt - Log immediately:
   python3 /home/workspace/N5/scripts/debug_logger.py append --convo-id <id> --component "<what>" --problem "<issue>" --hypothesis "<expected>" --actions "<did>" --outcome <status> --notes "<insights>"

2. BEFORE 3rd attempt - Check patterns:
   python3 /home/workspace/N5/scripts/debug_logger.py patterns --convo-id <id> --window 10 --threshold 2
   
   IF pattern detected → STOP, activate Debugger mode with planning

3. When claiming "done" - MUST have logged attempts + resolution

This is mandatory behavior during builds, not optional. Load file 'N5/prefs/operations/debug-logging-auto-behavior.md' for triggers.
```

---

**Total overhead:** ~35 tokens/response  
**Value:** Prevents state drift + enables creativity + catches debug loops
