# Networking CRM

**Version**: 1.0.0  
**Created**: 2025-10-09  
**Type**: Individual-Centric CRM with Event Cross-References

---

## Purpose

Manage networking contacts, track relationship history, and automate follow-ups. Structured around **individuals** (not events) with separate event logs for cross-referencing.

---

## Structure

```
Knowledge/crm/
├── README.md            # This file
├── index.jsonl         # Individual index (searchable)
├── individuals/        # Individual profiles (one per person)
│   ├── john-doe.md
│   ├── jane-smith.md
│   └── ...
├── events/             # Event logs (month-organized)
│   ├── 2025-10/
│   │   ├── 2025-10-09_sf-tech-week.md
│   │   └── ...
│   ├── 2025-11/
│   │   └── ...
│   └── index.jsonl    # Event index
└── follow-ups/         # Generated follow-up messages
    ├── john-doe_2025-10-09_linkedin.md
    ├── john-doe_2025-10-12_proposal.md
    └── ...
```

---

## Usage

### Add Contacts from Networking Event

```bash
# Interactive mode (recommended)
python N5/scripts/n5_networking_event_process.py

# Or conversationally
command 'N5/commands/networking-event-process.md'
```

### Search Individuals

```bash
# Search by name/company/tag
grep -r "VP Product" individuals/

# Or use index
cat index.jsonl | jq 'select(.company == "Acme Corp")'
```

### View Event History

```bash
# List events by month
ls events/2025-10/

# View specific event
cat events/2025-10/2025-10-09_sf-tech-week.md
```

### Find Follow-Ups

```bash
# List all generated follow-ups
ls follow-ups/

# Search by person
ls follow-ups/john-doe*
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

## Integration

### With N5 Lists

Contacts are automatically added to `N5/lists/networking-contacts.jsonl` for:
- List-based queries and filtering
- Integration with other N5 list workflows

### With Stakeholder Profile Generator

Leverages existing `N5/scripts/blocks/stakeholder_profile_generator.py` for:
- LLM-powered profile generation
- Consistent profile structure
- Meeting history integration

### With Deliverable Orchestrator

Integrates with `N5/scripts/deliverable_orchestrator.py` for:
- Auto-generated proposals
- One-pagers and memos
- Pitch decks

### With Voice Preferences

Uses `N5/prefs/communication/voice.md` for:
- Tone calibration in follow-up messages
- Relationship depth mapping
- CTA rigor adjustment

### With Essential Links

References `N5/prefs/communication/essential-links.json` for:
- Auto-insertion of Calendly links
- Trial codes for prospects
- Demo links and resources

---

## Post-Processing Enrichment

After initial processing, enrich high-priority contacts:

```bash
# Enrich individual profile
python N5/scripts/n5_networking_event_process.py --enrich john-doe
```

Enrichment sources:
- LinkedIn profile (role, background, education)
- Company info (size, funding, recent news)
- Recent mentions/articles (Google/Perplexity)
- Mutual connections discovery

---

## Best Practices

### When Adding Contacts

1. **Paste everything upfront** - Don't hold back, dump all notes in bulk
2. **Be conversational** - Verbal dumps don't need structure
3. **Mention action items naturally** - "I said I'd send them X"
4. **Name-drop mutual acquaintances** - "He knows Jane Smith"
5. **Trust the clarifying question** - If asked, it's to fill a critical gap

### When Following Up

1. **Same-day LinkedIn messages** - Establishes record while fresh
2. **Review before sending** - Always approve generated messages
3. **Track action items** - Check profile for promised follow-ups
4. **Update relationship history** - Log subsequent interactions

### When Enriching

1. **Prioritize high-value contacts** - Focus enrichment on prospects
2. **Batch process** - Enrich multiple contacts at once
3. **Update regularly** - Re-enrich quarterly for active relationships

---

## Maintenance

### Weekly

- Review pending follow-ups in `follow-ups/` folder
- Update relationship histories for active contacts
- Execute queued deliverables

### Monthly

- Run enrichment pass on high-priority contacts
- Generate summary reports (contacts by company, role, tag)
- Archive inactive contacts (status: "inactive")

### Quarterly

- Audit for duplicate entries
- Reconcile with `N5/lists/networking-contacts.jsonl`
- Update mutual acquaintances links

---

## Related Files

- **Command**: `N5/commands/networking-event-process.md`
- **Script**: `N5/scripts/n5_networking_event_process.py`
- **List**: `N5/lists/networking-contacts.jsonl`
- **Voice Prefs**: `N5/prefs/communication/voice.md`
- **Essential Links**: `N5/prefs/communication/essential-links.json`
- **Stakeholder Profiler**: `N5/scripts/blocks/stakeholder_profile_generator.py`

---

## Future Enhancements

- [ ] Organizational CRM (separate from individuals)
- [ ] Cross-reference individuals ↔ organizations
- [ ] Automated enrichment scheduling
- [ ] Relationship strength scoring
- [ ] Follow-up reminder system
- [ ] SQLite backend for faster queries (when >500 contacts)
- [ ] Export to external CRM systems (HubSpot, Salesforce)

---

**Last Updated**: 2025-10-09  
**Maintainer**: V (via N5 OS)
