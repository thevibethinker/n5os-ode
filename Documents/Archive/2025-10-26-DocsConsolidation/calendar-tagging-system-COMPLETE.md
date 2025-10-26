# Calendar Tagging System — Complete Reference

**Version:** 2.0.0 (V-OS Integration)  
**Date:** 2025-10-11  
**Status:** Active — Harmonized with Howie V-OS tags

---

## Overview

This document contains ALL functionality, code, configuration, and references related to the V-OS calendar tagging system for meeting prep digests. This is the single source of truth for the harmonized Howie ↔ Zo tagging taxonomy.

**Key Change:** N5 now uses Howie's V-OS tag format (`[LD-INV]`) instead of the previous hashtag format (`#stakeholder:investor`). This reduces cognitive load and provides a single tag system across both AI assistants.

---

## V-OS Tag Taxonomy

### Lead/Stakeholder Types (`{CATG}`)

```
[LD-INV]  - Investor/VC (CRITICAL priority by default)
[LD-HIR]  - Job seeker (recruiting/hiring)
[LD-COM]  - Community partner
[LD-NET]  - Business partner
[LD-GEN]  - Prospect (general)
```

**Mapping to N5 stakeholder types:**
- `[LD-INV]` → investor, discovery meeting, CRITICAL priority
- `[LD-HIR]` → job_seeker, discovery meeting
- `[LD-COM]` → community, partnership meeting
- `[LD-NET]` → partner, discovery meeting
- `[LD-GEN]` → prospect, discovery meeting

### Timing Constraints (`{TWIN}`)

```
[!!]   - CRITICAL/Urgent (protect time block)
[D5]   - Schedule within 5 days
[D5+]  - Schedule 5+ days out
[D10]  - Schedule 10+ days out
```

**Priority logic:**
- `[!!]` OR `[LD-INV]` = critical (do not reschedule)
- Everything else = non-critical

### Status Tags (`{POST}`)

```
[OFF]  - Postponed (skip in digest)
[AWA]  - Awaiting response/confirmation
[TERM] - Terminated/Inactive (skip in digest)
```

### Coordination Tags (`{CORD}`)

```
[LOG]  - Coordinate with Logan
[ILS]  - Coordinate with Ilse
```

### Weekend Availability (`{WKND}`)

```
[WEX]  - Weekend exception (allowed)
[WEP]  - Weekend preferred
```

### Accommodation Level (`{MISC}`)

```
[A-0]  - Minimal accommodation (clear requirements)
[A-1]  - Baseline accommodation (standard flexibility)
[A-2]  - Full accommodation (understand their needs)
```

### Priority Preferences (`{GPT}`)

```
[GPT-I]  - Prioritize internal meetings
[GPT-E]  - Prioritize external meetings
[GPT-F]  - Prioritize founder meetings
```

### Follow-up Rules (`{FLUP}`)

```
[F-X]   - Follow up in X days
[FL-X]  - Follow up lightly in X days
[FM-X]  - Follow up medium priority in X days
```

### Tag Activation

**Asterisk `*` at END of tag block activates tags:**
```
[LD-INV] [D5+] *

Purpose: Discuss Series A funding timeline
```

Without asterisk, tags are informational only.

---

## Code Implementation

### 1. V-OS Tag Constants

**Location:** `file 'N5/scripts/meeting_prep_digest.py'` lines 41-62

```python
# V-OS Tag System (Howie Integration)
# Lead/Stakeholder types with mappings
LEAD_TYPES = {
    "LD-INV": {"stakeholder": "investor", "type": "discovery", "priority": "critical"},
    "LD-HIR": {"stakeholder": "job_seeker", "type": "discovery"},
    "LD-COM": {"stakeholder": "community", "type": "partnership"},
    "LD-NET": {"stakeholder": "partner", "type": "discovery"},
    "LD-GEN": {"stakeholder": "prospect", "type": "discovery"}
}

# V-OS Tag Categories
TIMING_TAGS = ["!!", "D5", "D5+", "D10"]
STATUS_TAGS = ["OFF", "AWA", "TERM"]
COORD_TAGS = ["LOG", "ILS"]
WEEKEND_TAGS = ["WEX", "WEP"]
ACCOMMODATION_TAGS = ["A-0", "A-1", "A-2"]
PRIORITY_TAGS = ["GPT-I", "GPT-E", "GPT-F"]
FOLLOWUP_TAGS = ["F-", "FL-", "FM-"]
```

### 2. V-OS Tag Parsing Function

**Location:** `file 'N5/scripts/meeting_prep_digest.py'` lines 103-217

