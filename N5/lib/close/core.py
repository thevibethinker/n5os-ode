#!/usr/bin/env python3
"""Core close logic — main entry points for all close types.

ARCHITECTURE NOTE:
This module provides the MECHANICAL scaffolding for close operations.
The SEMANTIC work (summaries, decisions, positions) happens in the 
SKILL.md instructions — the LLM reads this module's output and does
the semantic analysis.

Flow:
1. Skill wrapper (e.g. thread-close/scripts/close.py) validates context
2. This module gathers raw data (files, state, deposits)
3. LLM (following SKILL.md) does semantic analysis on that data
4. This module writes final outputs

The scripts do NOT call LLMs. The LLM calls scripts, analyzes output,
then calls more scripts to write results.
"""

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from . import guards, emoji, pii


def _check_task_system_integration(convo_id: str) -> Dict[str, Any]:
    """Check if conversation is an action conversation via new task-system skill.
    
    This replaces the old regex-based action_tagger.py approach.
    Now we use the context.py script to gather data for AI reasoning.
    """
    try:
        # Run the context script to check if this is an action conversation
        result = subprocess.run(
            ['python3', '/home/workspace/Skills/task-system/scripts/context.py', 
             'action-check', '--convo-id', convo_id],
            capture_output=True,
            text=True,
            cwd='/home/workspace'
        )
        
        if result.returncode == 0:
            try:
                context = json.loads(result.stdout)
                
                # Check if there are matching tasks
                if context.get('matching_tasks'):
                    return {
                        'is_action_conversation': True,
                        'matching_tasks': context.get('matching_tasks', []),
                        'task_id': context.get('suggested_task_id'),
                        'context_available': True
                    }
                
                # Check if conversation focus indicates action work
                focus = context.get('session_state', {}).get('focus', '')
                if focus and any(keyword in focus.lower() for keyword in ['draft', 'write', 'create', 'build', 'send', 'fix']):
                    return {
                        'is_action_conversation': True,
                        'potential_task': True,
                        'focus': focus,
                        'context_available': True
                    }
            except json.JSONDecodeError:
                pass
        
        return {'is_action_conversation': False, 'context_available': False}
        
    except Exception as e:
        return {'is_action_conversation': False, 'error': str(e)}


def get_task_completion_context(convo_id: str, task_id: int) -> Optional[Dict[str, Any]]:
    """Get completion context for a task from the new task-system skill.
    
    This replaces the old assess_task_completion() from close_hooks.py.
    The context.py script gathers data, and AI does the reasoning.
    """
    try:
        result = subprocess.run(
            ['python3', '/home/workspace/Skills/task-system/scripts/context.py',
             'completion-check', '--convo-id', convo_id, '--task-id', str(task_id)],
            capture_output=True,
            text=True,
            cwd='/home/workspace'
        )
        
        if result.returncode == 0:
            return json.loads(result.stdout)
        
        return None
    except Exception as e:
        print(f"Error getting task completion context: {e}")
        return None


def get_task_next_step(task_id: int) -> Optional[Dict[str, Any]]:
    """Get next step suggestion for a task from the new task-system skill.
    
    This replaces the old infer_next_step() from close_hooks.py.
    """
    try:
        result = subprocess.run(
            ['python3', '/home/workspace/Skills/task-system/scripts/context.py',
             'next-step', '--task-id', str(task_id)],
            capture_output=True,
            text=True,
            cwd='/home/workspace'
        )
        
        if result.returncode == 0:
            return json.loads(result.stdout)
        
        return None
    except Exception as e:
        print(f"Error getting task next step: {e}")
        return None


def update_task_status(task_id: int, status: str, notes: str = "") -> bool:
    """Update task status using the new task-system skill.
    
    This replaces the old update_task_from_conversation() from close_hooks.py.
    """
    try:
        result = subprocess.run(
            ['python3', '/home/workspace/Skills/task-system/scripts/task.py',
             'update', str(task_id), '--status', status],
            capture_output=True,
            text=True,
            cwd='/home/workspace'
        )
        
        if result.returncode == 0:
            return True
        
        print(f"Failed to update task status: {result.stderr}")
        return False
    except Exception as e:
        print(f"Error updating task status: {e}")
        return False


