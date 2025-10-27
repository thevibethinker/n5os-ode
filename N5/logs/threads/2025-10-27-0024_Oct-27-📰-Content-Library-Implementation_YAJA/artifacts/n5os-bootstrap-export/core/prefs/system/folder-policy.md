# Folder Policy (Anchor-based)

Updated: 2025-10-24

Purpose: prevent sprawl and duplicates by resolving all new paths against canonical anchors.

- Anchors registry: file 'N5/config/anchors.json'
- Rules:
  - New folders must resolve via anchors; synonyms map to the anchor path.
  - Disallow case-variant siblings (e.g., Projects vs projects).
  - Temp/staging: Records/Temporary only.
  - Logs live in N5/logs.
  - Resumes live in Documents/Resumes.
  - Exports live in N5/exports.
- Exceptions: explicitly whitelisted project sub-structures.
- Enforcement: pre-flight guard is called by commands; background hygiene audits flag violations.
