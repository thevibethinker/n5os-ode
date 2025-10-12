# Conversation-End Workflow

**Module:** Operations  
**Version:** 1.0.0  
**Date:** 2025-10-09

---

## Purpose

This document defines the standard procedure for closing conversation threads, particularly when important system work has been completed. The goal is to ensure that conversation artifacts are properly archived and system documentation is correctly integrated into the N5 structure.

---

## When to Use This Workflow

Execute this workflow when:
- Closing a thread with the `n5: close-thread` command
- Significant system work was completed (new features, fixes, infrastructure)
- Documentation or analysis was created during the conversation
- Files were created in conversation workspace that need permanent homes

---

## Standard Procedure

### Phase 1: Identify Conversation Artifacts

**List all files created in conversation workspace:**
```bash
ls -la /home/.z/workspaces/con_<ID>/
```

**Categorize files by type:**
- **Analysis documents** - Root cause analysis, incident reports
- **Implementation summaries** - Technical details, testing results
- **System documentation** - Guides, references that become part of N5
- **Temporary artifacts** - Logs, test outputs, scratch files

---

### Phase 2: Archive Conversation Artifacts

**For threads with important work:**

1. **Create archive directory:**
   ```
   Documents/Archive/YYYY-MM-DD-Topic/
   ```

2. **Move analysis and summary documents:**
   - incident_analysis.md
   - implementation_summary.md
   - conversation_summary.md
   - Any other historical/reference documents

3. **Create archive README:**
   - Overview of what was accomplished
   - Links to related system components
   - Timeline entry references
   - Quick start / key commands

**Purpose:** Preserve context for future reference, debugging, and learning.

---

### Phase 3: Integrate System Documentation

**Identify system documentation** (guides, references, policies that become operational):

**For N5 system documentation:**
```
N5/System Documentation/
├── feature-guides/          # How-to guides for N5 features
├── technical-guides/        # Technical implementation details
├── quick-refs/              # Quick reference cards
└── [specific-topic].md      # Major feature documentation
```

**For preferences/policies:**
```
N5/prefs/
├── system/                  # System-level policies
├── operations/              # Operational workflows
├── communication/           # Communication standards
└── integration/             # Integration guidelines
```

**Key principle:** Documentation that will be referenced operationally should be integrated into N5 structure, not buried in archives.

---

### Phase 4: Update System Timeline

**Add timeline entry for system upgrades:**

Use `N5/timeline/system-timeline.jsonl` to record:

```json
{
  "timestamp": "YYYY-MM-DDTHH:MM:SSZ",
  "version": "X.Y.Z",
  "type": "infrastructure|feature|fix",
  "category": "safety|commands|documentation|workflow|...",
  "title": "Brief Title of System Change",
  "description": "Detailed description of what was implemented, why, and impact",
  "components": [
    "List of files created/modified",
    "Commands added",
    "Systems affected"
  ],
  "impact": "high|medium|low",
  "status": "completed|in-progress|planned",
  "author": "system|user",
  "tags": ["relevant", "tags", "for", "filtering"]
}
```

**Timeline entries should be added for:**
- ✅ New features or infrastructure
- ✅ Major fixes or improvements
- ✅ System reorganizations
- ✅ Documentation systems
- ⚠️ Incidents (already documented separately)

**Purpose:** Create audit trail of system evolution, not just problems.

---

### Phase 5: Verify Integration

**Checklist:**
- [ ] Archive created with README
- [ ] System docs moved to proper N5 locations
- [ ] Timeline entry added for system upgrade
- [ ] File references updated (if any)
- [ ] Git commit with descriptive message
- [ ] Quick test of any new functionality

---

## File Naming Conventions

### Archive Directories
```
Documents/Archive/YYYY-MM-DD-ShortTopic/
```

Examples:
- `2025-10-09-N5-Protection/`
- `2025-09-20-Timeline-System/`
- `2025-10-15-Command-Refactor/`