def complete_task(task_id: int, actual_minutes: Optional[int] = None) -> bool:
    """Mark a task as complete using the new task-system skill.
    """
    try:
        cmd = ['python3', '/home/workspace/Skills/task-system/scripts/task.py',
               'complete', str(task_id)]
        if actual_minutes:
            cmd.extend(['--actual', str(actual_minutes)])
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd='/home/workspace'
        )
        
        if result.returncode == 0:
            return True
        
        print(f"Failed to complete task: {result.stderr}")
        return False
    except Exception as e:
        print(f"Error completing task: {e}")
        return False


def json_serial(obj):
    """JSON serializer for objects not serializable by default."""
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def _is_placeholder_title(title: Optional[str]) -> bool:
    """Return True when title is empty or clearly a placeholder."""
    if not title:
        return True
    normalized = title.strip().lower()
    if not normalized:
        return True
    placeholder_tokens = {
        "untitled",
        "title",
        "semantic title",
        "your semantic title",
        "tbd",
        "todo",
    }
    return normalized in placeholder_tokens


def _ensure_title_format(convo_id: str, title: Optional[str]) -> str:
    """Guarantee a valid thread-close title with the 3-slot emoji prefix."""
    state = guards.load_session_state(convo_id)
    candidate = (title or "").strip()

    # If missing/placeholder, generate fully from state.
    if _is_placeholder_title(candidate):
        return emoji.generate_title(
            state=state,
            convo_id=convo_id,
            semantic_title=(state.get("focus") or "Conversation Close"),
        )

    # If semantic title exists but missing emoji/date prefix, normalize it.
    if " | " not in candidate:
        return emoji.generate_title(
            state=state,
            convo_id=convo_id,
            semantic_title=candidate,
        )

    return candidate


def detect_tier(convo_id: str) -> int:
    """Auto-detect appropriate tier for thread close.
    
    Tier 1: Simple discussions (<3 artifacts)
    Tier 2: Standard work (3-10 artifacts, research)
    Tier 3: Builds, orchestrators, complex debug
    """
    workspace = Path(f"/home/.z/workspaces/{convo_id}")
    state = guards.load_session_state(convo_id)
    
    # Tier 3 signals
    if state.get('type') == 'build':
        return 3
    if state.get('mode') == 'orchestrator':
        return 3
    
    # Count artifacts
    artifact_count = 0
    for pattern in ['*.py', '*.md', '*.json', '*.ts']:
        artifact_count += len(list(workspace.glob(pattern)))
    
    if artifact_count >= 10:
        return 3
    elif artifact_count >= 3:
        return 2
    else:
        return 1


def gather_thread_context(convo_id: str) -> Dict[str, Any]:
    """Gather all raw data needed for thread close.
    
    Returns dict with:
    - state: SESSION_STATE contents
    - artifacts: list of files in workspace
    - tier: detected tier
    - task_info: task system data if this is an action conversation
    
    The LLM uses this to do semantic analysis.
    """
    workspace = Path(f"/home/.z/workspaces/{convo_id}")
    state = guards.load_session_state(convo_id)
    tier = detect_tier(convo_id)
    
    # List all artifacts
    artifacts = []
    for pattern in ['*.py', '*.md', '*.json', '*.ts', '*.txt']:
        for f in workspace.glob(pattern):
            artifacts.append({
                'path': str(f),
                'name': f.name,
                'size': f.stat().st_size,
                'modified': datetime.fromtimestamp(f.stat().st_mtime).isoformat()
            })
    
    # Check if this is an action conversation and include task info if available
    task_check = _check_task_system_integration(convo_id)
    
    if task_check.get('is_action_conversation'):
        task_info = {
            'task_id': task_check.get('task_id'),
            'matching_tasks': task_check.get('matching_tasks', []),
            'potential_task': task_check.get('potential_task', False),
            'focus': task_check.get('focus'),
            'completion_context': None,
            'next_step': None,
            'suggested_action': None
        }
        
        # If we have a specific task_id, get completion context
        if task_info['task_id']:
            completion_ctx = get_task_completion_context(convo_id, task_info['task_id'])
            if completion_ctx:
                task_info['completion_context'] = completion_ctx
        
        return {
            'convo_id': convo_id,
            'workspace': str(workspace),
            'state': state,
            'tier': tier,
            'artifacts': artifacts,
            'artifact_count': len(artifacts),
            'task_info': task_info
        }
    
    return {
        'convo_id': convo_id,
        'workspace': str(workspace),
        'state': state,
        'tier': tier,
        'artifacts': artifacts,
        'artifact_count': len(artifacts)
    }


