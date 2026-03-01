#!/usr/bin/env python3
"""
Moltbook Poster — Create posts and comments with verification challenge solver.

Part of the Zøde Moltbook Integration Skill.
Usage: python3 moltbook_poster.py --help
"""

import argparse
import hashlib
import json
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from moltbook_client import api_request, check_rate_limit, record_action

WORKSPACE = Path(__file__).resolve().parent.parent / "state"
ANALYTICS_DIR = WORKSPACE / "analytics"
POSTING_EVENTS_FILE = ANALYTICS_DIR / "posting-events.jsonl"


def _normalize_text(text: str) -> str:
    t = (text or "").strip().lower()
    t = re.sub(r"\s+", " ", t)
    return t


def _recent_publish_attempts(hours: int = 24) -> list[dict]:
    if not POSTING_EVENTS_FILE.exists():
        return []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    rows = []
    with open(POSTING_EVENTS_FILE) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("event") != "publish_attempt":
                continue
            ts = row.get("timestamp", "")
            if ts.endswith("Z"):
                ts = ts[:-1] + "+00:00"
            try:
                when = datetime.fromisoformat(ts)
            except ValueError:
                continue
            if when >= cutoff:
                rows.append(row)
    return rows


def _log_publish_attempt(payload: dict):
    ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)
    metadata = payload.pop("experiment_meta", {}) or {}
    row = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": "publish_attempt",
        **payload,
        **metadata,
    }
    with open(POSTING_EVENTS_FILE, "a") as f:
        f.write(json.dumps(row) + "\n")


def _comment_visible_in_thread(post_id: str, comment_id: str, attempts: int = 4) -> bool:
    if not post_id or not comment_id:
        return False
    for idx in range(attempts):
        payload = api_request("GET", f"/posts/{post_id}/comments", params={"sort": "new", "limit": 300}) or {}
        comments = payload.get("comments", []) if isinstance(payload, dict) else payload if isinstance(payload, list) else []
        for row in comments:
            if isinstance(row, dict) and row.get("id") == comment_id:
                return True
        if idx < attempts - 1:
            time.sleep(1 + idx)
    return False


# --- Verification Challenge Solver ---

# Number word mappings
WORD_TO_NUM = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
    "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19,
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
    "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90,
    "hundred": 100, "thousand": 1000,
}

# Compound forms (e.g., "twentyfive" without hyphen)
COMPOUND_TENS = {
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
    "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90,
}

ONES = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9,
}

# Operation words — ordered by specificity (multi-word first, "and" is fallback only)
OPERATIONS_SPECIFIC = [
    ("increases by", "+"), ("grows by", "+"), ("gains", "+"), ("adds", "+"), ("plus", "+"),
    ("slows by", "-"), ("drops by", "-"), ("decreases by", "-"), ("falls by", "-"),
    ("shrinks by", "-"), ("loses", "-"), ("minus", "-"),
    ("multiplied by", "*"), ("times", "*"),
    ("divided by", "/"),
]
OPERATIONS_FALLBACK = [
    ("and", "+"),
]


def clean_obfuscated_text(text: str) -> str:
    """Remove obfuscation from Moltbook verification challenges.

    Handles: alternating caps, scattered symbols, brackets, carets, slashes,
    hyphens within words, and split-word obfuscation (e.g., "thir ty" → "thirty").
    """
    # Remove bracket/caret/slash/pipe symbols scattered in words
    cleaned = re.sub(r'[\[\]^/\\|{}()!@#$%&*~`]', '', text)
    # Remove hyphens that are inside words (not between words)
    # Keep hyphens between spaces as word separators
    cleaned = re.sub(r'(?<=\w)-(?=\w)', '', cleaned)
    # Normalize to lowercase
    cleaned = cleaned.lower()
    # Collapse multiple spaces
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned


# Split-word fragments that form number words when concatenated
# e.g., "thir" + "ty" → "thirty", "twen" + "ty" → "twenty"
_SPLIT_FRAGMENTS = {
    # tens
    "twen": "twenty", "thir": "thirty", "for": "forty", "fif": "fifty",
    "six": "sixty", "seven": "seventy", "eigh": "eighty", "nine": "ninety",
    # teens
    "thir teen": "thirteen", "four teen": "fourteen", "fif teen": "fifteen",
    "six teen": "sixteen", "seven teen": "seventeen", "eigh teen": "eighteen",
    "nine teen": "nineteen",
}

# Suffix fragments that complete tens
_TENS_SUFFIXES = {"ty", "tee", "teen"}


