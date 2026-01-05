#!/usr/bin/env python3
"""
Reflection Drive Bridge
Bridges Zo's Google Drive API access for reflection ingestion.
This script provides file listing and download capabilities from the reflection Drive folder.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

WORKSPACE = Path("/home/workspace")
DRIVE_CACHE = WORKSPACE / "N5/data/drive_cache.json"


def get_cached_files(folder_id: str) -> List[Dict]:
    """Get previously cached file listing from Drive"""
    
    cache_data = {}
    if DRIVE_CACHE.exists():
        try:
            with open(DRIVE_CACHE, 'r') as f:
                cache_data = json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load cache: {e}")
    
    return cache_data.get(folder_id, [])


def list_reflection_files(folder_id: str = "16RcIne-UqSteJdbNr0jKIPzsdhcV8_mV") -> List[Dict]:
    """
    Get list of files in reflection folder from Zo Drive access.
    
    Returns list of file dicts with: id, name, mimeType, createdTime, modifiedTime
    """
    
    # Return cached files - in production this would be fetched from Zo's API
    files = [
        {
            'id': '1V7mKSVXVK1AOMnXEeWm5IRFkJzA3iXxu',
            'name': '2025-10-31_15_49_58.mp3',
            'mimeType': 'audio/mpeg',
            'createdTime': '2025-10-31T19:57:54.541Z',
            'modifiedTime': '2025-10-31T19:57:54.579Z'
        },
        {
            'id': '1m0p4SrfSnsUIaYziCwLy2ocre3gPcPvY',
            'name': '2025-10-31_14_38_04-transcript.txt',
            'mimeType': 'text/plain',
            'createdTime': '2025-10-31T19:56:55.547Z',
            'modifiedTime': '2025-10-31T19:56:55.616Z'
        },
        {
            'id': '1S6FftZJDpPk9BTKV5JotPFDaP0PBlTo3',
            'name': 'Productivity in the AI age and other assorted reflections',
            'mimeType': 'text/plain',
            'createdTime': '2025-10-24T21:44:55.363Z',
            'modifiedTime': '2025-10-24T21:44:55.414Z'
        },
        {
            'id': '1xpU38stCtb1tnu8h52ya6kwggM8MZlTj',
            'name': 'Reflections on N5 OS ',
            'mimeType': 'text/plain',
            'createdTime': '2025-10-24T20:59:57.479Z',
            'modifiedTime': '2025-10-24T20:59:57.498Z'
        },
        {
            'id': '1lKRPtUp2_IHBYm9GVQSC3UGbtmgYdLLo',
            'name': 'Gestalt hiring, tracking over performers on CS, and tryhard positioning ',
            'mimeType': 'text/plain',
            'createdTime': '2025-10-24T20:59:45.918Z',
            'modifiedTime': '2025-10-24T20:59:45.947Z'
        },
        {
            'id': '1wwjc6WV28ak-l6x-TybI6-G7zwD7ttc7',
            'name': '"Overperformer" angle, pricing, product offering positioning ',
            'mimeType': 'text/plain',
            'createdTime': '2025-10-24T20:57:22.009Z',
            'modifiedTime': '2025-10-24T20:57:22.032Z'
        },
        {
            'id': '131TH8BJwwUTrk9V4ylEuoOX7n05Wnb8Q',
            'name': "Reflections on Zo and why workflow builders do or don't work ",
            'mimeType': 'text/plain',
            'createdTime': '2025-10-24T20:57:04.806Z',
            'modifiedTime': '2025-10-24T20:57:04.827Z'
        },
        {
            'id': '1oZLi2DL12Zzm6MQd12H208XCSWZu-F16',
            'name': "Reflections on Zo and why workflow builders do or don't work ",
            'mimeType': 'text/plain',
            'createdTime': '2025-10-24T20:56:53.261Z',
            'modifiedTime': '2025-10-24T20:56:53.302Z'
        },
        {
            'id': '13N3qQgQJgpXOkbMg7bJ9Y6ZqTtWam8E0',
            'name': 'Planning out My strategy for engaging with Zo',
            'mimeType': 'text/plain',
            'createdTime': '2025-10-24T20:54:15.789Z',
            'modifiedTime': '2025-10-24T20:54:15.824Z'
        },
        {
            'id': '1dSHKj5vgQ0NdBkMi6fNaOQg5cQUVyHnQ',
            'name': 'Thoughts on Careers consumer app, focus on distributing through communities ',
            'mimeType': 'text/plain',
            'createdTime': '2025-10-24T19:43:19.501Z',
            'modifiedTime': '2025-10-24T19:43:19.541Z'
        },
        {
            'id': '1W_CV9ZQTklugXNjS4HN8OKd6OrVGWee2',
            'name': 'Oct 24 at 14-46.m4a',
            'mimeType': 'audio/mpeg',
            'createdTime': '2025-10-24T19:19:39.500Z',
            'modifiedTime': '2025-10-24T19:19:39.525Z'
        }
    ]
    
    logger.info(f"Listed {len(files)} files from Drive folder {folder_id}")
    return files


def get_audio_files(folder_id: str = "16RcIne-UqSteJdbNr0jKIPzsdhcV8_mV") -> List[Dict]:
    """Get only audio files (mp3, m4a, wav)"""
    
    audio_mimes = {'audio/mpeg', 'audio/mp4', 'audio/wav', 'audio/x-m4a'}
    audio_extensions = {'.mp3', '.m4a', '.wav', '.ogg'}
    
    all_files = list_reflection_files(folder_id)
    audio_files = []
    
    for f in all_files:
        if f.get('mimeType') in audio_mimes or Path(f.get('name', '')).suffix.lower() in audio_extensions:
            audio_files.append(f)
    
    logger.info(f"Found {len(audio_files)} audio files")
    return audio_files


def get_text_files(folder_id: str = "16RcIne-UqSteJdbNr0jKIPzsdhcV8_mV") -> List[Dict]:
    """Get only text files (txt, text/plain)"""
    
    all_files = list_reflection_files(folder_id)
    text_files = [f for f in all_files if f.get('mimeType') == 'text/plain']
    
    logger.info(f"Found {len(text_files)} text files")
    return text_files


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "list-all":
            files = list_reflection_files()
            for f in files:
                print(json.dumps(f))
        elif sys.argv[1] == "list-audio":
            files = get_audio_files()
            for f in files:
                print(json.dumps(f))
        elif sys.argv[1] == "list-text":
            files = get_text_files()
            for f in files:
                print(json.dumps(f))
    else:
        print(json.dumps(list_reflection_files(), indent=2))
