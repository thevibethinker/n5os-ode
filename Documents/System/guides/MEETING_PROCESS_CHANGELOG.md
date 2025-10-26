# Meeting Process System - Changelog

## Version 2.1.0 - 2025-10-09

**Summary**: Process improvements from first production use (Alex Caveny coaching session)

### Added

1. **Advisor Stakeholder Type**
   - New category: `advisor` for coaching/advisory relationships
   - Distinct from `investor` (not evaluating for capital) and `customer_*` (not buying)
   - Use case: Business coaches, mentors, industry advisors

2. **Advice & Realizations Block** (Universal Block)
   - **Purpose**: Capture direct advice given + founder learning moments
   - **Contents**:
     - Direct advice from stakeholder (organized by topic)
     - Founder realizations during conversation (self-described + implicit)
     - Principles extracted from advice
     - Meta-lessons about learning/advising
     - Integration opportunities
   - **Why**: Most valuable coaching insights were HOW advice landed and was integrated, not just WHAT was said
   - **File**: `advice_and_realizations.md`

3. **Semi-Stable Information Extraction** (Essential & Full Modes)
   - **Purpose**: Capture learning that's between "to-do" and "knowledge base"
   - **Categories**:
     - Hypotheses validated/invalidated
     - Strategic constraints discovered
     - Patterns recognized across stakeholders
     - Stakeholder context updates
     - Advice with strategic implications
   - **Why**: Most meeting learning gets lost - either becomes immediate action item (then forgotten) or stays in notes (never synthesized)
   - **File**: `semi_stable_updates.md`
   - **Documentation**: `file 'N5/System Documentation/SEMI_STABLE_INFORMATION_SPEC.md'`

4. **Automatic .docx → .txt Conversion**
   - **Context**: Fireflies.ai transcripts stored as Word documents on Google Drive
   - **Process**: 
     - Download .docx from Google Drive
     - Convert to plain text using pandoc
     - Save both .docx (original) and .txt (working copy) to meeting folder
   - **Why**: Eliminates manual conversion step, ensures consistent text processing
   - **Implementation note**: Use `pandoc file.docx -t plain -o file.txt`

### Changed

1. **Essential Mode Scope Expanded**
   - **Old**: Follow-up email, action items, decisions only
   - **New**: Follow-up email, action items, decisions + advice_and_realizations + semi_stable_updates
   - **Rationale**: Semi-stable extraction is core value, not "nice to have" - should happen even in fast mode
   - **Processing time**: Still ~1 minute (LLM does extraction in parallel)

2. **Output Structure Updated**
   ```
   INTELLIGENCE/
   ├── action_items.md
   ├── decisions.md
   ├── key_insights.md
   ├── advice_and_realizations.md    # NEW
   ├── semi_stable_updates.md        # NEW
   └── stakeholder_profile.md
   ```

### Documentation Added

1. **`SEMI_STABLE_INFORMATION_SPEC.md`**
   - Complete specification of what semi-stable info is
   - Extraction process and quality criteria
   - Examples of good vs. bad extraction
   - Output format templates

2. **`MEETING_PROCESS_CHANGELOG.md`** (this file)
   - Version history with rationale
   - Process improvements from production use

### Implementation Notes

**For future script development**:

```python
# Step 1: Fetch transcript (with auto-conversion)
async def _fetch_transcript(self) -> Tuple[str, Dict[str, Any]]:
    # If Google Drive file
    if is_gdrive_file_id(self.transcript_source):
        docx_path = download_from_gdrive(self.transcript_source)
        
        # Auto-convert .docx to .txt (Fireflies transcripts)
        if docx_path.suffix == '.docx':
            txt_path = docx_path.with_suffix('.txt')
            subprocess.run(['pandoc', str(docx_path), '-t', 'plain', '-o', str(txt_path)])
            content = txt_path.read_text()
            # Save both formats to output dir later
        else:
            content = docx_path.read_text()
    
    # If local file
    else:
        # Similar auto-convert logic
        pass
    
    return content, metadata

# Step 7: Generate blocks (essential mode)
async def _generate_blocks(self, transcript, meeting_info, ...):
    if self.mode == "essential":
        blocks_to_generate = [
            "follow_up_email",
            "action_items", 
            "decisions",
            "advice_and_realizations",  # NEW
            "semi_stable_updates",      # NEW
        ]
    elif self.mode == "full":
        blocks_to_generate = [
            # All essential blocks +
            "key_insights",
            "stakeholder_profile",
            # Conditional blocks...
        ]
    # ...
```