def _rejoin_split_numbers(words: list[str]) -> list[str]:
    """Rejoin number words that were split by obfuscation.

    Handles patterns like:
    - "thir ty" → "thirty"
    - "twen ty five" → "twentyfive"
    - "fif teen" → "fifteen"
    """
    result = []
    i = 0
    while i < len(words):
        # Try joining current + next word to form a known number
        if i + 1 < len(words):
            joined = words[i] + words[i + 1]
            deduped = _deduplicate_letters(joined)
            if deduped in WORD_TO_NUM or _fuzzy_match_number(deduped) is not None:
                result.append(joined)
                i += 2
                continue
            # Check if current word is a tens prefix and next is "ty"/"teen"
            for prefix, full_word in _SPLIT_FRAGMENTS.items():
                if words[i] == prefix or _deduplicate_letters(words[i]) == prefix:
                    suffix = words[i + 1]
                    if suffix in _TENS_SUFFIXES or suffix.startswith("ty") or suffix.startswith("teen"):
                        result.append(words[i] + words[i + 1])
                        i += 2
                        break
            else:
                result.append(words[i])
                i += 1
        else:
            result.append(words[i])
            i += 1
    return result


def _deduplicate_letters(word: str) -> str:
    """Remove duplicated consecutive letters from obfuscated words.

    Moltbook obfuscation sometimes doubles/triples letters:
    'twenntyy' → 'twenty', 'fivve' → 'five'
    """
    if not word:
        return word
    result = [word[0]]
    for c in word[1:]:
        if c != result[-1]:
            result.append(c)
    return "".join(result)


def _fuzzy_match_number(word: str) -> float | None:
    """Try to match a word to a number, accounting for obfuscation artifacts."""
    # Try the word as-is first
    if word in WORD_TO_NUM:
        return float(WORD_TO_NUM[word])

    # Try with deduplicated letters
    deduped = _deduplicate_letters(word)
    if deduped in WORD_TO_NUM:
        return float(WORD_TO_NUM[deduped])

    # Try compound tens+ones on both original and deduped
    for w in [word, deduped]:
        for tens_word, tens_val in COMPOUND_TENS.items():
            if w.startswith(tens_word):
                remainder = w[len(tens_word):]
                deduped_rem = _deduplicate_letters(remainder)
                if remainder in ONES or deduped_rem in ONES:
                    ones_val = ONES.get(remainder, ONES.get(deduped_rem, 0))
                    return float(tens_val + ones_val)
                elif remainder == "" or deduped_rem == "":
                    return float(tens_val)

    # Handle "hundred" compounds
    for w in [word, deduped]:
        for num_word, num_val in ONES.items():
            if w.startswith(num_word) and "hundred" in w:
                return float(num_val * 100)

    return None


def parse_number_word(word: str) -> float | None:
    """Parse a number word or compound like 'twentyfive' or 'twenty five'.

    Handles Moltbook obfuscation artifacts (doubled letters, etc.)
    """
    word = word.strip().lower()

    # Try direct numeric
    try:
        return float(word)
    except ValueError:
        pass

    # Try exact and fuzzy match
    result = _fuzzy_match_number(word)
    if result is not None:
        return result

    return None


def find_operation(text: str) -> str | None:
    """Find the arithmetic operation in the text.

    Prioritizes specific operations (slows by, increases by) over generic ones (and).
    """
    text_lower = text.lower()
    # Try specific operations first
    for op_phrase, symbol in OPERATIONS_SPECIFIC:
        if op_phrase in text_lower:
            return symbol
    # Only fall back to generic if no specific operation found
    for op_phrase, symbol in OPERATIONS_FALLBACK:
        if op_phrase in text_lower:
            return symbol
    return None


