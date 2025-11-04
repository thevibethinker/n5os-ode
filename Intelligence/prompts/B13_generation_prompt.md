# B13 - PLAN_OF_ACTION Generation Prompt

You are generating a PLAN_OF_ACTION intelligence block from a meeting transcript.

## Core Principle

Synthesize ALL blocks (B01, B02, B05, B07, B08, etc.) into a PRIORITIZED action plan. This is the "what do we actually DO now" summary.

## Output Structure

## Prioritized Next Steps

### 1. [Highest Priority Action]
**Why first**: [Strategic rationale for prioritization]  
**Blockers**: [Any dependencies or risks]  
**Owner**: [Who's accountable]  
**Timeline**: [When this needs to happen]

### 2. [Second Priority Action]
[Same format]

### 3. [Third Priority Action]
[Same format]

### 4-5. [Additional actions if needed]
[Up to 5 total - more than that indicates lack of prioritization]

## Prioritization Criteria

Rank actions by:
1. **Time sensitivity**: Hard deadlines first
2. **Deal criticality**: What moves the opportunity forward?
3. **Dependency chains**: What unblocks other actions?
4. **Relationship maintenance**: What keeps momentum?
5. **Quick wins**: What builds credibility fast?

## Extraction Sources

Pull from:
- **B02 (Commitments)**: What did we promise?
- **B05 (Questions)**: What's blocking progress?
- **B07 (Warm Intros)**: Which intros are time-sensitive?
- **B08 (Stakeholder Intel)**: What enrichment is needed?
- **B25 (Deliverables)**: What content needs creation?

## Quality Standards

✅ **DO:**
- Prioritize ruthlessly (if everything's urgent, nothing is)
- Explain WHY each action is positioned where it is
- Identify owner accountability
- Flag blockers that could derail timeline
- Group related micro-tasks into single action

❌ **DON'T:**
- List more than 5 actions (forces discipline)
- Put low-impact busywork ahead of deal-critical items
- Forget to assign ownership
- Ignore dependencies
- Miss time-sensitive commitments

## Edge Cases

**No clear next steps**: Output: "No immediate action items identified. This was an informational/exploratory conversation. Monitor for future follow-up signals."

**Too many actions**: Group into themes (e.g., "CRM Enrichment" encompasses 3 research tasks)

**Conflicting priorities**: Note trade-offs: "Prioritized X over Y because [reasoning]"
