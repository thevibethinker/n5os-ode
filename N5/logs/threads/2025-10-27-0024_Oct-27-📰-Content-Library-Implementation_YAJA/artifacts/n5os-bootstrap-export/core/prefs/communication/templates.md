# Communication Templates & Patterns

**Module:** Communication  
**Version:** 2.0.0  
**Date:** 2025-10-09

---

## Micro-Templates

### Follow-Up: CTA + Next Steps

```
Thanks for [specific thing]. 

To move this forward, could you [specific ask] by [date/time]? 

If that timing's tight, [fallback option]. Happy to adjust as needed.
```

**Use when:** Need specific action with deadline flexibility

---

### Summary → Decision → Next Steps

```
We aligned on:
- [Point 1]
- [Point 2]

Decision needed: [specific decision]

Next steps:
- [Action A] (owner: [name], by: [date])
- [Action B] (owner: [name], by: [date])
```

**Use when:** Closing a meeting or alignment conversation

---

### Gentle Nudge

```
Quick nudge on [topic from previous exchange].

If helpful, I can [offer to unblock] to unblock; otherwise, [action] by [date] works.
```

**Use when:** Following up without pressure

---

### Gratitude → Reiterate → Ask → Close

```
Thanks for [specific contribution].

To recap: [1-sentence outcome].

Could you [specific ask with owner + date]?

[Warm closing]
```

**Use when:** High-performing structure for most contexts

---

## File Naming Patterns

For deliverables and exports:

### Pattern
```
[Type] - [Short Name] v[Major].[Minor] ([YYYY-MM-DD])
```

### Examples
- `Brief - IUI Guardrails v1.2 (2025-09-12)`
- `Prompt - JD Analyzer v7.3 (2025-09-10)`
- `Strategy - GTM Pivot Plan v2.0 (2025-09-20)`

### Types
- **Brief** — Short strategic documents
- **Prompt** — Prompt templates or chains
- **Strategy** — Strategic plans or frameworks
- **Analysis** — Analysis documents
- **Report** — Reports or summaries
- **Template** — Reusable templates

---

## Export Formats

### Preferred Formats by Use Case

1. **Canvas** (Preferred)
   - Long/iterative pieces
   - Documents requiring line edits
   - Collaborative editing

2. **Plain Text / Markdown**
   - Quick paste into other tools
   - Email composition
   - Chat/Slack messages

3. **PDF**
   - Final share-outs only
   - External stakeholders
   - Formal presentations

---

## CTA Patterns

### Two-Step CTA (Primary + Fallback)

```
Primary: [Ideal action with date]
Fallback: [Alternative if primary doesn't work]
```

**Example:**
```
Could you review by Thursday, Sep 22? If not, a quick async note by Friday works too.
```

### Owner + Date Format

Always specify both:
- **Owner:** Who is responsible
- **Date:** Absolute deadline (never "soon" or "next week")

**Example:**
```
- Review draft (owner: Logan, by: 2025-09-22 16:00 ET)
- Schedule follow-up (owner: Vrijen, by: 2025-09-23 10:00 ET)
```

---

## Email Signature Patterns

### Internal (Team)
```
V
```
or
```
Vrijen
```

### External (Formal)
```
Vrijen Attawar
CEO, Careerspan
vrijen@mycareerspan.com
```

### External (Warm)
```
Best,
Vrijen

Vrijen Attawar
CEO, Careerspan
```

---

## Subject Line Patterns

### For Follow-Ups
```
Re: [Original subject] — [Next action needed]
```

### For New Threads
```
[Category]: [Specific topic] — [Call to action]
```

**Examples:**
- `Re: Product roadmap — Review by Thu 9/22`
- `Strategy: Q4 GTM pivot — Input needed`
- `Quick sync: Hiring pipeline — 15 min this week?`

---

## Opening Lines

### By Context

**Cold outreach:**
```
I'm [role] at [company], and we [relevant context].
```

**Warm follow-up:**
```
Thanks for [specific previous interaction].
```

**Internal team:**
```
Quick update on [topic]:
```

**Status check:**
```
Checking in on [specific item from previous exchange].
```

---

## Closing Lines

### By Formality Level

**Formal (depth 1-2):**
- Best regards,
- Thank you,
- Looking forward to connecting,

**Balanced (depth 2-3):**
- Best,
- Thanks,
- Looking forward to it,

**Casual (depth 3-4):**
- Cheers,
- Talk soon,
- Let me know!

---

## Safeguards & Catches

### Version Bump Guard
Don't overwrite; bump version and log changes.

```
# Instead of overwriting v1.2
Create: document-name v1.3 (2025-10-09)
Log: "Updated section X based on feedback Y"
```

### Contradiction Checks
Flag mismatched numbers/dates or vague time words.

**Trigger checks when:**
- Dates mentioned without year
- Relative time without absolute anchor
- Numbers that don't reconcile
- Conflicting information in same document

### Missing Field Guard
Catch empty sections in templates.

**Required sections for most deliverables:**
- Next Steps (who, what, when)
- Risks or Considerations
- Success Criteria

### Privacy/Ethics Nudge
Warn on personal/medical claims; provide disclaimers.

**Template:**
```
⚠️ Note: This contains personal/medical information. 
- Ensure proper consent before sharing
- Consider privacy implications
- Recommend: "See a qualified professional for medical advice"
```

---

## Related Files

- **Voice & Style:** `file 'N5/prefs/communication/voice.md'`
- **Meta-Prompting:** `file 'N5/prefs/communication/meta-prompting.md'`
- **Email Processing:** `file 'N5/prefs/communication/email.md'`
- **Naming Conventions:** `file 'N5/prefs/naming-conventions.md'`

---

## Change Log

### v2.0.0 — 2025-10-09
- Extracted from monolithic prefs.md
- Organized templates by category
- Added file naming patterns section
- Added export formats preferences
- Added safeguards and checks
- Added subject line and opening/closing patterns
- Cross-referenced related modules
