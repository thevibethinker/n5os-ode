#!/usr/bin/env python3
"""Block Selection Logic for Meeting Pipeline"""
from typing import List

BLOCK_RULES = {
    "NETWORKING": ["B01", "B02", "B07", "B08", "B13", "B15", "B20", "B23", "B26"],
    "CUSTOMER": ["B01", "B02", "B06", "B10", "B22", "B24", "B26"],
    "FOUNDER": ["B01", "B02", "B11", "B14", "B22", "B24", "B26"],
    "INTERNAL": ["B01", "B02", "B13", "B26"]
}

def select_blocks(meeting_type: str) -> List[str]:
    """
    Select blocks to generate based on meeting type.
    
    Args:
        meeting_type: One of NETWORKING, CUSTOMER, FOUNDER, INTERNAL
        
    Returns:
        List of block IDs to generate
    """
    blocks = BLOCK_RULES.get(meeting_type.upper(), [])
    if not blocks:
        # Default to NETWORKING if unknown type
        blocks = BLOCK_RULES["NETWORKING"]
    return blocks

if __name__ == "__main__":
    # Test all meeting types
    for meeting_type in ["NETWORKING", "CUSTOMER", "FOUNDER", "INTERNAL"]:
        blocks = select_blocks(meeting_type)
        print(f"{meeting_type}: {len(blocks)} blocks -> {', '.join(blocks)}")
