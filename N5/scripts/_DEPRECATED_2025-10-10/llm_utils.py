#!/usr/bin/env python3
"""
Utility functions for interacting with the internal LLM.
This module centralizes LLM call simulation for consistency across generators and orchestrator.

FIXED VERSION - Properly extracts parameters from transcripts instead of using hardcoded stubs.
"""

import logging
from typing import Any, Dict, Optional, List
import asyncio
import json
import re

logger = logging.getLogger(__name__)

# === PARTICIPANT EXTRACTION ===

def extract_participants_from_transcript(transcript_content: str) -> List[str]:
    """
    Extract participant names from transcript.
    Supports multiple formats:
    1. Granola format (Meeting Title: + Attendee Emails:)
    2. Timestamp format (00:03\nName\nDialogue)
    """
    participants = set()
    
    # Check for Granola format first
    if "Meeting Title:" in transcript_content and "Attendee Emails:" in transcript_content:
        logger.info("Detected Granola transcript format")
        
        # Extract from Meeting Title
        title_match = re.search(r'Meeting Title:\s*(.+?)(?:\n|$)', transcript_content)
        if title_match:
            title = title_match.group(1).strip()
            # Extract names from title (format: "Name1 and Name2 + Name3")
            # Clean up escape characters
            title = title.replace('\\+', '+').replace('\\', '')
            # Split by "and" or "+"
            name_parts = re.split(r'\s+(?:and|\+)\s+', title)
            for name in name_parts:
                name = name.strip()
                if len(name) > 3 and not any(word in name.lower() for word in ['meeting', 'call', 'sync']):
                    participants.add(name)
        
        # Extract from Attendee Emails to get additional context
        emails_match = re.search(r'Attendee Emails:\s*(.+?)(?:\n|$)', transcript_content)
        if emails_match:
            emails = emails_match.group(1).strip()
            # Extract names from email addresses (before @)
            email_list = [e.strip() for e in emails.split(',')]
            logger.info(f"Found {len(email_list)} attendee emails")
        
        # Extract Creator Email
        creator_match = re.search(r'Creator Email:\s*(.+?)(?:\n|$)', transcript_content)
        if creator_match:
            creator_email = creator_match.group(1).strip()
            logger.info(f"Creator email: {creator_email}")
    
    # Fallback: Try timestamp format
    if not participants:
        # Pattern: timestamp followed by name followed by dialogue
        # Matches: "00:03\nVrijen Attawar\nHey..."
        pattern = r'\d{2}:\d{2}\n([A-Z][a-zA-Z\s]+)\n'
        matches = re.findall(pattern, transcript_content)
        
        for name in matches:
            name = name.strip()
            # Filter out common false positives
            if len(name) > 3 and not any(word in name.lower() for word in ['unknown', 'speaker', 'interviewer']):
                participants.add(name)
    
    result = list(participants)
    logger.info(f"Extracted {len(result)} participants: {result}")
    return result

def extract_company_names(transcript_content: str) -> List[str]:
    """Extract company/organization names mentioned in transcript."""
    companies = set()
    
    # Check for Granola format - extract from email domains
    if "Attendee Emails:" in transcript_content:
        emails_match = re.search(r'Attendee Emails:\s*(.+?)(?:\n|$)', transcript_content)
        if emails_match:
            emails = emails_match.group(1).strip()
            email_list = [e.strip() for e in emails.split(',')]
            for email in email_list:
                if '@' in email:
                    domain = email.split('@')[1].split('.')[0]
                    # Capitalize properly
                    company = domain.capitalize()
                    # Skip common domains
                    if domain not in ['gmail', 'yahoo', 'outlook', 'hotmail', 'icloud', 'theapply', 'mycareerspan']:
                        companies.add(company)
                        logger.info(f"Extracted company from email: {company}")
    
    # Common patterns for company mentions in transcript body
    patterns = [
        r'at ([A-Z][a-zA-Z]+)',  # "at Lensa", "at Google"
        r'from ([A-Z][a-zA-Z]+)',  # "from Microsoft"
        r'([A-Z][a-zA-Z]+) is ',  # "Lensa is a job board"
        r'work(?:ing)? (?:for|at|with) ([A-Z][a-zA-Z]+)',  # "working at Apple"
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, transcript_content)
        for company in matches:
            company = company.strip()
            # Filter common words that aren't companies
            if company not in ['I', 'The', 'A', 'An', 'And', 'But', 'Or', 'So', 'Yes', 'No']:
                companies.add(company)
    
    result = list(companies)
    logger.info(f"Extracted {len(result)} company mentions: {result}")
    return result

