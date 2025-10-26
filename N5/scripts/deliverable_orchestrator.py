#!/usr/bin/env python3
"""
Deliverable Generation Orchestrator (deliverable_orchestrator.py)

This script orchestrates the generation of various deliverables (blurbs, one-pagers/memos,
proposals/pricing sheets) based on meeting transcripts and contextual knowledge.
It acts as a central decision-maker, invoking specialized generator modules.
"""

import asyncio
import json
import logging
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any

# New: required knowledge references
REQUIRED_KNOWLEDGE_PATHS = {
    "gtm_hypotheses": Path("/home/workspace/Knowledge/hypotheses/gtm_hypotheses.md"),
    "pricing_model": Path("/home/workspace/Knowledge/stable/company/pricing.md"),
}
OPTIONAL_KNOWLEDGE_PATHS = {
    "company_overview": Path("/home/workspace/Knowledge/stable/company/overview.md"),
    "company_principles": Path("/home/workspace/Knowledge/stable/company/principles.md"),
    "company_strategy": Path("/home/workspace/Knowledge/stable/company/strategy.md"),
    "positioning_current": Path("/home/workspace/Knowledge/semi_stable/positioning_current.md"),
    "product_current": Path("/home/workspace/Knowledge/semi_stable/product_current.md"),
    "market_recruiting": Path("/home/workspace/Knowledge/market/recruiting_industry.md"),
    "market_community_hiring": Path("/home/workspace/Knowledge/market/community_driven_hiring.md"),
    "bio": Path("/home/workspace/Knowledge/stable/bio.md"),
    "voice_prefs": Path("/home/workspace/Knowledge/context/howie_instructions/preferences.md"),
}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)sZ %(levelname)s %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Constants
WORKSPACE = Path("/home/workspace")
DELIVERABLES_DIR = WORKSPACE / "Careerspan" / "Deliverables"
EXAMPLES_DIR = DELIVERABLES_DIR / "Examples"
SCRIPTS_DIR = WORKSPACE / "N5" / "scripts"
BLOCKS_DIR = SCRIPTS_DIR / "blocks"
DELIVERABLES_BLOCKS_DIR = BLOCKS_DIR / "deliverables"

# Ensure deliverable examples directory structure exists
(EXAMPLES_DIR / "blurbs").mkdir(parents=True, exist_ok=True)
(EXAMPLES_DIR / "one_pagers").mkdir(parents=True, exist_ok=True)
(EXAMPLES_DIR / "proposals_pricing").mkdir(parents=True, exist_ok=True)
DELIVERABLES_BLOCKS_DIR.mkdir(parents=True, exist_ok=True)


def load_or_create_pricing_md() -> Path:
    """Ensures pricing.md exists, creating it with placeholder content if not."""
    pricing_file_path = WORKSPACE / "Knowledge" / "stable" / "company" / "pricing.md"
    if not pricing_file_path.exists():
        logger.warning(f"Pricing model file not found: {pricing_file_path}. Creating a placeholder.")
        pricing_file_path.parent.mkdir(parents=True, exist_ok=True)
        placeholder_content = """# Careerspan Pricing Model

## Overview
This document outlines Careerspan's general pricing philosophy and common models.
Actual pricing is customized based on client needs, scope, and partnership type.

## Principles
- **Value-Based:** Pricing reflects the value delivered (e.g., quality hires, time saved).
- **Flexible:** Adaptable to different client sizes and engagement models.
- **Transparent:** Clear understanding of costs for services rendered.

## Common Models

### 1. Warm Introduction Fee (Per Placement Model)
- **Description:** A fee charged per successful warm introduction that leads to a hire.
- **Rate:** Typically $300-400 per warm introduction that results in a hire.
- **Use Case:** Initial engagements, proving value, smaller clients, low-risk trials.

### 2. Retainer-Based / Project-Based
- **Description:** A fixed fee for a defined scope of work over a period, or for a specific project.
- **Rate:** Varies greatly by project scope and duration.
- **Use Case:** Headhunting for specific roles, market mapping, talent pipeline building.

### 3. Subscription Model (Future)
- **Description:** Recurring access to Careerspan's services (e.g., candidate bundles, insights).
- **Rate:** TBD, dependent on features and usage tiers.
- **Conditions to Unlock:** Requires demonstrated success (e.g., 5-10 successful placements via warm intros).
- **Use Case:** Long-term partnerships, larger organizations with ongoing hiring needs.

## Custom Engagements
For unique requirements, Careerspan is open to structuring custom pricing models.

## Contact
For a detailed pricing proposal tailored to your needs, please contact the Careerspan sales team.
"""
        pricing_file_path.write_text(placeholder_content, encoding='utf-8')
    return pricing_file_path


