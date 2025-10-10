#!/usr/bin/env python3
"""
Research Prompt Generator

Generate deep research prompts for off-platform execution on ChatGPT/Claude.

Usage:
    research-prompt-generator --entity "Name" --type {person|company|nonprofit|vc|topic} [options]

Author: N5 OS
Version: 1.0.1
Date: 2025-10-09
"""

import argparse
import logging
import sys
import pytz
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)

# Entity types and depth levels
ENTITY_TYPES = ["person", "company", "nonprofit", "vc", "topic"]
DEPTH_LEVELS = ["light", "standard", "deep"]

# Timezone
ET_TZ = pytz.timezone('America/New_York')

def get_et_timestamp() -> str:
    """Get current timestamp in ET timezone."""
    now_et = datetime.now(ET_TZ)
    return now_et.strftime('%Y-%m-%d %H:%M:%S %Z')

def copy_to_clipboard(text: str) -> bool:
    """Copy text to clipboard if pyperclip available."""
    try:
        import pyperclip
        pyperclip.copy(text)
        return True
    except ImportError:
        logger.warning("pyperclip not installed. Install with: pip install pyperclip")
        return False
    except Exception as e:
        logger.warning(f"Clipboard copy failed: {e}")
        return False

def validate_inputs(args) -> None:
    """Validate command line arguments."""
    if not args.entity or not args.entity.strip():
        raise ValueError("Entity name cannot be empty")
    if len(args.entity.strip()) < 2:
        raise ValueError("Entity name too short (minimum 2 characters)")
    
    if args.type not in ENTITY_TYPES:
        raise ValueError(f"Invalid entity type. Must be one of: {', '.join(ENTITY_TYPES)}")
    
    if args.depth not in DEPTH_LEVELS:
        raise ValueError(f"Invalid depth level. Must be one of: {', '.join(DEPTH_LEVELS)}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entity", required=True, help="Entity name to research")
    parser.add_argument("--type", required=True, choices=ENTITY_TYPES, help="Entity type")
    parser.add_argument("--depth", default="standard", choices=DEPTH_LEVELS, help="Research depth")
    parser.add_argument("--context", default="", help="Custom context/framing")
    parser.add_argument("--output", help="Save prompt to file (default: clipboard + stdout)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without copying to clipboard")
    
    args = parser.parse_args()
    
    try:
        # Validate inputs
        validate_inputs(args)
        
        logger.info(f"Generating research prompt for: {args.entity} ({args.type})")
        
        # Load Careerspan context
        careerspan_context = load_careerspan_context()
        
        # Generate prompt
        prompt = generate_prompt(
            entity_name=args.entity,
            entity_type=args.type,
            depth_level=args.depth,
            custom_context=args.context,
            careerspan_context=careerspan_context
        )
        
        # Output
        print("\n" + "=" * 60)
        print("  RESEARCH PROMPT GENERATED")
        print("=" * 60)
        print(f"\nEntity: {args.entity}")
        print(f"Type: {args.type}")
        print(f"Depth: {args.depth}")
        
        if not args.dry_run:
            if copy_to_clipboard(prompt):
                print("\n✓ Copied to clipboard")
            else:
                print("\n✓ Clipboard copy unavailable - see output below")
        else:
            print("\n✓ DRY RUN - not copied to clipboard")
        
        print("\n" + "=" * 60 + "\n")
        print(prompt)
        print("\n" + "=" * 60)
        print("\nNEXT STEPS:")
        print("1. Copy prompt to ChatGPT/Claude")
        print("2. Run research off-platform")
        print("3. Return results to Zo")
        print("4. Run: extract-careerspan-insights --input results.txt")
        print("=" * 60 + "\n")
        
        # Save to file if specified
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(prompt)
            logger.info(f"✓ Saved prompt to: {output_path}")
        
        # TODO: Actually copy to clipboard (requires pyperclip or similar)
        logger.warning("Clipboard copy not yet implemented - copy from output above")
        
        return 0
        
    except Exception as e:
        logger.error(f"✗ Error: {e}", exc_info=True)
        return 1


def load_careerspan_context() -> Dict[str, Any]:
    """Load Careerspan strategic context."""
    context = {
        "company_overview": "Careerspan: 3-D talent data platform for hiring",
        "strategic_focuses": [
            "Go-to-market: partnerships, customer acquisition",
            "Fundraising: Series A preparation",
            "Product: AI coaching, alignment assessment",
            "Market: future of work, HR-tech, talent intelligence"
        ],
        "key_questions": [
            "Partnership potential?",
            "Customer fit?",
            "Investor alignment?",
            "Competitive threat?",
            "Evangelist opportunity?"
        ]
    }
    
    # Try to load bio for additional context
    bio_path = Path("/home/workspace/Knowledge/stable/bio.md")
    if bio_path.exists():
        logger.info("Loading bio context...")
        # Could parse bio here for additional context
        # For now, just use default context
    
    return context


