#!/usr/bin/env python3
"""
Utility functions for interacting with the internal LLM.
This module centralizes LLM call simulation for consistency across generators and orchestrator.
"""

import logging
from typing import Any, Dict, Optional
import asyncio # Import asyncio
import json

logger = logging.getLogger(__name__)

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
    num_sections = context.get("num_sections", 3) # For one-pager/proposal

    # --- Generic Simulated Response Structure ---
    # This part needs to be dynamically adjusted based on what kind of deliverable is expected.
    # For the blurb, one-pager, and proposal, I'll have specific logic in their generators.
    # For the general LLM utility, a generic structured response is fine for simulation.
    response_template = (
        f"-- Start Internal LLM Generated Content (simulated from {model}) --\n\n"
        f"This content is generated based on the prompt, considering the meeting on "
        f"{meeting_info.get('date', 'Unknown')} with participants {', '.join(meeting_info.get('participants', []))}. "
        f"The target is '{intended_audience}' with a '{persona}' tone and '{angle}' angle. "
        f"Relevant sections of the transcript were prioritized for factual accuracy. "
        f"Careerspan's strategic context and pricing model were woven in as background.\n\n"
        f"Key takeaway from transcript (first 100 chars): {transcript_content[:100].strip()}...\n"
        f"GTM Hypothesis snippet: {knowledge_base.get('gtm_hypotheses', [])[0]['statement'] if knowledge_base.get('gtm_hypotheses') else 'N/A'}...\n"
        f"Pricing context snippet: {knowledge_base.get('pricing_model_raw', '')[:50].strip()}...\n\n"
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
    Infers qualitative parameters for a deliverable from the transcript using the internal LLM.
    """
    logger.info(f"Inferring parameters for {deliverable_type} from transcript.")

    # This prompt guides the internal LLM to extract relevant parameters
    prompt = f"""
You are an AI assistant tasked with extracting key parameters for a {deliverable_type} from a meeting transcript.
Analyze the following meeting transcript. Identify any implicit or explicit mentions of:
- **Blurb Offer/Request:** Was a blurb explicitly offered or requested during the call? If so, why and for whom?
- **Intended Audience:** Who is this {deliverable_type} for? (e.g., specific person, company, type of stakeholder)
- **Persona:** What tone or style should the {deliverable_type} adopt? (e.g., professional, empathetic, direct, enthusiastic)
- **Angle/Focus:** What is the main message or purpose of the {deliverable_type}? What aspect should be emphasized? (e.g., partnership synergy, business benefits, technical integration, problem-solving)
- **Length/Structure (if applicable):** For a blurb, how many paragraphs (1-3)? For a one-pager/proposal, how many sections?

Prioritize information directly stated or strongly implied in the transcript. If a parameter is not clear, provide a reasonable default based on the overall meeting context.

Meeting Date: {meeting_info.get('date', 'Unknown')}
Participants: {', '.join(meeting_info.get('participants', []))}

--- Meeting Transcript ---
{transcript_content.strip()}

---

Provide the inferred parameters in a JSON object. Ensure numerical values are integers. Example structure:
{{
  "blurb_offered_requested": false, 
  "intended_audience": "Theresa (Community Manager)",
  "persona": "supportive, collaborative",
  "angle": "Careerspan's value for community monetization",
  "num_paragraphs": 2
}}
"""

    context_for_llm = {"meeting_info": meeting_info, "transcript_content": transcript_content}

    # Directly return a structured JSON string for simulation purposes
    # In a real LLM call, this would be the actual parsed output from the LLM.
    if deliverable_type == "blurb":
        # Based on the transcript summary for Theresa's call:
        # - No explicit offer/request for blurb, so false.
        # - Audience: MLH founder (for hackathon collab) or Theresa (for her community).
        #   Let's go with MLH founder based on the discussion of introductions.
        # - Persona: Collaborative, impact-focused.
        # - Angle: Partnership synergy for hackathon recruitment/talent pool.
        # - Length: 2 paragraphs seems reasonable for an intro blurb.
        simulated_json_response = json.dumps({
            "blurb_offered_requested": False,
            "intended_audience": "MLH Founder (for hackathon collaboration)",
            "persona": "collaborative, impact-focused",
            "angle": "Careerspan's support for MLH hackathon talent and community engagement",
            "num_paragraphs": 2
        })
    elif deliverable_type == "one_pager_memo":
        simulated_json_response = json.dumps({
            "num_sections": 3,
            "intended_audience": "Theresa Anoje (Social Impact SF Community Manager)",
            "persona": "informative, strategic",
            "angle": "potential partnership and community monetization with Careerspan"
        })
    elif deliverable_type == "proposal_pricing":
         simulated_json_response = json.dumps({
            "num_sections": 4,
            "intended_audience": "Theresa Anoje (Social Impact SF Community Manager)",
            "persona": "formal, value-driven",
            "angle": "Careerspan's tailored recruitment solutions and pricing for community partners"
        })
    else:
        simulated_json_response = json.dumps({
            "blurb_offered_requested": False,
            "intended_audience": "general",
            "persona": "professional",
            "angle": "summary",
            "num_paragraphs": 3 # Default
        })

    # This part of the function now directly returns the simulated_json_response
    # without calling query_llm_internal, as we are manually simulating the JSON output
    # for parameter inference here.
    
    if simulated_json_response:
        try:
            inferred_params = json.loads(simulated_json_response)
            return inferred_params
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from inferred parameters: {e}. Raw: {simulated_json_response}")
            return {}
    return {}