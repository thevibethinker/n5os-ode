# N5 Persona Switching System - Archived

**Date:** 2025-10-31
**Reason:** Conflicts with Zo's native persona system
**Action:** Backed up and removed custom switching infrastructure

## What Was Removed

This custom system attempted to create a "Core + Specialist" architecture with:
- Vibe Operator as always-on coordinator
- Auto-detection and activation of specialist modes
- Session state management for persona switching

## Issue

Zo already has built-in persona management. Running a custom system on top created conflicts and unexpected behavior.

## What's Preserved

Individual persona files remain in :
- vibe_builder_persona.md
- vibe_debugger_persona.md
- vibe_researcher_persona.md
- vibe_strategist_persona.md
- vibe_writer_persona.md
- vibe_teacher_persona.md

These can still be invoked directly via Zo's native system.

## Files Archived Here

- persona-management-protocol.md (the switching rules)
- vibe_operator_persona.md (the coordinator)
- INDEX.md (the switching architecture doc)
- Related rules and automation

---

*Archived: 2025-10-31 17:57 ET*

## Files Backed Up

✅ persona-management-protocol.md - The switching system rules
✅ vibe_operator_persona.md - The coordinator persona
✅ INDEX.md - Architecture documentation
✅ session_state_manager.py - The state tracking script
✅ templates_session_state/ - Session state templates
✅ RULES_TO_REMOVE.txt - Documentation of which rules to remove

## What Will Be Removed

**From Documents/System/personas/:**
- vibe_operator_persona.md (coordinator)
- INDEX.md (switching architecture)

**From N5/prefs/operations/:**
- persona-management-protocol.md

**From N5/scripts/:**
- session_state_manager.py

**From N5/templates/:**
- session_state/

**From prefs.md (user rules):**
- SESSION_STATE initialization rule
- SESSION_STATE maintenance rule  
- Specialist auto-activation rule

## What Will Be Preserved

**Individual specialist personas remain active:**
- vibe_builder_persona.md
- vibe_debugger_persona.md
- vibe_researcher_persona.md
- vibe_strategist_persona.md
- vibe_writer_persona.md
- vibe_teacher_persona.md

These can be invoked directly through Zo's native persona system.

