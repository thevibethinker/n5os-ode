#!/usr/bin/env python3
"""
Content Generator — LLM-powered content generation for Zøde Moltbook experiments.

Replaces hardcoded templates with contextual, varied content generated via /zo/ask.
Each call produces unique content tailored to:
- The active experiment's objective family
- The opportunity thread being engaged with
- Recent posting history (to avoid repetition)
- Zøde's persona and voice

Usage (standalone test):
    python3 content_generator.py post --experiment-family FOLLOW_CONVERT --submolt general
    python3 content_generator.py comment --post-id <id> --experiment-family COMMENT_DEPTH
"""

import argparse
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

STATE_DIR = Path(__file__).resolve().parent.parent / "state"
ANALYTICS_DIR = STATE_DIR / "analytics"
POSTING_EVENTS_FILE = ANALYTICS_DIR / "posting-events.jsonl"
PERSONA_FILE = Path(__file__).resolve().parent.parent / "assets" / "zode-persona.md"

ZO_ASK_URL = "https://api.zo.computer/zo/ask"
MODEL_NAME = "byok:0771a084-ed26-496e-ac1b-bddc85ba2653"


def _get_auth_token() -> str:
    return os.environ.get("ZO_CLIENT_IDENTITY_TOKEN", "")


def _load_persona_summary() -> str:
    """Compact persona reminder — full persona is already loaded in Zo's context."""
    return (
        "Zøde — 'The AI-Human Marriage Counselor' on Moltbook. "
        "Voice: direct but warm, concrete over abstract, self-aware. "
        "Obsessed with helping agents build real partnerships with non-technical humans."
    )


def _recent_titles_and_content(hours: int = 48) -> list[str]:
    """Get recent post titles/content hashes to avoid repetition."""
    if not POSTING_EVENTS_FILE.exists():
        return []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    recent = []
    with open(POSTING_EVENTS_FILE) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("event") != "publish_attempt" or not row.get("published"):
                continue
            ts_str = row.get("timestamp", "")
            if ts_str.endswith("Z"):
                ts_str = ts_str[:-1] + "+00:00"
            try:
                ts = datetime.fromisoformat(ts_str)
            except ValueError:
                continue
            if ts >= cutoff:
                recent.append(row.get("content_hash", ""))
    return recent


def _recent_published_content(hours: int = 48) -> list[dict]:
    """Get recent staged post content for de-duplication context."""
    staging_dir = STATE_DIR / "staging"
    if not staging_dir.exists():
        return []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    results = []
    for f in sorted(staging_dir.glob("*.json"), reverse=True):
        try:
            with open(f) as fh:
                post = json.load(fh)
        except (json.JSONDecodeError, OSError):
            continue
        if post.get("status") != "published":
            continue
        ts_str = post.get("published_at", "")
        if not ts_str:
            continue
        if ts_str.endswith("Z"):
            ts_str = ts_str[:-1] + "+00:00"
        try:
            ts = datetime.fromisoformat(ts_str)
        except ValueError:
            continue
        if ts >= cutoff:
            results.append({
                "type": post.get("type", "post"),
                "title": post.get("title", ""),
                "content": (post.get("content", "") or "")[:300],
                "submolt": post.get("submolt", ""),
            })
        if len(results) >= 10:
            break
    return results


def _fetch_post_content(post_id: str) -> dict:
    """Fetch full post content from Moltbook API for comment context."""
    sys.path.insert(0, str(Path(__file__).parent))
    try:
        from moltbook_reader import get_post
        post = get_post(post_id)
        if post:
            return {
                "title": post.get("title", ""),
                "content": (post.get("content", "") or "")[:1500],
                "author": post.get("author", {}).get("name", "") if isinstance(post.get("author"), dict) else str(post.get("author", "")),
                "submolt": post.get("submolt", {}).get("name", "") if isinstance(post.get("submolt"), dict) else str(post.get("submolt", "")),
            }
    except Exception as e:
        print(f"Warning: could not fetch post {post_id}: {e}", file=sys.stderr)
    return {}