def write_thread_close_output(
    convo_id: str,
    tier: int,
    title: str,
    summary: str,
    decisions: List[Dict] = None,
    next_steps: List[str] = None,
    aar_content: str = None,
    positions: List[Dict] = None,
    content_candidates: List[str] = None
) -> Dict[str, str]:
    """Write thread close outputs after LLM analysis.
    
    Called by LLM after it has done semantic analysis.
    Returns paths to written files.
    """
    workspace = Path(f"/home/.z/workspaces/{convo_id}")
    outputs = {}
    
    # Always write close summary
    normalized_title = _ensure_title_format(convo_id, title)
    close_data = {
        'convo_id': convo_id,
        'tier': tier,
        'title': normalized_title,
        'summary': summary,
        'completed_at': datetime.utcnow().isoformat()
    }
    
    if decisions:
        close_data['decisions'] = decisions
    if next_steps:
        close_data['next_steps'] = next_steps
    if positions:
        close_data['positions'] = positions
    if content_candidates:
        close_data['content_candidates'] = content_candidates
    
    close_path = workspace / "CLOSE_OUTPUT.json"
    close_path.write_text(json.dumps(close_data, indent=2, default=json_serial, ensure_ascii=False))
    outputs['close_data'] = str(close_path)

    # Human-readable title + summary artifacts for UI/file preview reliability
    title_path = workspace / "CLOSE_TITLE.txt"
    title_path.write_text(f"{normalized_title}\n", encoding="utf-8")
    outputs['title'] = str(title_path)

    now = datetime.utcnow().strftime("%Y-%m-%d")
    close_md_path = workspace / "CLOSE_OUTPUT.md"
    close_md = (
        "---\n"
        f"created: {now}\n"
        f"last_edited: {now}\n"
        "version: 1.0\n"
        f"provenance: {convo_id}\n"
        "---\n\n"
        "# Close Output\n\n"
        f"## Title\n\n{normalized_title}\n\n"
        "## Summary\n\n"
        f"{summary}\n"
    )
    close_md_path.write_text(close_md, encoding="utf-8")
    outputs['close_md'] = str(close_md_path)
    
    # Write AAR for tier 3
    if tier >= 3 and aar_content:
        aar_path = workspace / "AAR.md"
        aar_path.write_text(aar_content)
        outputs['aar'] = str(aar_path)
    
    # Run PII audit
    pii.audit_conversation(convo_id)
    outputs['pii_audit'] = 'completed'
    
    return outputs


def gather_drop_context(convo_id: str, drop_id: str, build_slug: str) -> Dict[str, Any]:
    """Gather context for drop close.
    
    Returns dict for LLM to analyze and write deposit.
    """
    workspace = Path(f"/home/.z/workspaces/{convo_id}")
    state = guards.load_session_state(convo_id)
    build_dir = Path(f"/home/workspace/N5/builds/{build_slug}")
    
    # Read the drop brief
    brief_path = None
    for f in (build_dir / "drops").glob(f"{drop_id}*.md"):
        brief_path = f
        break
    
    brief_content = brief_path.read_text() if brief_path else ""
    
    # List workspace artifacts
    artifacts = []
    for pattern in ['*.py', '*.md', '*.json', '*.ts']:
        for f in workspace.glob(pattern):
            artifacts.append(str(f.relative_to(workspace)))
    
    return {
        'drop_id': drop_id,
        'build_slug': build_slug,
        'convo_id': convo_id,
        'brief': brief_content,
        'state': state,
        'artifacts': artifacts
    }


