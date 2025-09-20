#!/usr/bin/env python3
"""
SourceStack API puller
Reads SOURCESTACK_KEY from env file, queries /jobs, returns list of job dicts
"""

import os, json, aiohttp, asyncio, logging, datetime
from typing import List, Dict, Optional

API_URL = "https://api.sourcestack.ai/jobs"

async def fetch_jobs(params: Dict[str, str]) -> List[Dict]:
    key = os.getenv("SOURCESTACK_KEY")
    if not key:
        raise RuntimeError("SOURCESTACK_KEY missing in environment")

    headers = {"Authorization": f"Bearer {key}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(API_URL, params=params, headers=headers, timeout=30) as resp:
            resp.raise_for_status()
            data = await resp.json()
            return data.get("jobs", [])

async def main():
    params = {"title": "Software Engineer", "days": "1", "limit": "10"}
    jobs = await fetch_jobs(params)
    print(json.dumps(jobs[:3], indent=2))

if __name__ == "__main__":
    asyncio.run(main())