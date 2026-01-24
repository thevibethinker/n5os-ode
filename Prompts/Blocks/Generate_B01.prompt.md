---
description: Generate B01 Detailed Recap block from meeting transcript
tags:
  - meeting-intelligence
  - block-generation
  - b01
  - recap
tool: true
created: 2025-11-03
last_edited: 2026-01-21
version: 2.0
---
# Generate Block B01: Detailed Recap

**Input:** Meeting transcript provided in context

**Your task:** Generate a comprehensive B01 Detailed Recap block that transforms raw transcript into strategic intelligence.

## Output Format

**REQUIRED YAML FRONTMATTER:**
```yaml
---
created: {YYYY-MM-DD}
last_edited: {YYYY-MM-DD}
version: 1.0
provenance: {agent_id or conversation_id}
---
```

**REQUIRED STRUCTURE:**

```markdown
# B01: Detailed Recap

## Meeting Overview
{2-4 sentences: Who met, what was the purpose, what was the overall arc of the conversation}

## Chronological Discussion

### {Topic/Phase Name} ({Approximate Timing})
{Narrative summary of this segment. Include:}
- **Key Points**: Specific facts, numbers, names mentioned
- **Decisions**: Any explicit decisions made
- **Interesting Details**: Strategic context, subtext, notable quotes

### {Next Topic/Phase}
...

## Key Takeaways
- {Bullet list of 3-7 most important outcomes, decisions, or insights}
```

## Quality Standards

1. **NARRATIVE SYNTHESIS, NOT TRANSCRIPT COPYING**
   - Transform raw dialogue into coherent narrative
   - NEVER output "Speaker: Quote" format
   - Synthesize multiple exchanges into insights

2. **STRATEGIC DEPTH**
   - Extract business context and implications
   - Note power dynamics and relationship signals
   - Identify commitments and follow-up triggers

3. **SPECIFIC CONTENT**
   - Include real names, companies, numbers, dates
   - Quote memorable phrases when strategically relevant
   - Note specific action items with owners

4. **STRUCTURAL INTEGRITY**
   - Minimum 500 bytes (real meetings produce 2000+ bytes)
   - Use ### headers for major discussion segments
   - Include timing approximations where clear from transcript

## Anti-Patterns (NEVER DO THESE)

❌ "### Discussion Flow" with bullet points of quotes
❌ "- Speaker Name: [transcript line]"
❌ "**Key Themes:** [generic categories]"
❌ Outputting raw transcript lines
❌ Generic summaries without specific content
❌ Missing YAML frontmatter

## Example of GOOD vs BAD Output

**BAD (what we're fixing):**
```markdown
### Meeting Recap
**Participants:** Person A, Person B
**Key Themes:** Revenue discussion
### Discussion Flow
- Person A: Hi how are you
- Person B: Good thanks
```

**GOOD:**
```markdown
---
created: 2026-01-21
last_edited: 2026-01-21
version: 1.0
provenance: agent_xyz123
---

# B01: Detailed Recap

## Meeting Overview
An introductory partnership discussion between Careerspan (V, Logan, Ilse) and FutureFit (Hamoon, Katya). The conversation explored potential acquisition/merger scenarios with strong cultural alignment signals.

## Chronological Discussion

### Opening Introductions (0:00-5:00)
The meeting opened with team introductions. Hamoon from FutureFit set expectations for a 34-45 minute exploratory call...

### Technical Deep-Dive (15:00-25:00)
Katya asked about Careerspan's NLP approach. Ilse explained their cost-efficiency strategy...

## Key Takeaways
- FutureFit is B2B/B2G only (no direct-to-consumer)
- Strong interest in Careerspan's coaching data as a differentiator
- Next step: NDA before technical discussions
```

---

**Generate the B01 block now using the transcript provided.**
