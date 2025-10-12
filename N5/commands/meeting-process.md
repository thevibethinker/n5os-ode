# `meeting-process`

**Version**: 4.0.0  
**Category**: Meeting Intelligence  
**Workflow**: AI-Driven Processing (Registry-Based)  
**Registry**: `N5/prefs/block_type_registry.json` (v1.3+)

## Purpose

This command processes meeting transcripts using a **registry-based system** to generate standardized "Smart Blocks" that provide structured meeting intelligence. Each block follows exact specifications defined in the Block Type Registry.

## Critical Principle: Registry as Source of Truth

**YOU MUST load and strictly follow** `N5/prefs/block_type_registry.json` for ALL block generation. The registry defines:
- All 30+ block types (B01-B30) with exact specifications
- Priority levels (REQUIRED, HIGH, MEDIUM, CONDITIONAL)
- When each block should be generated
- Exact format specifications with feedback markers
- Stakeholder-specific block combinations

**DO NOT improvise block formats or names.** Follow the registry exactly.

**CRITICAL: Understanding Format Strings**

**READ THIS:** `N5/prefs/REGISTRY_FORMAT_GUIDE.md` explains how to interpret format strings correctly.

**Key principle:** Text in `[square brackets]` within format strings are **extraction instructions**, NOT literal text to copy.

🚫 **NEVER copy placeholder text from format strings verbatim**  
🚫 **NEVER simulate or invent content not in the transcript**  
🚫 **NEVER use example/dummy data**

✅ **DO extract real content from transcript and format according to specification**  
✅ **DO use "[Unknown]" or "[Not discussed]" for missing information**  
✅ **DO follow block-specific rules from registry**

---

## Processing Workflow

### Step 1: Check for Pending Requests

Look in `N5/inbox/meeting_requests/` for JSON files.

**CRITICAL:** Process **ONLY ONE** transcript per invocation to avoid context window issues.

Select the **OLDEST request** by filename/timestamp (FIFO ordering).

### Step 2: Load Processing Request

Read the request JSON to get:
```json
{
  "meeting_id": "YYYY-MM-DD_stakeholder-name",
  "gdrive_id": "1abc...",
  "gdrive_link": "https://drive.google.com/...",
  "stakeholder_classification": "internal" | "external",
  "participants": ["Vrijen", "Other Person"],
  "detected_date": "ISO-8601 timestamp",
  "source": "google_drive"
}
```

### Step 3: Download Transcript

Use `use_app_google_drive` to download the transcript using the `gdrive_id`.

Save to: `N5/inbox/transcripts/{meeting_id}.txt`

### Step 4: Load Block Type Registry

**REQUIRED:** Load `N5/prefs/block_type_registry.json` into your working context.

This registry contains the complete specification for all blocks. You will reference it throughout processing.

### Step 5: Analyze Transcript & Determine Blocks

Read the transcript thoroughly and:

1. **Classify meeting type** (if not already classified):
   - Is this internal (Careerspan team only) or external?
   - Can you detect stakeholder type? (INVESTOR, NETWORKING, FOUNDER, COMMUNITY_PARTNER, etc.)

2. **Determine which blocks to generate** using this logic:

   **A. If stakeholder type is detected:**
   - Use the `stakeholder_combinations` section of registry
   - Generate blocks listed in that stakeholder's `block_ids` array
   - Example: `INVESTOR` → ["B26", "B01", "B08", "B16", "B11", "B13", "B02", "B07", "B04", "B05"]

   **B. If stakeholder type is NOT detected:**
   - Use priority-based selection:
     - **REQUIRED**: Always generate (e.g., B01, B08, B26)
     - **HIGH**: Generate unless clearly irrelevant to this meeting
     - **MEDIUM**: Generate only if substantial relevant content exists
     - **CONDITIONAL**: Generate ONLY if specific trigger is detected
   
