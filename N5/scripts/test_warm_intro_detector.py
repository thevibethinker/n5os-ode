#!/usr/bin/env python3
"""
Test script for warm intro detector
"""
import asyncio
import logging
from pathlib import Path
import sys

# Add blocks to path
sys.path.insert(0, str(Path(__file__).parent / "blocks"))

from warm_intro_detector import generate_warm_intros

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(message)s")
logger = logging.getLogger(__name__)


async def test_detection():
    """Test warm intro detection with sample transcript"""
    
    # Sample transcript with clear warm intro
    test_transcript = """
    Vrijen: Thanks for taking the time today, Jeff. Your network in the recruiting space is impressive.
    
    Jeff: Happy to help. Listen, I think you should talk to folks at Superposition. They're already interested in what you're building.
    
    Vrijen: That would be amazing.
    
    Jeff: Let me introduce you to their CEO. I'll send an email this week connecting you two. They've been looking for exactly this kind of marketplace tech.
    
    Vrijen: Perfect timing. And if you know anyone at Greenhouse or other ATS companies, those intros would be valuable too.
    
    Jeff: I'll connect you with LaunchSam as well. They're in Australia but doing similar work. I can make that intro next week.
    """
    
    test_meeting_info = {
        "meeting_id": "2025-11-02_test",
        "meeting_date": "2025-11-02",
        "meeting_type": "external",
        "meeting_folder_path": "/home/workspace/Personal/Meetings/TEST_2025-11-02"
    }
    
    output_dir = Path("/tmp/test_warm_intro_output")
    output_dir.mkdir(exist_ok=True)
    
    logger.info("Testing warm intro detection...")
    count = await generate_warm_intros(test_transcript, test_meeting_info, output_dir)
    
    logger.info(f"✓ Detection complete: {count} warm intro(s) found")
    
    # Check output file
    output_file = output_dir / "B07_WARM_INTRO_BIDIRECTIONAL.json"
    if output_file.exists():
        import json
        with open(output_file) as f:
            data = json.load(f)
            logger.info(f"Output file created with {len(data.get('warm_intros', []))} intros")
            for i, intro in enumerate(data.get('warm_intros', []), 1):
                logger.info(f"  {i}. {intro['promised_by']} → {intro['promised_to']} (target: {intro['target']})")
    
    return count


if __name__ == "__main__":
    result = asyncio.run(test_detection())
    sys.exit(0 if result > 0 else 1)
