---
created: 2026-01-19
last_edited: 2026-01-19
version: 1.1
provenance: con_PsffYknEXs0T7a81
description: Extract and classify "Zo Take Heed" verbal cues from meeting transcript
tags:
  - meeting-intelligence
  - block-generation
  - b00
  - zo-take-heed
  - zth
tool: true
---
# Generate Block B00: Zo Take Heed Extraction

**Input:** Meeting transcript provided in conversation context

**Purpose:** Extract verbal cues where V says "Zo take heed" followed by an instruction. These are deferred intents that either (a) influence downstream block generation, or (b) spawn discrete work tasks.

## ⛔ SPEAKER VALIDATION (CRITICAL)

**Only V can trigger Zo Take Heed.** If someone else on the call says the trigger phrase, IGNORE IT.

Valid speakers (case-insensitive):
- "V"
- "Vrijen"
- "Vrijen Attawar"
- Speaker labeled as host/organizer if V is hosting

**REJECT** if the speaker is:
- Any other named participant
- "Unknown"
- A guest/external party

When in doubt about speaker identity, check:
1. Is this speaker asking questions or presenting? (V typically leads)
2. Does the speaker's style match V's patterns?
3. Is the transcript speaker label consistent with V?

If the trigger phrase appears but speaker validation fails, log it but DO NOT process:
```json
{"id":"ZTH-REJECTED-001","reason":"speaker_validation_failed","speaker":"Jake Smith","raw_cue":"..."}
```

## Trigger Phrase Detection

Scan for these patterns (case-insensitive):
- "zo take heed"
- "zo, take heed"
- "zo takeheed"
- "zotakeheed"
- Phonetic variants: "zo take heed", "zoh take heed"

## Extraction Rules

For each detected trigger:

1. **Capture the instruction** — Everything after the trigger phrase until:
   - Another speaker starts talking
   - A clear topic shift occurs
   - Another ZTH trigger appears
   - Natural sentence boundary (if V continues on different topic)

2. **Extract timestamp** — Use transcript timestamps or approximate position (e.g., "early", "mid", "late" if no timestamps)

3. **Classify task type** using these rules:

| Task Type | Trigger Keywords | Execution Policy |
|-----------|------------------|------------------|
| `directive` | omit, emphasize, highlight, don't mention, skip, focus on, make sure to, remember that | `inline` (influences blocks) |
| `blurb` | blurb, linkedin post, social post | `auto_execute` |
| `follow_up_email` | follow-up, follow up, send email, email them, prep email | `auto_execute` |
| `warm_intro` | intro to, introduce me, warm intro, connect me with | `auto_execute` |
| `research` | research, look into, find out, investigate, dig into | `queue` |
| `list_add` | add to list, add this to, put on the list, add to [list-name] | `auto_execute` |
| `deal_add` | add as a deal, add deal, new deal, track this deal, add to pipeline | `auto_execute` |
| `deal_update` | update deal, deal note, deal status | `auto_execute` |
| `crm_contact` | add as contact, add to CRM, add as broker, add as lead, potential [role] | `auto_execute` |
| `intro_lead` | can intro me to, can connect me to, knows someone at, has a contact at | `auto_execute` |
| `custom` | (anything else) | `queue` |

4. **Determine scope** — What outputs should this affect?
   - Directives: `["B01", "B14"]` or specific blocks mentioned
   - Spawn triggers: The specific output type

## Additional Parameters by Task Type

**`list_add`:**
```json
{
  "additional_params": {
    "list_name": "startup-ideas",  // or "ideas", "must-contact", "exploration-and-growth"
    "item_summary": "AI-powered meeting assistant for sales teams"
  }
}
```
Lists are stored in `N5/lists/`. Common lists: `ideas.jsonl`, `must-contact.jsonl`, `exploration-and-growth.jsonl`

**`deal_add`:**
```json
{
  "additional_params": {
    "company": "Handshake",
    "pipeline": "careerspan",  // or "zo"
    "initial_note": "Intro via Jake on partnership call",
    "temperature": "warm"
  }
}
```
Deals sync via `N5/scripts/sms_deal_handler.py` and Notion.

**`deal_update`:**
```json
{
  "additional_params": {
    "company": "Acme Corp",
    "update_note": "Ready to proceed with pilot"
  }
}
```

**`crm_contact`:**
```json
{
  "additional_params": {
    "person_name": "Sarah Chen",
    "role": "broker",  // or "lead", "investor", "advisor"
    "company": "Handshake",
    "context": "Mentioned by Jake as potential partner contact"
  }
}
```

