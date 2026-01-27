#!/usr/bin/env python3
"""AAR (After-Action Report) generation.

Provides both templates (for LLM to fill) and generation functions (for mechanical fills).
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional


# AAR Template for threads
THREAD_AAR_TEMPLATE = """# After-Action Report: {title}

**Conversation:** {convo_id}  
**Date:** {date}  
**Tier:** {tier}

## Executive Summary

{summary}

## What Was Accomplished

{accomplishments}

## Key Decisions

{decisions}

## Lessons Learned

{lessons}

## Open Items / Next Steps

{next_steps}

## Artifacts Created

{artifacts}
"""

# AAR Template for builds
BUILD_AAR_TEMPLATE = """# Build AAR: {title}

**Build:** {slug}  
**Completed:** {date}  
**Drops:** {drop_count}

## Executive Summary

{summary}

## Objectives & Outcomes

### Original Objectives
{objectives}

### Actual Outcomes
{outcomes}

## Key Decisions (Aggregated)

{decisions}

## Learnings (Synthesized)

{learnings}

## Concerns & Risks

{concerns}

## Artifacts Produced

{artifacts}

## Recommendations

{recommendations}
"""


def get_thread_template() -> str:
    """Return the thread AAR template for LLM to fill."""
    return THREAD_AAR_TEMPLATE


def get_build_template() -> str:
    """Return the build AAR template for LLM to fill."""
    return BUILD_AAR_TEMPLATE


def generate_thread_aar(
    convo_id: str,
    state: Dict[str, Any],
    summary: str = "",
    accomplishments: List[str] = None,
    decisions: List[Dict] = None,
    lessons: List[str] = None,
    next_steps: List[str] = None,
    artifacts: List[str] = None
) -> str:
    """Generate a thread AAR with provided data.
    
    Args:
        convo_id: Conversation ID
        state: SESSION_STATE data
        summary: Executive summary (LLM should provide)
        accomplishments: List of what was done
        decisions: List of {decision, rationale} dicts
        lessons: List of lessons learned
        next_steps: List of open items
        artifacts: List of artifact paths
    
    Returns:
        Filled AAR markdown content
    """
    title = state.get('focus', state.get('objective', 'Untitled'))
    tier = state.get('tier', 'Unknown')
    date = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    
    # Format lists
    accomplishments_text = '\n'.join(f'- {a}' for a in (accomplishments or [])) or '(None documented)'
    decisions_text = '\n'.join(
        f"- **{d.get('decision', 'Unknown')}**: {d.get('rationale', '')}" 
        for d in (decisions or [])
    ) or '(None documented)'
    lessons_text = '\n'.join(f'- {l}' for l in (lessons or [])) or '(None documented)'
    next_steps_text = '\n'.join(f'- {n}' for n in (next_steps or [])) or '(None)'
    artifacts_text = '\n'.join(f'- `{a}`' for a in (artifacts or [])) or '(None)'
    
    return THREAD_AAR_TEMPLATE.format(
        title=title,
        convo_id=convo_id,
        date=date,
        tier=tier,
        summary=summary or '(Summary pending LLM generation)',
        accomplishments=accomplishments_text,
        decisions=decisions_text,
        lessons=lessons_text,
        next_steps=next_steps_text,
        artifacts=artifacts_text
    )


def generate_build_aar(
    slug: str,
    deposits: List[Dict],
    decisions: List[Dict] = None,
    meta: Dict = None,
    summary: str = "",
    objectives: str = "",
    outcomes: str = "",
    recommendations: List[str] = None
) -> str:
    """Generate a build AAR from deposits and metadata.
    
    Args:
        slug: Build slug
        deposits: List of deposit dicts from all Drops
        decisions: Aggregated decisions from all deposits
        meta: Build meta.json data
        summary: Executive summary (LLM should provide)
        objectives: Original objectives from PLAN.md
        outcomes: Actual outcomes (LLM should provide)
        recommendations: List of recommendations
    
    Returns:
        Filled AAR markdown content
    """
    meta = meta or {}
    title = meta.get('title', slug)
    date = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    drop_count = len(deposits)
    
    # Aggregate from deposits
    all_learnings = []
    all_concerns = []
    all_artifacts = []
    
    for d in deposits:
        if d.get('learnings'):
            all_learnings.append(f"[{d.get('drop_id', '?')}] {d['learnings']}")
        if d.get('concerns'):
            all_concerns.append(f"[{d.get('drop_id', '?')}] {d['concerns']}")
        all_artifacts.extend(d.get('artifacts', []))
    
    # Format
    decisions_text = '\n'.join(
        f"- **{d.get('decision', 'Unknown')}**: {d.get('rationale', '')}"
        for d in (decisions or [])
    ) or '(None documented)'
    learnings_text = '\n'.join(f'- {l}' for l in all_learnings) or '(None)'
    concerns_text = '\n'.join(f'- {c}' for c in all_concerns) or '(None)'
    artifacts_text = '\n'.join(f'- `{a}`' for a in all_artifacts) or '(None)'
    recommendations_text = '\n'.join(f'- {r}' for r in (recommendations or [])) or '(None)'
    
    return BUILD_AAR_TEMPLATE.format(
        title=title,
        slug=slug,
        date=date,
        drop_count=drop_count,
        summary=summary or '(Summary pending LLM generation)',
        objectives=objectives or '(See PLAN.md)',
        outcomes=outcomes or '(Outcomes pending LLM analysis)',
        decisions=decisions_text,
        learnings=learnings_text,
        concerns=concerns_text,
        artifacts=artifacts_text,
        recommendations=recommendations_text
    )


def validate_aar_content(content: str) -> List[str]:
    """Validate AAR content has required sections.
    
    Returns list of missing/empty sections.
    """
    issues = []
    required_sections = [
        "Executive Summary",
        "What Was Accomplished",
        "Key Decisions"
    ]
    
    for section in required_sections:
        if f"## {section}" not in content:
            issues.append(f"Missing section: {section}")
        else:
            # Check if section is filled
            parts = content.split(f"## {section}")
            if len(parts) > 1:
                section_content = parts[1].split("##")[0].strip()
                # Check for unfilled placeholders
                if section_content in ["", "{summary}", "{accomplishments}", "{decisions}"] or \
                   section_content.startswith("(") and section_content.endswith(")"):
                    issues.append(f"Unfilled section: {section}")
    
    return issues