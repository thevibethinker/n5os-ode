# Lessons & Learnings Schema

## System Learnings Schema v2

System-wide learnings that apply across all builds are stored in `SYSTEM_LEARNINGS.json`.

### Entry Format

```json
{
  "text": "string",
  "source": "manual|sms|build|inference",
  "origin_build": "string|null",
  "added_at": "ISO8601",
  "tags": ["string"],
  
  // Confidence & Validation
  "confidence": 0.7,           // 0.0-1.0, default 0.7
  "validated_count": 0,        // times this learning was confirmed
  "last_validated": null,      // ISO8601 or null
  
  // Expiration
  "decay_days": 30,            // days until confidence starts decaying
  "expires_at": null,          // ISO8601, null = never expires
  
  // Status Tracking
  "status": "active",          // active|disputed|invalidated|expired
  "disputed_by": null,         // reference to contradicting source
  "dispute_reason": null       // explanation of dispute
}
```

### Field Descriptions

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `text` | string | required | The learning content |
| `source` | string | "manual" | Where this came from: manual, sms, build, or inference |
| `origin_build` | string|null | null | Build slug if source is "build" |
| `added_at` | ISO8601 | now | When the learning was first recorded |
| `tags` | string[] | [] | Tags for categorization |
| `confidence` | float | 0.7 | Confidence score (0.0-1.0). Increases on validation, decays over time |
| `validated_count` | int | 0 | Number of times this learning has been explicitly validated |
| `last_validated` | ISO8601|null | null | Last time this was validated |
| `decay_days` | int | 30 | Days before confidence starts decaying if unvalidated |
| `expires_at` | ISO8601|null | null | Hard expiration date. null = never expires |
| `status` | string | "active" | Current state: active, disputed, invalidated, expired |
| `disputed_by` | string|null | null | Reference to source that contradicts this learning |
| `dispute_reason` | string|null | null | Explanation of why this learning was disputed |

### Status Values

- **active**: The learning is current and considered reliable
- **disputed**: The learning has been challenged and should not be applied until resolved
- **invalidated**: The learning was confirmed false and should be ignored
- **expired**: The learning has passed its expiration date or decay threshold

### Confidence Decay Logic

When `expire_stale_learnings()` runs:

1. For learnings with `expires_at` set:
   - If `now > expires_at`: status → "expired"

2. For learnings with `decay_days` but no `expires_at`:
   - If `last_validated` is null:
     - If `now > added_at + decay_days`: status → "expired"
   - If `last_validated` is set:
     - If `now > last_validated + decay_days`: status → "expired"

### CLI Commands

```bash
# Add a learning with custom confidence and decay
python3 Skills/pulse/scripts/pulse_learnings.py add <slug> "learning text" --system --confidence 0.9 --decay-days 60

# Validate a learning (boosts confidence)
python3 Skills/pulse/scripts/pulse_learnings.py validate <slug> <index>

# Dispute a learning
python3 Skills/pulse/scripts/pulse_learnings.py dispute <slug> <index> "reason why this is wrong"

# Invalidate a learning
python3 Skills/pulse/scripts/pulse_learnings.py invalidate <slug> <index>

# Mark stale learnings as expired
python3 Skills/pulse/scripts/pulse_learnings.py expire-stale
```

### Backward Compatibility

The system supports both schema v1 (without confidence/status fields) and v2. When loading learnings:
- Missing fields are filled with defaults (confidence: 0.7, status: "active", etc.)
- Old entries can be validated to upgrade them to v2

---

## Lesson Entry Format (Legacy)

```json
{
  "id": "L-YYYYMMDD-NNN",
  "created": "ISO8601",
  "source": {
    "type": "build|integration|debug|manual",
    "build_slug": "optional",
    "drop_id": "optional",
    "convo_id": "optional"
  },
  "category": "stub_code|missing_validation|architecture|dependency|other",
  "severity": "critical|high|medium|low",
  "description": "What went wrong",
  "root_cause": "Why it happened",
  "detection": "How it was caught",
  "resolution": "How it was fixed (if fixed)",
  "prevention": "How to prevent in future",
  "tags": ["tag1", "tag2"],
  "status": "open|resolved|systemic",
  "related_lessons": ["L-YYYYMMDD-NNN"]
}
```

## Categories (Legacy)

- **stub_code**: TODO/STUB/placeholder code that doesn't work
- **missing_validation**: No test caught the issue
- **architecture**: Design flaw that caused downstream issues
- **dependency**: Missing or broken dependency
- **other**: Uncategorized