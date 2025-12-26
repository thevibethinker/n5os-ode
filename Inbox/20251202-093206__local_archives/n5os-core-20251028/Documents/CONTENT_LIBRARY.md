# Content Library

**Version:** 1.0.0  
**Last Updated:** 2025-10-27  
**Category:** Knowledge Management

---

## Overview

The Content Library is a unified knowledge management system for **links and text snippets** that startup founders and operators need to reuse frequently. It provides intelligent auto-classification, multi-dimensional tagging, and fast retrieval.

### Use Cases

- **Founder Bios**: Store multiple versions (concise/detailed, formal/casual) for different contexts
- **Product Descriptions**: Maintain pitch variations for investors, customers, partners
- **Scheduling Links**: Quick access to Calendly, meeting templates, availability
- **Resource Links**: Articles, tools, documentation you reference frequently
- **Email Signatures**: Context-appropriate signatures for different audiences
- **Referral Codes**: Promo codes, affiliate links, discount offers
- **Pitch Hooks**: Opening lines, value propositions, compelling intros
- **Support Resources**: FAQ answers, troubleshooting snippets, onboarding text
- **Sales Templates**: Proposals, pricing snippets, objection responses

---

## Core Concepts

### Item Types

- **Link**: URL with optional description
- **Snippet**: Reusable text block

### Multi-Dimensional Tags

Content is automatically classified across multiple dimensions:

1. **Purpose** - Primary use case (bio, pitch, resource, etc.)
2. **Audience** - Who it's for (founders, investors, customers, etc.)
3. **Tone** - Communication style (concise, formal, technical, etc.)
4. **Entity** - Related entities (company, product, person)
5. **Category** - Custom organizational tags

### Auto-Classification

The system automatically infers tags based on:
- **Keyword signals** - Recognizes domain-specific terminology
- **Word count** - Detects concise vs. detailed content
- **Patterns** - Identifies formal language, technical jargon, storytelling elements

### Lifecycle Management

- **Version tracking** - Every update increments version number
- **Deprecation** - Mark outdated items without deleting them
- **Expiration** - Set time-to-live for time-sensitive content (promo codes, event links)
- **Usage tracking** - Track when items are last accessed

---

## Quick Start

### Installation

The content library is included in n5OS core. Ensure you have:

```bash
/home/workspace/N5/scripts/n5_content_library.py
/home/workspace/N5/config/content-library.json
```

### Initialize

Create your first item:

```bash
n5 content-add link "My Calendly" \
  --url "https://calendly.com/yourname/30min" \
  --notes "Main scheduling link"
```

### Search

Find content by keyword:

```bash
n5 content-search --query "calendly"
```

Filter by tags:

```bash
n5 content-search --tags '{"purpose": ["scheduling"]}'
```

### View Stats

```bash
n5 content-stats
```

---

## Command Reference

### `content-add`

Add new item to library.

```bash
n5 content-add <type> "<title>" [OPTIONS]
```

**Types:** `link` | `snippet`

**Options:**
- `--content <text>` - Text content (required for snippets)
- `--url <url>` - URL (required for links)
- `--id <custom-id>` - Custom ID (optional, auto-generated if omitted)
- `--tags <json>` - Manual tags as JSON object
- `--notes <text>` - Notes about this item

**Examples:**

```bash
# Add a link
n5 content-add link "Team Handbook" \
  --url "https://notion.so/team-handbook" \
  --notes "Internal reference only"

# Add a snippet with custom tags
n5 content-add snippet "30-second pitch" \
  --content "We help startup founders..." \
  --tags '{"purpose": ["pitch"], "audience": ["investors"], "tone": ["concise"]}'

# Add a snippet with custom ID
n5 content-add snippet "Bio - Concise" \
  --id "bio-concise" \
  --content "Jane Doe is the founder of..."
```

---

### `content-search`

Search and filter library items.

```bash
n5 content-search [OPTIONS]
```

