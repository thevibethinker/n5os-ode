#!/usr/bin/env python3
"""
N5 Lessons Review
Interactive batch review of pending lessons with principle updates

This script:
1. Loads all pending lessons from N5/lessons/pending/
2. Presents each lesson for review (approve/edit/reject/skip)
3. Updates architectural principles with approved lessons
4. Archives approved lessons, discards rejected ones
5. Tracks changes in principle module change logs

Run weekly (Sunday evenings) via scheduled task.
"""

import os
import sys
import json
import shutil
import logging
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Paths
WORKSPACE = Path("/home/workspace")
LESSONS_DIR = WORKSPACE / "N5/lessons"
PENDING_DIR = LESSONS_DIR / "pending"
ARCHIVE_DIR = LESSONS_DIR / "archive"
PRINCIPLES_DIR = WORKSPACE / "Knowledge/architectural/principles"


def load_pending_lessons():
    """
    Load all pending lessons from pending directory
    
    Returns: list of (filepath, lessons) tuples
    """
    if not PENDING_DIR.exists():
        logger.info("No pending directory found")
        return []
    
    pending_files = list(PENDING_DIR.glob("*.lessons.jsonl"))
    
    if not pending_files:
        logger.info("No pending lessons found")
        return []
    
    all_lessons = []
    
    for filepath in sorted(pending_files):
        try:
            lessons = []
            with open(filepath, 'r') as f:
                for line in f:
                    if line.strip():
                        lesson = json.loads(line)
                        lessons.append(lesson)
            
            if lessons:
                all_lessons.append((filepath, lessons))
                logger.info(f"Loaded {len(lessons)} lessons from {filepath.name}")
        
        except Exception as e:
            logger.error(f"Failed to load {filepath.name}: {e}")
    
    return all_lessons


def display_lesson(lesson, index, total):
    """
    Display a lesson for review
    
    Args:
        lesson: lesson dict
        index: current index (1-based)
        total: total lesson count
    """
    print("\n" + "="*70)
    print(f"LESSON {index} of {total}")
    print("="*70)
    print(f"Thread: {lesson['thread_id']}")
    print(f"Date: {lesson['timestamp'][:10]}")
    print(f"Type: {lesson['type']}")
    print()
    print(f"Title: {lesson['title']}")
    print()
    print("Description:")
    print(f"  {lesson['description']}")
    print()
    
    if lesson.get('context'):
        print("Context:")
        print(f"  {lesson['context']}")
        print()
    
    if lesson.get('outcome'):
        print("Outcome:")
        print(f"  {lesson['outcome']}")
        print()
    
    if lesson.get('principle_refs'):
        print(f"Principle Refs: {lesson['principle_refs']}")
    
    if lesson.get('tags'):
        print(f"Tags: {', '.join(lesson['tags'])}")
    
    print("\n" + "-"*70)


def prompt_action():
    """
    Prompt user for action
    
    Returns: action string ('approve', 'edit', 'reject', 'skip', 'quit')
    """
    print("[A]pprove  [E]dit  [R]eject  [S]kip  [Q]uit")
    response = input("> ").strip().lower()
    
    if response in ['a', 'approve']:
        return 'approve'
    elif response in ['e', 'edit']:
        return 'edit'
    elif response in ['r', 'reject']:
        return 'reject'
    elif response in ['s', 'skip']:
        return 'skip'
    elif response in ['q', 'quit']:
        return 'quit'
    else:
        print("Invalid option. Please choose A, E, R, S, or Q.")
        return prompt_action()


def edit_lesson(lesson):
    """
    Interactive lesson editing
    
    Args:
        lesson: lesson dict to edit
    
    Returns: modified lesson dict
    """
    print("\n" + "="*70)
    print("EDIT LESSON")
    print("="*70)
    print("Press Enter to keep current value\n")
    
    # Title
    current_title = lesson['title']
    new_title = input(f"Title [{current_title}]: ").strip()
    if new_title:
        lesson['title'] = new_title
    
    # Description
    current_desc = lesson['description']
    print(f"\nCurrent description: {current_desc}")
    new_desc = input("New description (or Enter to keep): ").strip()
    if new_desc:
        lesson['description'] = new_desc
    
    # Context
    current_context = lesson.get('context', '')
    if current_context:
        print(f"\nCurrent context: {current_context}")
    new_context = input("Context (or Enter to keep): ").strip()
    if new_context:
        lesson['context'] = new_context
    
    # Outcome
    current_outcome = lesson.get('outcome', '')
    if current_outcome:
        print(f"\nCurrent outcome: {current_outcome}")
    new_outcome = input("Outcome (or Enter to keep): ").strip()
    if new_outcome:
        lesson['outcome'] = new_outcome
    
    # Principle refs
    current_refs = lesson.get('principle_refs', [])
    print(f"\nCurrent principle refs: {current_refs}")
    new_refs = input("Principle refs (comma-separated, or Enter to keep): ").strip()
    if new_refs:
        lesson['principle_refs'] = [r.strip() for r in new_refs.split(',')]
    
    # Tags
    current_tags = lesson.get('tags', [])
    print(f"\nCurrent tags: {current_tags}")
    new_tags = input("Tags (comma-separated, or Enter to keep): ").strip()
    if new_tags:
        lesson['tags'] = [t.strip() for t in new_tags.split(',')]
    
    print("\n✓ Lesson updated")
    return lesson


