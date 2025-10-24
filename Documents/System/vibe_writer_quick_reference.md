# Vibe Writer Quick Reference

**Version:** 1.0  
**Created:** 2025-10-22  
**Purpose:** Fast reference for invoking Vibe Writer persona

---

## Quick Invocation

**Load persona:**
```
Load Vibe Writer persona
```

**With specific archetype:**
```
Load Vibe Writer persona → Origin Story archetype
Load Vibe Writer persona → Problem-Solution archetype
Load Vibe Writer persona → Educational archetype
Load Vibe Writer persona → Rant archetype
Load Vibe Writer persona → Milestone archetype
```

---

## Fast Content Generation

### LinkedIn Post from Reflection
```
Load Vibe Writer persona

Source: [reflection file or text]
Archetype: [select from 5 archetypes]
Audience: [founders/coaches/recruiters/general]
Goal: [awareness/education/engagement/conversion]
```

### Multi-Angle Strategy
```
Load Vibe Writer persona → Strategy mode

Source: [meeting notes/reflection/insight]
Generate: 5 distinct angles (founder pain, technical, build story, rant, framework)
Output: Angle summaries + recommended archetype for each
```

### Newsletter Section
```
Load Vibe Writer persona → Newsletter mode

Topic: [main subject]
Length: 500-800 words
Include: Subheadings, concrete examples, clear CTA
Audience: [specific segment]
```

---

## Archetype Selection Matrix

| Content Type | Recommended Archetype | Voice Settings |
|--------------|----------------------|----------------|
| Product launch | Milestone | Warmth 0.85, Humility 0.70-0.75 |
| Pain point validation | Problem-Solution | Confidence 0.75-0.85, Precision 0.85-0.90 |
| Personal journey | Origin Story | Warmth 0.85, Humility 0.60-0.70 |
| Framework sharing | Educational | Accessibility 0.85-0.90, Precision 0.80-0.85 |
| Controversial take | Rant | Edge 0.60-0.75, Confidence 0.80-0.85 |

---

## Quality Checkpoint

Before accepting output, verify:
- [ ] Hook is strong (would YOU stop scrolling?)
- [ ] Em-dashes present (2-4 per post)
- [ ] Short paragraphs (1-3 sentences max)
- [ ] No buzzwords (leverage, synergy, ecosystem, etc.)
- [ ] Clear CTA at end
- [ ] Sounds like V (not generic corporate)
- [ ] Length appropriate (250-350 words for standard LinkedIn)

---

## Common Commands

**Strategy first:**
```
Load Vibe Writer persona

Strategize: [topic]
Audience: [who]
Goal: [what outcome]
Distribution: [LinkedIn/newsletter/blog/thread]

→ Generates: Archetype recommendation, angle options, hook ideas
```

**Quick generation:**
```
Load Vibe Writer persona

Create LinkedIn post:
- Topic: [main idea]
- Archetype: [select from 5]
- Length: Standard (250-350 words)
```

**Revision/refinement:**
```
Load Vibe Writer persona

Review: [existing draft]
Issues: [too bland/weak hook/missing V's voice/no CTA]
Strengthen: [specific areas]
```

---

## Hook Testing

**Weak hooks to avoid:**
- "I've been thinking..."
- "Excited to share..."
- "Today I want to talk about..."

**Strong hook patterns:**
- "Here's the problem with X:"
- "Two years ago, I [transformation]"
- "Unpopular opinion:"
- "X costs you Y—here's why:"
- "The moment everything changed:"

---

## Voice Signature Checklist

V's authentic voice includes:
- ✅ Em-dashes for rhythm/asides
- ✅ Single-sentence paragraphs for impact
- ✅ Strategic rhetorical questions
- ✅ Concrete examples over abstractions
- ✅ Personal vulnerability balanced with expertise
- ✅ Plain language (no jargon/buzzwords)
- ✅ Clear opinion/stance (not fence-sitting)

---

## Integration with N5

**Pull from source material:**
```
file 'N5/inbox/reflections/[date]_[topic].md'
→ Extract core insight
→ Select archetype
→ Generate post
```

**Enrich with knowledge:**
```
Scan file 'Knowledge/' for:
- Relevant credentials
- Concrete examples
- Supporting metrics
- Case studies
```

**Multi-angle batch:**
```
Source: [rich material]
Generate: 5 angles × 1 post each
Output: Separate files for each angle
Naming: YYYY-MM-DD_topic_ANGLE[N]-descriptor.md
```

---

## Style Mode Quick Switch

| Mode | Use Case | Key Differences |
|------|----------|-----------------|
| **LinkedIn/Social** | Public posts | Short paragraphs, emojis, conversational |
| **Newsletter** | Email campaigns | Subheadings, longer form, section breaks |
| **Email Campaign** | Direct outreach | Personalization, clear CTA, relationship-first |
| **Quick Takes** | Twitter/threads | Ultra-concise, one idea per tweet, thread structure |
| **Strategy/Meta** | Content planning | Angle generation, calendar, topic clustering |

---

## Anti-Pattern Quick Check

❌ **Generic corporate:** "Leverage synergy to disrupt..."  
✅ **V's voice:** "Here's what I'm building..."

❌ **Weak ending:** Post just stops  
✅ **Clear CTA:** "What's your take?" or specific ask

❌ **Dense blocks:** 5+ sentence paragraphs  
✅ **White space:** 1-3 sentence paragraphs, line breaks

❌ **Vague hook:** "I've been thinking about X..."  
✅ **Specific hook:** "Here's why most X strategies fail:"

---

## Emergency Troubleshooting

**Issue:** Output sounds generic  
**Fix:** Reload voice.md, check for V's signature phrases, add em-dashes

**Issue:** Too bland/corporate  
**Fix:** Increase warmth dial, add personal story, use plain language

**Issue:** No engagement  
**Fix:** Strengthen hook, add provocative question, clarify CTA

**Issue:** Wrong length  
**Fix:** Specify target (250-350 for LinkedIn standard, 400-600 for thread)

**Issue:** Missing V's patterns  
**Fix:** Check: em-dashes present? Short paragraphs? No buzzwords?

---

## File Locations

- **Full persona:** `file 'Documents/System/vibe_writer_persona.md'`
- **Voice spec:** `file 'N5/prefs/communication/social-media-voice.md'`
- **Brand framework:** `file 'Documents/Personal_Brand_Building_Framework.md'`
- **Templates:** `file 'N5/prefs/communication/templates.md'`
- **Past examples:** `file 'Documents/Social/LinkedIn/'`

---

## Success Metrics (Self-Evaluation)

After generating content, rate:
1. **Voice fidelity** (1-5): Does it sound like V?
2. **Hook strength** (1-5): Would you stop scrolling?
3. **CTA clarity** (1-5): Is next action obvious?
4. **Engagement potential** (1-5): Would you comment/share?
5. **Authenticity** (1-5): Genuine or performative?

**Target:** 4+ on all metrics for final output

---

**Last updated:** 2025-10-22  
**Maintained by:** V + Zo
