---
created: 2025-12-07
last_edited: 2025-12-07
version: 1.0
---

# Sites System v1

This document defines how web-shaped apps (sites) are created, organized, and deployed on this Zo workspace.

## 1. Canonical locations

- All web apps **must live under** `Sites/`.
- Each site uses a **kebab-case slug**:
  - Example: `fabregas-cannon`, `productivity-dashboard`.
- Directories:
  - **Production:** `Sites/<slug>/`
  - **Staging (canonical dev copy):** `Sites/<slug>-staging/`
- Inbox copies like `Inbox/2025..._<slug>/` are **snapshots only**, never canonical.

## 2. Service conventions

Each production site has a user service:

- Label: `<slug>`
- Workdir: `Sites/<slug>`
- Entrypoint: typically `bun run prod` (or framework-specific start command)
- Port: taken from `zosite.json.publish.published_port` or explicit service config

Each staging site **may** have its own service:

- Label: `<slug>-staging`
- Workdir: `Sites/<slug>-staging`
- Entrypoint: typically `bun run dev`
- Port: **must differ** from prod.
- If the app supports `process.env.PORT`, staging sets `PORT` to its own port.

Example (Fabregas connections):

- Prod: `Sites/fabregas-cannon` ← service `fabregas-cannon` on port `50171`
- Staging: `Sites/fabregas-cannon-staging` ← service `fabregas-cannon-staging` on port `50172`

## 3. Creation protocol

When creating a new site:

1. **Choose slug** in kebab-case, e.g. `new-site-demo`.
2. **Scaffold under Sites**:
   - Use Zo's site creation so the code lands at `Sites/<slug>/` **or** `Sites/<slug>-staging/`.
   - Never create sites at the workspace root.
3. Add or confirm `zosite.json` under the site root:
   - `name` = `<slug>`
   - `local_port` = dev port
   - `publish` block defines prod entrypoint and published port.
4. Register or update the production user service to point at `Sites/<slug>`.

## 4. Staging vs production

- **Staging** (`Sites/<slug>-staging`) is the **source of truth for code edits**.
- **Production** (`Sites/<slug>`) is a **deployment copy**, not edited directly.
- Normal flow:
  1. Edit code in staging.
  2. Verify behavior via the staging service/URL.
  3. When ready, promote staging → prod using the promotion flow.

If staging becomes too messy, it can be reset from prod by copying prod back into staging; this should be done intentionally.

## 5. Promotion flow (staging → prod)

Promotion updates production code to match staging.

High-level steps:

1. **Pre-checks**
   - Ensure both `Sites/<slug>` and `Sites/<slug>-staging` exist.
   - Optionally run `python3 N5/scripts/n5_protect.py check Sites/<slug>` to confirm protection metadata.
2. **Sync code**
   - Copy from `Sites/<slug>-staging/` into `Sites/<slug>/`.
   - Exclude `node_modules/` and other environment-specific directories.
   - Delete files in prod that were removed in staging so prod does not accumulate dead files.
3. **Restart production service**
   - Restart the user service labeled `<slug>` so it picks up the new code.

### Generic helper script

For convenience, there is a generic helper script:

- `N5/scripts/promote_site.sh`

Usage:

```bash
# Dry-run to see what would change for a site
bash N5/scripts/promote_site.sh fabregas-cannon --dry-run

# Actual promotion (staging → prod)
bash N5/scripts/promote_site.sh fabregas-cannon
```

This script:

- Syncs `Sites/<slug>-staging/` → `Sites/<slug>/` using rsync
- Excludes `node_modules/`
- Supports `--dry-run` to preview changes
- Prints a reminder to restart the `<slug>` service afterwards

A backwards-compatible wrapper exists for Fabregas specifically:

- `N5/scripts/promote_fabregas_site.sh` → delegates to `promote_site.sh fabregas-cannon`

## 6. Protection rules

- `Sites/.n5protected` marks the entire Sites tree as protected.
- Critical sites also have their own `.n5protected` files, e.g.:
  - `Sites/productivity-dashboard/.n5protected`
  - `Sites/fabregas-cannon/.n5protected`
  - `Sites/fabregas-cannon-staging/.n5protected`

Operational rules:

- No agent or script should move or delete anything under `Sites/**` without an explicit, conscious step.
- If a site-shaped directory (contains `zosite.json` and `package.json`) is detected **outside** `Sites/`, it is considered misfiled and should be relocated into `Sites/<slug>-staging` or `Sites/<slug>`.

## 7. Future integration (optional)

- Git/GitHub can later be layered on:
  - `Sites/<slug>-staging` as the primary working copy tied to a Git repo.
  - `Sites/<slug>` as a deployment copy synced from a specific branch/commit.
- N5 git tools (e.g. git change checkers) can then summarize deltas before promotion.