def generate_prompt(
    entity_name: str,
    entity_type: str,
    depth_level: str,
    custom_context: str,
    careerspan_context: Dict[str, Any]
) -> str:
    """Generate the research prompt."""
    
    # Get templates
    base_template = get_base_template()
    entity_template = get_entity_template(entity_type)
    depth_modifiers = get_depth_modifiers(depth_level)
    
    # Build prompt
    prompt_parts = []
    
    # Header
    prompt_parts.append(f"<deepResearchPrompt version=\"1.0\" generated=\"{get_et_timestamp()}\">")
    prompt_parts.append("")
    
    # Core Meta
    prompt_parts.append("  <!-- Core Meta -->")
    prompt_parts.append("  <persona>Deep-Research Scholar</persona>")
    prompt_parts.append("  <audience>Careerspan founders & strategy team</audience>")
    prompt_parts.append("  <tone>Professional • insight-oriented • actionable</tone>")
    prompt_parts.append("  <outputFormat>Markdown + in-line citations</outputFormat>")
    prompt_parts.append("")
    
    # Objective
    depth_desc = {
        "light": "concise",
        "standard": "comprehensive",
        "deep": "exhaustive"
    }[depth_level]
    
    context_focus = custom_context if custom_context else "strategic evaluation"
    
    prompt_parts.append("  <!-- Objective -->")
    prompt_parts.append("  <goal>")
    prompt_parts.append(f"    Produce a {depth_desc} research dossier on {entity_name}")
    prompt_parts.append(f"    ({entity_type}) that is immediately actionable for Careerspan's")
    prompt_parts.append(f"    {context_focus}.")
    prompt_parts.append("  </goal>")
    prompt_parts.append("")
    
    # Pre-execution
    prompt_parts.append("  <!-- Socratic Pre-Check -->")
    prompt_parts.append("  <preExecution>")
    prompt_parts.append("    Ask clarifying questions only if:")
    prompt_parts.append(f"    • Critical information about {entity_name} is ambiguous")
    prompt_parts.append("    • Multiple entities match this name")
    prompt_parts.append("    • Scope needs refinement")
    prompt_parts.append("    Otherwise, proceed with research.")
    prompt_parts.append("  </preExecution>")
    prompt_parts.append("")
    
    # Deliverable structure
    prompt_parts.append("  <!-- Deliverable Structure -->")
    prompt_parts.append("  <deliverableStructure>")
    prompt_parts.append(f"    1. # {entity_name} – Research Dossier")
    prompt_parts.append("    2. ## Executive Summary (≤ 500 words)")
    prompt_parts.append("       • Key findings & explicit **Careerspan Relevance**")
    prompt_parts.append("       • **Strategic-Fit Score (1-5)** with 1-sentence rationale")
    prompt_parts.append("    3. ## Extended Report")
    prompt_parts.append("       • Facts by thematic section (see informationToGather)")
    prompt_parts.append("       • Milestones Timeline (chronological bullets)")
    prompt_parts.append("       • Mini **SWOT** table")
    if entity_type in ["person", "company", "vc"]:
        prompt_parts.append("       • Leadership/Founder Profile")
    prompt_parts.append("       • **Careerspan Relevance – Deep Dive**")
    prompt_parts.append("    4. ## References / Sources")
    prompt_parts.append("  </deliverableStructure>")
    prompt_parts.append("")
    
    # Constraints
    prompt_parts.append("  <!-- Constraints -->")
    prompt_parts.append("  <constraints>")
    prompt_parts.append("    • Cite every data point with an in-line link or footnote")
    prompt_parts.append("    • Tag missing or unverified facts as **{DATA_GAP}**")
    prompt_parts.append("    • Translate non-English sources automatically; append \"*(translated)*\"")
    prompt_parts.append("    • Use clear H2/H3 headings, bullets for dense facts")
    prompt_parts.append("    • Explain jargon on first use; spell out acronyms")
    prompt_parts.append("    • \"Recent news\" = 5 most-recent items ≤ 12 months old")
    prompt_parts.append("  </constraints>")
    prompt_parts.append("")
    
    # Information to gather (entity-specific)
    prompt_parts.append("  <!-- Information to Gather -->")
    prompt_parts.append(entity_template)
    prompt_parts.append("")
    
    # Careerspan lens
    prompt_parts.append("  <!-- Careerspan Lens -->")
    prompt_parts.append("  <careerspanRelevance>")
    prompt_parts.append(f"    **Context:** {careerspan_context['company_overview']}")
    prompt_parts.append("")
    prompt_parts.append("    **Strategic Focuses:**")
    for focus in careerspan_context["strategic_focuses"]:
        prompt_parts.append(f"    • {focus}")
    prompt_parts.append("")
    prompt_parts.append("    **Analysis Framework:**")
    prompt_parts.append("    • Partnership or integration angles")
    prompt_parts.append("    • Potential as customer, investor, or evangelist")
    prompt_parts.append("    • Overlap or conflict with Careerspan's 3-D talent-data thesis")
    prompt_parts.append("    • Risks (e.g., direct competition, platform lock-in)")
    prompt_parts.append("  </careerspanRelevance>")
    prompt_parts.append("")
    
    # Depth modifiers
    prompt_parts.append("  <!-- Depth Modifiers -->")
    prompt_parts.append(f"  <depthLevel value=\"{depth_level}\">")
    for key, value in depth_modifiers.items():
        prompt_parts.append(f"    <{key}>{value}</{key}>")
    prompt_parts.append("  </depthLevel>")
    prompt_parts.append("")
    
    # VC-specific additions
    if entity_type == "vc":
        prompt_parts.append("  <!-- VC-Specific Analysis -->")
        prompt_parts.append("  <vcSpecificRequirements>")
        prompt_parts.append("    • Synergy Matrix: Map Careerspan overlaps with portfolio/thesis")
        prompt_parts.append("    • Red-Flag Spotlight: Identify risks (ranked 1-3 severity)")
        prompt_parts.append("    • Anticipated Objections & Rebuttals")
        prompt_parts.append("    • Portfolio companies relevant to HR-tech/future-of-work")
        prompt_parts.append("    • Investment cadence & check size estimates")
        prompt_parts.append("  </vcSpecificRequirements>")
        prompt_parts.append("")
    
    # Close
    prompt_parts.append("</deepResearchPrompt>")
    
    return "\n".join(prompt_parts)


