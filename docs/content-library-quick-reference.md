---
created: 2025-11-17
last_edited: 2026-03-18
version: 2.0
---

# Content Library Quick Reference

**Database:** `N5/data/content_library.db`  
**CLI Tools:**
- `N5/scripts/content_library.py` — DB operations (search, add, get, stats)
- `N5/scripts/content_query.py` — Quick query interface
- `scripts/content_ingest.py` — File ingestion with normalization pipeline

**Status:** Active (v5 normalization pipeline)

---

## Ingesting Content

```bash
# Auto-detect type and ingest
python3 scripts/content_ingest.py /path/to/article.md

# Specify type explicitly
python3 scripts/content_ingest.py /path/to/file.md --type article

# Preview without changes
python3 scripts/content_ingest.py /path/to/file.md --dry-run

# Ingest and move to canonical location
python3 scripts/content_ingest.py /path/to/file.md --move

# Add tags
python3 scripts/content_ingest.py /path/to/file.md --tags "authored,medium"

# Skip normalization (keep raw content)
python3 scripts/content_ingest.py /path/to/file.md --no-normalize
```

### Content Types
| Type | Canonical Location | Auto-Detection |
|------|-------------------|----------------|
| `article` | `Knowledge/content-library/articles/` | Substack, Medium, news sites |
| `link` | `Knowledge/content-library/links/` | URLs with frontmatter (default) |
| `social-post` | `Knowledge/content-library/social-posts/` | X/Twitter, LinkedIn URLs |
| `profile` | `Knowledge/content-library/profiles/` | LinkedIn /in/ pages |
| `resource` | `Knowledge/content-library/resources/` | Docs, GitHub repos |
| `snippet` | `Knowledge/content-library/snippets/` | Short text blocks |
| `reflection` | `Knowledge/content-library/reflections/` | Personal reflections |
| `conversation` | `Knowledge/content-library/conversations/` | Chat transcripts |

### Normalization Pipeline (v5)
When `--normalize` is enabled (default):
1. **Classification** — Detect content mode (article, link, profile, social)
2. **Trafilatura extraction** — Extract clean text from HTML companion files
3. **Boilerplate removal** — Strip navigation, ads, cookie banners
4. **Summary generation** — Extract first meaningful paragraph as summary

---

## Searching the Library

```bash
# Text search
python3 N5/scripts/content_library.py search --query "trial"

# Filter by type
python3 N5/scripts/content_library.py search --query "trial" --type link

# Search by tag
python3 N5/scripts/content_library.py search --tag purpose=scheduling

# Combined search
python3 N5/scripts/content_library.py search --query "demo" --tag audience=prospects
```

### Get specific item
```bash
python3 N5/scripts/content_library.py get --id trial_code_general
```

### Add new item
```bash
# Add link
python3 N5/scripts/content_library.py add \
  --id new_link \
  --type link \
  --title "New Link Title" \
  --url "https://example.com" \
  --tag purpose=demo \
  --tag entity=your_company

# Add snippet
python3 N5/scripts/content_library.py add \
  --id bio_short \
  --type snippet \
  --title "Short Bio" \
  --content "Example bio snippet..." \
  --tag audience=investors
```

### List all items
```bash
python3 N5/scripts/content_library.py list --limit 50
```

### Deprecate item
```bash
python3 N5/scripts/content_library.py deprecate --id old_link
```

---

## Database Statistics

```bash
# View item counts
sqlite3 N5/data/content_library.db "
SELECT 
  COUNT(*) as total,
  SUM(CASE WHEN type='link' THEN 1 ELSE 0 END) as links,
  SUM(CASE WHEN type='snippet' THEN 1 ELSE 0 END) as snippets
FROM items WHERE deprecated=0;
"

# View all tags
sqlite3 N5/data/content_library.db "
SELECT DISTINCT tag_key FROM tags ORDER BY tag_key;
"

# View items by tag
sqlite3 N5/data/content_library.db "
SELECT i.title, t.tag_value 
FROM items i 
JOIN tags t ON i.id = t.item_id 
WHERE t.tag_key='purpose' 
ORDER BY i.title;
"
```

---

## Common Link Categories

### Meeting Scheduling
- **Tag:** `purpose=scheduling`
- **Examples:** Calendly links, meeting booking URLs

### Product Trials
- **Query:** `trial`
- **Examples:** Signup links, trial access codes

### Demos & Resources
- **Query:** `demo`
- **Examples:** Product walkthroughs, demo videos

### Company Info
- **Tag:** `entity=your_company`
- **Examples:** Homepage, LinkedIn, pitch decks

---

## Integration with Follow-Up Email Generator

The Follow-Up Email Generator automatically queries the database when generating emails:

**Workflow:**
1. AI reads meeting commitments (B02/B25)
2. AI detects promise to share link
3. AI queries database: `search --query "[keyword]"`
4. AI inserts correct URL into email

**No manual lookup required!**

---

## Maintenance Tips

### Weekly
- Review recent items: `list --limit 20`
- Check for duplicates

### Monthly
- Audit deprecated items
- Verify URLs still valid
- Update tags as needed

### When adding new links
- Use consistent naming: `entity_category_specifics`
- Add relevant tags: `purpose`, `audience`, `entity`
- Include notes for context

---

## Schema Reference

**Items table:**
- `id`: Unique identifier
- `type`: "link" or "snippet"
- `title`: Human-readable name
- `content`: Snippet text (for snippets) or URL (for links)
- `url`: URL (for links)
- `deprecated`: 0 (active) or 1 (deprecated)
- `tags`: Multi-value tags in separate table

**Common tags:**
- `purpose`: scheduling, trial, demo, reference, etc.
- `audience`: general, investors, prospects, friends, etc.
- `entity`: owner, your_company, etc.
- `duration`: 15min, 30min, 45min (for meeting links)

---

## Examples

### Find meeting booking link for 30-minute calls
```bash
python3 N5/scripts/content_library.py search --tag duration=30min
```

### Find all company-related links
```bash
python3 N5/scripts/content_library.py search --tag entity=your_company
```

### Get trial link for career centers
```bash
python3 N5/scripts/content_library.py get --id trial_code_career_centers
```

---

*Last updated: 2026-03-18*

