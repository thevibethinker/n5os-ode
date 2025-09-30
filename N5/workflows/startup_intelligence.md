# Startup Intelligence Workflow

## Overview

The Startup Intelligence system provides a structured approach to tracking and analyzing key stakeholders in the startup ecosystem.

## Categories

### Key Figures
Individual people tracked in the system. Located in `Startup Intelligence/Key Figures/`.

**Types:**
- `founder` - Company founders
- `investor` - Individual investors
- `community_leader` - Community organizers/leaders
- `recruiter` - Individual recruiters
- `notable_user` - Notable end users/customers
- `executive` - C-level executives
- `engineer` - Notable technical leads
- `advisor` - Advisors and consultants
- `thought_leader` - Industry thought leaders
- `other` - Other types

### Organizations
- **Startups/** - Early-stage companies
- **Companies/** - Established companies, public companies, recruiting firms
- **Communities/** - Networks, groups, ecosystems
- **Investors/** - VC firms, funds, angel groups (firm-level)
- **Channel Partners/** - Organizations that act as channel partners

## Ingestion Pipeline

### Step 1: Add to Tracking Queues

**Via Text/Message:**
Text Zo: "Add [Name] to startup intelligence - [brief context]"

Zo will ask if it's an individual or organization, and for more details (type/category, links).

**Manual Entry:**
Append a JSON line to either `N5/lists/individuals_queue.jsonl` or `N5/lists/organizations_queue.jsonl`.

**Example for Individuals:**
```json
{"name": "Sarah Chen", "context": "Met at YC demo day, founder of HealthTech AI", "source": "text message", "type": "founder", "links": ["https://linkedin.com/in/sarahchen", "https://twitter.com/sarahchen_ai"]}
```

**Example for Organizations:**
```json
{"name": "HealthTech AI", "context": "YC W25 cohort, innovating in diagnostics", "source": "text message", "category": "startup", "links": ["https://healthtech.ai"]}
```

### Step 2: Process the Queues (On-Demand)

Run the processing script:
```bash
python3 /home/workspace/N5/scripts/n5_process_tracking_queues.py
```

This will:
1. Create a Key Figure or Organization file for each new entry
2. Archive processed entries to `N5/lists/processed_archive.jsonl`
3. Clear the tracking queues

### Step 3: Enrich via Due Diligence (On-Demand)

Request DD on a Key Figure or Organization:
```
"Run DD on [Name] (category: [category])"
```

- **For Key Figures:** Use `category: key_figure` (e.g., "Run DD on Sarah Chen (category: key_figure)")
- **For Organizations:** Use the specific category (e.g., "Run DD on HealthTech AI (category: startup)")

The AI will follow the DD protocol and update the file.

## Due Diligence Protocol

When running DD on an entity, the AI follows this process:

1. **Website Review** - Check their website (if available)
2. **Platform Review** - Check LinkedIn/relevant social media/professional platforms
3. **Recent News** - Search for mentions in the last 6 months
4. **Verification** - Confirm we're looking at the correct entity
5. **Conflict Resolution** - If conflicting information arises, ask clarifying questions

Findings are timestamped and appended to the entity's file under "Recent Activity".

## Cross-Linking

Key Figures should be linked to their associated organizations in the `organizations` frontmatter field:

```yaml
organizations:
  - name: "Acme Startup"
    role: "CEO & Co-founder"
    category: "startup" # startup, company, community, investor, channel_partner
```

Organization files will have a `key_figures` frontmatter field to link back to individuals.

```yaml
key_figures:
  - name: "Jane Doe"
    role: "CEO"
    file: "jane-doe.md"
```

## File Naming Convention

- **Key Figures:** `firstname-lastname.md` (lowercase, hyphens)
- **Organizations:** `organization-name.md` (lowercase, hyphens)

## Schema Reference

- **Key Figures:** `N5/schemas/key_figure_schema.yaml`
- **Organizations:** Refer to `_TEMPLATE.md` files in respective `Startup Intelligence` subdirectories.

## Scripts

- **Process Tracking Queues:** `N5/scripts/n5_process_tracking_queues.py`
- **Quick DD:** `N5/scripts/n5_quick_dd.py` (helper for AI)

## Future Enhancements

- Cyclical research task (on hold for now)
- Automated cross-linking validation
- Relationship mapping visualizations
- Integration with CRM systems
