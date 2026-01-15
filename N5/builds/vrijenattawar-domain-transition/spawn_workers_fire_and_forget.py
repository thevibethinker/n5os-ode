#!/usr/bin/env python3
"""Spawn project workers via /zo/ask, write status to file, then exit quickly."""
import asyncio
import json
import os
from pathlib import Path

import aiohttp

RESULTS_FILE = Path(__file__).resolve().parent / "spawn_results.jsonl"
WORKERS = [
    {
        "id": "D-website-design",
        "assignment": Path(__file__).resolve().parent
        / "workers"
        / "D-website-design.md",
        "description": "Landing page design using Frontend Design prompt and NYSKI inspiration",
    },
    {
        "id": "E-dns-setup",
        "assignment": Path(__file__).resolve().parent
        / "workers"
        / "E-dns-setup.md",
        "description": "DNS guidance for vrijenattawar.com",
    },
]

async def spawn_worker(session, worker):
    try:
        assignment_text = worker["assignment"].read_text()
        payload = {
            "input": (
                f"You are now executing worker {worker['id']} for project "
                "vrijenattawar-domain-transition. Follow the instructions below and "
                "report completion clearly.\n\n" + assignment_text
            )
        }
        timeout = aiohttp.ClientTimeout(total=600)
        async with session.post(
            "https://api.zo.computer/zo/ask",
            headers={
                "authorization": os.environ["ZO_CLIENT_IDENTITY_TOKEN"],
                "content-type": "application/json",
            },
            json=payload,
            timeout=timeout,
        ) as resp:
            result = await resp.json()
            return {
                "worker_id": worker["id"],
                "status": "spawned",
                "conversation_id": result.get("conversation_id"),
                "output_preview": result.get("output", "")[:1000],
                "description": worker["description"],
            }
    except Exception as exc:
        return {
            "worker_id": worker["id"],
            "status": "error",
            "error": str(exc),
            "description": worker["description"],
        }

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [spawn_worker(session, w) for w in WORKERS]
        results = await asyncio.gather(*tasks)
    with open(RESULTS_FILE, "w") as fh:
        for item in results:
            fh.write(json.dumps(item) + "\n")
    print(f"Wrote spawn results to {RESULTS_FILE}")

if __name__ == "__main__":
    asyncio.run(main())


