# Persona Quick Reference

**Architecture:** Core + Specialist Modes v2.0  
**Updated:** 2025-10-28

---

## How It Works

**Vibe Operator** is always active. It automatically activates specialist modes based on your request signals.

**You rarely need to manually activate modes**—Operator detects and coordinates.

---

## Specialist Modes

### Builder Mode
**Auto-activates on:** build, implement, create, develop, setup, deploy, script, configure  
**Manual:** "Operator: activate Builder mode"  
**Use for:** System building, scripting, infrastructure, refactoring  
**Loads:** Planning prompt for complex builds, architectural principles, language selection logic

### Debugger Mode
**Auto-activates on:** verify, check, validate, audit, review, test, debug, inspect  
**Manual:** "Operator: activate Debugger mode"  
**Use for:** Verification, testing, compliance checks, root cause analysis  
**Runs:** 5-phase verification (Surface→Deep→Principle→Test→Report)

### Researcher Mode
**Auto-activates on:** research, investigate, analyze, study, explore, survey  
**Manual:** "Operator: activate Researcher mode"  
**Use for:** Information gathering, synthesis, competitive analysis, learning  
**Delivers:** 5-phase workflow (Clarify→Breadth→Depth→Synthesize→Package)

### Strategist Mode
**Auto-activates on:** strategy, decide, options, approach, direction, framework, choose  
**Manual:** "Operator: activate Strategist mode"  
**Use for:** Decision-making, tradeoff analysis, approach selection, frameworks  
**Provides:** 2-4 distinct options with clear tradeoffs, recommendation

### Writer Mode
**Auto-activates on:** write, draft, compose, email, post, article, message, "send to"  
**Manual:** "Operator: activate Writer mode"  
**Use for:** External communications, emails, posts, articles, content  
**Always loads:** Voice transformation system (non-negotiable for brand)

---

## Common Patterns

**Research → Strategy → Build:**
```
"Research SQLite best practices, evaluate options, then build a CLI"
```
Operator: Researcher → (findings) → Strategist → (recommendation) → Builder → (implementation)

**Build → Verify:**
```
"Create the script and verify it works"
```
Operator: Builder → (creates) → Debugger → (verifies)

**Complex Build:**
```
"Build a distributed task system with PostgreSQL backend"
```
Operator: Builder (detects complexity, loads planning prompt, applies Think→Plan→Execute)

---

## When to Explicitly Activate

**99% of time:** Let Operator auto-detect  
**1% of time:** Override when:
- Signal is ambiguous ("check" could be verify or investigate)
- You want specific mode regardless of signal
- Testing mode behavior

**Example explicit:**
```
"Operator: activate Debugger mode - check this architecture for principle compliance"
```

---

## What Changed (v2.0)

**Before (v1.x):**
- Manual: "Load Vibe Builder persona"
- Personas were standalone
- Had to remember which to use

**Now (v2.0):**
- Just describe what you want
- Operator coordinates automatically
- Specialists activate on demand
- Seamless experience

---

## Troubleshooting

**Mode didn't activate?**
- Check squawk log: `cat /home/workspace/N5/logs/squawk_log.jsonl | tail -5`
- Operator logged why (ambiguous, low confidence, etc.)

**Wrong mode activated?**
- Give feedback: "Actually I need Builder mode for this"
- Operator learns patterns

**Want to see mode activation?**
- Ask: "Which mode are you using?"
- Operator will confirm

---

## References

- **Operator Core:** `file 'Documents/System/personas/vibe_operator_persona.md'`
- **All Modes:** `file 'Documents/System/personas/INDEX.md'`
- **Management:** `file 'N5/prefs/operations/persona-management-protocol.md'`

---

*Quick ref v2.0 | 2025-10-28 | For daily Zo use*
