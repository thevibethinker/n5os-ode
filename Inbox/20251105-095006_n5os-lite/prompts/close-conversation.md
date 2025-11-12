---
tool: true
description: End conversation workflow with summary, artifact archival, and cleanup
tags: [workflow, conversation, archival, cleanup]
version: 1.0
created: 2025-11-03
---

# Close Conversation

Execute end-of-conversation workflow: summarize discussion, archive artifacts, clean up temporary files.

## Instructions

**You are executing the Close Conversation workflow. Follow these steps systematically:**

### Phase 1: Summary Generation

1. **Review Conversation**
   - Read through conversation history
   - Identify key topics discussed
   - Note decisions made
   - List artifacts created

2. **Generate Summary**
   Create a concise summary including:
   - **Purpose:** What was the conversation about?
   - **Key Topics:** Main themes discussed (3-5 bullets)
   - **Decisions Made:** Important choices or conclusions
   - **Artifacts Created:** Files, documents, systems built
   - **Next Steps:** If any follow-up actions identified

3. **Save Summary**
   - Filename: `conversation-summary-YYYY-MM-DD.md`
   - Location: Determine appropriate location based on content
     - If project-related → `Projects/[project-name]/docs/`
     - If personal → `Personal/Journal/` or relevant Personal subfolder
     - If research → `Knowledge/[category]/`
     - If general → `Inbox/` for later filing

### Phase 2: Artifact Management

4. **Identify Artifacts**
   - List all files created during conversation
   - Categorize as:
     - **Permanent:** Should be kept in user workspace
     - **Temporary:** Working files, can be archived or deleted
     - **Generated:** Intermediate outputs

5. **Archive or Organize**
   - **Permanent artifacts:** Move to appropriate workspace location
   - **Temporary files:** Move to conversation workspace or delete
   - **Documentation:** Ensure artifacts have clear names and locations

6. **Verify Organization**
   - Check that permanent files are in correct locations
   - Ensure no important files left in temporary locations
   - Update any references or links

### Phase 3: Cleanup

7. **Conversation Workspace**
   - Review conversation workspace files
   - Keep: Useful notes, documentation, reusable scripts
   - Remove: Redundant intermediate files, test outputs

8. **Temporary Files**
   - Clear any obviously temporary files (e.g., `temp_*.txt`, `test_*.py`)
   - Keep anything that might be referenced later

### Phase 4: Finalize

9. **Status Report**
   Provide brief report:
   ```
   ## Conversation Closed
   
   **Summary:** [One-line summary]
   **Artifacts:** [Count] files organized
   **Location:** [Where summary was saved]
   **Next Steps:** [If applicable]
   ```

10. **Completion**
    - Confirm all steps complete
    - Offer to answer final questions
    - Ready for conversation end

## Quality Checklist

Before reporting complete:
- [ ] Summary generated with all sections
- [ ] Summary saved to appropriate location
- [ ] All permanent artifacts moved to correct locations
- [ ] Temporary files cleaned up
- [ ] Status report provided
- [ ] No important files left in limbo

## Anti-Patterns

**❌ Generic summaries:** "We discussed various topics"  
**✓ Specific summaries:** "Designed N5OS Lite extraction workflow, created 15 principle files, documented directory structure"

**❌ Files scattered everywhere**  
**✓ Files organized by purpose and category**

**❌ Claiming done when artifacts not organized**  
**✓ Verify all permanent files in correct locations before complete**

## Example Output

```markdown
## Conversation Closed

**Summary:** Extracted N5OS Lite components for demonstrator account

**Key Topics:**
- Designed export package structure
- Created 10 principle files (P1, P2, P5, P8, P15, P21, P23, P28, P36, P37)
- Documented 5 personas (Operator, Builder, Strategist, Writer, Architect)
- Wrote list maintenance protocol
- Structured directory organization guide

**Artifacts:** 18 files created
- 10 principle YAML files → `n5os-lite/principles/`
- 5 persona YAML files → `n5os-lite/personas/`
- 2 system docs → `n5os-lite/system/`
- 1 planning prompt → `n5os-lite/prompts/`

**Location:** Summary saved to `n5os-lite/CONVERSATION_SUMMARY.md`

**Next Steps:**
- Phase 2: Extract scripts and adapt for vanilla environment
- Phase 3: Create example prompts
- Phase 4: Write installation guide
```

---

**Related:**
- Principles: P15 (Complete Before Claiming)
- Principles: P2 (Single Source of Truth)
