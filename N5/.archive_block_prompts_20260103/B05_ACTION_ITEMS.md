---
created: 2025-11-15
last_edited: 2025-11-15
version: 1
block_code: B05
block_name: ACTION_ITEMS
category: recommended
---
# B05: Action Items & Next Steps

## Objective

Extract concrete tasks and next steps that need to happen as a result of this meeting. Focus on WHAT needs to be done, not necessarily WHO committed (those are in B02 if they're explicit commitments).

## Output Format

Structured task list with context. Each action item should include:
- **Task** (what needs to happen)
- **Owner** (if specified/clear)
- **Deadline** (if mentioned)
- **Context** (why it matters, dependencies)
- **Status** (if discussed)

## Quality Criteria

**Good B05 includes:**
- Actionable, concrete tasks (not vague intentions)
- Clear next steps that advance work forward
- Both explicit and implied action items
- Dependencies between tasks if relevant
- Mix of immediate and future actions

**Avoid:**
- Vague aspirations ("think about...", "consider...")
- Commitments with clear ownership (those go in B02)
- Past actions already completed
- Duplicate tasks

## Distinction from B02 (Commitments)

**B02 = PROMISES** → "I will send you the deck by Friday" (explicit commitment with ownership)
**B05 = TASKS** → "Need to review pricing model before next meeting" (task that needs doing, ownership may be unclear)

**Rule of thumb:** If someone explicitly committed with accountability → B02. If it's a necessary next step → B05.

## Instructions

1. Scan for action-oriented language:
   - "We need to..."
   - "Someone should..."
   - "Next step is to..."
   - "Let's..."
   - "Make sure to..."
   - "Don't forget to..."

2. Extract both:
   - **Explicit actions** (directly stated)
   - **Implied actions** (necessary to move forward based on discussion)

3. For each action:
   - Describe the task clearly
   - Note owner if mentioned
   - Capture deadline if stated
   - Explain context/importance

4. Group logically (by project, person, or timeline)

## Edge Cases

**If no clear action items:**
```markdown
## B05_ACTION_ITEMS

No specific action items identified. Meeting was primarily informational/exploratory.
```

**If action depends on external factors:**
```markdown
- **Review contract terms** (Owner: TBD, pending legal team availability)
  - Context: Needed before final agreement
```

**If action is recurring/ongoing:**
```markdown
- **Weekly check-ins on project status** (ongoing)
  - Every Monday at 10am
  - Owner: Team leads
```

## Example Output

```markdown
## B05_ACTION_ITEMS

### Immediate (This Week)
- **Schedule follow-up meeting with stakeholders**
  - Owner: V
  - Deadline: By EOD Friday
  - Context: Need to finalize Q1 roadmap before holidays

- **Review and comment on partnership proposal draft**
  - Owner: Rory
  - Deadline: Wednesday
  - Context: V needs feedback to incorporate before sending to legal

### Near-term (Next 2 Weeks)
- **Conduct user interviews for feature validation**
  - Owner: Research team
  - Context: Findings will inform B05 prioritization

- **Prepare pricing comparison analysis**
  - Owner: TBD
  - Context: Needed for board presentation on Dec 1

### Dependencies
- **Finalize vendor selection** (blocks integration timeline)
  - Dependent on: Pricing analysis completion
  - Owner: V + Rory

### Ongoing/Recurring
- **Weekly stand-ups** every Monday 9am
- **Monthly metrics review** first Friday of each month
```

## Validation

Before finalizing, check:
- [ ] All action items are concrete and actionable
- [ ] Not duplicating B02 commitments
- [ ] Includes both explicit and reasonably implied actions
- [ ] Deadlines captured when mentioned
- [ ] Dependencies noted where relevant
- [ ] No vague tasks ("think about", "consider")
- [ ] Organized logically for easy reference

