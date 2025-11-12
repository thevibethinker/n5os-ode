# N5 Schemas

**Version:** 3.0  
**Updated:** 2025-11-02

Schemas define canonical formats for N5 artifacts and enable validation.

---

## Core Schemas

### Principle Schema
**Status:** In development  
**Purpose:** Validates all 37 principle YAML files

**Required Fields:**
- id, name, category, priority, version, created
- purpose, when_to_apply, examples, anti_patterns, changelog

### Existing Schemas

**Lists and Knowledge:**
- lists.item.schema.json
- lists.registry.schema.json  
- knowledge.facts.schema.json
- index.schema.json

**Operations:**
- commands.schema.json
- conversation-end-proposal.schema.json
- closure-manifest.schema.json
- phase_handoff.schema.json

**Workflows:**
- inbox_analysis.schema.json
- ingest.plan.schema.json
- meeting-metadata.schema.json
- meeting_gdrive_registry.schema.json

**Integrations:**
- incantum_registry.schema.json
- zobridge.schema.json
- ai_request.schema.json

**Quality:**
- output-review.schema.json
- zo_feedback.schema.json

---

## Usage

Validate JSON:
python3 -m jsonschema -i data.json schema.json

In scripts:
import jsonschema
jsonschema.validate(instance=data, schema=schema)

---

## Integration

Schemas integrate with:
- Principles (N5/prefs/principles/)
- Scripts (N5/scripts/)
- Operations (validation protocols)

---

Last updated: 2025-11-05 11:40 ET
