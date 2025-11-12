# N5OS Lite Directory Structure

## Overview

N5OS Lite uses a simple, hierarchical directory structure designed for clarity and maintainability. Each directory has a specific purpose and follows consistent naming conventions.

## Recommended Structure

```
workspace/
├── Prompts/              # Reusable AI workflows and procedures
├── Knowledge/            # Long-term reference and documentation
│   ├── architectural/    # System design docs
│   ├── technical/        # Technical references
│   └── domain/           # Domain-specific knowledge
├── Personal/             # Personal content and planning
│   ├── Journal/          # Daily notes and reflections
│   ├── Planning/         # Goals and project planning
│   └── Meetings/         # Meeting notes and follow-ups
├── Projects/             # Active work projects
│   └── [project-name]/   # Individual project directories
├── Inbox/                # Temporary staging area
├── Archive/              # Completed or obsolete content
└── N5/                   # System intelligence (optional)
    ├── prefs/            # System preferences
    ├── scripts/          # Utility scripts
    └── docs/             # System documentation
```

## Directory Purposes

### Prompts/
Reusable AI workflows stored as markdown files. These can be invoked by mentioning them with `@` in chat or discovered via prompt listing tools.

**Characteristics:**
- Markdown files with YAML frontmatter
- Include description and tags for discoverability
- Self-contained, executable instructions

### Knowledge/
Long-term reference documentation organized by category.

**Subcategories:**
- `architectural/` - System design patterns, planning frameworks
- `technical/` - Programming references, API docs
- `domain/` - Business/domain-specific knowledge

**Principles:**
- Single Source of Truth (P2) - canonical references only
- Human-Readable First (P1) - markdown over structured formats

### Personal/
Personal content not directly related to project work.

**Subcategories:**
- `Journal/` - Daily notes, reflections, learning logs
- `Planning/` - Strategic planning, goal tracking
- `Meetings/` - Meeting notes with standard format

### Projects/
Active work organized by project. Each project is self-contained.

**Structure:**
```
Projects/
└── project-name/
    ├── README.md         # Project overview
    ├── docs/             # Project documentation
    ├── src/              # Source code/content
    └── data/             # Project-specific data
```

### Inbox/
Temporary staging for incoming content that needs processing or filing.

**Usage:**
- Quick captures
- Downloads pending review
- Content awaiting categorization

**Principle:** Flow Over Pools - everything in Inbox has exit conditions

### Archive/
Completed or obsolete content preserved for reference.

**When to archive:**
- Project completed and no longer active
- Content outdated but worth preserving
- Historical reference value

## Naming Conventions

### Files
- Use lowercase with hyphens: `my-document.md`
- Date prefix for chronological content: `2025-11-03-meeting-notes.md`
- Descriptive names, avoid abbreviations
- Consistent extensions: `.md` for documentation, `.yaml` for configs

### Directories
- TitleCase for top-level: `Knowledge/`, `Projects/`
- lowercase-with-hyphens for projects: `my-project/`
- Clear, descriptive names
- Plural for collections: `Meetings/`, `Projects/`

## Protection System

Mark directories that should not be moved or deleted by creating a `.protected` file:

```bash
# Create protection
echo "reason: Contains critical system configurations" > /path/to/directory/.protected

# Check if protected
# (Use your system's protection checking mechanism)
```

Protected directories require explicit confirmation before modification.

## Best Practices

1. **Keep It Flat**: Avoid deep nesting (>3 levels). Flat structures are easier to navigate.

2. **Clear Naming**: Directory/file names should be self-explanatory. Future you will thank you.

3. **Regular Cleanup**: Review Inbox weekly. Archive completed projects monthly.

4. **SSOT Compliance**: Each piece of information lives in one place. Use links, not copies.

5. **Flow Management**: Everything in Inbox has an exit condition (file to project, knowledge, or archive).

## Migration Guide

If adopting N5OS Lite structure:

1. **Audit Current Structure**: List all top-level directories
2. **Map to N5 Categories**: Where does each fit?
3. **Create Target Structure**: Set up recommended directories
4. **Gradual Migration**: Move content over time, not all at once
5. **Update Links**: Fix any broken references
6. **Archive Old**: Keep old structure in Archive during transition

## Customization

This structure is a recommendation, not a requirement. Adapt to your needs:

- Add categories relevant to your work
- Adjust naming conventions to your preferences
- Keep what works, change what doesn't

**Core Principle:** Structure should serve your workflow, not constrain it.

---

*For more on organizational principles, see file 'principles/P02_single_source_truth.yaml'*
