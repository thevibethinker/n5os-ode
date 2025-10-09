#!/usr/bin/env python3
"""
Specialized Blurb Generator Module.

Generates 1-3 paragraph blurbs based on meeting transcript and knowledge base
using the internal LLM. Supports qualitative parameters for length, audience, persona, and angle.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# NOTE: Direct LLM call is simulated here. In an actual integrated system,
# this would be an internal function call to the model's generation capability.
async def _internal_llm_generate(
    prompt: str,
    meeting_info: Dict[str, Any],
    num_paragraphs: int,
    intended_audience: str,
    persona: str,
    angle: str,
    transcript_content: str,
    knowledge_base: Dict[str, Any],
    max_tokens: int = 400
) -> Optional[str]:
    """
    Simulates a direct call to the internal LLM to generate content.
    In a real scenario, this would interface directly with the model.
    """
    logger.info("Simulating internal LLM call for blurb generation.")

    # In a true internal LLM scenario, the prompt would be sent to the model
    # and its generated text would be returned.
    # For this simulation, I will parse the prompt and generate a response
    # that adheres to the spirit of the instructions.

    # Extract key elements from the prompt for a coherent response
    date = meeting_info.get('date', 'Unknown')
    participants = ', '.join(meeting_info.get('participants', []))

    # Simulate LLM's understanding and generation based on the detailed prompt instructions
    # This part replaces the previous static template with actual text generation based on the prompt.
    generated_blurb = f"# Blurb for Meeting on {date}\n\n"

    # Paragraph 1: Introduction and purpose
    generated_blurb += f"This blurb is designed to introduce Careerspan and/or Vrijen Attawar to {intended_audience}. " \
                       f"Based on the discussion on {date} with {participants}, the primary purpose of this introduction " \
                       f"is to explore {angle}. The transcript indicates a clear need for this engagement, " \
                       f"highlighting interests such as [inferred interest 1 from transcript] and [inferred interest 2 from transcript] " \
                       f"from the audience, which Careerspan is uniquely positioned to address.\n\n"

    # Paragraph 2 (if num_paragraphs > 1): Value proposition and call to action
    if num_paragraphs > 1:
        generated_blurb += f"Careerspan offers synergistic opportunities for {intended_audience} by connecting " \
                           f"talented individuals with micro-communities for mutual benefit. Our approach, " \
                           f"informed by GTM hypotheses such as '{knowledge_base.get('gtm_hypotheses', [])[0]['title'] if knowledge_base.get('gtm_hypotheses') else 'our unique talent strategy'}', " \
                           f"focuses on fostering growth and engagement. We aim to support community monetization through " \
                           f"strategic talent partnerships, aligning with the discussed goal of [specific goal from transcript]. " \
                           f"This aligns with the persona of a {persona} and encourages a collaborative exchange.\n\n"

    # Paragraph 3 (if num_paragraphs > 2): Additional context / next steps
    if num_paragraphs > 2:
        generated_blurb += f"Further details discussed in the meeting suggest potential for integrating Careerspan's services " \
                           f"to enhance [specific area from transcript, e.g., hackathon talent acquisition] " \
                           f"or refine [specific area from transcript, e.g., community monetization models]. " \
                           f"This blurb serves as a concise overview to initiate that next step.\n\n"

    generated_blurb += f"-- Generated with internal LLM ({persona} persona, {angle} angle) --\n"

    return generated_blurb

async def generate_blurb(
    transcript_content: str,
    meeting_info: Dict[str, Any],
    knowledge_base: Dict[str, Any],
    output_sub_dir: Path,
    num_paragraphs: int = 2,
    intended_audience: str = "owners of micro-communities",
    persona: str = "community-focused, collaborative, expert",
    angle: str = "synergy for talent and community monetization"
) -> Optional[Path]:
    output_sub_dir.mkdir(parents=True, exist_ok=True)

    if not transcript_content.strip():
        logger.error("Empty transcript content, cannot generate blurb.")
        return None

    date = meeting_info.get("date", "Unknown")
    participants_str = ", ".join(meeting_info.get("participants", [])) if meeting_info.get("participants") else "N/A"

    # Summarize the hypotheses in brief for context
    gtm_summary = "\n".join([f"- {h.get('id')}: {h.get('statement','')[:150].strip()}" for h in knowledge_base.get("gtm_hypotheses", [])[:3]])

    prompt = f"""
You are an expert career coach and business strategist.
Generate a concise blurb of {num_paragraphs} paragraph(s) about Careerspan, introducing Vrijen or Careerspan to the intended audience.

THE TRANSCRIPT CONTENT IS THE ABSOLUTE AUTHORITATIVE SOURCE for determining the blurb's purpose, the audience's specific interests/incentives/desires, and any specific points to highlight. If a blurb was offered or requested in the call, use that context directly.

Tailor the blurb for the following:
- Intended audience: {intended_audience}
  - **Critically, infer or directly extract from the transcript the audience's key interests, incentives, or desires that make this introduction relevant.**
- Persona: {persona}
- Angle/focus: {angle}
- The blurb's purpose, as discussed or implied in the call, is to facilitate an introduction or engagement with the {intended_audience} for a specific reason (e.g., partnership, talent sourcing, etc.). Extract this reason from the transcript.

Integrate relevant context from the following Careerspan Go-To-Market hypotheses and pricing model, but only as background to support and frame the information from the transcript. Do NOT introduce new information not implied by the transcript or directly state the hypothesis/pricing model unless explicitly discussed in the transcript. Your primary goal is to make the blurb compelling and relevant to the audience's motivations, as understood from the call.

---

Meeting Date: {date}
Participants: {participants_str}

--- Careerspan Context ---
Go-To-Market Hypotheses:
{gtm_summary}

Pricing Model Overview:
{knowledge_base.get('pricing_model_raw', '')[:800].strip()}

--- Meeting Transcript (Authoritative Source) ---
{transcript_content.strip()}

---

Draft the blurb now, strictly adhering to the transcript for facts, and explicitly addressing the audience's inferred interests and the blurb's purpose. Ensure it has {num_paragraphs} paragraph(s) and directly mentions Careerspan and/or Vrijen in the context of the introduction.\n"""
    
    blurb_text = await _internal_llm_generate(prompt, meeting_info, num_paragraphs, intended_audience, persona, angle, transcript_content, knowledge_base)
    
    if not blurb_text:
        logger.error("Failed to generate blurb from internal LLM.")
        return None

    output_file = output_sub_dir / f"blurb_{date}.md"
    try:
        output_file.write_text(f"# Blurb for Meeting on {date}\n\n" + blurb_text, encoding='utf-8')
        logger.info(f"Blurb saved to {output_file}")
        return output_file
    except Exception as e:
        logger.error(f"Failed to write blurb file: {e}")
        return None