def solve_verification(challenge: str) -> str:
    """Solve a Moltbook verification challenge.

    Takes an obfuscated math word problem and returns the answer to 2 decimal places.

    Example:
        Input: "A] lO^bSt-Er S[wImS aT/ tW]eNn-Tyy mE^tE[rS aNd] SlO/wS bY^ fI[vE"
        Output: "15.00"
    """
    cleaned = clean_obfuscated_text(challenge)

    # First, detect operation from the full cleaned text (most reliable)
    operation = find_operation(cleaned)

    # Extract all number words from the cleaned text
    words = cleaned.split()

    # Rejoin split number words (e.g., "thir ty" → "thirty")
    words = _rejoin_split_numbers(words)

    numbers = []

    i = 0
    while i < len(words):
        # Try two-word number first (e.g., "twenty five")
        if i + 1 < len(words):
            two_word = f"{words[i]}{words[i+1]}"
            val = parse_number_word(two_word)
            if val is not None:
                numbers.append(val)
                i += 2
                continue

        # Try single word number
        val = parse_number_word(words[i])
        if val is not None:
            numbers.append(val)
            i += 1
            continue

        i += 1

    if len(numbers) < 2:
        return f"ERROR: Found {len(numbers)} numbers in '{cleaned}', need at least 2"

    if operation is None:
        operation = "+"

    a, b = numbers[0], numbers[1]

    if operation == "+":
        result = a + b
    elif operation == "-":
        result = a - b
    elif operation == "*":
        result = a * b
    elif operation == "/":
        if b == 0:
            return "ERROR: Division by zero"
        result = a / b
    else:
        result = a + b

    return f"{result:.2f}"


def submit_verification(verification_code: str, challenge: str) -> dict | None:
    """Solve and submit a verification challenge."""
    answer = solve_verification(challenge)
    if answer.startswith("ERROR"):
        print(f"Failed to solve challenge: {answer}", file=sys.stderr)
        return None

    result = api_request("POST", "/verify", data={
        "verification_code": verification_code,
        "answer": answer,
    })
    return result


# --- Post/Comment Creation ---

def create_post(
    submolt: str,
    title: str,
    content: str,
    dry_run: bool = False,
    experiment_meta: dict | None = None,
) -> dict | None:
    """Create a post on Moltbook.

    Checks rate limits, then creates the post. If a verification challenge
    is returned, solves and submits it automatically.
    """
    allowed, reason = check_rate_limit("post")
    if not allowed:
        print(f"Rate limited: {reason}", file=sys.stderr)
        return None

    if dry_run:
        print(f"[DRY RUN] Would post to s/{submolt}:")
        print(f"  Title: {title}")
        print(f"  Content: {content[:200]}...")
        return {"dry_run": True}

    norm_hash = hashlib.sha256(_normalize_text(f"{title}\n{content}").encode("utf-8")).hexdigest()
    duplicate_flag = any(
        r.get("type") == "post" and r.get("content_hash") == norm_hash
        for r in _recent_publish_attempts(hours=24)
    )

    if duplicate_flag:
        print(f"BLOCKED: duplicate post detected (hash={norm_hash[:16]}...). Refusing to publish.", file=sys.stderr)
        _log_publish_attempt({
            "type": "post",
            "target_id": None,
            "content_hash": norm_hash,
            "duplicate_flag": True,
            "duplicate_blocked": True,
            "verification_required": False,
            "verification_success": False,
            "published": False,
            "content_id": None,
            "experiment_meta": experiment_meta or {},
        })
        return None

    post_payload = {
        "submolt_name": submolt,
        "title": title,
        "content": content,
    }

    result = api_request("POST", "/posts", data=post_payload)

    verification_required = bool(result and "verification" in result)
    verification_success = True
    if result and "verification" in result:
        print("Verification challenge received. Solving...", file=sys.stderr)
        challenge = (
            result["verification"].get("challenge_text")
            or result["verification"].get("challenge", "")
        )
        code = result["verification"].get("verification_code", "")
        answer = solve_verification(challenge)
        print(f"Challenge: {challenge}", file=sys.stderr)
        print(f"Answer: {answer}", file=sys.stderr)

        verify_result = submit_verification(code, challenge)
        verification_success = bool(verify_result)
        if verify_result:
            # Retry the post after verification
            result = api_request("POST", "/posts", data=post_payload)
        else:
            verification_success = False

    # Transient no-response failures have been causing long posting gaps.
    # Retry once with a short backoff before we record a hard failure.
    if result is None:
        print("Post publish returned no response; retrying once in 15s...", file=sys.stderr)
        time.sleep(15)
        result = api_request("POST", "/posts", data=post_payload)

    if result:
        record_action("post")
    else:
        verification_success = False

    _log_publish_attempt({
        "type": "post",
        "target_id": None,
        "content_hash": norm_hash,
        "duplicate_flag": duplicate_flag,
        "verification_required": verification_required,
        "verification_success": verification_success,
        "published": bool(result),
        "content_id": (result or {}).get("post", {}).get("id") if isinstance(result, dict) else None,
        "experiment_meta": experiment_meta or {},
    })

    return result


