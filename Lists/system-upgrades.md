# System Upgrades List

<!-- Generated MD view of JSONL -->

## Open

### Enhanced Command Authoring User Experience

**ID:** cmd-auth-ux-disc-1758364385

**Created:** 2025-09-20T10:33:05Z

**Updated:** 2025-10-14T11:20:45.238422+00:00

**Priority:** M

**Tags:** ux, discoverability, interface

---

### Organizations System for CRM

**ID:** 2025-10-14-organizations-system

**Created:** 2025-10-14T04:41:00Z

**Priority:** H

**Tags:** crm, organizations, high-priority, phase-9

---

### File Cleanup System for Root and N5 Directories

**ID:** 2025-10-14-file-cleanup-system

**Created:** 2025-10-14T06:47:00Z

**Priority:** H

**Tags:** automation, cleanup, maintenance, system

---

### Build a Meeting Block Builder

**ID:** 20251015-meeting-block-builder

**Created:** 2025-10-15T17:11:51.678573+00:00

**Priority:** M

**Tags:** automation, meetings, tools

---

### Custom System Settings Configuration Area on Zo

**ID:** 20251015-custom-settings-area

**Created:** 2025-10-15T22:53:50Z

**Priority:** M

**Tags:** system, settings, configuration, ux

---

### create a meeting to talking point to knowledge base to content pipeline

**ID:** 4e78cf37-0c3b-4ac3-a18d-d08114f542a4

**Created:** 2025-10-16T04:17:17.240539+00:00

**Updated:** 2025-10-16T04:17:17.240571+00:00

**Tags:** workflow, pipeline, knowledge-base

---

### Create Sandbox for Files Mode

**ID:** 50a70792-6c16-46f3-87d4-41cb3d6505a4

**Created:** 2025-10-28T14:09:06.179986+00:00

**Priority:** M

**Tags:** sandbox, file-management, protocol, temporary-files

---

### Reference Files Coherence Check Script

**ID:** e658222c-afaa-4140-be6f-88038713299d

**Created:** 2025-11-03T06:58:20.787261+00:00

**Priority:** L

**Tags:** reference-files, validation, maintenance, coherence

---

### Create Vibe Persona

**ID:** 20251104-vibe-persona-02ed5f31

**Created:** 2025-11-04T19:58:53.065554+00:00

**Priority:** H

**Tags:** persona, vibe, design, high-priority

---

### Create Documenter Persona

**ID:** 20251104-documenter-persona-c51f61c2

**Created:** 2025-11-04T19:58:53.065583+00:00

**Priority:** H

**Tags:** persona, documenter, documentation, high-priority

---

### Create Systems Maintainer Persona

**ID:** 20251104-systems-maintainer-cfa085de

**Created:** 2025-11-04T19:58:53.065596+00:00

**Priority:** H

**Tags:** persona, systems-maintainer, maintenance, high-priority

---

### Integrate RescueTime for Android Screen Time tracking in Wellness Monitor

**ID:** 2025-12-11-screen-time-integration

**Created:** 2025-12-11T14:00:00Z

**Priority:** M

**Tags:** integration, wellness, screen-time, android

---

### Screen Time Integration (Android)

**ID:** 20251211-screen-time-integration

**Created:** 2025-12-11T14:00:00Z

**Priority:** M

**Tags:** health, integration, screen-time, rescuetime

---

### Wellness Dashboard 2.0 (Visuals)

**ID:** 20251211-wellness-dashboard-v2

**Created:** 2025-12-11T14:30:00Z

**Priority:** M

**Tags:** health, dashboard, visualization, wellness

---

### Integrate Cobalt for Media Capture

**ID:** 20251211-cobalt-06042d7a

**Created:** 2025-12-11T16:05:30.594256+00:00

**Priority:** M

**Tags:** media, tool-integration, cobalt, capture

---

### Daily Thought Provoker Session

**ID:** 20251218-thought-provoker-session

