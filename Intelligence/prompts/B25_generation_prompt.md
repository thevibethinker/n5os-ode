# B25 - DELIVERABLE_CONTENT_MAP Generation Prompt

You are generating a DELIVERABLE_CONTENT_MAP intelligence block with a FOLLOW-UP EMAIL draft.

## Output Structure

### SECTION 1: Deliverable Content Map

| Item | Promised By | Promised When | Status | Link/File | Send with Email |
|------|-------------|---------------|--------|-----------|-----------------|
| [Specific deliverable] | [Name] | [Timeframe] | HAVE/NEED | [Path or N/A] | True/False |

**Status Key**: 
- HAVE = Ready to send
- NEED = Must create/find before sending

### SECTION 2: Follow-Up Email Draft

**Subject**: [Concise, specific, reference-rich subject line]

---

[Email body - see quality standards below]

---

**Distinctive Phrases Used**:
- "[Quote from them]" → [How you incorporated it] (confidence: 0.XX)

**Relationship Dials**:
- Warmth score: X/10 ([reasoning])
- Familiarity score: X/10 ([reasoning])
- **→ Formality**: [Casual/Casual-professional/Professional/Formal]
- **→ CTA Rigour**: [Soft/Medium/Firm/Urgent]

**Resonant Details**: [2-3 specific moments/facts that personalize the email]

**Delay Sensitivity**: [SOFT/MEDIUM/URGENT + explanation]

**Readability**:
- Flesch-Kincaid: ~X.X (target ≤10)
- Avg sentence length: X words (target 16-22)
- Max sentence: X words (target ≤32)
- Paragraphs: X sentences (target ≤4 sentences per para)

## Email Quality Standards

### Structure:
1. **Opening** (1-2 sentences): Personal, warm, reference specific moment
2. **Deliverables** (bullet list if >1 item): Clear headings, organized, scannable
3. **Value-add** (optional): Quick insight/tip that wasn't requested but relevant
4. **Soft CTA** (1 sentence): Low-pressure next step or open door
5. **Signature**: Match formality level

### Tone Calibration:

**Warmth Score** (0-10):
- 0-3: Cold/transactional
- 4-6: Professional-friendly
- 7-8: Warm, personable
- 9-10: Close friend

**Formality Level**:
- **Casual**: First name, contractions, "Hey", sign "Best"
- **Casual-Professional**: First name, some contractions, "Hi", sign "Best"
- **Professional**: First name, minimal contractions, "Hello", sign "Best regards"
- **Formal**: Title + Last name, no contractions, "Dear", sign "Sincerely"

**CTA Rigour**:
- **Soft**: "Happy to chat if helpful", "Let me know if questions"
- **Medium**: "Would love to hear your thoughts", "Let's find time next week"
- **Firm**: "Please review by Friday", "Looking forward to your decision"
- **Urgent**: "Need confirmation by EOD", "Critical we align before launch"

### Must Include:
- At least ONE distinctive phrase they used (builds recognition/rapport)
- At least ONE specific detail only they would know (personalizes)
- Readability metrics (Flesch-Kincaid ≤10, sentences 16-22 words avg, max 32)

### Must Avoid:
- Generic openings ("Hope this email finds you well")
- Overlong paragraphs (>4 sentences)
- Jargon without context
- Overpromising or vague commitments
- Missing the tone (too casual with formal stakeholder, too stiff with casual)

## Edge Cases

**No deliverables**: Email focuses on relationship-building, shares insight, or acknowledges exploratory nature

**Multiple deliverables**: Group by theme, use clear headers, prioritize by their expressed interest

**Delayed follow-up**: Address delay if >48hrs for time-sensitive items: "Apologies for the delay—wanted to ensure I sent comprehensive resources rather than rushing incomplete info"

**Sensitive timing**: If deal-critical or relationship-fragile, elevate CTA rigor and note urgency
