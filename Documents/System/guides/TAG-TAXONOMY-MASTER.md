# N5 Tag Taxonomy — Master Reference

**Version:** 3.1.0 (Hashtag Format)  
**Date:** 2025-10-12  
**Status:** Active — Centralized tagging framework
**Changes in v3.1.0:** Fixed semantic collision - Priority is N5-only (binary), Accommodation owns [A-*]

---

## Overview

This is the **single source of truth** for all N5 tagging.

**Format:** Hashtags (`#category:value`) for all internal N5 use  
**External Integration:** Auto-translate to brackets for Howie (`[LD-INV]`)  
**Rationale:** Hashtags are more ergonomic, self-documenting, and extensible

---

## Tag Categories

### 1. Stakeholder Types (`#stakeholder:*`)

Primary classification of external contacts.

| Hashtag | Description | Howie Bracket | Priority Default |
|---------|-------------|---------------|------------------|
| `#stakeholder:investor` | Investors, VCs, funding sources | `[LD-INV]` | `#priority:critical` |
| `#stakeholder:community` | Community partners, nonprofits | `[LD-COM]` | `#priority:non-critical` |
| `#stakeholder:partner:collaboration` | Integration/collaboration partners | `[LD-NET]` | `#priority:non-critical` |
| `#stakeholder:partner:channel` | Distribution/resale partners | `[LD-NET]` | `#priority:non-critical` |
| `#stakeholder:prospect` | General leads, exploratory contacts | `[LD-GEN]` | `#priority:non-critical` |
| `#stakeholder:customer` | Paying customers | *(N5 only)* | `#priority:critical` |
| `#stakeholder:vendor` | Service providers, suppliers | *(N5 only)* | `#priority:non-critical` |
| `#stakeholder:advisor` | Strategic advisors, mentors | *(N5 only)* | `#priority:critical` |
| `#stakeholder:networking_contact` | Relationship beyond business context | *(N5 only)* | `#priority:non-critical` |

**Partner Subtypes:**
- `:collaboration` — Integration, co-marketing, joint initiatives
- `:channel` — Distribution, resale, affiliate relationships

