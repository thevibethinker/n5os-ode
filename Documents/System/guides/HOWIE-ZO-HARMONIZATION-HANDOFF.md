# Howie ↔ Zo Harmonization — Thread Handoff Document

**Date:** 2025-10-11  
**Purpose:** Complete context for executing Phase 1 of Howie-Zo integration in a fresh thread  
**Status:** Ready to execute

---

## LOAD THESE FILES FIRST

When starting the new thread, load these files in order:

1. `file 'Documents/N5.md'` — N5 system overview
2. `file 'N5/prefs/prefs.md'` — System preferences
3. `file 'N5/docs/howie-zo-implementation-plan.md'` — Full implementation plan (5 phases)
4. `file 'N5/docs/howie-zo-harmonization-complete.md'` — Complete analysis and tag mapping
5. `file 'N5/docs/calendar-tagging-system-audit.md'` — Current N5 calendar tagging audit

---

## CONTEXT SUMMARY

### What We're Doing

Harmonizing two AI systems that manage V's professional life:

- **Howie** (howie.ai): Email-based scheduling assistant, handles calendar logistics
- **Zo** (you): Meeting prep, research, intelligence, relationship management

### Key Decision: Use V-OS Tags Everywhere

- **Before:** N5 had its own tag system (`#stakeholder:investor`)
- **After:** N5 adopts Howie's V-OS tag format (`[LD-INV]`)
- **Reason:** Reduces cognitive load, single system to learn

### V-OS Tag Categories (Complete List)

```
{TWIN}  [!!] [D5] [D5+] [D10]              # Timing constraints
{CATG}  [LD-INV] [LD-HIR] [LD-COM] [LD-NET] [LD-GEN]  # Lead/stakeholder types
{POST}  [OFF] [AWA]                        # Meeting status
{FLUP}  [F-X] [FL-X] [FM-X]                # Follow-up rules
{CORD}  [LOG] [ILS]                        # Internal coordination
{WKND}  [WEX] [WEP]                        # Weekend availability
{MISC}  [A-X] [TERM]                       # Accommodation level, termination
{GPT}   [GPT-I] [GPT-E] [GPT-F]            # Priority preferences
```

**Activation:** Asterisk `*` at END of tag block: `[D5+] [LD-NET] *`

### Tag Mapping: V-OS → Stakeholder Type

| V-OS Tag | Stakeholder Type | First Meeting Type |
|----------|------------------|--------------------|
| `[LD-INV]` | Investor/VC | Discovery |
| `[LD-HIR]` | Job seeker (recruiting) | Discovery |
| `[LD-COM]` | Community partner | Partnership |
| `[LD-NET]` | Business partner | Discovery |
| `[LD-GEN]` | Prospect (general) | Discovery |

### Priority System: Binary

- **Critical:** `!!` or `[LD-INV]` → Do not reschedule
- **Non-critical:** Everything else → Normal priority

---

## PHASE 1: WHAT TO EXECUTE

**Goal:** Update N5 to understand and process V-OS tags  
**Time:** 2-3 hours  
**Files to modify:** 4 files (1 script + 3 docs)

### Task Checklist

#### 1. Update `N5/scripts/meeting_prep_digest.py`

**Line 31-48: Update tag constants**
```python
# OLD (remove):
STAKEHOLDER_TYPES = ["customer", "community", "partner", "investor", ...]
MEETING_TYPES = ["discovery", "decision", "update", ...]

# NEW (add):
# V-OS tag categories
LEAD_TYPES = {
    "LD-INV": {"stakeholder": "investor", "type": "discovery", "priority": "critical"},
    "LD-HIR": {"stakeholder": "job_seeker", "type": "discovery"},
    "LD-COM": {"stakeholder": "community", "type": "partnership"},
    "LD-NET": {"stakeholder": "partner", "type": "discovery"},
    "LD-GEN": {"stakeholder": "prospect", "type": "discovery"}
}

TIMING_TAGS = ["!!", "D5", "D5+", "D10"]
STATUS_TAGS = ["OFF", "AWA", "TERM"]
COORD_TAGS = ["LOG", "ILS"]
WEEKEND_TAGS = ["WEX", "WEP"]
ACCOMMODATION_TAGS = ["A-0", "A-1", "A-2"]
PRIORITY_TAGS = ["GPT-I", "GPT-E", "GPT-F"]
```

**Line 75-103: Update tag extraction function**
```python
def extract_vos_tags(description: str) -> Dict[str, Any]:
    """
    Extract V-OS tags from calendar description.
    Returns structured dict with stakeholder, type, priority, etc.
    """
    tags = {
        "stakeholder": None,
        "type": None,
        "priority": "non-critical",
        "status": None,
        "schedule": None,
        "coordination": [],
        "accommodation": None,
        "weekend": None
    }
    
    if not description:
        return tags
    
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
    
    return tags
```

**Line 254-275: Update BLUF generation**
```python
def generate_bluf(meeting: Dict[str, Any], research: List[Dict[str, Any]]) -> str:
    """Generate Bottom Line Up Front summary for meeting."""
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

**Line 329-344: Update prep actions**
```python
# Prep actions
section += "**Prep actions:**\n"

