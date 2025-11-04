---
description: |
tool: true
  Report a problem you've encountered in Zo interface - logs to debug system for pattern tracking.
  Use when you see errors, unexpected behavior, or anything that isn't working right.
tags:
  - debugging
  - issue-reporting
  - user-feedback
---
# Report Issue

Quick command for you to report problems you're seeing in the Zo interface or with system behavior.

## What This Does

- Logs your problem description to the debug system
- Captures screenshot if you provide one
- Helps AI track patterns and avoid circular debugging
- Creates searchable record of issues

## Usage

Just tell me what you're seeing:

**Examples:**

- "The session state isn't initializing - seeing error about missing template"
- "Build failed with import error, attaching screenshot"
- "Rate limit hit on third attempt, seems like backoff isn't working"

I'll automatically log this to the debug system with:

- Your problem description
- Conversation context
- Timestamp
- Any screenshots you share

## Behind the Scenes

Your report gets logged as:

```json
{
  "timestamp": "2025-10-29T...",
  "entry_id": "abc123",
  "component": "user_report",
  "problem": "Your description",
  "hypothesis": "User observation",
  "actions": ["User reported issue"],
  "outcome": "reported",
  "notes": "Additional context from conversation"
}
```

## Pattern Detection

If you report similar issues 3+ times, the system will:

- Flag potential circular problem
- Suggest different approach
- Alert me to review debug log
- Consider activating Debugger mode with planning

## Integration

This feeds into the same debug logging system that tracks:

- My failed attempts
- Hypotheses and outcomes
- Circular pattern detection
- Build/debug session progress