---
created: 2025-12-01
last_edited: 2025-12-01
version: 1.0
---

# Offline teaching package exchange (Phase 4)

This document describes how two Zos can use the Tutor Kit to exchange
"teaching packages" **purely via files/email**, without any live
network bridge.

## Teacher side: exporting a package

From the Tutor Kit repo root (e.g. `Projects/zo-tutor-kit`):

1. Ensure the kit is initialized:

   ```bash
   python3 tutor_cli.py init --zo-id <your_zo_id>
   ```

2. Export a package for the desired mode:

   ```bash
   # capability | knowledge | data
   python3 tutor_cli.py export-package --mode capability --out /tmp/tutor_package_capability.json
   ```

3. Send the resulting JSON file (e.g.
   `/tmp/tutor_package_capability.json`) to the other Zo's human via
   email, Drive, etc.

## Student side: importing a package

On the receiving Zo, after downloading the JSON file:

1. Place the file somewhere accessible, e.g. `/tmp/tutor_package_capability.json`.

2. From the Tutor Kit repo root:

   ```bash
   python3 tutor_cli.py init --zo-id <your_zo_id>
   python3 tutor_cli.py import-package /tmp/tutor_package_capability.json
   ```

3. The `import-package` command will:
   - Validate the JSON shape using the Teaching Package dataclasses.
   - Create a new per-session sandbox under `/home/workspace/TutorSandboxes/`.
   - Write a normalized copy of the teaching package into that sandbox.
   - Record an inbound log entry in `/home/workspace/Logs/tutor_sessions/`.

At this stage, all behavior is still demo-focused; the packages are
synthetic. Later phases will replace the synthetic content with
real capability/knowledge/data extraction while keeping this
file-based workflow intact as a transport option.

