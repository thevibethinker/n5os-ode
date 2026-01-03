---
created: 2026-01-03
last_edited: 2026-01-03
version: 3.0
provenance: con_JEp786ebM2EkVLmG
---

# Build Plan: Claude Code + N5OS Integration

**Build Slug:** `zo-claude-code-native`  
**Title:** Claude Code as Zo-Native Tool  
**Owner:** Architect (Vibe Architect)  
**Status:** ✅ Phase 2 COMPLETE

---

## Philosophy

> **Inform, don't override.**

Claude Code's planning is excellent. We enhance it with:
- Environment awareness (protected paths, conventions)
- Session continuity (session-context.md)
- N5OS logging (sessions tracked with Zo conversations)

---

## Checklist

### Phase 1: Foundation ✅ COMPLETE
- [x] MCP bridge (`n5_mcp_bridge.ts`) with 3 tools
- [x] `close_convo_bridge.py` for session logging
- [x] Hooks infrastructure (`~/.claude/hooks/`)
  - [x] `session-start.py` - creates session-context.md
  - [x] `pre-tool-use.py` - warns about protected paths
  - [x] `pre-stop.py` - logs session to N5OS
- [x] Slash commands (`/n5-close`, `/n5-status`)
- [x] `CLAUDE.md` in workspace root (informational, not methodological)
- [x] Lightweight conventions skill (not planning override)
- [x] Settings.json with hooks configuration

### Phase 2: Testing & Refinement ✅ COMPLETE
- [x] Test hooks fire correctly in real Claude Code session
- [x] Verify session-context.md creates/updates
- [x] Add native import of session-context.md in CLAUDE.md
- [x] Confirm N5OS logging works end-to-end (MCP → SQLite → Zo API async)
- [x] Tune hook behavior based on usage (async mode enabled)

### Phase 3: Future Enhancements (Optional)
- [ ] Memory persistence (memory.jsonl pattern from Meridian)
- [ ] Plan sync (Claude Code plans → N5/builds/)
- [ ] Bi-directional context (Zo knowledge in Claude Code)

---

## Installation (Already Done)

```bash
# MCP
claude mcp add --transport stdio n5-bridge -- bun /home/workspace/Integrations/claude-code/n5_mcp_bridge.ts

# Skill
claude skill add /home/workspace/Integrations/claude-code/n5-planning-skill.md

# Hooks (copied to ~/.claude/)
# Settings.json (merged)
# CLAUDE.md (copied to /home/workspace/)
```

---

## Files Created

| File | Purpose |
|------|---------|
| `Integrations/claude-code/n5_mcp_bridge.ts` | MCP server with N5 tools |
| `N5/scripts/close_convo_bridge.py` | Session close via Zo API |
| `~/.claude/hooks/*.py` | Lifecycle hooks |
| `~/.claude/commands/*.md` | Slash commands |
| `~/.claude/settings.json` | Hook configuration |
| `/home/workspace/CLAUDE.md` | Environment conventions |

---

## Verification

```bash
# Check MCP
claude mcp list

# In Claude Code session:
/n5-status
```

---

*Plan v3.0 | Phase 1 Complete | 2026-01-03*


