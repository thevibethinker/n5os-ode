---
created: 2026-02-17
last_edited: 2026-02-18
version: 2.1
provenance: con_D22Ewo8OGuQrMBrx
spawn_mode: manual
status: pending
---
# D3: Use Case Research + Competitive Landscape

## Context from Prior Drops

**D5 (Zo Docs) delivered:**
- 93-entry knowledge index: `Knowledge/zo-hotline/00-knowledge-index.md` — this is what Zoseph currently knows. Your gap analysis should diff against this.
- 41 platform docs in `Knowledge/zo-hotline/96-zo-platform/` — current Zo features already documented.
- 6 conversational playbook files in `Knowledge/zo-hotline/97-conversational-playbook/` — includes Explorer, Challenger, Builder pathways. Your messaging/competitive work feeds the Challenger pathway directly.
- Thematic analysis from 8 real calls: `Research/zo-hotline/hotline-thematic-analysis.md` — proven phrases and what resonated already documented here.

**D1 (Infrastructure) delivered:**
- Trimmed system prompt (901 words): `Skills/zo-hotline/prompts/zoseph-system-prompt.md`
- Tool usage logging at `Datasets/zo-hotline-calls/tool_usage.jsonl` — this is where messaging effectiveness data will accumulate. Your messaging cheat sheet sets the baseline that gets measured here.
- Call spotlights table in DuckDB — flags notable calls for the daily digest.

**Don't duplicate what exists.** Build on the knowledge index, fill its gaps, and produce competitive/messaging artifacts that D4 can wire into the system prompt and playbook.

## Objective
Discover what real Zo users are building AND map the competitive landscape so Zoseph can speak credibly about both.

## Scope

### 1. Community Use Case Scan
- Zo Discord: showcases, help threads, creative uses, "look what I built" posts
- r/ZoComputer (if exists) or relevant subreddits for user stories
- X/Twitter: @zocomputer mentions, community posts, user showcases
- Zo blog/changelog: recent features, use case spotlights
- Target: 10+ real-world use cases documented

### 2. Competitive Landscape
- **Claude Projects / Claude Pro**: What can persistent Projects do? Limitations vs Zo?
- **OpenAI GPTs + Actions**: Custom GPTs, scheduled capabilities, integration depth
- **Cursor / Windsurf / coding agents**: How they position, what they can't do that Zo can
- **Zapier AI / Make.com AI**: Automation-first competitors, where Zo's integration model differs
- **Notion AI / Airtable AI**: Workspace-embedded AI, limitations vs full compute environment
- For each: what they do well, where they fall short, honest Zo advantage

### 3. Messaging Effectiveness Baseline
- What differentiation language exists in Zo's marketing?
- What language do competitors use?
- What resonated in the 8 thematic analysis calls? (already documented)
- Produce: "Messaging That Works" cheat sheet for D4 to wire into the system prompt
- Include: honest concessions ("Claude is great for X") + pivots ("but for Y, Zo is the only option")

### 4. Idealism / Open Source Angle
- What open-source positioning does Zo have?
- What does the Zo Substrate / Skill Exchange vision look like?
- How does this compare to competitors' closed ecosystems?
- Produce: talking points for the Challenger pathway's idealism vector

## Deliverables
- Use case synthesis document (10+ cases, each with: description, which Zo features used, complexity level, profession/role)
- Competitive landscape table (feature-by-feature, honest)
- Messaging cheat sheet (what works, what doesn't, honest concessions + pivots)
- Idealism/open-source talking points
- Gap analysis: what callers ask about vs. what Zoseph currently knows
- All stored in `Knowledge/zo-hotline/` or build deposits

## Acceptance Criteria
- [ ] Minimum 10 real-world use cases documented from community sources
- [ ] Competitive landscape covers top 5 competitors with honest assessment
- [ ] Messaging cheat sheet produced with proven phrases + new recommendations
- [ ] Idealism angle documented with specific talking points
- [ ] All deliverables in voice-friendly format (short paragraphs, no jargon)
