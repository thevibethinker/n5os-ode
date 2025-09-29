import aiohttp
import asyncio
import json

async def test_api():
    key = "1aV6WGooxh4vK8k3RcY6j83xHiTzxzCx62Z8TFcm"
    url = "https://sourcestack-api.com/jobs"
    headers = {"X-API-KEY": key}
    data = {
        "filters": [
            {"field": "job_name", "operator": "CONTAINS_ANY", "value": "product manag"},
            {"field": "city", "operator": "CONTAINS_ANY", "value": "New York"},
            {"field": "first_indexed", "operator": "GREATER_THAN", "value": "LAST_3D"}
        ],
        "limit": 5
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as resp:
            print(f"Status: {resp.status}")
            text = await resp.text()
            print(text)

asyncio.run(test_api())