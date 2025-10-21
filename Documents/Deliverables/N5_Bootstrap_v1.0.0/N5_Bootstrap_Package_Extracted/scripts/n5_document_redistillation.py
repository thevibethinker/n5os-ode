#!/usr/bin/env python3
"""
Document Redistillation Function for N5 Knowledge System.

Processes accumulated appended documents and rewrites them into a coherent, streamlined master document.
Surfaces contradictions and unresolved issues for interactive resolution.
"""

import asyncio
import json
from pathlib import Path
from functions import use_app_openai_chat_completion

KNOWLEDGE_DIR = Path(__file__).resolve().parents[1] / "knowledge"


async def call_llm_redistillation(text: str) -> str:
    prompt = f"""
You are a knowledgeable assistant tasked with rewriting accumulated documents into a coherent, clear, and streamlined master document.
Preserve all information, surface contradictions explicitly, and suggest resolutions.
Here is the input document content:
{text}
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


def load_documents() -> str:
    contents = []
    for file in KNOWLEDGE_DIR.glob("*.md"):
        contents.append(file.read_text())
    return "\n\n".join(contents)


async def main():
    doc_text = load_documents()
    print("Starting document redistillation...")
    distilled = await call_llm_redistillation(doc_text)
    print("\nRedistilled document content:\n")
    print(distilled)


if __name__ == '__main__':
    asyncio.run(main())
