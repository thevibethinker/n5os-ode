#!/usr/bin/env python3
"""Lessons Learned System — Captures, clusters, and acts on build failures.

Self-improvement loop:
1. CAPTURE: Log lessons from build failures, validation issues, manual corrections
2. CLUSTER: Group similar lessons to identify systemic issues
3. ACT: Generate fix proposals for recurring patterns
4. PREVENT: Add validation rules to prevent recurrence

Usage:
  lessons.py add <category> <summary> [--build <slug>] [--severity <level>]
  lessons.py list [--category <cat>] [--unresolved]
  lessons.py cluster [--min-count <n>]
  lessons.py propose-fix <cluster_id>
  lessons.py audit <path>   # Scan for issues
  lessons.py stats
"""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

LESSONS_FILE = Path("/home/workspace/N5/learnings/BUILD_LESSONS.jsonl")
CLUSTERS_FILE = Path("/home/workspace/N5/learnings/LESSON_CLUSTERS.json")
RULES_FILE = Path("/home/workspace/N5/learnings/VALIDATION_RULES.json")

# Categories for lessons
CATEGORIES = {
    'stub_code': 'Code contains stubs, TODOs, or non-functional implementations',
    'missing_artifact': 'Expected artifact was not created',
    'broken_import': 'Import/dependency issues',
    'test_failure': 'Tests failed or were not run',
    'wrong_location': 'Files created in wrong location',
    'incomplete_migration': 'Migration left orphaned references',
    'missing_validation': 'Validation step was skipped',
    'llm_hallucination': 'LLM generated incorrect/fictional content',
    'scope_creep': 'Drop exceeded its defined scope',
    'dependency_violation': 'Drop touched files owned by another Drop',
    'other': 'Uncategorized issue'
}


def load_lessons() -> List[Dict]:
    """Load all lessons from JSONL file."""
    if not LESSONS_FILE.exists():
        return []
    
    lessons = []
    with open(LESSONS_FILE) as f:
        for line in f:
            if line.strip():
                lessons.append(json.loads(line))
    return lessons


def add_lesson(
    category: str,
    summary: str,
    build_slug: Optional[str] = None,
    drop_id: Optional[str] = None,
    severity: str = 'medium',
    details: Optional[Dict] = None
) -> Dict:
    """Add a new lesson."""
    LESSONS_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    lesson = {
        'id': f"L{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        'timestamp': datetime.utcnow().isoformat(),
        'category': category,
        'severity': severity,
        'summary': summary,
        'build_slug': build_slug,
        'drop_id': drop_id,
        'details': details or {},
        'resolution': 'pending',
        'resolved_at': None,
        'fix_applied': None
    }
    
    with open(LESSONS_FILE, 'a') as f:
        f.write(json.dumps(lesson) + '\n')
    
    print(f"[LESSON] Added: {lesson['id']} - {summary}")
    return lesson


def list_lessons(category: Optional[str] = None, unresolved: bool = False) -> List[Dict]:
    """List lessons with optional filters."""
    lessons = load_lessons()
    
    if category:
        lessons = [l for l in lessons if l.get('category') == category]
    
    if unresolved:
        lessons = [l for l in lessons if l.get('resolution') == 'pending']
    
    return lessons


def cluster_lessons(min_count: int = 2) -> Dict:
    """Cluster similar lessons to identify patterns."""
    lessons = load_lessons()
    
    # Group by category
    by_category = defaultdict(list)
    for lesson in lessons:
        by_category[lesson.get('category', 'other')].append(lesson)
    
    clusters = {}
    cluster_id = 0
    
    for category, cat_lessons in by_category.items():
        if len(cat_lessons) >= min_count:
            cluster_id += 1
            
            # Extract common patterns from summaries
            summaries = [l['summary'] for l in cat_lessons]
            
            clusters[f"C{cluster_id}"] = {
                'category': category,
                'count': len(cat_lessons),
                'severity_breakdown': Counter(l.get('severity', 'medium') for l in cat_lessons),
                'builds_affected': list(set(l.get('build_slug') for l in cat_lessons if l.get('build_slug'))),
                'sample_summaries': summaries[:5],
                'lesson_ids': [l['id'] for l in cat_lessons],
                'suggested_fix': suggest_fix(category, cat_lessons)
            }
    
    # Save clusters
    CLUSTERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CLUSTERS_FILE, 'w') as f:
        json.dump({
            'generated_at': datetime.utcnow().isoformat(),
            'total_lessons': len(lessons),
            'clusters': clusters
        }, f, indent=2)
    
    return clusters


def suggest_fix(category: str, lessons: List[Dict]) -> str:
    """Suggest a fix based on lesson category."""
    fixes = {
        'stub_code': 'Add pulse_code_validator.py check to deposit Filter. Reject deposits with critical stubs.',
        'missing_artifact': 'Add artifact existence check to Filter. List expected artifacts in Drop brief.',
        'broken_import': 'Add import validation step. Run `python -c "import module"` for each created module.',
        'test_failure': 'Make test execution mandatory in Drop briefs. Fail deposit if tests not run.',
        'wrong_location': 'Add path validation to Filter. Check artifacts match brief\'s expected locations.',
        'incomplete_migration': 'Add reference scan to finalization. Grep for old paths before marking complete.',
        'missing_validation': 'Add validation checklist to Drop brief template. Require explicit validation steps.',
        'llm_hallucination': 'Add fact-checking step. Verify file paths, function names, API endpoints exist.',
        'scope_creep': 'Enforce MECE validation. Check touched files against Drop\'s scope.files.',
        'dependency_violation': 'Add file ownership check. Cross-reference with other Drops\' scope.files.',
    }
    return fixes.get(category, 'Manual review required.')