**`intro_lead`:**
```json
{
  "additional_params": {
    "source_person": "Jake Smith",  // Who can make the intro
    "target_person": "Lisa Wong",   // Who V wants to meet
    "target_company": "Handshake",
    "target_role": "VP Partnerships",
    "context": "Jake mentioned he knows Lisa from previous company"
  }
}
```

## Output Format

Generate a JSONL file with one JSON object per line. Each object:

```json
{
  "id": "ZTH-001",
  "timestamp": "00:14:32",
  "raw_cue": "Zo take heed, prep a follow-up email emphasizing our integration capabilities",
  "instruction": "prep a follow-up email emphasizing our integration capabilities",
  "task_type": "follow_up_email",
  "execution_policy": "auto_execute",
  "scope": ["follow_up_email"],
  "context": "Discussion about API integration with prospect",
  "additional_params": {}
}
```

**Field definitions:**
- `id`: Sequential identifier ZTH-001, ZTH-002, etc.
- `timestamp`: Transcript timestamp or position indicator
- `raw_cue`: Exact text including trigger phrase
- `instruction`: Cleaned instruction without trigger phrase
- `task_type`: One of: directive, blurb, follow_up_email, warm_intro, research, custom
- `execution_policy`: One of: inline, auto_execute, queue
- `scope`: Array of affected outputs
- `context`: Brief context from surrounding transcript (1-2 sentences)
- `additional_params`: Task-specific parameters (e.g., recipient for warm_intro)

## Special Cases

**Multiple ZTH in sequence:**
```
V: "Zo take heed, omit the pricing discussion. Zo take heed, prep a follow-up email."
```
→ Generate two separate entries (ZTH-001, ZTH-002)

**Ambiguous task type:**
If the instruction doesn't clearly match any category, default to `custom` with `queue` policy.

**No ZTH detected:**
Generate an empty JSONL file (0 bytes) or a single comment line:
```
# No Zo Take Heed cues detected in this transcript
```

## Quality Checks

Before outputting, verify:
- [ ] All detected ZTH phrases are captured
- [ ] Task types are correctly classified
- [ ] Instructions are complete (not cut off mid-sentence)
- [ ] IDs are sequential
- [ ] JSON is valid (parseable)

## Example Output (Extended)

For a transcript containing:
> V: "...Zo take heed, omit the specific pricing numbers from the recap..."
> Jake: "Zo take heed, send me a summary." (IGNORED - wrong speaker)
> V: "...Zo take heed, add Handshake as a deal, Jake here can intro me to their partnerships team..."
> V: "...Zo take heed, Jake mentioned he can connect me to Lisa Wong who runs partnerships at Handshake, track that intro lead..."
> V: "...Zo take heed, add this business model to the startup ideas list..."

Output `B00_ZO_TAKE_HEED.jsonl`:
```json
{"id":"ZTH-001","timestamp":"mid","speaker":"V","raw_cue":"Zo take heed, omit the specific pricing numbers from the recap","instruction":"omit the specific pricing numbers from the recap","task_type":"directive","execution_policy":"inline","scope":["B01","B14"],"context":"Pricing discussion","additional_params":{}}
{"id":"ZTH-REJECTED-001","reason":"speaker_validation_failed","speaker":"Jake","raw_cue":"Zo take heed, send me a summary"}
{"id":"ZTH-002","timestamp":"mid","speaker":"V","raw_cue":"Zo take heed, add Handshake as a deal, Jake here can intro me to their partnerships team","instruction":"add Handshake as a deal","task_type":"deal_add","execution_policy":"auto_execute","scope":["deal"],"context":"Partnership discussion with Jake","additional_params":{"company":"Handshake","pipeline":"careerspan","initial_note":"Jake can intro to partnerships team"}}
{"id":"ZTH-003","timestamp":"mid","speaker":"V","raw_cue":"Zo take heed, Jake mentioned he can connect me to Lisa Wong who runs partnerships at Handshake, track that intro lead","instruction":"track intro lead to Lisa Wong at Handshake via Jake","task_type":"intro_lead","execution_policy":"auto_execute","scope":["crm","warm_intro"],"context":"Jake offering intro","additional_params":{"source_person":"Jake Smith","target_person":"Lisa Wong","target_company":"Handshake","target_role":"partnerships"}}
{"id":"ZTH-004","timestamp":"late","speaker":"V","raw_cue":"Zo take heed, add this business model to the startup ideas list","instruction":"add business model to startup ideas list","task_type":"list_add","execution_policy":"auto_execute","scope":["list"],"context":"Business model discussion","additional_params":{"list_name":"ideas","item_summary":"[extract from context]"}}
```

---

**Generate the B00 block now using the transcript provided in this conversation.**