def detect_meeting_type(transcript_content: str, meeting_types: List[str]) -> str:
    """
    Determine primary meeting type from content and declared types.
    """
    content_lower = transcript_content.lower()
    
    # Weight declared types
    if meeting_types:
        return meeting_types[0]
    
    # Infer from content
    if any(word in content_lower for word in ['pricing', 'proposal', 'contract', 'partnership', 'traffic', 'cpc', 'cpa']):
        return 'sales'
    elif any(word in content_lower for word in ['fundraising', 'investment', 'round', 'valuation', 'investor']):
        return 'fundraising'
    elif any(word in content_lower for word in ['community', 'members', 'network', 'alumni']):
        return 'community_partnerships'
    else:
        return 'general'

def detect_blurb_request(transcript_content: str) -> bool:
    """Detect if a blurb was explicitly requested or offered."""
    content_lower = transcript_content.lower()
    keywords = ['blurb', 'introduction', 'intro email', 'write up', 'brief description', 'summary to share']
    return any(keyword in content_lower for keyword in keywords)

def infer_audience_from_transcript(transcript_content: str, participants: List[str], companies: List[str]) -> str:
    """
    Infer the intended audience for deliverables.
    Priority:
    1. Named participant + company (best)
    2. Company name only
    3. Stakeholder type inferred from content
    4. Generic fallback
    """
    # Remove "Vrijen Attawar" from participants if present
    external_participants = [p for p in participants if 'vrijen' not in p.lower()]
    
    if external_participants and companies:
        # Best case: "Mai Flynn (Lensa)" or "Mai Flynn, Lensa team"
        return f"{external_participants[0]} ({companies[0]})"
    elif external_participants:
        return external_participants[0]
    elif companies:
        return f"{companies[0]} team"
    else:
        # Fallback to inferring from content
        content_lower = transcript_content.lower()
        if 'community' in content_lower:
            return "community leaders"
        elif 'investor' in content_lower:
            return "potential investors"
        elif 'customer' in content_lower or 'client' in content_lower:
            return "potential clients"
        else:
            return "business partners"

def infer_persona_from_context(meeting_type: str, transcript_content: str) -> str:
    """Infer the appropriate persona/tone based on meeting type and content."""
    content_lower = transcript_content.lower()
    
    if meeting_type == 'fundraising':
        return "professional, strategic, growth-focused"
    elif meeting_type == 'community_partnerships':
        return "collaborative, supportive, community-focused"
    elif meeting_type == 'sales':
        # Check if more technical or more relationship-focused
        if any(word in content_lower for word in ['api', 'integration', 'technical', 'xml', 'feed']):
            return "professional, technical, solutions-oriented"
        else:
            return "professional, value-focused, collaborative"
    else:
        return "professional, clear, engaging"

def infer_angle_from_transcript(transcript_content: str, meeting_type: str, companies: List[str]) -> str:
    """
    Infer the primary angle/focus for the deliverable.
    Should reflect what was actually discussed.
    """
    content_lower = transcript_content.lower()
    
    # Look for key themes
    if 'job' in content_lower and any(word in content_lower for word in ['board', 'posting', 'distribution', 'traffic']):
        company_str = companies[0] if companies else "job board"
        return f"partnership for job distribution with {company_str}"
    elif 'community' in content_lower and 'monetization' in content_lower:
        return "community monetization through talent partnerships"
    elif 'fundraising' in content_lower or 'investment' in content_lower:
        return "investment opportunity and growth strategy"
    elif 'hackathon' in content_lower:
        return "hackathon talent acquisition and community engagement"
    elif 'recruitment' in content_lower or 'hiring' in content_lower:
        return "recruitment solutions and talent access"
    else:
        # Generic fallback based on meeting type
        if meeting_type == 'sales':
            return "business partnership and mutual value creation"
        elif meeting_type == 'community_partnerships':
            return "community growth and member value"
        else:
            return "strategic collaboration opportunities"