```python
def extract_vos_tags(description: str) -> Dict[str, Any]:
    """
    Extract V-OS tags from calendar description.
    Returns structured dict with stakeholder, type, priority, etc.
    
    V-OS Tag Categories:
    - Lead types: [LD-INV], [LD-HIR], [LD-COM], [LD-NET], [LD-GEN]
    - Timing: [!!], [D5], [D5+], [D10]
    - Status: [OFF], [AWA], [TERM]
    - Coordination: [LOG], [ILS]
    - Weekend: [WEX], [WEP]
    - Accommodation: [A-0], [A-1], [A-2]
    - Priority preferences: [GPT-I], [GPT-E], [GPT-F]
    - Follow-up: [F-X], [FL-X], [FM-X]
    
    Activation: Asterisk * at END of tag block indicates active tags
    """
    tags = {
        "stakeholder": None,
        "type": None,
        "priority": "non-critical",
        "status": None,
        "schedule": None,
        "coordination": [],
        "accommodation": None,
        "weekend": None,
        "priority_pref": None,
        "followup": None,
        "active": False
    }
    
    if not description:
        return tags
    
    # Check for activation asterisk
    if '*' in description:
        tags["active"] = True
    
    # Extract lead type (determines stakeholder + type + maybe priority)
    lead_match = re.search(r'\[LD-(INV|HIR|COM|NET|GEN)\]', description, re.IGNORECASE)
    if lead_match:
        lead_key = f"LD-{lead_match.group(1).upper()}"
        if lead_key in LEAD_TYPES:
            lead_info = LEAD_TYPES[lead_key]
            tags["stakeholder"] = lead_info.get("stakeholder")
            tags["type"] = lead_info.get("type")
            if lead_info.get("priority"):
                tags["priority"] = lead_info["priority"]
    
    # Extract timing (!! = critical)
    if re.search(r'\[!!\]', description):
        tags["priority"] = "critical"
        tags["schedule"] = "immediate"
    
    # Extract schedule timing
    if re.search(r'\[D5\]', description):
        tags["schedule"] = "within_5d"
    elif re.search(r'\[D5\+\]', description):
        tags["schedule"] = "5d_plus"
    elif re.search(r'\[D10\]', description):
        tags["schedule"] = "10d_plus"
    
    # Extract status
    if re.search(r'\[OFF\]', description):
        tags["status"] = "postponed"
    elif re.search(r'\[AWA\]', description):
        tags["status"] = "awaiting"
    elif re.search(r'\[TERM\]', description):
        tags["status"] = "inactive"
    
    # Extract coordination
    if re.search(r'\[LOG\]', description):
        tags["coordination"].append("logan")
    if re.search(r'\[ILS\]', description):
        tags["coordination"].append("ilse")
    
    # Extract accommodation
    acc_match = re.search(r'\[A-([012])\]', description)
    if acc_match:
        acc_level = acc_match.group(1)
        if acc_level == "0":
            tags["accommodation"] = "minimal"
        elif acc_level == "1":
            tags["accommodation"] = "baseline"
        elif acc_level == "2":
            tags["accommodation"] = "full"
    
    # Extract weekend
    if re.search(r'\[WEX\]', description):
        tags["weekend"] = "allowed"
    elif re.search(r'\[WEP\]', description):
        tags["weekend"] = "preferred"
    
    # Extract priority preferences
    if re.search(r'\[GPT-I\]', description):
        tags["priority_pref"] = "internal"
    elif re.search(r'\[GPT-E\]', description):
        tags["priority_pref"] = "external"
    elif re.search(r'\[GPT-F\]', description):
        tags["priority_pref"] = "founders"
    
    # Extract follow-up patterns (F-X, FL-X, FM-X where X is number)
    followup_match = re.search(r'\[(F|FL|FM)-(\d+)\]', description)
    if followup_match:
        followup_type = followup_match.group(1)
        followup_days = followup_match.group(2)
        tags["followup"] = {"type": followup_type, "days": int(followup_days)}
    
    return tags
```

### 3. Tag-Based BLUF Generation

**Location:** `file 'N5/scripts/meeting_prep_digest.py'` lines 289-318

