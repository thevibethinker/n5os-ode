---
title: Communications Generator
description: "Generate send-ready follow-up emails and blurbs for meetings in [P] state, using V's voice transformation system and full Careerspan context"
tags:
  - meeting-intelligence
  - communications
  - email
  - blurbs
  - pipeline-2
  - voice-system
tool: true
created: 2025-11-16
last_edited: 2025-11-16
version: 2
---
# Communications Generator (Pipeline 2)

## Purpose

Generate **send-ready outbound communications** (follow-up emails and blurbs) for meetings that have completed intelligence extraction ([P] state). Uses powerful model with full Careerspan context **and V's voice transformation system**.

---

## When To Run

**Trigger conditions:**
- Meeting folder is in `[P]` state (all intelligence blocks complete)
- AND at least one of:
  - B25 exists AND "Follow-Up Email Needed = YES"
  - B14 exists (blurbs were requested)

**Do NOT run if:**
- Folder is not in [P] state
- Neither B14 nor B25 exists
- B25 exists but "Follow-Up Email Needed = NO"

---

## Context Loading (Sequential)

### 1. Voice Transformation System (FIRST - CRITICAL)
```bash
# Load voice system - REQUIRED for authentic V voice
cat /home/workspace/N5/prefs/communication/voice-transformation-system.md
cat /home/workspace/N5/prefs/communication/voice-system-prompt.md
```

### 2. Knowledge/current/ (Careerspan Context)
```bash
# Load ALL documents from Knowledge/current/ - this is V's context dumping ground
# Contains positioning, value props, recent wins, active initiatives
if [ -d "/home/workspace/Knowledge/current" ]; then
  for doc in /home/workspace/Knowledge/current/*; do
    if [ -f "$doc" ]; then
      echo "=== CONTEXT: $(basename $doc) ==="
      cat "$doc"
      echo ""
    fi
  done
else
  echo "⚠️  WARNING: Knowledge/current/ is empty - communications will lack current Careerspan context"
fi
```

---

## Voice Transformation System

**CRITICAL:** All communications MUST use V's authentic voice through transformation system.

### System Files
- Transformation system: `file 'N5/prefs/communication/voice-transformation-system.md'`
- System prompt: `file 'N5/prefs/communication/voice-system-prompt.md'`
- Few-shot examples: Built into transformation system (5 transformation pairs)

### Transformation Process

**For Every Communication:**

1. **Style-Free Draft First:**
   - Generate factual, personality-free content
   - Strip warmth, personality, filler
   - Keep only core facts and requests
   - Use neutral, robotic language

2. **Load Transformation Pairs:**
   - Use 2-3 relevant examples from voice system
   - For emails: PAIR 1, 2, 3, 5 (professional communication)
   - For blurbs: Adapt PAIR 3 (ask for introduction style)
   - Format: style-free → authentic V voice

3. **Transform:**
   - Apply learned pattern to generate V's voice
   - Maintain all facts from style-free draft
   - Add personality, warmth, natural flow
   - Use V's structural patterns (em-dashes, semicolons, etc.)

4. **Validate Against Anti-Patterns:**
   - ❌ No emoji in professional email
   - ❌ No single-sentence paragraphs (LinkedIn effect)
   - ❌ No performative vulnerability
   - ❌ No corporate jargon: "synergy", "leverage", "paradigm"
   - ❌ No desperate or pushy language
   - ❌ No generic flattery

### Voice Quality Checklist

**Before presenting output:**
- [ ] Opens with warmth or rapport (not cold)
- [ ] Uses specific details for credibility
- [ ] Reduces pressure on recipient
- [ ] Natural transitions (em-dashes, semicolons)
- [ ] Personality without being performative
- [ ] Flows naturally (not choppy)
- [ ] Avoids all anti-patterns
- [ ] Sounds like something V would actually write

---

## Generation Tasks

### Task 1: Follow-Up Email (if B25 triggers it)