class DeliverableOrchestrator:
    def __init__(self, meeting_context: Dict[str, Any]):
        self.meeting_context = meeting_context
        self.transcript_content = meeting_context.get("transcript_content", "")
        self.meeting_info = meeting_context.get("meeting_info", {})
        self.meeting_types = meeting_context.get("meeting_types", [])
        self.stakeholder_types = meeting_context.get("stakeholder_types", [])
        self.output_dir = Path(meeting_context.get("output_dir", "./generated_deliverables")) # Must be an absolute path
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.knowledge_base = self._load_knowledge_base()
        self.generated_deliverables: List[Dict[str, str]] = []
        self.errors: List[Dict[str, str]] = []

    def _parse_gtm_hypotheses(self, markdown_content: str) -> List[Dict[str, Any]]:
        """
        Parses the GTM hypotheses markdown content into a structured list of dictionaries.
        """
        hypotheses = []
        # Regex to find each hypothesis block
        hypothesis_pattern = re.compile(
            r"## (H-GTM-\d{3}:.*?)\n"  # Hypothesis heading
            r"(.*?)(?=\n## H-GTM-\d{3}:|\n## Template for New Hypotheses|\Z)", # Content until next hypothesis or end
            re.DOTALL
        )
        
        # Extract individual hypothesis blocks
        for match in hypothesis_pattern.finditer(markdown_content):
            full_heading = match.group(1).strip()
            content = match.group(2).strip()

            # Extract Hypothesis Name (H-GTM-XXX) and Title
            heading_parts = full_heading.split(':', 1)
            hypothesis_id = heading_parts[0].strip()
            hypothesis_title = heading_parts[1].strip() if len(heading_parts) > 1 else ""

            # Further parse content for key fields
            statement_match = re.search(r"Statement:\n(.*?)(?=\nWhy it matters:|\Z)", content, re.DOTALL)
            why_it_matters_match = re.search(r"Why it matters:\n(.*?)(?=\nHow to test:|\Z)", content, re.DOTALL)
            how_to_test_match = re.search(r"How to test:\n(.*?)(?=\nStatus:|\Z)", content, re.DOTALL)
            status_match = re.search(r"Status:\s*`(.+?)`", content)
            evidence_match = re.search(r"Evidence:\n(.*?)(?=\nLast updated:|\Z)", content, re.DOTALL)
            stakeholders_match = re.search(r"Stakeholders:\s*(.*?)\n", content)
            last_updated_match = re.search(r"Last updated:\s*(\d{4}-\d{2}-\d{2})", content)


            hypothesis = {
                "id": hypothesis_id,
                "title": hypothesis_title,
                "stakeholders": [s.strip("`[]") for s in stakeholders_match.group(1).split("` `")] if stakeholders_match else [],
                "statement": statement_match.group(1).strip() if statement_match else "",
                "why_it_matters": why_it_matters_match.group(1).strip() if why_it_matters_match else "",
                "how_to_test": how_to_test_match.group(1).strip() if how_to_test_match else "",
                "status": status_match.group(1).strip() if status_match else "UNKNOWN",
                "evidence": evidence_match.group(1).strip() if evidence_match else "",
                "last_updated": last_updated_match.group(1).strip() if last_updated_match else "",
                "full_content": content # Keep full content for LLM context if needed
            }
            hypotheses.append(hypothesis)
        
        return hypotheses

    def _read_markdown_file(self, file_path: Path) -> str:
        """Helper to read markdown content."""
        if file_path.exists():
            return file_path.read_text(encoding='utf-8')
        logger.warning(f"Knowledge file not found: {file_path}")
        return ""

    def _load_knowledge_base(self) -> Dict[str, Any]:
        """
        Loads semi-stable and stable information (GTM, pricing, etc.).
        Protocol: always attempt to load core Knowledge files.
        """
        # Ensure pricing.md exists or create placeholder
        pricing_file_path = load_or_create_pricing_md()

        # Required
        gtm_md = self._read_markdown_file(REQUIRED_KNOWLEDGE_PATHS["gtm_hypotheses"])  # may be empty but logged
        pricing_md = self._read_markdown_file(pricing_file_path)

        # Optional set
        opt = {k: self._read_markdown_file(p) for k, p in OPTIONAL_KNOWLEDGE_PATHS.items()}

        knowledge = {
            "gtm_hypotheses": self._parse_gtm_hypotheses(gtm_md) if gtm_md else [],
            "pricing_model_raw": pricing_md,
            "company_overview": opt.get("company_overview", ""),
            "company_principles": opt.get("company_principles", ""),
            "company_strategy": opt.get("company_strategy", ""),
            "positioning_current": opt.get("positioning_current", ""),
            "product_current": opt.get("product_current", ""),
            "market_recruiting": opt.get("market_recruiting", ""),
            "market_community_hiring": opt.get("market_community_hiring", ""),
            "bio": opt.get("bio", ""),
            "voice_prefs": opt.get("voice_prefs", ""),
            "knowledge_sources": {
                "required": {k: str(v) for k, v in REQUIRED_KNOWLEDGE_PATHS.items()},
                "optional": {k: str(v) for k, v in OPTIONAL_KNOWLEDGE_PATHS.items()},
            },
        }
        logger.info(
            "Loaded knowledge base: gtm=%s, pricing=%s, optional_keys=%s",
            len(knowledge["gtm_hypotheses"]), bool(knowledge["pricing_model_raw"]),
            [k for k in OPTIONAL_KNOWLEDGE_PATHS.keys() if knowledge.get(k)]
        )
        return knowledge

    def _enforce_knowledge_protocol(self, strict: bool = True):
        """Ensure core Knowledge files are available; in strict mode, raise if missing."""
        missing = []
        for key, path in REQUIRED_KNOWLEDGE_PATHS.items():
            if not path.exists():
                missing.append((key, str(path)))
        if missing:
            msg = f"Missing required Knowledge files: {missing}"
            if strict:
                logger.error(msg)
                raise RuntimeError(msg)
            else:
                logger.warning(msg)

    async def _determine_deliverables_needed(self) -> List[str]:
        """
        Intelligently determines which deliverables are needed based on transcript and meeting context.
        This is the core decision-making logic.
        """
        needed_deliverables = []

        # --- Blurbs ---
        if "summary" in self.transcript_content.lower() or \
           any(m_type in self.meeting_types for m_type in ["sales", "networking", "community_partnerships"]):
            needed_deliverables.append("blurb")

        # --- One-Pagers / Memos ---
        if "one-pager" in self.transcript_content.lower() or \
           "memo" in self.transcript_content.lower() or \
           any(m_type in self.meeting_types for m_type in ["sales", "community_partnerships", "fundraising"]):
            needed_deliverables.append("one_pager_memo")

        # --- Proposals / Pricing Sheets ---
        if "proposal" in self.transcript_content.lower() or \
           "pricing" in self.transcript_content.lower() or \
           "terms" in self.transcript_content.lower() or \
           any(m_type in self.meeting_types for m_type in ["sales", "fundraising", "community_partnerships"]):
            needed_deliverables.append("proposal_pricing")

        logger.info(f"Determined deliverables needed: {needed_deliverables}")
        return needed_deliverables

    async def generate_deliverables(self) -> List[Dict[str, str]]:
        """Orchestrates the generation of all identified deliverables."""
        # Enforce knowledge protocol before generation
        self._enforce_knowledge_protocol(self.meeting_context.get("strict_knowledge", True))

        deliverables_to_generate = await self._determine_deliverables_needed()

        for deliverable_type in deliverables_to_generate:
            try:
                # Infer parameters for blurb specifically
                blurb_params = {}
                if deliverable_type == "blurb":
                    from llm_utils import infer_parameters_from_transcript
                    blurb_params = await infer_parameters_from_transcript(
                        self.transcript_content,
                        self.meeting_info,
                        deliverable_type="blurb",
                        max_tokens=300
                    )
                    blurb_params.setdefault("num_paragraphs", 2)
                    blurb_params.setdefault("intended_audience", "owners of micro-communities")
                    blurb_params.setdefault("persona", "community-focused, collaborative, expert")
                    blurb_params.setdefault("angle", "synergy for talent and community monetization")
                    logger.info(f"Inferred blurb parameters: {blurb_params}")

                if deliverable_type == "blurb":
                    from blocks.deliverables import blurb_generator
                    generated_path = await blurb_generator.generate_blurb(
                        self.transcript_content,
                        self.meeting_info,
                        self.knowledge_base,
                        self.output_dir / "blurbs",
                        num_paragraphs=blurb_params["num_paragraphs"],
                        intended_audience=blurb_params["intended_audience"],
                        persona=blurb_params["persona"],
                        angle=blurb_params["angle"]
                    )
                    if generated_path:
                        self.generated_deliverables.append({
                            "type": "blurb",
                            "path": str(generated_path),
                            "inferred_params": blurb_params
                        })
                elif deliverable_type == "one_pager_memo":
                    from blocks.deliverables import one_pager_memo_generator
                    generated_path = await one_pager_memo_generator.generate_one_pager_memo(
                        self.transcript_content,
                        self.meeting_info,
                        self.knowledge_base,
                        self.output_dir / "one_pagers"
                    )
                    if generated_path:
                        self.generated_deliverables.append({
                            "type": "one_pager_memo",
                            "path": str(generated_path)
                        })
                elif deliverable_type == "proposal_pricing":
                    from blocks.deliverables import proposal_pricing_generator
                    generated_path = await proposal_pricing_generator.generate_proposal_pricing(
                        self.transcript_content,
                        self.meeting_info,
                        self.knowledge_base,
                        self.output_dir / "proposals_pricing"
                    )
                    if generated_path:
                        self.generated_deliverables.append({
                            "type": "proposal_pricing",
                            "path": str(generated_path)
                        })
                else:
                    logger.warning(f"Unknown deliverable type requested: {deliverable_type}")

            except Exception as e:
                logger.error(f"Failed to generate {deliverable_type}: {e}", exc_info=True)
                self.errors.append({
                    "deliverable_type": deliverable_type,
                    "message": str(e)
                })

        return self.generated_deliverables

    def _log_error(self, component: str, message: str, severity: str):
        """Internal error logging for the orchestrator."""
        self.errors.append({
            "component": component,
            "message": message,
            "severity": severity
        })

