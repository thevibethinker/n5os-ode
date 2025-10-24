# Content Library System

**Version:** 1.0.0  
**Created:** 2025-10-22  
**Status:** Active

## Overview

The Content Library is a unified system for managing **links** and **text snippets** (bios, marketing copy, boilerplate descriptions) used across communication workflows. It replaces the previous `essential-links.json` system with a more powerful, searchable, and extensible architecture.

## Architecture

### Core Components

```
N5/prefs/communication/
├── content-library.json      # SSOT for all links and snippets
└── essential-links.json      # DEPRECATED (archived after migration)

N5/scripts/
└── content_library.py        # CLI tool + Python API

Workflows (updated to use content-library):
├── follow-up-email-generator.md
├── meeting-intelligence-orchestrator.md
└── [future workflows]
```

### Schema

Each item in `content-library.json` has:

```json
{
  "id": "unique_identifier",
  "type": "link" | "snippet",
  "title": "Human-readable title",
  "content": "URL or text content",
  "tags": {
    "context": ["email", "chat", "meeting"],
    "audience": ["founders", "investors", "general"],
    "purpose": ["demo", "referral", "education"],
    "tone": ["professional", "casual"],
    "entity": ["vrijen", "careerspan", "zo_partnership"]
  },
  "metadata": {
    "created": "2025-10-22",
    "updated": "2025-10-22",
    "deprecated": false,
    "expires_at": null,
    "version": 1,
    "last_used": null,
    "notes": "Additional context"
  }
}
```

### Tag Dimensions

Items are tagged along multiple axes for intelligent retrieval:

- **context**: Where the item is used (email, chat, meeting, pitch, social, website)
- **audience**: Who receives it (founders, investors, job_seekers, general, friends, family)
- **purpose**: Why it's used (demo, referral, education, scheduling, marketing, partnership)
- **tone**: Communication style (professional, casual, formal)
- **entity**: Related entity (vrijen, careerspan, zo_partnership)
- **duration**: For meetings (15min, 30min, 45min)

## CLI Usage

### Search Items

```bash
# By tags
python3 N5/scripts/content_library.py search --tag audience:founders --tag purpose:referral

# Text search
python3 N5/scripts/content_library.py search --query "bio" --type snippet

# Multiple criteria
python3 N5/scripts/content_library.py search --tag context:email --tag entity:careerspan --type link
```

### Add New Item

```bash
python3 N5/scripts/content_library.py add \
  --id vrijen_bio_short \
  --type snippet \
  --title "Vrijen Bio (Short)" \
  --content "CEO & Co-Founder of Careerspan..." \
  --tag context:email \
  --tag context:social \
  --tag audience:general \
  --tag purpose:introduction \
  --tag entity:vrijen \
  --notes "Use for brief introductions"
```

### Update Item

```bash
python3 N5/scripts/content_library.py update \
  --id vrijen_bio_short \
  --content "Updated bio text..." \
  --notes "Revised 2025-10-22"
```

### Deprecate Item

```bash
python3 N5/scripts/content_library.py deprecate \
  --id old_promo_link \
  --expires-at 2025-12-31
```

### List All

```bash
python3 N5/scripts/content_library.py list
python3 N5/scripts/content_library.py list --show-deprecated
```

### Export

```bash
# Export as markdown
python3 N5/scripts/content_library.py export --tag entity:careerspan --format markdown

# Export as JSON
python3 N5/scripts/content_library.py export --tag audience:investors --format json
```

## Programmatic API

For use in workflows and scripts:

```python
from content_library import ContentLibrary

# Initialize
lib = ContentLibrary()

# Search
items = lib.search(tags={"audience": ["founders"], "purpose": ["referral"]})
investor_items = lib.search(tags={"audience": ["investors"]})

# Get specific item
snippet = lib.get_by_id("vrijen_bio_short")

# Add item
lib.add(
    item_id="new_snippet",
    item_type="snippet",
    title="Title",
    content="Content...",
    tags={"context": ["email"], "audience": ["general"]},
    notes="Context"
)

# Mark as used (tracking)
lib.mark_used("vrijen_bio_short")
```

## Workflow Integration Pattern

Workflows automatically load relevant content based on context:

```python
# In follow-up email generator
from content_library import ContentLibrary

lib = ContentLibrary()

# Load context-appropriate items
relevant_items = lib.search(tags={
    "context": ["email"],
    "entity": ["vrijen", "careerspan"]
})

# Auto-inject meeting links if needed
meeting_links = lib.search(tags={"purpose": ["scheduling"]})

# Track usage
for item in used_items:
    lib.mark_used(item["id"])
```

## Migration Status

**Phase 1: Create System** ✅
- Built content-library.json
- Built content_library.py CLI tool
- Migrated all links from essential-links.json
- Added command registration
- Added deprecation notice to old file

**Phase 2: Parallel Operation** (Current)
- Both systems active
- New items go to content-library only
- Old file marked deprecated

**Phase 3: Update Workflows** (Next)
- Update follow-up-email-generator.md
- Update meeting-intelligence-orchestrator.md
- Any other communication workflows

**Phase 4: Archive Old System**
- Move essential-links.json to Documents/Archive/
- Remove references from workflows

## Maintenance

### Version Control

- Every edit auto-commits via git
- `metadata.version` increments
- Use git diff/revert for history

### Adding Snippets

Common snippet types to add:

1. **Bio Variants**
   - Short (1-2 sentences)
   - Medium (paragraph)
   - Long (full bio with background)

2. **Company Descriptions**
   - Elevator pitch
   - Full description
   - Value proposition variants

3. **Marketing Copy**
   - Campaign-specific messaging
   - Audience-specific pitches
   - Product descriptions

4. **Boilerplate**
   - Email signatures
   - Disclaimers
   - Common responses

### Tagging Best Practices

- **Be specific**: Use multiple tags to enable precise filtering
- **Be consistent**: Use established tag values
- **Add context**: Use `notes` field for usage guidance
- **Track usage**: System records `last_used` automatically

## Principles Compliance

- ✅ **P1 (Human-Readable)**: JSON, clear schema
- ✅ **P2 (SSOT)**: Single content-library.json
- ✅ **P5 (Anti-Overwrite)**: Phased migration, backups
- ✅ **P7 (Dry-Run)**: CLI supports --dry-run flag
- ✅ **P8 (Minimal Context)**: Workflows load only relevant items
- ✅ **P15 (Complete)**: Clear migration phases
- ✅ **P19 (Error Handling)**: CLI validates schema, catches errors
- ✅ **P20 (Modular)**: Separate CLI + API, workflows opt-in
- ✅ **P22 (Language)**: Python (right for JSON + text processing)

## Performance

- **Current scale**: 26 items migrated
- **Expected scale**: 100-200 items max
- **Search performance**: Sub-millisecond (JSON in-memory)
- **No database needed**: JSON optimal for this scale

## Future Enhancements

Potential additions (not currently planned):

- Rich text formatting for snippets (Markdown)
- Template variables for dynamic content
- A/B testing variants tracking
- Analytics on usage patterns
- Integration with CRM for personalization

---

**References:**
- CLI Tool: `file 'N5/scripts/content_library.py'`
- Data File: `file 'N5/prefs/communication/content-library.json'`
- Deprecated: `file 'N5/prefs/communication/essential-links.json'`

---
*2025-10-22*
