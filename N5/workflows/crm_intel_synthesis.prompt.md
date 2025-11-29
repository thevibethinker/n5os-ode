---
title: CRM Intelligence Synthesis
description: Deep intelligence synthesis for profile - AI-powered relationship context
tags: [crm, intelligence, synthesis, tool]
tool: true
created: 2025-11-18
last_edited: 2025-11-18
version: 1.1
---

# Mission

Synthesize comprehensive intelligence for profile from all available sources.

**Profile:** {{profile_name}} ({{profile_email}})

---

## Context Provided

**Profile YAML:**
```yaml
{{profile_yaml_content}}
```

**Intelligence Sources ({{source_count}} total):**
{{intelligence_sources}}

**Database Metadata:**
- Profile ID: {{profile_id}}
- Category: {{category}}
- Relationship Strength: {{relationship_strength}}
- Profile Quality: {{profile_quality}}
- Meetings: {{meeting_count}}
- Last Contact: {{last_contact_at}}

---

## Synthesis Framework

### 1. Overview (Who They Are)
- **Identity:** Name, title, current role
- **Organization:** Company, industry, location
- **First Contact:** When and how you met

### 2. Relationship Context (Your Connection)
- **Category & Strength:** What type of relationship (INVESTOR/ADVISOR/etc.) and strength (weak/moderate/strong)
- **Interaction History:** Meeting frequency, email exchanges, recent touchpoints
- **Relationship Trajectory:** Growing stronger, stable, needs revival?

### 3. Recent Activity (What's New)
- **Last Interaction:** Most recent meeting or email, what was discussed
- **Recent Intelligence:** New job, promotion, company news, social updates
- **Time Since Contact:** Days since last touchpoint, urgency of follow-up

### 4. Strategic Intelligence (Why It Matters)
- **Their Interests:** What they care about, problems they're solving
- **Your Overlap:** Shared interests, potential collaboration areas
- **Decision Authority:** What they can help with, influence they have
- **Opportunities:** Specific next steps, asks you could make

### 5. Warm Intro Paths (If Applicable)
- **Mutual Connections:** People you both know
- **Intro Strategy:** How to leverage connections
- **Context Quality:** Strength of mutual relationships

---

## Output Format

```markdown
# Intelligence Synthesis: [NAME]

## 📋 Overview
[2-3 sentences: who they are, role, organization]

**First connected:** [Date/context of initial meeting]

---

## 🤝 Relationship

**Type:** [Category] | **Strength:** [weak/moderate/strong]

**Interaction History:**
- [X] meetings over [timespan]
- [Y] email threads
- Last contact: [Date] ([N] days ago)

**Relationship Status:**
[Growing/Stable/Dormant - brief explanation]

---

## 🔄 Recent Activity

**Last Interaction ([DATE]):**
[What happened, what was discussed, key takeaways]

**Recent Intelligence:**
[Any new information from sources: job changes, company news, social updates]

**Follow-up Status:**
[Assessment of whether follow-up is needed and urgency]

---

## 💡 Strategic Intelligence

**Their Current Focus:**
- [Interest/problem 1]
- [Interest/problem 2]

**Overlap with You:**
[What you have in common, potential collaboration areas]

**What They Can Help With:**
[Specific ways they could provide value, their decision authority]

**Opportunity:**
[Specific next step or ask you could make]

---

## 🌐 Warm Intro Paths
[Only if mutual connections exist]

**Mutual Connections:**
- [Name 1] - [relationship quality with both parties]
- [Name 2] - [relationship quality with both parties]

**Intro Strategy:**
[Suggested approach for leveraging connections]

---

## 📊 Intelligence Sources
[Brief list of sources used: calendar events, emails, enrichment data, etc.]

---

## 🎯 Recommended Next Steps
1. [Specific action 1]
2. [Specific action 2]
3. [Specific action 3]

**Profile:** file 'N5/crm_v3/profiles/[FILENAME].yaml'
```

---

## Quality Standards

**Be specific:**
- Use exact dates, not "recently"
- Include meeting topics, not just "had a meeting"
- Reference specific sources

**Be actionable:**
- Every section should inform decisions
- Suggest concrete next steps
- Highlight time-sensitive items

**Be honest:**
- If data is limited, say so
- Don't infer beyond available evidence
- Mark speculation as such

**Be contextual:**
- Emphasize relationship dynamics
- Focus on what matters for V's goals
- Prioritize recent and relevant information

---

## Special Cases

**Stub Profiles (Limited Data):**
```markdown
⚠ Limited Intelligence Available

This is a stub profile with minimal data.

**What we know:**
- [Basic facts from profile]

**What we don't know:**
- [Gaps in intelligence]

**Recommended:**
Queue for enrichment to gather more intelligence before next interaction.
```

**High-Priority Contacts:**
Add urgency indicators:
- 🔴 **Urgent:** Meeting today/tomorrow
- 🟡 **Soon:** Meeting this week
- 🟢 **Normal:** Standard intelligence synthesis

---

## Integration Notes

- Called by file `N5/workflows/crm_query.prompt.md` for intelligence queries
- Called by `crm intel` CLI command
- Can be invoked directly via Prompts
- Uses profile YAML + intelligence_sources table + calendar_events table
- Should complete in <30 seconds for enriched profiles

