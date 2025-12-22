---
created: 2025-12-12
last_edited: 2025-12-12
version: 1.0
---

# Organizations Registry

This directory contains profiles for organizations (companies, non-profits, groups) extracted from individual profiles or created manually.

## Structure

Each organization file follows the `TEMPLATE.md` structure.
Filename format: `kebab-case-name.md` (e.g., `careerspan.md`, `google.md`).

## Relationships

- Individuals link to Organizations via the `organization` frontmatter field.
- Organizations list their associated Individuals.

## Automation

Organizations are auto-extracted from individual profiles by `N5/scripts/extract_organizations.py`.

