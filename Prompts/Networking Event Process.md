---
description: 'Command: networking-event-process'
tags:
- networking
- crm
- follow-up
- automation
- interactive
---
# Command – Networking Event Processor

**Version**: 1.0.0  
**Category**: Networking & CRM  
**Type**: Hybrid (Interactive Prompt + Python Script)

---

## Purpose

Process networking events by capturing contacts, generating profiles, creating same-day LinkedIn follow-ups, and managing action items. Maintains an individual-centric CRM with event cross-references.

---

## Features

✅ **Individual-Centric CRM** - Profiles stored by person, not event  
✅ **Event Cross-Referencing** - Separate event logs with pointers to individuals  
✅ **Verbal Dump Interface** - Paste all notes upfront, then conversational extraction per person  
✅ **Stakeholder Profiles** - Leverages existing `stakeholder-profile-generator` logic  
✅ **Same-Day LinkedIn Messages** - <120 words, includes context + why following up  
✅ **Dynamic Action Handling** - Auto-detects links, proposals, intros from conversation  
✅ **Mutual Acquaintances Tracking** - Links to other CRM individuals  
✅ **Post-Processing Enrichment** - Optional web enrichment via LinkedIn/Google/Perplexity  
✅ **Deliverables Automation** - Integrates with `deliverable-orchestrator`

---

## Usage

### Interactive Mode (Recommended)

```bash
python N5/scripts/n5_networking_event_process.py
```

**Workflow:**
1. Paste all contact notes (one person per line)
2. Provide event context (name, date, location)
3. For each person: verbal dump + 1 clarifying question
4. Review and approve generated materials
5. Optional: Run enrichment pass

### Conversational Mode

Simply invoke this command in conversation:

```
command 'N5/commands/networking-event-process.md'

Here's my event:
- SF Tech Week on 2025-10-09
- John Doe - VP Product at Acme
- Jane Smith - Founder at StartupXYZ
- ...
```

Then follow the prompts for each individual.

---

## CRM Structure

```
Knowledge/crm/
├── individuals/          # Individual profiles (one per person)
│   ├── john-doe.md
│   ├── jane-smith.md
│   └── ...
├── events/              # Event logs (month-organized)
│   ├── 2025-10/
│   │   └── 2025-10-09_sf-tech-week.md
│   └── index.jsonl     # Event index
├── follow-ups/          # Generated follow-up messages
│   ├── john-doe_2025-10-09_linkedin.md
│   └── ...
└── index.jsonl         # Individual index
```

---

## Individual Profile Schema

Each individual profile includes:

- **One-Line Context** - Quick reference summary
- **Basic Info** - Company, role, connection channels
- **Mutual Acquaintances** - Links to other CRM individuals
- **Background & Experience**
- **Interests & Focus Areas**
- **Pain Points & Challenges**
- **Opportunities & Needs**
- **Key Quotes**
- **Relationship History** - Event cross-references
- **Follow-Ups & Action Items**
- **Generated Materials** - Links to messages/proposals
- **Enrichment Status** - Web research tracking

---

## Event Log Schema

Each event log includes:

- **Event Metadata** - Date, location, type, purpose
- **People Met** - Grouped by priority with context
- **Event-Level Insights** - Themes, patterns, opportunities
- **Event-Level Action Items**
- **Cross-References** - Links to individual profiles

---

## LinkedIn Message Format

Generated messages follow `voice.md` guidelines:

- **Length**: <120 words
- **Tone**: Balanced, warm (calibrated to relationship depth)
- **Structure**:
  1. Greeting (relationship-depth calibrated)
  2. Resonant detail (memorable moment from conversation)
  3. Context (what we discussed)
  4. Why following up (specific reason)
  5. Immediate action if applicable (link/proposal)
  6. Soft CTA
  7. Sign-off (Vrijen)
- **Strategic Function**: Same-day acknowledgment, buys time for deeper action items
- **Auto-Link Insertion**: Pulls from `content-library.json` when relevant

---

## Integration Points

### Existing N5 Functions Leveraged

| Function | Usage |
|----------|-------|
| `stakeholder-profile-generator` | Generate detailed profiles |
| `deliverable-orchestrator` | Auto-generate proposals/one-pagers |
| `lists-add` | Add contacts to networking list |
| `content-library.json` | Auto-insert Calendly/trial codes |
| `voice.md` | Calibrate message tone |
| Knowledge files | Reference Careerspan context |
| `web_search` / `web_research` | Post-processing enrichment |

---

## Workflow Steps

### Step 1: Event Context + Bulk Paste
- Paste all contact notes (one person per line)
- Provide event name, date, location, purpose