# === CORE LLM FUNCTIONS ===

async def query_llm_internal(
    prompt: str,
    context: Dict[str, Any],
    max_tokens: int = 500,
    model: str = "internal-careerspan-llm",
) -> Optional[str]:
    """
    Simulates a direct call to the internal LLM to generate content.
    In a real Zo environment, this would interface directly with the model's generation capability.
    
    Args:
        prompt: The full prompt string for the LLM.
        context: A dictionary containing all relevant parameters (meeting_info, num_paragraphs, etc.)
                 needed to construct the *simulated* LLM response for testing purposes.
        max_tokens: The maximum number of tokens to generate.
        model: The name of the internal LLM model to use.
        
    Returns:
        The generated text from the LLM, or None if generation failed.
    """
    logger.info(f"Simulating internal LLM call to model: {model} with prompt length {len(prompt)}")

    # Extract context variables for the simulated response
    meeting_info = context.get("meeting_info", {})
    transcript_content = context.get("transcript_content", "")
    knowledge_base = context.get("knowledge_base", {})
    num_paragraphs = context.get("num_paragraphs", 3)
    intended_audience = context.get("intended_audience", "general")
    persona = context.get("persona", "professional")
    angle = context.get("angle", "summary")
    num_sections = context.get("num_sections", 3)

    # --- Generic Simulated Response Structure ---
    response_template = (
        f"-- Start Internal LLM Generated Content (simulated from {model}) --\\n\\n"
        f"This content is generated based on the prompt, considering the meeting on "
        f"{meeting_info.get('date', 'Unknown')} with participants {', '.join(meeting_info.get('participants', []))}. "
        f"The target is '{intended_audience}' with a '{persona}' tone and '{angle}' angle. "
        f"Relevant sections of the transcript were prioritized for factual accuracy. "
        f"Careerspan's strategic context and pricing model were woven in as background.\\n\\n"
        f"Key takeaway from transcript (first 100 chars): {transcript_content[:100].strip()}...\\n"
        f"GTM Hypothesis snippet: {knowledge_base.get('gtm_hypotheses', [])[0]['statement'] if knowledge_base.get('gtm_hypotheses') else 'N/A'}...\\n"
        f"Pricing context snippet: {knowledge_base.get('pricing_model_raw', '')[:50].strip()}...\\n\\n"
        f"-- End Internal LLM Generated Content (simulated) --"
    )
    
    # Simulate some processing time
    await asyncio.sleep(0.5)
    
    return response_template