**Options:**
- `--query <text>` - Keyword search across title, content, URL, tags
- `--type <type>` - Filter by type (`link` | `snippet`)
- `--tags <json>` - Filter by tags (JSON object)
- `--include-deprecated` - Include deprecated items
- `--include-expired` - Include expired items
- `--max <n>` - Max results (default: 50)

**Examples:**

```bash
# Search by keyword
n5 content-search --query "pitch"

# Filter by purpose
n5 content-search --tags '{"purpose": ["bio"]}'

# Filter by audience and tone
n5 content-search --tags '{"audience": ["investors"], "tone": ["formal"]}'

# Get all snippets
n5 content-search --type snippet

# Include deprecated items
n5 content-search --include-deprecated
```

---

### `content-get`

Retrieve item by ID (updates "last_used" timestamp).

```bash
n5 content-get <id>
```

**Example:**

```bash
n5 content-get bio-concise
```

---

### `content-update`

Update existing item.

```bash
n5 content-update <id> [OPTIONS]
```

**Options:**
- `--title <text>` - New title
- `--content <text>` - New content
- `--url <url>` - New URL
- `--tags <json>` - Replace tags (JSON object)
- `--deprecate` - Mark as deprecated
- `--notes <text>` - Update notes

**Examples:**

```bash
# Update content
n5 content-update bio-concise \
  --content "Updated bio text here..."

# Deprecate old version
n5 content-update bio-old-version --deprecate

# Update tags
n5 content-update my-link \
  --tags '{"purpose": ["resource"], "category": ["engineering"]}'
```

---

### `content-delete`

Permanently delete item.

```bash
n5 content-delete <id>
```

**Example:**

```bash
n5 content-delete old-promo-code
```

**Warning:** This is permanent. Consider using `--deprecate` for soft deletion.

---

### `content-stats`

Show library statistics.

```bash
n5 content-stats
```

**Output:**
- Total items
- Breakdown by type
- Deprecated count
- Expired count
- Top purposes
- Top audiences

---

## Configuration

Configuration file: `N5/config/content-library.json`

### Default Configuration

```json
{
  "library_path": "./data/content-library.json",
  "auto_classify": true,
  "classification_rules": {
    "purpose_signals": {
      "bio": ["founder", "ceo", "background", "experience"],
      "pitch": ["pitch deck", "investor", "fundraising"],
      "scheduling": ["calendly", "meeting", "book", "schedule"],
      "product": ["feature", "product", "demo", "launch"],
      ...
    },
    "audience_signals": {
      "founders": ["founder", "startup", "entrepreneur"],
      "investors": ["investor", "fundraising", "pitch"],
      ...
    },
    "tone_signals": {
      "concise": {"max_words": 50},
      "detailed": {"min_words": 200},
      ...
    }
  },
  "search_defaults": {
    "include_deprecated": false,
    "include_expired": false,
    "max_results": 50
  }
}
```

### Customizing Classification Rules

Edit `content-library.json` to add your own signals:

```json
{
  "classification_rules": {
    "purpose_signals": {
      "custom_purpose": ["keyword1", "keyword2"]
    },
    "entity_extraction": {
      "custom_entities": ["YourCompany", "YourProduct"]
    }
  }
}
```

---

## Data Storage

### File Format

Library stored as JSON: `Knowledge/content-library.json`

### Schema

Follows schemas in:
- `schemas/content-library.item.schema.json`
- `schemas/content-library.registry.schema.json`

### Example Item

```json
{
  "id": "bio-concise",
  "type": "snippet",
  "title": "Bio - Concise (50 words)",
  "content": "Jane Doe is the founder of...",
  "tags": {
    "purpose": ["bio"],
    "audience": ["general"],
    "tone": ["concise"]
  },
  "metadata": {
    "created": "2025-10-27T12:00:00Z",
    "updated": "2025-10-27T12:00:00Z",
    "deprecated": false,
    "version": 1,
    "last_used": "2025-10-27T14:30:00Z",
    "notes": "For LinkedIn, conference bios",
    "source": "manual"
  }
}
```

---

## Integration with Other N5 Systems

### Email Generation

Content library integrates with follow-up email generator:

```bash
n5 email --meeting-folder /path/to/meeting --use-content-library
```

