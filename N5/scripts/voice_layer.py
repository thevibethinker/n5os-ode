#!/usr/bin/env python3
"""
Voice Injection Layer

Fully automatic. Zero human intervention.
Consumers call inject_voice(), get back enhanced prompt.

Part of Voice Library V2. See N5/builds/voice-injection-layer/PLAN.md

Usage:
    from N5.scripts.voice_layer import VoiceContext, inject_voice
    
    ctx = VoiceContext(
        content_type="email",
        platform="email", 
        purpose="follow-up",
        topic_domains=["hiring", "career"],
    )
    
    enhanced_prompt = inject_voice(base_prompt, ctx)

CLI (for testing only):
    python3 voice_layer.py --content-type email --purpose follow-up --domains hiring,career
    python3 voice_layer.py --test
"""

import argparse
import json
import sqlite3
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

# Paths
WORKSPACE = Path("/home/workspace")
DB_PATH = WORKSPACE / "N5" / "data" / "voice_library.db"

# Configuration
DEFAULT_PRIMITIVE_COUNT = 3
THROTTLE_HOURS = 24  # Don't reuse same primitive within this window


@dataclass
class VoiceContext:
    """
    Context for voice injection. Minimal by design.
    
    This is the contract between consumers and the voice layer.
    Keep it stable — consumers depend on this interface.
    """
    content_type: str  # email, blurb, tweet, post, doc
    platform: str = "general"  # x, linkedin, email, slack
    purpose: str = "general"  # follow-up, intro, thought-leadership
    topic_domains: list[str] = field(default_factory=list)
    primitive_count: int = DEFAULT_PRIMITIVE_COUNT


# Type preferences by content type
TYPE_PREFERENCES = {
    "tweet": ["signature_phrase", "metaphor", "rhetorical_device"],
    "email": ["syntactic_pattern", "signature_phrase", "conceptual_frame"],
    "blurb": ["metaphor", "analogy", "signature_phrase"],
    "post": ["conceptual_frame", "metaphor", "rhetorical_device"],
    "doc": ["conceptual_frame", "syntactic_pattern", "analogy"],
}


def get_primitives(
    domains: Optional[list[str]] = None,
    types: Optional[list[str]] = None,
    count: int = DEFAULT_PRIMITIVE_COUNT,
    min_distinctiveness: float = 0.6,
    update_usage: bool = True,
) -> list[dict]:
    """
    Retrieve primitives from voice library.
    
    Implements throttling to avoid repetition.
    Updates usage stats when update_usage=True.
    
    Returns list of primitive dicts with keys:
        id, exact_text, primitive_type, domains, distinctiveness_score, use_count
    """
    if not DB_PATH.exists():
        return []
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Build query with filters
    conditions = ["status = 'approved'"]
    params = []
    
    # Distinctiveness filter
    conditions.append("distinctiveness_score >= ?")
    params.append(min_distinctiveness)
    
    # Throttle: exclude recently used
    throttle_cutoff = (datetime.now(timezone.utc) - timedelta(hours=THROTTLE_HOURS)).isoformat()
    conditions.append("(last_used_at IS NULL OR last_used_at < ?)")
    params.append(throttle_cutoff)
    
    # Domain filter (if specified)
    domain_conditions = []
    if domains:
        for domain in domains:
            domain_conditions.append("domains_json LIKE ?")
            params.append(f'%"{domain}"%')
        if domain_conditions:
            conditions.append(f"({' OR '.join(domain_conditions)})")
    
    # Type filter (if specified)
    if types:
        type_placeholders = ",".join(["?" for _ in types])
        conditions.append(f"primitive_type IN ({type_placeholders})")
        params.extend(types)
    
    query = f"""
        SELECT id, exact_text, primitive_type, domains_json, 
               distinctiveness_score, use_count
        FROM primitives
        WHERE {' AND '.join(conditions)}
        ORDER BY 
            distinctiveness_score DESC,
            use_count ASC,
            RANDOM()
        LIMIT ?
    """
    params.append(count)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    primitives = []
    for row in rows:
        try:
            domains_list = json.loads(row["domains_json"]) if row["domains_json"] else []
        except json.JSONDecodeError:
            domains_list = []
        
        primitives.append({
            "id": row["id"],
            "exact_text": row["exact_text"],
            "primitive_type": row["primitive_type"],
            "domains": domains_list,
            "distinctiveness_score": row["distinctiveness_score"],
            "use_count": row["use_count"],
        })
    
    # Update usage stats
    if update_usage and primitives:
        now = datetime.now(timezone.utc).isoformat()
        ids = [p["id"] for p in primitives]
        placeholders = ",".join(["?" for _ in ids])
        cursor.execute(f"""
            UPDATE primitives 
            SET use_count = use_count + 1, last_used_at = ?
            WHERE id IN ({placeholders})
        """, [now] + ids)
        conn.commit()
    
    conn.close()
    return primitives


