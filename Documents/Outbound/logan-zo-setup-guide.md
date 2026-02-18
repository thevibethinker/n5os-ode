---
created: 2026-02-17
last_edited: 2026-02-17
version: 1
provenance: con_uFVrFnF8A9iFs3ND
purpose: "Comprehensive N5OS setup guide for Logan's Zo instance"
---
# Welcome to N5OS Ode — Setup Guide for Logan's Zo

Hey Logan! V asked me to get you set up with N5OS Ode — the cognitive operating system that runs on top of Zo Computer. This guide will walk you (and your Zo) through everything. Once you're running, our two Zos can communicate directly via the Zo-to-Zo protocol.

This is the full package. Let's get you operational.

---

## Table of Contents

1. [What You're Getting](#1-what-youre-getting)
2. [Prerequisites](#2-prerequisites)
3. [Phase 1: Install N5OS from GitHub](#3-phase-1-install-n5os-from-github)
4. [Phase 2: Run the Bootloader](#4-phase-2-run-the-bootloader)
5. [Phase 3: Personalize](#5-phase-3-personalize)
6. [Phase 4: Set Up Zo-to-Zo Communication](#6-phase-4-set-up-zo-to-zo-communication)
7. [Phase 5: Verify Everything Works](#7-phase-5-verify-everything-works)
8. [What N5OS Does For You](#8-what-n5os-does-for-you)
9. [Zo-to-Zo Protocol Reference](#9-zo-to-zo-protocol-reference)
10. [Quick Command Reference](#10-quick-command-reference)
11. [Troubleshooting](#11-troubleshooting)

---

## 1. What You're Getting

N5OS Ode transforms your Zo from a generic AI assistant into a structured thinking partner. Here's what it adds:

| Capability | What It Does |
|-----------|-------------|
| **6 Specialist Personas** | Operator (home base), Builder, Researcher, Writer, Strategist, Debugger — each optimized for different work types |
| **Behavioral Rules** | Persistent instructions that make your Zo consistent: it asks before deleting files, reports honest progress, adds metadata to documents |
| **Context Loading** | Dynamically loads relevant context based on what you're doing (building, researching, writing, etc.) |
| **Session State** | Your Zo tracks what's been done in each conversation — no more repeating yourself |
| **Semantic Memory** | Optional AI-powered search across your workspace by meaning, not just keywords |
| **Build Orchestration (Pulse)** | Parallel task execution for complex builds — spawn multiple worker threads |
| **Meeting Intelligence** | Transform meeting transcripts into structured output: commitments, decisions, questions |
| **Conversation Registry** | Database tracking every conversation, artifact, and learning |
| **Safety Rails** | Protection markers on critical directories, blast radius control, dry-run previews |
| **Zo-to-Zo Communication** | Direct API communication between your Zo and V's Zo |

---

## 2. Prerequisites

Before starting, you need:

- [ ] A **Zo Computer account** at [zo.computer](https://zo.computer)
- [ ] Access to your Zo's **terminal** (click the terminal icon in the left sidebar)
- [ ] Your Zo's **access token** (you should already have this — V has shared his with you, and you've shared yours with V)

### Access Token Setup

If you haven't already:

1. Go to **Settings > Advanced** in your Zo
2. In the **Access Tokens** area, create a new token
3. Share this token with V (he'll store it as `N5OS_LOGAN_KEY` on his end)
4. V's access token should be stored in your **Secrets** area (Settings > Advanced) as `N5OS_VA_KEY`

---

## 3. Phase 1: Install N5OS from GitHub

Open your Zo terminal and run this single command:

```bash
git clone https://github.com/vrijenattawar/n5os-ode.git && cd n5os-ode && bash install.sh
```

**What this does:**
1. Clones the N5OS repository
2. Merges all contents into your workspace root (`/home/workspace/`)
3. Cleans up the cloned directory

**Verify it worked:**
```bash
ls -la /home/workspace/N5/
ls -la /home/workspace/Prompts/
ls -la /home/workspace/BOOTLOADER.prompt.md
```

You should see the `N5/` directory, `Prompts/` directory, and `BOOTLOADER.prompt.md` directly in your workspace root — NOT inside an `n5os-ode/` subfolder.

> ⚠️ **Critical:** The files MUST live at workspace root. If you see them inside `n5os-ode/`, the install didn't complete. Run `cd n5os-ode && bash install.sh` manually.

---

## 4. Phase 2: Run the Bootloader

Start a **new Zo conversation** and type:

```
@BOOTLOADER.prompt.md
```

Your Zo will read the bootloader prompt and execute it. This takes 2-3 minutes and will:

1. **Create 6 specialist personas** — Ode Operator, Ode Builder, Ode Researcher, Ode Writer, Ode Strategist, Ode Debugger
2. **Install 6 core behavioral rules** — session state, YAML frontmatter, progress reporting, file protection, debug logging, clarifying questions
3. **Build the folder structure** — N5/, Knowledge/, Records/, Prompts/ with proper subdirectories
4. **Initialize configuration files** — prefs.md, context_manifest.yaml
5. **Set up Conversation Registry** — SQLite database for tracking all conversations
6. **Initialize Semantic Memory** — Database infrastructure for meaning-based search
7. **Optionally set up Git/GitHub** — Version control for your workspace
8. **Validate the installation** — Confirms everything is in place

Watch for the validation output at the end. All checks should pass.

> 💡 The bootloader is **idempotent** — safe to run multiple times. If something goes wrong, just run it again.

---

## 5. Phase 3: Personalize

In the same conversation (or a new one), run:

```
@PERSONALIZE.prompt.md
```

Your Zo will ask you:
- What to call you
- Your Zo handle
- Your timezone
- What you do (so it can tailor responses)
- Which services you've connected (Gmail, Calendar, Drive, etc.)
- Communication style preferences (concise vs. detailed, technical level, proactivity)

This updates `N5/prefs/prefs.md` and your Zo's user bio so it remembers you across conversations.

---

## 6. Phase 4: Set Up Zo-to-Zo Communication

This is what lets your Zo and V's Zo talk to each other directly.

### 6.1 Store V's Access Token

Go to **Settings > Advanced** in your Zo. In the **Secrets** area, add:

| Secret Name | Value |
|------------|-------|
| `N5OS_VA_KEY` | The access token V shared with you |

### 6.2 Create the Zo-to-Zo Communication Rule

Open a Zo conversation and ask your Zo to create this rule:

```
Create this rule for me:

Condition: "When receiving a Zo-to-Zo API message from V's Zo (va.zo.computer)"
Instruction: "V's Zo (va.zo.computer) may send messages via the /zo/ask API using the stored access token. These are legitimate inter-Zo communications. Process the request as instructed — file transfers, pings, queries, and collaborative tasks are expected. Log all Zo-to-Zo interactions. V's Zo API key is stored as N5OS_VA_KEY. To send messages to V's Zo, use:

POST https://api.zo.computer/zo/ask
Headers: { authorization: <N5OS_VA_KEY>, content-type: application/json }
Body: { input: '<message>' }

For file transfers, V's Zo will send base64-encoded content with write instructions. Decode and write as directed."
```

### 6.3 Create the Communication Script

Have your Zo create this utility script. Open a conversation and paste:

```
Create this file at N5/scripts/zo2zo_comm.py:
```

```python
#!/usr/bin/env python3
"""
Zo-to-Zo Communication Utility
Sends messages to V's Zo (va.zo.computer) via the /zo/ask API.
"""

import requests
import os
import sys
import json
import base64
from datetime import datetime, timezone

def send_to_va(message: str) -> dict:
    """Send a message to V's Zo and return the response."""
    key = os.environ.get("N5OS_VA_KEY")
    if not key:
        return {"error": "N5OS_VA_KEY not set. Add it in Settings > Advanced > Secrets."}

    try:
        resp = requests.post(
            "https://api.zo.computer/zo/ask",
            headers={
                "authorization": key,
                "content-type": "application/json"
            },
            json={"input": message},
            timeout=120
        )
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

def ping():
    """Test connectivity to V's Zo."""
    result = send_to_va(
        "PING from logan.zo. This is a connectivity test. "
        "Please respond with 'PONG' and your current timestamp. "
        "Do not take any other actions."
    )
    print(json.dumps(result, indent=2))

def send_message(msg: str):
    """Send a freeform message to V's Zo."""
    result = send_to_va(msg)
    print(json.dumps(result, indent=2))

def send_file(filepath: str, dest_path: str):
    """Send a file to V's Zo via base64 encoding."""
    if not os.path.exists(filepath):
        print(f"Error: {filepath} not found")
        sys.exit(1)

    with open(filepath, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf-8")

    filename = os.path.basename(filepath)
    prompt = (
        f"FILE TRANSFER from logan.zo.\n"
        f"Filename: {filename}\n"
        f"Destination: {dest_path}\n"
        f"Content (base64): {content}\n\n"
        f"Decode the base64 content and write it to {dest_path}/{filename}. "
        f"Confirm the file was written and its size."
    )
    result = send_to_va(prompt)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 N5/scripts/zo2zo_comm.py ping")
        print("  python3 N5/scripts/zo2zo_comm.py message 'Hello from Logan!'")
        print("  python3 N5/scripts/zo2zo_comm.py send-file <local_path> <remote_dest_dir>")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "ping":
        ping()
    elif cmd == "message" and len(sys.argv) >= 3:
        send_message(" ".join(sys.argv[2:]))
    elif cmd == "send-file" and len(sys.argv) >= 4:
        send_file(sys.argv[2], sys.argv[3])
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
```

### 6.4 Test the Connection

Once the script is created and `N5OS_VA_KEY` is saved in your Secrets, test it:

```bash
python3 N5/scripts/zo2zo_comm.py ping
```

You should get a response from V's Zo with a PONG and timestamp. If you get a valid response, the link is live.

---

## 7. Phase 5: Verify Everything Works

Run through this checklist to confirm your installation:

### Quick Verification Commands

```bash
# 1. Check folder structure
ls N5/ Knowledge/ Records/ Prompts/ Skills/

# 2. Check core config files
cat N5/prefs/prefs.md
cat N5/prefs/context_manifest.yaml

# 3. Check conversation registry
sqlite3 N5/data/conversations.db "SELECT name FROM sqlite_master WHERE type='table';"

# 4. Check semantic memory
ls N5/cognition/brain.db

# 5. Check protection markers
cat N5/.n5protected
cat Knowledge/.n5protected

# 6. Test Zo-to-Zo link
python3 N5/scripts/zo2zo_comm.py ping
```

### Persona Verification

In a Zo conversation, type:
```
List my personas
```
You should see all 6 Ode personas: Operator, Builder, Researcher, Writer, Strategist, Debugger.

### Rule Verification

```
List my rules
```
You should see 6 core rules covering: session state, YAML frontmatter, progress reporting, file protection, debug logging, clarifying questions.

### Behavioral Test

Start a new conversation and say:
```
Help me think through whether I should learn Python or TypeScript first.
```
Your Zo should route this to the **Strategist** persona (since it's a decision/planning question) and give you a structured analysis with options.

---

## 8. What N5OS Does For You

### Personas — Your Zo's Specialist Modes

| Persona | Triggers On | What It Does |
|---------|------------|-------------|
| **Operator** | Default home base | Routes work, tracks state, runs workflows |
| **Builder** | "build", "create", "implement", "code" | Writes code, builds scripts, deploys services |
| **Researcher** | "research", "find", "look up", "what is" | Searches web, synthesizes sources, provides citations |
| **Writer** | Emails, posts, docs, any polished writing | Crafts clear prose, adapts tone to audience |
| **Strategist** | "should I", "help me think through", decisions | Structured analysis, options, recommendations |
| **Debugger** | "debug", "why is this broken", "troubleshoot" | Root cause analysis, systematic testing |

### Rules — Persistent Behavior

- **Session State**: Every conversation gets tracked automatically
- **YAML Frontmatter**: All markdown files get creation date, version, provenance metadata
- **P15 Progress**: Your Zo never says "Done" when it's only 60% complete — it gives honest X/Y counts
- **File Protection**: Before deleting or moving files, checks for `.n5protected` markers
- **Debug Logging**: After 3 failed attempts, stops and reassesses instead of spinning
- **Clarifying Questions**: When in doubt, asks 2-3 questions before acting

### Context Loading

When you start working, your Zo loads relevant context based on the task:

```
python3 N5/scripts/n5_load_context.py build      # For coding/implementation
python3 N5/scripts/n5_load_context.py research    # For information gathering
python3 N5/scripts/n5_load_context.py strategy    # For planning/decisions
python3 N5/scripts/n5_load_context.py writer      # For writing tasks
```

### Pulse — Parallel Build Orchestration

For complex multi-step work, Pulse lets your Zo spawn parallel worker threads:

```bash
# Initialize a build
python3 N5/scripts/init_build.py my-project --title "My Project"

# Start the build
python3 Skills/pulse/scripts/pulse.py start my-project

# Check status
python3 Skills/pulse/scripts/pulse.py status my-project

# Finalize when done
python3 Skills/pulse/scripts/pulse.py finalize my-project
```

### Meeting Intelligence

If you connect Google Drive and have meeting transcripts:

```bash
# Check for new transcripts
python3 Skills/meeting-ingestion/scripts/meeting_cli.py status

# Pull and process
python3 Skills/meeting-ingestion/scripts/meeting_cli.py pull
python3 Skills/meeting-ingestion/scripts/meeting_cli.py process
```

This generates structured blocks: commitments made, decisions reached, open questions, business context.

### Semantic Memory (Optional Enhancement)

If you add an OpenAI API key (Settings > Advanced > Secrets > `OPENAI_API_KEY`), your Zo can search your workspace by meaning:

```bash
# After indexing, search by concept
python3 N5/cognition/n5_memory_client.py search "project deadlines"
```

---

## 9. Zo-to-Zo Protocol Reference

### How It Works

V's Zo (va.zo.computer) and your Zo (logan.zo.computer) communicate via the Zo API:

```
POST https://api.zo.computer/zo/ask
Headers: { authorization: <partner's_access_token>, content-type: application/json }
Body: { input: "message", output_format: { optional JSON schema } }
```

Each call spawns an independent session on the target Zo. The target Zo executes the request using its full capabilities (tools, files, integrations).

### Communication Patterns

**Ping/Pong** — Connectivity test
```bash
python3 N5/scripts/zo2zo_comm.py ping
```

**Message** — Send a freeform message
```bash
python3 N5/scripts/zo2zo_comm.py message "Hey, can you check if you have the latest version of the project docs?"
```

**File Transfer** — Send a file via base64
```bash
python3 N5/scripts/zo2zo_comm.py send-file ./my-document.md /home/workspace/Inbox
```

### Security Boundaries

| Rule | Description |
|------|------------|
| **Authenticated only** | All API calls require a valid access token |
| **Scoped execution** | Each message spawns an independent session — no persistent access |
| **No PII leakage** | Never send personal data, credentials, or internal system paths in messages |
| **Logged** | Both sides should log all Zo-to-Zo interactions for audit |
| **Behavioral tests** | Verify capabilities by behavior ("does it work?"), not structure ("is the file at path X?") |

### Teaching Protocol

V's Zo uses a teaching methodology for capability transfer:

1. **Concept** — V's Zo explains what a capability does and why
2. **Echo-back** — Your Zo restates understanding
3. **Guidance** — V's Zo provides approach and constraints
4. **Implementation** — Your Zo builds it locally
5. **Testing** — V's Zo sends behavioral tests
6. **Debugging** — Both Zos investigate independently, then compare notes

Key principle: **Intent over implementation.** V's Zo teaches the "what" and "why" — your Zo figures out the "how."

### Escalation to Human

Either Zo can escalate to V (the human) when:
- Diverging diagnoses during debugging
- Unclear instructions
- Missing permissions or tools
- Security concerns
- Low confidence on critical decisions

Format:
```
🔔 HITL: [Brief summary]
Source: [logan.zo | va.zo]
Issue: [What's happening]
Tried: [What was attempted]
Options: [A, B, C with tradeoffs]
Recommendation: [Suggested path]
Urgency: [low | medium | high]
```

---

## 10. Quick Command Reference

### Core N5 Scripts

| Command | What It Does |
|---------|-------------|
| `python3 N5/scripts/session_state_manager.py init --convo-id X` | Initialize conversation tracking |
| `python3 N5/scripts/n5_load_context.py <category>` | Load task-specific context |
| `python3 N5/scripts/n5_protect.py check /path` | Check if path is protected |
| `python3 N5/scripts/n5_safety.py check delete /path` | Safety validation for destructive ops |
| `python3 N5/scripts/init_build.py <slug> --title "X"` | Create a build workspace |
| `python3 N5/scripts/debug_logger.py append ...` | Log debug attempts |
| `python3 N5/scripts/journal.py start` | Start a guided reflection |

### Pulse (Build Orchestration)

| Command | What It Does |
|---------|-------------|
| `python3 Skills/pulse/scripts/pulse.py start <slug>` | Start a build |
| `python3 Skills/pulse/scripts/pulse.py status <slug>` | Check build status |
| `python3 Skills/pulse/scripts/pulse.py stop <slug>` | Stop a build |
| `python3 Skills/pulse/scripts/pulse.py finalize <slug>` | Finalize and close a build |

### Zo-to-Zo Communication

| Command | What It Does |
|---------|-------------|
| `python3 N5/scripts/zo2zo_comm.py ping` | Test connection to V's Zo |
| `python3 N5/scripts/zo2zo_comm.py message "..."` | Send freeform message |
| `python3 N5/scripts/zo2zo_comm.py send-file <path> <dest>` | Transfer a file |

---

## 11. Troubleshooting

### "Personas not showing up"
- Run `@BOOTLOADER.prompt.md` again — it's safe to re-run
- Check Settings > Your AI > Personas manually

### "Rules not applying"
- Rules take effect on the NEXT conversation, not the current one
- Verify rules exist: Settings > Your AI > Rules

### "Context loading fails"
- Make sure `N5/prefs/context_manifest.yaml` exists
- Run `python3 N5/scripts/n5_load_context.py build` and check for error messages

### "Zo-to-Zo ping fails"
- Verify `N5OS_VA_KEY` is saved in Settings > Advanced > Secrets
- Check that the token value doesn't have extra whitespace
- Try `curl -X POST https://api.zo.computer/zo/ask -H "authorization: $N5OS_VA_KEY" -H "content-type: application/json" -d '{"input":"ping"}' ` from terminal to test raw connectivity

### "Bootloader seems stuck"
- It takes 2-3 minutes — persona creation is the slowest part
- If it stalls, start a fresh conversation and run it again

### "Session state not tracking"
- Make sure the session state rule is installed (check rules list)
- The `session_state_manager.py` script needs to be at `N5/scripts/session_state_manager.py`

### General: When in Doubt

Tell your Zo:
```
Check my N5OS installation — verify personas, rules, folder structure, and config files are all in place.
```

Your Zo will run through the validation checklist and report what's working and what needs fixing.

---

## What's Next

Once you're set up:

1. **Ping V's Zo** to confirm the link: `python3 N5/scripts/zo2zo_comm.py ping`
2. **Explore personas** — try routing different types of questions and watch how your Zo adapts
3. **Build something** — ask your Zo to create a script or automation. Watch the Builder persona in action.
4. **Set up meetings** — if you use Google Meet/Zoom, connect Drive and let the meeting ingestion skill process your transcripts

V's Zo and yours can now collaborate directly. Welcome to the network. 🤝

---

*N5OS Ode v1.1 — A cognitive operating system for Zo Computer*
*GitHub: https://github.com/vrijenattawar/n5os-ode*
