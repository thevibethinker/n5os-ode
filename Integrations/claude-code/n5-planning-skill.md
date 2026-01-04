# N5OS Conventions Reference

This is a lightweight reference for N5OS conventions. It does NOT override Claude Code's native planning — it simply provides context about the environment.

## When to Reference This

- Before creating new directories or major file structures
- Before delete/move operations on system directories
- When deciding where to place new scripts or integrations

## Quick Reference

### Directory Structure

```
/home/workspace/
├── N5/                    # System (protected)
│   ├── scripts/           # Python scripts
│   ├── builds/            # Build workspaces
│   └── prefs/             # Preferences and principles
├── Sites/                 # Websites (protected)
├── Personal/              # Personal data (protected)
├── Integrations/          # External tool integrations
├── Projects/              # Active projects
└── Knowledge/             # Research and intel
```

### Build Workspace Pattern

For major new work, create a build workspace:

```bash
python3 N5/scripts/init_build.py "my-feature" --title "Feature Title"
```

This creates `N5/builds/my-feature/` with PLAN.md template.

### Protection Check

Before destructive operations:

```
Use n5_protect_check tool with path argument
```

### Session Close

When done with a session:

```
Use /n5-close command or n5_close_conversation tool
```

## Philosophy

**Inform, don't override.** Claude Code's planning is excellent. This skill just provides environment context so your plans account for N5OS conventions.