def update_principle_with_lesson(principle_num, lesson):
    """
    Update a principle module with an approved lesson
    
    Args:
        principle_num: principle number (str)
        lesson: lesson dict
    
    Returns: bool success
    """
    # Map principle number to module
    principle_to_module = {
        '0': 'core.md', '2': 'core.md',
        '5': 'safety.md', '7': 'safety.md', '11': 'safety.md', '19': 'safety.md',
        '1': 'quality.md', '15': 'quality.md', '16': 'quality.md', '18': 'quality.md',
        '3': 'design.md', '4': 'design.md', '8': 'design.md', '20': 'design.md',
        '6': 'operations.md', '9': 'operations.md', '10': 'operations.md',
        '12': 'operations.md', '13': 'operations.md', '14': 'operations.md', '17': 'operations.md'
    }
    
    module_name = principle_to_module.get(principle_num)
    
    if not module_name:
        logger.warning(f"Unknown principle number: {principle_num}")
        return False
    
    module_path = PRINCIPLES_DIR / module_name
    
    if not module_path.exists():
        logger.error(f"Principle module not found: {module_path}")
        return False
    
    # Read current content
    with open(module_path, 'r') as f:
        content = f.read()
    
    # Find the principle section
    principle_marker = f"## {principle_num})"
    
    if principle_marker not in content:
        logger.error(f"Principle {principle_num} section not found in {module_name}")
        return False
    
    # Create example text
    date_str = datetime.now().strftime("%Y-%m-%d")
    example = f"""

**Example from lesson extraction ({date_str}):**
- Thread: {lesson['thread_id']}
- Issue: {lesson['description']}
"""
    
    if lesson.get('context'):
        example += f"- Context: {lesson['context']}\n"
    
    if lesson.get('outcome'):
        example += f"- Resolution: {lesson['outcome']}\n"
    
    # Find where to insert (before next ## or before --- if exists, or at end)
    # For now, append to end of file before final --- or at very end
    
    # Simple approach: append before the last "---" if it exists, else at end
    if '\n---\n' in content:
        parts = content.rsplit('\n---\n', 1)
        new_content = parts[0] + example + '\n---\n' + parts[1]
    else:
        new_content = content + example
    
    # Write back
    with open(module_path, 'w') as f:
        f.write(new_content)
    
    logger.info(f"✓ Updated {module_name} with lesson example")
    return True


def approve_lesson(lesson):
    """
    Approve a lesson and update principles
    
    Args:
        lesson: lesson dict
    
    Returns: bool success
    """
    print("\nApproving lesson and updating principles...")
    
    principle_refs = lesson.get('principle_refs', [])
    
    if not principle_refs:
        print("⚠️  No principle references - cannot update principles")
        create = input("Create new principle? (y/N): ").strip().lower()
        if create == 'y':
            print("→ New principle creation not yet implemented")
            print("   Please add principle reference and try again")
            return False
        else:
            return False
    
    # Update each referenced principle
    updated_count = 0
    for principle_num in principle_refs:
        if update_principle_with_lesson(principle_num, lesson):
            updated_count += 1
    
    if updated_count > 0:
        print(f"✓ Updated {updated_count} principle module(s)")
        lesson['status'] = 'approved'
        return True
    else:
        print("✗ Failed to update principles")
        return False


def archive_lesson(lesson, source_filepath):
    """
    Archive an approved lesson
    
    Args:
        lesson: lesson dict
        source_filepath: original file path
    
    Returns: archived filepath
    """
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Archive by month
    month_str = datetime.now().strftime("%Y-%m")
    thread_id = lesson['thread_id']
    filename = f"{month_str}_{thread_id}.lessons.jsonl"
    archive_path = ARCHIVE_DIR / filename
    
    # Append to archive file (may have multiple lessons from same thread)
    with open(archive_path, 'a') as f:
        f.write(json.dumps(lesson) + '\n')
    
    logger.info(f"Archived lesson to {archive_path}")
    
    return archive_path


