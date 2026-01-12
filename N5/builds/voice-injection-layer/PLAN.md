---
created: 2026-01-12
last_edited: 2026-01-12
version: 1.1
provenance: con_TBnwuolXxSkp5t1D
status: planning
---

# Plan: Voice Injection Layer

**Slug:** `voice-injection-layer`  
**Owner:** Vibe Architect  
**Status:** Planning  
**Created:** 2026-01-12  

---

## Open Questions

1. ~~Should primitives be injected automatically or require approval?~~ **DECIDED: Fully automatic**
2. ~~Pangram: automatic or ad-hoc?~~ **DECIDED: Ad-hoc only (not in pipeline)**
3. ~~Primitive usage: forced or suggested to LLM?~~ **DECIDED: Suggested (LLM has creative discretion)**

**All questions resolved. Ready for execution.**

---

## Design Clarification

### The Model: Automatic Pipeline, Natural Incorporation

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────────┐
│  Consumer   │───▶│ Voice Layer  │───▶│  LLM Gets   │───▶│  Output has  │
│  Triggers   │    │ (auto-fires) │    │  Primitives │    │  V's Voice   │
└─────────────┘    └──────────────┘    │  as Context │    └──────────────┘
                                       └─────────────┘
     No human           Automatic         LLM weaves        V just sees
     gate here          retrieval         naturally         the result
```

### What Happens (Zero Human Intervention)

1. **Consumer fires** (e.g., Follow-Up Email Generator starts)
2. **Layer auto-retrieves** primitives based on content type, topic, platform
3. **Primitives injected** into generation prompt as voice context
4. **LLM writes naturally** — incorporates primitives where they fit (not forced)
5. **V sees output** — already voice-enhanced, no approval step

### What This Is NOT

| ❌ NOT This | ✅ This |
|------------|---------|
| V reviews primitives before generation | Primitives flow automatically |
| V picks "use this line, not that" | LLM decides naturally |
| Forced phrase insertion | Suggested patterns LLM weaves in |
| Manual trigger each time | Auto-fires on every generation |

---

## Master Checklist

### Phase 1: Core Layer
- [ ] 1.1 Create `N5/scripts/voice_layer.py` — unified auto-fire entry point
- [ ] 1.2 Define VoiceContext dataclass (content_type, platform, purpose, topic_domains)
- [ ] 1.3 Implement `get_voice_injection()` — returns prompt fragment
- [ ] 1.4 Implement `inject_voice()` — wraps any generation prompt with voice context
- [ ] 1.5 Add CLI for testing/debugging only (production is fully automatic)
- [ ] 1.6 Unit tests

### Phase 2: Wiring (All Automatic)
- [ ] 2.1 Wire to Follow-Up Email Generator (auto-inject on every run)
- [ ] 2.2 Wire to Blurb Generator (auto-inject on every run)
- [ ] 2.3 Wire to X Thought Leader (auto-inject on every run)
- [ ] 2.4 Wire to Social Post Generator (auto-inject on every run)
- [ ] 2.5 Wire to generate_follow_up_emails workflow (auto-inject on every run)
- [ ] 2.6 Update Generate With Voice to use layer (consolidate)

### Phase 3: Pangram Ad-Hoc Mode
- [ ] 3.1 Remove Pangram from automatic pipeline
- [ ] 3.2 Create `@Pangram Check` prompt for manual validation when desired
- [ ] 3.3 Document: Pangram is for calibration, not iteration

---

## Philosophy

**Fully automatic. Zero friction. LLM decides fit.**

The Voice Injection Layer is invisible infrastructure. V never interacts with it directly — it just makes every generated piece of content sound more like V.

### The Contract

**Input (from consumer):**
```python
VoiceContext(
    content_type="email",      # What kind of content
    platform="email",          # Where it's going
    purpose="follow-up",       # Why it's being written
    topic_domains=["hiring"],  # What it's about
)
```

**Output (to LLM):**
```markdown
## Voice Enhancement (Auto-Applied)

Weave these V-distinctive patterns naturally into your writing:

