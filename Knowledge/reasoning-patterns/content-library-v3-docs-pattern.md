---
created: 2025-12-02
last_edited: 2025-12-02
version: 1.0
---

# Pattern: Docs-From-Architecture-and-CLI

## Context

Used when writing or updating system documentation for an existing or newly migrated subsystem (here: Content Library v3) where code and architecture specs already exist.

## Steps

1. **Anchor on architecture spec first**
   - Open the canonical architecture file (SQL + design principles).
   - Extract the mental model: data model, canonical paths, and intended responsibilities.

2. **Read the live CLI / API implementation**
   - Open the primary script (here `content_library_v3.py`).
   - Enumerate actual commands, flags, and method signatures.
   - Note any deltas between architecture and code (e.g., missing `migrate` command).

3. **Cross-check legacy docs and usages**
   - Skim old system/quickstart/architecture docs.
   - Identify concepts that must survive into v3 (e.g., tag conventions, meeting flows).

4. **Design the doc set as a layered stack**
   - Main README: mental model + full reference for a human operator.
   - System guide: architecture, integration patterns, and cutover/rollback.
   - Quickstart: one-liner patterns for day-to-day usage.
   - Integration spec: contract for other systems (query patterns + migration history).

5. **Write against real commands only**
   - For each example, ensure a 1:1 match with actual CLI flags.
   - Avoid inventing commands or options that the code does not implement.

6. **Execute smoke tests from the docs**
   - Run a minimal set of documented commands: `stats`, `lint`, `search`.
   - Confirm canonical paths (DB + scripts) exist via `ls`.
   - Record any lint issues without blocking doc completion.

7. **Wire into session and artifact tracking**
   - Declare all planned `.new` files in SESSION_STATE before creating them.
   - Treat the reasoning pattern itself as a permanent knowledge artifact.

## When to Reuse

- Any v2→v3 style migration where code exists and documentation needs to catch up.
- When consolidating fragmented docs into a single, layered doc set.
- When you need high confidence that docs and CLI/API are actually in sync.

## Guarantees

- Documentation only describes capabilities that exist in code.
- Examples are runnable as written (or clearly marked as illustrative).
- Integration specs stay anchored to real tag/topic conventions and paths.

