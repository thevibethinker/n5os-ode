---
tool: true
description: Standardize a meeting folder by adding frontmatter and renaming to a clear, greppable format
tags: [meetings, standardization, naming, organization]
created: 2025-11-04
last_edited: 2025-11-04
version: 1.0
---

# Standardize Meeting Folder

**Purpose:** Add frontmatter to intelligence files and rename meeting folder to standard format after B26 generation.

---

## Format

`YYYY-MM-DD_lead-participant_context_subtype`

**Example good names:**
```
2025-09-12_greenlight_recruiting-discovery_sales
2025-10-09_alex-caveny_founder-burnout_coaching
2025-09-02_aniket_recruiting-collab_partnership
2025-11-03_team_standup_standup
```

**Example bad names (avoid):**
```
2025-09-02_ld-network_gpt-exp-go-to-market_partnership     ❌ Used CRM codes instead of actual name
2025-09-12_potential-client-customer_product-demo-sales-d_sales  ❌ Mechanical extraction, truncated, redundant
2025-10-09_advisorycoaching_founder-burnout-reco_coaching  ❌ Smashed words together
```

---

## Field Requirements

### 1. Date (YYYY-MM-DD)
- Extract from B26 **Meeting ID** or **Date** field
- ISO 8601 format

### 2. Lead Participant
**CRITICAL: Use ACTUAL NAMES, not CRM codes or classifications**

**External meetings:**
- Company name: `greenlight`, `wisdom-partners`, `careerspan`
- Person name: `alex-caveny`, `aniket`, `allie-cialeo`
- ❌ NEVER use: `ld-net`, `gpt-exp`, `potential-client-customer`

**Internal meetings:**
- Use descriptor: `team`, `cofounder`, `leadership`

**How to extract:**
1. Read the **Attendees** section in B26
2. Find the external party (if external meeting)
3. Use their actual name/company
4. Lowercase, hyphenate spaces

### 3. Context (2-4 words)
**Be semantic, not mechanical**

Good contexts:
- `recruiting-discovery` (what it was about)
- `founder-burnout` (the topic)
- `referral-networks` (key theme)
- `go-to-market` (subject)

Bad contexts:
- `product-demo-sales-d` (mechanical extraction, truncated)
- `talent-quality-filte` (truncated)
- `community-builder-fo` (truncated)

**How to extract:**
1. Read **Key Themes** or **Rationale** in B26
2. Pick 2-4 words that capture the essence
3. Be concise but descriptive
4. Lowercase, hyphenate

### 4. Subtype
Pick ONE from taxonomy:

**External:**
- `coaching` - 1-1 advisory/coaching sessions
- `partnership` - Business partnerships, collaborations
- `sales` - Discovery calls, demos, customer meetings
- `workshop` - Group sessions, workshops
- `discovery` - Early exploration
- `ai-consulting` - AI advisory work
- `career-advising` - Career guidance
- `general` - Other external

**Internal:**
- `standup` - Team standups, daily syncs
- `technical` - Technical discussions, architecture
- `planning` - Strategy, planning, war rooms
- `cofounder` - 1-1s with cofounders
- `general` - Other internal

**How to infer:**
1. Read **Stakeholder Classification** in B26
2. Look for keywords matching taxonomy
3. Use context from **CRM Tags** and **Rationale**

---

## Process

When this prompt is invoked:

1. **Read B26_metadata.md** from the meeting folder
2. **Extract the 4 fields** using rules above
3. **Validate:**
   - Date is YYYY-MM-DD format
   - Lead participant is actual name (not code)
   - Context is 2-4 words, no truncation
   - Subtype matches taxonomy
4. **Add frontmatter** to all B*.md files (if missing):
```yaml
---
created: YYYY-MM-DD
last_edited: YYYY-MM-DD
version: 1.0
block_id: B##
---
```
5. **Rename folder** to standard format
6. **Log the rename** to `rename_log.jsonl`

---

## Validation Checklist

Before finalizing name, verify:
- ✅ Date is 10 characters (YYYY-MM-DD)
- ✅ Lead participant is recognizable (not a code)
- ✅ Context describes what meeting was about
- ✅ Subtype matches one from taxonomy
- ✅ No truncated words
- ✅ All lowercase, hyphenated
- ✅ 4 parts separated by underscores

---

## Usage

**Automated:** Runs automatically in pipeline after B26 generation

**Manual:**
```
@standardize_meeting_folder [meeting-folder-path]
```

Or:
```bash
python3 /home/workspace/N5/scripts/meeting_pipeline/standardize_meeting.py <meeting_id>
```