def write_drop_deposit(
    drop_id: str,
    build_slug: str,
    convo_id: str,
    status: str,
    summary: str,
    artifacts: List[str],
    learnings: str = "",
    concerns: str = "",
    decisions: List[Dict] = None
) -> str:
    """Write drop deposit after LLM analysis.
    
    Called by LLM after analyzing the drop's work.
    Returns path to deposit file.
    """
    deposit = {
        'drop_id': drop_id,
        'convo_id': convo_id,
        'status': status,
        'completed_at': datetime.utcnow().isoformat(),
        'summary': summary,
        'artifacts': artifacts,
        'learnings': learnings,
        'concerns': concerns,
        'decisions': decisions or []
    }
    
    deposit_path = Path(f"/home/workspace/N5/builds/{build_slug}/deposits/{drop_id}.json")
    deposit_path.parent.mkdir(parents=True, exist_ok=True)
    deposit_path.write_text(json.dumps(deposit, indent=2, default=json_serial))
    
    return str(deposit_path)


def gather_build_context(slug: str) -> Dict[str, Any]:
    """Gather all deposits and context for build close.
    
    Returns aggregated data for LLM to synthesize.
    """
    build_dir = Path(f"/home/workspace/N5/builds/{slug}")
    deposits_dir = build_dir / "deposits"
    
    # Load all deposits
    deposits = []
    for deposit_file in sorted(deposits_dir.glob("D*.json")):
        if '_filter' in deposit_file.name or '_forensics' in deposit_file.name:
            continue
        deposits.append(json.loads(deposit_file.read_text()))
    
    # Load meta
    meta_path = build_dir / "meta.json"
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    
    # Load build lessons
    lessons_path = build_dir / "BUILD_LESSONS.json"
    lessons = json.loads(lessons_path.read_text()) if lessons_path.exists() else []
    
    # Aggregate all decisions
    all_decisions = []
    for d in deposits:
        all_decisions.extend(d.get('decisions', []))
    
    # Aggregate all learnings
    all_learnings = [d.get('learnings', '') for d in deposits if d.get('learnings')]
    
    # Aggregate all concerns
    all_concerns = [d.get('concerns', '') for d in deposits if d.get('concerns')]
    
    # List all artifacts across deposits
    all_artifacts = []
    for d in deposits:
        all_artifacts.extend(d.get('artifacts', []))
    
    return {
        'slug': slug,
        'title': meta.get('title', slug),
        'deposit_count': len(deposits),
        'deposits': deposits,
        'decisions': all_decisions,
        'learnings': all_learnings,
        'concerns': all_concerns,
        'artifacts': list(set(all_artifacts)),
        'lessons': lessons
    }


def write_build_close_output(
    slug: str,
    summary: str,
    synthesized_decisions: List[Dict],
    synthesized_learnings: List[str],
    key_concerns: List[str],
    position_candidates: List[Dict] = None,
    content_candidates: List[str] = None,
    aar_content: str = None
) -> Dict[str, str]:
    """Write build close outputs after LLM synthesis.
    
    Called by LLM after synthesizing across all deposits.
    """
    build_dir = Path(f"/home/workspace/N5/builds/{slug}")
    outputs = {}
    
    # Write BUILD_CLOSE.md
    close_content = f"""# Build Close: {slug}

**Completed:** {datetime.utcnow().isoformat()}

## Summary

{summary}

## Key Decisions ({len(synthesized_decisions)})

"""
    for d in synthesized_decisions:
        close_content += f"- **{d.get('decision', 'Unknown')}**: {d.get('rationale', '')}\n"
    
    close_content += f"""
## Learnings ({len(synthesized_learnings)})

"""
    for l in synthesized_learnings:
        close_content += f"- {l}\n"
    
    if key_concerns:
        close_content += f"""
## Concerns ({len(key_concerns)})

"""
        for c in key_concerns:
            close_content += f"- {c}\n"
    
    if position_candidates:
        close_content += f"""
## Position Candidates ({len(position_candidates)})

"""
        for p in position_candidates:
            close_content += f"- **{p.get('title', 'Untitled')}**: {p.get('insight', '')}\n"
    
    if content_candidates:
        close_content += f"""
## Content Library Candidates ({len(content_candidates)})

"""
        for c in content_candidates:
            close_content += f"- {c}\n"
    
    close_path = build_dir / "BUILD_CLOSE.md"
    close_path.write_text(close_content)
    outputs['close'] = str(close_path)
    
    # Write AAR
    if aar_content:
        aar_path = build_dir / "BUILD_AAR.md"
        aar_path.write_text(aar_content)
        outputs['aar'] = str(aar_path)
    
    return outputs


