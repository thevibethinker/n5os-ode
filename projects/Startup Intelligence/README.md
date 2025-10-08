# Startup Intelligence System

This folder contains your organized intelligence on the startup ecosystem.

## Structure

- **Key Figures/** - Individual people tracked in the system
  - Founders, investors, community leaders, recruiters, notable users, etc.
  - Each file uses structured frontmatter (see `file 'N5/schemas/key_figure_schema.yaml'`)

- **Startups/** - Early-stage companies
  - Cross-linked to Key Figures who work there

- **Companies/** - Established companies & recruiting firms

- **Communities/** - Networks, groups, ecosystems
  - Cross-linked to Key Figures who lead or participate

- **Investors/** - VC firms, funds, angel groups (firm-level)

- **Channel Partners/** - Organizations that act as channel partners

## Workflow

### Adding New Individuals or Organizations to Track

**Quick Add (via text/message):**
You can text Zo to add someone or an organization. The entry goes to `file 'N5/lists/individuals_queue.jsonl'` or `file 'N5/lists/organizations_queue.jsonl'`.

**Example for Individuals:**
```json
{"name": "Sarah Chen", "context": "Met at YC demo day, founder of HealthTech AI", "source": "text message", "type": "founder", "links": ["https://linkedin.com/in/sarahchen"]}
```

**Example for Organizations:**
```json
{"name": "HealthTech AI", "context": "YC W25 cohort, innovating in diagnostics", "source": "text message", "category": "startup", "links": ["https://healthtech.ai"]}
```

**Process the Queues:**
Run: `python3 /home/workspace/N5/scripts/n5_process_tracking_queues.py`

This creates new Key Figure or Organization files and archives the processed entries.

### Running Due Diligence

To perform on-demand DD on a Key Figure or Organization:

1. Ask Zo: "Run DD on [Name] (category: [category])"
   - Example: "Run DD on Sarah Chen (category: key_figure)"
   - Example: "Run DD on HealthTech AI (category: startup)"
2. Zo will follow the DD protocol:
   - Review website and LinkedIn/relevant platforms
   - Check recent news (last 6 months)
   - Identify social media presence/relevant online activity
   - Verify correct entity
   - Flag any conflicts
3. Findings are appended to the entity's file.

### Cross-Linking

When you add or update a Key Figure, link them to their organizations in their frontmatter:

```yaml
organizations:
  - name: "Acme Startup"
    role: "CEO & Co-founder"
    category: "startup"
```

Similarly, organization files will have a `key_figures` section to link back to individuals.

## Notes

- The tracking queues (`file 'N5/lists/individuals_queue.jsonl'` and `file 'N5/lists/organizations_queue.jsonl'`) are your intake queues.
- Processed entries are archived to `file 'N5/lists/processed_archive.jsonl'`.
- Cyclical research is not yet enabled (manual DD only for now).
