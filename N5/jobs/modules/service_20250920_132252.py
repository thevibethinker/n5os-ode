#!/usr/bin/env python3
"""
Persistent Service for Jobs Ingestion
FastAPI app with /sms webhook and /health
"""

from fastapi import FastAPI, Request
import json
from .orchestrate import scrape_flow

app = FastAPI()

@app.post("/sms")
async def sms_handler(request: Request):
    data = await request.json()
    text = data.get("text", "").strip()
    
    if text.startswith("jobs: scrape"):
        companies = text.split("scrape")[1].strip().split()
        result = scrape_flow(companies, [], "jobs-scraped")
        # Placeholder: send SMS back with result
        return {"reply": f"Scraped: {result['new_jobs']} new, {result['rejected']} rejected"}
    
    return {"reply": "Unrecognized command"}

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8899)