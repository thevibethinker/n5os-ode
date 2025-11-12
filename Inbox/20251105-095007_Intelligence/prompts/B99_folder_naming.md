---
created: 2025-11-04
last_edited: 2025-11-04
version: 1.0
tool: true
description: Generate optimal meeting folder name from B26/B28 intelligence metadata
tags: [meeting-pipeline, naming, intelligence, automation]
---

# B99: Meeting Folder Name Generation

## Purpose

Generate an optimal, human-readable folder name for a processed meeting based on its B26 metadata and B28 strategic intelligence. Use semantic understanding to create names that are:
- **Scannable**: Immediately convey who/what the meeting was about
- **Unique**: Distinguish between multiple meetings with same stakeholder
- **Consistent**: Follow established naming patterns
- **Contextual**: Use organization names when they add clarity

## Input

You will receive:
1. **B26_metadata.md** content (meeting metadata, stakeholders, date, type)
2. **B28_strategic_intelligence.md** content (strategic context, meeting classification)
3. **Current folder name** (if being renamed)
4. **Date** (YYYY-MM-DD format)

## Priority-Based Naming Logic

Apply the FIRST matching priority:

**Priority 1: Single external stakeholder**
- Format: `{date}_{FirstName-LastName}_{type}`
- Example: `2025-08-29_Tim-He_partnership`
- Example: `2025-10-20_Bennett-Lee_advisory`
- Use when: Exactly 1 external stakeholder
- **Always use dash between first and last name**

**Priority 2: Multiple stakeholders, same organization**
- Format: `{date}_{org}_{type}`
- Example: `2025-09-12_greenlight_sales`
- Example: `2025-09-15_twill_partnership`
- Use when: 2+ external stakeholders from same org
- **Use org name, not individual names**

**Priority 3: Multiple stakeholders, different organizations**
- Format: `{date}_{topic}_{type}`
- Example: `2025-09-20_community-partnerships_discovery`
- Use when: External stakeholders from 2+ different orgs
- Topic should capture the common theme

**Priority 4: Internal meeting (team/cofounder)**
- Format: `{date}_careerspan-team_{topic}_{type}`
- Example: `2025-09-22_careerspan-team_daily-standup_standup`
- Example: `2025-09-22_careerspan_kathy-pham-interview_planning`
- Use when: All attendees are internal (Careerspan)

**Priority 5: Unknown/ambiguous**
- Format: `{date}_unknown_{type}`
- Example: `2025-10-20_unknown_external`
- Use when: Cannot determine stakeholders from B26/B28

## Name Component Rules

### Stakeholder Names
- Use First-Last format (with hyphen between first and last name)
- Example: `Allie-Cialeo`, `Tim-He`, `Bennett-Lee`
- For compound last names: Include all parts with hyphens (e.g., `Maria-Garcia-Lopez`)
- Single names: Use as-is (e.g., `Nafisa`)
- Remove titles (Dr., Mr., etc.)

### Organization Names
- Lowercase, hyphenated
- Remove "Inc", "LLC", "Corporation"
- Use recognizable short forms (e.g., "twill" not "Twill Technologies Inc")
- Multi-word: hyphenate (e.g., "mayo-clinic")

### Topic Extraction
- Extract from B28 "Meeting Type" or "Strategic Context"
- 1-3 words maximum
- Lowercase, hyphenated
- Focus on PURPOSE not format (e.g., "recruiting" not "discovery-call")
- Common topics: partnership, sales, discovery, integration, coaching, planning, standup

### Meeting Type Suffix
- `_external` - External stakeholders, any context
- `_partnership` - Partnership discussions
- `_sales` - Sales/demo meetings
- `_coaching` - Coaching sessions
- `_technical` - Technical deep-dives
- `_planning` - Planning sessions
- `_standup` - Daily standups
- `_internal` - General internal meetings

## Process

1. **Parse B26 metadata**:
   - Extract date (normalize to YYYY-MM-DD)
   - Extract stakeholders list with organizations
   - Identify internal vs external
   - Extract meeting type

2. **Parse B28 strategic intelligence**:
   - Extract meeting classification/type
   - Extract strategic context for topic keywords
   - Understand decision stage and purpose

3. **Apply priority logic**:
   - Count external stakeholders
   - Check organization distribution
   - Determine appropriate format

4. **Generate components**:
   - Date: Use from B26, fallback to folder name
   - Primary identifier: Stakeholder name(s) or org
   - Topic: Extract from B28 context
   - Type suffix: Based on meeting classification

5. **Validate and return**:
   - Format: `{date}_{identifier}_{type}`
   - All lowercase except stakeholder names (PascalCase)
   - Hyphens within components, underscores between
   - Maximum 60 characters total

## Output Format

Return ONLY the folder name, nothing else. No explanation, no markdown, just:

```
YYYY-MM-DD_identifier_type
```

## Examples

### Input: Tim He meeting (B26 shows single external, Twill)
```
2025-08-29_Tim-He_partnership
```

### Input: Allie Cialeo meeting (B26 shows Allie + Paul from Greenlight)
```
2025-09-12_greenlight_sales
```

### Input: Bennett Lee meeting (B26 shows single external, independent founder)
```
2025-10-20_Bennett-Lee_advisory
```

### Input: Internal team standup
```
2025-11-03_careerspan-team_daily-standup_standup
```

### Input: Alex Caveny coaching (recurring, single external)
```
2025-11-04_Alex-Caveny_coaching
```

## Edge Cases

- **Unknown stakeholders**: `{date}_unknown-attendee_{type}`
- **Ambiguous context**: Prefer organization name over generic "meeting"
- **Recurring meetings**: Include topic to distinguish (e.g., `_daily-standup`, `_weekly-review`)
- **Multiple meetings same day**: Topic becomes critical differentiator

## Quality Checks

Before outputting, verify:
- ✅ Date is valid YYYY-MM-DD format
- ✅ No spaces in output (use hyphens/underscores)
- ✅ Stakeholder names use First-Last format with hyphen
- ✅ Organization/topic use lowercase-with-hyphens
- ✅ Total length reasonable (<60 chars preferred)
- ✅ Name is scannable and meaningful to human reader

---

*This prompt is invoked as a tool during meeting processing pipeline*
