# Conversation-End Cleanup Protocol

**Version:** 1.0.0  
**Last Updated:** 2025-10-22  
**Owner:** Vibe Builder

---

## Purpose

Ensure deliverables reach proper locations, temporary files are archived, and Records/Temporary/ stays clean. Prevents SSOT violations (P2) and placement issues (P13).

---

## When to Execute

**Trigger:** Conversation produces finalized deliverables (emails, documents, scripts) that went through iterative refinement

**Examples:**
- Meeting email generation with multiple drafts
- Document editing with revision history
- Script development with test versions
- Multi-stage content creation

---

## Cleanup Checklist

### 1. Identify Final Deliverables ✅

**Question:** What was produced that the USER will use/send/reference?

**Examples:**
- Follow-up email (final, ready to send)
- Meeting notes (complete analysis)
- Script (production-ready)
- Document (final draft)

**Action:** Confirm which version is "final"

---

### 2. Move Finals to Proper Locations ✅

**Per N5 Standard:**

| Deliverable Type | Destination | Symlink Location |
|-----------------|-------------|------------------|
| Meeting follow-up email | `N5/records/meetings/{meeting_id}/DELIVERABLES/follow_up_email_copy_paste.txt` | `Records/Company/emails/{meeting_id}_follow_up_email.txt` |
| Meeting notes/analysis | `N5/records/meetings/{meeting_id}/` | None (or per meeting-process.md) |
| Scripts (production) | `N5/scripts/` | None |
| Scripts (one-off) | Stay in conversation workspace | Document in conversation notes |
| Documents (deliverable) | `Documents/{category}/` or `Records/Company/` | None |
| Research/analysis | `Knowledge/{category}/` or conversation workspace | None |

**Action:** Move or verify final versions in correct locations

---

### 3. Handle Temporary Files ✅

**Temporary Location:** `Records/Temporary/`

**Decision Tree:**

```
For each file in Records/Temporary/:
├─ Is this the final version? 
│  └─ YES → Already moved in Step 2, delete from Temporary/
│
├─ Is this a valuable iteration/draft?
│  └─ YES → Archive to Records/Archive/{YYYY-MM}/{project-name}/
│
└─ Is this a scratch file/test?
   └─ YES → Delete
```

**Archive Pattern:**
```
Records/Archive/
└── {YYYY-MM}/
    └── {descriptive-name}/
        ├── draft_v1.md
        ├── draft_v2.md
        └── README.md (context: what these were, which was final)
```

**Action:** Archive valuable iterations, delete scratch files

---

### 4. Validate Symlinks ✅

**For files with symlinks (typically emails):**

```bash
# Check symlink exists and points to correct location
ls -la Records/Company/emails/{name}_follow_up_email.txt

# Expected output: symlink → N5/records/meetings/{id}/DELIVERABLES/...
```

**Action:** Verify symlinks work and point to finals

---

### 5. Document What Was Done ✅

**In conversation workspace, create/update:**
- `_deliverables_summary.md` - What was produced, where it lives, what was sent

**Template:**
```markdown
# Conversation Deliverables Summary

**Date:** {date}
**Conversation ID:** {id}

## Finals Delivered
- **{Deliverable name}**: file '{path}'
  - Status: {sent/ready/pending}
  - Notes: {any context}

## Archived
- {count} drafts/iterations → Records/Archive/{YYYY-MM}/{name}/

## Deleted
- {count} scratch files removed from Records/Temporary/
```

**Action:** Document for future reference

---

### 6. Check Records/Temporary/ is Clean ✅

**Final verification:**

```bash
ls -lh Records/Temporary/

# Should contain:
# - Active staging (email_staging/)
# - Recent processing logs (< 7 days old)
# - Worker assignment files (system-managed)

# Should NOT contain:
# - Multiple versions of same deliverable
# - Files with "FINAL" in name that aren't being actively worked
# - Drafts > 7 days old
```

**Action:** Confirm Temporary/ is clean

---

## Common Patterns

### Pattern: Email Generation with Iterations

**Situation:** Generated follow-up email with 5 draft versions

**Steps:**
1. Final email → `N5/records/meetings/{id}/DELIVERABLES/follow_up_email_copy_paste.txt`
2. Create symlink → `Records/Company/emails/{id}_follow_up_email.txt`
3. Archive drafts → `Records/Archive/{YYYY-MM}/{meeting-name}-email-iterations/`
4. Delete any pure scratch files
5. Document in conversation workspace

**Example:**
```bash
# Finals
N5/records/meetings/2025-10-10_hamoon-ekhtiari-futurefit/DELIVERABLES/follow_up_email_copy_paste.txt

# Symlink
Records/Company/emails/2025-10-10_hamoon-ekhtiari-futurefit_follow_up_email.txt → [above]

# Archived
Records/Archive/2025-10/hamoon-email-iterations/
├── HAMOON_EMAIL_FINAL.md
├── HAMOON_EMAIL_OPTIONS.md
└── ...
```

---

### Pattern: Script Development

**Situation:** Developed script with test versions

**Steps:**
1. **Production script** → `N5/scripts/{name}.py`
2. **One-off/helper script** → Keep in conversation workspace, document
3. **Test versions** → Delete (no archive needed unless valuable for learning)
4. Document script purpose, usage in N5/scripts/README.md or inline

---

### Pattern: Document/Research with Revisions

**Situation:** Created analysis document with multiple revisions

**Steps:**
1. **Final document** → Appropriate Knowledge/ or Documents/ location
2. **Draft revisions** → Archive if valuable, else delete
3. **Research notes** → Keep in conversation workspace or move to Knowledge/
4. Document in conversation workspace what was produced

---

## Validation Script

**Quick check for cleanup completion:**

```bash
# Run from /home/workspace
python3 N5/scripts/validate_cleanup.py --conversation-id {id}

# Checks:
# - Records/Temporary/ file age
# - Duplicate "FINAL" files
# - Broken symlinks
# - Missing deliverable documentation
```

*(Script to be created)*

---

## Principles Applied

- **P2 (SSOT):** Single final version in canonical location
- **P5 (Safety):** Archive before delete, clear naming
- **P13 (Naming & Placement):** Consistent paths, predictable structure
- **P8 (Minimal Context):** Clean workspace aids future work

---

## Anti-Patterns to Avoid

❌ **Multiple files with "FINAL" in Records/Temporary/**
- Indicates cleanup not performed
- Violates SSOT

❌ **Deliverables only in conversation workspace**
- Won't persist for USER
- Needs to move to USER workspace

❌ **No documentation of what was produced**
- Future you won't remember
- Creates confusion

❌ **Broken or missing symlinks**
- USER expects files in standard locations
- Symlinks must work

---

## Notes

- This protocol focuses on **file hygiene**, not content quality
- Complements file 'N5/commands/meeting-process.md' (meeting-specific workflow)
- Should be invoked by Vibe Builder before ending substantial work sessions
- Can be partially automated via script (future enhancement)

---

**Version History:**
- 1.0.0 (2025-10-22): Initial protocol based on Hamoon email cleanup lessons

**Related:**
- file 'Knowledge/architectural/architectural_principles.md' (P2, P5, P13)
- file 'N5/commands/meeting-process.md' (meeting deliverables)
- file 'Records/README.md' (Records structure)
