#!/usr/bin/env python3
"""
Enhanced Block Selection Logic for Meeting Pipeline
Version 2.0 - Content-aware selection
"""
import re
from typing import List, Dict, Set
from pathlib import Path

# Baseline blocks by meeting type (SAFE - always generated)
BASELINE_BLOCKS = {
    "NETWORKING": ["B01", "B02", "B05", "B26"],
    "CUSTOMER": ["B01", "B02", "B05", "B06", "B26"],
    "FOUNDER": ["B01", "B02", "B05", "B26"],
    "INTERNAL": ["B01", "B02", "B05", "B26"],
    "EXTERNAL": ["B01", "B02", "B05", "B26"]
}

# Conditional blocks - added based on transcript content analysis
CONDITIONAL_BLOCKS = {
    # Metrics & Numbers
    "B11": {
        "triggers": ["metrics", "numbers", "revenue", "growth", "$", "%", "users"],
        "min_count": 3,
        "description": "METRICS_SNAPSHOT - When meeting discusses quantitative data"
    },
    
    # Strategic & Planning
    "B13": {
        "triggers": ["plan", "roadmap", "timeline", "milestone", "deadline", "schedule"],
        "min_count": 2,
        "description": "PLAN_OF_ACTION - When clear action plan emerges"
    },
    
    "B31": {
        "triggers": ["strategy", "positioning", "competitive", "market", "approach", "vision"],
        "min_count": 2,
        "description": "STRATEGIC_INTEL - When strategic discussion occurs"
    },
    
    # Insights & Key Moments
    "B15": {
        "triggers": ["insight", "realize", "important", "key", "critical", "breakthrough"],
        "min_count": 2,
        "description": "INSIGHTS - When significant realizations occur"
    },
    
    "B21": {
        "triggers": ["quote", "said", "mentioned", "emphasized", "highlighted"],
        "min_count": 5,
        "description": "KEY_MOMENTS - For meetings with memorable quotes/moments"
    },
    
    # Network & Introductions
    "B07": {
        "triggers": ["intro", "connect", "know", "meet", "referral", "network"],
        "min_count": 2,
        "description": "WARM_INTRO - When networking/introductions discussed"
    },
    
    "B08": {
        "triggers": ["person", "contact", "founder", "investor", "partner", "advisor"],
        "min_count": 3,
        "description": "STAKEHOLDER_INTELLIGENCE - When key people discussed"
    },
    
    # Product & Ideas
    "B14": {
        "triggers": ["blurb", "description", "summary", "pitch", "explain"],
        "min_count": 2,
        "description": "BLURBS_REQUESTED - When descriptions/summaries needed"
    },
    
    "B24": {
        "triggers": ["idea", "feature", "product", "build", "create", "develop"],
        "min_count": 3,
        "description": "PRODUCT_IDEAS - When product ideas discussed"
    },
    
    # Customer & Pilot
    "B10": {
        "triggers": ["customer", "client", "user", "buyer", "prospect"],
        "min_count": 3,
        "description": "CUSTOMER_INTELLIGENCE - When customers discussed"
    },
    
    "B22": {
        "triggers": ["pilot", "poc", "trial", "test", "experiment"],
        "min_count": 2,
        "description": "PILOT_EXPANSION - When pilot programs discussed"
    },
    
    # Deliverables & Content
    "B25": {
        "triggers": ["deliverable", "document", "deck", "write", "create", "send"],
        "min_count": 2,
        "description": "DELIVERABLES - When concrete outputs needed"
    },
    
    "B27": {
        "triggers": ["messaging", "positioning", "pitch", "explain", "story"],
        "min_count": 2,
        "description": "KEY_MESSAGING - When positioning/messaging discussed"
    }
}

# Internal-specific blocks (B40 series)
INTERNAL_CONDITIONAL = {
    "B40": {
        "triggers": ["decide", "decision", "choice", "option", "select"],
        "min_count": 2,
        "description": "INTERNAL_DECISIONS"
    },
    
    "B41": {
        "triggers": ["coordinate", "sync", "align", "team", "who", "when"],
        "min_count": 2,
        "description": "TEAM_COORDINATION"
    },
    
    "B42": {
        "triggers": ["market", "competitive", "competitor", "landscape", "position"],
        "min_count": 2,
        "description": "MARKET_COMPETITIVE_INTEL"
    },
    
    "B43": {
        "triggers": ["product", "feature", "roadmap", "build", "technical", "architecture"],
        "min_count": 2,
        "description": "PRODUCT_INTELLIGENCE"
    },
    
    "B44": {
        "triggers": ["gtm", "sales", "pricing", "package", "distribution", "channel"],
        "min_count": 2,
        "description": "GTM_SALES_INTEL"
    },
    
    "B45": {
        "triggers": ["process", "workflow", "tool", "operations", "efficiency"],
        "min_count": 2,
        "description": "OPERATIONS_PROCESS"
    },
    
    "B46": {
        "triggers": ["hire", "hiring", "role", "candidate", "recruit", "compensation"],
        "min_count": 2,
        "description": "HIRING_TEAM"
    },
    
    "B47": {
        "triggers": ["debate", "disagree", "uncertain", "unclear", "open question"],
        "min_count": 1,
        "description": "OPEN_DEBATES"
    }
}

