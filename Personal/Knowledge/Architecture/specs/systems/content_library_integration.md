---
created: 2025-11-29
last_edited: 2025-11-29
version: 1.0
grade: knowledge
domain: systems
stability: time_bound
form: spec
---

# Content Library Integration

## Overview

The **Content Library** is V's canonical database of links and resources for use in emails, documents, and communications. It ensures consistent, accurate delivery of promised resources across all workflows.

## Architecture

**Database:** `file 'N5/data/content_library.db'`  
**Manager Script:** `file 'N5/scripts/content_library.py'`  
**Schema:** `file 'N5/schemas/content_library.sql'`

**Status:** ✓ Active (Migrated from JSON 2025-11-17)  
**Deprecated:** `content-library.json`, `essential-links.json` (archived)

## Data Model

```sql
items (
  id TEXT PRIMARY KEY,          -- human-readable ID (e.g., "trial_code_general")
  type TEXT NOT NULL,            -- "link" or "snippet"
  title TEXT NOT NULL,           -- Display name
  content TEXT,                  -- Optional description/content
  url TEXT,                      -- For links: the actual URL
  created_at TEXT,
  updated_at TEXT,
  deprecated INTEGER DEFAULT 0,  -- 1 = don't use anymore
  ...
)

tags (
  item_id TEXT,                  -- Foreign key to items
  tag_key TEXT,                  -- e.g., "category", "audience", "type"
  tag_value TEXT                 -- e.g., "scheduling", "trial", "product"
)
```

## Current Inventory

**Total Items:** 66 (59 links, 7 snippets)

**Categories:**
- **Scheduling:** Calendar links for meetings (Vrijen, founders, team)
- **Product:** Trial codes, demo links, product URLs
- **Company:** Website, social profiles, marketing assets
- **Personal:** Bio snippets, social links, personal brand

## Usage

### Command-Line Interface

```bash
# Search for items
python3 /home/workspace/N5/scripts/content_library.py search "trial" --type link

# Get links for context (smart matching)
python3 /home/workspace/N5/scripts/content_library.py context "calendar scheduling"

# Get specific item by ID
python3 /home/workspace/N5/scripts/content_library.py get trial_code_general

# List all items
python3 /home/workspace/N5/scripts/content_library.py list --type link --category scheduling

# Mark item as used (tracks usage)
python3 /home/workspace/N5/scripts/content_library.py mark-used trial_code_general
```

### Integration Points

**1. Follow-Up Email Generator**
- Automatically queries database when commitments mention links
- Maps promises to actual URLs (e.g., "I'll send trial link" → `trial_code_general`)
- Ensures no broken promises or missing links in emails

**2. Meeting Intelligence Pipeline**
- Scans B02_COMMITMENTS.md for resource promises
- Flags when promised items don't exist in database
- Suggests adding missing links

**3. Communication Workflows**
- LinkedIn posts referencing product links
- Email templates with calendar links
- Any workflow that needs consistent resource delivery

## Common Query Patterns

| Promise Made | Query Command | Expected Results |
|--------------|---------------|------------------|
| "I'll send you a trial link" | `context "trial"` | Trial code links (general, friends/family, career centers) |
| "Here's my calendar" | `context "calendar meeting scheduling"` | Vrijen's meeting scheduling links |
| "Check out our website" | `search "website" --type link` | Careerspan main website |
| "I'll share the pitch deck" | `search "pitch deck"` | Deck link or snippet |
| "Here's our demo" | `context "demo product"` | Product demo links |

## Maintenance

### Adding New Items

```python
# Direct SQL insert
sqlite3 /home/workspace/N5/data/content_library.db
INSERT INTO items (id, type, title, url, created_at, updated_at)
VALUES ('new_link_id', 'link', 'New Link Title', 'https://...', datetime('now'), datetime('now'));

INSERT INTO tags (item_id, tag_key, tag_value)
VALUES ('new_link_id', 'category', 'product');
```

### Deprecating Items

```sql
UPDATE items SET deprecated = 1, notes = 'Replaced by X' WHERE id = 'old_item_id';
```

### Updating URLs

```sql
UPDATE items SET url = 'https://new-url.com', updated_at = datetime('now') WHERE id = 'item_id';
```

## Quality Standards

**All items MUST have:**
- ✓ Unique, descriptive ID
- ✓ Accurate, current URL (for links)
- ✓ At least one category tag
- ✓ Clear title explaining purpose

**Regular audits:**
- Verify URLs are not broken (run link checker)
- Remove duplicates
- Update deprecated items
- Tag items consistently

## Integration with Follow-Up Email Generator

The Follow-Up Email Generator (v2.0+) integrates with content_library.db in Phase 1 (HARVEST):

1. **Load meeting intelligence** (B02, B25)
2. **Extract promised deliverables** (commitments mentioning links/resources)
3. **Query content library** for each promise:
   - "trial" → Search for trial links
   - "calendar" → Search for scheduling links
   - Specific IDs → Direct lookup
4. **Enrich deliverables map** with actual URLs
5. **Compose email** with correct links embedded

**This ensures:**
- ✓ No missing links in follow-up emails
- ✓ Consistent URLs across all communications
- ✓ Single source of truth for all resources
- ✓ Tracking of which resources are most used

## Migration History

**2025-11-17:** Migrated from `content-library.json` to SQLite database
- Consolidated 66 items (59 links, 7 snippets)
- Archived deprecated JSON files
- Updated all workflows to query database instead of JSON

**Previous system:** JSON-based storage at `N5/prefs/communication/content-library.json`

## Future Enhancements

- [ ] Link health checker (verify URLs are live)
- [ ] Usage analytics (which links are sent most often)
- [ ] Auto-suggest links based on meeting topics
- [ ] Version control for link updates
- [ ] Expiration dates for time-sensitive links (e.g., trial codes)

---

**See also:**
- `file 'N5/scripts/content_library.py'` - Management script
- `file 'N5/schemas/content_library.sql'` - Database schema
- `file 'Prompts/Follow-Up Email Generator.prompt.md'` - Integration example
