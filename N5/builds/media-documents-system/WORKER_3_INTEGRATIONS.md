# BUILD WORKER 3: Cross-System Integrations

Build Orchestrator: con_L3ITnGAwWvfxEKz3
Task: W3-INTEGRATIONS
Time: 50-60 minutes
Depends On: Workers 1 & 2 Complete

## Mission
Integrate Media & Documents system with Essential Link System, Meetings, CRM, and Follow-up Email Generator.

## Context Files (MUST READ)
- /home/.z/workspaces/con_L3ITnGAwWvfxEKz3/media_documents_architecture_v2.md (Sections 6 & 7)
- WORKER_1_COMPLETION_REPORT.md
- WORKER_2_COMPLETION_REPORT.md

## Deliverables

### 1. Essential Link System Integration
Location: /home/workspace/N5/scripts/media_documents/essentiallink_integration.py

Functions:
- generate_persistent_id() - Create MD-YYYYMMDD-XXXX IDs
- register_with_essentiallink(content_id, persistent_id)
- resolve_reference(persistent_id) - Return content details
- update_cross_references() - Sync bidirectional links

Update content_items table: ensure persistent_id field populated for all items.

### 2. Meeting Intelligence Integration
Location: /home/workspace/N5/scripts/media_documents/meeting_integration.py

Functions:
- pre_meeting_content_pull(meeting_id, contact_names, topics)
  - Query content by taxonomy tags matching topics
  - Query content linked to contact via CRM
  - Return relevant content list for meeting prep

- post_meeting_content_link(meeting_id, content_ids)
  - Create meeting_references entries
  - Update both meeting DB and media_documents DB

Test with actual meeting from /home/workspace/Personal/Meetings/

### 3. CRM Integration
Location: /home/workspace/N5/scripts/media_documents/crm_integration.py

**Critical:** CRM database location TBD - check with V for path.

Functions:
- link_content_to_contact(content_id, contact_id, relationship_type)
  - Create entry in contact_content_xref table
  - Update both databases

- get_contact_relevant_content(contact_id)
  - Query content by contact's industry/role/interests
  - Return ranked list

- get_content_relevant_contacts(content_id)
  - From content topics, find matching contacts
  - Return potential follow-up list

### 4. Follow-up Email Integration
Location: /home/workspace/N5/scripts/media_documents/email_integration.py

Functions:
- generate_content_summary_for_email(content_ids)
  - Format content summaries for email body
  - Include persistent_ids for reference

- suggest_content_for_followup(contact_id, meeting_id)
  - Based on meeting topics + contact profile
  - Return content recommendations with formatted summaries

Integration point: Follow-up email generator should call these functions.

### 5. Knowledge/ Bidirectional Linking
Location: /home/workspace/N5/scripts/media_documents/knowledge_sync.py

Functions:
- sync_knowledge_links() - Scan Knowledge/ for media_documents references
- create_backlinks() - Update cross_references table
- validate_links() - Check for broken references

## Success Criteria
- Essential Link IDs generated for all content
- Pre-meeting content pull works with test meeting
- CRM integration tested (1 content <-> 1 contact)
- Email summary generation works
- Knowledge/ bidirectional links validated
- All integrations have error handling (P11, P19)

## Testing Protocol
# Generate persistent IDs
python3 /home/workspace/N5/scripts/media_documents/essentiallink_integration.py generate-all

# Test meeting integration
python3 /home/workspace/N5/scripts/media_documents/meeting_integration.py   pre-meeting-pull --meeting-id <test_meeting>

# Test CRM link
python3 /home/workspace/N5/scripts/media_documents/crm_integration.py   link-content --content-id 1 --contact-id <test_contact>

# Test email summary
python3 /home/workspace/N5/scripts/media_documents/email_integration.py   generate-summary --content-ids 1,2,3

# Sync Knowledge/ links
python3 /home/workspace/N5/scripts/media_documents/knowledge_sync.py sync

## Open Questions for V (ask in completion report)
1. CRM database path - where is it?
2. Follow-up email generator location - integration point?
3. Essential Link System registry location - where to register?

## Handoff
Create WORKER_3_COMPLETION_REPORT.md with integration test results and open questions.

## Critical Principles
- P2: Single source of truth - use cross-references, not duplication
- P11: Halt on missing dependencies (CRM path, etc.)
- P19: Defensive coding - check all external dependencies

Created: 2025-11-03 21:00 ET
