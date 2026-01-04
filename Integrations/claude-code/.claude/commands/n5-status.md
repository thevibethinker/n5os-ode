# /n5-status

Check N5OS integration status and protected paths.

## Instructions

When the user invokes `/n5-status`:

1. **Check MCP connection**: Verify `n5_protect_check` tool is available
2. **Show protected paths**: Use `n5_protect_check` on key directories:
   - `/home/workspace/N5`
   - `/home/workspace/Sites`
   - `/home/workspace/Personal`
3. **Show session context**: Read `.claude/session-context.md` if it exists
4. **Report status**: Summarize what's connected and working

## Example Output

```
N5OS Integration Status:
✓ MCP Bridge connected
✓ Protected paths checked:
  - N5/ (protected: system root)
  - Sites/ (protected: production sites)
  - Personal/ (protected: personal data)
✓ Session context: .claude/session-context.md exists

Ready for N5OS-aware development.
```

