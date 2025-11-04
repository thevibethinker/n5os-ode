---
description: 'Command: incantum-quickref'
tool: true
tags: []
---
# Incantum Quick Reference

Natural language triggers that invoke N5 commands.

---

## Lists

- "add to [list]" → lists-add
- "find in lists" → lists-find
- "export lists" → lists-export
- "check list health" → lists-health-check

## Knowledge

- "add to knowledge" → knowledge-add
- "find in knowledge" → knowledge-find
- "ingest this" → knowledge-ingest

## Thread Management

- "close thread" / "end conversation" → conversation-end
- "export this" / "export thread" → thread-export

## CRM

- "find [person/company]" → crm-find
- "search crm for [query]" → crm-find

## Tally Surveys

- "create survey" / "make a form" → tally-create
- "list surveys" / "show my forms" → tally-list
- "get survey [id]" → tally-get
- "survey responses" → tally-submissions

## Git

- "check git" → git-check
- "audit git" → git-audit

## Documentation

- "rebuild index" → index-rebuild
- "generate docs" → docgen

## System

- "scan placeholders" → placeholder-scan
- "core audit" → core-audit

---

**See:** `file 'N5/config/incantum_triggers.json'` for complete mappings  
**See:** `file 'N5/prefs/system/command-triggering.md'` for details
