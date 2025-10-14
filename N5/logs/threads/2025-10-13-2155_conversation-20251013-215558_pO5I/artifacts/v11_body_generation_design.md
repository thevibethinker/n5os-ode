# v11.0 Email Body Generation - Design Specification

**Date:** 2025-10-13 17:55 ET  
**Status:** Design Phase  
**Principles Loaded:** Core, Safety, Quality

---

## Phase 1: Requirements & Context

### Problem Statement
Current email generation system generates headers + metadata but email body is placeholder. Need to implement v11.0 specification features for complete automation.

### Success Criteria
1. Generate complete email drafts (header + body + footer) automatically
2. Implement all v11.0 command spec features:
   - Resonant details extraction
   - Transcript language echoing
   - Confidence-based link insertion
   - Enhanced dial-based tone calibration
   - Master voice engine application
   - Compression pass
3. Pass validation: FK ≤10, avg sentence 16-22 words
4. Test with Hamoon meeting produces comparable output to manual v11-1_TEST email

### Constraints
- Must integrate with existing tag/dial pipeline (keep that working)
- No external LLM API calls (I AM the LLM)
- Must follow architectural principles (especially P0, P7, P15, P18, P19)
- User prefers Python for scripts
- Must be non-interactive (for automation)

### Scope
**In Scope:**
- Implement body generation following v11.0 spec
- Transcript loading and analysis
- Resonant details extraction
- Link insertion logic
- Tone calibration based on dials
- Readability validation
- Integration with existing pipeline

**Out of Scope:**
- Changing tag extraction (works already)
- Changing dial mapping (works already)
- V-OS tag generation (works already)
- Gmail API integration
- Interactive refinement loops

---

## Phase 2: Architectural Review

### Principle Compliance Check

- [x] **P0 Rule-of-Two:** Will load voice.md + style constraints for generation context
- [x] **P2 SSOT:** Links from essential-links.json, voice from voice.md
- [x] **P5 Anti-overwrite:** Generate to new file or _DRAFT suffix
- [x] **P7 Dry-run:** Add `--dry-run` flag to test without writing
- [x] **P8 Minimal Context:** Only load what's needed for each step
- [x] **P11 Failure Modes:** Document what happens if transcript missing, profile missing, etc.
- [x] **P15 Complete Before Claiming:** Clear checklist - all v11 steps implemented
- [x] **P16 No Invented Limits:** Don't assume API limits or constraints not in docs
- [x] **P17 Test Production:** Test with real meeting (Hamoon)
- [x] **P18 State Verification:** Verify file written, size > 0, valid markdown
- [x] **P19 Error Handling:** Try-catch for file I/O, transcript parsing, missing data
- [x] **P20 Modular:** Separate functions for each v11 step
- [x] **P21 Document Assumptions:** Docstrings explain what each function assumes

---

## Phase 3: Design Specification

### System Architecture

```
Input: meeting_folder, recipient_email
  ↓
[Existing Pipeline - Keep Intact]
  ↓ query_stakeholder_tags.py
Tags Extracted
  ↓ map_tags_to_dials.py  
Dial Settings
  ↓ map_tags_to_vos.py
V-OS Tags
  ↓
[NEW: Body Generation Pipeline]
  ↓ load_transcript()
  ↓ load_stakeholder_profile()
  ↓ extract_resonant_details(transcript, profile)
  ↓ extract_language_patterns(transcript)
  ↓ select_confident_links(profile, links_db)
  ↓ generate_email_body(dials, resonance, language, links, voice, style)
  ↓ apply_compression_pass(body, target_length)
  ↓ validate_readability(body)
  ↓
Output: Complete email draft
```

### File Structure

**New file:**
```
N5/scripts/email_body_generator.py
```

**Purpose:** Modular functions for each v11 step

**Functions:**
1. `load_transcript(meeting_folder) -> str`
2. `extract_resonant_details(transcript, profile) -> Dict`
3. `extract_language_patterns(transcript) -> List[str]`
4. `select_confident_links(profile, confidence_threshold=0.75) -> List[Dict]`
5. `generate_email_body(context: Dict) -> str`
6. `apply_compression_pass(body: str, target_words: int) -> str`
7. `validate_readability(body: str) -> Dict[str, float]`

