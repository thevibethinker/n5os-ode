---
description: Process internal team meeting transcripts into strategically structured
tool: true
  intelligence blocks (B40-B48) following MECEM principles (Mutually Exclusive, Collectively
  Exhaustive, Minimally Repeating).
tags: []
---
# `internal-meeting-process`

**Version**: 1.0.0  
**Category**: Meeting Intelligence  
**Workflow**: Internal Meeting Processing  
**Architecture**: MECEM Framework  
**Created**: 2025-10-13

---

## Purpose

Process internal team meeting transcripts into strategically structured intelligence blocks (B40-B48) following MECEM principles (Mutually Exclusive, Collectively Exhaustive, Minimally Repeating).

---

## Meeting Types

### INTERNAL_STANDUP_COFOUNDER
- Co-founder sync meetings (Vrijen + Logan, or Vrijen + Ilse, or all three)
- Detected when: All participants are co-founders (2-3 people)
- Duration: Typically 15-60 minutes
- Blocks: B26, B40, B41, B47, + conditional B42-B46, B48

### INTERNAL_STANDUP_TEAM
- Team all-hands or standup meetings
- Detected when: 4+ internal participants
- Duration: Typically 15-90 minutes
- Blocks: B26, B40, B41, B47, + conditional B42-B46, B48

### INTERNAL_STRATEGIC
- Strategic planning, retrospectives, deep dives, workshops
- Detected when: #N5OS tag + strategic keywords OR explicit keywords (planning, strategy, retrospective, quarterly, OKR, roadmap, strategic, vision, deep dive, workshop)
- Duration: Typically 60-240 minutes
- Blocks: B26, B40, B41, B47, + conditional B42-B46, B48 (B48 very likely)

---

## Block Structure (B40-B48)

### Always Generated
- **B26**: Meeting Metadata Summary
- **B40**: Internal Decisions (strategic + tactical + interrelationships)
- **B41**: Team Coordination (action items with decision context)
- **B47**: Open Debates (unresolved strategic questions)

### Conditionally Generated
- **B42**: Market/Competitive Intel (if market/competitive topics discussed)
- **B43**: Product Intelligence (if product/roadmap discussed)
- **B44**: GTM/Sales Intel (if GTM/sales topics discussed)
- **B45**: Operations/Process (if ops/process topics discussed)
- **B46**: Hiring/Team (if hiring/team topics discussed)
- **B48**: Strategic Memo (if ≥30min AND significant strategic decisions)

---

## MECEM Principles

**Mutually Exclusive**: Each piece of information belongs in exactly ONE canonical location
- Strategic decisions → B40 only
- Action items → B41 (references B40 for context)
- Market intelligence → B42 (not in B40)

**Collectively Exhaustive**: All relevant information captured somewhere
- Strategic + tactical decisions → B40
- Unresolved items → B47
- Execution → B41
- Domain intelligence → B42-B46