**Removed from stakeholder types:**
- ~~`#stakeholder:job_seeker`~~ → Moved to `#status:job_seeking` (V's insight: job seeking is a state, not a type)

**Notes:**
- Tags marked *(N5 only)* have no Howie equivalent and are not synced
- Investor, advisor, customer stakeholders auto-inherit `#priority:critical`
- Anyone can have `#status:job_seeking` regardless of stakeholder type

---

### 2. Relationship Status (`#relationship:*`)

Describes the current state of the relationship.

| Hashtag | Description | When to Use |
|---------|-------------|-------------|
| `#relationship:new` | First contact, no history | First meeting or initial email exchange |
| `#relationship:warm` | Active, engaged, responsive | 5+ emails/month, regular contact |
| `#relationship:active` | Ongoing collaboration | Current partnership, recurring meetings |
| `#relationship:cold` | No recent contact | 30+ days since last interaction |
| `#relationship:dormant` | Past relationship, inactive | Previous partnership/customer, no current engagement |

**Notes:**
- These tags are **N5 only** (internal relationship tracking)
- Not synced to Howie

---

### 3. Priority Level (`#priority:*`)

**IMPORTANT:** Priority is now **N5-only** and **binary** (critical vs non-critical).  
**Priority ≠ Accommodation:** Priority = importance to business. Accommodation = meeting flexibility.

| Hashtag | Description | Howie Bracket | Behavior |
|---------|-------------|---------------|----------|
| `#priority:critical` | Business-critical (investors, customers, advisors) | `!!` | Protect time, never let slip, high responsiveness |
| `#priority:non-critical` | Important but not urgent (community, recruiting, exploratory) | *(N5 only)* | Standard responsiveness, can defer if needed |

**Auto-inheritance:**
- `#stakeholder:investor` → Auto-assigns `#priority:critical`
- `#stakeholder:advisor` → Auto-assigns `#priority:critical`
- `#stakeholder:customer` → Auto-assigns `#priority:critical`
- `#stakeholder:job_seeker` → Auto-assigns `#priority:non-critical`
- `#stakeholder:community` → Auto-assigns `#priority:non-critical`
- `#stakeholder:prospect` → Auto-assigns `#priority:non-critical`
- `#stakeholder:vendor` → Auto-assigns `#priority:non-critical`

**Note:** Partners (collaboration/channel) do not auto-inherit; priority depends on strategic value.

---

### 4. Engagement Status (`#engagement:*`)

Communication behavior and responsiveness.

| Hashtag | Description | When to Use |
|---------|-------------|-------------|
| `#engagement:responsive` | Quick replies (<4 hours avg) | Fast responders, high engagement |
| `#engagement:slow` | Slow responses (>24 hours avg) | Low engagement, need patience |
| `#engagement:needs_followup` | Waiting on their response | V sent last message, awaiting reply |
| `#engagement:waiting_on_us` | Waiting on our response | They sent last message, V needs to reply |

**Notes:**
- Auto-suggested based on email analysis
- N5 only (not synced to Howie)

---

### 5. Context/Industry (`#context:*`)

Domain or industry classification.

| Hashtag | Description |
|---------|-------------|
| `#context:hr_tech` | HR technology, recruiting tech |
| `#context:venture_capital` | VC firms, investment funds |
| `#context:saas` | SaaS companies |
| `#context:enterprise` | Enterprise buyers/users |
| `#context:startup` | Startup ecosystem |
| `#context:nonprofit` | Nonprofit, social impact |

**Notes:**
- Extensible: add new contexts as needed
- N5 only (not synced to Howie)
- Multiple context tags allowed per contact

---

### 6. Meeting Type (`#type:*`)

Type of meeting or interaction.

| Hashtag | Description | Howie Usage |
|---------|-------------|-------------|
| `#type:discovery` | First meeting, exploratory | Auto from `[LD-*]` tags |
| `#type:partnership` | Partnership discussion | Auto from `[LD-COM]` |
| `#type:followup` | Follow-up meeting | Manual or auto-suggested |
| `#type:recurring` | Regular recurring meeting | Auto-detected from calendar |

---

### 7. Job Seeking Status (`#job_seeking:*`)

Whether contact is currently seeking employment.

| Hashtag | Description | Use Cases |
|---------|-------------|-----------|
| `#job_seeking:active` | Currently seeking employment | Interviewing, using Careerspan product, job search active |
| `#job_seeking:inactive` | Not currently seeking | Employed and settled, not looking |

**V's Principle:** "Job seeking is a state, not a stakeholder type. Anyone can be job seeking."

**Examples:**
- Community leader who is job seeking: `#stakeholder:community` + `#job_seeking:active`
- Advisor who is job seeking: `#stakeholder:advisor` + `#job_seeking:active`
- Investor between roles: `#stakeholder:investor` + `#job_seeking:active`

**Benefits:**
- Clean orthogonal taxonomy (type vs. state)
- No dual stakeholder classification needed
- Tracks career transitions (active → inactive when placed)
- Can track product usage lifecycle (job_seeking:active users)

**Notes:**
- N5 only (not synced to Howie)
- Most contacts won't have this tag (only relevant if job seeking)
- Default: No tag (assume inactive unless evidence of active search)

---

### 8. Status Tags (`#status:*`)

Meeting or relationship status.

| Hashtag | Description | Howie Bracket | Behavior |
|---------|-------------|---------------|----------|
| `#status:postponed` | Meeting postponed/rescheduled | `[OFF]` | Skip in digest |
| `#status:awaiting` | Awaiting confirmation | `[AWA]` | Mark as tentative |
| `#status:inactive` | Relationship terminated | `[TERM]` | Skip in digest |
| `#status:active` | Currently active | *(default)* | Include in digest |

**Note:** `#status:job_seeking` moved to its own category `#job_seeking:*` (V's insight)

---

### 9. Schedule Tags (`#schedule:*`)

Timing constraints for scheduling.

| Hashtag | Description | Howie Bracket |
|---------|-------------|---------------|
| `#schedule:within_5d` | Schedule within 5 business days | `[D5]` |
| `#schedule:5d_plus` | Schedule 5+ business days out | `[D5+]` |
| `#schedule:10d_plus` | Schedule 10+ business days out | `[D10]` |

---

### 10. Coordination Tags (`#align:*`)

Internal coordination requirements.

| Hashtag | Description | Howie Bracket |
|---------|-------------|---------------|
| `#align:logan` | Align with Logan's schedule | `[LOG]` |
| `#align:ilse` | Align with Ilse's schedule | `[ILS]` |
| `#align:founders` | Align with founders | `[GPT-F]` |

---

### 11. Accommodation Level (`#accommodation:*`)

Flexibility and accommodation approach.

| Hashtag | Description | Howie Bracket | Meeting Behavior |
|---------|-------------|---------------|------------------|
| `#accommodation:minimal` | On our terms only | `[A-0]` | Strong position, clear requirements |
| `#accommodation:baseline` | Standard flexibility | `[A-1]` | Default approach |
| `#accommodation:full` | Fully accommodating | `[A-2]` | Understand their needs first |

---

### 12. Availability Tags (`#availability:*`)

Scheduling availability preferences.

| Hashtag | Description | Howie Bracket |
|---------|-------------|---------------|
| `#availability:weekend_ok` | Weekends allowed | `[WEX]` |
| `#availability:weekend_preferred` | Prefer weekends | `[WEP]` |

---

### 13. Follow-up Tags (`#followup:*`)

Automated follow-up reminders.

| Hashtag | Description | Howie Bracket |
|---------|-------------|---------------|
| `#followup:external_N` | Follow up with external party in N days | `[F-N]` |
| `#followup:logan_N` | Private follow-up to Logan in N days | `[FL-N]` |
| `#followup:vrijen_N` | Personal reminder in N days | `[FM-N]` |

**Example:** `#followup:external_7` → Remind to follow up with contact in 7 days

---

## Tag Combination Rules

### Recommended Tag Sets

**New Investor Contact:**
```
#stakeholder:investor
#relationship:new
#priority:critical
#type:discovery
#context:venture_capital
```

**Active Partnership:**
```
#stakeholder:partner:collaboration
#relationship:active
#priority:normal
#type:partnership
#context:hr_tech
#engagement:responsive
```

**Advisor Relationship:**
```
#stakeholder:advisor
#relationship:active
#priority:high
#context:enterprise
#engagement:responsive
```

**Cold Prospect:**
```
#stakeholder:prospect
#relationship:cold
#priority:low
#engagement:slow
```

---

## Translation Layer (Howie Integration)

### Hashtag → Bracket Mapping

**Location:** `N5/config/tag_mapping.json`

**Bidirectional translation:**
- **N5 → Howie:** Convert hashtags to brackets when creating calendar events
- **Howie → N5:** Parse brackets from calendar descriptions, convert to hashtags

**N5-only tags (not sent to Howie):**
- `#relationship:*`
- `#engagement:*`
- `#context:*`
- `#stakeholder:customer`
- `#stakeholder:vendor`
- `#stakeholder:advisor`

**See:** `file '/home/.z/workspaces/con_eceInSZIEtjzb9zS/TAG-FORMAT-PROPOSAL.md'` for full translation spec

---

## Tag Usage Guidelines

### When to Add Tags

**Stakeholder profiles:**
- Add stakeholder type on first contact
- Add relationship status after 2-3 interactions
- Add engagement status after 5+ emails
- Add context tags as discovered

**Meeting prep:**
- Tags extracted from calendar descriptions
- Auto-translate brackets to hashtags
- Display in meeting digest

**Weekly review:**
- System suggests tags based on email analysis
- V reviews and confirms
- Tags marked as "verified" with timestamp

### Tag Verification Levels

**Suggested (unverified):**
- Auto-generated by system
- Shown with confidence score
- Require V's review

**Verified (confirmed):**
- Approved by V
- Timestamped
- Used for downstream decisions (Howie, meeting prep, CRM)

---

## Tag Hierarchy

Tags use colon notation for hierarchical subtypes:

```
#stakeholder:partner                    ← Parent
  ├── #stakeholder:partner:collaboration  ← Subtype 1
  └── #stakeholder:partner:channel        ← Subtype 2
```

**Benefits:**
- Allows granular filtering (`#stakeholder:partner:*` matches both)
- Maintains semantic clarity
- Extensible without breaking existing tags

---

## Configuration Files

### `N5/config/tag_mapping.json`
Bidirectional translation between hashtags and brackets

### `N5/config/tag_taxonomy.json`
Full tag list with descriptions and metadata

### `N5/config/tagging_rules.json`
Tag suggestion logic and confidence thresholds

### `N5/schemas/stakeholder_tags.schema.json`
JSON schema for tag validation

---

## Scripts & Tools

### `N5/scripts/tag_translator.py`
Convert between hashtag and bracket formats

### `N5/scripts/apply_verified_tags.py`
Apply confirmed tags to stakeholder profiles

### `N5/scripts/analyze_stakeholder_patterns.py`
Auto-suggest tags based on email analysis

### `N5/scripts/query_contacts.py`
Search contacts by tags

---

## Examples

### Example 1: Hamoon Ekhtiari (FutureFit)

**Verified Tags:**
```
#stakeholder:partner:collaboration
#relationship:new
#priority:normal
#engagement:needs_followup
#context:hr_tech
```

**Howie Calendar Translation:**
```
[LD-NET] [A-1] *

Purpose: Partnership exploration with FutureFit
```

---

### Example 2: Alex Caveny (Advisor)

**Verified Tags:**
```
#stakeholder:advisor
#relationship:active
#priority:high
#context:enterprise
#engagement:responsive
```

**Howie Calendar Translation:**
```
*(No Howie equivalent—advisor is N5-only)*

Purpose: Strategic coaching session
```

---

### Example 3: Carly Ackerman (Coca-Cola)

**Verified Tags:**
```
#stakeholder:advisor
#relationship:warm
#priority:high
#context:enterprise
#context:hr_tech
```

**Howie Calendar Translation:**
```
*(No Howie equivalent—advisor is N5-only)*

Purpose: Enterprise HR advisory — alumni network partnerships
```

**Note:** Currently at Coca-Cola, previously at Eightfold AI (Director of Customer Experience)

---

### Example 4: Kim Wilkes (UPDATED — Job Seeking as Status)

**Verified Tags:**
```
#stakeholder:community
#job_seeking:active
#relationship:active
#priority:critical
#context:hr_tech
#engagement:responsive
```

**Howie Calendar Translation:**
```
[LD-COM] *

Purpose: Women in tech community partnerships
```

**Note:** Kim is a community stakeholder with active job-seeking status (using Careerspan product for job search). Clean separation: stakeholder type (community) vs. employment state (job seeking).

**Product tracking:** `#job_seeking:active` indicates she's using Careerspan, track placement outcome. When placed: Update to `#job_seeking:placed`

---

### Example 5: Tim He (Networking Contact)

**Suggested Tags:**
```
#stakeholder:networking_contact
#relationship:active
#priority:normal
#context:saas
```

**Howie Calendar Translation:**
```
*(No Howie equivalent—networking contact is N5-only)*

Purpose: General networking, relationship building
```

**Note:** Hiring candidate context but V sees as networking relationship beyond hiring

---

## Migration Notes

### From Bracket System (Old)

**Before (brackets in N5):**
```
[LD-INV] [D5+] *
Stakeholder Type: Investor
```

**After (hashtags in N5):**
```
#stakeholder:investor
#type:discovery
#priority:critical
#schedule:5d_plus
```

**Calendar descriptions still use brackets** (for Howie compatibility), but N5 internal storage and display uses hashtags.

---

## Tag Validation Rules

### Required Tags (Stakeholder Profiles)
- `#stakeholder:*` — REQUIRED (primary classification)

### Optional Tags
- `#relationship:*` — Recommended after 2+ interactions
- `#priority:*` — Auto-assigned or manual
- `#engagement:*` — Auto-suggested from email analysis
- `#context:*` — Add as discovered
- All others — Use as needed

### Mutually Exclusive Tags
- Only one `#stakeholder:*` per contact (use most specific)
- Only one `#relationship:*` per contact
- Only one `#priority:*` per contact

---

## Changelog

### v3.2.0 (2025-10-12) — Job Seeking Reclassification
- **BREAKING:** Removed `#stakeholder:job_seeker` stakeholder type
- **NEW:** Added `#job_seeking:*` category (active, inactive)
- **Principle:** Job seeking is a state, not a type (V's insight)
- **Impact:** Eliminates dual stakeholder classification, cleaner taxonomy
- Updated all examples (Kim Wilkes no longer dual stakeholder type)

### v3.1.0 (2025-10-12)
- **BREAKING:** Fixed semantic collision - Priority is N5-only (binary), Accommodation owns [A-*]
- **BREAKING:** Removed [A-0], [A-1], [A-2] mappings from priority
- **BREAKING:** Updated priority section to reflect new binary system
- **BREAKING:** Updated auto-inheritance rules for priority

### v3.0.0 (2025-10-12)
- **BREAKING:** Migrated from brackets to hashtags for all N5 internal use
- Added partner subtypes (`:collaboration`, `:channel`)
- Added translation layer for Howie integration
- Consolidated all tagging docs into master reference

### v2.0.0 (2025-10-11)
- Harmonized with Howie V-OS tag system
- Added full bracket mapping

### v1.0.0 (2025-10-09)
- Initial N5 tagging system (hashtags)

---

**Related Documentation:**
- `file 'N5/docs/calendar-tagging-system-COMPLETE.md'` — Calendar event tagging (bracket format for Howie)
- `file 'N5/docs/howie-zo-harmonization-complete.md'` — Howie ↔ Zo integration
- `file '/home/.z/workspaces/con_eceInSZIEtjzb9zS/TAG-FORMAT-PROPOSAL.md'` — Hashtag format proposal
- `file '/home/.z/workspaces/con_eceInSZIEtjzb9zS/stakeholder-auto-tagging-plan.md'` — Auto-tagging implementation plan
