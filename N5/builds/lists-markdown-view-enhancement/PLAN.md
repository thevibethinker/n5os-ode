---
created: 2025-12-24
last_edited: 2025-12-24
version: 1.0
provenance: con_tD6dy87hIIevo1Zw
---

# PLAN: Lists Markdown View Enhancement

## Purpose
Enhance the Lists system's markdown view generation to include content from hybrid entries (JSONL entries with linked markdown files). Currently, the view only shows JSONL fields (title, tags, notes) and does not pull in the full content from associated markdown files.

## Problem Statement
Current behavior:
- `n5_lists_add.py` creates a basic markdown view with JSONL metadata
- Hybrid entries (with `links` field pointing to `.md` files) only show title/tags/notes
- Full content from linked markdown is NOT displayed in the view

Desired behavior:
- Markdown view should detect hybrid entries and:
  1. Read linked markdown file(s) from `links[*].value`
  2. Extract key sections (summary, ingredients, steps, metadata)
  3. Embed content intelligently in the markdown view
  4. Fallback gracefully if link is broken or file missing

## Architecture Overview

### Current System
```
JSONL Entry
├── title, tags, notes, status
└── links[0].value → "Lists/content/recipes/c58cc6dd-spaghetti-carbonara.md"

Markdown View (recipes.md)
├── Generated from JSONL ONLY
└── Missing: Linked markdown content
```

### Enhanced System
```
JSONL Entry + Linked MD
├── title, tags, notes, status
└── links[0].value → "Lists/content/recipes/c58cc6dd-spaghetti-carbonara.md"
    ├── Full recipe content
    └── Should be embedded in view

Enhanced Markdown View (recipes.md)
├── JSONL metadata (title, tags, notes)
└── Linked markdown content (embedded sections)
```

## Decision Logic for Hybrid Entries

### When to Embed Content
An item is considered hybrid if:
- `links` field exists AND is non-empty
- At least one link has `type: "file"`

### Content Embedding Strategy
1. **Read linked file**: Load markdown from `links[0].value`
2. **Parse frontmatter**: Extract YAML frontmatter for structured data
3. **Content extraction**:
   - If recipe-like: Extract Ingredients, Instructions, Metadata sections
   - If generic: Extract all sections between headers
   - Truncate if too long (configurable limit)
4. **Embed in view**: Add as collapsible section or full content block
5. **Error handling**: If file missing, show placeholder with warning

### Markdown View Structure
```
## Title (JSONL)

**ID:** <uuid>
**Tags:** <tags>
**Status:** <status>

### Notes
<notes from JSONL>

---

<if hybrid entry>

### 📄 Linked Content
<content from linked markdown file>

</if hybrid entry>

---
```

## Implementation Plan

### Phase 1: Analysis & Script Inspection
- [x] Examine `n5_lists_add.py` markdown view generation logic
- [x] Identify `n5_docgen.py` as actual view generator
- [x] Locate `render_list_md()` function (line 289)
- [x] Review existing markdown parsing patterns in N5 scripts
- [x] Define content extraction rules for different entry types

### Phase 2: Create Content Extractor Module
- [x] Create `N5/scripts/n5_lists_content_extractor.py`
- [x] Implement `read_linked_markdown()` function
- [x] Implement `parse_frontmatter()` function (YAML extraction)
- [x] Implement `extract_content_sections()` function
- [x] Implement `get_truncated_preview()` for long content
- [x] Add error handling for missing/broken links

### Phase 3: Integrate into Docgen Script
- [x] Modify `n5_docgen.py` to import content extractor
- [x] Update `render_list_md()` function to:
  - [x] Detect hybrid entries (links field exists)
  - [x] Call content extractor for hybrid entries
  - [x] Embed extracted content in markdown view
  - [x] Handle errors gracefully (file not found, parse errors)
- [x] Test with existing `recipes` list

### Phase 4: Enhance Other List Scripts
- [ ] Update `n5_lists_set.py` to regenerate view with content
- [ ] Update `n5_lists_find.py` to show content in search results
- [ ] Update any other scripts that modify list entries

### Phase 5: Testing & Validation
- [ ] Test with `recipes` list (existing hybrid entry)
- [ ] Test with non-hybrid lists (ideas, must-contact)
- [ ] Test with broken link (verify error handling)
- [ ] Test with long content (verify truncation works)
- [ ] Verify markdown view syntax is valid
- [ ] Run validation script to ensure no regressions

## Affected Files

### New Files
- `N5/scripts/n5_lists_content_extractor.py` - Content extraction module

### Modified Files
- `N5/scripts/n5_lists_add.py` - Main list addition script
- `N5/scripts/n5_lists_set.py` - List item modification script
- `N5/scripts/n5_lists_find.py` - List search script (optional enhancement)

## Testing Strategy

### Unit Tests
- Test `read_linked_markdown()` with valid paths
- Test `read_linked_markdown()` with missing paths (should handle gracefully)
- Test `parse_frontmatter()` with YAML frontmatter
- Test `parse_frontmatter()` without frontmatter (should return empty dict)
- Test `extract_content_sections()` with recipe format
- Test `extract_content_sections()` with generic markdown

### Integration Tests
- Add new hybrid entry → verify view includes content
- Modify existing hybrid entry → verify view updates
- Add non-hybrid entry → verify view works normally
- Test with long content → verify truncation

## Edge Cases & Considerations
- Multiple links: Only embed first `type: "file"` link
- Non-markdown links: Skip or show as reference
- Circular references: Detect and prevent infinite loops
- Very long content: Implement sensible truncation (configurable)
- Empty markdown files: Handle gracefully
- Malformed frontmatter: Parse errors should not break view

## Success Criteria
- [x] Hybrid entries show full content in markdown view
- [x] Non-hybrid entries work exactly as before
- [x] Broken links show helpful error messages
- [x] Long content is truncated appropriately
- [x] All tests pass
- [x] Validation script confirms no regressions

## Rollback Plan
If implementation causes issues:
1. Git revert to commit before enhancement
2. All existing functionality will be restored
3. Hybrid entries will simply not show content (current behavior)



### Phase 4: Enhance Other List Scripts
- [N/A] Update `n5_lists_set.py` to regenerate view with content
- [N/A] Update `n5_lists_find.py` to show content in search results
- [N/A] Update any other scripts that modify list entries

### Phase 5: Testing & Validation
- [x] Test with `recipes` list (existing hybrid entry)
- [x] Test with non-hybrid lists (ideas, must-contact)
- [x] Test with broken link (verify error handling)
- [x] Test with long content (verify truncation works)
- [x] Verify markdown view syntax is valid
- [x] Run validation script to ensure no regressions

### Phase 6: Finalize
- [x] Update PLAN.md with completion status
- [x] Update session state with build summary






