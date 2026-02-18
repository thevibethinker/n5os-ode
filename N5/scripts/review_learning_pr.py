#!/usr/bin/env python3
"""
Review Learning PRs - Va-side script to review and manage Zoputer learning PRs.

Checks for open PRs from the zoputer/learnings branch, assesses quality,
and either auto-merges high-confidence PRs or notifies V for review.

Usage:
    python3 N5/scripts/review_learning_pr.py check          # List open PRs
    python3 N5/scripts/review_learning_pr.py review         # Auto-review all open PRs
    python3 N5/scripts/review_learning_pr.py merge <number> # Manual merge specific PR
    python3 N5/scripts/review_learning_pr.py diff <number>  # Show PR diff
    python3 N5/scripts/review_learning_pr.py comment <number> <message>  # Add comment
"""

import argparse
import json
import os
import subprocess
import sys
import re
from pathlib import Path
from datetime import datetime

REPO = "vrijenattawar/zoputer-substrate"
LEARNING_BRANCH = "zoputer/learnings"
CONFIDENCE_THRESHOLD = 0.8


def run_gh(args: list[str], capture: bool = True) -> tuple[str, int]:
    """Run gh CLI command and return output and return code."""
    cmd = ["gh"] + args
    result = subprocess.run(cmd, capture_output=capture, text=True)
    return result.stdout.strip() if capture else "", result.returncode


def get_open_prs() -> list[dict]:
    """Get all open PRs from the zoputer/learnings branch."""
    output, code = run_gh([
        "pr", "list",
        "--repo", REPO,
        "--head", LEARNING_BRANCH,
        "--state", "open",
        "--json", "number,title,createdAt,url,additions,deletions,changedFiles"
    ])
    
    if code != 0 or not output:
        return []
    
    return json.loads(output)


def get_pr_diff(pr_number: int) -> str:
    """Get the diff content for a specific PR."""
    output, _ = run_gh([
        "pr", "diff", str(pr_number),
        "--repo", REPO
    ])
    return output


def get_pr_files(pr_number: int) -> list[dict]:
    """Get list of files changed in PR."""
    output, _ = run_gh([
        "pr", "view", str(pr_number),
        "--repo", REPO,
        "--json", "files"
    ])
    if output:
        data = json.loads(output)
        return data.get("files", [])
    return []


def assess_learning_quality(diff: str, files: list[dict]) -> dict:
    """
    Assess the quality of learning content in a PR.
    
    Returns:
        dict with keys: confidence (0-1), action (approve/reject/uncertain), feedback
    """
    issues = []
    positives = []
    
    # Check for sensitive patterns
    sensitive_patterns = [
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # emails
        r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # phone numbers
        r'\$\d+[,\d]*(?:\.\d{2})?\s*(?:USD|usd)?',  # dollar amounts with values
        r'(?:password|secret|token|api[_-]?key)\s*[:=]\s*\S+',  # credentials
        r'(?:SSN|social\s*security)\s*[:=]?\s*\d',  # SSN patterns
    ]
    
    for pattern in sensitive_patterns:
        if re.search(pattern, diff, re.IGNORECASE):
            issues.append(f"Potential sensitive data detected (pattern: {pattern[:30]}...)")
    
    # Check for proper YAML structure in learning files
    if "category:" in diff and "confidence:" in diff:
        positives.append("Proper YAML frontmatter structure")
    else:
        if "+++ b/Learnings/" in diff:  # Only if actually adding learning files
            issues.append("Learning file may be missing required frontmatter")
    
    # Check for reasonable confidence levels
    confidence_matches = re.findall(r'confidence:\s*([\d.]+)', diff)
    for conf in confidence_matches:
        try:
            conf_val = float(conf)
            if conf_val > 1.0 or conf_val < 0:
                issues.append(f"Invalid confidence value: {conf}")
            elif conf_val < 0.3:
                issues.append(f"Very low confidence learning: {conf}")
        except ValueError:
            issues.append(f"Non-numeric confidence value: {conf}")
    
    # Check file paths are in expected location
    for f in files:
        path = f.get("path", "")
        if not path.startswith("Learnings/"):
            issues.append(f"File outside Learnings/ directory: {path}")
    
    # Check for reasonable content length
    learning_additions = len([l for l in diff.split('\n') if l.startswith('+') and not l.startswith('+++')])
    if learning_additions > 500:
        issues.append(f"Very large addition ({learning_additions} lines) - manual review recommended")
    elif learning_additions > 10:
        positives.append(f"Reasonable content size ({learning_additions} lines)")
    
    # Calculate confidence and action
    if len(issues) == 0:
        confidence = 0.95
        action = "approve"
        feedback = "Learning content looks good. " + " ".join(positives)
    elif len(issues) <= 2 and all("sensitive" not in i.lower() for i in issues):
        confidence = 0.6
        action = "uncertain"
        feedback = f"Minor concerns: {'; '.join(issues)}"
    else:
        confidence = 0.3
        action = "reject" if any("sensitive" in i.lower() for i in issues) else "uncertain"
        feedback = f"Issues found: {'; '.join(issues)}"
    
    return {
        "confidence": confidence,
        "action": action,
        "feedback": feedback,
        "issues": issues,
        "positives": positives
    }