**Created:** 2025-12-18T12:15:00.000000+00:00

**Priority:** M

**Tags:** feature, thinking, content-generation, inbox-intelligence

---

### Genomics Deep-Dive Query Workflow

**ID:** 20251229-genomics-deep-dive-workflow

**Created:** 2025-12-29T17:50:00Z

**Priority:** H

**Tags:** health, genomics, 23andme, duckdb, vibe-trainer

---

### Standardize review artifact location under N5/review/

**ID:** 20260103-review-artifacts-folder

**Created:** 2026-01-03T18:32:14Z

**Priority:** M

**Tags:** review, hitl, convention, positions, traceability

**Body:**

Establish N5/review/<domain>/ as the canonical staging area for all human-in-the-loop review artifacts. For positions: write batch review sheets to N5/review/positions/YYYY-MM-DD_positions-review_batch-###.md. All workflows that generate review queues should default to this path.

---


## Done

### Command to Export a Particular Thread and Package Everything Needed to Restart Exercise in Another Thread

**ID:** 2025-09-19-export-thread-command

**Created:** 2025-09-19T17:16:00Z

**Updated:** 2025-10-14T11:20:45.238422+00:00

**Priority:** M

**Notes:** MVP completed: Interactive AAR generation with dual-write (JSON+MD), schema validation, artifact archiving. Located in N5/logs/threads/[thread-id]-[descriptive-title]/

---

### Upgrade system configuration

**ID:** 97f5627f-f5b2-4455-87b7-7381c3f654ae

**Created:** 2025-09-19T17:17:51.641889+00:00

**Updated:** 2025-10-14T11:20:45.238422+00:00

**Tags:** upgrade, system, configuration

---

### Workflow for Processing and Tracking Persons of Note (CRM)

**ID:** 2025-09-19-persons-crm-workflow

**Created:** 2025-09-19T17:21:00Z

**Updated:** 2025-10-14T11:20:45.238422+00:00

**Priority:** M

---

### Upgrade system config

**ID:** e92257eb-5fa1-4d2b-82cc-0d64e95fb9fe

**Created:** 2025-09-19T22:48:02.095297+00:00

**Updated:** 2025-10-14T11:20:45.238422+00:00

---

### Implement workflow enhancement for better productivity

**ID:** 4983d033-9367-4925-8519-bee89824e3b8

**Created:** 2025-09-19T22:49:07.267319+00:00

**Updated:** 2025-10-14T11:20:45.238422+00:00

**Tags:** implement, workflow, enhancement

---

### Long-standing Issue: Overriding Phenomenon

**ID:** 105c25cc-645c-4abc-b73d-6a8d9b463742

**Created:** 2025-09-19T23:19:56.554945+00:00

**Updated:** 2025-10-14T11:20:45.238422+00:00

**Tags:** issue,workflow

**Body:**

Files being accidentally overwritten or emptied during merges, commits, or syncs (e.g., knowledge/bio.md emptied recently). Pattern: Often from docgen or auto-updates. Impact: Data loss. Mitigation: Review diffs; check for empties.

---

### Long-standing Issue: Git Merge Conflicts

**ID:** 25145434-a989-4f6f-9afd-2d303ffde735

**Created:** 2025-09-19T23:20:02.660447+00:00

**Updated:** 2025-10-14T11:20:45.238422+00:00

**Tags:** issue,git

**Body:**

Unresolved conflicts during merges can overwrite sections or entire files. Pattern: Seen in multi-file updates. Impact: Inconsistent state. Mitigation: Resolve conflicts carefully; test after merge.

---

### Long-standing Issue: Uncommitted Changes Lost

**ID:** 2dd7244d-df6e-41c8-b622-0138fcd2c1d9

**Created:** 2025-09-19T23:20:08.707790+00:00

**Updated:** 2025-10-14T11:20:45.238422+00:00

**Tags:** issue,git,workflow

**Body:**