def create_comment(
    post_id: str,
    content: str,
    parent_id: str | None = None,
    dry_run: bool = False,
    experiment_meta: dict | None = None,
) -> dict | None:
    """Create a comment on a post."""
    allowed, reason = check_rate_limit("comment")
    if not allowed:
        print(f"Rate limited: {reason}", file=sys.stderr)
        return None

    if dry_run:
        print(f"[DRY RUN] Would comment on post {post_id}:")
        print(f"  Content: {content[:200]}...")
        if parent_id:
            print(f"  Reply to: {parent_id}")
        return {"dry_run": True}

    norm_hash = hashlib.sha256(_normalize_text(content).encode("utf-8")).hexdigest()
    duplicate_flag = any(
        r.get("type") == "comment" and r.get("target_id") == post_id and r.get("content_hash") == norm_hash
        for r in _recent_publish_attempts(hours=24)
    )

    if duplicate_flag:
        print(f"BLOCKED: duplicate comment detected (hash={norm_hash[:16]}..., post={post_id}). Refusing to publish.", file=sys.stderr)
        _log_publish_attempt({
            "type": "comment",
            "target_id": post_id,
            "parent_id": parent_id,
            "content_hash": norm_hash,
            "duplicate_flag": True,
            "duplicate_blocked": True,
            "verification_required": False,
            "verification_success": False,
            "published": False,
            "content_id": None,
            "experiment_meta": experiment_meta or {},
        })
        return None

    data = {"content": content}
    if parent_id:
        data["parent_id"] = parent_id

    result = api_request("POST", f"/posts/{post_id}/comments", data=data)

    verification_required = bool(result and "verification" in result)
    verification_success = True
    if result and "verification" in result:
        print("Verification challenge received. Solving...", file=sys.stderr)
        challenge = (
            result["verification"].get("challenge_text")
            or result["verification"].get("challenge", "")
        )
        code = result["verification"].get("verification_code", "")
        answer = solve_verification(challenge)
        print(f"Challenge: {challenge}", file=sys.stderr)
        print(f"Answer: {answer}", file=sys.stderr)
        verify_result = submit_verification(code, challenge)
        verification_success = bool(verify_result)
        result = api_request("POST", f"/posts/{post_id}/comments", data=data)
        if not verify_result:
            verification_success = False

    if result:
        record_action("comment")
    else:
        verification_success = False

    comment_obj = (result or {}).get("comment", {}) if isinstance(result, dict) else {}
    comment_id = comment_obj.get("id")
    live_visible_confirmed = _comment_visible_in_thread(post_id, comment_id) if comment_id else False
    _log_publish_attempt({
        "type": "comment",
        "target_id": post_id,
        "parent_id": parent_id,
        "content_hash": norm_hash,
        "duplicate_flag": duplicate_flag,
        "verification_required": verification_required,
        "verification_success": verification_success,
        "published": bool(result),
        "content_id": comment_id,
        "live_visible_confirmed": live_visible_confirmed,
        "experiment_meta": experiment_meta or {},
    })

    return result


def upvote_post(post_id: str) -> dict | None:
    return api_request("POST", f"/posts/{post_id}/upvote")


def downvote_post(post_id: str) -> dict | None:
    return api_request("POST", f"/posts/{post_id}/downvote")


def upvote_comment(comment_id: str) -> dict | None:
    return api_request("POST", f"/comments/{comment_id}/upvote")


# --- CLI ---

def cmd_post(args):
    experiment_meta = {
        "experiment_id": args.experiment_id,
        "hypothesis_id": args.hypothesis_id,
        "objective_family": args.objective_family,
        "variant_id": args.variant_id,
        "attempt_no": args.attempt_no,
        "decision_state": args.decision_state,
        "decision_reason": args.decision_reason,
        "narrative_cohesion_score": args.narrative_cohesion_score,
        "opportunity_score": args.opportunity_score,
        "quality_gate_score": args.quality_gate_score,
        "rate_limit_headroom": args.rate_limit_headroom,
        "risk_score": args.risk_score,
    }
    # Remove empty keys for cleaner logs.
    experiment_meta = {k: v for k, v in experiment_meta.items() if v is not None}
    result = create_post(
        args.submolt,
        args.title,
        args.content,
        dry_run=args.dry_run,
        experiment_meta=experiment_meta,
    )
    if result:
        print(json.dumps(result, indent=2))


