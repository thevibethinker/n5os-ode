---
description: Architecture compliance and quality review
tags:
  - architecture
  - quality
  - review
  - principles
---

# Build Review

Review implementation for architecture compliance.

**Pre-Flight:**
1. Load `file Knowledge/architectural/architectural_principles.md`
2. Load `file N5/commands/system-design-workflow.md`

**Review Checklist:**

**Architecture (P0, P1, P2, P8, P20):**
- [ ] Human-readable paths and names (P1)
- [ ] Single Source of Truth (P2)
- [ ] Minimal context principle (P8)
- [ ] Modular separation (P20)

**Safety (P5, P7, P11, P19):**
- [ ] Backup strategy (P5)
- [ ] Dry-run capability (P7)
- [ ] Failure modes documented (P11)
- [ ] Error handling complete (P19)

**Quality (P15, P16, P18, P21, P22):**
- [ ] Complete before claiming (P15)
- [ ] No invented limits (P16)
- [ ] State verification (P18)
- [ ] Assumptions documented (P21)
- [ ] Right language choice (P22)

**Output:** Compliance report with principle violations and recommendations