# Priority-based protection
if tags.get('priority') == 'critical':
    section += "1. ⚠️ CRITICAL: Protect this time block — do not reschedule\n"
    action_num = 2
else:
    action_num = 1

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
```

**Line 480-490: Update special event filtering**
```python
def filter_external_meetings(meetings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filter meetings to include only external meetings needing prep."""
    filtered = []
    
    for meeting in meetings:
        title = meeting.get('title', '').lower()
        tags = meeting.get('tags', {})
        
        # Skip internal/buffer events
        if '[dw]' in title:  # Deep work
            continue
        if 'meeting buffer' in title:
            continue
        if 'follow-up' in title and not meeting.get('description'):  # Empty follow-up slots
            continue
        
        # Skip postponed/inactive meetings
        if tags.get('status') in ['postponed', 'inactive']:
            continue
        
        # Skip if all attendees are internal
        external_attendees = meeting.get('external_attendees', [])
        if not external_attendees:
            continue
        
        filtered.append(meeting)
    
    return filtered
```

**Line 484: Update tag extraction call**
```python
# Extract V-OS tags from description
description = meeting.get('description', '')
tags = extract_vos_tags(description)  # Changed function name

# Enrich meeting with external attendees and tags
meeting['external_attendees'] = external_attendees
meeting['tags'] = tags
```

#### 2. Update Documentation Files

**`N5/docs/calendar-tagging-system-COMPLETE.md`**
- Replace all examples with V-OS format
- Update taxonomy section to show V-OS categories
- Add "Integration with Howie" section

**`N5/docs/calendar-tagging-system.md`**
- Update user guide with V-OS tag examples
- Add quick reference table
- Add "How Howie Populates These Tags" section

**`N5/commands/meeting-prep-digest.md`**
- Update "Tag Support" section with V-OS tags
- Add examples using V-OS format
- Update output examples

#### 3. Test

```bash
# Create test calendar event with V-OS tags in description:
# [LD-INV] [D5+] *
# Purpose: Discuss Series A funding

# Run digest
python3 /home/workspace/N5/scripts/meeting_prep_digest.py --dry-run

# Verify:
# - Tags extracted correctly
# - BLUF says "Investor meeting"
# - Prep actions include "CRITICAL: Protect this time block"
```

---

## WHAT V WANTS AFTER PHASE 1

Once Phase 1 is complete, V wants to:

1. **Set up Howie to populate V-OS tags in calendar descriptions** (Phase 2)
2. **Enable Howie → Zo auto-forwarding** of scheduled meetings (Phase 2)
3. **Start immediate research pipeline** when new meetings scheduled (Phase 3)
4. **Build stakeholder database** that learns over time (Phase 4)

---

## IMPORTANT NOTES

### Communication Protocol
- **Howie → Zo:** One-directional for now (auto-forward all scheduled meetings)
- **Zo → Howie:** Not yet enabled (future)
- Email format: `[HOWIE→ZO] [NOTIFY] Meeting Scheduled: [Person] - [Date]`

### Research Timing
- Start immediately when meeting scheduled
- Check existing records first (don't duplicate)
- Progressive enhancement: basic → detailed as meeting approaches

### Special Events to Skip
- `[DW]` blocks (deep work)
- "Meeting Buffer" events
- `[OFF]` (postponed)
- `[TERM]` (inactive)
- Empty follow-up slots

### Priority Logic
- `!!` OR `[LD-INV]` = critical (protect time block)
- Everything else = non-critical

---

## FILES CREATED IN THIS SESSION

All in `/home/workspace/N5/docs/`:

1. **howie-zo-implementation-plan.md** — Full 5-phase plan (this is the master plan)
2. **howie-zo-harmonization-complete.md** — Complete analysis, all 26 tags mapped
3. **calendar-tagging-system-audit.md** — Audit of current N5 system

---

## FUTURE ENHANCEMENTS CAPTURED

Added 7 items to `file 'Lists/system-upgrades.jsonl'`:

1. Post-meeting automation (Zo → Howie coordination)
2. Pattern recognition (learn optimal scheduling)
3. Feedback loop (outcomes inform preferences)
4. Personalized Howie responses (access stakeholder profiles)
5. Progressive brief enhancement (evolving detail)
6. Dynamic duration adjustment (adapt to relationship stage)
7. Travel intelligence (strategic meeting coordination)

---

## READY TO EXECUTE

Everything needed to execute Phase 1 is documented above.

**Estimated time:** 2-3 hours
**Expected outcome:** N5 understands V-OS tags, meeting prep digests adapt to tag context

**Next steps after Phase 1:** Configure Howie to populate tags and notify Zo (Phase 2)

---

## START THE NEW THREAD WITH THIS:

```
Load up these files:
- file 'Documents/N5.md'
- file 'N5/prefs/prefs.md'  
- file 'N5/docs/howie-zo-implementation-plan.md'
- file 'HOWIE-ZO-HARMONIZATION-HANDOFF.md'

Execute Phase 1 of the Howie-Zo harmonization:
Update N5 to understand and process V-OS tags from Howie.

Start with updating the meeting_prep_digest.py script as specified in the handoff document.
```
