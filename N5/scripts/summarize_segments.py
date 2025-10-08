#!/usr/bin/env python3
import json
import logging
import os
from datetime import datetime
from typing import List, Dict
import asyncio
import aiohttp

# Setup logging per N5OS (telemetry to dated log)
LOG_DIR = '/home/workspace/Knowledge/logs/Email'
os.makedirs(LOG_DIR, exist_ok=True)
log_file = os.path.join(LOG_DIR, f"{datetime.now().strftime('%Y%m%d')}.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    handlers=[logging.FileHandler(log_file), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# MasterVoiceSchema reference (embedded subset for voice fidelity; full in prefs or companion file)
MASTER_VOICE_SCHEMA = {
    "tone": "reflective",
    "formality": "balanced",
    "ctaRigour": "light",
    "structure": "summary → shared insight → optional next step"
}

async def llm_query(session, prompt: str, api_url: str = "https://api.openai.com/v1/chat/completions", model: str = "gpt-4o-mini") -> str:
    """Async LLM query for summarization (replace with actual API key/env)"""
    headers = {
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 500
    }
    async with session.post(api_url, headers=headers, json=payload) as response:
        if response.status == 200:
            data = await response.json()
            return data['choices'][0]['message']['content'].strip()
        else:
            logger.error(f"LLM query failed: {response.status}")
            return ""

async def summarize_segments(transcript_text: str, segment_size: int = 1000) -> List[Dict]:
    """Chunk transcript and summarize each segment using LLM"""
    segments = []
    for i in range(0, len(transcript_text), segment_size):
        chunk = transcript_text[i:i + segment_size]
        prompt = f"Summarize the following transcript segment in a reflective, balanced tone per MasterVoiceSchema: {chunk}"
        async with aiohttp.ClientSession() as session:
            summary = await llm_query(session, prompt)
        segments.append({
            "original": chunk,
            "summary": summary,
            "voice_applied": MASTER_VOICE_SCHEMA["tone"]
        })
        logger.info(f"Summarized segment {len(segments)}: {summary[:50]}...")
    return segments

def main(input_file: str, output_file: str, dry_run: bool = False):
    if not os.path.exists(input_file):
        logger.error(f"Input file not found: {input_file}")
        return 1
    
    with open(input_file, 'r') as f:
        transcript = f.read()
    
    segments = asyncio.run(summarize_segments(transcript))
    
    if dry_run:
        logger.info("Dry run: Segments generated but not saved.")
        print(json.dumps(segments, indent=2))
    else:
        with open(output_file, 'w') as f:
            json.dump(segments, f, indent=2)
        logger.info(f"Summarized segments saved to {os.path.abspath(output_file)}")
    
    # Validation: Check for completeness
    if len(segments) == 0:
        logger.warning("No segments generated - transcript may be empty.")
    
    return 0

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: summarize_segments.py <input_transcript.txt> <output_segments.json> [--dry-run]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    dry_run = "--dry-run" in sys.argv
    sys.exit(main(input_file, output_file, dry_run))
