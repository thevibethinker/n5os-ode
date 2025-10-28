# Content Map Evaluation Rubric

This rubric evaluates the quality and accuracy of content maps extracted from meeting transcripts based on their faithfulness to the original content, minimization of hallucinations, and practical utility.

## Evaluation Criteria

### 1. Transcript Accuracy (30 points)
**Definition**: How accurately the content map reflects the actual content, statements, and timeline of the original transcript.

**Scoring Guidelines**:
- **90-100% accuracy (26-30 points)**: All key statements, decisions, and commitments are captured with verbatim quotes and accurate timestamps
- **70-89% accuracy (18-25 points)**: Most statements are accurate but some minor details are missing or slightly imprecise
- **50-69% accuracy (10-17 points)**: Several important details are misrepresented or missing
- **<50% accuracy (0-9 points)**: Major inaccuracies, statements attributed to wrong speakers, or completely fabricated information

### 2. Hallucination Detection (25 points)
**Definition**: The presence of hallucinated content not found in the transcript - information, decisions, or concepts that weren't actually discussed.

**Scoring Guidelines**:
- **No hallucinations (23-25 points)**: All content can be traced back to transcript evidence
- **Minimal hallucinations (17-22 points)**: 1-2 minor hallucinated details that don't affect core meaning
- **Some hallucinations (8-16 points)**: 3-5 hallucinated elements that may mislead interpretation
- **Significant hallucinations (0-7 points)**: Multiple fabricated items, entire topics, or major commitments invented

### 3. Context Preservation (20 points)
**Definition**: How well the content map preserves the surrounding context of statements, ensuring they're not taken out of context or misinterpreted.

**Scoring Guidelines**:
- **Excellent context (18-20 points)**: Each statement includes appropriate context and nuance
- **Good context (14-16 points)**: Most statements have adequate context, minimal misinterpretation risk
- **Mediocre context (8-13 points)**: Some statements lack context that could lead to misinterpretation
- **Poor context (0-7 points)**: Many statements are decontextualized or likely to be misunderstood

### 4. Completeness of Capture (15 points)
**Definition**: How comprehensively the content map captures the key elements discussed in the meeting.

**Scoring Guidelines**:
- **Highly complete (13-15 points)**: All major decisions, commitments, and topic areas captured
- **Mostly complete (9-12 points)**: Most important elements captured, some minor elements missed
- **Partially complete (5-8 points)**: Several significant elements missing
- **Incomplete (0-4 points)**: Many key elements not captured

### 5. Structure & Usability (10 points)
**Definition**: How well the content map is organized for practical use, with clear categorization and searchability.

**Scoring Guidelines**:
- **Excellent structure (9-10 points)**: Well-organized with clear indices, topics, and navigation
- **Good structure (7-8 points)**: Generally well-organized with minor usability issues
- **Fair structure (4-6 points)**: Some organization problems, could be more useful
- **Poor structure (0-3 points)**: Poorly organized, difficult to use effectively

## Evaluation Process

1. **Line-by-line verification**: Check each claim against transcript at specific timestamps
2. **Context verification**: Ensure statements are interpreted in their original context
3. **Completeness check**: Identify any major topics or decisions not captured
4. **Usability assessment**: Evaluate how easily the content map can be used for follow-up actions

## Scoring Interpretation

- **90-100 points**: Excellent content map - highly accurate and useful
- **75-89 points**: Good content map - useful with minor issues
- **60-74 points**: Fair content map - serviceable but needs improvement
- **<60 points**: Poor content map - unreliable and should not be used

## Red Flags (Automatic Quality Issues)

- Statements attributed to wrong speakers
- Decisions or commitments not actually made
- Major timeline inconsistencies
- Complete fabrication of topics or discussions
- Evidence of hallucination of business relationships or agreements

## Notes
- All verbatim quotes should be exact matches to transcript
- Time ranges should accurately reflect when topics were discussed
- Confidence scores should be justified by evidence quality
- Missing context is often more problematic than minor inaccuracies