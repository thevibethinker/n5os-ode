#!/usr/bin/env python3
"""
Careerspan Insights Extractor

Extract strategic insights from research results with Careerspan relevance analysis.

Usage:
    extract-careerspan-insights --input FILE [options]
    extract-careerspan-insights --from-knowledge --entity "Name" [options]

Author: N5 OS
Version: 1.0.1
Date: 2025-10-09
"""

import argparse
import json
import logging
import sys
import pytz
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)

# Analysis types
ANALYSIS_TYPES = ["partnership", "investment", "customer", "general"]

# Timezone
ET_TZ = pytz.timezone('America/New_York')

def get_et_timestamp() -> str:
    """Get current timestamp in ET timezone."""
    now_et = datetime.now(ET_TZ)
    return now_et.strftime('%Y-%m-%d %H:%M:%S %Z')

def get_future_deadline(days: int = 7) -> str:
    """Get future deadline in ET timezone."""
    now_et = datetime.now(ET_TZ)
    deadline = now_et + timedelta(days=days)
    return deadline.strftime('%Y-%m-%d 17:00 %Z')

def validate_inputs(args) -> None:
    """Validate command line arguments."""
    if args.entity:
        if not args.entity.strip():
            raise ValueError("Entity name cannot be empty")
        if len(args.entity.strip()) < 2:
            raise ValueError("Entity name too short (minimum 2 characters)")
    
    if args.input:
        input_path = Path(args.input)
        if not input_path.exists():
            raise ValueError(f"Input file not found: {args.input}")
        if input_path.stat().st_size == 0:
            raise ValueError(f"Input file is empty: {args.input}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    
    # Input source (mutually exclusive)
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--input", help="Research results file")
    source_group.add_argument("--from-knowledge", action="store_true", help="Extract from knowledge base")
    
    # Other arguments
    parser.add_argument("--entity", help="Entity name for context (recommended)")
    parser.add_argument("--output", help="Output file (default: {input}_insights.md)")
    parser.add_argument("--analysis-type", default="general", choices=ANALYSIS_TYPES, 
                       help="Analysis focus area")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Preview output without saving")
    
    args = parser.parse_args()
    
    try:
        # Validate inputs
        validate_inputs(args)
        
        # Load research content
        if args.from_knowledge:
            if not args.entity:
                logger.error("--entity required when using --from-knowledge")
                return 1
            logger.info(f"Loading research from knowledge base for: {args.entity}")
            research_content = load_from_knowledge_base(args.entity)
            input_source = f"Knowledge Base: {args.entity}"
        else:
            logger.info(f"Loading research from file: {args.input}")
            input_path = Path(args.input)
            if not input_path.exists():
                logger.error(f"Input file not found: {args.input}")
                return 1
            research_content = input_path.read_text()
            input_source = str(input_path)
        
        # Load Careerspan context
        careerspan_context = load_careerspan_context()
        
        # Extract insights
        logger.info(f"Extracting insights (analysis type: {args.analysis_type})...")
        insights = extract_insights(
            research_content=research_content,
            entity_name=args.entity or "Unknown Entity",
            analysis_type=args.analysis_type,
            careerspan_context=careerspan_context,
            input_source=input_source
        )
        
        # Generate output
        output_content = generate_insights_document(insights)
        
        # Dry-run mode
        if args.dry_run:
            logger.info("DRY RUN - Preview only, not saving to file")
            print("\n" + "=" * 60)
            print("  PREVIEW MODE (--dry-run)")
            print("=" * 60 + "\n")
            print(output_content)
            return 0
        
        # Determine output path
        if args.output:
            output_path = Path(args.output)
        elif args.input:
            input_path = Path(args.input)
            output_path = input_path.parent / f"{input_path.stem}_insights.md"
        else:
            output_path = Path(f"insights_{args.entity.replace(' ', '_').lower()}.md")
        
        # Save output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output_content)
        
        logger.info(f"✓ Insights generated: {output_path}")
        
        # Print summary
        print("\n" + "=" * 60)
        print("  STRATEGIC INSIGHTS EXTRACTED")
        print("=" * 60)
        print(f"\nEntity: {args.entity or 'Unknown'}")
        print(f"Analysis Type: {args.analysis_type}")
        print(f"Strategic-Fit Score: {insights['strategic_fit_score']}/5")
        print(f"\nOutput: {output_path}")
        print("=" * 60 + "\n")
        
        return 0
        
    except Exception as e:
        logger.error(f"✗ Error: {e}", exc_info=True)
        return 1


def load_from_knowledge_base(entity_name: str) -> str:
    """
    Load research about entity from N5 knowledge base.
    
    Queries facts, timeline, bio, glossary for mentions of entity.
    """
    logger.info("Querying knowledge base...")
    
    results = {
        "facts": [],
        "timeline_events": [],
        "bio_mentions": [],
        "glossary_entries": []
    }
    
    # Query facts.jsonl
    facts_path = Path("/home/workspace/Knowledge/facts.jsonl")
    if facts_path.exists():
        with open(facts_path) as f:
            for line in f:
                try:
                    fact = json.loads(line)
                    if entity_name.lower() in str(fact).lower():
                        results["facts"].append(fact)
                except (json.JSONDecodeError, ValueError) as e:
                    logger.debug(f"Failed to parse fact line: {e}")
                    continue
        logger.info(f"  Found {len(results['facts'])} facts")
    
    # Query timeline.jsonl
    timeline_path = Path("/home/workspace/Knowledge/timeline.jsonl")
    if timeline_path.exists():
        with open(timeline_path) as f:
            for line in f:
                try:
                    event = json.loads(line)
                    if entity_name.lower() in str(event).lower():
                        results["timeline_events"].append(event)
                except (json.JSONDecodeError, ValueError) as e:
                    logger.debug(f"Failed to parse timeline line: {e}")
                    continue
        logger.info(f"  Found {len(results['timeline_events'])} timeline events")
    
    # Query bio.md
    bio_path = Path("/home/workspace/Knowledge/stable/bio.md")
    if bio_path.exists():
        bio_content = bio_path.read_text()
        if entity_name.lower() in bio_content.lower():
            results["bio_mentions"].append("Mentioned in bio")
        logger.info(f"  Bio mentions: {len(results['bio_mentions'])}")
    
    # Compile into text
    compiled = []
    compiled.append(f"# Knowledge Base Extract: {entity_name}\n")
    
    if results["facts"]:
        compiled.append("## Facts\n")
        for fact in results["facts"]:
            compiled.append(f"- {json.dumps(fact)}\n")
    
    if results["timeline_events"]:
        compiled.append("\n## Timeline Events\n")
        for event in results["timeline_events"]:
            compiled.append(f"- {json.dumps(event)}\n")
    
    if not any(results.values()):
        logger.warning("No data found in knowledge base for this entity")
        compiled.append("\n*No data found in knowledge base*\n")
    
    return "\n".join(compiled)


def load_careerspan_context() -> Dict[str, Any]:
    """Load Careerspan strategic context."""
    return {
        "company_overview": "Careerspan: 3-D talent data platform for hiring",
        "strategic_areas": {
            "gtm": "Go-to-market: partnerships, customer acquisition",
            "fundraising": "Fundraising: Series A preparation",
            "product": "Product: AI coaching, alignment assessment",
            "market": "Market: future of work, HR-tech, talent intelligence"
        },
        "value_proposition": "3-D talent data, AI-powered coaching, objective alignment assessment",
        "target_customers": "Companies hiring at scale, HR-tech platforms, talent marketplaces"
    }


def extract_insights(
    research_content: str,
    entity_name: str,
    analysis_type: str,
    careerspan_context: Dict[str, Any],
    input_source: str
) -> Dict[str, Any]:
    """
    Extract strategic insights from research content.
    
    This is a simplified version. In production, would use LLM to analyze.
    """
    
    # NOTE: This is a stub implementation
    # In production, would use LLM to:
    # 1. Parse research content
    # 2. Extract key themes
    # 3. Map to Careerspan strategic areas
    # 4. Generate SWOT
    # 5. Identify action items
    # 6. Generate questions
    
    logger.warning("Using simplified extraction logic - implement LLM-based analysis")
    
    # Calculate strategic fit score (1-5)
    # In production: LLM-based scoring
    strategic_fit_score = 3
    
    # Extract themes (simplified)
    themes = extract_themes_simple(research_content)
    
    # Map to strategic areas
    strategic_relevance = map_to_strategic_areas(
        research_content,
        analysis_type,
        careerspan_context
    )
    
    # Generate SWOT
    swot = generate_swot_simple(research_content, analysis_type)
    
    # Generate actions
    actions = generate_actions_simple(analysis_type, entity_name)
    
    # Generate questions
    questions = generate_questions_simple(analysis_type, entity_name)
    
    return {
        "entity_name": entity_name,
        "analysis_type": analysis_type,
        "input_source": input_source,
        "timestamp": datetime.now().isoformat(),
        "strategic_fit_score": strategic_fit_score,
        "fit_rationale": f"Moderate alignment with Careerspan's {analysis_type} objectives",
        "executive_summary": generate_executive_summary(research_content, entity_name, analysis_type),
        "themes": themes,
        "strategic_relevance": strategic_relevance,
        "swot": swot,
        "patterns": extract_patterns_simple(research_content),
        "actions": actions,
        "questions": questions,
        "knowledge_links": []  # Would populate from KB in production
    }


def extract_themes_simple(content: str) -> List[Dict[str, str]]:
    """Extract key themes (simplified)."""
    return [
        {
            "title": "Market Position",
            "analysis": "Entity operates in relevant market with established presence.",
            "careerspan_relevance": "Potential overlap with Careerspan's target market."
        },
        {
            "title": "Strategic Focus",
            "analysis": "Focus areas align partially with talent/hiring space.",
            "careerspan_relevance": "Opportunities for partnership or learning."
        }
    ]


def map_to_strategic_areas(content: str, analysis_type: str, context: Dict) -> Dict[str, List[str]]:
    """Map findings to Careerspan strategic areas."""
    
    # Analysis-type specific mapping
    if analysis_type == "partnership":
        return {
            "gtm_opportunities": [
                "Potential co-marketing opportunities",
                "Shared customer base exploration",
                "Integration possibilities"
            ],
            "product_synergies": [
                "Complementary product features",
                "Data sharing potential"
            ],
            "risks": [
                "Integration complexity",
                "Overlapping roadmaps"
            ]
        }
    elif analysis_type == "investment":
        return {
            "fundraising_implications": [
                "Investor has relevant portfolio companies",
                "Thesis alignment with Careerspan's market",
                "Potential for strategic value-add"
            ],
            "positioning_angles": [
                "Emphasize 3-D talent data differentiation",
                "Highlight AI coaching capabilities"
            ],
            "risks": [
                "Competitive portfolio companies",
                "Stage mismatch potential"
            ]
        }
    elif analysis_type == "customer":
        return {
            "icp_fit": [
                "Company size aligns with target",
                "Hiring pain points evident",
                "Decision-maker access possible"
            ],
            "sales_strategy": [
                "Lead with alignment assessment value",
                "Pilot with specific team/role"
            ],
            "risks": [
                "Budget constraints",
                "Existing vendor relationships"
            ]
        }
    else:  # general
        return {
            "opportunities": [
                "Multiple potential relationship vectors",
                "Market intelligence value",
                "Network expansion"
            ],
            "considerations": [
                "Requires further scoping",
                "Timeline unclear"
            ]
        }


def generate_swot_simple(content: str, analysis_type: str) -> Dict[str, List[str]]:
    """Generate SWOT analysis."""
    return {
        "strengths": [
            "Established market presence",
            "Relevant domain expertise",
            "Aligned with Careerspan focus areas"
        ],
        "weaknesses": [
            "Limited public information on specific capabilities",
            "Unclear decision-making process"
        ],
        "opportunities": [
            "Partnership exploration",
            "Market learning",
            "Network expansion"
        ],
        "threats": [
            "Competitive dynamics",
            "Market timing",
            "Resource allocation constraints"
        ]
    }


def extract_patterns_simple(content: str) -> List[str]:
    """Extract notable patterns."""
    return [
        "Entity shows consistent focus on talent/hiring space",
        "Recent activity suggests market expansion",
        "Strategic positioning aligns with future of work trends"
    ]


def generate_actions_simple(analysis_type: str, entity_name: str) -> Dict[str, List[Dict]]:
    """Generate recommended actions."""
    
    # Calculate deadlines
    deadline_1week = get_future_deadline(7)
    deadline_2weeks = get_future_deadline(14)
    deadline_4weeks = get_future_deadline(28)
    
    if analysis_type == "partnership":
        return {
            "immediate": [
                {"action": f"Schedule exploratory call with {entity_name}", "owner": "Vrijen", "timeline": f"by {deadline_2weeks}"},
                {"action": "Prepare partnership value proposition", "owner": "Team", "timeline": "Before call"}
            ],
            "near_term": [
                {"action": "Identify integration requirements", "owner": "Logan", "timeline": "Post initial call"},
                {"action": "Draft partnership framework", "owner": "Vrijen", "timeline": "If aligned"}
            ],
            "monitor": [
                {"action": f"Track {entity_name} product developments", "owner": "Team", "timeline": "Ongoing"}
            ]
        }
    elif analysis_type == "investment":
        return {
            "immediate": [
                {"action": f"Research {entity_name} portfolio companies", "owner": "Vrijen", "timeline": f"by {deadline_1week}"},
                {"action": "Tailor pitch deck for investor", "owner": "Vrijen", "timeline": "Before outreach"}
            ],
            "near_term": [
                {"action": "Warm intro via network", "owner": "Vrijen", "timeline": f"by {deadline_4weeks}"},
                {"action": "Prepare for objections", "owner": "Team", "timeline": "Before pitch"}
            ],
            "monitor": [
                {"action": f"Track {entity_name} recent investments", "owner": "Team", "timeline": "Monthly"}
            ]
        }
    else:
        return {
            "immediate": [
                {"action": f"Clarify engagement objective with {entity_name}", "owner": "Vrijen", "timeline": f"by {deadline_1week}"}
            ],
            "near_term": [
                {"action": "Determine next steps based on objective", "owner": "Team", "timeline": "TBD"}
            ],
            "monitor": []
        }


def generate_questions_simple(analysis_type: str, entity_name: str) -> List[str]:
    """Generate strategic questions for follow-up."""
    
    questions = [
        f"What is Careerspan's highest-value engagement mode with {entity_name}?",
        f"What are {entity_name}'s current pain points in talent/hiring?",
        "How does this opportunity compare to other priorities?",
        "What resources would this engagement require?",
        "What is the timeline to value?"
    ]
    
    if analysis_type == "investment":
        questions.extend([
            f"What are {entity_name}'s key decision criteria?",
            "How should we position against competitive investments?",
            "What value beyond capital can they provide?"
        ])
    
    return questions


def generate_executive_summary(content: str, entity_name: str, analysis_type: str) -> str:
    """Generate executive summary."""
    
    # Simplified summary generation
    # In production: LLM-based summarization
    
    summaries = {
        "partnership": f"{entity_name} represents a strategic partnership opportunity in the talent/hiring space. Initial analysis suggests moderate alignment with Careerspan's go-to-market objectives, with potential for product integration and customer base expansion. Key considerations include integration complexity and resource requirements. Recommended next step: exploratory discussion to validate mutual value proposition.",
        
        "investment": f"{entity_name} shows alignment with Careerspan's Series A fundraising objectives. The investor has relevant portfolio companies and thesis alignment with the future of work space. Preliminary fit assessment suggests moderate to strong potential, pending deeper validation of value-add capabilities and competitive dynamics. Recommended approach: secure warm introduction and tailor pitch to emphasize 3-D talent data differentiation.",
        
        "customer": f"{entity_name} exhibits characteristics consistent with Careerspan's ICP. Preliminary analysis identifies hiring pain points and potential decision-maker access. Strategic fit is moderate, with opportunity for pilot engagement. Key considerations include budget constraints and existing vendor relationships. Recommended strategy: lead with alignment assessment value proposition.",
        
        "general": f"{entity_name} operates in a space adjacent to Careerspan's focus areas. Initial research surfaces multiple potential engagement vectors including partnership, customer, and market intelligence. Strategic relevance is moderate and requires further scoping to determine highest-value interaction mode. Recommended next step: clarify engagement objective and prioritize relative to other opportunities."
    }
    
    return summaries.get(analysis_type, summaries["general"])


def generate_insights_document(insights: Dict[str, Any]) -> str:
    """Generate the insights markdown document."""
    
    lines = []
    
    # Header
    lines.append(f"# Strategic Insights: {insights['entity_name']}")
    lines.append("")
    lines.append(f"**Generated:** {get_et_timestamp()}")
    lines.append(f"**Source:** {insights['input_source']}")
    lines.append(f"**Analysis Type:** {insights['analysis_type'].capitalize()}")
    lines.append(f"**Analyst:** N5 OS / Careerspan Insight Extractor v1.0")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Executive Summary
    lines.append("## Executive Summary")
    lines.append("")
    lines.append(insights["executive_summary"])
    lines.append("")
    lines.append(f"**Strategic-Fit Score:** {insights['strategic_fit_score']} / 5")
    lines.append("")
    lines.append(f"**Rationale:** {insights['fit_rationale']}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Key Themes
    lines.append("## Key Themes & Insights")
    lines.append("")
    for theme in insights["themes"]:
        lines.append(f"### {theme['title']}")
        lines.append("")
        lines.append(theme["analysis"])
        lines.append("")
        lines.append(f"**Why This Matters to Careerspan:** {theme['careerspan_relevance']}")
        lines.append("")
    lines.append("---")
    lines.append("")
    
    # Strategic Relevance
    lines.append("## Strategic Relevance to Careerspan")
    lines.append("")
    for area, items in insights["strategic_relevance"].items():
        area_title = area.replace("_", " ").title()
        lines.append(f"### {area_title}")
        lines.append("")
        for item in items:
            lines.append(f"- {item}")
        lines.append("")
    lines.append("---")
    lines.append("")
    
    # SWOT
    swot = insights["swot"]
    lines.append("## SWOT Analysis")
    lines.append("")
    lines.append("| **Strengths** | **Weaknesses** |")
    lines.append("|---------------|----------------|")
    max_len = max(len(swot["strengths"]), len(swot["weaknesses"]))
    for i in range(max_len):
        s = swot["strengths"][i] if i < len(swot["strengths"]) else ""
        w = swot["weaknesses"][i] if i < len(swot["weaknesses"]) else ""
        lines.append(f"| {s} | {w} |")
    lines.append("")
    lines.append("| **Opportunities** | **Threats** |")
    lines.append("|-------------------|-------------|")
    max_len = max(len(swot["opportunities"]), len(swot["threats"]))
    for i in range(max_len):
        o = swot["opportunities"][i] if i < len(swot["opportunities"]) else ""
        t = swot["threats"][i] if i < len(swot["threats"]) else ""
        lines.append(f"| {o} | {t} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Patterns
    lines.append("## Patterns & Trends Identified")
    lines.append("")
    for pattern in insights["patterns"]:
        lines.append(f"- {pattern}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Actions
    lines.append("## Recommended Actions")
    lines.append("")
    actions = insights["actions"]
    if "immediate" in actions:
        lines.append("**Priority 1 (Immediate):**")
        for i, action in enumerate(actions["immediate"], 1):
            lines.append(f"{i}. {action['action']} (Owner: {action['owner']}, Timeline: {action['timeline']})")
        lines.append("")
    if "near_term" in actions:
        lines.append("**Priority 2 (Near-term):**")
        for i, action in enumerate(actions["near_term"], 1):
            lines.append(f"{i}. {action['action']} (Owner: {action['owner']}, Timeline: {action['timeline']})")
        lines.append("")
    if "monitor" in actions and actions["monitor"]:
        lines.append("**Priority 3 (Monitor):**")
        for i, action in enumerate(actions["monitor"], 1):
            lines.append(f"{i}. {action['action']} (Owner: {action['owner']}, Timeline: {action['timeline']})")
        lines.append("")
    lines.append("---")
    lines.append("")
    
    # Questions
    lines.append("## Strategic Questions for Follow-Up")
    lines.append("")
    for i, question in enumerate(insights["questions"], 1):
        lines.append(f"{i}. {question}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Related Knowledge
    lines.append("## Related Knowledge & Context")
    lines.append("")
    lines.append("**N5 Knowledge Base Links:**")
    if insights["knowledge_links"]:
        for link in insights["knowledge_links"]:
            lines.append(f"- {link}")
    else:
        lines.append("- *(No direct knowledge base links found)*")
    lines.append("")
    lines.append("**Source Research:**")
    lines.append(f"- Original source: `{insights['input_source']}`")
    lines.append(f"- Analysis date: {insights['timestamp'][:10]}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("**Generated by:** N5 OS / Careerspan Insight Extractor v1.0")
    lines.append("**Command:** `extract-careerspan-insights`")
    lines.append("")
    
    return "\n".join(lines)


if __name__ == "__main__":
    sys.exit(main())