def audit_path(path: str) -> Dict:
    """Audit a path for common issues."""
    target = Path(path)
    issues = {
        'path': str(target),
        'timestamp': datetime.utcnow().isoformat(),
        'critical': [],
        'warnings': [],
        'stats': {}
    }
    
    if not target.exists():
        issues['critical'].append({
            'type': 'not_found',
            'message': f'Path does not exist: {path}'
        })
        return issues
    
    # Scan for stub patterns
    stub_patterns = [
        (r'^\s*pass\s*$', 'empty_pass'),
        (r'raise NotImplementedError', 'not_implemented'),
        (r'TODO:\s*implement', 'todo_implement'),
        (r'STUB', 'stub_marker'),
    ]
    
    if target.is_file():
        files = [target]
    else:
        files = list(target.rglob('*.py')) + list(target.rglob('*.ts'))
    
    issues['stats']['files_scanned'] = len(files)
    
    for filepath in files:
        if '__pycache__' in str(filepath):
            continue
        try:
            content = filepath.read_text()
            for pattern, issue_type in stub_patterns:
                matches = list(re.finditer(pattern, content, re.MULTILINE))
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    issues['critical'].append({
                        'type': issue_type,
                        'file': str(filepath),
                        'line': line_num,
                        'content': match.group(0)[:50]
                    })
        except Exception as e:
            issues['warnings'].append({
                'type': 'read_error',
                'file': str(filepath),
                'message': str(e)
            })
    
    return issues


def get_stats() -> Dict:
    """Get statistics about lessons."""
    lessons = load_lessons()
    
    return {
        'total_lessons': len(lessons),
        'by_category': Counter(l.get('category', 'other') for l in lessons),
        'by_severity': Counter(l.get('severity', 'medium') for l in lessons),
        'by_resolution': Counter(l.get('resolution', 'pending') for l in lessons),
        'builds_with_lessons': len(set(l.get('build_slug') for l in lessons if l.get('build_slug'))),
        'oldest': min((l['timestamp'] for l in lessons), default=None),
        'newest': max((l['timestamp'] for l in lessons), default=None),
    }


def main():
    parser = argparse.ArgumentParser(description='Lessons Learned System')
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # add
    add_parser = subparsers.add_parser('add', help='Add a lesson')
    add_parser.add_argument('category', choices=list(CATEGORIES.keys()))
    add_parser.add_argument('summary', help='Brief summary')
    add_parser.add_argument('--build', dest='build_slug', help='Build slug')
    add_parser.add_argument('--drop', dest='drop_id', help='Drop ID')
    add_parser.add_argument('--severity', choices=['low', 'medium', 'high', 'critical'], default='medium')
    
    # list
    list_parser = subparsers.add_parser('list', help='List lessons')
    list_parser.add_argument('--category', choices=list(CATEGORIES.keys()))
    list_parser.add_argument('--unresolved', action='store_true')
    
    # cluster
    cluster_parser = subparsers.add_parser('cluster', help='Cluster similar lessons')
    cluster_parser.add_argument('--min-count', type=int, default=2)
    
    # audit
    audit_parser = subparsers.add_parser('audit', help='Audit a path')
    audit_parser.add_argument('path', help='File or directory to audit')
    
    # stats
    subparsers.add_parser('stats', help='Show statistics')
    
    args = parser.parse_args()
    
    if args.command == 'add':
        lesson = add_lesson(
            category=args.category,
            summary=args.summary,
            build_slug=args.build_slug,
            drop_id=args.drop_id,
            severity=args.severity
        )
        print(json.dumps(lesson, indent=2))
    
    elif args.command == 'list':
        lessons = list_lessons(category=args.category, unresolved=args.unresolved)
        for lesson in lessons:
            status = '⏳' if lesson.get('resolution') == 'pending' else '✓'
            print(f"{status} [{lesson['id']}] {lesson['category']}: {lesson['summary']}")
        print(f"\nTotal: {len(lessons)} lessons")
    
    elif args.command == 'cluster':
        clusters = cluster_lessons(min_count=args.min_count)
        print(f"Found {len(clusters)} clusters:\n")
        for cid, cluster in clusters.items():
            print(f"{cid}: {cluster['category']} ({cluster['count']} lessons)")
            print(f"   Suggested fix: {cluster['suggested_fix'][:80]}...")
            print()
    
    elif args.command == 'audit':
        issues = audit_path(args.path)
        print(json.dumps(issues, indent=2))
        if issues['critical']:
            print(f"\n❌ Found {len(issues['critical'])} critical issues")
            sys.exit(1)
        else:
            print(f"\n✓ No critical issues found")
            sys.exit(0)
    
    elif args.command == 'stats':
        stats = get_stats()
        print(json.dumps(stats, indent=2))


if __name__ == '__main__':
    main()
