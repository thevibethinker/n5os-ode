#!/usr/bin/env python3
"""
Specialized Proposal / Pricing Sheet Generator Module.

Generates structured proposals and pricing sheets based on meeting transcript and knowledge base
using the internal LLM. Supports qualitative parameters for number of sections, audience, persona, and angle.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# NOTE: Direct LLM call is simulated here. In an actual integrated system,
# this would be an internal function call to the model's generation capability.
async def _internal_llm_generate_proposal_pricing(
    prompt: str,
    meeting_info: Dict[str, Any],
    num_sections: int,
    intended_audience: str,
    persona: str,
    angle: str,
    transcript_content: str,
    knowledge_base: Dict[str, Any],
    max_tokens: int = 1600
) -> Optional[str]:
    """
    Simulates a direct call to the internal LLM to generate content.
    In a real scenario, this would interface directly with the model.
    """
    # This simulation provides a structured response.
    logger.info("Simulating internal LLM call for proposal/pricing generation.")

    def _truncate(txt: str, n: int) -> str:
        return (txt[:n] + "...") if len(txt) > n else txt

    generated_content = (
        f"-- Start Internal LLM Proposal/Pricing (simulated) --\n\n"
        f"# Proposal for Meeting on {meeting_info.get('date', 'Unknown')}\n\n"
        f"## Executive Summary\n"
        f"This proposal, stemming from the discussion on {meeting_info.get('date', 'Unknown')} with "
        f"participants {', '.join(meeting_info.get('participants', []))}, is designed for "
        f"an audience of '{intended_audience}' with a '{persona}' persona, emphasizing the '{angle}' "
        f"across {num_sections} key sections. The content is directly informed by the meeting's specifics.\n\n"
        f"## Proposed Solution\n"
        f"Based on the authoritative transcript, our proposed solution addresses key needs like: "
        f"{_truncate(transcript_content, 500)}... This aligns with Careerspan's GTM strategies related to "
        f"{knowledge_base.get('gtm_hypotheses', [])[0]['title'] if knowledge_base.get('gtm_hypotheses') else 'strategic partnerships'}.\n\n"
        f"## Pricing Structure\n"
        f"Our pricing is transparent and value-based, informed by Careerspan's standard pricing model "
        f"({_truncate(knowledge_base.get('pricing_model_raw', ''), 300)}) and tailored to the discussed scope. "
        f"Specific line items and costs derived from the meeting are: "
        f"(LLM would extract and format these from transcript)\n\n"
        f"## Terms and Next Steps\n"
        f"Standard terms apply, with next steps including further scope refinement and agreement. "
        f"All details are consistent with the meeting dialogue.\n\n"
        f"-- End Internal LLM Proposal/Pricing (simulated) --"
    )
    return generated_content

async def generate_proposal_pricing(
    transcript_content: str,
    meeting_info: Dict[str, Any],
    knowledge_base: Dict[str, Any],
    output_sub_dir: Path,
    num_sections: int = 4,
    intended_audience: str = "general",
    persona: str = "professional",
    angle: str = "business terms"
) -> Optional[Path]:
    output_sub_dir.mkdir(parents=True, exist_ok=True)

    if not transcript_content.strip():
        logger.error("Empty transcript content, cannot generate proposal/pricing sheet.")
        return None

    date = meeting_info.get("date", "Unknown")
    participants_str = ", ".join(meeting_info.get("participants", [])) if meeting_info.get("participants") else "N/A"

    gtm_summary = "\n".join([f"- {h.get('id')}: {h.get('statement','')[:150].strip()}" for h in knowledge_base.get("gtm_hypotheses", [])[:3]])

    prompt = f"""
You are an expert business strategist and proposal writer.
Generate a structured proposal and/or pricing sheet with {num_sections} sections summarizing the key points and outcomes from the meeting transcript below.

THE TRANSCRIPT CONTENT IS THE ABSOLUTE AUTHORITATIVE SOURCE. Any information, particularly regarding specific deliverables, numbers, or agreements, must come directly from the transcript.

Tailor the proposal/pricing sheet for the following:\n- Intended audience: {intended_audience}\n- Persona: {persona}\n- Angle/focus: {angle}\n\nIntegrate relevant context from the following Careerspan Go-To-Market hypotheses and pricing model, but only as background to support and frame the information from the transcript. Do NOT introduce new information not implied by the transcript or directly state the hypothesis/pricing model unless explicitly discussed in the transcript.\n\n---\n\nMeeting Date: {date}\nParticipants: {participants_str}\n
--- Careerspan Context ---\nGo-To-Market Hypotheses:\n{gtm_summary}\n\nPricing Model Overview:\n{knowledge_base.get('pricing_model_raw', '')[:800].strip()}\n
--- Meeting Transcript (Authoritative Source) ---\n{transcript_content.strip()}\n\n---\n
Draft the proposal/pricing sheet now, strictly adhering to the transcript for facts, and using the context to frame it. Ensure it has {num_sections} clear sections, including a pricing section if applicable.\n"""

    # Direct call to internal LLM (simulated for now)
    proposal_text = await _internal_llm_generate_proposal_pricing(prompt, meeting_info, num_sections, intended_audience, persona, angle, transcript_content, knowledge_base)

    if not proposal_text:
        logger.error("Failed to generate proposal/pricing sheet from internal LLM.")
        return None

    output_file = output_sub_dir / f"proposal_pricing_{date}.md"
    try:
        output_file.write_text(f"# Proposal / Pricing Sheet for Meeting on {date}\n\n" + proposal_text, encoding='utf-8')
        logger.info(f"Proposal/pricing sheet saved to {output_file}")
        return output_file
    except Exception as e:
        logger.error(f"Failed to write proposal/pricing file: {e}")
        return None