async def infer_parameters_from_transcript(
    transcript_content: str,
    meeting_info: Dict[str, Any],
    deliverable_type: str,
    max_tokens: int = 200
) -> Dict[str, Any]:
    """
    Infers qualitative parameters for a deliverable from the transcript.
    
    FIXED VERSION: Actually extracts information from the transcript instead of returning hardcoded stubs.
    """
    logger.info(f"Inferring parameters for {deliverable_type} from transcript.")
    
    # === EXTRACT ACTUAL INFORMATION FROM TRANSCRIPT ===
    
    # 1. Extract participants
    participants = extract_participants_from_transcript(transcript_content)
    if not participants:
        # Fallback to meeting_info if extraction failed
        participants = meeting_info.get('participants', [])
    
    # 2. Extract company names
    companies = extract_company_names(transcript_content)
    
    # 3. Detect meeting type
    meeting_types = meeting_info.get('meeting_types', [])
    meeting_type = detect_meeting_type(transcript_content, meeting_types)
    
    # 4. Infer deliverable-specific parameters
    blurb_requested = detect_blurb_request(transcript_content)
    intended_audience = infer_audience_from_transcript(transcript_content, participants, companies)
    persona = infer_persona_from_context(meeting_type, transcript_content)
    angle = infer_angle_from_transcript(transcript_content, meeting_type, companies)
    
    # === BUILD PARAMETER DICT BASED ON DELIVERABLE TYPE ===
    
    if deliverable_type == "blurb":
        inferred_params = {
            "blurb_offered_requested": blurb_requested,
            "intended_audience": intended_audience,
            "persona": persona,
            "angle": angle,
            "num_paragraphs": 2,
            # Metadata for debugging
            "_extracted_participants": participants,
            "_extracted_companies": companies,
            "_detected_meeting_type": meeting_type,
        }
    elif deliverable_type == "one_pager_memo":
        inferred_params = {
            "num_sections": 3,
            "intended_audience": intended_audience,
            "persona": persona,
            "angle": angle,
            "_extracted_participants": participants,
            "_extracted_companies": companies,
        }
    elif deliverable_type == "proposal_pricing":
        inferred_params = {
            "num_sections": 4,
            "intended_audience": intended_audience,
            "persona": persona,
            "angle": f"partnership terms and pricing for {intended_audience}",
            "_extracted_participants": participants,
            "_extracted_companies": companies,
        }
    else:
        inferred_params = {
            "intended_audience": intended_audience,
            "persona": persona,
            "angle": angle,
        }
    
    logger.info(f"Inferred parameters for {deliverable_type}: {json.dumps(inferred_params, indent=2)}")
    
    # === VALIDATION ===
    # Check if inferred params seem reasonable
    if intended_audience == "business partners" and len(participants) > 1:
        logger.warning(f"Generic audience inferred despite {len(participants)} participants found. May indicate extraction issue.")
    
    if "unknown" in angle.lower():
        logger.warning("Generic angle inferred. Transcript may lack clear discussion points.")
    
    return inferred_params

# === VALIDATION FUNCTIONS ===

def validate_inferred_parameters(
    inferred_params: Dict[str, Any],
    transcript_content: str,
    deliverable_type: str
) -> Dict[str, Any]:
    """
    Validate that inferred parameters make sense given the transcript.
    Returns validation results with confidence scores and warnings.
    """
    validation = {
        "valid": True,
        "confidence": 1.0,
        "warnings": [],
        "errors": []
    }
    
    intended_audience = inferred_params.get("intended_audience", "")
    angle = inferred_params.get("angle", "")
    
    # Check 1: Audience name appears in transcript
    if intended_audience and "(" in intended_audience:
        # Extract name and company
        name_part = intended_audience.split("(")[0].strip()
        company_part = intended_audience.split("(")[1].replace(")", "").strip()
        
        # Name should appear in transcript
        if name_part.lower() not in transcript_content.lower():
            validation["warnings"].append(f"Audience name '{name_part}' not found in transcript")
            validation["confidence"] *= 0.7
        
        # Company should appear in transcript
        if company_part.lower() not in transcript_content.lower():
            validation["warnings"].append(f"Company '{company_part}' not found in transcript")
            validation["confidence"] *= 0.8
    
    # Check 2: Angle keywords should appear in transcript
    angle_keywords = angle.lower().split()
    significant_keywords = [w for w in angle_keywords if len(w) > 4 and w not in ['partnership', 'with', 'through', 'for']]
    matches = sum(1 for keyword in significant_keywords if keyword in transcript_content.lower())
    
    if significant_keywords and matches == 0:
        validation["warnings"].append(f"None of the angle keywords {significant_keywords} found in transcript")
        validation["confidence"] *= 0.5
        validation["valid"] = False
    
    # Check 3: Deliverable type makes sense for content
    content_lower = transcript_content.lower()
    if deliverable_type == "proposal_pricing" and 'pricing' not in content_lower and 'proposal' not in content_lower:
        validation["warnings"].append("Proposal/pricing deliverable requested but not discussed in meeting")
        validation["confidence"] *= 0.8
    
    # Final confidence check
    if validation["confidence"] < 0.5:
        validation["valid"] = False
        validation["errors"].append(f"Confidence too low ({validation['confidence']:.2f}) - parameters may be incorrect")
    
    logger.info(f"Validation result: confidence={validation['confidence']:.2f}, valid={validation['valid']}, warnings={len(validation['warnings'])}")
    
    return validation