1. [metaphor] "talent optionality" — framing career moves as options
2. [signature_phrase] "provenanced work history" — emphasizing verified experience
3. [syntactic_pattern] "X isn't Y, it's Z" — reframe expectations

Guidelines:
- Use what fits naturally, skip what doesn't
- One distinctive element per paragraph max
- Never force — if it feels mechanical, leave it out
```

The LLM receives this as context and incorporates naturally. No human review.

---

## Alternatives Considered

### Alt 1: Human-in-the-Loop Primitive Selection (Rejected)
V reviews retrieved primitives before each generation.

**Why rejected:** V explicitly doesn't want this. "I don't want to have to approve and say use this line, use that line."

### Alt 2: Forced Phrase Insertion (Rejected)
Layer literally inserts phrases into output.

**Why rejected:** Sounds mechanical. LLM should weave naturally.

### Alt 3: Automatic Retrieval + Natural Incorporation (Selected) ✅
Layer auto-fires, retrieves primitives, LLM incorporates naturally.

**Why selected:**
- Zero friction for V
- Primitives enhance without forcing
- Fully automatic pipeline

---

## Trap Door Analysis

| Decision | Reversibility | Risk |
|----------|--------------|------|
| Automatic injection | Fully reversible (remove from prompts) | Low |
| VoiceContext schema | Medium — consumers depend on it | Design minimal |
| Removing Pangram auto | Fully reversible | Low |

**Key trap door:** VoiceContext becomes a contract. Keep it minimal.

---

## Phase 1: Core Layer

### Affected Files
- `N5/scripts/voice_layer.py` (NEW)

### Implementation

```python
"""
Voice Injection Layer

Fully automatic. Zero human intervention.
Consumers call inject_voice(), get back enhanced prompt.
"""

from dataclasses import dataclass, field
from typing import Optional
from N5.scripts.retrieve_primitives import get_primitives

@dataclass
class VoiceContext:
    """Context for voice injection. Minimal by design."""
    content_type: str  # email, blurb, tweet, post, doc
    platform: str = "general"  # x, linkedin, email, slack
    purpose: str = "general"  # follow-up, intro, thought-leadership
    topic_domains: list[str] = field(default_factory=list)
    primitive_count: int = 3

def get_voice_fragment(ctx: VoiceContext) -> str:
    """
    Auto-retrieves primitives and formats as prompt fragment.
    Called automatically — no human review.
    """
    # Map content type to preferred primitive types
    type_preferences = {
        "tweet": ["signature_phrase", "metaphor", "rhetorical_device"],
        "email": ["syntactic_pattern", "signature_phrase", "conceptual_frame"],
        "blurb": ["metaphor", "analogy", "signature_phrase"],
        "post": ["conceptual_frame", "metaphor", "rhetorical_device"],
    }
    
    preferred = type_preferences.get(ctx.content_type, None)
    
    # Retrieve primitives (auto, no approval)
    primitives = get_primitives(
        domains=ctx.topic_domains if ctx.topic_domains else None,
        types=preferred,
        count=ctx.primitive_count,
        update_usage=True,  # Track what's been used
    )
    
    if not primitives:
        return ""  # No primitives = no injection (graceful)
    
    # Format as prompt fragment
    lines = ["## Voice Enhancement (Auto-Applied)", ""]
    lines.append("Weave these V-distinctive patterns naturally into your writing:")
    lines.append("")
    
    for i, p in enumerate(primitives, 1):
        lines.append(f"{i}. [{p['primitive_type']}] \"{p['exact_text']}\"")
    
    lines.append("")
    lines.append("Guidelines:")
    lines.append("- Use what fits naturally, skip what doesn't")
    lines.append("- One distinctive element per paragraph max")
    lines.append("- Never force — if it feels mechanical, leave it out")
    
    return "\n".join(lines)

def inject_voice(prompt: str, ctx: VoiceContext) -> str:
    """
    Wraps any generation prompt with voice context.
    Fully automatic — just call and use the result.
    """
    fragment = get_voice_fragment(ctx)
    if not fragment:
        return prompt
    return f"{fragment}\n\n---\n\n{prompt}"
