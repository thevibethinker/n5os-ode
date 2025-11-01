---
description: Generate text content using the voice transformation system with multi-angle
  evaluation and hybrid structure.
tags: []
---
# Command: generate-with-voice
**Version:** 2.0  
**Type:** Content Generation  
**Auto-Applied:** Yes (runs automatically for all text generation)

---

## Purpose

Generate text content using the voice transformation system with multi-angle evaluation and hybrid structure.

---

## Usage

### Automatic (Default)
System automatically detects and applies when user requests text generation:
- "Draft an email to..."
- "Write a blog post about..."
- "Create a document for..."
- "Post this to LinkedIn..."
- "Take notes on..."

**No explicit command needed.**

### Explicit Invocation
```
generate-with-voice <content-type> <request>
```

**Examples:**
```
generate-with-voice email "Tell Sarah about Q4 roadmap delay"
generate-with-voice blog "Article about hiring mistakes"
generate-with-voice social "Post about vulnerable founder journey"
```

### With Override
```
generate-with-voice --override email "Professional update to board"
```

---

## Parameters

**Required:**
- `request`: What content to generate

**Optional:**
- `--type <type>`: Force specific content type (email/blog/doc/social/note)
- `--override`: Use neutral/professional tone instead of voice profile
- `--angle <angle>`: Force specific angle (direct/collaborative/narrative/etc)
- `--show-all`: Show all angle options, not just best
- `--dry-run`: Show process without executing

---

## Process

### Step 1: Detection
```python
from N5.scripts.content_type_detector import ContentTypeDetector

detector = ContentTypeDetector()
result = detector.detect(user_request, context)
content_type = result.content_type
```

### Step 2: Angle Generation
```python
from N5.scripts.angle_generator import AngleGenerator

generator = AngleGenerator()
angles = generator.get_angles(content_type)
# Returns 2-3 distinct messaging angles
```

### Step 3: Style-Free Drafts
For each angle, generate style-free draft:
- Focus on facts and structure
- No voice or personality
- Complete information
- Clear logic flow

### Step 4: Voice Transformation
```python
from N5.scripts.voice_transformer import VoiceTransformer

transformer = VoiceTransformer()
for angle in angles:
    result = transformer.transform(
        content=style_free_draft,
        content_type=content_type,
        angle=angle.name,
        use_override=False
    )
```

Apply hybrid structure:
- v2.0 prose (natural language)
- v1.0 structure (white space, sections)
- Strategic breaks (horizontal rules)

### Step 5: Evaluation
```python
for angle_result in all_results:
    score, strengths, weaknesses = generator.evaluate_angle(
        angle=angle_result.angle,
        transformed_content=angle_result.content,
        content_type=content_type
    )
```

### Step 6: Selection
```python
best_angle, reasoning = generator.select_best_angle(all_results)
```

### Step 7: Validation
```python
is_valid, issues = transformer.validate_output(
    content=best_angle.content,
    content_type=content_type,
    original_draft=style_free_draft
)
```

Check against file 'N5/prefs/communication/quality-validation.json':
- Accuracy requirements (extremely high for docs)
- Voice consistency
- Structural requirements
- Quality threshold

### Step 8: Output
Present best angle to user.

---

## Content Type Profiles

**Loaded from:** file 'N5/prefs/communication/voice-profiles.json'

- `email`: Professional, warm, action-oriented
- `blog`: Conversational, substantial, engaging
- `social`: Authentic, scannable, platform-optimized
- `doc`: Clear, accurate, well-structured
- `note`: Flexible, efficient, personal
- `override`: Neutral, professional, brand-safe

---

## Quality Standards

**Accuracy Levels:**
- `doc`: Extremely high (no placeholders, no hallucinations, citations required)
- `email`: High (accurate commitments, correct details)
- `blog`: High (verifiable claims, appropriate citations)
- `social`: Medium-high (brand-safe, no false claims)
- `note`: Medium (internal use, basic accuracy)

**Voice Consistency:**
- Profile attributes applied correctly
- Structure rules followed
- Voice markers present
- Avoidance rules respected

**Quality Thresholds:**
- doc: 0.90
- email/blog: 0.80
- social: 0.75
- note: 0.60

---

## Examples

### Example 1: Email

**User Request:**
"Draft email to Sarah about Q4 roadmap delay"

**Process:**
1. Detected: email
2. Angles generated: [direct, collaborative, apologetic]
3. Style-free drafts created for each
4. Transformed using email profile + hybrid structure
5. Evaluated: collaborative scored highest (9.2/10)
6. Validated: ✓ passed
7. Presented: Collaborative version

**Output:**
```
Hey Sarah,

Quick heads up on Q4—we're looking at a 2-week delay on the marketplace launch.

The holdup is integration testing. We uncovered some edge cases that need proper handling before we ship. I know this affects your team's timeline, and I want to make sure we're aligned on next steps.

---

Here's what I'm thinking:

We can either:
1. Push the launch to mid-November (safest option)
2. Ship a limited beta on schedule (riskier but keeps momentum)

What works better for your planning? Happy to walk through the details if that's helpful.

Thanks for rolling with this—

V
```

### Example 2: Social Media

**User Request:**
"LinkedIn post about hiring too early"

**Process:**
1. Detected: social
2. Angles generated: [satirical, educational, vulnerable]
3. Transformed using social profile + hybrid structure
4. Evaluated: satirical scored highest (8.9/10)
5. Validated: ✓ passed
6. Presented: Satirical version

**Output:**
*(Hybrid version from earlier in conversation)*

### Example 3: Document (Override)

**User Request:**
"Document the new onboarding process --override"

**Process:**
1. Detected: doc
2. Override: neutral/professional tone
3. Generated: comprehensive angle only
4. Transformed using override profile
5. Validated: extremely high accuracy check
6. Presented: Professional document

---

## Troubleshooting

**Issue:** Wrong content type detected  
**Fix:** Use `--type <type>` to force specific type

**Issue:** Voice doesn't sound right  
**Fix:** Provide feedback in new conversation; system will adapt profiles

**Issue:** Output too formal/informal  
**Fix:** Use `--override` for neutral, or specify angle

**Issue:** Validation failed  
**Fix:** System will regenerate or flag specific issues

---

## Integration

### System Prompt
File 'N5/prefs/communication/voice-system-prompt.md' loaded automatically.
Makes this command run for all text generation without explicit invocation.

### Vibe Writer Persona
Vibe Writer v2.0 optimized for this workflow.
But system works independently of persona.

### Feedback Loop
User feedback in new conversation → system adapts → future outputs improve.

---

## Dependencies

**Scripts:**
- file 'N5/scripts/content_type_detector.py'
- file 'N5/scripts/angle_generator.py'
- file 'N5/scripts/voice_transformer.py'

**Configs:**
- file 'N5/prefs/communication/voice-profiles.json'
- file 'N5/prefs/communication/quality-validation.json'
- file 'N5/prefs/communication/content-library.json'

**Documentation:**
- file 'N5/prefs/communication/voice-transformation-system.md'
- file 'N5/prefs/communication/voice-system-prompt.md'

---

## Registration

```json
{
  "trigger": "generate-with-voice",
  "description": "Generate text with voice transformation (auto-applied)",
  "file_path": "N5/commands/generate-with-voice.md",
  "category": "content",
  "auto_apply": true,
  "requires_confirmation": false
}
```

---

**Status:** ACTIVE — Auto-applying to all text generation.