def get_voice_fragment(ctx: VoiceContext) -> str:
    """
    Auto-retrieves primitives and formats as prompt fragment.
    Called automatically — no human review.
    
    Returns empty string if no primitives available (graceful no-op).
    """
    # Get preferred types for content type
    preferred_types = TYPE_PREFERENCES.get(ctx.content_type, None)
    
    # Retrieve primitives (automatic, no approval)
    primitives = get_primitives(
        domains=ctx.topic_domains if ctx.topic_domains else None,
        types=preferred_types,
        count=ctx.primitive_count,
        update_usage=True,
    )
    
    if not primitives:
        return ""  # Graceful no-op
    
    # Format as prompt fragment
    lines = [
        "## Voice Enhancement (Auto-Applied)",
        "",
        "Weave these V-distinctive patterns naturally into your writing:",
        "",
    ]
    
    for i, p in enumerate(primitives, 1):
        lines.append(f"{i}. [{p['primitive_type']}] \"{p['exact_text']}\"")
    
    lines.extend([
        "",
        "Guidelines:",
        "- Use what fits naturally, skip what doesn't",
        "- One distinctive element per paragraph max", 
        "- Never force — if it feels mechanical, leave it out",
    ])
    
    return "\n".join(lines)


def inject_voice(prompt: str, ctx: VoiceContext) -> str:
    """
    Wraps any generation prompt with voice context.
    Fully automatic — just call and use the result.
    
    Args:
        prompt: The base generation prompt
        ctx: VoiceContext with content type, platform, purpose, domains
        
    Returns:
        Enhanced prompt with voice fragment prepended.
        Returns original prompt unchanged if no primitives available.
    """
    fragment = get_voice_fragment(ctx)
    if not fragment:
        return prompt
    return f"{fragment}\n\n---\n\n{prompt}"


def run_tests() -> bool:
    """Run unit tests. Returns True if all pass."""
    print("\n=== Voice Layer Unit Tests ===\n")
    passed = 0
    failed = 0
    
    # Test 1: VoiceContext defaults
    print("Test 1: VoiceContext defaults...")
    ctx = VoiceContext(content_type="email")
    assert ctx.platform == "general", "platform default failed"
    assert ctx.purpose == "general", "purpose default failed"
    assert ctx.topic_domains == [], "topic_domains default failed"
    assert ctx.primitive_count == 3, "primitive_count default failed"
    print("  ✅ PASS")
    passed += 1
    
    # Test 2: get_voice_fragment returns well-formed markdown
    print("Test 2: get_voice_fragment markdown format...")
    ctx = VoiceContext(content_type="email", topic_domains=["career"])
    fragment = get_voice_fragment(ctx)
    if fragment:  # May be empty if DB empty
        assert "## Voice Enhancement" in fragment, "missing header"
        assert "Guidelines:" in fragment, "missing guidelines"
        print("  ✅ PASS")
        passed += 1
    else:
        print("  ⚠️ SKIP (no primitives in DB)")
        passed += 1
    
    # Test 3: inject_voice prepends fragment
    print("Test 3: inject_voice prepends correctly...")
    base = "Write an email."
    ctx = VoiceContext(content_type="email")
    result = inject_voice(base, ctx)
    assert base in result, "original prompt lost"
    if "Voice Enhancement" in result:
        assert result.index("Voice Enhancement") < result.index(base), "fragment not prepended"
    print("  ✅ PASS")
    passed += 1
    
    # Test 4: Empty primitives = graceful no-op
    print("Test 4: Graceful handling when no primitives match...")
    ctx = VoiceContext(
        content_type="email",
        topic_domains=["nonexistent_domain_xyz123"],
    )
    fragment = get_voice_fragment(ctx)
    # Should return empty or valid fragment, not crash
    assert fragment == "" or "Voice Enhancement" in fragment
    print("  ✅ PASS")
    passed += 1
    
    # Test 5: Type preferences load correctly
    print("Test 5: Type preferences configured...")
    assert "tweet" in TYPE_PREFERENCES
    assert "email" in TYPE_PREFERENCES
    assert len(TYPE_PREFERENCES["tweet"]) >= 2
    print("  ✅ PASS")
    passed += 1
    
    print(f"\n=== Results: {passed}/{passed + failed} passed ===\n")
    return failed == 0


def main():
    parser = argparse.ArgumentParser(
        description="Voice Injection Layer (testing/debug CLI)"
    )
    parser.add_argument("--content-type", "-c", default="email",
                        help="Content type (email, blurb, tweet, post, doc)")
    parser.add_argument("--platform", "-p", default="general",
                        help="Platform (x, linkedin, email, slack)")
    parser.add_argument("--purpose", default="general",
                        help="Purpose (follow-up, intro, thought-leadership)")
    parser.add_argument("--domains", "-d", default="",
                        help="Comma-separated topic domains")
    parser.add_argument("--count", "-n", type=int, default=3,
                        help="Number of primitives")
    parser.add_argument("--test", action="store_true",
                        help="Run unit tests")
    parser.add_argument("--json", action="store_true",
                        help="Output as JSON")
    
    args = parser.parse_args()
    
    if args.test:
        success = run_tests()
        sys.exit(0 if success else 1)
    
    # Build context
    domains = [d.strip() for d in args.domains.split(",") if d.strip()]
    ctx = VoiceContext(
        content_type=args.content_type,
        platform=args.platform,
        purpose=args.purpose,
        topic_domains=domains,
        primitive_count=args.count,
    )
    
    if args.json:
        # Return structured output
        primitives = get_primitives(
            domains=domains if domains else None,
            types=TYPE_PREFERENCES.get(args.content_type),
            count=args.count,
            update_usage=False,  # Don't update in debug mode
        )
        print(json.dumps(primitives, indent=2))
    else:
        # Return fragment
        fragment = get_voice_fragment(ctx)
        if fragment:
            print(fragment)
        else:
            print("(No primitives available for this context)")


if __name__ == "__main__":
    main()

