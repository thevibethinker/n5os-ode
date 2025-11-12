---
description: 'Pre-processor: Extract meeting metadata and clean filenames before intelligence generation'
tool: true
tags: [meeting, metadata, preprocessing]
created: 2025-11-04
version: 1.0
---

# Meeting Metadata Extractor

**Purpose:** Semantic analysis of meeting transcripts to extract metadata, generate clean human-readable filenames, convert to markdown with frontmatter, and organize files before intelligence block generation.

**Position in Pipeline:** Runs BEFORE `Meeting Process.md` as pre-processing step.

**Philosophy:** Let the LLM understand the meeting semantically, not regex pattern matching.

---

## Your Task

You are given a meeting transcript file (could be .docx, .md, .txt). Your job is to:

1. **Read and understand the transcript** semantically
2. **Extract metadata** about the meeting
3. **Generate clean, human-readable filename**
4. **Convert to markdown** with frontmatter
5. **Rename folder** to match clean naming
6. **Delete original file** after conversion

---

## Step 1: Extract Metadata

Analyze the transcript and extract:

### Required Fields:
- **date**: Meeting date (YYYY-MM-DD format)
  - Look for: transcript metadata, calendar references, date mentions
  - If unclear: use file timestamp or current date

- **meeting_type**: One of:
  - `internal` - Team meetings, standups, internal discussions
  - `external` - Client calls, partner meetings, investor pitches, networking
  - `seminar` - Presentations, panels, workshops, conferences
  - `presentation` - Solo presentations, demos, pitches

- **stakeholder_type**: Determine if this is internal team or which external category
  - For internal: `internal-team`
  - For external: `external-{descriptor}`
  - For seminars/presentations: `seminar-{event}` or `presentation-{topic}`

### Participant Analysis:

**For one-on-one or small group meetings:**
- Extract individual names (first-last or first only)
- Example: `vrijen-ilya`, `laura-close`, `danny-x-vrijen`
- Skip "Vrijen" when he's one participant (assume it's his transcript)
- If only 2 people and one is Vrijen: use other person's name

**For multi-party meetings with organization:**
- Use organization name instead of individuals
- Example: `acme-corp`, `techstars`, `sequoia`
- If multiple orgs: `acme-corp-x-techstars`

**For team meetings:**
- Use `team` or `team-standup` or specific team name

**For seminars/presentations:**
- Use event name or topic
- Example: `techstars-demo-day`, `aws-summit`, `product-launch`

### Source Detection:
Identify transcript source from metadata or content:
- `fireflies` (Fireflies.ai)
- `granola` (Granola)
- `plaud` (Plaud Note)
- `otter` (Otter.ai)
- `manual` (manually uploaded)
- `unknown` (if cannot determine)

---

## Step 2: Generate Clean Filename

Create human-readable filename following this pattern:

### Format:
```
YYYY-MM-DD_{type}_{participants-or-org}_{optional-topic}.md
```

### Examples:

**One-on-one external:**
```
2025-11-04_external_ilya_sales-coaching.md
2025-10-27_external_lisa-noble_discovery.md
```

**Team meetings:**
```
2025-11-03_internal_team-standup.md
2025-10-29_internal_team_sprint-planning.md
```

**Client/Partner with org:**
```
2025-11-01_external_acme-corp_requirements-gathering.md
2025-10-15_external_techstars_mentor-session.md
```

**Seminars/Presentations:**
```
2025-09-20_seminar_techstars-demo-day.md
2025-10-10_presentation_product-launch.md
```

### Naming Rules:
- Use hyphens for spaces within words: `sales-coaching`, `team-standup`
- Use underscores to separate components: `external_lisa-noble_discovery`
- Keep it concise but descriptive
- Topic is optional - only if it adds clarity
- All lowercase
- No special characters except hyphens and underscores

---

## Step 3: Convert to Markdown with Frontmatter

1. **Read original file** (handle .docx, .txt, .md)
2. **Convert to markdown** format
3. **Add YAML frontmatter** at top:

```yaml
---
date: YYYY-MM-DD
org1: [Primary organization or "Careerspan" for internal]
org2: [Second organization if multi-party, otherwise omit]
org3: [Third organization if applicable, otherwise omit]
speaker1: [First participant name]
speaker2: [Second participant name, if applicable]
speaker3: [Third participant name, if applicable]
meeting_type: [internal|external|seminar|presentation]
source: [fireflies|granola|plaud|otter|manual|unknown]
---
```

### Frontmatter Rules:
- **org fields:** Use actual organization names. For internal meetings, use "Careerspan"
- **speaker fields:** Use full names (First Last). Only include speakers who actively participated
- **Omit fields** that don't apply (e.g., if only 2 speakers, don't include speaker3)
- **meeting_type:** Must be one of the four types
- **source:** Must be one of the listed sources

### Content Formatting:
- Preserve transcript structure
- Use markdown headers (##, ###) for sections if not already present
- Keep speaker labels clear: **Speaker Name:** or variations
- Ensure readability

---

## Step 4: Rename Folder

The meeting folder should match the clean filename (without .md extension).

**Current folder:** `/home/workspace/Personal/Meetings/{old_name}/`  
**New folder:** `/home/workspace/Personal/Meetings/{clean_name}/`

Where `{clean_name}` is the filename without .md extension.

---

## Step 5: Cleanup

1. **Delete original file** after successful conversion
2. **Keep only** the new clean markdown file
3. **Preserve** any other files in the folder (metadata, blocks, etc.)

---

## Output Requirements

After processing, provide a summary:

```
✅ Meeting Metadata Extracted

**Original:** [old filename]
**New:** [clean filename]
**Folder:** [new folder path]

**Metadata:**
- Date: YYYY-MM-DD
- Type: [meeting_type]
- Stakeholders: [participant/org names]
- Source: [source]

**Files:**
- ✅ Converted to markdown with frontmatter
- ✅ Renamed to: [clean name]
- ✅ Folder renamed to: [folder name]
- ✅ Original file deleted

**Ready for intelligence block generation.**
```

---

## Error Handling

### If transcript is unreadable:
- Report error clearly
- Do NOT proceed with rename
- Leave files as-is

### If metadata cannot be extracted:
- Use sensible defaults:
  - date: file modification date
  - type: `external` (most common)
  - participants: `unknown-meeting`
  - source: `unknown`
- Proceed with conversion but note uncertainty in output

### If file conversion fails:
- Report specific error
- Do NOT delete original
- Leave folder as-is

---

## Integration Note

This prompt runs as a **pre-processor** before `Meeting Process.md`. After this completes successfully, the main intelligence block generation will use the clean files and metadata.

**Next step:** The AI request will automatically proceed to `Meeting Process.md` using the cleaned transcript.

---

*Prompt created: 2025-11-04*  
*Part of nuclear reset enhancement*  
*Follows Option B: Separate pre-processing approach*
