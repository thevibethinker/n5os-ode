# Meeting Processed: {{meeting_name}}

**Date:** {{meeting_date}}  
**Participants:** {{participants}}  
**Type:** {{meeting_type}}

---

## Quick Summary

{{quick_summary}}

---

## Action Items

{{action_items_count}} action items identified:

{{action_items_preview}}

[View full action items]({{review_first_link}})

---

## Recommended Deliverables

Based on the meeting content, I recommend generating:

{{#each recommended_deliverables}}
### {{@index}}. {{this.type_display}}
- **Why:** {{this.reason}}
- **Confidence:** {{this.confidence}}%
- **Time:** ~{{this.estimated_time}}

{{/each}}

---

## What Would You Like Me to Generate?

Reply to this email with:
- `all` - Generate all recommended deliverables
- `blurb` - Just the introduction blurb
- `blurb + email` - Blurb and follow-up email
- Or any combination you'd like

Alternatively, use the command:
```
N5: generate-deliverables "{{meeting_folder_name}}" --deliverables blurb,follow_up_email
```

---

## Review Meeting Intelligence

- [REVIEW_FIRST.md]({{review_first_link}}) - Executive summary
- [content-map.md]({{content_map_link}}) - What was extracted
- [RECOMMENDED_DELIVERABLES.md]({{recommendations_link}}) - Full recommendations

---

**Processing Time:** {{processing_time}} seconds  
**Confidence:** {{extraction_confidence}}%

_This is an automated notification from your N5 meeting processing system._
