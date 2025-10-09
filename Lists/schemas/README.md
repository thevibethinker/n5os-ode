# Lists Schemas

This directory contains JSON Schema definitions for validating list item structures.

## Schemas

- **`lists.item.schema.json`**: Base schema for all list items
  - Required: id, created_at, title, status
  - Optional: body, tags, priority, links, project, due, notes
  - Extensible: `additionalProperties: true` allows custom fields

- **`lists.registry.schema.json`**: Schema for list registry metadata
  - Tracks available lists and their configurations

- **`system-upgrades.schema.json`**: Custom schema for N5 system improvements
  - Specialized fields for tracking technical debt and enhancements

## Usage

These schemas enable:
- **Validation**: Every list operation validates against schema
- **Portability**: Lists remain interpretable without N5 OS
- **Extensibility**: Custom lists can add specialized fields
- **Type Safety**: Ensures data consistency across operations

## Related

- Data: `../*.jsonl`
- Scripts: `/home/workspace/N5/scripts/n5_lists_*.py`
- Governance: `../POLICY.md`