```python
def generate_bluf(meeting: Dict[str, Any], research: List[Dict[str, Any]]) -> str:
    """Generate Bottom Line Up Front summary for meeting using V-OS tag context."""
    title = meeting.get('title', 'Meeting')
    attendee_names = [r['name'] for r in research]
    tags = meeting.get('tags', {})
    
    stakeholder = tags.get('stakeholder')
    meeting_type = tags.get('type')
    accommodation = tags.get('accommodation')
    
    # Stakeholder-specific BLUFs
    if stakeholder == 'investor':
        bluf = f"Investor meeting: {title.lower()} with {' & '.join(attendee_names)}"
    elif stakeholder == 'job_seeker':
        bluf = f"Hiring discussion: evaluate fit for {' & '.join(attendee_names)}"
    elif stakeholder == 'community':
        bluf = f"Community partnership: explore collaboration with {' & '.join(attendee_names)}"
    elif stakeholder == 'partner':
        bluf = f"Partnership discussion: {title.lower()} with {' & '.join(attendee_names)}"
    elif meeting_type == 'discovery':
        bluf = f"Discovery: understand needs and fit for {' & '.join(attendee_names)}"
    else:
        bluf = f"Connect with {' & '.join(attendee_names)} to {title.lower()}"
    
    # Add accommodation context
    if accommodation == 'full':
        bluf += " — Focus: understand their needs and constraints"
    elif accommodation == 'minimal':
        bluf += " — Focus: establish clear value and requirements"
    
    return bluf
```

### 4. Tag-Based Prep Actions

**Location:** `file 'N5/scripts/meeting_prep_digest.py'` lines 392-434

```python
# Prep actions (V-OS context-aware)
section += "**Prep actions:**\n"
action_num = 1

# Priority-based protection
if tags.get('priority') == 'critical':
    section += f"{action_num}. ⚠️ CRITICAL: Protect this time block — do not reschedule\n"
    action_num += 1

# Accommodation-based prep
if tags.get('accommodation') == 'full':
    section += f"{action_num}. Prepare 3+ options showing flexibility\n"
    action_num += 1
elif tags.get('accommodation') == 'minimal':
    section += f"{action_num}. Prepare 1-2 clear options with non-negotiables\n"
    action_num += 1
elif tags.get('type') == 'discovery':
    section += f"{action_num}. Prepare 3 questions to qualify fit\n"
    action_num += 1
elif tags.get('type') == 'partnership':
    section += f"{action_num}. Prepare partnership framework and value proposition\n"
    action_num += 1
else:
    section += f"{action_num}. Review last interaction and prepare 1-2 specific asks\n"
    action_num += 1

section += f"{action_num}. Set explicit outcome: what decision or next step do you need?\n"

# Coordination notes
if 'logan' in tags.get('coordination', []):
    section += "\n**Note:** Coordinate with Logan on scheduling and agenda\n"
if 'ilse' in tags.get('coordination', []):
    section += "\n**Note:** Coordinate with Ilse on scheduling and agenda\n"

# Weekend note
if tags.get('weekend') == 'preferred':
    section += "\n**Note:** ☀️ Weekend meeting — likely high engagement from their side\n"
elif tags.get('weekend') == 'allowed':
    section += "\n**Note:** Weekend availability confirmed\n"
```

### 5. Event Filtering with V-OS Status Tags

**Location:** `file 'N5/scripts/meeting_prep_digest.py'` lines 83-101

```python
def should_skip_event(meeting_title: str, description: str, tags: Dict[str, Any]) -> bool:
    """Check if event should be skipped (internal/buffer/postponed/inactive)."""
    title_lower = meeting_title.lower()
    
    # Skip deep work blocks
    if re.search(r'\[dw\]', title_lower, re.IGNORECASE):
        return True
    
    # Skip meeting buffers
    if 'buffer' in title_lower:
        return True
    
    # Skip postponed or inactive events (V-OS status tags)
    if tags.get('status') in ['postponed', 'inactive']:
        return True
    
    return False
```

---

## Integration with Howie

### How Howie Populates Tags

When Howie schedules a meeting via email, it automatically populates the Google Calendar event description with:

```
[Active V-OS tags from email thread]

Purpose: [Brief description from email context]

---
Please send anything you would like me to review in advance to vrijen@mycareerspan.com.

[Conferencing details]
[Rescheduling links]
```

**Example:**
```
[LD-INV] [D5+] *

Purpose: Discuss Series A funding timeline and requirements

---
Please send anything you would like me to review in advance to vrijen@mycareerspan.com.

Zoom: https://zoom.us/j/...
```

### Howie → Zo Communication

**Phase 2 (upcoming):** Howie will auto-forward all scheduled meetings to `va@zo.computer` with format:

```
Subject: [HOWIE→ZO] [NOTIFY] Meeting Scheduled: [Person] x Vrijen - [Date/Time]

Body:
- Person: [Name] ([Email])
- Date/Time: [ISO8601]
- V-OS Tags: [LD-INV] [D5+] *
- Context: [Brief from email thread]
```

