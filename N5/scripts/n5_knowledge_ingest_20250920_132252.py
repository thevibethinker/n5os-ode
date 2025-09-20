#!/usr/bin/env python3
"""
# Bio Information

## Bio Update 2025-09-19T00:42:49Z

**Vrijen Attawar (CEO/Co-founder):** CEO and co-founder of Careerspan with extensive background in coaching and education that directly informed the platform's coach-first design. Active in company development since late 2022/early 2023. Led the strategic rebrand from The ApplyAI to Careerspan in early 2024 to align with expanded "career companion" vision. Demonstrates conviction-forward, data-anchored communication style with decisive calls-to-action. Personal motivations include frustrations with navigating career changes, acting as informal "career cheerleaders" with Logan Currie, and building an affordable AI-driven solution (priced like a coffee per week) to democratize career guidance. Guided by "candidate-first" philosophy, emphasizing authentic coaching over algorithmic optimization.

**Logan Currie (Co-founder):** Co-founder of Careerspan with complementary background in coaching and education that contributed to the platform's design philosophy. Active in company development since late 2022/early 2023. Partnered with Vrijen Attawar to build Careerspan on the day ChatGPT launched, bringing prior decade of coaching/education experience to inform product development. Shared personal journey of career pivots and informal support, contributing to the vision of an always-available career companion.

Both founders reunited specifically to build Careerspan, leveraging their combined coaching expertise to create an AI-mediated career companion that prioritizes authentic candidate development over superficial resume optimization. Early product (The ApplyAI) focused on application help; rebrand to Careerspan emphasized continuous career management. Mission: Solve informational problems in hiring through rich qualitative data from coaching conversations. 

# N5 Knowledge Ingest Script

Ingests a chunk of biographical/historical/strategic information about V and Careerspan,
analyzes it with direct LLM processing, breaks it down into components, 
and stores across knowledge reservoirs.

Append-only update for facts, glossary, timeline, sources.
Controlled overwrite for bio and company files with future plan to handle merging.
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime, timezone
import uuid
import asyncio

ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE_DIR = ROOT / "knowledge"
FACTS_FILE = KNOWLEDGE_DIR / "facts.jsonl"

# Import direct processing mechanism
from scripts.direct_ingestion_mechanism import DirectKnowledgeIngestion
from scripts.n5_knowledge_conflict_resolution_interactive import load_facts, prompt_llm_for_conflict_resolution, call_llm, parse_conflicts
from scripts.n5_knowledge_adaptive_suggestions import call_llm_for_suggestions

def load_schema():
    with open(ROOT / "schemas" / "ingest.plan.schema.json") as f:
        return json.load(f)

def validate_plan(plan):
    schema = load_schema()
    required_props = schema["properties"]
    for prop in required_props:
        if prop not in plan:
            plan[prop] = [] if "array" in str(required_props[prop]) else {}
    if "suggestions" in plan:
        for suggestion in plan["suggestions"]:
            if "type" not in suggestion or suggestion["type"] not in ["new_reservoir", "new_subcategory"]:
                print(f"Warning: Invalid suggestion: {suggestion}")
    return plan

def process_direct_ingestion(input_text: str, source_name: str = "direct_ingestion") -> dict:
    """
    Process content using direct LLM processing
    This is now the default approach for knowledge ingestion
    """
    print("🔄 Using direct LLM processing (default)")
    
    # Initialize direct processing mechanism
    ingestion = DirectKnowledgeIngestion()
    
    # Process the content directly
    structured_data = ingestion.process_large_document(input_text, source_name)
    
    # Convert to plan format for compatibility
    plan = {
        "prefs": {},
        "bio": {"summary": structured_data.get("bio", {}).get("summary", "")} if structured_data.get("bio") else {"summary": ""},
        "timeline": structured_data.get("timeline", []),
        "glossary": structured_data.get("glossary", []),
        "sources": structured_data.get("sources", []),
        "company": {
            "overview": structured_data.get("company_overview", ""),
            "history": structured_data.get("company_history", ""),
            "strategy": {
                "summary": structured_data.get("strategy_summary", ""),
                "pillars": structured_data.get("strategy_pillars", [])
            },
            "principles": structured_data.get("operating_principles", []),
            "market_rationale": structured_data.get("market_data", "")
        },
        "facts": structured_data.get("facts", []),
        "suggestions": structured_data.get("suggestions", [])
    }
    
    return validate_plan(plan)

def apply_plan(plan, dry_run=False):
    if dry_run:
        print("DRY RUN: Would apply plan:")
        print(json.dumps(plan, indent=2))
        return

    if plan.get("bio", {}).get("summary"):
        bio_file = KNOWLEDGE_DIR / "bio.md"
        with open(bio_file, "a") as f:
            f.write(f"\n# Bio Update {datetime.now(timezone.utc).isoformat()}\n\n{plan['bio']['summary']}\n")
        print(f"Appended to {bio_file}")

    if plan.get("timeline"):
        timeline_file = KNOWLEDGE_DIR / "timeline.md"
        with open(timeline_file, "a") as f:
            for entry in sorted(plan["timeline"], key=lambda x: x["date"]):
                f.write(f"## {entry['date']}: {entry['title']}\n")
                if "description" in entry:
                    f.write(f"{entry['description']}\n\n")
        print(f"Appended {len(plan['timeline'])} entries to {timeline_file}")

    if plan.get("glossary"):
        glossary_file = KNOWLEDGE_DIR / "glossary.md"
        with open(glossary_file, "a") as f:
            for term in plan["glossary"]:
                f.write(f"## {term['term']}\n{term['definition']}\n")
                if "aliases" in term:
                    f.write(f"Aliases: {', '.join(term['aliases'])}\n")
                if "notes" in term:
                    f.write(f"Notes: {term['notes']}\n")
                f.write("\n")
        print(f"Appended {len(plan['glossary'])} terms to {glossary_file}")

    if plan.get("sources"):
        sources_file = KNOWLEDGE_DIR / "sources.md"
        with open(sources_file, "a") as f:
            for source in plan["sources"]:
                f.write(f"- [{source['title']}]({source['url']})\n")
        print(f"Appended {len(plan['sources'])} sources to {sources_file}")

    company = plan.get("company", {})
    if company.get("overview"):
        with open(KNOWLEDGE_DIR / "company" / "overview.md", "w") as f:
            f.write(f"# Overview\n\n{company['overview']}\n")
    if company.get("history"):
        with open(KNOWLEDGE_DIR / "company" / "history.md", "w") as f:
            f.write(f"# History\n\n{company['history']}\n")
    if company.get("strategy"):
        strategy = company["strategy"]
        with open(KNOWLEDGE_DIR / "company" / "strategy.md", "w") as f:
            f.write(f"# Strategy\n\n## Summary\n{strategy.get('summary', '')}\n\n## Pillars\n")
            for pillar in strategy.get("pillars", []):
                f.write(f"- **{pillar['name']}**: {pillar.get('description', '')}\n")
    if company.get("principles"):
        with open(KNOWLEDGE_DIR / "company" / "principles.md", "w") as f:
            f.write("# Principles\n\n" + "\n".join(f"- {p}" for p in company["principles"]) + "\n")
    
    if plan.get("facts"):
        with open(FACTS_FILE, "a") as f:
            for fact in plan["facts"]:
                fact["id"] = str(uuid.uuid4())
                fact["created_at"] = datetime.now(timezone.utc).isoformat()
                f.write(json.dumps(fact) + "\n")
        print(f"Appended {len(plan['facts'])} facts to {FACTS_FILE}")

    if plan.get("suggestions"):
        print("Suggestions for new reservoirs/subcategories:")
        for suggestion in plan["suggestions"]:
            print(f"- {suggestion['type']}: {suggestion['name']} - {suggestion['rationale']}")


async def run_adaptive_suggestions():
    schema = load_schema()
    schema_text = json.dumps(schema, indent=2)
    print("Getting adaptive knowledge reservoir suggestions from LLM...")
    suggestion_text = await call_llm_for_suggestions(schema_text)
    print("Received adaptive suggestions.")
    
    # Parse suggestions (assuming parse_suggestions function exists or implement simple parsing)
    suggestions = parse_suggestions_from_text(suggestion_text)
    
    if not suggestions:
        print("No valid suggestions parsed.")
        return
    
    print(f"Parsed {len(suggestions)} suggestions:")
    for s in suggestions:
        print(f"- {s['type']}: {s['name']} - {s['rationale']}")
    
    # Automatically apply if confidence > threshold
    applied = []
    for suggestion in suggestions:
        if suggestion.get('confidence', 0) > 0.7:  # Example threshold
            applied.append(suggestion)
            print(f"Auto-applying: {suggestion['type']} - {suggestion['name']}")
        else:
            print(f"Skipping low-confidence suggestion: {suggestion['type']} - {suggestion['name']}")
    
    if applied:
        validate_and_apply_suggestions(applied, schema)
    else:
        print("No suggestions met auto-apply threshold.")

async def run_conflict_resolution():
    facts = load_facts()
    if not facts:
        print("No facts to check for conflicts.")
        return
    
    print("Checking for conflicts in knowledge facts...")
    facts_text = json.dumps(facts, indent=2)
    prompt = prompt_llm_for_conflict_resolution(facts_text)
    llm_output = await call_llm(prompt)
    conflicts = parse_conflicts(llm_output)
    
    if not conflicts:
        print("No conflicts detected.")
        return
    
    print(f"Found {len(conflicts)} conflicts:")
    for conflict in conflicts:
        print(f"- {conflict.get('subject')} {conflict.get('predicate')}: {len(conflict.get('conflicting_objects', []))} variants")
    
    # Auto-resolve simple conflicts (e.g., merge if similar)
    resolved = 0
    for conflict in conflicts:
        if conflict.get('similarity_score', 0) > 0.9:
            # Auto-merge
            print(f"Auto-merging high-similarity conflict: {conflict['subject']}")
            resolved += 1
        else:
            print(f"Flagging conflict for manual review: {conflict['subject']}")
    
    print(f"Auto-resolved {resolved} conflicts. Remaining flagged for review.")


async def main_async(dry_run=False, input_text=None):
    if not input_text:
        print("Error: No input text provided.")
        return

    print(f"Processing {len(input_text)} characters of input...")

    # Use direct processing as default
    plan = process_direct_ingestion(input_text)
    plan = validate_plan(plan)

    if not dry_run:
        apply_plan(plan, dry_run=dry_run)

    # Run conflict resolution
    try:
        await run_conflict_resolution()
    except Exception as e:
        print(f"Conflict resolution failed: {e}")

    # Run adaptive suggestions
    try:
        await run_adaptive_suggestions()
    except Exception as e:
        print(f"Adaptive suggestions failed: {e}")

    print("Ingestion complete.")


def main():
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="Ingest knowledge about V and Careerspan")
    parser.add_argument("--input_text", help="Text to ingest")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    args = parser.parse_args()

    input_text = args.input_text
    if not input_text:
        if not sys.stdin.isatty():
            input_text = sys.stdin.read()
        else:
            print("Error: No input text provided. Use --input_text or pipe input.")
            sys.exit(1)

    asyncio.run(main_async(dry_run=args.dry_run, input_text=input_text))


def parse_suggestions_from_text(suggestion_text: str) -> list:
    """Parse LLM suggestions into structured format."""
    # Placeholder: Implement actual parsing logic
    suggestions = []
    lines = suggestion_text.split('\n')
    for line in lines:
        if 'new_reservoir' in line.lower() or 'new_subcategory' in line.lower():
            suggestions.append({
                'type': 'new_reservoir' if 'reservoir' in line.lower() else 'new_subcategory',
                'name': line.strip(),
                'rationale': 'Parsed from LLM output',
                'confidence': 0.8  # Default confidence
            })
    return suggestions

def validate_and_apply_suggestions(suggestions: list, schema: dict):
    """Validate and apply schema suggestions."""
    # Placeholder: Implement schema update logic
    print(f"Applying {len(suggestions)} suggestions to schema...")
    # In real implementation, update the schema file
    pass


if __name__ == "__main__":
    main()
