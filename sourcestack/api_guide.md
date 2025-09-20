# SourceStack API Usage Guide

## Lessons Learned

- **Authentication**: Use the `X-API-KEY` header with your API key.  
- **Base URL**: All endpoints start with `https://sourcestack-api.com`.  
- **Simple Queries**: Use GET requests for basic params (e.g., `/jobs?name=Engineer&limit=10`).  
- **Advanced Filtering**: Use POST with JSON body `{"filters": [...], "limit": n}`.  
  - Filters are arrays of objects: `{"field": "job_name", "operator": "CONTAINS_ANY", "value": "product manag"}`.  
  - Common operators: `CONTAINS_ANY`, `GREATER_THAN`, `LESS_THAN`, etc.  
  - For jobs: key fields include `job_name`, `city`, `first_indexed` (e.g., "LAST_7D").  
- **Request Method**: POST works reliably for filtered queries; curl had parsing issues, so use Python (aiohttp) for complex requests.  
- **Response**: JSON with job data including `post_url` for actual postings.  
- **Limits**: Set `limit` to control results (e.g., 5-25); API handles pagination if needed.  
- **Error Handling**: Watch for "Forbidden" (key issues) or "429" (rate limits); implement retries.  

## Example Request (Python with aiohttp)

```python
import aiohttp
import asyncio

async def fetch_jobs():
    key = "YOUR_API_KEY"
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
            if resp.status == 200:
                jobs = await resp.json()
                for job in jobs:
                    print(job["job_name"], job["post_url"])
            else:
                print(f"Error: {resp.status}")

asyncio.run(fetch_jobs())
```

## Next Steps

- For production: Add retries, logging, and CSV export.  
- Monitor credits via response headers.  
- Expand filters for more precise searches (e.g., company, salary).  
- Schedule automated runs if needed.