Automatically inserts appropriate signatures, bios, scheduling links based on context.

### Knowledge Base

Content library complements Knowledge system:
- **Knowledge**: Long-form strategic insights, research, context
- **Content Library**: Reusable tactical snippets and links

### Lists System

Export content library stats to lists for tracking:

```bash
n5 content-stats | n5 lists-add content-library-metrics
```

---

## Best Practices

### Naming Conventions

- **Links**: Use descriptive titles: "Team Handbook (Notion)" not "Handbook"
- **Snippets**: Include length/version: "Bio - Concise (50 words)" not "Bio"

### Tagging Strategy

- **Be specific**: Use multiple tags from different dimensions
- **Use custom categories**: Add project-specific tags as needed
- **Review auto-tags**: Check what the system inferred, refine if needed

### Lifecycle Management

- **Deprecate, don't delete**: Keep history for reference
- **Set expiration**: Add `expires_at` for time-sensitive content
- **Version incrementally**: Don't overwrite - create new version with new ID

### Organization

- **Purpose-first**: Primary organization by purpose (bio, pitch, etc.)
- **Audience-second**: Filter by who it's for
- **Tone-third**: Narrow by communication style

---

## Troubleshooting

### Item not auto-classified correctly

**Solution:** Add manual tags during creation:

```bash
n5 content-add snippet "My Text" \
  --content "..." \
  --tags '{"purpose": ["correct-purpose"]}'
```

### Search returns too many results

**Solution:** Use multi-dimensional filtering:

```bash
n5 content-search \
  --type snippet \
  --tags '{"purpose": ["bio"], "tone": ["concise"]}'
```

### Need to bulk-update tags

**Solution:** Edit `Knowledge/content-library.json` directly, or write a script:

```python
import json
from pathlib import Path

lib_path = Path.home() / "workspace/Knowledge/content-library.json"
with open(lib_path) as f:
    lib = json.load(f)

# Bulk update logic here
for item in lib["items"]:
    if "old-tag" in item.get("tags", {}).get("category", []):
        item["tags"]["category"].append("new-tag")

with open(lib_path, "w") as f:
    json.dump(lib, f, indent=2)
```

---

## Advanced Usage

### Programmatic Access

Use the Python class directly:

```python
from n5_content_library import ContentLibrary
from pathlib import Path

lib = ContentLibrary(
    library_path=Path.home() / "workspace/Knowledge/content-library.json",
    config_path=Path.home() / "workspace/N5/config/content-library.json"
)

# Add item
item = lib.add_item(
    item_type="snippet",
    title="My snippet",
    content="Text here...",
    tags={"purpose": ["bio"]}
)

# Search
results = lib.search(
    query="founder",
    tags={"audience": ["investors"]}
)

# Get by ID
item = lib.get_item("bio-concise")
```

### Export for Training

Extract high-quality content for LLM training:

```bash
# Export all approved content
n5 content-search --tags '{"category": ["approved"]}' > training-data.json
```

---

## Roadmap

**Completed:**
- ✅ Core library system (links + snippets)
- ✅ Auto-classification
- ✅ Multi-dimensional tagging
- ✅ Lifecycle management
- ✅ Schema validation

**Future:**
- 🔄 Web UI for browsing/editing
- 🔄 Browser extension for quick-add
- 🔄 Import from bookmarks/notes apps
- 🔄 Analytics dashboard (usage trends, popular items)
- 🔄 Collaborative sharing between n5OS users

---

## Support

- **Documentation**: `/docs/CONTENT_LIBRARY.md`
- **Schemas**: `/schemas/content-library.*.schema.json`
- **Config Example**: `/config/content-library.example.json`
- **Issues**: Report via n5OS issue tracker

---

**Built with n5OS architectural principles:**
- P1 (Human-Readable): JSON format, clear naming
- P2 (SSOT): Single registry file
- P5 (Anti-Overwrite): Version tracking
- P8 (Minimal Context): Focused on reusable content only
- P19 (Error Handling): Comprehensive validation
- P21 (Document Assumptions): Auto-classification rules documented

