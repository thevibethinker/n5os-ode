---
created: 2025-11-18
last_edited: 2025-11-18
version: 1.0
---

# CRM V3 Database Schema

**Database:** `crm_v3.db`  
**Location:** `/home/workspace/N5/data/crm_v3.db`  
**Created:** 2025-11-18 01:57:21 ET  
**Orchestrator:** con_RxzhtBdWYFsbQueb  
**Worker:** W1-DB-SCHEMA

## Tables Overview

| Table | Purpose | Records | Foreign Keys |
|-------|---------|---------|--------------|
| `profiles` | Core profile data | 0 | None |
| `enrichment_queue` | Async enrichment tasks | 0 | → profiles |
| `calendar_events` | Google Calendar events | 0 | None |
| `event_attendees` | Event-profile mapping | 0 | → calendar_events, → profiles |
| `intelligence_sources` | Intelligence tracking | 0 | → profiles |

## Relationships

```
profiles (1) ──→ (N) enrichment_queue
profiles (1) ──→ (N) event_attendees
profiles (1) ──→ (N) intelligence_sources

calendar_events (1) ──→ (N) event_attendees
```

## Table Details

### `profiles`
**Purpose:** Core profile data with enrichment tracking

**Key Columns:**
- `email` (UNIQUE): Primary identifier
- `yaml_path` (UNIQUE): Path to source-of-truth YAML file
- `enrichment_status`: 'pending' | 'in_progress' | 'complete' | 'failed'
- `profile_quality`: 'stub' | 'basic' | 'enriched' | 'comprehensive'
- `category`: 'ADVISOR' | 'INVESTOR' | 'COMMUNITY' | 'NETWORKING' | 'OTHER'

**Indexes:** email, enrichment_status, source, category

### `enrichment_queue`
**Purpose:** Scheduled enrichment tasks with priority queue

**Key Columns:**
- `profile_id`: Foreign key to profiles
- `priority`: 0-100 (higher = more urgent)
- `checkpoint`: 'initial' | 'pre_meeting' | 'morning_of'
- `status`: 'queued' | 'processing' | 'complete' | 'failed'
- `trigger_source`: 'calendar_webhook' | 'manual' | 'email_reply'

**Indexes:** status, priority DESC, scheduled_for, profile_id

### `calendar_events`
**Purpose:** Google Calendar event storage

**Key Columns:**
- `event_id` (UNIQUE): Google Calendar event ID
- `summary`: Meeting title
- `start_time`, `end_time`: ISO8601 timestamps
- `attendee_count`: Number of attendees linked

**Indexes:** event_id, start_time

### `event_attendees`
**Purpose:** Many-to-many relationship between events and profiles

**Key Columns:**
- `event_id`: Foreign key to calendar_events
- `profile_id`: Foreign key to profiles
- `response_status`: 'accepted' | 'declined' | 'tentative' | 'needsAction'
- `is_organizer`: 0 or 1

**Constraints:** UNIQUE(event_id, profile_id)  
**Indexes:** event_id, profile_id

### `intelligence_sources`
**Purpose:** Track all intelligence blocks linked to profiles

**Key Columns:**
- `profile_id`: Foreign key to profiles
- `source_type`: 'b08_block' | 'aviato_enrichment' | 'gmail_thread' | etc.
- `source_path`: Path to meeting file, email ID, etc.
- `source_date`: Date of intelligence
- `summary`: One-line summary

**Indexes:** profile_id, source_type, source_date DESC

## Foreign Key Cascades

All foreign keys use `ON DELETE CASCADE`:

- Deleting a profile automatically removes:
  - All enrichment queue items
  - All event attendee links
  - All intelligence sources
  
- Deleting a calendar event automatically removes:
  - All event attendee links

## Migration Notes

This schema serves as the **queryable index** while YAML files remain the **source of truth**.

The database enables:
- Fast lookups by email, category, enrichment status
- Priority queue for async enrichment
- Calendar event webhook processing
- Intelligence source tracking

**Next Worker:** W2-MIGRATION (Worker 2 - Migration Scripts)
