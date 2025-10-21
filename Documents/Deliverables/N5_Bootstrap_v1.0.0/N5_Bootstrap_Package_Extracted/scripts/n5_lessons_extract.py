#!/usr/bin/env python3
"""
N5 Lessons Extraction
Extract techniques, strategies, patterns, and troubleshooting lessons from conversation threads

This script analyzes a conversation thread to identify:
- Novel techniques or creative approaches
- Design patterns applied
- Troubleshooting strategies that worked
- Anti-patterns encountered
- Errors and their resolutions

Called automatically by conversation-end for significant threads.
"""

import os
import sys
import json
import uuid
import logging
from pathlib import Path
from datetime import datetime, timezone

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Paths
WORKSPACE = Path("/home/workspace")
LESSONS_DIR = WORKSPACE / "N5/lessons"
PENDING_DIR = LESSONS_DIR / "pending"
SCHEMA_FILE = LESSONS_DIR / "schemas/lesson.schema.json"


def is_thread_significant(thread_id=None, conversation_ws=None):
    """
    Determine if a thread is significant enough to extract lessons
    
    Significance criteria:
    - Errors or exceptions occurred
    - Troubleshooting sequences
    - System changes or refactoring
    - Novel or creative techniques
    - Multiple retry attempts
    - Workarounds or fixes
    
    Returns: (is_significant, reasons)
    """
    # For now, return placeholder - in production this would analyze thread content
    # This is a stub that can be expanded with actual LLM analysis
    
    # TODO: Implement actual significance detection
    # Could analyze:
    # - Error messages in logs
    # - Number of tool retries
    # - File creation patterns (lots of versioning = troubleshooting)
    # - Presence of keywords: "error", "fix", "workaround", "troubleshoot"
    
    reasons = []
    
    # Placeholder logic
    if conversation_ws and conversation_ws.exists():
        # Check for error logs
        log_files = list(conversation_ws.glob("*error*.log"))
        if log_files:
            reasons.append("Error logs present")
        
        # Check for multiple versions of files (indicates iteration/troubleshooting)
        all_files = [f.name for f in conversation_ws.rglob("*") if f.is_file()]
        versioned = [f for f in all_files if "_v2" in f or "_v3" in f or "_v4" in f]
        if len(versioned) >= 3:
            reasons.append(f"Multiple file versions ({len(versioned)} files)")
        
        # Check for implementation/planning docs (indicates system changes)
        implementation_files = [f for f in all_files if any(kw in f.lower() for kw in ["implementation", "design", "spec", "plan"])]
        if implementation_files:
            reasons.append("Design/implementation documents present")
    
    is_significant = len(reasons) > 0
    
    return is_significant, reasons


def extract_lessons_llm(thread_id, conversation_ws, significance_reasons):
    """
    Use LLM to extract lessons from thread content
    
    This analyzes the conversation workspace to extract meaningful lessons.
    
    Args:
        thread_id: Thread identifier
        conversation_ws: Path to conversation workspace
        significance_reasons: List of reasons why thread is significant
    
    Returns: list of lesson dicts
    """
    logger.info("Extracting lessons using LLM analysis...")
    
    # Load conversation summary
    conversation_summary = generate_conversation_summary(conversation_ws)
    
    # Load extraction prompt template
    prompt_template_path = WORKSPACE / "N5/lessons/schemas/extraction_prompt.txt"
    if not prompt_template_path.exists():
        logger.warning("Extraction prompt template not found, using basic extraction")
        return []
    
    with open(prompt_template_path, 'r') as f:
        prompt_template = f.read()
    
    # Format prompt
    prompt = prompt_template.format(
        thread_id=thread_id,
        significance_reasons=", ".join(significance_reasons),
        conversation_summary=conversation_summary
    )
    
    # TODO: Call actual LLM API here
    # For now, log that we would extract lessons
    logger.info("LLM extraction prompt prepared")
    logger.info(f"Thread: {thread_id}")
    logger.info(f"Significance: {significance_reasons}")
    logger.info(f"Summary length: {len(conversation_summary)} chars")
    
    # Placeholder: In production, this would call LLM and parse JSON response
    # Example:
    # response = call_llm_api(prompt)
    # lessons_data = json.loads(response)
    # return lessons_data
    
    return []


def generate_conversation_summary(conversation_ws):
    """
    Generate a summary of the conversation from workspace files
    
    Args:
        conversation_ws: Path to conversation workspace
    
    Returns: str summary
    """
    if not conversation_ws or not conversation_ws.exists():
        return "No conversation workspace found"
    
    summary_parts = []
    
    # Count files by type
    all_files = list(conversation_ws.rglob("*"))
    file_count = len([f for f in all_files if f.is_file()])
    
    summary_parts.append(f"Files created: {file_count}")
    
    # Check for specific indicators
    py_files = [f for f in all_files if f.suffix == '.py']
    md_files = [f for f in all_files if f.suffix == '.md']
    
    if py_files:
        summary_parts.append(f"Python scripts: {len(py_files)}")
    if md_files:
        summary_parts.append(f"Documentation: {len(md_files)}")
    
    # Look for key files that indicate activity type
    key_files = []
    for f in all_files:
        if f.is_file():
            name_lower = f.name.lower()
            if any(kw in name_lower for kw in ['implementation', 'design', 'spec', 'error', 'fix', 'troubleshoot']):
                key_files.append(f.name)
    
    if key_files:
        summary_parts.append(f"Key files: {', '.join(key_files[:5])}")
    
    return " | ".join(summary_parts)


