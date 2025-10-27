# Core Commands Rationale

**Total**: 31 commands (from 113 available)

---

## Selection Criteria

Commands included in core if they:
1. **Enable core workflows** (conversation-end, state management, list/knowledge ops)
2. **Maintain system health** (git-check, index-rebuild, workspace-maintenance)
3. **Support building/extending** (system-design-workflow, placeholder-scan)
4. **Provide essential discovery** (search-commands, gfetch, knowledge-find)

Commands excluded if they:
- Specialized workflows (meeting processing, deliverable generation)
- Domain-specific (Careerspan jobs, social media, CRM)
- Optional automation (reflections, digests, email processing)
- Entertainment (play-movie, play-tv-show)

---

## Core Commands (31)

### System Infrastructure (11)
- `conversation-end` — Formal conversation close-out
- `thread-export` — AAR generation
- `init-state-session`, `check-state-session`, `update-state-session` — Session state
- `core-audit` — Daily system health check
- `git-check`, `git-audit` — Git safety
- `index-rebuild`, `index-update` — System index
- `workspace-root-cleanup`, `workspace-maintenance` — Cleanup
- `hygiene-preflight` — Pre-flight safety checks
- `placeholder-scan` — Code quality enforcement (P16, P21)
- `file-protector` — Prevent accidental overwrites
- `system-timeline`, `system-timeline-add` — Track system evolution
- `system-design-workflow` — Building on N5

### List Management (6)
- `lists-add` — Add items to lists
- `lists-create` — Create new list
- `lists-find` — Search lists
- `lists-export` — Export list data
- `lists-health-check` — Detect orphaned/stale items
- `list-view` — View list contents

### Knowledge Management (4)
- `knowledge-add` — Add to knowledge base
- `knowledge-find` — Search knowledge
- `knowledge-ingest` — Bulk ingest
- `direct-knowledge-ingest` — Direct add

### Discovery (2)
- `search-commands` — Find commands
- `gfetch` — Fetch from Google Drive/Gmail

---

## Expansion Pack Commands (82)

### Meeting System (~12 commands)
- meeting-*, transcript-*, auto-process-meetings, etc.

### Deliverables (~5 commands)
- deliverable-generate, generate-deliverables, etc.

### Social Media (~8 commands)
- social-idea-*, social-post-*, linkedin-post-generate, etc.

### Careerspan (~5 commands)
- jobs-*, extract-careerspan-insights, careerspan-timeline

### Reflections (~8 commands)
- reflection-*, reflection-pipeline, etc.

### Email/Communication (~4 commands)
- email-post-process, follow-up-email-generator, warm-intro-generate

### Research/Intelligence (~6 commands)
- deep-research-due-diligence, pr-intel-extractor, strategy-compounder

### Digests (~3 commands)
- add-digest, digest-runs, weekly-strategic-review

### CRM/Relationships (~3 commands)
- crm-*, relationship-pipeline-add, strategic-partner

### Misc (~28 commands)
- Everything else (incantum, prompts, personas, etc.)

---

## Philosophy

**Core = Self-Sufficient Foundation**

With 31 core commands, users can:
- Manage conversations, sessions, threads ✅
- Organize knowledge and lists ✅
- Maintain system health ✅
- Build extensions ✅
- Search and discover ✅

Everything else is specialized functionality that builds on this foundation.

---

**Date**: 2025-10-27  
**Version**: 1.0-core  
**Commands**: 31 core / 113 total (27%)
