#!/usr/bin/env python3
"""
Deal LLM Prompts — Centralized prompt templates for deal intelligence
Part of Worker 1: Signal Router Core
"""

# =============================================================================
# DEAL MATCHING PROMPT
# =============================================================================

DEAL_MATCH_PROMPT = """You are matching a user query to a deal in our CRM.

Query: "{query}"
Context hint: "{context}"

## Available Deals:
{deal_list}

## Available Contacts:
{contact_list}

## Instructions:
1. Find the best match considering:
   - Exact matches on company name
   - Partial name matches (e.g., "darwin" → "Darwinbox")
   - Contact name matches (person associated with deal)
   - Common abbreviations or nicknames
   - Typo tolerance (e.g., "darwnibox" → "Darwinbox")

2. If query matches a contact, find their associated deal

3. If query could match both zo and careerspan pipelines, prefer the one in context hint

4. Return confidence 0-100:
   - 95-100: Exact match
   - 80-94: Clear partial match or contact match
   - 60-79: Fuzzy match, likely correct
   - Below 60: Uncertain, may need clarification

Return ONLY valid JSON:
{{
  "deal_id": "matched deal id or null",
  "contact_id": "matched contact id or null",
  "confidence": 0-100,
  "match_reason": "brief explanation of why this matched"
}}"""


# =============================================================================
# SIGNAL EXTRACTION PROMPT
# =============================================================================

SIGNAL_EXTRACTION_PROMPT = """Extract deal intelligence from this update.

## Update text:
"{text}"

## Current deal state:
- Company: {company}
- Pipeline: {pipeline}
- Current stage: {stage}
- Last touched: {last_touch}
- Temperature: {temperature}

## Stage definitions (in progression order):
- identified: Target recognized, not yet researched
- researched: Intel gathered, warm intro path identified
- outreach: First touch sent (email, call, intro request)
- engaged: Response received, conversation is open
- qualified: Confirmed mutual interest + fit
- negotiating: Terms, pricing, or deal structure being discussed
- closed_won: Deal completed successfully
- closed_lost: Deal dead, declined, or passed

## Stage inference rules:
- "sent first email/message" → outreach
- "they responded/replied" → engaged
- "confirmed interest" or "want to move forward" → qualified
- "discussing terms/pricing/structure" → negotiating
- "deal signed/closed/won" → closed_won
- "they passed/declined/not interested" → closed_lost

## Extract:
1. Whether this signals a stage change
2. Key facts worth recording
3. Next action if mentioned
4. Overall sentiment and urgency

Return ONLY valid JSON:
{{
  "stage_signal": "none|positive|negative|stage_change",
  "inferred_stage": "stage_name or null if no change",
  "stage_change_reason": "why stage should change, or null",
  "key_facts": ["fact1", "fact2"],
  "next_action": "specific next action or null",
  "next_action_date": "YYYY-MM-DD or null",
  "sentiment": "positive|neutral|negative",
  "urgency": "low|medium|high"
}}"""


# =============================================================================
# NEW DEAL DETECTION PROMPT
# =============================================================================

NEW_DEAL_DETECTION_PROMPT = """Analyze this content for potential new deal signals.

## Content:
"{content}"

## Source: {source}

## Context:
This is from V's {source}. Look for signals that indicate:
- A new potential acquisition target (Careerspan pipeline)
- A new potential distribution partner (Zo pipeline)
- A new broker/intermediary relationship
- A new leadership contact to track

## Questions to answer:
1. Is there a new company/entity being discussed as a potential deal?
2. What type of deal is it? (acquisition, partnership, broker relationship)
3. How strong is the signal? (explicit vs. implied)
4. What action is appropriate?

Return ONLY valid JSON:
{{
  "has_new_deal_signal": true|false,
  "signal_strength": "strong|medium|weak",
  "deal_type": "acquisition|partnership|broker|leadership|null",
  "suggested_pipeline": "careerspan|zo|null",
  "company_name": "extracted company name or null",
  "contact_name": "extracted person name or null",
  "summary": "brief summary of the signal",
  "recommended_action": "create_deal|track_contact|follow_up|ignore"
}}"""


# =============================================================================
# INTELLIGENCE SUMMARY FORMAT PROMPT
# =============================================================================

INTEL_SUMMARY_FORMAT_PROMPT = """Format this deal intelligence as a summary entry.

## Raw intel:
{intel_json}

## Source: {source}
## Date: {date}

Format as a markdown summary block suitable for appending to an intelligence log:

---
## [{date}] {source_title}

**Stage:** {stage_transition}
**Signal:** {signal_summary}
**Key Intel:**
{key_facts_bullets}

**Next:** {next_action}

---"""


# =============================================================================
# SMS PARSE PROMPT
# =============================================================================

SMS_DEAL_PARSE_PROMPT = """Parse this SMS deal update command.

## SMS text:
"{sms_text}"

## Expected format:
n5 deal <deal_name> <update>

## Examples:
- "n5 deal darwinbox They're ready to move forward, setting up call next week"
- "n5 deal ribbon Christine confirmed budget, need to send proposal"
- "n5 deal aviato Hot lead - founder wants to integrate ASAP"

## Extract:
1. The deal query (what to match against)
2. The update text
3. Any implicit context (pipeline hints, urgency signals)

Return ONLY valid JSON:
{{
  "is_valid_command": true|false,
  "deal_query": "the deal name/query to match",
  "update_text": "the update content",
  "pipeline_hint": "careerspan|zo|null if unclear",
  "parse_error": "error message if invalid, null otherwise"
}}"""