def approve_and_merge(pr_number: int, comment: str = None) -> bool:
    """Approve and merge a PR."""
    # Add approval comment
    if comment:
        run_gh([
            "pr", "comment", str(pr_number),
            "--repo", REPO,
            "--body", f"✅ Auto-approved by va review script.\n\n{comment}"
        ])
    
    # Merge the PR
    _, code = run_gh([
        "pr", "merge", str(pr_number),
        "--repo", REPO,
        "--merge",
        "--delete-branch"
    ])
    
    return code == 0


def request_changes(pr_number: int, feedback: str) -> bool:
    """Request changes on a PR with feedback."""
    _, code = run_gh([
        "pr", "comment", str(pr_number),
        "--repo", REPO,
        "--body", f"⚠️ Review needed:\n\n{feedback}\n\n*This is an automated review.*"
    ])
    return code == 0


def notify_v_for_review(pr: dict, assessment: dict) -> None:
    """Notify V that a PR needs manual review."""
    message = f"""🔍 Learning PR needs review

PR #{pr['number']}: {pr['title']}
URL: {pr['url']}

Assessment: {assessment['action']} (confidence: {assessment['confidence']:.0%})

{assessment['feedback']}

Run `python3 N5/scripts/review_learning_pr.py diff {pr['number']}` to see changes."""

    print(f"\n{'='*60}")
    print("📨 NOTIFICATION FOR V:")
    print(message)
    print(f"{'='*60}\n")


def cmd_check(args):
    """List all open learning PRs."""
    prs = get_open_prs()
    
    if not prs:
        print("No open PRs from zoputer/learnings branch.")
        return
    
    print(f"Found {len(prs)} open PR(s):\n")
    for pr in prs:
        created = pr.get('createdAt', 'unknown')[:10]
        print(f"  #{pr['number']} - {pr['title']}")
        print(f"      Created: {created} | +{pr.get('additions', 0)}/-{pr.get('deletions', 0)} | {pr.get('changedFiles', 0)} files")
        print(f"      URL: {pr['url']}\n")


def cmd_review(args):
    """Auto-review all open PRs."""
    prs = get_open_prs()
    
    if not prs:
        print("No open PRs to review.")
        return
    
    print(f"Reviewing {len(prs)} PR(s)...\n")
    
    for pr in prs:
        print(f"Reviewing PR #{pr['number']}: {pr['title']}")
        
        diff = get_pr_diff(pr['number'])
        files = get_pr_files(pr['number'])
        assessment = assess_learning_quality(diff, files)
        
        print(f"  Assessment: {assessment['action']} (confidence: {assessment['confidence']:.0%})")
        print(f"  Feedback: {assessment['feedback']}")
        
        if assessment['confidence'] > CONFIDENCE_THRESHOLD:
            if assessment['action'] == 'approve':
                if args.dry_run:
                    print(f"  [DRY RUN] Would approve and merge PR #{pr['number']}")
                else:
                    if approve_and_merge(pr['number'], assessment['feedback']):
                        print(f"  ✅ Approved and merged PR #{pr['number']}")
                    else:
                        print(f"  ❌ Failed to merge PR #{pr['number']}")
            else:
                if args.dry_run:
                    print(f"  [DRY RUN] Would request changes on PR #{pr['number']}")
                else:
                    request_changes(pr['number'], assessment['feedback'])
                    print(f"  📝 Requested changes on PR #{pr['number']}")
        else:
            notify_v_for_review(pr, assessment)
        
        print()


def cmd_merge(args):
    """Manually merge a specific PR."""
    pr_number = args.pr_number
    
    comment = f"Manually merged by va at {datetime.now().isoformat()}"
    if approve_and_merge(pr_number, comment):
        print(f"✅ Successfully merged PR #{pr_number}")
    else:
        print(f"❌ Failed to merge PR #{pr_number}")
        sys.exit(1)


def cmd_diff(args):
    """Show diff for a specific PR."""
    diff = get_pr_diff(args.pr_number)
    print(diff)


def cmd_comment(args):
    """Add a comment to a PR."""
    _, code = run_gh([
        "pr", "comment", str(args.pr_number),
        "--repo", REPO,
        "--body", args.message
    ])
    
    if code == 0:
        print(f"✅ Comment added to PR #{args.pr_number}")
    else:
        print(f"❌ Failed to add comment")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Review Zoputer learning PRs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # check command
    check_parser = subparsers.add_parser("check", help="List open learning PRs")
    check_parser.set_defaults(func=cmd_check)
    
    # review command
    review_parser = subparsers.add_parser("review", help="Auto-review all open PRs")
    review_parser.add_argument("--dry-run", "-n", action="store_true",
                               help="Show what would be done without taking action")
    review_parser.set_defaults(func=cmd_review)
    
    # merge command
    merge_parser = subparsers.add_parser("merge", help="Manually merge a specific PR")
    merge_parser.add_argument("pr_number", type=int, help="PR number to merge")
    merge_parser.set_defaults(func=cmd_merge)
    
    # diff command
    diff_parser = subparsers.add_parser("diff", help="Show diff for a PR")
    diff_parser.add_argument("pr_number", type=int, help="PR number")
    diff_parser.set_defaults(func=cmd_diff)
    
    # comment command
    comment_parser = subparsers.add_parser("comment", help="Add comment to a PR")
    comment_parser.add_argument("pr_number", type=int, help="PR number")
    comment_parser.add_argument("message", help="Comment message")
    comment_parser.set_defaults(func=cmd_comment)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == "__main__":
    main()
