#!/usr/bin/env python3
"""
Batch process meeting routing via /zo/ask API.
Reads prompts from JSONL, calls LLM for classification, writes B36 files.
"""
import asyncio
import aiohttp
import json
import os
from pathlib import Path
from datetime import datetime
import argparse

CONCURRENT_LIMIT = 20
API_URL = "https://api.zo.computer/zo/ask"

async def classify_meeting(session, semaphore, prompt_data: dict) -> dict:
    """Call /zo/ask to classify a single meeting."""
    async with semaphore:
        meeting_path = prompt_data['meeting_path']
        prompt = prompt_data['prompt']
        
        try:
            async with session.post(
                API_URL,
                headers={
                    "authorization": os.environ["ZO_CLIENT_IDENTITY_TOKEN"],
                    "content-type": "application/json"
                },
                json={
                    "input": f"{prompt}\n\nRespond with ONLY valid JSON, no markdown.",
                }
            ) as resp:
                result = await resp.json()
                output = result.get("output", "")
                
                # Parse JSON from response
                try:
                    # Handle potential markdown wrapping
                    if "```json" in output:
                        output = output.split("```json")[1].split("```")[0]
                    elif "```" in output:
                        output = output.split("```")[1].split("```")[0]
                    classification = json.loads(output.strip())
                except json.JSONDecodeError:
                    classification = {"error": "Failed to parse JSON", "raw": output[:500]}
                
                return {
                    "meeting_path": meeting_path,
                    "meeting_name": prompt_data.get('meeting_name'),
                    "classification": classification,
                    "status": "success" if "error" not in classification else "parse_error"
                }
        except Exception as e:
            return {
                "meeting_path": meeting_path,
                "meeting_name": prompt_data.get('meeting_name'),
                "classification": {"error": str(e)},
                "status": "api_error"
            }

async def process_batch(prompts: list[dict], output_file: str) -> list[dict]:
    """Process all prompts with concurrency limit."""
    semaphore = asyncio.Semaphore(CONCURRENT_LIMIT)
    results = []
    
    async with aiohttp.ClientSession() as session:
        tasks = [classify_meeting(session, semaphore, p) for p in prompts]
        
        for i, coro in enumerate(asyncio.as_completed(tasks)):
            result = await coro
            results.append(result)
            if (i + 1) % 10 == 0:
                print(f"Processed {i + 1}/{len(prompts)} meetings...")
    
    # Write results
    with open(output_file, 'w') as f:
        for r in results:
            f.write(json.dumps(r) + '\n')
    
    return results

def write_b36_files(results: list[dict]) -> tuple[int, int]:
    """Write B36_DEAL_ROUTING.json and .md files for each meeting."""
    written = 0
    skipped = 0
    
    for r in results:
        if r['status'] != 'success':
            skipped += 1
            continue
            
        meeting_path = Path(r['meeting_path'])
        classification = r['classification']
        
        if not meeting_path.exists():
            skipped += 1
            continue
        
        # Write JSON
        json_path = meeting_path / 'B36_DEAL_ROUTING.json'
        with open(json_path, 'w') as f:
            json.dump(classification, f, indent=2)
        
        # Write MD
        md_path = meeting_path / 'B36_DEAL_ROUTING.md'
        companies = classification.get('companies_mentioned', [])
        # Handle both list of strings and list of dicts
        if isinstance(companies, list) and companies:
            if isinstance(companies[0], dict):
                companies_str = ', '.join(c.get('name', str(c)) for c in companies)
            else:
                companies_str = ', '.join(str(c) for c in companies)
        else:
            companies_str = str(companies) if companies else ''
        
        md_content = f"""---
created: {datetime.now().strftime('%Y-%m-%d')}
last_edited: {datetime.now().strftime('%Y-%m-%d')}
version: 1.0
provenance: batch_meeting_router
block: B36
---

# B36: Deal Routing Classification

**Zo Relevance:** {classification.get('zo_relevance_score', 'N/A')}  
**Careerspan Relevance:** {classification.get('careerspan_relevance_score', 'N/A')}

## Summary
{classification.get('summary', 'No summary available')}

## Zo Analysis
{classification.get('zo_reasoning', 'N/A')}

## Careerspan Analysis
{classification.get('careerspan_reasoning', 'N/A')}

## Companies Mentioned
{companies_str if companies_str else 'None identified'}

## Deal Match
{classification.get('deal_match', 'None')}
"""
        with open(md_path, 'w') as f:
            f.write(md_content)
        
        written += 1
    
    return written, skipped

def main():
    parser = argparse.ArgumentParser(description='Batch process meeting routing via /zo/ask API')
    parser.add_argument('--prompts', required=True, help='Input prompts JSONL file')
    parser.add_argument('--output', default='/tmp/routing_results.jsonl', help='Output results JSONL')
    parser.add_argument('--write-b36', action='store_true', help='Write B36 files after classification')
    parser.add_argument('--limit', type=int, help='Limit number of prompts to process')
    args = parser.parse_args()
    
    # Load prompts
    prompts = []
    with open(args.prompts) as f:
        for line in f:
            if line.strip():
                prompts.append(json.loads(line))
    
    if args.limit:
        prompts = prompts[:args.limit]
    
    print(f"Processing {len(prompts)} meetings with {CONCURRENT_LIMIT} concurrent requests...")
    
    # Run async processing
    results = asyncio.run(process_batch(prompts, args.output))
    
    # Stats
    success = sum(1 for r in results if r['status'] == 'success')
    errors = len(results) - success
    print(f"\nClassification complete: {success} success, {errors} errors")
    print(f"Results saved to: {args.output}")
    
    if args.write_b36:
        written, skipped = write_b36_files(results)
        print(f"B36 files written: {written}, skipped: {skipped}")

if __name__ == '__main__':
    main()