def create_lesson_record(lesson_data, thread_id):
    """
    Create a validated lesson record
    
    Args:
        lesson_data: dict with lesson fields
        thread_id: conversation thread ID
    
    Returns: validated lesson dict
    """
    lesson = {
        "lesson_id": str(uuid.uuid4()),
        "thread_id": thread_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "type": lesson_data.get("type", "technique"),
        "title": lesson_data.get("title", "Untitled lesson"),
        "description": lesson_data.get("description", ""),
        "context": lesson_data.get("context", ""),
        "outcome": lesson_data.get("outcome", ""),
        "principle_refs": lesson_data.get("principle_refs", []),
        "tags": lesson_data.get("tags", []),
        "status": "pending"
    }
    
    # Validate required fields
    if not lesson["title"] or len(lesson["title"]) < 5:
        raise ValueError("Lesson title must be at least 5 characters")
    
    if not lesson["description"] or len(lesson["description"]) < 10:
        raise ValueError("Lesson description must be at least 10 characters")
    
    return lesson


def save_lessons(lessons, thread_id):
    """
    Save lessons to pending directory as JSONL
    
    Args:
        lessons: list of lesson dicts
        thread_id: conversation thread ID
    
    Returns: Path to saved file
    """
    if not lessons:
        logger.info("No lessons to save")
        return None
    
    # Create pending directory
    PENDING_DIR.mkdir(parents=True, exist_ok=True)
    
    # Generate filename
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"{date_str}_{thread_id}.lessons.jsonl"
    filepath = PENDING_DIR / filename
    
    # Write JSONL
    with open(filepath, 'w') as f:
        for lesson in lessons:
            f.write(json.dumps(lesson) + '\n')
    
    logger.info(f"Saved {len(lessons)} lessons to {filepath}")
    
    # Verify write succeeded
    if not filepath.exists() or filepath.stat().st_size == 0:
        raise IOError(f"Failed to write lessons file: {filepath}")
    
    return filepath


def extract_lessons(thread_id=None, conversation_ws=None, force=False):
    """
    Main extraction logic
    
    Args:
        thread_id: Conversation thread ID (auto-detected if None)
        conversation_ws: Path to conversation workspace (auto-detected if None)
        force: Extract lessons even if thread not significant
    
    Returns: dict with extraction results
    """
    # Auto-detect thread ID and workspace
    if not thread_id:
        thread_id = os.getenv("CONVERSATION_ID", "unknown")
    
    if not conversation_ws:
        conversation_ws_env = os.getenv("CONVERSATION_WORKSPACE")
        if conversation_ws_env:
            conversation_ws = Path(conversation_ws_env)
        else:
            # Try to find most recent workspace
            workspaces_dir = Path("/home/.z/workspaces")
            if workspaces_dir.exists():
                workspaces = [d for d in workspaces_dir.iterdir() if d.is_dir() and d.name.startswith("con_")]
                if workspaces:
                    conversation_ws = max(workspaces, key=lambda d: d.stat().st_mtime)
                    thread_id = conversation_ws.name
    
    logger.info(f"Analyzing thread: {thread_id}")
    logger.info(f"Workspace: {conversation_ws}")
    
    # Check significance
    is_significant, reasons = is_thread_significant(thread_id, conversation_ws)
    
    if not is_significant and not force:
        logger.info(f"Thread not significant - skipping lesson extraction")
        return {
            "extracted": False,
            "reason": "thread_not_significant",
            "lessons_count": 0
        }
    
    logger.info(f"Thread is significant: {', '.join(reasons)}")
    
    # Extract lessons using LLM
    # TODO: Load actual thread content
    thread_content = ""  # Placeholder
    
    lessons_data = extract_lessons_llm(thread_id, conversation_ws, reasons)
    
    if not lessons_data:
        logger.info("No lessons extracted by LLM")
        return {
            "extracted": True,
            "reason": "no_lessons_found",
            "lessons_count": 0,
            "significance_reasons": reasons
        }
    
    # Create validated lesson records
    lessons = []
    for lesson_data in lessons_data:
        try:
            lesson = create_lesson_record(lesson_data, thread_id)
            lessons.append(lesson)
        except ValueError as e:
            logger.warning(f"Invalid lesson skipped: {e}")
    
    # Save to pending
    if lessons:
        filepath = save_lessons(lessons, thread_id)
        logger.info(f"✓ Extracted {len(lessons)} lessons from thread {thread_id}")
        
        return {
            "extracted": True,
            "reason": "success",
            "lessons_count": len(lessons),
            "filepath": str(filepath),
            "significance_reasons": reasons
        }
    else:
        return {
            "extracted": True,
            "reason": "no_valid_lessons",
            "lessons_count": 0,
            "significance_reasons": reasons
        }


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract lessons from conversation thread")
    parser.add_argument("--thread-id", help="Thread ID (auto-detected if omitted)")
    parser.add_argument("--workspace", type=Path, help="Conversation workspace path (auto-detected if omitted)")
    parser.add_argument("--force", action="store_true", help="Extract lessons even if thread not significant")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        result = extract_lessons(
            thread_id=args.thread_id,
            conversation_ws=args.workspace,
            force=args.force
        )
        
        # Print summary
        print("\n" + "="*70)
        print("LESSON EXTRACTION SUMMARY")
        print("="*70)
        print(f"Extracted: {result['extracted']}")
        print(f"Reason: {result['reason']}")
        print(f"Lessons: {result['lessons_count']}")
        
        if result.get('significance_reasons'):
            print(f"\nSignificance reasons:")
            for reason in result['significance_reasons']:
                print(f"  - {reason}")
        
        if result.get('filepath'):
            print(f"\nSaved to: {result['filepath']}")
        
        print("="*70)
        
        return 0 if result['lessons_count'] > 0 else 1
        
    except Exception as e:
        logger.error(f"Extraction failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