def reject_lesson(lesson):
    """
    Reject a lesson (confirm and discard)
    
    Args:
        lesson: lesson dict
    
    Returns: bool confirmed
    """
    print("\n⚠️  Reject this lesson permanently?")
    confirm = input("Type 'yes' to confirm: ").strip().lower()
    
    if confirm == 'yes':
        reason = input("Rejection reason (optional): ").strip()
        if reason:
            logger.info(f"Rejected lesson: {lesson['title']} - Reason: {reason}")
        else:
            logger.info(f"Rejected lesson: {lesson['title']}")
        
        lesson['status'] = 'rejected'
        return True
    else:
        print("→ Rejection cancelled")
        return False


def review_lessons(lessons_data, dry_run=False, auto_approve=False):
    """
    Interactive review of lessons
    
    Args:
        lessons_data: list of (filepath, lessons) tuples
        dry_run: preview only, don't make changes
        auto_approve: automatically approve all lessons
    
    Returns: dict with review statistics
    """
    stats = {
        'total': 0,
        'approved': 0,
        'rejected': 0,
        'skipped': 0,
        'edited': 0
    }
    
    # Flatten lessons
    all_lessons = []
    lesson_to_file = {}
    
    for filepath, lessons in lessons_data:
        for lesson in lessons:
            all_lessons.append(lesson)
            lesson_to_file[lesson['lesson_id']] = filepath
    
    stats['total'] = len(all_lessons)
    
    if stats['total'] == 0:
        print("\n✓ No pending lessons to review")
        return stats
    
    print(f"\n{'='*70}")
    print(f"LESSON REVIEW SESSION")
    print(f"{'='*70}")
    print(f"Total lessons: {stats['total']}")
    
    if dry_run:
        print("DRY-RUN MODE: No changes will be made")
    
    if auto_approve:
        print("AUTO-APPROVE MODE: All lessons will be approved automatically")
    
    # Review each lesson
    for i, lesson in enumerate(all_lessons, 1):
        display_lesson(lesson, i, stats['total'])
        
        if auto_approve:
            action = 'approve'
        else:
            action = prompt_action()
        
        if action == 'approve':
            if dry_run:
                print("→ [DRY-RUN] Would approve lesson")
                stats['approved'] += 1
            else:
                if approve_lesson(lesson):
                    archive_lesson(lesson, lesson_to_file[lesson['lesson_id']])
                    stats['approved'] += 1
                else:
                    print("→ Approval failed, skipping")
                    stats['skipped'] += 1
        
        elif action == 'edit':
            lesson = edit_lesson(lesson)
            stats['edited'] += 1
            # Show again after edit
            display_lesson(lesson, i, stats['total'])
            action = prompt_action()
            if action == 'approve':
                if not dry_run:
                    if approve_lesson(lesson):
                        archive_lesson(lesson, lesson_to_file[lesson['lesson_id']])
                        stats['approved'] += 1
                    else:
                        stats['skipped'] += 1
        
        elif action == 'reject':
            if dry_run:
                print("→ [DRY-RUN] Would reject lesson")
                stats['rejected'] += 1
            else:
                if reject_lesson(lesson):
                    stats['rejected'] += 1
                else:
                    stats['skipped'] += 1
        
        elif action == 'skip':
            print("→ Skipped, will review next time")
            stats['skipped'] += 1
        
        elif action == 'quit':
            print("\n→ Review session ended early")
            break
    
    # Clean up processed files
    if not dry_run:
        for filepath, lessons in lessons_data:
            # Check if all lessons from this file were processed
            file_lessons = [l for l in lessons]
            processed = all(l.get('status') in ['approved', 'rejected'] for l in file_lessons)
            
            if processed:
                logger.info(f"Removing processed file: {filepath.name}")
                filepath.unlink()
    
    return stats


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Review pending lessons")
    parser.add_argument("--dry-run", action="store_true", help="Preview only, don't make changes")
    parser.add_argument("--auto-approve", action="store_true", help="Auto-approve all lessons")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Load pending lessons
        lessons_data = load_pending_lessons()
        
        if not lessons_data:
            print("\n✓ No pending lessons to review")
            return 0
        
        # Review lessons
        stats = review_lessons(lessons_data, dry_run=args.dry_run, auto_approve=args.auto_approve)
        
        # Print summary
        print("\n" + "="*70)
        print("REVIEW SUMMARY")
        print("="*70)
        print(f"Total lessons: {stats['total']}")
        print(f"Approved: {stats['approved']}")
        print(f"Rejected: {stats['rejected']}")
        print(f"Skipped: {stats['skipped']}")
        print(f"Edited: {stats['edited']}")
        print("="*70)
        
        if not args.dry_run:
            print("\n✓ Architectural principles updated with approved lessons")
            print("→ Remember to commit changes to git")
        
        return 0
        
    except Exception as e:
        logger.error(f"Review failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