async def main():
    """
    Example CLI entry point for testing the DeliverableOrchestrator.
    In a real scenario, this would be called by the MeetingOrchestrator.
    """
    import argparse
    parser = argparse.ArgumentParser(description="Generate deliverables from a transcript.")
    parser.add_argument("transcript_path", help="Path to the meeting transcript file.")
    parser.add_argument("--meeting-type", nargs='*', default=[], help="Type of meeting (e.g., sales, fundraising).")
    parser.add_argument("--stakeholder-type", nargs='*', default=[], help="Type of stakeholder (e.g., vc, customer_founder).")
    parser.add_argument("--output-dir", default="./generated_deliverables", help="Directory to save generated deliverables.")
    parser.add_argument("--strict-knowledge", action="store_true", default=True, help="Require core Knowledge files to be present.")
    # ADDED: New arguments for qualitative parameters
    parser.add_argument("--num-paragraphs", type=int, default=2, help="Number of paragraphs for blurbs.")
    parser.add_argument("--num-sections", type=int, default=3, help="Number of sections for one-pagers/proposals.")
    parser.add_argument("--intended-audience", default="general", help="Intended audience for the deliverable.")
    parser.add_argument("--persona", default="professional", help="Persona/voice for the deliverable.")
    parser.add_argument("--angle", default="summary", help="Angle or focus for the deliverable.")


    args = parser.parse_args()

    # Simulate meeting context from arguments
    transcript_content = ""
    try:
        with open(args.transcript_path, 'r', encoding='utf-8') as f:
            transcript_content = f.read()
    except FileNotFoundError:
        logger.error(f"Transcript file not found: {args.transcript_path}")
        return 1

    # Ensure pricing.md exists for context
    pricing_file_path = load_or_create_pricing_md()

    meeting_context = {
        "transcript_content": transcript_content,
        "meeting_info": {
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "participants": ["Vrijen Attawar"] + [p.strip() for p in args.stakeholder_type if p.strip() != ""],
            "stakeholder_primary": args.stakeholder_type[0] if args.stakeholder_type else "unknown"
        },
        "meeting_types": args.meeting_type,
        "stakeholder_types": args.stakeholder_type,
        "output_dir": os.path.abspath(args.output_dir),
        "strict_knowledge": bool(args.strict_knowledge),
        # ADDED: Pass new arguments to context
        "num_paragraphs": args.num_paragraphs,
        "num_sections": args.num_sections,
        "intended_audience": args.intended_audience,
        "persona": args.persona,
        "angle": args.angle,
    }

    orchestrator = DeliverableOrchestrator(meeting_context)
    generated = await orchestrator.generate_deliverables()

    if generated:
        logger.info(f"Successfully generated {len(generated)} deliverables.")
        for item in generated:
            print(f"- Type: {item['type']}, Path: {item['path']}")
    else:
        logger.info("No deliverables generated or all failed.")

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))
