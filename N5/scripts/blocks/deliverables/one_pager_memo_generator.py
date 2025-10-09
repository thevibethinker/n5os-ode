#!/usr/bin/env python3
"""
Specialized One-Pager / Memo Generator Module.

Generates detailed, structured one-pager or memo style deliverables from meeting transcript and knowledge base
using the internal LLM. Supports qualitative parameters for number of sections, audience, persona, and angle.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# NOTE: Direct LLM call is simulated here. In an actual integrated system,
# this would be an internal function call to the model's generation capability.
async def _internal_llm_generate_one_pager_memo(
    prompt: str,
    meeting_info: Dict[str, Any],
    num_sections: int,
    intended_audience: str,
    persona: str,
    angle: str,
    transcript_content: str,
    knowledge_base: Dict[str, Any],
    max_tokens: int = 1200
) -> Optional[str]:
    """
    Simulates a direct call to the internal LLM to generate content.
    In a real scenario, this would interface directly with the model.
    """
    # This simulation provides a structured response.
    logger.info("Simulating internal LLM call for one-pager/memo generation.")

    def _truncate(txt: str, n: int) -> str:
        return (txt[:n] + "...") if len(txt) > n else txt

    generated_content = (
        f"-- Start Internal LLM One-Pager/Memo (simulated) --\n\n"
        f"# One-Pager/Memo for Meeting on {meeting_info.get('date', 'Unknown')}\n\n"
        f"## Overview\n"
        f"This one-pager/memo summarizes the key aspects of the discussion held on {meeting_info.get('date', 'Unknown')} "
        f"with participants {', '.join(meeting_info.get('participants', []))}. It is tailored for "
        f"an audience of '{intended_audience}' with a '{persona}' persona, focusing on the '{angle}' angle "
        f"across {num_sections} sections.\n\n"
        f"## Key Discussion Points (derived from transcript)\n"
        f"The transcript clearly outlined several critical areas, including: "
        f"{_truncate(transcript_content, 300)}...\n\n"
        f"## Strategic Context (from GTM Hypotheses)\n"
        f"Careerspan's Go-To-Market strategy, particularly the hypotheses around "
        f"{knowledge_base.get('gtm_hypotheses', [])[0]['title'] if knowledge_base.get('gtm_hypotheses') else 'key market areas'}, "
        f"informs our understanding of this meeting's implications.\n\n"
        f"## Pricing Considerations (from Model)\n"
        f"The discussion also touched upon pricing aspects. Based on Careerspan's pricing model, "
        f"relevant structures could involve: {_truncate(knowledge_base.get('pricing_model_raw', ''), 200)}...\n\n"
        f"-- End Internal LLM One-Pager/Memo (simulated) --"
    )
    return generated_content

async def generate_one_pager_memo(
    transcript_content: str,
    meeting_info: Dict[str, Any],
    knowledge_base: Dict[str, Any],
    output_sub_dir: Path,
    num_sections: int = 3,
    intended_audience: str = "general",
    persona: str = "professional",
    angle: str = "overview"
) -> Optional[Path]:
    output_sub_dir.mkdir(parents=True, exist_ok=True)
    
    if not transcript_content.strip():
        logger.error("Empty transcript content, cannot generate one-pager/memo.")
        return None

    date = meeting_info.get("date", "Unknown")
    participants_str = ", ".join(meeting_info.get("participants", [])) if meeting_info.get("participants") else "N/A"

    gtm_summary = "\n".join([f"- {h.get('id')}: {h.get('statement','')[:150].strip()}" for h in knowledge_base.get("gtm_hypotheses", [])[:3]])

    prompt = f"""
You are an expert career coach and business strategist.\nGenerate a structured one-pager or memo with {num_sections} sections summarizing the key points and outcomes from the meeting transcript below.\n\nTHE TRANSCRIPT CONTENT IS THE ABSOLUTE AUTHORITATIVE SOURCE. Any information, particularly regarding specific deliverables, numbers, or agreements, must come directly from the transcript.\n\nTailor the one-pager/memo for the following:\n- Intended audience: {intended_audience}\n- Persona: {persona}\n- Angle/focus: {angle}\n
Integrate relevant context from the following Careerspan Go-To-Market hypotheses and pricing model, but only as background to support and frame the information from the transcript. Do NOT introduce new information not implied by the transcript or directly state the hypothesis/pricing model unless explicitly discussed in the transcript.\n
---

Meeting Date: {date}\nParticipants: {participants_str}\n
--- Careerspan Context ---\nGo-To-Market Hypotheses:\n{gtm_summary}\n\nPricing Model Overview:\n{knowledge_base.get('pricing_model_raw', '')[:800].strip()}\n
--- Meeting Transcript (Authoritative Source) ---\n{transcript_content.strip()}\n\n---

Draft the one-pager/memo now, strictly adhering to the transcript for facts, and using the context to frame it. Ensure it has {num_sections} clear sections.\n"""

    # Direct call to internal LLM (simulated for now)
    one_pager_text = await _internal_llm_generate_one_pager_memo(prompt, meeting_info, num_sections, intended_audience, persona, angle, transcript_content, knowledge_base)

    if not one_pager_text:
        logger.error("Failed to generate one-pager/memo from internal LLM.")
        return None

    output_file = output_sub_dir / f"one_pager_memo_{date}.md"
    try:
        output_file.write_text(f"# One-Pager / Memo for Meeting on {date}\n\n" + one_pager_text, encoding='utf-8')
        logger.info(f"One-pager/memo saved to {output_file}")
        return output_file
    except Exception as e:
        logger.error(f"Failed to write one-pager/memo file: {e}")
        return None