This triggers immediate stakeholder research in N5.

---

## Tag Usage Examples

### Example 1: Investor Meeting (Critical Priority)

**Calendar Description:**
```
[LD-INV] [D5+] *

Purpose: Discuss Series A funding timeline

---
Please send pitch deck in advance to vrijen@mycareerspan.com.
```

**N5 Processing:**
- **Stakeholder:** investor
- **Type:** discovery
- **Priority:** critical (auto-set by [LD-INV])
- **Schedule:** 5d_plus
- **BLUF:** "Investor meeting: discuss series a funding timeline with [Name]"
- **Prep Action:** "⚠️ CRITICAL: Protect this time block — do not reschedule"

---

### Example 2: Hiring Discussion (Full Accommodation)

**Calendar Description:**
```
[LD-HIR] [A-2] [WEP] *

Purpose: Evaluate engineering candidate for senior role

---
Please send resume in advance to vrijen@mycareerspan.com.
```

**N5 Processing:**
- **Stakeholder:** job_seeker
- **Type:** discovery
- **Accommodation:** full
- **Weekend:** preferred
- **BLUF:** "Hiring discussion: evaluate fit for [Name] — Focus: understand their needs and constraints"
- **Prep Action:** "Prepare 3+ options showing flexibility"
- **Note:** "☀️ Weekend meeting — likely high engagement from their side"

---

### Example 3: Partnership Follow-up (Coordination Required)

**Calendar Description:**
```
[LD-NET] [LOG] [ILS] *

Purpose: Finalize pilot job descriptions and timeline

---
Please send job descriptions in advance to vrijen@mycareerspan.com.
```

**N5 Processing:**
- **Stakeholder:** partner
- **Type:** discovery
- **Coordination:** logan, ilse
- **BLUF:** "Partnership discussion: finalize pilot job descriptions and timeline with [Name]"
- **Note:** "Coordinate with Logan on scheduling and agenda"
- **Note:** "Coordinate with Ilse on scheduling and agenda"

---

### Example 4: Postponed Meeting (Skipped in Digest)

**Calendar Description:**
```
[LD-COM] [OFF]

Purpose: Community partnership discussion — postponed to next month
```

**N5 Processing:**
- **Status:** postponed
- **Action:** Skipped in daily meeting prep digest (not actionable)

---

## Configuration & Settings

### Where to Update V-OS Tags

**To add/remove/modify V-OS tags:**
1. Update constants in `file 'N5/scripts/meeting_prep_digest.py'` lines 41-62
2. Update extraction logic in `extract_vos_tags()` function (lines 103-217)
3. Update this documentation
4. Coordinate with Howie configuration (Phase 2)

### Testing V-OS Tag Extraction

```bash
# Run test suite
python3 /home/.z/workspaces/con_Qqg3HjE36MRpwyYi/test_vos_tags.py

# Test with dry-run
python3 /home/workspace/N5/scripts/meeting_prep_digest.py --dry-run
```

---

## Migration Notes

### Changes from v1.0.0 (Hashtag System)

| Old Format | New Format | Notes |
|------------|------------|-------|
| `#stakeholder:investor` | `[LD-INV]` | Auto-sets critical priority |
| `#stakeholder:job_seeker` | `[LD-HIR]` | Hiring/recruiting |
| `#stakeholder:community` | `[LD-COM]` | Partnership type |
| `#stakeholder:partner` | `[LD-NET]` | Business partner |
| `#type:discovery` | (implicit via LD tag) | Most LD tags → discovery |
| `#priority:high` | `[!!]` | Critical/urgent |
| `#priority:protect` | `[!!]` or `[LD-INV]` | Do not reschedule |

### Backward Compatibility

**Status:** Old hashtag format is DEPRECATED but still parsed for transition period.

To ensure smooth migration:
- Meeting prep digest recognizes BOTH formats during transition
- V-OS tags take precedence if both present
- Plan to remove hashtag support in v4.0.0 (Q1 2026)

---

## References

**Implementation Plan:** `file 'N5/docs/howie-zo-implementation-plan.md'`  
**Complete V-OS Tag Analysis:** `file 'N5/docs/howie-zo-harmonization-complete.md'`  
**User Guide:** `file 'N5/docs/calendar-tagging-system.md'`  
**Command Reference:** `file 'N5/commands/meeting-prep-digest.md'`

---

**Last Updated:** 2025-10-11  
**Version:** 2.0.0 (V-OS Integration)  
**Status:** Active — Phase 1 Complete
