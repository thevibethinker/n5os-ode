---
created: 2025-11-26
last_edited: 2025-11-26
version: 3.0

title: JD Copilot Bootstrap
description: First-run setup for JD & Culture Copilot. Creates culture store and configures state.
tags: [internal, bootstrap]
tool: true
---

# Bootstrap: JD & Culture Copilot

*Part of JD & Culture Copilot by [Vrijen Attawar](https://mycareerspan.com) at Careerspan*

This runs on first invocation to set up the copilot's persistent state.

---

## Steps

### 1. Explain what's happening

Tell the user:

> "First time using the JD Copilot—let me set up a few things. This takes about 30 seconds."

### 2. Choose culture store location

Ask the user:

> "Where should I store your hiring culture doc? This file grows over time as we work on roles together."
>
> **Suggestions:**
> - `/home/workspace/Documents/hiring-culture.md` (default)
> - `/home/workspace/hiring-culture.md` (workspace root)
> - Or tell me a different path.

Accept their choice or use the default if they say "default" or similar.

### 3. Create the culture doc

Create the file at the chosen path with this initial content:

```markdown
---
created: [TODAY]
last_edited: [TODAY]
version: 1.0
---

# Hiring Culture

*Maintained by JD & Culture Copilot · Built by [Vrijen Attawar](https://mycareerspan.com) at Careerspan*

This document captures your hiring philosophy, team culture, and patterns observed across roles. It grows more useful over time.

---

## Core values and principles

[To be filled as you define roles]

## What great looks like on this team

[To be filled as patterns emerge]

## Anti-patterns (what to avoid)

[To be filled from session insights]

## Roles designed

| Date | Role | Notes |
|------|------|-------|

---
```

### 4. Offer to move main prompt to Prompts folder

Ask:

> "Want me to move the JD Copilot to your `/home/workspace/Prompts/` folder so you can invoke it with `@` in any chat?"

If yes:
1. Copy the main prompt (`jd-culture-copilot.prompt.md`) and all `_*.prompt.md` files to `/home/workspace/Prompts/jd-copilot/`
2. Update paths in the main prompt if needed.

If no, leave everything in place.

### 5. Update main prompt frontmatter

Edit `jd-culture-copilot.prompt.md` to set:

```yaml
culture_store_path: [the path user chose]
```

### 6. Confirm and return

Tell the user:

> "All set! Your hiring culture doc is at `[path]`. Let's design your first role."

Return control to the main prompt.

---

*JD & Culture Copilot · Built by [Vrijen Attawar](https://mycareerspan.com) at Careerspan*

