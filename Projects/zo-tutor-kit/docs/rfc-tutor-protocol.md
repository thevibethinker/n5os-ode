---
created: 2025-11-30
last_edited: 2025-11-30
version: 1.0
---

# Tutor Protocol RFC (Draft)

This document describes the goals, constraints, and high-level design of
a "Tutor Protocol" that allows one Zo to teach another in a controlled,
time-bounded, sandboxed manner.

This is a skeleton to be iterated as the implementation evolves.

## MVP implementation snapshot

The initial implementation focuses on a single Zo running everything
locally, or exchanging files via email/drive, without any live network
bridge between Zos:

- A repository skeleton at `Projects/zo-tutor-kit` containing:
  - `tutor_cli.py` with `init`, `status`, `local-demo`, `export-package`,
    and `import-package` commands.
  - `zo_tutor_kit/tutor_protocol.py` defining basic session metadata and
    minimal teaching package schemas for capability, knowledge, and
    data-drop modes.
  - `zo_tutor_kit/sandbox_manager.py` for per-session sandbox
    directories under `/home/workspace/TutorSandboxes`.
  - `zo_tutor_kit/logging_forensics.py` for simple per-session message
    logging.
- A `local-demo` CLI flow that:
  - Ensures a local tutor config exists.
  - Synthesizes a `SessionStart` and `SessionScope` object.
  - Creates a sandbox for the demo session.
  - Builds a small JSON "teaching package" and writes it into the
    sandbox.
  - Records a single synthetic log entry via the forensics logger.
- File-based exchange via `export-package` / `import-package`:
  - `export-package` writes a standalone JSON teaching package file,
    suitable for sending via email or file sharing.
  - `import-package` reads such a JSON file, validates its shape via the
    Teaching Package dataclasses, places a copy into a new sandbox, and
    records an inbound log entry.

Future phases will layer on:

- Real cross-Zo networking and authenticated sessions.
- Richer capability/knowledge/data package schemas.
- Stronger sandbox isolation and tamper-evident logging.



