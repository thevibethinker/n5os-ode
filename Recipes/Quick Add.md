---
description: 'Command: quick-add'
tags:
- lists
- text-processing
- categorization
---
# `quick-add`

Version: 1.0.0

Summary: Process text input and automatically categorize into appropriate lists with smart URL recognition.

Workflow: lists

Tags: lists, text-processing, smart-categorization, urls

## Inputs
- text : string (optional) — Text to process
- --stdin : flag — Read text from stdin
- --non-interactive : flag — Skip diagnostic questions, use auto-categorization
- --dry-run : flag — Preview without adding to lists

## Outputs
- items : list — List of created items with IDs and assignments
- summary : text — Processing summary

## Side Effects
- writes:file (JSONL list files)
- modifies:file (list contents)

## Examples
- Quick add from command line: `python N5/scripts/n5_text_to_list_processor.py "Check out this LinkedIn profile https://linkedin.com/in/example"`
- Interactive mode: `python N5/scripts/n5_text_to_list_processor.py "Remember to call Sarah about the project"`
- Batch processing: `echo "Task 1\nTask 2\nTask 3" | python N5/scripts/n5_text_to_list_processor.py --stdin`
- Non-interactive: `python N5/scripts/n5_text_to_list_processor.py "System needs upgrade" --non-interactive`

## Smart Categorization Rules
- LinkedIn profiles/companies → CRM/contacts
- GitHub repositories → projects/development  
- YouTube videos → media/content
- Twitter/X posts → social/social-media
- Blog articles → reading/articles
- News articles → news/reading
- System keywords → system-upgrades
- Default fallback → ideas

## Related Components

**Related Commands**: [`lists-add`](../commands/lists-add.md), [`lists-create`](../commands/lists-create.md), [`lists-find`](../commands/lists-find.md)

**Scripts**: [`n5_text_to_list_processor.py`](../scripts/n5_text_to_list_processor.py), [`listclassifier.py`](../scripts/listclassifier.py)

**Knowledge Areas**: [List Management](../knowledge/list-management.md), [Smart Categorization](../knowledge/smart-categorization.md)

**Examples**: See [Examples Library](../examples/) for usage patterns