**Block generation for advice_and_realizations**:
```python
# blocks/advice_and_realizations_extractor.py

async def extract_advice_and_realizations(
    transcript: str,
    meeting_info: Dict[str, Any]
) -> str:
    """
    Extract:
    1. Direct advice from stakeholder (with topic categorization)
    2. Founder realizations (self-described + implicit from questions)
    3. Principles extracted from advice
    4. Meta-lessons about learning/advising
    5. Integration opportunities
    
    Focus on:
    - HOW advice was received and integrated
    - WHY specific advice landed (not just what was said)
    - Learning moments visible in conversation
    - Behavior changes signaled by founder
    """
    # LLM prompt with examples from spec
    # Return markdown formatted output
```

**Block generation for semi_stable_updates**:
```python
# blocks/semi_stable_extractor.py

async def extract_semi_stable_info(
    transcript: str,
    meeting_info: Dict[str, Any],
    meeting_history: List[Dict[str, Any]]  # For cross-reference
) -> str:
    """
    Extract semi-stable information:
    1. Hypotheses validated/invalidated (with evidence)
    2. New constraints discovered
    3. Patterns recognized
    4. Stakeholder context updates
    5. Strategic advice with lasting impact
    
    Quality criteria:
    - Specific (cites evidence)
    - Actionable (clear implications)
    - Cumulative (builds on previous knowledge)
    - Falsifiable (could be proven wrong)
    
    See: N5/System Documentation/SEMI_STABLE_INFORMATION_SPEC.md
    """
    # LLM prompt with spec examples
    # Include meeting_history context for cross-reference
    # Return markdown formatted output
```

### Testing Checklist for v2.1.0

When implementing these changes:

- [ ] Test .docx auto-conversion with Fireflies transcript
- [ ] Verify both .docx and .txt saved to output folder
- [ ] Confirm essential mode generates advice_and_realizations block
- [ ] Confirm essential mode generates semi_stable_updates block
- [ ] Validate output format matches specs
- [ ] Test with advisor stakeholder type
- [ ] Verify processing time still ~1 min for essential mode
- [ ] Check metadata correctly tracks new blocks
- [ ] Integration test: Full pipeline with Fireflies .docx from GDrive

### User Feedback Incorporated

**From V (2025-10-09)**:

1. ✅ "Make sure that converting it into text is the default assumption since it's always stored as a word document"
   - Implemented: Auto .docx → .txt conversion
   
2. ✅ "Add a block predicated on either advice that was directly provided to me or things that I self describe as having seen or learned or realized during a conversation"
   - Implemented: advice_and_realizations block
   
3. ✅ "Make sure that the identification and updating of semi-stable information, hypotheses, etc. always takes place even in essential, not just in full"
   - Implemented: Semi-stable extraction in essential mode

### Breaking Changes

**None** - All changes are additive

Existing meeting processing outputs remain compatible. New fields added but old structure preserved.

### Migration Notes

**For existing meetings**:
- Can retroactively process with v2.1.0 to generate new blocks
- Particularly valuable for coaching/advisory sessions
- Command: `N5: meeting-reprocess <meeting_folder> --add-blocks advice_and_realizations,semi_stable_updates`

### Known Limitations

1. **Semi-stable extraction quality depends on meeting type**
   - Best: Coaching, strategy sessions, deep customer conversations
   - Good: Sales meetings with substantial discussion
   - Poor: Quick check-ins, status updates

2. **Cross-meeting synthesis still manual**
   - Semi-stable info extracted per meeting
   - Aggregation across meetings (hypothesis tracking, pattern recognition) still requires manual review
   - Future: Implement hypothesis_log, constraint_register, pattern_library systems

3. **Advice extraction assumes advisory relationship**
   - Works well for coaching, mentorship
   - Less applicable to transactional sales calls
   - May need to suppress or reframe for non-advisory meeting types

### Future Enhancements (Not in v2.1.0)

1. **Hypothesis tracking system**: Central log of all hypotheses across meetings with status, confidence evolution
2. **Constraint register**: Active constraints affecting strategy, expected resolution timeline
3. **Pattern library**: Recognized patterns with sample size, application guidance
4. **Semi-stable synthesis**: Aggregate semi-stable info across meetings to identify meta-patterns
5. **Meeting types**: Internal meetings, team meetings (different stakeholder dynamics)

---

## Version 2.0.0 - 2025-10-09

**Summary**: Complete redesign from v1.0 - block-based architecture, dashboard, list integration

(See original meeting-process.md documentation for details)

---

## Version 1.0.0 - 2025-09-20 (Deprecated)

Initial version - monolithic processing, basic action item extraction

(Superseded by v2.0 architecture)
