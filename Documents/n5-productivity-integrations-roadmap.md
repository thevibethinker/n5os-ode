# N5 OS Productivity Integrations - Implementation Roadmap
**Date:** 2025-10-27  
**Owner:** V  
**Purpose:** Implement productivity tools for research, programming, and vibe coding

---

## Selected Integrations

Based on our discussion, we're implementing:

1. ✅ **Obsidian** - PKM for Knowledge graph
2. ✅ **DevDocs** - Offline documentation
3. **Zed Editor** - Open source Cursor alternative  
4. **Raycast** - Command launcher (clarification needed)

---

## 1. Obsidian Integration

### What It Does
- Graph view of your Knowledge/ directory
- Bidirectional linking between concepts
- Canvas for visual planning
- Community plugins for extending

### Implementation Plan

```bash
# Download Obsidian AppImage
curl -L "https://github.com/obsidianmd/obsidian-releases/releases/download/v1.7.7/Obsidian-1.7.7.AppImage" -o ~/Apps/Obsidian.AppImage
chmod +x ~/Apps/Obsidian.AppImage

# Create desktop entry
cat > ~/.local/share/applications/obsidian.desktop <<'EOF'
[Desktop Entry]
Name=Obsidian
Exec=/home/workspace/Apps/Obsidian.AppImage
Icon=obsidian
Type=Application
Categories=Office;
EOF
```

**Vault Setup:**
- Point Obsidian to `/home/workspace/Knowledge/`
- Enable core plugins: Graph view, Backlinks, Outline
- Recommended community plugins:
  - Dataview (query notes like database)
  - Templater (advanced templates)
  - Excalidraw (visual diagrams)

**N5 Integration:**
- Keep markdown as SSOT
- Obsidian becomes a *view* into Knowledge/
- Use graph view for architectural planning
- Create templates for recurring knowledge patterns

**Cost:** FREE

---

## 2. DevDocs Integration

### What It Does
- Offline documentation for 100+ languages/frameworks
- Instant fuzzy search
- No more context-switching to browser

### Implementation - Option A: Web App (Simplest)

```bash
# Self-hosted DevDocs
git clone https://github.com/freeCodeCamp/devdocs.git ~/Apps/devdocs
cd ~/Apps/devdocs
thor docs:download python go rust javascript css --version=latest

# Run locally
rackup -p 9292
# Access at http://localhost:9292
```

### Implementation - Option B: Desktop App (Better)

```bash
# Use Zeal (desktop DevDocs alternative)
# Available in most Linux package managers
sudo apt install zeal  # or your package manager

# Download docsets for your stack
# Python, JavaScript, CSS, Bash, etc.
```

### N5 Integration
- Add alias to N5 commands: `docs` → open Zeal/DevDocs
- Bind to keyboard shortcut
- Reference in scripts when using unfamiliar APIs

**Cost:** FREE

---

## 3. Zed Editor - Open Source Cursor Alternative ⭐

### Why Zed Over Cursor

**Cursor:**
- ❌ Closed source
- ❌ $20/month subscription
- ❌ Sends code through their servers
- ✅ Best-in-class AI integration

**Zed:**
- ✅ Fully open source (GPL-3.0)
- ✅ FREE with BYO API keys
- ✅ Built in Rust (blazing fast)
- ✅ Native AI integration (not bolted on)
- ✅ Supports Ollama (local models)
- ✅ Agentic editing mode
- ✅ Real-time collaboration built-in
- ✅ Mac + Linux (Windows coming)
- ✅ 68k+ GitHub stars
- ✅ Created by Atom/Tree-sitter team

### Key Features for N5 Development

1. **Agentic Editing** - Delegate complex tasks to AI
2. **Edit Prediction** - Predicts your next edit (like Copilot but open)
3. **Multi-file refactoring** - Handles codebase-wide changes
4. **MCP Support** - Model Context Protocol (same as Cursor)
5. **Vim mode** - Best Vim integration of any modern editor
6. **GPU-accelerated** - 120fps rendering
7. **Zero bloat** - No Electron overhead

### Implementation

```bash
# Install Zed
curl -f https://zed.dev/install.sh | sh

# Or via package manager
# Debian/Ubuntu
curl https://zed.dev/install.sh | bash

# Configure with your API keys
# Settings > Language Models
# Add: Anthropic (Claude), OpenAI, or Ollama (local)

# For local AI (FREE):
# Install Ollama first
curl https://ollama.ai/install.sh | sh
ollama pull deepseek-coder  # or qwen2.5-coder

# Point Zed to Ollama in settings
```

### Zed vs Other Open Source Alternatives

