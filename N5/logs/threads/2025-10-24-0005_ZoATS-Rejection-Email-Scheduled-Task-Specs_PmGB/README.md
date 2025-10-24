# Thread Archive: ZoATS Rejection Email + Scheduled Task Specs

**Conversation ID:** con_PmGBfimCfDhawS6h  
**Date:** 2025-10-24  
**Events:** 1-50  
**Closure:** #1 (first closure)

---

## Overview

Implemented ZoATS rejection email composer with config-driven Careerspan promo and optional feedback system. Created comprehensive scheduled task specifications for ZoATS deployment automation.

---

## Key Outputs

1. **Rejection Email System** (file 'ZoATS/workers/rejection_email/')
   - Config-driven promo placement (italic, third-person, respectful)
   - Optional legally-safe feedback with filter and fallbacks
   - Batch processing with --limit for one-at-a-time cadence

2. **Scheduled Task Specs** (file 'ZoATS/scheduled_tasks/')
   - 7 complete task specifications for candidate pipeline
   - 5-min cadence for queue processing (intake, parser, scoring, dossier, rejection drafts)
   - Clarification monitoring and re-evaluation specs
   - All default to disabled + dry-run for safe deployment

---

## Artifacts

See file 'AAR.md' for complete list.

Primary directories:
- file 'ZoATS/workers/rejection_email/'
- file 'ZoATS/scheduled_tasks/'

---

## Context Files

- file 'Documents/N5.md' — System documentation
- file 'N5/prefs/prefs.md' — User preferences
- file 'N5/prefs/operations/scheduled-task-protocol.md' — Task safety protocol
- file 'Knowledge/architectural/architectural_principles.md' — Design principles

---

## Related Threads

- ZoATS planning and architecture threads
- Scheduled task protocol development

---

## Tags

#zoats #ats #rejection-email #scheduling #specs #deployment #config
