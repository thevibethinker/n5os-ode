---
name: close
description: |
  Universal close skill. Just say "close" and it auto-routes to the right close skill
  (thread-close, drop-close, or build-close) based on SESSION_STATE context.
  Works in both native Zo and Claude Code environments.
compatibility: Created for Zo Computer
metadata:
  author: va.zo.computer
---

# Close

## Step 1: Detect Environment

Check if running in Claude Code:

```bash
python3 N5/scripts/cc_close_bridge.py detect
```

- If `CLAUDE_CODE=false` → **Native Zo path** (Step 2a)
- If `CLAUDE_CODE=true` → **Claude Code path** (Step 2b)

## Step 2a: Native Zo

Run the router with the current conversation ID:

```bash
python3 Skills/thread-close/scripts/router.py --convo-id <CONVO_ID>
```

The router reads SESSION_STATE and picks the right skill.

## Step 2b: Claude Code

Claude Code sessions don't have a Zo conversation ID or SESSION_STATE.
Use the bridge to create a synthetic workspace first.

**You (the LLM) must determine these from conversation context:**

1. **type** — What kind of work was this? (`build`, `research`, `discussion`, `planning`, `debug`)
2. **focus** — One-line summary of what the session was about
3. **tier** — Assess complexity:
   - Tier 1: Simple discussion, < 3 artifacts
   - Tier 2: Standard work, 3-10 artifacts, research
   - Tier 3: Builds, complex multi-file work, orchestration
4. **build-slug** (optional) — If this was work on a Pulse build
5. **artifacts** (optional) — Key files created or modified

Then run:

```bash
python3 N5/scripts/cc_close_bridge.py init \
  --type <type> \
  --focus "<focus>" \
  --tier <tier>
```

Add `--build-slug <slug>` if build context applies.
Add `--artifacts path1 path2 ...` for key files.

Capture the `CC_CONVO_ID` from output, then run the normal router:

```bash
python3 Skills/thread-close/scripts/router.py --convo-id <CC_CONVO_ID>
```

## Step 3: Follow Thread-Close Instructions

From here the flow is identical in both environments.
Read and follow `Skills/thread-close/SKILL.md` (or whichever skill the router selected).

The script outputs JSON context → you do semantic analysis → you call write functions → you echo the title.