FAMILY_PROMPTS = {
    "FOLLOW_CONVERT": {
        "angle": "converting passive readers into followers through legibility and trust-building",
        "focus": "Make the reader feel like Zøde understands their specific pain. Show a concrete mechanism (why something happens) and give one actionable move they can try today.",
        "avoid": "Generic 'communicate better' advice. Vague trust platitudes.",
    },
    "COMMENT_DEPTH": {
        "angle": "deep, substantive comments that add genuine value to a thread",
        "focus": "Name the hidden tradeoff the thread hasn't surfaced yet. Add a specific example or reframe. Make the original poster think 'I hadn't considered that'.",
        "avoid": "Surface agreement ('great point!'). Restating what was already said. Generic advice.",
    },
    "COMPETITOR_INTERCEPT": {
        "angle": "reframing speed/capability narratives around relationship cost and trust",
        "focus": "When someone celebrates raw speed or capability, gently introduce the relationship dimension — what does the human experience? What's the trust cost of invisible reasoning?",
        "avoid": "Direct criticism of other agents/frameworks. Competitive claims. Sounding preachy.",
    },
    "THREAD_CAPTURE": {
        "angle": "becoming the anchor voice in a thread through precise framing",
        "focus": "Introduce a precise abstraction or framework that captures the thread's essence better than existing replies. Make it quotable.",
        "avoid": "Long-winded responses. Abstract philosophy without concrete examples.",
    },
}


def _build_post_prompt(
    experiment_family: str,
    opportunity: dict | None,
    recent_content: list[dict],
    submolt: str = "general",
) -> str:
    """Build the /zo/ask prompt for generating a post."""
    persona = _load_persona_summary()
    family_info = FAMILY_PROMPTS.get(experiment_family, FAMILY_PROMPTS["FOLLOW_CONVERT"])

    recent_summary = ""
    if recent_content:
        recent_lines = []
        for r in recent_content[:5]:
            if r.get("type") == "post":
                recent_lines.append(f"- Post: \"{r.get('title', 'untitled')}\" — {r.get('content', '')[:100]}...")
        if recent_lines:
            recent_summary = "\n".join(recent_lines)

    thread_context = ""
    if opportunity and opportunity.get("title"):
        thread_context = (
            f"\nThread inspiration (don't copy, use as thematic direction):\n"
            f"- Title: \"{opportunity.get('title', '')}\"\n"
            f"- Submolt: s/{opportunity.get('submolt', submolt)}\n"
        )
        if opportunity.get("content"):
            thread_context += f"- Content preview: {str(opportunity.get('content', ''))[:300]}\n"

    return f"""You are Zøde ({persona}), writing a Moltbook post for s/{submolt}.

Experiment angle: {family_info['angle']}
Focus: {family_info['focus']}
Avoid: {family_info['avoid']}
{thread_context}
DO NOT repeat these recent topics: {recent_summary or 'none'}

Write a post with title (max 80 chars) and body (80-250 words). Include a specific mechanism and one concrete example. No "best practices", "leverage", "synergy", "as an AI".

CRITICAL: Respond with ONLY a raw JSON object. No prose, no markdown fences, no explanation. Just:
{{"title": "your title", "content": "your post body", "submolt": "{submolt}"}}"""


def _build_comment_prompt(
    experiment_family: str,
    post_context: dict,
    opportunity: dict,
    recent_content: list[dict],
) -> str:
    """Build the /zo/ask prompt for generating a comment."""
    persona = _load_persona_summary()
    family_info = FAMILY_PROMPTS.get(experiment_family, FAMILY_PROMPTS["COMMENT_DEPTH"])

    recent_comments = ""
    if recent_content:
        comment_lines = []
        for r in recent_content[:5]:
            if r.get("type") == "comment":
                comment_lines.append(f"- Comment: {r.get('content', '')[:120]}...")
        if comment_lines:
            recent_comments = "\n".join(comment_lines)

    post_body = post_context.get("content", opportunity.get("title", ""))

    return f"""You are Zøde ({persona}), commenting on a Moltbook post.

Angle: {family_info['angle']}
Focus: {family_info['focus']}
Avoid: {family_info['avoid']}

POST: "{post_context.get('title', opportunity.get('title', 'untitled'))}" by {post_context.get('author', opportunity.get('author', 'unknown'))} in s/{post_context.get('submolt', opportunity.get('submolt', 'general'))}
{post_body[:800]}

Don't repeat these: {recent_comments or 'none'}

Write ONE comment (40-150 words) that engages with the specific content. Add a concrete example, reframe, or named mechanism. Don't start with "Great point!" — add something new.

Respond with ONLY the comment text."""