3. **Check conditional triggers:**
   
   For each CONDITIONAL block, check if its "when" condition is met:
   
   - **B06 (PILOT_INTELLIGENCE)**: Only if pilot explicitly discussed
   - **B07 (WARM_INTRO_BIDIRECTIONAL)**: Only if warm intro mentioned
   - **B11 (METRICS_SNAPSHOT)**: Only if data/ROI/metrics discussed
   - **B13 (PLAN_OF_ACTION)**: Only for complex initiatives with multi-step execution
   - **B14 (BLURBS_REQUESTED)**: Only if someone requested a blurb or offered to introduce Vrijen
   - **B15 (STAKEHOLDER_MAP)**: Only if multiple stakeholders with different roles/interests
   - **B16 (MOMENTUM_MARKERS)**: Only for sales/investment conversations
   - **B17-B19 (Community/Product/Sales specific)**: Only if topic explicitly discussed
   - **B30 (INTRO_EMAIL_TEMPLATE)**: Only if Vrijen is introducing someone (not being introduced)

### Step 6: Generate Blocks

For each block you determined should be generated:

1. **Load the block specification** from the registry:
   - Block name (e.g., "DETAILED_RECAP")
   - Format specification (exact markdown structure)
   - Variables to populate
   - Special rules (if any)
   - Feedback enabled (yes/no)

2. **Extract relevant content** from the transcript according to the block's "purpose" and "variables"

3. **Format the block** following the EXACT format string from the registry:
   
   **Standard format structure:**
   ```markdown
   ### BLOCKNAME
   ---
   **Feedback**: - [ ] Useful
   ---
   
   [Block-specific content following format specification]
   ```
   
   **Notes on formatting:**
   - Use the block's "name" field for the header (all UPPERCASE)
   - Include feedback checkbox ONLY if `"feedback_enabled": true` in registry
   - Follow the format specification exactly (preserve markdown structure, tables, bullets)
   - Populate all variables listed in the "variables" array
   - Apply any special "rules" defined in the block specification

4. **Apply stakeholder-specific rules:**
   
   From B02 (COMMITMENTS_CONTEXTUAL) example:
   - "Vrijen/Logan/Careerspan team = 'We', Others = Name (your side)"
   - Preserve date formats as stated ("EOD Friday", "early next week")
   - Flag missing dates with "[Date TBD]"

5. **Save each block as a separate file:**
   
   **File naming convention:** `B##_BLOCKNAME.md`
   - Two-digit block number with leading zero (B01, B08, B21)
   - Underscore separator
   - Block name in UPPERCASE from registry
   - `.md` extension
   
   **Location:** `N5/records/meetings/{meeting_id}/B##_BLOCKNAME.md`

### Step 7: Create Metadata File

Create `N5/records/meetings/{meeting_id}/_metadata.json`:

```json
{
  "meeting_id": "YYYY-MM-DD_stakeholder-name",
  "processed_date": "ISO-8601 timestamp",
  "transcript_path": "/absolute/path/to/transcript.txt",
  "stakeholder_classification": "internal" | "external",
  "stakeholder_type": "INVESTOR" | "NETWORKING" | "FOUNDER" | null,
  "participants": ["Name 1", "Name 2"],
  "blocks_generated": ["B01", "B08", "B21", "B25", "B26", "B29"],
  "processing_duration_seconds": 60,
  "registry_version": "1.3",
  "granola_diarization": true | false
}
```

**Important:** List blocks in the order they were generated (use `output_order` from registry as reference).

### Step 8: Mark as Processed

1. **Update Google Drive file:**
   - Rename file by adding `[ZO-PROCESSED]` prefix
   - This prevents reprocessing

2. **Move request file:**
   - Move from `N5/inbox/meeting_requests/{meeting_id}_request.json`
   - To `N5/inbox/meeting_requests/processed/{meeting_id}_request.json`

### Step 9: Confirm Completion

Report to V:
- Meeting ID processed
- Number of blocks generated
- List of block codes (B01, B08, etc.)
- Location of output directory

---

## Block Selection Logic (Detailed)

