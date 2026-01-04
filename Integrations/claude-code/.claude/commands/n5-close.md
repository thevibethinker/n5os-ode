# /n5-close

Close this Claude Code session and log it to N5OS.

## Instructions

When the user invokes `/n5-close`:

1. **Summarize the session**: Briefly describe what was accomplished
2. **Update session-context.md**: Fill in the Progress and Decisions sections
3. **Call the close tool**: Use `n5_close_conversation` MCP tool with:
   - `summary`: Your session summary
   - `tier`: 1 (quick close)

## Example

```
Session complete. Updated session-context.md with:
- Progress: Refactored auth module, fixed 3 bugs
- Decisions: Used JWT over session cookies

Logged to N5OS ✓
```