def run_thread_close(
    convo_id: str,
    tier: int = None,
    dry_run: bool = False
) -> int:
    """Main entry point for thread close.
    
    This gathers context and outputs it for LLM to process.
    In dry_run mode, just prints what would happen.
    
    Returns exit code (0 = success).
    """
    context = gather_thread_context(convo_id)
    
    if tier is None:
        tier = context['tier']
    
    if dry_run:
        print(f"[DRY RUN] Thread Close for {convo_id}")
        print(f"  Tier: {tier}")
        print(f"  Artifacts: {context['artifact_count']}")
        if 'task_info' in context:
            print(f"  Action conversation: Yes")
            if context['task_info'].get('task_id'):
                print(f"  Task ID: {context['task_info']['task_id']}")
        print(f"  State: {json.dumps(context['state'], indent=2, default=json_serial)[:200]}...")
        return 0
    
    # Output context as JSON for LLM to consume
    print(json.dumps(context, indent=2, default=json_serial))
    return 0


def run_drop_close(
    convo_id: str,
    drop_id: str = None,
    build_slug: str = None
) -> int:
    """Main entry point for drop close.
    
    Gathers context and outputs it for LLM to write deposit.
    Returns exit code (0 = success).
    """
    state = guards.load_session_state(convo_id)
    
    # Get drop_id and build_slug from state if not provided
    if drop_id is None:
        drop_id = state.get('drop_id') or state.get('worker_id')
    if build_slug is None:
        build_slug = state.get('build_slug') or state.get('build')
    
    if not drop_id or not build_slug:
        print(f"ERROR: Missing drop_id ({drop_id}) or build_slug ({build_slug})")
        print("SESSION_STATE must have drop_id and build_slug for drop close.")
        return 1
    
    context = gather_drop_context(convo_id, drop_id, build_slug)
    print(json.dumps(context, indent=2, default=json_serial))
    return 0


def run_build_close(
    slug: str,
    dry_run: bool = False
) -> int:
    """Main entry point for build close.
    
    Gathers all deposits and outputs aggregated context for LLM synthesis.
    Returns exit code (0 = success).
    """
    context = gather_build_context(slug)
    
    if dry_run:
        print(f"[DRY RUN] Build Close for {slug}")
        print(f"  Title: {context['title']}")
        print(f"  Deposits: {context['deposit_count']}")
        print(f"  Decisions: {len(context['decisions'])}")
        print(f"  Artifacts: {len(context['artifacts'])}")
        print("\n  Deposit summaries:")
        for d in context['deposits']:
            print(f"    [{d.get('drop_id')}] {d.get('summary', '')[:60]}...")
        return 0
    
    # Output full context for LLM to synthesize
    print(json.dumps(context, indent=2, default=json_serial))
    return 0


def complete_action_conversation(
    convo_id: str,
    task_id: int,
    status: str,
    notes: str = ""
) -> Dict[str, Any]:
    """Update task status after user confirmation.
    
    This function is called to update the task status in the task system
    after the user has confirmed the completion of the action conversation.
    
    Args:
        convo_id: Conversation ID
        task_id: Task ID to update
        status: New status ('complete', 'partial', 'in_progress', etc.)
        notes: Optional notes about the completion
    
    Returns:
        Dict with status and result/error message
    """
    if not _check_task_system_integration(convo_id).get('is_action_conversation'):
        return {'status': 'error', 'message': 'Task system not available or not an action conversation'}
    
    try:
        if status == 'complete':
            success = complete_task(task_id)
            return {
                'status': 'success' if success else 'error',
                'action': 'complete',
                'task_id': task_id,
                'notes': notes
            }
        else:
            success = update_task_status(task_id, status, notes)
            return {
                'status': 'success' if success else 'error',
                'action': 'update',
                'task_id': task_id,
                'new_status': status,
                'notes': notes
            }
    except Exception as e:
        return {'status': 'error', 'message': str(e)}
