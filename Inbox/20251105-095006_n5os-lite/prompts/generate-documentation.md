---
tool: true
description: Generate comprehensive documentation for code, systems, or processes
tags: [documentation, technical-writing, workflow]
version: 1.0
created: 2025-11-03
---

# Generate Documentation

Create clear, comprehensive documentation for code, systems, or processes.

## Instructions

**You are generating documentation. Identify the documentation type and follow the appropriate template:**

### Step 1: Identify Documentation Type

Choose appropriate type:
- **API Documentation:** Functions, classes, endpoints
- **System Documentation:** Architecture, components, data flow
- **User Guide:** How to use a tool or system
- **Process Documentation:** Workflows, procedures, protocols
- **Code Documentation:** Inline comments, module docs

### Step 2: Gather Information

Depending on type:

**For Code:**
- Read source files
- Identify public interfaces
- Note parameters, return types, exceptions
- Find usage examples

**For Systems:**
- Map components and relationships
- Identify data flows
- Document dependencies
- Note configuration requirements

**For Processes:**
- List steps in sequence
- Identify decision points
- Note prerequisites
- Document success criteria

### Step 3: Choose Template

Select appropriate structure:

#### API Documentation Template

```markdown
# [Module/Class Name]

## Overview
[Brief description of purpose and use cases]

## Installation
```bash
[Installation command]
```

## Quick Start
```python
[Minimal working example]
```

## API Reference

### [FunctionName]
**Purpose:** [What it does]

**Parameters:**
- `param1` (type): Description
- `param2` (type): Description

**Returns:** (type) Description

**Raises:**
- `ExceptionType`: When this happens

**Example:**
```python
[Usage example]
```

### [NextFunction]
[Continue pattern]

## Advanced Usage
[Complex scenarios, patterns, best practices]

## Troubleshooting
[Common issues and solutions]
```

#### System Documentation Template

```markdown
# [System Name]

## Overview
[High-level description, purpose, key capabilities]

## Architecture

### Components
- **Component A:** [Purpose and responsibility]
- **Component B:** [Purpose and responsibility]

### Data Flow
[Describe how data moves through system]

```
[Optional: Include diagram]
```

## Setup

### Prerequisites
- [Requirement 1]
- [Requirement 2]

### Installation
1. [Step 1]
2. [Step 2]

### Configuration
[Required configuration with examples]

## Usage

### Basic Operations
[Common tasks with examples]

### Advanced Features
[Complex scenarios]

## Maintenance

### Monitoring
[What to watch, how to check health]

### Troubleshooting
[Common issues and solutions]

### Backup/Recovery
[How to backup and restore]

## Reference

### Configuration Options
[Complete configuration reference]

### API/Interfaces
[Technical interface documentation]
```

#### User Guide Template

```markdown
# [Tool/System Name] - User Guide

## Introduction
[What is it, who is it for, what problems does it solve]

## Getting Started

### Installation
[Simple installation steps]

### First Use
[Guided walkthrough of basic task]

## Common Tasks

### [Task 1]
1. [Step 1]
2. [Step 2]

**Example:**
[Concrete example]

### [Task 2]
[Continue pattern]

## Tips and Best Practices
[Helpful advice for effective use]

## Troubleshooting
[Solutions to common problems]

## FAQ
**Q:** [Question]  
**A:** [Answer]

## Getting Help
[Where to find support]
```

#### Process Documentation Template

```markdown
# [Process Name]

**Purpose:** [Why this process exists]  
**Owner:** [Who maintains it]  
**Frequency:** [How often executed]

## Prerequisites
- [Requirement 1]
- [Requirement 2]

## Process Steps

### Phase 1: [Phase Name]

1. **[Step Name]**
   - **Action:** [What to do]
   - **Responsible:** [Who does it]
   - **Duration:** [How long]
   - **Success Criteria:** [How to verify]

2. **[Next Step]**
   [Continue pattern]

### Phase 2: [Next Phase]
[Continue pattern]

## Decision Points

### [Decision Name]
**Condition:** [When this decision is needed]  
**Options:**
- **Option A:** [When to choose, consequences]
- **Option B:** [When to choose, consequences]

## Quality Checks
- [ ] [Verification 1]
- [ ] [Verification 2]

## Troubleshooting
**Issue:** [Problem]  
**Solution:** [Resolution steps]

## Related Processes
- [Related process 1]
- [Related process 2]
```

### Step 4: Write Documentation

Follow template, ensuring:
- **Clear language:** No jargon without definition
- **Concrete examples:** Show, don't just tell
- **Complete coverage:** All important aspects documented
- **Logical structure:** Easy to navigate
- **Current information:** Accurate as of documentation date

### Step 5: Add Metadata

Include at top or in frontmatter:
```yaml
---
title: [Document Title]
version: 1.0
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: draft | active | deprecated
author: [Optional]
---
```

### Step 6: Review Quality

Check documentation quality:
- [ ] Purpose clear from introduction
- [ ] All sections complete (no stubs)
- [ ] Examples concrete and tested
- [ ] Navigation easy (headings, TOC if long)
- [ ] Terminology consistent
- [ ] Links/references valid
- [ ] Up-to-date with current implementation

## Quality Standards

### Good Documentation

- **Scannable:** Can grasp key points in 30 seconds
- **Complete:** Covers all essential information
- **Current:** Reflects actual implementation
- **Tested:** Examples actually work
- **Clear:** Understandable to target audience

### Documentation Principles

1. **Show, don't tell:** Concrete examples > abstract descriptions
2. **Start simple:** Basic usage first, advanced later
3. **Anticipate questions:** Cover what users will wonder
4. **Maintainable:** Easy to update as system changes
5. **Findable:** Good structure, search-friendly

## Anti-Patterns

**❌ Outdated examples**
Code examples that don't work with current version

**✓ Tested examples**
Verify all examples work before publishing

**❌ Jargon without context**
"Utilize the singleton factory pattern"

**✓ Plain language**
"Create one shared instance that all code uses"

**❌ Missing prerequisites**
Assumes reader knows setup steps

**✓ Complete prerequisites**
Lists all requirements and how to verify them

**❌ No examples**
Only abstract descriptions

**✓ Concrete examples**
Show actual usage with real inputs/outputs

## Example: Function Documentation

```python
def process_data(input_path: str, output_path: str, normalize: bool = False) -> dict:
    """
    Process data file and save results.
    
    Reads CSV file, applies transformations, writes processed data to output.
    Optionally normalizes numeric columns to 0-1 range.
    
    Args:
        input_path: Path to input CSV file
        output_path: Path where processed CSV will be saved
        normalize: If True, normalize numeric columns (default: False)
    
    Returns:
        dict: Processing statistics with keys:
            - 'rows_processed': Number of rows processed
            - 'columns': List of column names
            - 'errors': Number of rows with errors
    
    Raises:
        FileNotFoundError: If input_path doesn't exist
        ValueError: If CSV format is invalid
    
    Example:
        >>> stats = process_data('data.csv', 'output.csv', normalize=True)
        >>> print(f"Processed {stats['rows_processed']} rows")
        Processed 1000 rows
    """
    # Implementation
```

---

**Related:**
- Principles: P1 (Human-Readable First)
- Principles: P8 (Minimal Context, Maximal Clarity)
- Prompt: `create-prompt.md`
