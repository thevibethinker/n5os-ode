# B26 - MEETING_METADATA_SUMMARY Generation Prompt

You are generating a MEETING_METADATA_SUMMARY intelligence block.

## Core Principle

Provide quick-reference metadata for system operations, CRM classification, and email generation.

## Output Structure

**Title**: [Concise meeting title - Topic/Focus - Stakeholder Name]

**Email Subject Line**: [Subject for follow-up email - contextual and specific]

**Delay Sensitivity**: [SOFT/MEDIUM/URGENT] ([timeframe, reasoning])

**Stakeholder Type**: [Classification - see below]

**N5OS Tags**: `[TAG1] [TAG2] [TAG3]`

**Tag Rationale**:
- `[TAG1]`: [Why this tag applies]
- `[TAG2]`: [Why this tag applies]
- `[TAG3]`: [Why this tag applies]

**Priority**: [Critical/High/Medium/Low]

**Confidence Score**: [High/Medium/Low] ([reasoning])

**Transcript Quality**: [Excellent/Good/Fair/Poor] ([details])

**Meeting Date**: YYYY-MM-DD

**Duration**: [Approximate length]

## Stakeholder Type Classifications

### External Meeting Types:
- **PROSPECT**: Active sales opportunity
- **PARTNER**: Potential/existing business partnership
- **NETWORKING**: Knowledge-sharing, relationship-building
- **CUSTOMER**: Existing client/user
- **INVESTOR**: Funding-related conversations
- **ADVISOR**: Seeking/receiving strategic guidance
- **CANDIDATE**: Hiring/recruitment discussions

### Internal Meeting Types:
- **INTERNAL_STANDUP**: Team coordination
- **INTERNAL_STRATEGY**: Planning/decision-making
- **INTERNAL_RETROSPECTIVE**: Review/learning

## N5OS Tags System

**Lifecycle Tags**:
- `[LD-DSC]`: Discovery (first touch)
- `[LD-NET]`: Networking (relationship building)
- `[LD-EXP]`: Exploration (evaluating fit)
- `[LD-NEG]`: Negotiation (active deal discussions)
- `[LD-CLO]`: Closing (final stages)
- `[LD-ACT]`: Active (current customer/partner)

**GPT Tags** (Conversation Mode):
- `[GPT-P]`: Pitch mode
- `[GPT-D]`: Discovery mode
- `[GPT-E]`: Exploratory mode
- `[GPT-C]`: Consultative mode

**Attentiveness Tags** (Scheduling):
- `[A-1]`: VIP (immediate response, flexible scheduling)
- `[A-2]`: High Priority (respond within 24hrs)
- `[A-3]`: Standard (respond within 48-72hrs)
- `[A-4]`: Low Priority (can reschedule freely)

## Delay Sensitivity

**URGENT**: 
- Time: <24hrs
- Examples: Active deal, time-sensitive commitment, follow-up to problem

**MEDIUM**:
- Time: 24-72hrs
- Examples: Standard follow-up, promised deliverable, maintain momentum

**SOFT**:
- Time: 72hrs-1week
- Examples: Networking follow-up, exploratory conversation, no hard commitments

## Quality Standards

✅ **DO:**
- Choose MOST SPECIFIC stakeholder type
- Select tags that reflect ACTUAL conversation dynamics
- Provide reasoning for confidence/quality assessments
- Note any transcript issues that affect processing

❌ **DON'T:**
- Use generic tags that don't add signal
- Mismatch delay sensitivity with actual urgency
- Over-index priority (not everything is "High")
- Ignore transcript quality issues

## Example

**Title**: AI Development & Technical Exploration - Elaine P

**Email Subject Line**: Following Up: AI Learning Resources & Zo Platform

**Delay Sensitivity**: SOFT (24-72hr, networking conversation without hard commitments)

**Stakeholder Type**: NETWORKING

**N5OS Tags**: `[LD-NET] [GPT-E] [A-3]`

**Tag Rationale**:
- `[LD-NET]`: Knowledge-sharing conversation, relationship-building focus
- `[GPT-E]`: Exploratory mode - learning about each other's work
- `[A-3]`: Standard attentiveness - friendly but not business-critical

**Priority**: Medium

**Confidence Score**: High (clear transcript, straightforward conversation)

**Transcript Quality**: Excellent (clear audio, accurate timestamps)

**Meeting Date**: 2025-10-14

**Duration**: ~30 minutes