def get_base_template() -> str:
    """Get base template structure."""
    # Already integrated into generate_prompt
    return ""


def get_entity_template(entity_type: str) -> str:
    """Get entity-specific information requirements."""
    
    templates = {
        "person": """  <informationToGather type="person">
    • Biography & career timeline
    • Current role & organization
    • Public statements on hiring, careers, HR-tech, future of work
    • Board seats, investments, philanthropy
    • Media quotes, op-eds, podcast appearances
    • LinkedIn activity & professional network
    • Twitter/X presence (if relevant)
    • Publications or thought leadership
    • Educational background
    • Connections to Careerspan's domain
  </informationToGather>""",
        
        "company": """  <informationToGather type="company">
    • Products / Services & value proposition
    • Go-to-market motion (channels, pricing, ICP)
    • Key customers (if B2B) or best-guess ICP (if B2C)
    • Founder bios (brief, career highlights)
    • Fund-raising & investors (rounds, dates, totals)
    • Momentum metrics (user counts, ARR, growth rates, headcount)
    • Five most-recent news items (past 12 months)
    • Strategic initiatives / roadmap clues
    • Competitive landscape & adjacencies
    • Technology stack & product architecture (if relevant)
    • Talent/hiring philosophy & practices
  </informationToGather>""",
        
        "nonprofit": """  <informationToGather type="nonprofit">
    • Mission & programs
    • Leadership bios (founder / CEO / Executive Director)
    • Funding sources / major donors & grants
    • Partnerships & advocacy focus
    • Momentum / impact metrics (budget size, individuals served)
    • Recent initiatives / press coverage
    • Geographic focus & scale
    • Stakeholder ecosystem (beneficiaries, partners, funders)
  </informationToGather>""",
        
        "vc": """  <informationToGather type="vc">
    • Fund sizes, vintage years, dry-powder estimate
    • GP / founding-partner bios
    • Investment theses / thematic focus
    • Portfolio highlights (esp. HR-tech / future-of-work companies)
    • Recent deals (last 24 months) & cadence insights
    • Notable exits or marked-up wins
    • Momentum metrics (AUM growth, fund performance signals)
    • Co-investor network
    • Check sizes & stage focus
    • Careerspan-adjacent investments or theses
  </informationToGather>""",
        
        "topic": """  <informationToGather type="topic">
    • Comprehensive definition & scope
    • Historical context & evolution
    • Current state of the art
    • Key players / organizations / thought leaders
    • Recent developments & trends (past 12 months)
    • Academic research & publications
    • Practical applications & use cases
    • Challenges & open problems
    • Future directions & predictions
    • Relevance to Careerspan's domain (talent data, hiring, coaching)
  </informationToGather>"""
    }
    
    return templates.get(entity_type, templates["company"])


def get_depth_modifiers(depth_level: str) -> Dict[str, str]:
    """Get depth-specific modifiers."""
    
    modifiers = {
        "light": {
            "deliverableLength": "500-1000 words",
            "sourcesRequired": "≥3 sources",
            "timeInvestment": "15-30 minutes",
            "sectionsIncluded": "Executive summary, key facts, Careerspan relevance"
        },
        "standard": {
            "deliverableLength": "1500-2500 words",
            "sourcesRequired": "≥5 sources, ≥2 per key fact",
            "timeInvestment": "45-90 minutes",
            "sectionsIncluded": "All standard sections + SWOT"
        },
        "deep": {
            "deliverableLength": "3000-5000 words",
            "sourcesRequired": "≥10 sources, ≥2 independent per key fact",
            "timeInvestment": "2-4 hours",
            "sectionsIncluded": "All sections + competitive analysis + network graph + counter-thesis",
            "additionalRequirements": "Confidence tags, cross-referenced facts, assumptions stated"
        }
    }
    
    return modifiers.get(depth_level, modifiers["standard"])


if __name__ == "__main__":
    sys.exit(main())