### Step 2: Person-by-Person Loop
For each person:
1. You do **verbal dump** about that person
2. System extracts structured data via LLM
3. System asks **ONE** clarifying question (if needed)
4. System checks if individual already exists in CRM
   - If exists: Updates profile, appends to relationship history
   - If new: Creates new profile
5. System generates stakeholder profile
6. System generates LinkedIn follow-up message
7. System detects dynamic actions:
   - "send them link X" → references `content-library.json`
   - "send proposal" → queues `deliverable-orchestrator`
   - "intro to Logan" → adds to action items
8. System identifies mutual acquaintances and links them
9. Confirm and move to next person

### Step 3: Create Event Log
- Generate event markdown with pointers to individuals
- Store in `events/YYYY-MM/` folder
- Update event `index.jsonl`

### Step 4: Synthesis & Deliverables
- Compile action items across all contacts
- Execute deliverables queue (proposals, etc.)
- Present summary with all generated materials

### Step 5: Post-Processing Enrichment (Optional)
- Run enrichment pass for high-priority contacts
- Web search for LinkedIn profiles, company info, recent news
- Update profiles with enriched data
- Mark enrichment status

---

## Examples

### Example Input

```
Event: SF Tech Week on 2025-10-09 in San Francisco

Contacts:
- John Doe - VP Product at Acme
- Jane Smith - Founder at StartupXYZ
- Bob Johnson - Head of HR at TechCo
```

### Example Verbal Dump (Person 1)

```
John is VP Product at Acme Corp. We talked about their hiring challenges—
they're spending 60+ days to fill roles and struggling to find "hidden gems" 
vs just going with brand-name candidates. He's got budget approved for Q1 2026 
to upgrade their talent tech stack and is specifically looking for AI screening 
tools. I promised to send him a proposal by Oct 12 and intro him to Logan for 
a technical discussion. He knows Jane Smith—they were college roommates. 
Super engaged, asked great questions about how our alignment scoring works.
```

### Example Generated LinkedIn Message

```markdown
Hey John,

Great connecting at SF Tech Week yesterday! I appreciated your insight about 
the "hidden gems vs brand-name" hiring dilemma—it's exactly the challenge 
we built Careerspan to solve.

As discussed, I'll send over a proposal this week outlining how our AI 
screening tool can help you cut time-to-hire while surfacing those overlooked 
candidates. Happy to connect you with Logan for a deeper technical dive.

Looking forward to exploring this together.

Best,
Vrijen

---
Word Count: 78/120
```

---

## Post-Processing Enrichment

After initial processing, run enrichment for high-priority contacts:

```bash
python N5/scripts/n5_networking_event_process.py --enrich john-doe
```

Enriches:
- LinkedIn profile (role, background, education)
- Company info (size, funding, recent news)
- Recent mentions/articles
- Potential mutual connections

---

## Output Files

For each networking event, generates:

1. **Individual Profiles** - `Knowledge/crm/individuals/{name}.md` (created or updated)
2. **Event Log** - `Knowledge/crm/events/YYYY-MM/{date}_{event-name}.md`
3. **LinkedIn Messages** - `Knowledge/crm/follow-ups/{name}_{date}_linkedin.md`
4. **Deliverables** (if requested) - Proposals, one-pagers, etc.
5. **Index Updates** - `Knowledge/crm/index.jsonl` and `Knowledge/crm/events/index.jsonl`
6. **List Additions** - `N5/lists/networking-contacts.jsonl`

---

## Tips

- **Paste everything upfront** - Don't hold back, dump all notes in Step 1
- **Be conversational** - The verbal dump doesn't need structure, just talk through what you remember
- **Mention action items naturally** - "I said I'd send them X" or "They asked for Y"
- **Name-drop mutual acquaintances** - "He knows Jane Smith" or "Alex Caveny introduced us"
- **Trust the clarifying question** - If the system asks, it's to fill a critical gap
- **Review before sending** - Always approve LinkedIn messages before they go out

---

## Related Commands

- `command 'N5/commands/follow-up-email-generator.md'` - For meeting follow-ups (not networking)
- `command 'N5/commands/deliverable-generate.md'` - Generate proposals/one-pagers
- `command 'N5/commands/lists-add.md'` - Manually add to networking list
- `command 'N5/commands/knowledge-add.md'` - Manually add knowledge entries

---

## Version History

### v1.0.0 — 2025-10-09
- Initial implementation
- Individual-centric CRM structure
- Event cross-referencing
- Verbal dump interface
- Stakeholder profile integration
- Same-day LinkedIn message generation
- Dynamic action detection
- Mutual acquaintances tracking
- Post-processing enrichment support
- Deliverables automation integration

---

## Support

For issues or enhancements, use `command 'N5/commands/core-audit.md'` to log suggestions.