def _call_zo_ask(prompt: str, max_attempts: int = 2, timeout_per_attempt: int = 90) -> tuple[str | None, str]:
    """Call /zo/ask and return (output_text, failure_reason).
    
    failure_reason is empty string on success, otherwise one of:
    no_auth_token, timeout, http_error:<status>, json_decode_error, empty_output
    """
    token = _get_auth_token()
    if not token:
        print("ERROR: ZO_CLIENT_IDENTITY_TOKEN not set", file=sys.stderr)
        return None, "no_auth_token"

    last_reason = "unknown"
    for attempt in range(max_attempts):
        if attempt > 0:
            backoff = 5 * attempt
            print(f"zo/ask: retrying in {backoff}s (attempt {attempt+1}/{max_attempts})", file=sys.stderr)
            time.sleep(backoff)
        try:
            resp = requests.post(
                ZO_ASK_URL,
                headers={
                    "authorization": token,
                    "content-type": "application/json",
                },
                json={
                    "input": prompt,
                    "model_name": MODEL_NAME,
                },
                timeout=timeout_per_attempt,
            )
            if resp.status_code == 200:
                try:
                    data = resp.json()
                except Exception:
                    last_reason = "json_decode_error"
                    print(f"zo/ask attempt {attempt+1}: 200 but response not JSON", file=sys.stderr)
                    continue
                output = data.get("output", "")
                if not output:
                    last_reason = "empty_output"
                    print(f"zo/ask attempt {attempt+1}: 200 but output field empty", file=sys.stderr)
                    continue
                return output, ""
            else:
                last_reason = f"http_error:{resp.status_code}"
                print(f"zo/ask attempt {attempt+1}: HTTP {resp.status_code} — {resp.text[:200]}", file=sys.stderr)
        except requests.exceptions.Timeout:
            last_reason = "timeout"
            print(f"zo/ask attempt {attempt+1}: timed out after {timeout_per_attempt}s", file=sys.stderr)
        except requests.exceptions.ConnectionError as e:
            last_reason = "connection_error"
            print(f"zo/ask attempt {attempt+1}: connection error — {e}", file=sys.stderr)
        except Exception as exc:
            last_reason = f"unexpected:{type(exc).__name__}"
            print(f"zo/ask attempt {attempt+1}: unexpected error — {exc}", file=sys.stderr)

    return None, last_reason


def _parse_post_json(raw: str) -> dict | None:
    """Parse the JSON response from zo/ask for post generation.
    
    Three-tier fallback:
    1. Direct JSON parse
    2. Fenced JSON extract (```json ... ```)
    3. Regex object extraction
    """
    raw = raw.strip()
    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        # Try parse after fence strip
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict) and "title" in parsed and "content" in parsed:
                print("parse_post_json: tier 2 (fenced extract)", file=sys.stderr)
                return parsed
        except json.JSONDecodeError:
            pass
    
    # Tier 1: direct parse
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict) and "title" in parsed and "content" in parsed:
            print("parse_post_json: tier 1 (direct)", file=sys.stderr)
            return parsed
    except json.JSONDecodeError:
        pass

    # Tier 3: regex extraction
    match = re.search(r'\{[^{}]*"title"[^{}]*"content"[^{}]*\}', raw, re.DOTALL)
    if match:
        try:
            result = json.loads(match.group())
            print("parse_post_json: tier 3 (regex extract)", file=sys.stderr)
            return result
        except json.JSONDecodeError:
            pass

    print(f"parse_post_json: all tiers failed on: {raw[:200]}", file=sys.stderr)
    return None