| Feature | Zed | Continue.dev | Cline | Void |
|---------|-----|--------------|-------|------|
| **Type** | Standalone IDE | VS Code Extension | VS Code Extension | VS Code Fork |
| **Performance** | ⭐⭐⭐⭐⭐ (Rust) | ⭐⭐⭐ (JS) | ⭐⭐⭐ (JS) | ⭐⭐⭐ (Electron) |
| **AI Integration** | Native, deep | Plugin | Plugin | Native |
| **Agentic Mode** | ✅ Yes | Limited | ✅ Yes (strong) | ✅ Yes |
| **Local Models** | ✅ Ollama | ✅ Ollama | ✅ Ollama | ✅ Ollama |
| **Multi-file Edit** | ✅ Excellent | ⭐⭐ Fair | ✅ Good | ✅ Good |
| **Vim Mode** | ✅ Best-in-class | N/A (VSCode's) | N/A (VSCode's) | Good |
| **Collaboration** | ✅ Built-in | ❌ No | ❌ No | ❌ No |
| **Maturity** | ⭐⭐⭐⭐ (5 years) | ⭐⭐⭐ (2 years) | ⭐⭐⭐ (1 year) | ⭐⭐ (1 year) |
| **Stars** | 68k+ | 29k+ | 51k+ | 27k+ |
| **Speed** | Fastest | Slow | Slow | Medium |

**Verdict:** Zed is the clear winner if you want:
- Best performance (critical for vibe coding flow)
- Native AI (not an afterthought)
- Open source without compromises
- Professional-grade tool

**Alternative Stack:**
If you're heavily invested in VS Code:
- **Cline** (51k stars) - Most powerful agentic VS Code extension
- **Continue.dev** (29k stars) - Most flexible, model-agnostic

### N5 Integration

```bash
# Add Zed as default editor
export EDITOR="zed --wait"

# Create N5 command shortcuts
# Add to N5/commands/:
{
  "name": "edit",
  "description": "Open file in Zed",
  "command": "zed {file}"
}

# Open entire N5 workspace in Zed for system work
zed /home/workspace/N5
```

### Recommended Zed Workflow for N5

1. **Daily coding:** Use Zed with local Ollama models (FREE)
2. **Complex refactors:** Use Claude/GPT-4 via API (pay per use)
3. **Pair on architecture:** Use built-in collaboration
4. **Graph dependencies:** Use agentic mode to analyze codebase

**Cost:** 
- FREE (with Ollama local models)
- OR $0.03/1K tokens (Claude via your API key)
- OR $20/month (Zed Pro for hosted AI)

---

## 4. Raycast - Command Launcher ⚠️

**Clarification Needed:**

Raycast is a macOS-only app launcher (like Spotlight on steroids). 

**What I meant by "launch N5 scripts from anywhere":**
- Press a hotkey anywhere on your system
- Type part of an N5 command name
- Execute it instantly without opening terminal

**The Problem:**
- Raycast only works on **macOS**
- You're running Linux (Debian)

### Linux Alternatives to Raycast

**Option 1: Ulauncher** (Recommended)
```bash
# Install
sudo add-apt-repository ppa:agornostal/ulauncher
sudo apt update
sudo apt install ulauncher

# Features:
# - Fuzzy search applications
# - Custom scripts/commands
# - Extensions for workflows
# - Hotkey activation
```

**Option 2: Albert**
```bash
# Lightweight launcher
sudo apt install albert

# Similar to Raycast/Ulauncher
```

**Option 3: Just use your terminal + tmux**
```bash
# You might already have the best launcher:
# Super fast terminal with zsh/fish autocomplete
# + tmux for persistent sessions
```

**My Question:**
Do you actually need a GUI launcher, or would you prefer:
1. Better terminal shortcuts
[truncated]
8k+ stars, open source)
2. **Continue.dev** (29k stars, most popular extension, supports everything)
3. **Tabby** (31k stars, self-hosted, privacy-first)

For non-technical → technical journey:
- **Zed** is best: fast feedback loop, native AI, feels like magic
- **Cline** second: most powerful agent mode in VS Code
- **Aider** for terminal purists: lightweight, local-first

---

## Next Steps

**Immediate (This Week):**
1. ✅ Install Obsidian - point at Knowledge/ directory
2. ✅ Install Zeal (DevDocs alternative) - download Python, JS, Bash docsets
3. ✅ Install Zed - configure with Ollama for local AI
4. ⏸️ Clarify Raycast need - decide on Linux alternative

**Week 2:**
1. Configure Zed with N5 workspace
2. Set up Obsidian templates for knowledge capture
3. Create N5 command shortcuts for quick access

**Questions for You:**
1. **Raycast:** Do you want a GUI launcher (Ulauncher) or prefer terminal workflows?
2. **AI Coding:** Should I install Zed + Ollama, or would you prefer Cline in VS Code?
3. **Obsidian:** Want me to set up specific plugins for N5 workflows?

---

**Cost Summary:**
- Obsidian: FREE
- DevDocs/Zeal: FREE  
- Zed: FREE (with Ollama)
- Launcher: FREE

**Total: $0/month** for entire productivity stack upgrade

---

file '/home/.z/workspaces/con_tqhby3BWBBPmhuwi/n5-builder-integrations.md' (detailed analysis)  
file '/home/.z/workspaces/con_tqhby3BWBBPmhuwi/quick-wins-summary.md' (quick reference)
