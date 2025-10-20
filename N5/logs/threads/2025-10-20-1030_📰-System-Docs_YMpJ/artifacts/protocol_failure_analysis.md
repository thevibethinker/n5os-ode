# Protocol Failure Analysis: Reflection Ingest
**Date:** 2025-10-20  
**Incident:** AI bypassed established reflection pipeline and improvised ad-hoc solution

---

## What Failed

### Trigger Recognition
**Problem:** Email subject "N5 reflection-ingest: Brainstorm for Zo System GTM" should have triggered reflection pipeline protocol  
**What happened:** AI saw "reflection-ingest" but didn't recognize it as a command invocation trigger  
**Root cause:** No conditional rule mapping email subjects containing "reflection-ingest" to the reflection pipeline command

### Command Registry Check
**Problem:** Standing rule exists: "Before executing system operations, check if a registered command exists in commands.jsonl"  
**What happened:** AI didn't check commands.jsonl or N5/commands/ for reflection-related commands  
**Root cause:** Conditional rule scope limited to "system operations" - didn't trigger for "content processing"

### Protocol Loading
**Problem:** AI should have loaded `file 'N5/commands/reflection-ingest.md'` to understand the workflow  
**What happened:** AI improvised an analysis workflow instead  
**Root cause:** No automatic protocol loading triggered by email subject patterns

---

## Gap Analysis

### Missing Conditional Rules
1. **Email subject pattern matching**: No rule mapping specific subject patterns (e.g., "reflection-ingest", "[Reflect]") to specific protocols
2. **Command-first approach**: Existing rule doesn't cover content/reflection processing, only "system operations"
3. **Protocol discovery**: No rule requiring AI to search N5/commands/ when uncertain about workflow

### Unclear Trigger Mechanism
The reflection-ingest command documentation doesn't specify:
- How AI should recognize when to invoke it (email subject patterns)
- Whether email subjects are signals vs. explicit invocations
- Priority: follow email instructions vs. follow registered protocol

### Script Limitations
`reflection_ingest.py` has placeholders for email/Drive ingestion that say "requires Zo to call Gmail/Drive tools" - but the email WAS sent to Zo, creating circular dependency.

---

## Proposed Fixes

### 1. New Conditional Rule (CRITICAL)
```markdown
CONDITION: When email subject contains reflection-related keywords ("reflection-ingest", "[Reflect]", "reflection-pipeline") or when user mentions reflections in context of processing/ingesting
RULE: 
1. STOP and load `file 'N5/commands/reflection-ingest.md'`
2. Check if file is already staged in N5/records/reflections/incoming/
3. If not staged, stage it first
4. Execute: `python3 /home/workspace/N5/scripts/reflection_ingest.py`
5. Follow the established approval workflow - do NOT improvise
```

### 2. Enhanced Command-First Rule
Update existing rule to be broader:
```markdown
CONDITION: Before ANY operation that resembles a defined workflow (system operations, content processing, knowledge management, reflections, etc.)
RULE: Check if a registered command exists in `file 'N5/config/commands.jsonl'` OR search N5/commands/*.md for relevant protocols. Priority: command-first approach.
```

### 3. Reflection Ingest Protocol Update
Add to `N5/commands/reflection-ingest.md`:
```markdown
## Email-to-Zo Trigger Pattern

When V emails with subject containing "reflection-ingest" or "[Reflect]":
1. Attachment is already in conversation workspace
2. Stage attachment to N5/records/reflections/incoming/
3. Run: `python3 /home/workspace/N5/scripts/reflection_ingest.py`
4. Follow approval workflow (do NOT skip to final outputs)
```

### 4. Script Enhancement
Update `reflection_ingest.py` to detect conversation workspace attachments:
- Check `/home/.z/workspaces/*/email_attachment/` for new files
- Auto-stage them to incoming/
- Remove circular dependency on Gmail API for email-triggered runs

---

## Immediate Actions Required

1. **Clean up improvised outputs** (delete ad-hoc files)
2. **Stage actual file properly**
3. **Run correct pipeline**
4. **Add new conditional rule to prefs**
5. **Update reflection-ingest.md with email trigger pattern**
6. **Enhance reflection_ingest.py to handle email attachments automatically**

---

## Prevention Checklist

Before processing ANY user request that mentions a workflow term:
- [ ] Search N5/commands/ for relevant .md files
- [ ] Check commands.jsonl for registered commands
- [ ] Load protocol documentation fully before proceeding
- [ ] If uncertain, ask: "Is there an established protocol for this?"

---

## Lesson for Principles

**Candidate for new principle or enhancement to existing:**

**P0 Enhancement**: "Rule-of-Protocol: Before implementing ANY workflow, search N5/commands/ and commands.jsonl for established protocols. Improvisation is a last resort."

**New Principle**: "Trigger Recognition: Email subjects, file locations, and naming patterns are intentional signals. Map them to registered protocols before processing."