def analyze_transcript_content(transcript_path: str) -> Dict[str, any]:
    """Analyze transcript to extract signals for block selection."""
    try:
        with open(transcript_path, 'r') as f:
            content = f.read().lower()
    except:
        return {
            "word_count": 0,
            "duration_estimate": 0,
            "trigger_matches": {},
            "has_metrics": False,
            "has_names": False,
            "question_count": 0
        }
    
    words = content.split()
    word_count = len(words)
    duration_estimate = word_count / 150
    
    trigger_matches = {}
    for block_id, config in {**CONDITIONAL_BLOCKS, **INTERNAL_CONDITIONAL}.items():
        count = sum(content.count(trigger) for trigger in config["triggers"])
        if count >= config["min_count"]:
            trigger_matches[block_id] = count
    
    has_metrics = bool(re.search(r'\d+[%$]|\d+\s*(user|customer|revenue|growth)', content))
    has_names = bool(re.search(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b', content))
    question_count = content.count('?')
    
    return {
        "word_count": word_count,
        "duration_estimate": duration_estimate,
        "trigger_matches": trigger_matches,
        "has_metrics": has_metrics,
        "has_names": has_names,
        "question_count": question_count
    }

def select_blocks(meeting_type: str, transcript_path: str = None) -> List[str]:
    """Select blocks based on meeting type and content analysis."""
    meeting_type = meeting_type.upper()
    blocks = set(BASELINE_BLOCKS.get(meeting_type, BASELINE_BLOCKS["NETWORKING"]))
    
    if not transcript_path or not Path(transcript_path).exists():
        return sorted(blocks)
    
    analysis = analyze_transcript_content(transcript_path)
    
    for block_id in analysis["trigger_matches"].keys():
        if block_id.startswith("B4") and meeting_type != "INTERNAL":
            continue
        blocks.add(block_id)
    
    if analysis["duration_estimate"] >= 30:
        blocks.add("B21")
        if meeting_type == "INTERNAL":
            blocks.add("B48")
    
    if analysis["has_metrics"]:
        blocks.add("B11")
    
    if analysis["question_count"] >= 5:
        blocks.add("B05")
    
    if analysis["has_names"] and meeting_type in ["NETWORKING", "EXTERNAL"]:
        blocks.add("B07")
        blocks.add("B08")
    
    if meeting_type == "CUSTOMER":
        blocks.update(["B06", "B10", "B22"])
    elif meeting_type == "FOUNDER":
        blocks.update(["B11", "B14", "B24"])
    elif meeting_type == "INTERNAL":
        blocks.update(["B13", "B40", "B41"])
    elif meeting_type in ["NETWORKING", "EXTERNAL"]:
        blocks.update(["B07", "B08", "B15"])
    
    return sorted(blocks)

def explain_selection(meeting_type: str, transcript_path: str = None) -> Dict:
    """Return detailed explanation of block selection."""
    baseline = set(BASELINE_BLOCKS.get(meeting_type.upper(), BASELINE_BLOCKS["NETWORKING"]))
    all_blocks = set(select_blocks(meeting_type, transcript_path))
    conditional = all_blocks - baseline
    
    analysis = None
    if transcript_path and Path(transcript_path).exists():
        analysis = analyze_transcript_content(transcript_path)
    
    return {
        "blocks": sorted(all_blocks),
        "baseline": sorted(baseline),
        "conditional": sorted(conditional),
        "analysis": analysis,
        "total_count": len(all_blocks)
    }

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        meeting_type = sys.argv[1]
        transcript_path = sys.argv[2] if len(sys.argv) > 2 else None
        
        result = explain_selection(meeting_type, transcript_path)
        print(f"\n=== Block Selection for {meeting_type} ===")
        print(f"Baseline: {', '.join(result['baseline'])} ({len(result['baseline'])})")
        print(f"Conditional: {', '.join(result['conditional'])} ({len(result['conditional'])})")
        print(f"Total: {', '.join(result['blocks'])} ({result['total_count']})")
        
        if result['analysis']:
            print(f"\nContent Analysis:")
            print(f"  Duration: ~{result['analysis']['duration_estimate']:.1f} min")
            print(f"  Words: {result['analysis']['word_count']}")
            print(f"  Has metrics: {result['analysis']['has_metrics']}")
            print(f"  Has names: {result['analysis']['has_names']}")
            print(f"  Questions: {result['analysis']['question_count']}")
            if result['analysis']['trigger_matches']:
                print(f"  Triggered: {', '.join(result['analysis']['trigger_matches'].keys())}")
    else:
        print("\n=== Basic Block Selection Test ===")
        for mtype in ["NETWORKING", "CUSTOMER", "FOUNDER", "INTERNAL"]:
            blocks = select_blocks(mtype)
            print(f"{mtype}: {len(blocks)} blocks -> {', '.join(blocks)}")
