---
description: Run N5 safety audit and compliance check
tags:
  - safety
  - quality
  - audit
  - principles
---

# Safety Check

Run comprehensive N5 safety and compliance audit.

**Checks:**

1. **P5 Anti-Overwrite** - Backup validation
2. **P7 Dry-Run** - Preview capability for scripts
3. **P11 Failure Modes** - Error handling completeness
4. **P19 Error Handling** - Try/except coverage
5. **Placeholder Detection** - Undocumented TODOs (P21)

**Scripts:**
- `file N5/scripts/n5_safety.py` - Safety validator
- `file N5/commands/placeholder-scan.md` - Placeholder detection

**Detection Rules:** `file N5/lists/detection_rules.md`

**Process:**
1. Run safety validator on specified files/directory
2. Check for invented limits (P16)
3. Validate state verification (P18)
4. Review error handling patterns
5. Report violations with line numbers

**Output:** Safety violations report with actionable fixes
