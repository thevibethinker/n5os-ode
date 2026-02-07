---
name: content-classifier
description: Workspace scanner that classifies every path into Tier 0/1/2 before anything is exported from the Zoffice Consultancy Stack. Keeps client exports safe by design and enforces the dual-sided audit policy.
compatibility: Created for Zo Computer
metadata:
  author: va.zo.computer
  version: "1.0"
  created: "2026-02-06"
created: 2026-02-06
last_edited: 2026-02-06
version: 1.0
provenance: con_GwlFHPrBi5KsNm1X
---

# Content Classifier

## Purpose

Classify every file and directory under `/home/workspace` into one of three export tiers so that the exports streamed to `zoputer.zo.computer` never expose sensitive data. Conservative defaults keep Tier 2 content off the pipeline and surfaces questionable items for V's review.

## Usage

```bash
# Scan a directory and print tier results
python3 Skills/content-classifier/scripts/scan.py classify --path /home/workspace --output /tmp/content-tiers.json

# Generate the export manifest, picking up only Tier 0 assets
python3 Skills/content-classifier/scripts/scan.py manifest --since "2026-02-01" --output N5/builds/consulting-zoffice-stack/CONSULTING_MANIFEST.json

# Check a specific path
python3 Skills/content-classifier/scripts/scan.py check --path /home/workspace/Personal
```

## Integration

Run this scanner before every export step (Drop 3.1), and automatically redact Tier 2 candidates:

```python
from Skills.content-classifier.scripts.scan import classify_path

def safe_export(path):
    tier, reason = classify_path(path)
    if tier == "Tier 2":
        raise RuntimeError(f"Cannot export {path}: {reason}")
    return tier
```
