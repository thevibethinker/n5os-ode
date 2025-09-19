#!/usr/bin/env python3
"""
N5 Knowledge Ingest Script

Ingests a chunk of biographical/historical/strategic information about V and Careerspan,
analyzes it with LLM, breaks it down into components, and stores across knowledge reservoirs.

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

from scripts.n5_knowledge_adaptive_suggestions import call_llm_for_suggestions
from scripts.n5_knowledge_adaptive_suggestions_expand import parse_suggestions, validate_and_apply_suggestions


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


def call_deep_research(input_text):
    schema = load_schema()
    instructions = f"""
Analyze the following text about V and Careerspan, break into mutually exclusive, collectively exhaustive components per ingestion standards 'N5/knowledge/ingestion_standards.md'.
Focus on biographical info, recurring characters, company details, strategic/historical context.
Exclude operational, sensitive, unverified data.
Output JSON matching the provided schema.
Input:
{input_text}
"""
    # For now, return a template structure - this will be replaced with actual deep_research call
    # when the script is invoked through the AI assistant
    print("Note: deep_research analysis would be performed here")
    return {
        "prefs": {},
        "bio": {"summary": "Analysis pending - run through AI assistant"},
        "timeline": [],
        "glossary": [],
        "sources": [],
        "company": {},
        "facts": [],
        "suggestions": []
    }


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
    suggestions = parse_suggestions(suggestion_text)
    if not suggestions:
        print("No suggestions parsed.")
        return

    print(f"Parsed {len(suggestions)} suggestions:")
    for s in suggestions:
        print(f"- {s['type']}: {s['name']} - {s['rationale']}")

    confirm = input("Apply these schema updates? (yes/no): ")
    if confirm.lower() in ['yes', 'y']:
        validate_and_apply_suggestions(suggestions, schema)
    else:
        print("Schema update aborted by user.")


async def main_async(dry_run=False, input_text=None):
    if not input_text:
        print("Error: No input text provided.")
        return

    print(f"Processing {len(input_text)} characters of input...")

    # Analyze with LLM
    plan = call_deep_research(input_text)
    plan = validate_plan(plan)

    if not dry_run:
        apply_plan(plan, dry_run=dry_run)

    await run_adaptive_suggestions()

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


if __name__ == "__main__":
    main()
