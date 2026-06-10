#!/usr/bin/env python3
"""Tier-specific close logic."""

from .core import run_thread_close


def run_tier(tier: str, convo_id: str, dry_run: bool = False):
    """Dispatch a close workflow tier."""
    normalized = str(tier).strip().lower()
    tier_map = {
        "1": 1,
        "tier1": 1,
        "tier-1": 1,
        "2": 2,
        "tier2": 2,
        "tier-2": 2,
        "3": 3,
        "tier3": 3,
        "tier-3": 3,
    }
    if normalized not in tier_map:
        raise ValueError(f"Unknown close tier: {tier}")
    return run_thread_close(convo_id=convo_id, tier=tier_map[normalized], dry_run=dry_run)