**Modified file:**
```
N5/scripts/generate_followup_email_draft.py
```

**Changes:**
- Import email_body_generator functions
- Call body generation after dial calibration
- Integrate generated body into draft template
- Add `--dry-run` flag
- Add readability validation

**Configuration files used (no changes):**
- `N5/prefs/communication/voice.md` (v3.0.0)
- `N5/docs/EMAIL_GENERATOR_STYLE_CONSTRAINTS.md` (v1.1.0)
- `N5/prefs/communication/essential-links.json` (v1.7.0)
- `N5/config/tag_dial_mapping.json` (v1.0.0)

### Data Flow

**Step 1: Load Context**
```python
transcript = load_transcript(meeting_folder)
profile = load_stakeholder_profile(meeting_folder)
dial_settings = get_dial_settings(recipient_email, meeting_folder)
```

**Step 2: Extract Resonance**
```python
resonance = extract_resonant_details(transcript, profile)
# Returns: {
#   "shared_values": [...],
#   "pain_points_mentioned": [...],
#   "specific_requests": [...],
#   "key_quotes": [...]
# }
```

**Step 3: Extract Language Patterns**
```python
language_patterns = extract_language_patterns(transcript)
# Returns: ["distinctive phrase 1", "phrase 2", ...]
```

**Step 4: Select Links**
```python
links = select_confident_links(profile, essential_links_db, threshold=0.75)
# Returns: [{"url": "...", "context": "...", "confidence": 0.85}, ...]
```

**Step 5: Generate Body**
```python
body = generate_email_body({
    "dial_settings": dial_settings,
    "resonance": resonance,
    "language_patterns": language_patterns,
    "links": links,
    "voice_guidelines": voice_md,
    "style_constraints": style_constraints_md
})
```

**Step 6: Compress & Validate**
```python
body = apply_compression_pass(body, target_words=300)
readability = validate_readability(body)
if readability["flesch_kincaid"] > 10:
    # Simplify
    body = simplify_language(body)
```

### Error Handling

**Scenarios:**

1. **Transcript missing**
   - Log warning
   - Generate email without resonant details
   - Include disclaimer in draft

2. **Profile missing**
   - Use default dial settings (already implemented)
   - Skip profile-specific resonance
   - Continue with generic tone

3. **Links database missing**
   - Skip link insertion
   - Log warning
   - Continue without links

4. **Voice/style files missing**
   - Use hardcoded defaults
   - Log error
   - Continue with fallback

5. **Readability validation fails**
   - Log warning with specific metrics
   - Include validation results in draft header
   - Don't block generation

**Recovery:**
- All errors are non-blocking
- Generate best possible email with available data
- Log what's missing for debugging
- Include metadata about what features were used/skipped

### Testing Strategy

**Dry-Run:**
```bash
python N5/scripts/generate_followup_email_draft.py \
  --email hamoon@futurefit.ai \
  --meeting-folder N5/records/meetings/2025-10-10_hamoon-ekhtiari-futurefit \
  --dry-run
```

**Output:** Preview of generated email without writing file

**Production Test:**
```bash
python N5/scripts/generate_followup_email_draft.py \
  --email hamoon@futurefit.ai \
  --meeting-folder N5/records/meetings/2025-10-10_hamoon-ekhtiari-futurefit
```

**Validation:**
1. File created ✓
2. File size > 1000 bytes ✓
3. Contains all sections (greeting, body, closing, V-OS tags) ✓
4. Readability FK ≤ 10 ✓
5. Avg sentence length 16-22 words ✓
6. Compare to manual v11-1_TEST email ✓

---

## Phase 4: Implementation Approach

### Step-by-Step Plan

**1. Create email_body_generator.py (30 min)**
- Skeleton with all functions
- Docstrings with assumptions
- Error handling placeholders

**2. Implement data loading functions (15 min)**
- load_transcript()
- load_stakeholder_profile()
- Test with Hamoon meeting

**3. Implement resonance extraction (45 min)**
- Parse transcript for shared values
- Extract pain points
- Identify specific requests
- Pull relevant quotes

