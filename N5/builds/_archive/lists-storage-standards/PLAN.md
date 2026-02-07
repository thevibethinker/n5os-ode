---
created: 2025-12-24
last_edited: 2025-12-24
version: 1.0
provenance: con_tD6dy87hIIevo1Zw
---

# PLAN: Lists Storage Standards & Content Classification System

## Purpose
Define a standardized approach for storing information in the Lists system, including when to use JSONL-only entries vs. hybrid JSONL+markdown references, with full implementation for a recipe list as proof of concept.

## Context
- V's Lists system uses JSONL as SSOT with a `links` field for external references
- No documented standards exist for when to create external markdown files
- Need a hybrid pattern for complex content (recipes, procedures, frameworks)
- Recipe list is the first use case requiring this pattern

## Checklist

- [x] **Phase 1: Standards Document**
  - [x] Create `Documents/System/Lists-Storage-Standards.md`
  - [x] Document content classification matrix (Atomic/Reference/External)
  - [x] Define decision criteria for each type
  - [x] Establish file location conventions
  - [x] Specify YAML frontmatter standards
  - [x] Include validation/orphan detection guidance

- [x] **Phase 2: System Integration**
  - [x] Update `Lists/POLICY.md` with reference to new standards
  - [x] Create `Lists/content/recipes/` directory
  - [x] Create `Lists/templates/recipe-template.md`

- [x] **Phase 3: Recipe List Implementation (Proof of Concept)**
  - [x] Create `Lists/recipes.jsonl` with proper schema
  - [x] Register `recipes` in `Lists/index.jsonl`
  - [x] Create example hybrid recipe (JSONL + markdown)
  - [x] Verify JSONL→Markdown link works

- [x] **Phase 4: Validation Script (Bonus from Level Upper Review)**
  - [x] Create `N5/scripts/n5_lists_validate.py`
  - [x] Implement orphan detection for `links[*].value` files
  - [x] Test validation on existing lists
  - [x] Fix path resolution bug (resolved against WORKSPACE_ROOT)

- [x] **Phase 5: Session State Update**
  - [x] Update SESSION_STATE.md with completed artifacts
  - [ ] Switch back to Operator

---

## Affected Files by Phase

### Phase 1
- **Create:** `Documents/System/Lists-Storage-Standards.md`

### Phase 2
- **Modify:** `Lists/POLICY.md`
- **Create:** `Lists/content/recipes/` (directory)
- **Create:** `Lists/templates/recipe-template.md`

### Phase 3
- **Create:** `Lists/recipes.jsonl`
- **Modify:** `Lists/index.jsonl` (add recipes registration)
- **Create:** `Lists/content/recipes/{id}-example-recipe.md`

### Phase 4
- **Create:** `N5/scripts/n5_lists_validate.py`

---

## Unit Tests

### Phase 1
- N/A (documentation only)

### Phase 2
- Verify `Lists/POLICY.md` references new standards document
- Verify directory `Lists/content/recipes/` is created

### Phase 3
- Verify `Lists/recipes.jsonl` passes schema validation
- Verify `Lists/index.jsonl` contains `recipes` entry
- Verify example JSONL entry has `links: [{type: "file", value: "..."}]`
- Verify linked markdown file exists at expected path

### Phase 4
- Test script on lists with broken links → should report orphans
- Test script on valid lists → should pass silently
- Test script on list without `links` field → should handle gracefully