```

### Unit Tests
- `VoiceContext` defaults work correctly
- `get_voice_fragment()` returns well-formed markdown
- `inject_voice()` prepends fragment to prompt
- Empty primitives = graceful no-op (no crash)
- Throttle prevents same primitive in consecutive calls

---

## Phase 2: Wiring (All Automatic)

### Pattern for Each Consumer

Each writing prompt gets updated to auto-call the layer:

```markdown
### Voice Enhancement (Automatic)

This prompt auto-injects voice primitives. No action required.

At generation time, the system:
1. Detects content type and context
2. Retrieves relevant V-distinctive patterns  
3. Injects them into the generation prompt
4. LLM incorporates naturally

**Implementation:**
```python
from N5.scripts.voice_layer import VoiceContext, inject_voice

ctx = VoiceContext(
    content_type="email",  # ← set per prompt
    platform="email",
    purpose="follow-up",
    topic_domains=extracted_from_meeting_context,
)

# Wrap the generation prompt (happens automatically)
enhanced_prompt = inject_voice(base_prompt, ctx)
```
```

### Consumer-Specific Context

| Consumer | content_type | platform | purpose | topic_domains |
|----------|--------------|----------|---------|---------------|
| Follow-Up Email | email | email | follow-up | from meeting |
| Blurb Generator | blurb | varies | intro | from subject |
| X Thought Leader | tweet | x | thought-leadership | from topic |
| Social Post | post | linkedin/x | thought-leadership | from topic |
| generate_follow_up_emails | email | email | follow-up | from meeting |
| Generate With Voice | varies | varies | varies | from request |

### Unit Tests
- Each prompt has voice layer wired
- Context populated correctly per consumer
- Output includes V-distinctive patterns (spot check)

---

## Phase 3: Pangram Ad-Hoc

### Changes

**Remove from automatic pipeline:**
- `Generate With Voice.prompt.md` — delete Step 7.5 (Pangram auto-check)

**Create manual prompt:**
- `Prompts/Pangram Check.prompt.md` — for when V wants to validate

### Pangram Check Prompt

```markdown
---
tool: true
description: "Ad-hoc AI detection check. Use post-refinement, not during iteration."
tags: [voice, validation, pangram]
---

# Pangram Check

Manual AI detection validation. **Not part of automatic pipeline.**

## When to Use
- Before publishing high-stakes content
- Periodic voice calibration (weekly/monthly)
- Testing if voice improvements are working

## When NOT to Use
- During drafting iteration (slows you down)
- For internal notes or low-stakes content
- Every single piece of content (overkill)

## Usage

```bash
python3 Integrations/Pangram/pangram.py --text "your content here"
```

**Target:** < 0.5 AI score

If score is high, the voice layer should already be helping. 
If consistently high, review primitive quality or add more to library.
```

---

## Success Criteria

| Metric | Target |
|--------|--------|
| Voice layer auto-fires on all 6 consumers | 6/6 |
| Zero human intervention required | ✅ Fully automatic |
| Pangram removed from auto-pipeline | ✅ Ad-hoc only |
| Output quality maintained or improved | Spot check 3 outputs |

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Over-injection (too many primitives) | Medium | Cap at 3, "use what fits" guidance |
| Primitives don't match content | Medium | Domain filtering + diverse types |
| LLM ignores primitives | Low | Few-shot examples if needed |
| Slows generation | Low | Local DB, fast retrieval |

---

## Handoff

When approved:
1. Switch to Builder: `set_active_persona("567cc602-060b-4251-91e7-40be591b9bc3")`
2. Execute Phase 1 (core layer + tests)
3. Execute Phase 2 (wire all 6 consumers)
4. Execute Phase 3 (Pangram ad-hoc)
5. Spot check outputs

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.1 | 2026-01-12 | Clarified: fully automatic pipeline, natural incorporation, zero human approval. Renamed "suggested" to "automatic retrieval + natural incorporation." |
| 1.0 | 2026-01-12 | Initial plan. |

