# Conversation Close - Diagnosis Summary

**Issue**: Recipe invocation produces short summary instead of full AAR structure

## Root Cause

**The recipe file is documentation-only.** When invoked, I (the AI) read the recipe markdown and generate a text summary, but **don't execute** `n5_conversation_end.py`.

## What Should Happen

1. User invokes `/close-conversation`
2. AI runs: `python3 /home/workspace/N5/scripts/n5_conversation_end.py --auto --convo-id con_XXX`
3. Script executes 11 phases (lesson extraction, AAR, organization, etc.)
4. Creates full AAR structure:
   - `N5/logs/threads/YYYY-MM-DD-HHMM_Title_ID/`
     - INDEX.md
     - RESUME.md
     - CONTEXT.md
     - DESIGN.md
     - IMPLEMENTATION.md
     - VALIDATION.md
     - aar-YYYY-MM-DD.json
     - artifacts/

## What Actually Happens

1. User invokes `/close-conversation`
2. AI reads `Recipes/Close Conversation.md`
3. AI generates text summary based on recipe description
4. **No script execution** ❌
5. **No AAR created** ❌
6. **No thread title** ❌
7. **No folder structure** ❌

## Why This Broke

**Hypothesis**: The recipe system changed from commands to recipes

- **OLD**: `commands.jsonl` had executable triggers
- **NEW**: Recipe markdown files are documentation
- **Gap**: No execution bridge between recipe invocation → script execution

## The Fix

Need to establish that when certain recipes are invoked, specific scripts should run.

### Option 1: Add conditional rule
```
CONDITION: User invokes /close-conversation
RULE: Execute: python3 /home/workspace/N5/scripts/n5_conversation_end.py --auto --convo-id <current>
```

### Option 2: Register as command
```json
{
  "trigger": "close-conversation",
  "command": "python3 /home/workspace/N5/scripts/n5_conversation_end.py --auto --convo-id {convo_id}",
  "category": "workflow",
  "requires_approval": false
}
```

### Option 3: Update recipe with explicit execution section
Add to recipe:
```markdown
## Execution

```bash
python3 /home/workspace/N5/scripts/n5_conversation_end.py \
  --auto \
  --convo-id $(current_conversation_id)
```
```

## Verification

Test the script manually:
```bash
python3 /home/workspace/N5/scripts/n5_conversation_end.py \
  --auto \
  --convo-id con_FHdPXi1NOvDeMj3C
```

Should create full AAR in `N5/logs/threads/`.
