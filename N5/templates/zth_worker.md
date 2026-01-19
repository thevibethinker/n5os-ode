---
created: {{created}}
last_edited: {{created}}
version: 1.0
provenance: {{provenance}}
type: zth_worker
zth_id: {{zth_id}}
task_type: {{task_type}}
execution_policy: {{execution_policy}}
meeting_id: {{meeting_id}}
meeting_folder: {{meeting_folder}}
status: pending
---

# ZTH Worker: {{task_title}}

## Original Cue

> "{{raw_cue}}"

**Timestamp:** {{timestamp}}

## Meeting Context

**Meeting:** {{meeting_title}}
**Folder:** `{{meeting_folder}}`

{{context}}

## Instruction

{{instruction}}

## Execution

{{#if is_blurb}}
Run: `file 'Prompts/Blurb-Generator.prompt.md'`
With meeting context from: `file '{{meeting_folder}}/B01_DETAILED_RECAP.md'`

**Voice Requirements:**
```bash
python3 N5/scripts/retrieve_voice_lessons.py --content-type linkedin_post --include-global
```
{{/if}}

{{#if is_follow_up_email}}
Run: `file 'Prompts/Follow-Up Email Generator.prompt.md'`
With meeting context from: `file '{{meeting_folder}}/B01_DETAILED_RECAP.md'`

**Voice Requirements:**
```bash
python3 N5/scripts/retrieve_voice_lessons.py --content-type follow_up --include-global
```

**Additional Context:**
- Recipient hint: {{recipient_hint}}
- Apply standard follow-up voice and formatting
{{/if}}

{{#if is_warm_intro}}
Run: `file 'Prompts/Meeting Warm Intro Generation.prompt.md'`
With meeting context from: `file '{{meeting_folder}}/B01_DETAILED_RECAP.md'`

**Voice Requirements:**
```bash
python3 N5/scripts/retrieve_voice_lessons.py --content-type intro --include-global
```

**Additional Context:**
- Target: {{recipient_hint}}
{{/if}}

{{#if is_research}}
**Research Request** (queued for manual execution)

Topic: {{instruction}}

Suggested approach:
1. Use `web_research` with appropriate category filters
2. Check existing `Knowledge/` for related content
3. Output findings to `{{meeting_folder}}/research/{{zth_id}}_findings.md`
{{/if}}

{{#if is_custom}}
**Custom Task** (queued for manual execution)

This task didn't match a known pattern. Review and execute manually.

Instruction: {{instruction}}
{{/if}}

## Output Location

Save output to: `{{meeting_folder}}/zth_outputs/{{zth_id}}_{{task_type}}.md`

## Status Log

- [ ] Worker generated: {{created}}
- [ ] Execution started: (pending)
- [ ] Execution completed: (pending)
- [ ] Output saved: (pending)