### System Documentation
```
N5/System Documentation/
├── [feature-name]-guide.md         # Major feature guides
├── [feature-name]-quick-ref.md     # Quick references
└── [topic]/                        # Grouped documentation
    ├── overview.md
    ├── technical-details.md
    └── troubleshooting.md
```

**Convention:** kebab-case, descriptive, no abbreviations unless standard

---

## Decision Tree

```
Closing thread?
├─ Important system work?
│  ├─ YES → Execute full workflow (Phases 1-5)
│  └─ NO → Simple cleanup, no archive needed
│
├─ Created documentation?
│  ├─ Operational (will be referenced) → Move to N5 structure
│  └─ Historical (context only) → Archive only
│
└─ System changes?
   ├─ YES → Add timeline entry for upgrade
   └─ NO → Timeline entry not needed
```

---

## Examples

### Example 1: File Protection System (This Thread)

**Phase 1:** Identified files in conversation workspace
- incident_analysis.md
- implementation_summary.md
- conversation_summary.md

**Phase 2:** Created archive
```
Documents/Archive/2025-10-09-N5-Protection/
├── README.md
├── incident_analysis.md
├── implementation_summary.md
└── conversation_summary.md
```

**Phase 3:** Integrated system docs
```
N5/System Documentation/
├── FILE_PROTECTION_GUIDE.md (created during thread)
└── protection-quick-ref.md (moved from N5 root)
```

**Phase 4:** Added timeline entries
- Incident entry (already existed)
- System upgrade entry (added)

**Phase 5:** Verified and committed

### Example 2: New Command Implementation

**Archive:** `Documents/Archive/2025-XX-XX-CommandName/`
**System Docs:** Update `N5/System Documentation/commands-catalog.md`
**Timeline:** Add entry for new command
**Components:** `N5/commands/command-name.md`, `N5/config/commands.jsonl`

### Example 3: Bug Fix (No Archive Needed)

**No archive** - Simple fix, no documentation
**Timeline:** Optional, if significant
**Commit:** Direct commit with fix

---

## Common Mistakes to Avoid

❌ **Don't:** Create archive without README  
✅ **Do:** Always include context for future reference

❌ **Don't:** Store operational docs only in archive  
✅ **Do:** Integrate into N5 structure for accessibility

❌ **Don't:** Only log incidents in timeline  
✅ **Do:** Log system upgrades and improvements

❌ **Don't:** Use arbitrary folder names  
✅ **Do:** Follow YYYY-MM-DD-Topic convention

❌ **Don't:** Skip verification phase  
✅ **Do:** Test and verify integration worked

---

## Integration with File Saving Policy

This workflow extends the file saving policy documented in `N5/prefs/prefs.md`:

**During conversation:**
- Files created in conversation workspace: `/home/.z/workspaces/con_<ID>/`

**At conversation end:**
- **Propose destinations** based on file type and purpose
- **Get user approval** before moving files
- **Execute this workflow** for important threads

**Priority order:**
1. User's explicit preferences (always respected)
2. This conversation-end workflow (for system work)
3. Default file saving policy (for general work)

---

## Maintenance

**Review quarterly:**
- Are archives being created consistently?
- Is system documentation properly integrated?
- Are timeline entries comprehensive?
- Do naming conventions need updating?

**Update this document when:**
- Archive structure changes
- New documentation categories added
- Timeline format evolves
- Integration points change

---

## Related Documents

- `N5/prefs/prefs.md` - General file saving policy
- `N5/prefs/system/folder-policy.md` - Folder structure governance
- `N5/timeline/system-timeline.jsonl` - System timeline format
- `Documents/Archive/` - Archive examples

---

## Version History

**1.0.0** (2025-10-09)
- Initial documentation
- Defines 5-phase workflow
- Includes decision tree and examples
- Addresses lessons from file protection implementation