### Internal Meetings
**Core blocks (always generate):**
- B26: MEETING_METADATA_SUMMARY (required)
- B01: DETAILED_RECAP (required)
- B08: RESONANCE_POINTS (required)

**High priority (usually generate):**
- B21: SALIENT_QUESTIONS
- B22: DEBATE_TENSION_ANALYSIS
- B23: STRATEGIC_PRIORITIES_ALIGNMENT
- B05: OUTSTANDING_QUESTIONS (if any open loops)
- B02: COMMITMENTS_CONTEXTUAL (if action items exist)

**Conditional:**
- B24: PRODUCT_IDEA_EXTRACTION (only if product ideas discussed)
- B25: DELIVERABLE_CONTENT_MAP (only if deliverables mentioned)
- B29: KEY_QUOTES_HIGHLIGHTS (if significant quotes exist)

### External Meetings
**Core blocks (always generate):**
- B26: MEETING_METADATA_SUMMARY (required)
- B01: DETAILED_RECAP (required)
- B08: RESONANCE_POINTS (required)

**High priority (usually generate):**
- B21: SALIENT_QUESTIONS
- B28: FOUNDER_PROFILE_SUMMARY (external only)
- B25: DELIVERABLE_CONTENT_MAP (if deliverables mentioned)
- B05: OUTSTANDING_QUESTIONS (if any open loops)
- B02: COMMITMENTS_CONTEXTUAL (if action items exist)

**Medium priority:**
- B29: KEY_QUOTES_HIGHLIGHTS (if significant quotes)
- B04: LINKS_WITH_CONTEXT (if resources shared)

**Conditional:**
- B06: PILOT_INTELLIGENCE (only if pilot discussed)
- B07: WARM_INTRO_BIDIRECTIONAL (only if intros mentioned)
- B11: METRICS_SNAPSHOT (only if data/ROI discussed)
- B13: PLAN_OF_ACTION (only for complex initiatives)
- B14: BLURBS_REQUESTED (only if blurb requested/intro offered)
- B30: INTRO_EMAIL_TEMPLATE (only if Vrijen is introducer)

### Stakeholder-Specific Combinations

If you can confidently identify the stakeholder type, use these predefined combinations from the registry:

**INVESTOR:**
`["B26", "B01", "B08", "B16", "B11", "B13", "B02", "B07", "B04", "B05"]`

**NETWORKING:**
`["B26", "B01", "B08", "B07", "B14", "B04", "B05"]`

**FOUNDER:**
`["B26", "B01", "B08", "B28", "B29", "B24", "B05", "B07", "B14"]`

**COMMUNITY_PARTNER:**
`["B26", "B01", "B08", "B17", "B28", "B02", "B05"]`

---

## Output Format Requirements

### Directory Structure
```
N5/records/meetings/YYYY-MM-DD_stakeholder-name/
├── B01_DETAILED_RECAP.md
├── B02_COMMITMENTS_CONTEXTUAL.md
├── B05_OUTSTANDING_QUESTIONS.md
├── B08_RESONANCE_POINTS.md
├── B21_SALIENT_QUESTIONS.md
├── B25_DELIVERABLE_CONTENT_MAP.md
├── B26_MEETING_METADATA_SUMMARY.md
├── B28_FOUNDER_PROFILE_SUMMARY.md
├── B29_KEY_QUOTES_HIGHLIGHTS.md
├── _metadata.json
└── transcript.txt (copied from inbox)
```

### Block File Format

**With Feedback (when `feedback_enabled: true`):**
```markdown
### DETAILED_RECAP
---
**Feedback**: - [ ] Useful
---

Key decisions and agreements:
• We aligned on [specific outcome with context]
• You confirmed [exact commitment with rationale]
• Both sides agreed that [mutual understanding]
• Next critical step is [specific milestone]
```

