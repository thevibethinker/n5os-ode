# Claude Code + N5OS Integration

This integration makes Claude Code **N5OS-aware** without overriding its excellent native planning capabilities.

## Philosophy

> **Inform, don't override.**

Claude Code's planning is a core strength. This integration provides:
- **Environment awareness** (protected paths, conventions)
- **Session continuity** (session-context.md survives compaction)
- **N5OS logging** (sessions tracked alongside Zo conversations)

It does NOT:
- Override planning methodology
- Block any operations
- Require specific workflows

---

## Installation

### Step 1: Add the MCP Server (gives Claude Code access to N5 tools)

```bash
claude mcp add --transport stdio n5-bridge -- bun /home/workspace/Integrations/claude-code/n5_mcp_bridge.ts
```

### Step 2: Add the Conventions Skill

```bash
claude skill add /home/workspace/Integrations/claude-code/n5-planning-skill.md
```

### Step 3: Copy Hooks to Your Claude Config

```bash
# Copy hooks infrastructure
cp -r /home/workspace/Integrations/claude-code/.claude/hooks ~/.claude/
cp -r /home/workspace/Integrations/claude-code/.claude/commands ~/.claude/

# Merge settings (or copy if you don't have custom settings)
cat /home/workspace/Integrations/claude-code/.claude/settings.json
# Manually merge the "hooks" section into ~/.claude/settings.json
```

### Step 4: Copy CLAUDE.md to Workspace Root

```bash
cp /home/workspace/Integrations/claude-code/CLAUDE.md /home/workspace/CLAUDE.md
```

### Step 5: Verify

```bash
claude mcp list
# Should show: n5-bridge

# Start a Claude Code session and run:
# /n5-status
```

---

## What You Get

### MCP Tools

| Tool | Purpose |
|------|---------|
| `n5_protect_check` | Check if path is protected before delete/move |
| `n5_log_bio` | Log health/mood entries |
| `n5_close_conversation` | Log session to N5OS |

### Hooks

| Hook | Trigger | Action |
|------|---------|--------|
| `session-start.py` | Session start / post-compaction | Creates session-context.md |
| `pre-tool-use.py` | Before Edit/Write/Bash | Warns about protected paths |
| `pre-stop.py` | Session end | Logs to N5OS |

### Slash Commands

| Command | Action |
|---------|--------|
| `/n5-close` | Summarize and close session |
| `/n5-status` | Check integration status |

### Files

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Environment conventions (project root) |
| `.claude/session-context.md` | Session state (survives compaction) |

---

## Session Lifecycle

```
┌─────────────────┐
│  Session Start  │
│  (hook fires)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ session-context │
│   .md created   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Your Work     │
│ (Claude plans   │
│  as it normally │
│  would)         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Protected Path? │──── Warning shown (doesn't block)
│   (hook fires)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Session End    │
│  (hook fires)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Logged to N5OS  │
└─────────────────┘
```

---

## Customization

### Adding More Protected Paths

Edit `/home/workspace/N5/scripts/n5_protect.py` or add `.n5protected` files to directories.

### Changing Hook Behavior

Edit the Python scripts in `.claude/hooks/`. They're simple and readable.

### Disabling Hooks

Remove entries from `~/.claude/settings.json`.

---

## Troubleshooting

### MCP not connecting

```bash
# Check MCP status
claude mcp list

# Re-add if needed
claude mcp remove n5-bridge
claude mcp add --transport stdio n5-bridge -- bun /home/workspace/Integrations/claude-code/n5_mcp_bridge.ts
```

### Hooks not firing

```bash
# Check settings.json has hooks section
cat ~/.claude/settings.json | grep -A20 hooks

# Test hook manually
echo '{"session_id": "test"}' | python3 ~/.claude/hooks/session-start.py
```

### Session context not created

The hook creates it in the project root's `.claude/` directory, not globally.

---

*Integration v2.0 | 2026-01-03 | Inform, don't override.*

