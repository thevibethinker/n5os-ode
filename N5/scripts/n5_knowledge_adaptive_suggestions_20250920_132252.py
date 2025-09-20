import argparse

#!/usr/bin/env python3
"""
Adaptive Suggestion Engine for N5 Knowledge Ingestion System.

Detects new knowledge reservoirs or subcategories needed based on ingested data patterns.
Suggests schema expansions with rationale and confidence.
"""

import asyncio
import json
from pathlib import Path

from functions import use_app_openai_chat_completion

SCHEMA_FILE = Path(__file__).resolve().parents[1] / "schemas" / "ingest.plan.schema.json"

async def call_llm_for_suggestions(input_text: str) -> str:
    prompt = f"""
You are a knowledge management AI.
Analyze the following ingested knowledge data.
Identify any gaps, new reservoirs, or subcategories that should be created to organize information better.
For each suggestion provide:
- type (new_reservoir or new_subcategory)
- name
- description
- rationale

Input data:
{input_text}
"""
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


def load_schema():
    with open(SCHEMA_FILE, "r") as f:
        return json.load(f)

async def analyze_and_suggest():
    schema = load_schema()
    schema_text = json.dumps(schema, indent=2)

    print("Requesting adaptive knowledge reservoir suggestions from LLM...")
    suggestion_text = await call_llm_for_suggestions(schema_text)

    print("Suggestions received:\n")
    print(suggestion_text)
    # Future: parse suggestions JSON, integrate with ingestion pipeline


def main():
    asyncio.run(analyze_and_suggest())



parser = argparse.ArgumentParser()
parser.add_argument('--dry-run', action='store_true', help='Run in dry-run mode')
args = parser.parse_args()

if __name__ == '__main__':
    main()