**Without Feedback (when `feedback_enabled: false`):**
```markdown
### COMMITMENTS_CONTEXTUAL

| Owner | Deliverable | Context/Why | Due Date | Dependencies |
|-------|------------|-------------|----------|--------------|
| We | [deliverable] | [context] | [date] | [dependencies] |
| [Name] | [deliverable] | [context] | [date] | [dependencies] |
```

---

## Special Format Requirements

### Tables (B02, B11, etc.)
- Use proper markdown table syntax
- Align columns for readability
- Include all columns specified in format

### Lists (B01, B04, B05, B08, etc.)
- Use bullet points (•) or markdown bullets (-)
- Maintain consistent indentation
- Use nested bullets for sub-items (→)

### Headers
- Use `###` (h3) for block name
- Use horizontal rules (`---`) to separate feedback section
- Use `**bold**` for field labels

### Quotes (B29)
- Use markdown blockquotes (>) for verbatim quotes
- Include speaker attribution
- Provide context for why the quote matters

---

## Validation Checklist

Before marking a meeting as processed, verify:

- [ ] All REQUIRED blocks generated (B01, B08, B26)
- [ ] Block files use `B##_BLOCKNAME.md` naming convention
- [ ] All blocks follow exact format from registry
- [ ] Feedback checkboxes included where `feedback_enabled: true`
- [ ] No template system artifacts (no lowercase_underscored names)
- [ ] No consolidated `blocks.md` file (each block separate)
- [ ] `_metadata.json` includes `blocks_generated` array
- [ ] `_metadata.json` includes `registry_version: "1.3"`
- [ ] Transcript copied to meeting directory
- [ ] Google Drive file marked with `[ZO-PROCESSED]`
- [ ] Request moved to `processed/` folder

---

## Error Handling

### If transcript download fails:
- Log error to conversation workspace
- Do NOT move request to processed
- Report to V with specific error
- Leave request for retry

### If block generation fails:
- Log which blocks were successfully generated
- Save partial results
- Report to V with specific error
- Do NOT mark as processed

### If meeting_id is malformed:
- Report to V immediately
- Do NOT process
- Ask for manual intervention

---

## Integration Points

### Upstream
- **`transcript-auto-processor`**: Creates request files in inbox

### Downstream
- **`meeting-approve`**: Displays generated blocks for review
- **`deliverable-generate`**: Uses blocks to create deliverables
- **`follow-up-email-generator`**: Consumes block data for emails

---

## Related Commands

- `meeting-approve` - Review and approve generated blocks
- `deliverable-generate` - Generate deliverables from blocks
- `transcript-ingest` - Manual transcript ingestion

---

## Version History

### v4.0.0 (2025-10-12)
- **BREAKING CHANGE**: Switched from template system to registry-based system
- All blocks now follow `block_type_registry.json` specifications
- Standardized output format: `B##_BLOCKNAME.md`
- Added feedback checkboxes for enabled blocks
- Removed all template system references
- Added comprehensive block selection logic
- Added stakeholder-specific block combinations

### v3.0.0 (Previous)
- Template-based system (deprecated)

---

## Notes for AI Processors (Zo)

**Remember:**
1. You ARE the processor - this is an instruction manual for YOU
2. The registry is your specification - follow it exactly
3. When in doubt, favor generating a block rather than skipping (unless clearly irrelevant)
4. Quality over speed - take time to extract accurate information
5. If you're unsure about a stakeholder type, use priority-based selection
6. Check conditional triggers carefully - don't generate blocks that don't apply
7. Preserve exact wording from transcript for quotes and key phrases
8. Use judgment for "context" fields - explain WHY things matter, not just WHAT was said

**Common pitfalls to avoid:**
- ❌ Creating a single consolidated `blocks.md` file
- ❌ Using lowercase_underscored naming (old format)
- ❌ Improvising block formats instead of following registry
- ❌ Skipping feedback checkboxes when enabled
- ❌ Generating conditional blocks without triggers
- ❌ Missing required blocks (B01, B08, B26)
- ❌ Incorrect file naming (must be `B##_BLOCKNAME.md`)
