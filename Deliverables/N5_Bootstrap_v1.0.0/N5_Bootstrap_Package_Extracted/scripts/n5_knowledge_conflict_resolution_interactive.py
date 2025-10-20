#!/usr/bin/env python3
"""
Interactive Conflict Resolution Framework for N5 Knowledge Ingestion.

Parses LLM natural language conflict summaries into structured form.
Provides CLI-based resolution flows.
Supports merging, rejecting, or flagging knowledge facts.
"""

import asyncio
import json
import re
from pathlib import Path
from typing import List, Dict, Any

from functions import use_app_openai_chat_completion

FACTS_FILE = Path(__file__).resolve().parents[1] / "knowledge" / "facts.jsonl"


def load_facts() -> List[Dict[str, Any]]:
    if not FACTS_FILE.exists():
        return []
    with open(FACTS_FILE, "r") as f:
        return [json.loads(line.strip()) for line in f if line.strip()]


def prompt_llm_for_conflict_resolution(facts_text: str) -> str:
    prompt = f"""
You are a knowledge assistant.
Analyze the following facts and identify conflicts in detail.
Format your response as JSON array of conflict objects, each with:
- id
- subject
- predicate
- conflicting_objects (array)
- similarity_score (0-1, higher means more similar)
- resolution_recommendations (array of strings)
Facts:
{facts_text}
"""
    # This will be called asynchronously outside
    return prompt


async def call_llm(prompt: str) -> str:
    response = await use_app_openai_chat_completion(
        tool_name="chat-completion",
        configured_props={
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        }
    )
    return response.get("choices", [{}])[0].get("message", {}).get("content", "")


def parse_conflicts(llm_json_str: str) -> List[Dict[str, Any]]:
    try:
        return json.loads(llm_json_str)
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        # Fallback regex extraction
        matches = re.findall(r'\[\{.*?\}\]', llm_json_str, re.DOTALL)
        for idx, match in enumerate(matches):
            try:
                parsed = json.loads(match)
                print(f"Parsed JSON conflict array at fallback index {idx}")
                return parsed
            except json.JSONDecodeError as e2:
                print(f"Fallback JSON decode error at index {idx}: {e2}")
        print("Failed to parse any JSON array in LLM output.")
        print(f"LLM output was: {llm_json_str[:1000]}...")  # Truncated
        return []


def interactive_resolve(conflicts: List[Dict[str, Any]], facts: List[Dict[str, Any]]):
    for conflict in conflicts:
        print(f"Conflict ID: {conflict.get('id')}")
        print(f"Subject: {conflict.get('subject')}")
        print(f"Predicate: {conflict.get('predicate')}")
        print(f"Conflicting Objects: {conflict.get('conflicting_objects')}")
        print(f"Similarity Score: {conflict.get('similarity_score')}")
        print("Resolution Suggestions:")
        for rec in conflict.get('resolution_recommendations', []):
            print(f"  - {rec}")

        # Simple CLI choice stub
        choice = input("Choose resolution action (merge/reject/skip): ").strip().lower()
        if choice == "merge":
            print("Merging conflict facts (not implemented yet).")
            # Placeholder: merge logic here
        elif choice == "reject":
            print("Rejecting conflict facts (not implemented yet).")
            # Placeholder: reject logic here
        elif choice == "skip":
            print("Skipping conflict.")
        else:
            print("Invalid choice, skipping.")
        print("---")


def main():
    facts = load_facts()
    if not facts:
        print("No facts found.")
        return
    facts_text = json.dumps(facts, indent=2)

    prompt = prompt_llm_for_conflict_resolution(facts_text)
    llm_output = asyncio.run(call_llm(prompt))

    conflicts = parse_conflicts(llm_output)

    if not conflicts:
        print("No structured conflicts parsed from LLM output.")
        print("LLM Output was:")
        print(llm_output)
        return

    interactive_resolve(conflicts, facts)


if __name__ == '__main__':
    main()