**4. Implement language echoing (30 min)**
- Extract distinctive phrases from transcript
- Filter for authenticity (not generic)
- Return top 5-10 patterns

**5. Implement link selection (20 min)**
- Load essential-links.json
- Match profile context to link relevance
- Filter by confidence threshold
- Return sorted by confidence

**6. Implement body generation (60 min)**
- Load voice + style constraints
- Structure email based on dial settings
- Integrate resonance, language, links
- Apply tone calibration

**7. Implement compression (30 min)**
- Count words
- Remove redundancy
- Preserve key information
- Target 250-350 words

**8. Implement readability validation (20 min)**
- Calculate Flesch-Kincaid
- Calculate avg sentence length
- Return metrics dict

**9. Integration with main script (30 min)**
- Update generate_followup_email_draft.py
- Add body generation call
- Wire up data flow
- Add --dry-run flag

**10. Testing (45 min)**
- Dry-run test
- Production test with Hamoon
- Compare to manual email
- Iterate if needed

**Total: ~5 hours**

---

## Phase 5: Validation Checklist

### Feature Completeness
- [ ] All v11.0 steps implemented
- [ ] Transcript loading
- [ ] Resonance extraction
- [ ] Language echoing
- [ ] Link insertion (confidence-based)
- [ ] Dial-based tone calibration
- [ ] Voice engine application
- [ ] Compression pass
- [ ] Readability validation

### Quality Checks
- [ ] FK ≤ 10
- [ ] Avg sentence 16-22 words
- [ ] No invented constraints (P16)
- [ ] Error handling complete (P19)
- [ ] State verification (P18)
- [ ] Production config tested (P17)

### Integration
- [ ] Works with existing tag pipeline
- [ ] Preserves dial calibration
- [ ] V-OS tags still generated
- [ ] File structure maintained
- [ ] No breaking changes

### Documentation
- [ ] Docstrings complete
- [ ] Assumptions documented (P21)
- [ ] Error scenarios documented
- [ ] Usage examples provided
- [ ] Integration guide updated

---

## Key Decisions

### 1. Resonance Extraction Method
**Decision:** Rule-based extraction + pattern matching (not ML)
**Rationale:** 
- Simpler, more transparent
- No external dependencies
- Sufficient for current use case
- Can upgrade to ML later if needed

### 2. Language Echoing Implementation
**Decision:** Extract distinctive phrases from transcript, avoid generic business-speak
**Rationale:**
- Adds authenticity
- Shows attention to conversation
- Matches v11.0 spec

### 3. Link Confidence Threshold
**Decision:** 0.75 default, configurable
**Rationale:**
- Prevents spurious links
- Matches v11.0 spec requirement
- Can adjust per stakeholder type

### 4. Compression Strategy
**Decision:** Target 250-350 words, preserve key info > length target
**Rationale:**
- Matches voice.md guidelines
- Prevents over-compression
- Maintains substance

### 5. Error Handling Philosophy
**Decision:** Non-blocking, generate best possible with available data
**Rationale:**
- Partial automation > no automation
- Log warnings for debugging
- Don't fail if one feature unavailable

---

## Risk Assessment

**LOW RISK:**
- Integration with existing pipeline (well-defined interfaces)
- File I/O (standard operations with error handling)
- Configuration loading (already working)

**MEDIUM RISK:**
- Resonance extraction quality (subjective, needs testing)
- Language echoing effectiveness (may need tuning)
- Compression algorithm (balance substance vs length)

**MITIGATION:**
- Test with multiple meetings
- Compare to manual emails
- Iterate based on feedback
- Start conservative, refine over time

---

## Success Metrics

1. **Automated generation rate:** 100% of meetings with transcript
2. **Readability:** FK ≤ 10 in 95%+ of generated emails
3. **User acceptance:** Generated emails require minimal editing
4. **Integration:** No breaking changes to existing pipeline
5. **Performance:** Generation time < 30 seconds

---

**Ready to implement:** Yes  
**Principles compliance:** ✓  
**Clear definition of done:** ✓  
**Error handling designed:** ✓  
**Testing strategy defined:** ✓