**Input:**
- B25 table (deliverables promised)
- B08 (stakeholder intelligence, resonance)
- Transcript (meeting tone and dynamics)
- Knowledge/current/ (Careerspan positioning)
- **Voice transformation system** (V's authentic voice)

**Output:**
- File: `FOLLOW_UP_EMAIL.md`
- Location: Same folder as meeting blocks
- Status: Send-ready (V can copy-paste to email client)

**Generation Process:**

**Step 1: Style-Free Draft**
```
Generate factual email content:
- List deliverables from B25
- Note next steps
- Include any key points
- NO personality, NO warmth, NO style
Example style-free:
"I am sending the deliverables discussed. Please find attached X and Y. The next step is Z."
```

**Step 2: Load Relevant Transformation Pairs**
```
From voice-transformation-system.md:
- PAIR 1: Professional Introduction (warmth + specific details)
- PAIR 2: Apologetic Update (natural flow + personality)
- PAIR 3: Ask for Introduction (credibility + low pressure)
- PAIR 5: Brief Apology (if >2 days since meeting)
```

**Step 3: Transform to V's Voice**
```
Apply learned pattern:
- Add opening warmth
- Use specific callback to meeting moment
- Incorporate natural transitions
- Reduce pressure on recipient
- Sign off naturally
```

**Requirements:**

1. **Voice-First Structure:**
   - Subject line (specific, actionable)
   - Opening (warmth appropriate to relationship - from transformation pairs)
   - Meeting callback (specific moment from transcript)
   - Deliverables section (organized, natural language)
   - Next steps (low-pressure framing)
   - Closing (authentic V style)

2. **Voice Patterns to Apply:**
   - **Opening:** "Hope you're doing well!" or "Man, I know you're busy"
   - **Credibility markers:** Specific numbers, lived experience
   - **Pressure reduction:** "No pressure though", "if it makes sense"
   - **Transitions:** Em-dashes for asides, semicolons for related thoughts
   - **Personality:** Occasional humor, natural abbreviations
   - **Closing:** Gratitude before asks, low-pressure exit

3. **Style Requirements:**
   - **Length:** 150-250 words (concise but complete)
   - **Readability:** Conversational, natural flow
   - **Warmth:** Calibrated to B08 resonance level
   - **Authenticity:** Sounds like V actually wrote it

4. **Content Integration:**
   - Reference specific deliverables from B25 table
   - Incorporate Careerspan positioning from Knowledge/current/ naturally
   - Align messaging with stakeholder's stated interests (from B08)
   - Weave in recent wins/traction subtly (if relevant)

5. **Quality Standards:**
   - No generic platitudes
   - Specific callback to actual meeting moment
   - Deliverables clearly listed (bullets or natural flow)
   - No marketing speak unless stakeholder prefers that
   - Voice transformation validated against anti-patterns

**Example Structure:**
```markdown
---
created: 2025-11-16
last_edited: 2025-11-16
version: 1.0
voice_system: applied
---

# Follow-Up Email Draft

**To:** [Stakeholder Name]  
**Subject:** [Specific subject line]  
**Voice Transformation:** Applied (PAIR 1, 2)  
**Status:** Ready to send

---

**Subject:** [Subject line here]

Hope you're doing well!

[Specific callback to meeting moment - natural V style]

[Deliverables section - natural language with V's patterns]

[Careerspan positioning woven in naturally]

[Next steps with pressure reduction]

[Authentic closing]

Best,
V

---

## Voice Quality Checklist

Generated using transformation system:
- [x] Style-free draft created first
- [x] Transformation pairs applied (PAIR 1, 2)
- [x] Opens with warmth/rapport
- [x] Specific details for credibility
- [x] Pressure reduction present
- [x] Natural transitions (em-dashes/semicolons)
- [x] No anti-patterns detected
- [x] Sounds like V wrote it

## Content Checklist

Please review before sending:
- [ ] Subject line is specific and compelling
- [ ] Meeting callback feels authentic
- [ ] All deliverables from B25 included
- [ ] Tone matches relationship stage (from B08)
- [ ] Careerspan positioning natural, not forced
- [ ] Length appropriate (150-250 words)
- [ ] No typos or awkward phrasing
```

---

### Task 2: Blurbs Generation (if B14 exists)

**Input:**
- B14 (what was requested, by whom, for what purpose)
- B08 (stakeholder intelligence)
- Transcript (context)
- Knowledge/current/ (Careerspan positioning)
- **Voice transformation system** (adapted for professional/doc tone)

**Output:**
- File: `BLURBS_GENERATED.md`
- Location: Same folder as meeting blocks
- Status: Copy-paste ready

**Generation Process:**

**Step 1: Style-Free Draft (Each Blurb)**
```
Generate factual content:
- What Careerspan does
- Key benefits
- Current traction
- Relevant differentiators
- NO style, NO warmth, just facts
```

**Step 2: Adapt Voice System**
```
For blurbs, adapt transformation system:
- More formal than email
- Less conversational than social
- Still V's voice but polished
- Use PAIR 3 style (credibility + specifics)
- Professional without being corporate
```

**Step 3: Transform to Polished V Voice**
```
Apply transformation:
- Add credibility markers (numbers, specifics)
- Natural flow (not choppy bullets)
- Professional but authentic
- No jargon, no fluff
```

**Requirements:**

1. **One Section Per Blurb:**
   - Title (what it is, who requested it)
   - Target audience noted
   - Voice transformation note
   - The actual blurb (formatted for copying)
   - Usage notes if needed

2. **Voice Quality (Adapted):**
   - Professional polish (more formal than emails)
   - Credibility markers prominent
   - Natural flow (not marketing speak)
   - Specific details (numbers, experience)
   - No corporate jargon
   - V's authentic voice but business-appropriate

3. **Quality Standards:**
   - Match requested length exactly (if specified)
   - Tailor to target audience (from B14)
   - Emphasize focal points (from B14 "Key focus" field)
   - Use current positioning from Knowledge/current/
   - Match tone to usage context

4. **Format Example:**
```markdown
---
created: 2025-11-16
last_edited: 2025-11-16
version: 1.0
voice_system: applied_professional
---

# Generated Blurbs

**Meeting:** [Stakeholder Name] - [Date]  
**Total Blurbs:** [Number]  
**Voice Transformation:** Applied (professional adaptation)

---

## 1. [Type of Material] for [Requestor Name]

**Target Audience:** [From B14]  
**Purpose:** [From B14]  
**Tone:** Professional/polished V voice  
**Length:** [Actual word count]

### The Blurb

[Blurb content - transformation applied]

**Voice Notes:**
- Credibility markers included: [specific numbers/experience]
- Natural flow maintained (not marketing copy)
- Tailored to: [target audience specifics]

### Usage Notes
- [Context V needs]
- [E.g., "Jennifer will use in board deck"]

---

## Voice Quality Validation

For each blurb:
- [x] Style-free draft created
- [x] Professional voice transformation applied
- [x] Credibility markers included
- [x] Natural flow (not choppy)
- [x] No corporate jargon
- [x] Specific to target audience
- [x] Copy-paste ready

## Content Checklist

Please review:
- [ ] Each blurb matches requested length
- [ ] Tone appropriate for audience
- [ ] Key focus areas emphasized
- [ ] Current positioning incorporated
- [ ] Professional but authentic
```

---

## Model Selection

**Recommended:** Claude Opus (Sonnet-4 if Opus unavailable)

**Why:**
- Best at nuanced voice transformation
- Excellent at few-shot learning
- Strong at maintaining authenticity
- Can balance multiple context sources
- High quality voice without over-engineering

**Alternative:** GPT-4 or o1-preview if Opus unavailable

**NOT recommended:**
- Standard models (can't handle voice transformation well)
- Fast/cheap models (voice quality will suffer)

---

## State Management

### Finding Folders to Process

```bash
# Find folders in [P] state that need communications
find /home/workspace/Personal/Meetings/Inbox -maxdepth 1 -type d -name "*_[P]" | while read folder; do
  # Check if communications needed (B14 or B25 exists)
  if [ -f "$folder/B14_BLURBS_REQUESTED.md" ] || [ -f "$folder/B25_DELIVERABLE_CONTENT_MAP.md" ]; then
    # Check if already processed (outputs exist)
    needs_processing=false
    
    if [ -f "$folder/B14_BLURBS_REQUESTED.md" ] && [ ! -f "$folder/BLURBS_GENERATED.md" ]; then
      needs_processing=true
    fi
    
    if [ -f "$folder/B25_DELIVERABLE_CONTENT_MAP.md" ] && [ ! -f "$folder/FOLLOW_UP_EMAIL.md" ]; then
      needs_processing=true
    fi
    
    if [ "$needs_processing" = true ]; then
      echo "Processing: $(basename $folder)"
      # Generate communications here
      break  # Process one folder per run
    fi
  fi
done
```

### On Success

1. Verify outputs created:
   - `FOLLOW_UP_EMAIL.md` exists (if B25 triggered it)
   - `BLURBS_GENERATED.md` exists (if B14 triggered it)
   - Both have voice transformation validation sections

2. Update folder state:
   ```bash
   # Rename folder from [P] to [R]
   folder_path="/home/workspace/Personal/Meetings/Inbox/2025-11-16_Meeting_Example_[P]"
   new_path="${folder_path%_[P]}_[R]"
   mv "$folder_path" "$new_path"
   echo "✓ State transition: [P] → [R]"
   echo "✓ $(basename $new_path) ready for deployment"
   ```

3. Log completion:
   ```bash
   echo "[$(date)] Communications generated for $(basename $new_path) (voice system applied)" >> /home/.z/workspaces/con_MMUy9beXziOyCQC5/communications.log
   ```

### On Failure

1. **Retry logic:**
   - Attempt 3 times before escalating
   - Wait 30 seconds between retries
   - Verify voice system files loaded

2. **If 3 retries fail:**
   - Create `_COMMUNICATIONS_FAILED.md` with error details
   - Keep folder in [P] state
   - Alert for manual review
   - Do NOT block access to intelligence blocks

3. **Common failure modes:**
   - Voice system files missing → Check N5/prefs/communication/
   - Knowledge/current/ empty → Warn V to populate
   - B08 missing → Can't personalize, use generic voice
   - Model timeout → Retry with same context

---

## Quality Control

### Pre-Flight Checks

**Before generating, verify:**
- [ ] Voice transformation system files loaded
- [ ] Folder is in [P] state
- [ ] All intelligence blocks exist
- [ ] B08 exists (required for personalization)
- [ ] Knowledge/current/ has at least 1 file
- [ ] Outputs don't already exist (idempotent)

### Post-Generation Validation

**After generating, verify:**
- [ ] Output files exist in correct location
- [ ] Files have proper frontmatter
- [ ] Voice transformation validation sections present
- [ ] No anti-patterns detected
- [ ] Length appropriate
- [ ] No placeholder text like "[NAME]" or "[TODO]"
- [ ] Sounds like V would actually write this

---

## Integration Points

### With Voice System

**Always loads:**
- `N5/prefs/communication/voice-transformation-system.md`
- `N5/prefs/communication/voice-system-prompt.md`

**Process:**
- Style-free draft → Transformation pairs → V's voice
- Validate against anti-patterns
- Ensure natural flow and authenticity

### With Pipeline 1 (Intelligence)

**Depends on:**
- B08 (STAKEHOLDER_INTELLIGENCE) - required
- B25 (DELIVERABLE_CONTENT_MAP) - optional
- B14 (BLURBS_REQUESTED) - optional

**Triggered by:**
- Folder reaching [P] state
- At least one of B14/B25 exists

### With Knowledge System

**Always loads:**
- Everything in Knowledge/current/ folder

**Why:**
- Guaranteed up-to-date Careerspan context
- V controls exactly what's referenced
- Single dumping ground for communications context

### With State Machine

**Input state:** [P] (Processing complete - intelligence done)  
**Output state:** [R] (Ready for deployment - communications done)

**Next step:**
- Folder moves to final destination
- Communications ready for V to send

---

## Success Criteria

**Communications Generator is successful when:**

1. **Voice Quality:** Emails/blurbs sound like V actually wrote them
2. **Minimal Edits:** V can send with 0-2 tweaks
3. **Accuracy:** All deliverables included, all requests fulfilled
4. **Tone Match:** Matches relationship stage from B08
5. **Context Integration:** Careerspan positioning woven naturally
6. **Efficiency:** Generates in <3 minutes per meeting (voice system adds time)
7. **Reliability:** <5% failure rate, successful voice transformation

**Voice System Success:**
- No anti-patterns present
- Natural flow and authenticity
- Pressure reduction present
- Credibility markers included
- Sounds genuinely like V

---

## Troubleshooting

### Issue: Generated email doesn't sound like V

**Diagnosis:**
- Voice transformation system not loaded
- Style-free draft skipped
- Wrong transformation pairs used
- Anti-patterns present

**Fix:**
- Verify voice system files loaded first
- Generate style-free draft explicitly
- Use PAIR 1, 2, 3, 5 for emails
- Validate against anti-patterns checklist

---

### Issue: Blurbs sound too corporate

**Diagnosis:**
- Not adapting voice system properly
- Using marketing language
- Missing credibility markers

**Fix:**
- Adapt transformation system (professional not corporate)
- Remove jargon: "synergy", "leverage", "paradigm"
- Add specific numbers and lived experience
- Use PAIR 3 style (specific + credible)

---

### Issue: Voice transformation taking too long

**Diagnosis:**
- Multiple style-free → voiced iterations
- Over-engineering the transformation

**Fix:**
- Generate style-free once
- Apply transformation once
- Validate quickly against anti-patterns
- Don't iterate endlessly

---

## Maintenance

### Weekly
- [ ] Check voice quality on 2-3 emails
- [ ] Verify no anti-patterns slipping through
- [ ] Ensure Knowledge/current/ up-to-date

### Monthly
- [ ] Audit 10-15 communications for voice consistency
- [ ] Gather V's feedback on authenticity
- [ ] Update transformation pairs if needed
- [ ] Refresh Knowledge/current/ positioning

---

**This is Pipeline 2 of the Meeting Intelligence Communications Architecture v2**

**Voice System:** Integrated v2.0 (few-shot transformation)

*Created: 2025-11-16 14:08 EST*  
*Updated: 2025-11-16 14:45 EST (voice system integration)*