**Minimally Repeating**: Information stored once, referenced everywhere
- Use cross-references: [B40.D3], [B41.A5], [B47.Q2]
- Action items reference B40 for WHY (don't duplicate strategic rationale)
- B48 synthesizes (exception for executive readability)

---

## Cross-Reference Format

```markdown
[B40.D3]  → Decision 3 in B40 (current meeting)
[B40.T5]  → Tactical decision 5 in B40
[B41.A7]  → Action 7 in B41
[B47.Q2]  → Open question 2 in B47
[2025-08-27_internal-team/B40.D2]  → Decision from past meeting
```

---

## Usage

### Step 1: Classify Meeting

```bash
cd /home/workspace/N5/scripts/utils
python3 stakeholder_classifier.py --event "#N5OS Co-founder planning" vrijen@mycareerspan.com logan@theapply.ai
```

Output will show meeting classification (e.g., INTERNAL_STANDUP_COFOUNDER)

### Step 2: Generate Blocks

```bash
cd /home/workspace/N5/scripts
python3 generate_internal_blocks.py \
  --transcript /path/to/transcript.txt \
  --output-dir /home/workspace/N5/records/meetings/YYYY-MM-DD_internal-meeting \
  --meeting-type INTERNAL_STANDUP_COFOUNDER \
  --duration 45
```

This will:
1. Load block definitions and registry
2. Analyze transcript for conditional blocks
3. Generate prompt files for each block (_PROMPT_B##.md)
4. You then process each prompt with Zo to generate final block content

### Step 3: Process Prompts with Zo

For each `_PROMPT_B##.md` file in the output directory:
1. Open the prompt file
2. Zo will generate the block content
3. Save to the corresponding B##_BLOCKNAME.md file

---

## Block Descriptions

### B40 - INTERNAL_DECISIONS ✅ ALWAYS
**Purpose**: Canonical location for ALL strategic and tactical decisions with interrelationships

**Structure**:
- Strategic Decisions (table: ID | Decision | Type | Rationale | Related Tactical)
- Tactical Decisions (table: ID | Decision | Type | Rationale | Supports Strategic)
- Holistic Pushes (strategic initiatives with tactical execution path)
- Resolved Tactical Debates (if any occurred)

**Decision Types**: Product, Go-to-Market, Operations, Hiring, Investment, Partnerships

**Key Principle**: Captures the "holistic push" - both the strategic WHY and the tactical HOW

### B41 - TEAM_COORDINATION ✅ ALWAYS
**Purpose**: Action items with owners, deadlines, and decision context via references

**Structure**: Table with Owner | Action | Context [B40 ref] | Due Date | Dependencies | Status

**Key Principle**: References B40 for context (doesn't duplicate WHY)

### B42 - MARKET_COMPETITIVE_INTEL ⚙️ CONDITIONAL
**Purpose**: Market trends, competitive landscape, customer insights from internal discussion

**Sections**:
- Market Trends
- Competitive Intelligence  
- Customer Insights
- Positioning Implications

**Generate when**: Market/competitive analysis discussed

### B43 - PRODUCT_INTELLIGENCE ⚙️ CONDITIONAL
**Purpose**: Product strategy, roadmap, architecture, technical decisions

**Sections**:
- Product Strategy
- Roadmap Updates
- Feature Decisions (links to B40)
- Technical Approach
- User Experience

**Generate when**: Product/roadmap/engineering discussed

### B44 - GTM_SALES_INTEL ⚙️ CONDITIONAL
**Purpose**: Go-to-market strategy, sales process, pricing, distribution (separate from product)

**Sections**:
- GTM Strategy
- Sales Process
- Pricing & Packaging (links to B40)
- Distribution
- Messaging & Positioning

**Generate when**: GTM/sales/pricing discussed

### B45 - OPERATIONS_PROCESS ⚙️ CONDITIONAL
**Purpose**: Operational processes, tools, workflows, organizational decisions

**Sections**:
- Process Changes (links to B40)
- Tool Decisions
- Team Structure
- Efficiency Improvements

**Generate when**: Process/tools/org structure discussed

### B46 - HIRING_TEAM ⚙️ CONDITIONAL
**Purpose**: Hiring decisions, role definitions, team expansion

**Sections**:
- Hiring Decisions (links to B40)
- Role Definitions
- Compensation Strategy
- Pipeline Status

**Generate when**: Hiring/recruiting discussed

### B47 - OPEN_DEBATES ✅ ALWAYS
**Purpose**: Unresolved strategic questions and debates requiring future resolution

**Structure**: Table with Q# | Question | Type | Context | Perspectives | Next Steps

**Key Rules**:
- Resolved tactical disagreements go to B40, NOT here
- Only unresolved strategic uncertainty
- Link to B40 if related to existing decisions

### B48 - STRATEGIC_MEMO ⚙️ CONDITIONAL
**Purpose**: Executive synthesis of major internal meetings (ONLY exception to MECEM for readability)

**Sections**:
- Executive Summary
- Key Strategic Decisions (from B40)
- Major Initiatives (holistic pushes from B40)
- Intelligence Highlights (from B42-B46)
- Open Strategic Questions (from B47)
- Next Steps (from B41)
- Strategic Implications

**Generate when**: Meeting ≥30min AND significant strategic decisions

**Style**: Executive narrative, 500-1000 words, written for "Future V reading this 3 months later"

---

## Blocks NOT Generated for Internal Meetings

These external-only blocks are never generated:
- B01-B31: External stakeholder blocks (DETAILED_RECAP, STAKEHOLDER_INTELLIGENCE, etc.)

---

## Quality Checks

Before finalizing, verify:

1. ✅ B40 captures ALL decisions (strategic + tactical + interrelationships)
2. ✅ B41 uses cross-references to B40 (no context duplication)
3. ✅ B47 only has UNRESOLVED items (resolved debates go to B40)
4. ✅ Cross-references use correct format [B##.ID#]
5. ✅ Conditional blocks only generated when relevant
6. ✅ B48 synthesizes across blocks (if generated)
7. ✅ No overlap between B42-B46 (mutually exclusive domains)
8. ✅ Holistic pushes captured in B40 (strategy + execution path)

---

## Examples

### Example B40 Entry (Strategic Decision with Tactical Execution)

```markdown
## Strategic Decisions

| ID | Decision | Type | Rationale | Related Tactical |
|----|----------|------|-----------|------------------|
| D3 | Prioritize embedded widgets over standalone platform | Product | Better distribution strategy, lower integration friction for partners like FutureFit | T7, T8, T9 |

## Tactical Decisions

| ID | Decision | Type | Rationale | Supports Strategic |
|----|----------|------|-----------|-------------------|
| T7 | Build vibe-check widget first | Product | Smallest useful increment, can demo to partners quickly | D3 |
| T8 | Use iframe embedding approach | Product | Easier for partners to integrate, sandboxed execution | D3 |
| T9 | Launch partner preview in 3 weeks | Product | Fast feedback loop before full build | D3 |

## Holistic Pushes

**Initiative**: Embedded Widget Strategy  
**Strategic Rationale**: [D3] Shift from platform to data layer, better partner distribution  
**Tactical Execution**: [T7] Build vibe-check widget → [T8] iframe approach → [T9] Partner preview  
**Dependencies**: Need partner agreements ([B41.A2]), design mockups ([B41.A5])  
**Success Criteria**: 2+ partners integrated within 8 weeks, positive user feedback
```

### Example B41 Entry (Action with Decision Context)

```markdown
| Owner | Action | Context | Due Date | Dependencies | Status |
|-------|--------|---------|----------|--------------|--------|
| Ilse | Build vibe-check widget prototype | [B40.T7] Embedded widget strategy | 2025-10-20 | Design mockups | In Progress |
| Logan | Reach out to FutureFit for widget partnership | [B40.D3] Need launch partner for embedded approach | 2025-10-15 | None | Not Started |
```

---

## Architectural Principles Reference

See `file 'N5/prefs/architectural_principles.md'` for complete MECEM framework documentation.

---

## Version History

- **v1.0.0** (2025-10-13): Initial internal meeting processing command
  - B40-B48 block structure defined
  - MECEM principles integrated
  - Three internal meeting types supported
  - Conditional block generation logic
  - Cross-reference framework established

---

**Transform internal meetings into strategic accountability and institutional memory.**
