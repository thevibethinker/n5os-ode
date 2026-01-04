#!/usr/bin/env python3
"""
Health Checkpoint Generator

Generates SMS content for health checkpoints by reading from regimen.json.
Data-driven: all content comes from SSOT, no hardcoding.

Usage:
    python3 health_checkpoint.py --checkpoint wake
    python3 health_checkpoint.py --checkpoint post_workout
    python3 health_checkpoint.py --checkpoint evening
    python3 health_checkpoint.py --list  # List all checkpoints
"""

import argparse
import json
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

REGIMEN_PATH = Path("/home/workspace/N5/systems/health/regimen.json")


def load_regimen() -> dict:
    """Load the regimen SSOT."""
    if not REGIMEN_PATH.exists():
        raise FileNotFoundError(f"Regimen not found: {REGIMEN_PATH}")
    with open(REGIMEN_PATH) as f:
        return json.load(f)


def format_item_list(items: list[str], regimen: dict) -> str:
    """Format item IDs into human-readable list with doses."""
    formatted = []
    for item_id in items:
        item = regimen["items"].get(item_id, {})
        if not item.get("active", True):
            continue
        name = item.get("name", item_id)
        dose = item.get("dose", "")
        brand = item.get("brand", "")
        
        if dose and brand and brand != "TBD":
            formatted.append(f"{name} ({dose})")
        elif dose:
            formatted.append(f"{name} ({dose})")
        else:
            formatted.append(name)
    
    return " + ".join(formatted)


def generate_sms(checkpoint_id: str, regimen: dict) -> str:
    """Generate SMS content for a checkpoint."""
    checkpoint = None
    for cp in regimen["checkpoints"]:
        if cp["id"] == checkpoint_id:
            checkpoint = cp
            break
    
    if not checkpoint:
        raise ValueError(f"Checkpoint not found: {checkpoint_id}")
    
    emoji = checkpoint.get("emoji", "💊")
    label = checkpoint.get("label", checkpoint_id.title())
    items = checkpoint.get("items", [])
    template = checkpoint.get("sms_template", "{emoji} {label}: {item_list}. Reply 'done' when taken.")
    
    item_list = format_item_list(items, regimen)
    
    # Format template
    sms = template.format(
        emoji=emoji,
        label=label,
        item_list=item_list
    )
    
    return sms


def get_checkpoint_info(checkpoint_id: str, regimen: dict) -> dict:
    """Get full checkpoint info for automation."""
    checkpoint = None
    for cp in regimen["checkpoints"]:
        if cp["id"] == checkpoint_id:
            checkpoint = cp
            break
    
    if not checkpoint:
        raise ValueError(f"Checkpoint not found: {checkpoint_id}")
    
    return {
        "id": checkpoint["id"],
        "time": checkpoint.get("time", ""),
        "label": checkpoint.get("label", ""),
        "life_counter_slug": checkpoint.get("life_counter_slug", ""),
        "sms": generate_sms(checkpoint_id, regimen),
        "items": checkpoint.get("items", []),
        "conditions": checkpoint.get("conditions", {})
    }


def list_checkpoints(regimen: dict) -> list[dict]:
    """List all checkpoints with times."""
    result = []
    for cp in regimen["checkpoints"]:
        result.append({
            "id": cp["id"],
            "time": cp.get("time", ""),
            "label": cp.get("label", ""),
            "items_count": len(cp.get("items", []))
        })
    return result


def main():
    parser = argparse.ArgumentParser(description="Generate health checkpoint SMS content")
    parser.add_argument("--checkpoint", "-c", type=str, help="Checkpoint ID (wake, post_workout, evening)")
    parser.add_argument("--list", "-l", action="store_true", help="List all checkpoints")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--full", action="store_true", help="Include full checkpoint info (not just SMS)")
    args = parser.parse_args()
    
    try:
        regimen = load_regimen()
    except FileNotFoundError as e:
        logger.error(str(e))
        print(f"ERROR: {e}")
        return 1
    
    if args.list:
        checkpoints = list_checkpoints(regimen)
        if args.json:
            print(json.dumps(checkpoints, indent=2))
        else:
            print("Available checkpoints:")
            for cp in checkpoints:
                print(f"  {cp['time']} - {cp['id']}: {cp['label']} ({cp['items_count']} items)")
        return 0
    
    if not args.checkpoint:
        parser.print_help()
        return 1
    
    try:
        if args.full:
            info = get_checkpoint_info(args.checkpoint, regimen)
            if args.json:
                print(json.dumps(info, indent=2))
            else:
                print(f"Checkpoint: {info['id']}")
                print(f"Time: {info['time']}")
                print(f"Life Counter: {info['life_counter_slug']}")
                print(f"SMS: {info['sms']}")
        else:
            sms = generate_sms(args.checkpoint, regimen)
            if args.json:
                print(json.dumps({"checkpoint": args.checkpoint, "sms": sms}))
            else:
                print(sms)
        return 0
    except ValueError as e:
        logger.error(str(e))
        print(f"ERROR: {e}")
        return 1


if __name__ == "__main__":
    exit(main())

