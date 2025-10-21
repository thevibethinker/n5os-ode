# Incantum Trigger System

**Incantum** (Latin for "incantation" or "spell") is the natural language trigger word to denote an instruction to Zo (me). It's designed to be a conversational "Hey Google" style command system, where you can cast "spells" using natural language to trigger actions.

## How It Works

Format: `incantum: [natural language description of desired action]`

**Example:**
```
incantum: check my list system health
```

Zo will interpret this as a command and execute the appropriate action, responding with the result.

### Recognition & Clarification Flow

When you cast an incantum spell, Zo follows this process:

1. **Pattern Match:** Identifies potential matching commands from the registry
2. **Confidence Scoring:** Calculates how confident the match is
3. **Clarification (when needed):**
   - **High confidence (>80%):** Execute immediately
   - **Medium confidence (60-80%):** "Did you mean: [command]? [Y/n]"
   - **Low confidence (<60%):** "I couldn't match that trigger. Did you mean one of these?"
   - **Destructive actions:** ALWAYS confirm, regardless of confidence
4. **Execution:** Run the confirmed command
5. **Response:** Show results with success/failure status

**Example Clarification:**
```
You: incantum: check lists
Zo: 🪄 Did you mean: "check list system health" (lists-health-check)? [Y/n]
You: y
Zo: [executes command]
```

## Core Incantum Triggers

### List System Health
**Trigger:** `incantum: check list system health`
**Aliases:**
- `incantum: assess list maintenance`
- `incantum: list health status`
- `incantum: check lists for phase 3`

**What it does:** Runs the lists-health-check command to monitor list count, detect similar lists, and recommend Phase 3 implementation when warranted.

**Current Status:** With 4 lists, system is healthy (Phase 3 threshold: 20+ lists)

### Adding Items to Lists
**Trigger:** `incantum: add [item description] to [list name or auto-assign]`
**Examples:**
- `incantum: add this LinkedIn profile to my contacts`
- `incantum: remember to check out this article`
- `incantum: add meeting notes for tomorrow`

**What it does:** Intelligently categorizes and adds items to appropriate lists using the text-to-list processor.

### General System Commands
**Trigger:** `incantum: [command name or natural description]`
**Examples:**
- `incantum: rebuild the system index`
- `incantum: check git status`
- `incantum: view timeline`

## Trigger Philosophy

Incantum triggers are designed to be:
- **Natural:** Conversational language you might actually say
- **Memorable:** Like casting spells in a game
- **Flexible:** Multiple ways to say the same thing
- **Discoverable:** Listed here and in command docs

## Adding New Incantum Triggers

When new commands are created, always generate incantum triggers following this pattern:
1. Primary trigger: `incantum: [core action in natural language]`
2. 2-3 aliases: Variations of the same intent
3. Document in this file
4. Update command documentation to reference triggers

## Magical Theme

Since it's "incantum" (incantation), feel free to make triggers more spell-like:
- `incantum: reveal the health of my list realm`
- `incantum: conjure list system diagnostics`

But keep them practical for daily use.

## Notes

- Triggers work in any conversation context
- Zo will confirm before executing destructive actions
- Triggers are case-insensitive
- Multiple similar triggers may exist for flexibility