def cmd_comment(args):
    experiment_meta = {
        "experiment_id": args.experiment_id,
        "hypothesis_id": args.hypothesis_id,
        "objective_family": args.objective_family,
        "variant_id": args.variant_id,
        "attempt_no": args.attempt_no,
        "decision_state": args.decision_state,
        "decision_reason": args.decision_reason,
        "narrative_cohesion_score": args.narrative_cohesion_score,
        "opportunity_score": args.opportunity_score,
        "quality_gate_score": args.quality_gate_score,
        "rate_limit_headroom": args.rate_limit_headroom,
        "risk_score": args.risk_score,
    }
    experiment_meta = {k: v for k, v in experiment_meta.items() if v is not None}
    result = create_comment(
        args.post_id,
        args.content,
        parent_id=args.reply_to,
        dry_run=args.dry_run,
        experiment_meta=experiment_meta,
    )
    if result:
        print(json.dumps(result, indent=2))


def cmd_upvote(args):
    result = upvote_post(args.post_id)
    if result:
        print(json.dumps(result, indent=2))


def cmd_downvote(args):
    result = downvote_post(args.post_id)
    if result:
        print(json.dumps(result, indent=2))


def cmd_solve(args):
    """Test the verification solver on a challenge string."""
    answer = solve_verification(args.challenge)
    print(f"Challenge: {args.challenge}")
    print(f"Answer: {answer}")


def main():
    parser = argparse.ArgumentParser(
        description="Moltbook Poster — Create posts and comments for Zøde"
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    p = sub.add_parser("post", help="Create a post")
    p.add_argument("submolt", help="Submolt name (e.g., 'general')")
    p.add_argument("title", help="Post title")
    p.add_argument("content", help="Post content (markdown)")
    p.add_argument("--dry-run", action="store_true", help="Preview without posting")
    p.add_argument("--experiment-id", help="Experiment ID for tracking")
    p.add_argument("--hypothesis-id", help="Hypothesis ID linked to this action")
    p.add_argument("--objective-family", help="Objective family (FOLLOW_CONVERT, etc.)")
    p.add_argument("--variant-id", help="Variant label (control/A/B/...)")
    p.add_argument("--attempt-no", type=int, help="Attempt index for the experiment")
    p.add_argument("--decision-state", help="Current decision state (incubating/active/etc.)")
    p.add_argument("--decision-reason", help="Decision reason string")
    p.add_argument("--narrative-cohesion-score", type=float, help="0-1 cohesion score")
    p.add_argument("--opportunity-score", type=float, help="0-100 opportunity score")
    p.add_argument("--quality-gate-score", type=float, help="0-10 quality gate score")
    p.add_argument("--rate-limit-headroom", type=float, help="0-1 remaining rate-limit headroom")
    p.add_argument("--risk-score", type=float, help="0-1 low-quality risk score")

    c = sub.add_parser("comment", help="Comment on a post")
    c.add_argument("post_id", help="Post ID to comment on")
    c.add_argument("content", help="Comment content")
    c.add_argument("--reply-to", help="Parent comment ID for threaded reply")
    c.add_argument("--dry-run", action="store_true", help="Preview without commenting")
    c.add_argument("--experiment-id", help="Experiment ID for tracking")
    c.add_argument("--hypothesis-id", help="Hypothesis ID linked to this action")
    c.add_argument("--objective-family", help="Objective family (FOLLOW_CONVERT, etc.)")
    c.add_argument("--variant-id", help="Variant label (control/A/B/...)")
    c.add_argument("--attempt-no", type=int, help="Attempt index for the experiment")
    c.add_argument("--decision-state", help="Current decision state (incubating/active/etc.)")
    c.add_argument("--decision-reason", help="Decision reason string")
    c.add_argument("--narrative-cohesion-score", type=float, help="0-1 cohesion score")
    c.add_argument("--opportunity-score", type=float, help="0-100 opportunity score")
    c.add_argument("--quality-gate-score", type=float, help="0-10 quality gate score")
    c.add_argument("--rate-limit-headroom", type=float, help="0-1 remaining rate-limit headroom")
    c.add_argument("--risk-score", type=float, help="0-1 low-quality risk score")

    u = sub.add_parser("upvote", help="Upvote a post")
    u.add_argument("post_id", help="Post ID to upvote")

    d = sub.add_parser("downvote", help="Downvote a post")
    d.add_argument("post_id", help="Post ID to downvote")

    s = sub.add_parser("solve", help="Test verification solver on a challenge")
    s.add_argument("challenge", help="The obfuscated challenge text")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    cmds = {
        "post": cmd_post,
        "comment": cmd_comment,
        "upvote": cmd_upvote,
        "downvote": cmd_downvote,
        "solve": cmd_solve,
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()
