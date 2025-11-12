---
tool: true
description: Create new reusable prompt with proper structure and frontmatter
tags: [workflow, prompt-authoring, meta]
version: 1.0
created: 2025-11-03
---

# Create Prompt

Create a new reusable prompt file with proper YAML frontmatter and clear instructions.

## Instructions

**You are creating a new prompt. Follow this structure:**

### Step 1: Clarify Requirements

Ask the user:
1. **Purpose:** What should this prompt do?
2. **Inputs:** What information/context does it need?
3. **Outputs:** What should it produce?
4. **Audience:** Who will use this? (Affects complexity/explanation level)
5. **Frequency:** How often will it be used?

### Step 2: Design Prompt Structure

Based on requirements, determine:
- **Format:** Workflow (step-by-step) vs Template (fill-in) vs Guide (reference)
- **Complexity:** Simple (5-10 steps) vs Complex (multiple phases)
- **Specificity:** Generic (reusable) vs Specific (one-time use)

### Step 3: Write Frontmatter

Required fields:
```yaml
---
tool: true                    # Makes prompt discoverable
description: [One-line description]
tags: [tag1, tag2, tag3]     # For categorization
version: 1.0
created: YYYY-MM-DD
---
```

Optional fields:
```yaml
dependencies: [file1, file2]  # If prompt requires specific files
inputs: [input1, input2]      # Expected inputs
outputs: [output1, output2]   # Expected outputs
```

### Step 4: Write Instructions

Clear, executable instructions:

```markdown
# [Prompt Name]

[Brief introduction explaining what this prompt does]

## Instructions

**[Opening context-setting sentence]**

### Phase 1: [Phase Name]

1. **[Step Name]**
   - [Specific action]
   - [Clarification or detail]
   - [Example if helpful]

2. **[Next Step]**
   ...

[Continue with remaining phases]

## Quality Checklist

Before marking complete:
- [ ] [Quality criterion 1]
- [ ] [Quality criterion 2]
- [ ] [Quality criterion 3]

## Anti-Patterns

**❌ [Bad Practice]**  
**✓ [Good Practice]**

## Example Output

[Show example of what following this prompt produces]

---

**Related:**
- [Link to related prompts, principles, or docs]
```

### Step 5: Save Prompt

- **Filename:** `lowercase-with-hyphens.md`
- **Location:** `/workspace/Prompts/`
- **Validation:** Ensure YAML frontmatter is valid

### Step 6: Test Prompt

Optional but recommended:
1. Read prompt in fresh context
2. Check if instructions are clear
3. Verify checklist is complete
4. Ensure examples are helpful

## Quality Standards

### Good Prompts

- **Clear purpose:** Obvious what it does from description
- **Executable:** Can follow without additional context
- **Self-contained:** All necessary information included
- **Examples:** Show expected output format
- **Quality checks:** Built-in validation steps

### Prompt Principles

1. **Active voice:** "Generate summary" not "Summary should be generated"
2. **Specific actions:** "Create file at path X" not "Put file somewhere"
3. **Ordered steps:** Logical sequence, dependencies clear
4. **Quality gates:** Checklist prevents incomplete execution
5. **Anti-patterns:** Explicit warnings about common mistakes

## Anti-Patterns

**❌ Vague instructions**
"Do some research and make something useful"

**✓ Specific instructions**
"Search 3 academic databases, extract key findings, create structured summary with citations"

**❌ No quality checks**
Prompt ends with "Execute" - no verification

**✓ Built-in validation**
Checklist ensures all requirements met before claiming done

**❌ Assumes context**
References files/concepts without explanation

**✓ Self-contained**
All necessary context provided or explicitly requested

## Example Prompt

```markdown
---
tool: true
description: Generate weekly project status report from git commits and notes
tags: [reporting, project-management, automation]
version: 1.0
created: 2025-11-03
---

# Weekly Project Report

Generate structured weekly status report combining git activity and project notes.

## Instructions

**You are generating a weekly project status report. Follow these steps:**

### Phase 1: Gather Data

1. **Git Activity**
   ```bash
   git log --since="1 week ago" --pretty=format:"%h - %s (%an)" > recent_commits.txt
   ```

2. **Project Notes**
   - Review `Projects/[project]/docs/notes.md`
   - Check `Projects/[project]/TODO.md`

### Phase 2: Analyze Progress

3. **Categorize Commits**
   - Features: New functionality
   - Fixes: Bug corrections
   - Docs: Documentation updates
   - Refactor: Code improvements

4. **Identify Blockers**
   - Check TODO for stalled items
   - Note any dependencies

### Phase 3: Generate Report

5. **Create Report**

```markdown
# Weekly Status - [Project Name]
**Week of:** [Date]

## Summary
[2-3 sentence overview]

## Progress
- [Achievement 1]
- [Achievement 2]
- [Achievement 3]

## Commits
- Features: [count]
- Fixes: [count]
- Documentation: [count]

## Blockers
- [Blocker 1] - [Status/next step]

## Next Week
- [Priority 1]
- [Priority 2]
```

6. **Save Report**
   - Location: `Projects/[project]/reports/YYYY-MM-DD-weekly.md`

## Quality Checklist

- [ ] All sections complete
- [ ] Specific achievements (not vague)
- [ ] Blockers include next steps
- [ ] Next week priorities clear
- [ ] Report saved to correct location

## Anti-Patterns

**❌ Generic statements:** "Made good progress"  
**✓ Specific outcomes:** "Implemented user authentication (3 commits), fixed login bug, documented API"

---

**Related:**
- Template: `project-report-template.md`
- Principle: P15 (Complete Before Claiming)
```

## Template

When user asks to create a prompt, use this template as starting point:

```markdown
---
tool: true
description: [One-line description of what this does]
tags: [category, subcategory, type]
version: 1.0
created: YYYY-MM-DD
---

# [Prompt Name]

[Brief explanation of purpose and context]

## Instructions

**[Opening sentence setting context]**

### Phase 1: [First Phase Name]

1. **[Step 1 Name]**
   - [Action or detail]
   - [Additional info]

2. **[Step 2 Name]**
   - [Action or detail]

### Phase 2: [Second Phase Name]

[Continue with additional phases as needed]

## Quality Checklist

Before marking complete:
- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] [Criterion 3]

## Anti-Patterns

**❌ [Bad practice with brief explanation]**  
**✓ [Good practice showing correct approach]**

## Example Output

[Show what following this prompt produces]

---

**Related:**
- [Links to related resources]
```

---

**Related:**
- Principles: P1 (Human-Readable First)
- Principles: P8 (Minimal Context, Maximal Clarity)
- Directory Structure: `system/directory_structure.md`
