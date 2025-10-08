---
date: "2025-09-20T22:24:55Z"
last-tested: "2025-09-20T22:24:55Z"
generated_date: "2025-09-20T22:24:55Z"
checksum: c648c1c73c6b9d6599506f55f3cc5371
tags: []
category: unknown
priority: medium
related_files: []
anchors: 
input: null
output: /home/workspace/N5_mirror/workflows_register.md
---
# N5 Workflows Register

This register documents workflows for enriching influencer dossiers in `Startup Intelligence/Influencers`. It aligns with N5 ingestion standards (MECE, cross-references, adaptive suggestions) and is designed for eventual command authoring.

## Workflow: Quick Add to Dossier (Record Mode)

### Trigger
- User shares a link with intent to add to a specific influencer's dossier (e.g., "Add to Nate Jones: https://example.com").
- Assumes direction to a particular person for stable, lightweight ingestion.

### Steps
1. **Verify Profile**: Confirm profile exists; if not, create base .md using template.
2. **Light Parsing & Summarization**:
   - Use `read_webpage` for URL (extract title, summary, key points).
   - Generate brief summary (1-2 sentences) of content and relation to influencer/Careerspan.
3. **Append to Dossier**:
   - Add under "Resources" section in .md: Link, description, summary, association (e.g., "Associated with Nate Jones").
   - Tag: `person:[Name]`, `company:Careerspan` if relevant.
   - Ensure MECE: Check for duplicates; cross-reference if lesson emerges.
4. **Log**: Record in register for tracking.

### Tools Used
- `read_webpage`: Parsing.
- `edit_file_llm`: Append to .md.

### Distinction from Deep Enrichment
- Quick: Stable info only; no `deep_research`.
- Deep: Full enrichment with research, lessons extraction.

### Proposed Command
- Syntax: `add-to-dossier <influencer_name> <url> [--deep]`
- Default: Quick mode.
- With `--deep`: Trigger full workflow (research, lessons).
- Future: Integrate via N5 command authoring (update commands.jsonl, regenerate catalog).

## Workflow: Enrich Influencer Dossier

### Trigger
- User shares a link/article/URL related to an influencer (e.g., via message or mention).
- Manual trigger for existing profiles (e.g., "enrich Nate Jones dossier").

### Steps
1. **Identify/Verify Influencer**: Check if profile exists in `/home/workspace/Startup Intelligence/Influencers/[Name]/[Name].md`. If not, create folder and base .md using template.
2. **Parse Input**:
   - Use `read_webpage` for URLs (fetches text, metadata; saves to conversation workspace).
   - Extract: Title, author, summary, key quotes, themes.
3. **Deep Research Enrichment**:
   - Call `deep_research` with instructions: "Research [Influencer Name] in AI/startup/career context. Extract biographical info, key contributions, lessons for Careerspan/V. Include citations. Output structured dossier sections (Resources, Lessons Learned, Relations)."
   - Schema: {"type": "object", "properties": {"resources": {"type": "array"}, "lessons": {"type": "array"}, "relations": {"type": "string"}}}
4. **Update Dossier**:
   - Append to .md: New resources (links, descriptions), lessons (summaries, takeaways), relations to Careerspan/V.
   - Ensure MECE: No duplicates; cross-reference to N5 knowledge (e.g., link to `file 'N5/knowledge/bio.md'` if relevant).
   - Tag entities: `person:[Name]`, `company:Careerspan`.
5. **Document & Adapt**:
   - Log in register: Date, input, actions taken, suggestions for new subcategories (e.g., if AI ethics emerges as theme).
   - If patterns suggest expansion (per ingestion standards), propose updates to structure.

### Tools Used
- `read_webpage`: Initial parsing.
- `deep_research`: Comprehensive enrichment.
- `edit_file_llm`: Update .md files.
- `grep_search`: Verify existing profiles or cross-references.