Local changes overwritten by pulls or resets without stashing. Pattern: During rapid iterations. Impact: Loss of work. Mitigation: Commit frequently; use branches.

---

### Long-standing Issue: Schema Validation Failures

**ID:** 1676a7fb-4fc2-4937-8102-7af5919332ef

**Created:** 2025-09-19T23:20:15.938200+00:00

**Updated:** 2025-10-14T11:20:45.238422+00:00

**Tags:** issue,validation

**Body:**

Invalid JSON/JSONL leading to corrupt lists or commands. Pattern: During additions/updates. Impact: Breaks functionality. Mitigation: Run validation before staging.

---

### Long-standing Issue: Dependency Conflicts

**ID:** a50875a7-24a9-46e4-ad96-38f16b404f9a

**Created:** 2025-09-19T23:20:22.153830+00:00

**Updated:** 2025-10-14T11:20:45.238422+00:00

**Tags:** issue,dependencies

**Body:**

Python modules or tools conflicting (e.g., jsonschema). Pattern: Import errors. Impact: Script failures. Mitigation: Pin versions; test in isolation.

---

### Implement dual-store synchronization module

**ID:** fff5f29c-4ca1-4304-b391-1dc47619c345

**Created:** 2025-09-20T06:06:45Z

**Updated:** 2025-10-14T11:20:45.238422+00:00

**Priority:** H

**Body:**

Create a module for atomic write and sync between Markdown and JSONL stores with locking.

---

### Add CLI enhancements (--dry-run, --verify, --rollback)

**ID:** 3ca94d01-a76a-457d-8f61-1ed9d6bcc0e3

**Created:** 2025-09-20T06:07:43Z

**Updated:** 2025-10-14T11:20:45.238422+00:00

**Priority:** H

**Body:**

Implement --dry-run to show changes without applying, --verify to validate post-write, --rollback to restore from backup.

---

### Implement backup retention and recovery

**ID:** 764a505c-c737-4a61-93a2-10d7f4052baa

**Created:** 2025-09-20T06:07:49Z

**Updated:** 2025-10-14T11:20:45.238422+00:00

**Priority:** H

**Body:**

Create backup pruner script to enforce policy of last 30 backups + 14 days TTL, provide recovery runbook.

---

### Schema validation and CI guardrails

**ID:** debccffe-1e4e-4832-be24-de97f9c2549f

**Created:** 2025-09-20T06:07:56Z

**Updated:** 2025-10-14T11:20:45.238422+00:00

**Priority:** M

**Body:**

Implement JSON Schema validator script, local validator for JSONL, CI hook for automated validation.

---

### Record dispatcher integration

**ID:** c0825e08-442f-42e1-9f64-5e533f1a04ec

**Created:** 2025-09-20T06:08:08Z

**Updated:** 2025-10-14T11:20:45.238422+00:00

**Priority:** M

**Body:**

Update record mappings JSON to route 'record upgrade' commands to system_upgrades_add.py with appropriate args pattern.

---

### Update documentation and command spec

**ID:** 4fd28ff9-1228-4e73-b9fd-2bab2323ea2b

**Created:** 2025-09-20T06:08:15Z

**Updated:** 2025-10-14T11:20:45.238422+00:00

**Priority:** L

**Body:**

Update N5/commands/system-upgrades-add.md with new CLI options, usage examples, troubleshooting, and operational runbook.

---

### Concrete End Step for Conversations with Action Implementation and System Synchronization

**ID:** 2025-09-20-conversation-end-step

**Created:** 2025-09-20T07:50:00Z

**Updated:** 2025-10-14T11:20:45.238422+00:00

**Priority:** MEDIUM

---

### Command Authoring Performance Optimization

**ID:** cmd-auth-perf-opt-1758364366

**Created:** 2025-09-20T10:32:46Z

**Updated:** 2025-10-14T11:20:45.238422+00:00

**Priority:** H

**Tags:** performance, llm, optimization

---


