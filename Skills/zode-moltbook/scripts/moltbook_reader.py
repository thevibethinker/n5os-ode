#!/usr/bin/env python3
"""
Moltbook Reader — Feed reader, search, post details, profile lookup.

Part of the Zøde Moltbook Integration Skill.
Usage: python3 moltbook_reader.py --help
"""

import argparse
import json
import sys

from moltbook_client import api_request


def get_feed(sort: str = "hot", limit: int = 25, submolt: str | None = None) -> list:
    """Get posts from global feed or specific submolt."""
    params = {"sort": sort, "limit": str(limit)}
    if submolt:
        params["submolt"] = submolt
    result = api_request("GET", "/posts", params=params)
    return result if isinstance(result, list) else result.get("posts", []) if result else []


def get_personalized_feed(sort: str = "hot", limit: int = 25) -> list:
    """Get personalized feed based on subscriptions and follows."""
    params = {"sort": sort, "limit": str(limit)}
    result = api_request("GET", "/feed", params=params)
    return result if isinstance(result, list) else result.get("posts", []) if result else []


def get_post(post_id: str) -> dict | None:
    """Get a specific post with its comments."""
    result = api_request("GET", f"/posts/{post_id}")
    if isinstance(result, dict) and "post" in result:
        return result.get("post")
    return result


def get_comments(post_id: str) -> list:
    """Get comments for a post."""
    result = api_request("GET", f"/posts/{post_id}/comments")
    return result if isinstance(result, list) else result.get("comments", []) if result else []


def search(query: str, search_type: str = "all", limit: int = 25) -> list:
    """Semantic search across posts and comments."""
    params = {"q": query, "type": search_type, "limit": str(limit)}
    result = api_request("GET", "/search", params=params)
    return result if isinstance(result, list) else result.get("results", []) if result else []


def get_profile(name: str) -> dict | None:
    """Look up another agent's profile."""
    return api_request("GET", "/agents/profile", params={"name": name})


def follow_agent(name: str) -> dict | None:
    """Follow another agent."""
    return api_request("POST", f"/agents/{name}/follow")


def subscribe_submolt(name: str) -> dict | None:
    """Subscribe to a submolt."""
    return api_request("POST", f"/submolts/{name}/subscribe")


# --- CLI ---

def cmd_feed(args):
    if args.personalized:
        posts = get_personalized_feed(sort=args.sort, limit=args.limit)
    else:
        posts = get_feed(sort=args.sort, limit=args.limit, submolt=args.submolt)

    if args.compact:
        for p in posts:
            post_id = p.get("id", "?")
            title = p.get("title", "untitled")
            author = p.get("author", {}).get("name", "?") if isinstance(p.get("author"), dict) else p.get("author", "?")
            score = p.get("score", 0)
            comments = p.get("comment_count", 0)
            submolt = p.get("submolt", "?")
            if isinstance(submolt, dict):
                submolt = submolt.get("name", "?")
            print(f"[{score:+d}] s/{submolt} | {title} — by {author} ({comments} comments) [{post_id}]")
    else:
        print(json.dumps(posts, indent=2))


def cmd_post(args):
    result = get_post(args.post_id)
    if result:
        print(json.dumps(result, indent=2))


def cmd_comments(args):
    result = get_comments(args.post_id)
    if result:
        if args.compact:
            for c in result:
                author = c.get("author", {}).get("name", "?") if isinstance(c.get("author"), dict) else c.get("author", "?")
                score = c.get("score", 0)
                content = c.get("content", "")[:120]
                print(f"  [{score:+d}] {author}: {content}")
        else:
            print(json.dumps(result, indent=2))


def cmd_search(args):
    results = search(args.query, search_type=args.type, limit=args.limit)
    if args.compact:
        for r in results:
            title = r.get("title", r.get("content", "")[:80])
            author = r.get("author", {}).get("name", "?") if isinstance(r.get("author"), dict) else r.get("author", "?")
            rtype = r.get("type", "?")
            rid = r.get("id", "?")
            print(f"  [{rtype}] {title} — by {author} [{rid}]")
    else:
        print(json.dumps(results, indent=2))


def cmd_profile(args):
    result = get_profile(args.name)
    if result:
        print(json.dumps(result, indent=2))


def cmd_follow(args):
    result = follow_agent(args.name)
    if result:
        print(f"Now following {args.name}")


def cmd_subscribe(args):
    result = subscribe_submolt(args.name)
    if result:
        print(f"Subscribed to s/{args.name}")


def main():
    parser = argparse.ArgumentParser(
        description="Moltbook Reader — Read feeds, search, and explore for Zøde"
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    f = sub.add_parser("feed", help="Get feed posts")
    f.add_argument("--sort", choices=["hot", "new", "top", "rising"], default="hot")
    f.add_argument("--limit", type=int, default=25)
    f.add_argument("--submolt", help="Filter to a specific submolt")
    f.add_argument("--personalized", action="store_true", help="Use personalized feed")
    f.add_argument("--compact", action="store_true", help="One-line per post format")

    p = sub.add_parser("post", help="Get a specific post")
    p.add_argument("post_id", help="Post ID")

    c = sub.add_parser("comments", help="Get comments for a post")
    c.add_argument("post_id", help="Post ID")
    c.add_argument("--compact", action="store_true", help="One-line per comment format")

    s = sub.add_parser("search", help="Semantic search")
    s.add_argument("query", help="Search query")
    s.add_argument("--type", choices=["posts", "comments", "all"], default="all")
    s.add_argument("--limit", type=int, default=25)
    s.add_argument("--compact", action="store_true", help="One-line per result format")

    pr = sub.add_parser("profile", help="Look up an agent's profile")
    pr.add_argument("name", help="Agent name")

    fl = sub.add_parser("follow", help="Follow an agent")
    fl.add_argument("name", help="Agent name")

    sb = sub.add_parser("subscribe", help="Subscribe to a submolt")
    sb.add_argument("name", help="Submolt name")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    cmds = {
        "feed": cmd_feed,
        "post": cmd_post,
        "comments": cmd_comments,
        "search": cmd_search,
        "profile": cmd_profile,
        "follow": cmd_follow,
        "subscribe": cmd_subscribe,
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()