### Edge Cases
- No profile exists: Prompt user for confirmation before creating.
- Sensitive info: Exclude per standards (e.g., skip unverified rumors).
- Overlap: If lesson relates to V's bio, store primarily in dossier but cross-link.

### Future Integration
- Command authoring: Compact into N5 command (e.g., `enrich-dossier <name> <url>`), updating commands.jsonl and regenerating catalog via `docgen`.

## Workflow: Extract & Store Lessons Separately

### Trigger
- After dossier enrichment or on demand (e.g., "extract lessons from Nate Jones").

### Steps
1. **Aggregate Lessons**: From dossier .md, pull all "Lessons Learned" sections.
2. **Extract & Refine**:
   - Use `deep_research` for: "Extract standalone lessons from [content]. Make them actionable, tag themes (e.g., AI strategy, career navigation). Output as JSON list."
   - Schema: {"type": "array", "items": {"type": "object", "properties": {"lesson": {"type": "string"}, "source": {"type": "string"}, "themes": {"type": "array"}}}}
3. **Store Separately**:
   - Create/Update `/home/workspace/Startup Intelligence/Influencers/[Name]/Lessons/` folder.
   - Save as `lessons.json` or individual .md files for each lesson.
   - Cross-reference back to main dossier.

### Tools Used
- `deep_research`: Lesson extraction.
- `create_or_rewrite_file`: Store lessons.

### Alignment
- Follows ingestion standards: Exhaustive lessons, no overlap, single source.
- Adaptive: Suggest new lesson categories if themes evolve.
## Workflow: Transcript Ingestion and Processing

### Trigger
- CLI command: `transcript-ingest <transcript_source>`
- File upload or Google Drive folder monitoring
- Scheduled batch processing of new transcripts

### Steps
1. **Validate Input**: Confirm transcript source exists and is accessible
2. **Load & Parse**: Extract meeting metadata, speaker lines, and timestamps
3. **Content Mapping**: Generate structured analysis including:
   - Meeting datetime and participants
   - Commitments (my/others/our), decisions, deal context
   - Resonance analysis and warm introduction opportunities
   - Speaker-aware parsing and attribution
4. **Generate Outputs**:
   - Content maps (JSON) with structured metadata
   - Action tickets for deliverables and introductions
   - Communication drafts using MasterVoiceSchema
   - Summary blurbs and workflow reports
5. **Knowledge Integration**: Feed results into N5 knowledge reservoirs
6. **Cleanup**: Remove temporary files and log completion

### Modes
- `load`: Basic parsing and validation
- `map`: Full content mapping and analysis
- `tickets`: Generate action items and deliverables
- `email`: Create communication drafts
- `full`: Complete end-to-end processing

### Tools Used
- `consolidated_transcript_workflow.py`: Main processing engine
- `gdrive_transcript_workflow.py`: Google Drive integration
- `direct_ingestion_mechanism.py`: Knowledge system integration
- `MasterVoiceSchema`: Voice consistency for communications

### Outputs
- Content maps: `/N5/output/content_maps/transcript_content_map_*.json`
- Tickets: `/N5/output/tickets/transcript_tickets_*.json`
- Communications: `/N5/output/communications/transcript_emails_*.md`
- Knowledge updates: Integrated into bio, timeline, facts, sources reservoirs

### Integration Points
- N5 knowledge system (bio, timeline, glossary, sources)
- Google Drive API for folder processing
- MasterVoiceSchema for communication consistency
- Safety layer via `n5_safety.py`
- Execution telemetry via `n5_run_record.py`

### Edge Cases
- Malformed transcripts: Graceful error handling with partial processing
- Speaker identification issues: Manual review prompts
- Large batch processing: Chunked processing with progress tracking
- API rate limits: Exponential backoff and retry logic

### Command Interface
```bash
transcript-ingest /path/to/transcript.txt --mode full
transcript-ingest folder_id --gdrive --output-dir /custom/path
```

### Future Enhancements
- Real-time processing triggers
- Multi-language transcript support
- Advanced speaker diarization
- Integration with calendar systems for meeting context
