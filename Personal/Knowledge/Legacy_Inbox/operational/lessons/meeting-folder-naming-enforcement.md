# Lesson: Meeting Folder Naming Convention Enforcement

**Date:** 2025-10-27  
**Context:** Bug fix - Scheduled task created profiles with wrong folder structure  
**Category:** System Integrity, Naming Conventions, Prevention

---

## Problem Pattern

Scheduled task generated inline profile creation code that violated established naming convention:
- **Wrong:**  (date folder with name subfolder)
- **Correct:**  (hyphenated single folder)

**Root Cause:** Task instruction lacked explicit guidance to use proper profile manager functions

---

## Solution Pattern

**3-Step Fix:**
1. Migrate violations to correct format
2. Update task instruction with explicit protocol
3. Add automated validation to daily monitoring

**Key Principle:** P21 (Document Assumptions) - Explicit instructions prevent implicit bad patterns

---

## Prevention Protocol

**For Scheduled Tasks:**


**For System Monitoring:**
- Add validation scripts for critical conventions
- Integrate checks into daily/weekly maintenance
- Register validation commands for quick access

---

## Reusable Components

1. **Validation Script Template:**
   - Scan directory for convention violations
   - Report issues with suggested fixes
   - Support  and  modes
   - Integrate into daily guardian

2. **Task Instruction Enhancement:**
   - Add "CRITICAL: Protocol" sections
   - Reference proper module functions
   - Prohibit inline generation explicitly

3. **Command Registration:**
   - Create quick-access validation commands
   - Add to commands.jsonl for easy invocation

---

## Success Metrics

- 4 profiles migrated correctly
- 0 violations remaining
- Task updated with protocol
- Daily monitoring active
- 100% compliance achieved in 45 minutes

---

## Applicable To

- Any system with naming conventions
- Scheduled task management
- File organization protocols
- Automated validation needs

---

**Tags:** #bug-fix #naming-conventions #scheduled-tasks #validation #prevention #P21