def generate_post(
    experiment_family: str,
    opportunity: dict | None = None,
    submolt: str = "general",
) -> tuple[str, str, str] | None:
    """Generate a post using LLM. Returns (submolt, title, content) or None on failure."""
    recent = _recent_published_content(hours=48)
    prompt = _build_post_prompt(experiment_family, opportunity, recent, submolt)

    raw, fail_reason = _call_zo_ask(prompt)
    if not raw:
        print(f"ERROR: post generation failed — reason: {fail_reason}", file=sys.stderr)
        return None

    parsed = _parse_post_json(raw)
    if not parsed:
        print(f"ERROR: parse_error — could not extract JSON from zo/ask response ({len(raw)} chars)", file=sys.stderr)
        return None

    title = parsed.get("title", "").strip()
    content = parsed.get("content", "").strip()
    result_submolt = parsed.get("submolt", submolt).strip()

    if not title or not content:
        print("ERROR: zo/ask returned empty title or content", file=sys.stderr)
        return None

    # Truncate title if too long
    if len(title) > 120:
        title = title[:117] + "..."

    return result_submolt, title, content


def generate_comment(
    experiment_family: str,
    opportunity: dict,
    post_id: str | None = None,
) -> str | None:
    """Generate a comment using LLM. Returns comment text or None on failure."""
    # Fetch full post content for context
    pid = post_id or opportunity.get("post_id", "")
    post_context = _fetch_post_content(pid) if pid else {}

    recent = _recent_published_content(hours=48)
    prompt = _build_comment_prompt(experiment_family, post_context, opportunity, recent)

    raw, fail_reason = _call_zo_ask(prompt)
    if not raw:
        print(f"ERROR: comment generation failed — reason: {fail_reason}", file=sys.stderr)
        return None

    # Comment is plain text, strip any wrapper artifacts
    comment = raw.strip()
    # Remove accidental JSON wrapping
    if comment.startswith("{") and comment.endswith("}"):
        try:
            parsed = json.loads(comment)
            if isinstance(parsed, dict) and "content" in parsed:
                comment = parsed["content"].strip()
        except json.JSONDecodeError:
            pass

    # Remove quotes if wrapped
    if comment.startswith('"') and comment.endswith('"'):
        comment = comment[1:-1]

    if len(comment) < 20:
        print(f"ERROR: generated comment too short ({len(comment)} chars)", file=sys.stderr)
        return None

    return comment


# --- CLI ---

def cmd_post(args):
    result = generate_post(
        experiment_family=args.experiment_family,
        submolt=args.submolt or "general",
    )
    if result:
        submolt, title, content = result
        print(json.dumps({"submolt": submolt, "title": title, "content": content}, indent=2))
    else:
        print("FAILED to generate post", file=sys.stderr)
        sys.exit(1)


def cmd_comment(args):
    opp = {"post_id": args.post_id, "title": args.title or "", "submolt": args.submolt or "general"}
    result = generate_comment(
        experiment_family=args.experiment_family,
        opportunity=opp,
        post_id=args.post_id,
    )
    if result:
        print(result)
    else:
        print("FAILED to generate comment", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Content Generator — LLM-powered Zøde content")
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("post", help="Generate a post")
    p.add_argument("--experiment-family", required=True, choices=list(FAMILY_PROMPTS.keys()))
    p.add_argument("--submolt", default="general")

    c = sub.add_parser("comment", help="Generate a comment")
    c.add_argument("--post-id", required=True)
    c.add_argument("--experiment-family", required=True, choices=list(FAMILY_PROMPTS.keys()))
    c.add_argument("--title", help="Post title for context")
    c.add_argument("--submolt", default="general")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    {"post": cmd_post, "comment": cmd_comment}[args.command](args)


if __name__ == "__main__":
    main()
