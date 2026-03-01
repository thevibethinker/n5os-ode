#!/usr/bin/env python3
"""
lineage_analyzer.py — Scan N5/builds/ and cluster related builds by capability.

Identifies build lineage chains (e.g., zo-hotline → zo-hotline-v4 → zo-hotline-v7),
determines which build is canonical, and flags promotable builds.

Usage:
    python3 Skills/build-promote/scripts/lineage_analyzer.py scan
    python3 Skills/build-promote/scripts/lineage_analyzer.py cluster <slug>
    python3 Skills/build-promote/scripts/lineage_analyzer.py promotable
    python3 Skills/build-promote/scripts/lineage_analyzer.py scan --save
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

WORKSPACE = Path("/home/workspace")
BUILDS_DIR = WORKSPACE / "N5" / "builds"
SKILLS_DIR = WORKSPACE / "Skills"
STATE_DIR = WORKSPACE / "Skills" / "build-promote" / "state"

# Suffixes to strip when computing a build's "base name"
VERSION_SUFFIXES = re.compile(
    r"[-_](?:v\d+|fix|debug|patch|staging|extended|integration|revamp|"
    r"refresh|consolidation|validation|wiring)$"
)

# Build folders that are definitely not promotable
SKIP_DIRS = {"_archive", "test-build", "test-validator-pass"}


def load_meta(slug: str) -> dict | None:
    meta_path = BUILDS_DIR / slug / "meta.json"
    if not meta_path.exists():
        return None
    try:
        return json.loads(meta_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, IOError):
        return None


def get_base_name(slug: str) -> str:
    """Strip version/variant suffixes to find the base capability name."""
    name = slug
    # Iteratively strip known suffixes
    changed = True
    while changed:
        changed = False
        m = VERSION_SUFFIXES.search(name)
        if m:
            name = name[: m.start()]
            changed = True
    return name


def find_matching_skill(slug: str, base_name: str) -> str | None:
    """Check if a Skill directory exists that matches this build."""
    # Direct match
    if (SKILLS_DIR / slug / "SKILL.md").exists():
        return slug
    if (SKILLS_DIR / base_name / "SKILL.md").exists():
        return base_name
    # Check for skills whose name is a substring match
    for skill_dir in SKILLS_DIR.iterdir():
        if not skill_dir.is_dir() or skill_dir.name.startswith("_"):
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        # Exact slug or base name match
        if skill_dir.name == slug or skill_dir.name == base_name:
            return skill_dir.name
    return None


def scan_all_builds() -> dict:
    """Scan all builds and produce cluster map."""
    builds = {}
    base_groups = defaultdict(list)

    for entry in sorted(BUILDS_DIR.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name in SKIP_DIRS or entry.name.startswith("."):
            continue

        slug = entry.name
        meta = load_meta(slug)
        base_name = get_base_name(slug)
        base_groups[base_name].append(slug)

        info = {
            "slug": slug,
            "base_name": base_name,
            "has_meta": meta is not None,
            "status": meta.get("status", "unknown") if meta else "no_meta",
            "title": meta.get("title", slug) if meta else slug,
            "created": meta.get("created", None) if meta else None,
            "completed_at": meta.get("completed_at", None) if meta else None,
            "has_transition_note": bool(meta.get("transition_note")) if meta else False,
            "parent_build": meta.get("lineage", {}).get("parent_build") if meta else None,
        }

        # Check for operational content beyond scaffolding
        scripts_dir = entry / "scripts"
        artifacts_dir = entry / "artifacts"
        workspace_dir = entry / "workspace"
        info["has_scripts"] = scripts_dir.exists() and any(scripts_dir.glob("*.py")) or any(scripts_dir.glob("*.ts")) if scripts_dir.exists() else False
        info["has_artifacts"] = artifacts_dir.exists() and any(artifacts_dir.iterdir()) if artifacts_dir.exists() else False
        info["has_workspace"] = workspace_dir.exists() and any(workspace_dir.iterdir()) if workspace_dir.exists() else False

        builds[slug] = info

    # Build clusters from base_groups, merging single-member groups that
    # match other clusters via explicit lineage
    clusters = {}
    slug_to_cluster = {}

    for base_name, slugs in base_groups.items():
        cluster_id = base_name
        cluster = {
            "id": cluster_id,
            "builds": sorted(slugs),
            "canonical": None,
            "existing_skill": None,
            "promotion_status": "unknown",
        }

        # Determine canonical build (prefer: most recent complete/finalized, then active, then latest)
        candidates = []
        for s in slugs:
            b = builds[s]
            # Score: finalized=4, complete=3, active=2, other=1, no_meta=0
            score = {"finalized": 4, "complete": 3, "active": 2, "no_meta": 0}.get(
                b["status"], 1
            )
            candidates.append((score, b.get("created") or "", s))

        candidates.sort(reverse=True)
        if candidates:
            cluster["canonical"] = candidates[0][2]

        # Check for existing skill
        for s in slugs:
            skill = find_matching_skill(s, base_name)
            if skill:
                cluster["existing_skill"] = skill
                break

        # Determine promotion status
        canonical = cluster["canonical"]
        canonical_build = builds.get(canonical, {})

        if cluster["existing_skill"]:
            # Check if the build has a transition note (already promoted)
            if canonical_build.get("has_transition_note"):
                cluster["promotion_status"] = "already_promoted"
            else:
                cluster["promotion_status"] = "has_skill_may_need_sync"
        elif canonical_build.get("status") in ("complete", "finalized"):
            has_content = (
                canonical_build.get("has_scripts")
                or canonical_build.get("has_artifacts")
                or canonical_build.get("has_workspace")
            )
            if has_content:
                cluster["promotion_status"] = "promotable"
            else:
                cluster["promotion_status"] = "not_promotable"
        elif canonical_build.get("status") in ("active", "planning"):
            cluster["promotion_status"] = "in_progress"
        else:
            cluster["promotion_status"] = "not_promotable"

        clusters[cluster_id] = cluster
        for s in slugs:
            slug_to_cluster[s] = cluster_id

    # Merge clusters connected by explicit lineage
    for slug, info in builds.items():
        parent = info.get("parent_build")
        if parent and parent in slug_to_cluster:
            parent_cluster = slug_to_cluster[parent]
            child_cluster = slug_to_cluster.get(slug)
            if child_cluster and parent_cluster != child_cluster:
                # Merge child into parent cluster
                parent_c = clusters[parent_cluster]
                child_c = clusters.pop(child_cluster, None)
                if child_c:
                    for s in child_c["builds"]:
                        if s not in parent_c["builds"]:
                            parent_c["builds"].append(s)
                        slug_to_cluster[s] = parent_cluster
                    parent_c["builds"].sort()

    return {
        "builds": builds,
        "clusters": clusters,
        "slug_to_cluster": slug_to_cluster,
        "summary": {
            "total_builds": len(builds),
            "total_clusters": len(clusters),
            "promotable": sum(
                1
                for c in clusters.values()
                if c["promotion_status"] == "promotable"
            ),
            "already_promoted": sum(
                1
                for c in clusters.values()
                if c["promotion_status"] == "already_promoted"
            ),
            "has_skill_may_need_sync": sum(
                1
                for c in clusters.values()
                if c["promotion_status"] == "has_skill_may_need_sync"
            ),
            "in_progress": sum(
                1
                for c in clusters.values()
                if c["promotion_status"] == "in_progress"
            ),
            "not_promotable": sum(
                1
                for c in clusters.values()
                if c["promotion_status"] == "not_promotable"
            ),
        },
    }


def cmd_scan(args):
    """Full analysis of all builds."""
    result = scan_all_builds()

    if args.save:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        out_path = STATE_DIR / "lineage.json"
        with open(out_path, "w") as f:
            json.dump(result, f, indent=2, default=str)
        print(f"Saved to {out_path}", file=sys.stderr)

    # Human-readable summary to stderr
    s = result["summary"]
    print(f"\n=== Build Lineage Scan ===", file=sys.stderr)
    print(f"Total builds:         {s['total_builds']}", file=sys.stderr)
    print(f"Total clusters:       {s['total_clusters']}", file=sys.stderr)
    print(f"Promotable:           {s['promotable']}", file=sys.stderr)
    print(f"Already promoted:     {s['already_promoted']}", file=sys.stderr)
    print(f"Has skill (may sync): {s['has_skill_may_need_sync']}", file=sys.stderr)
    print(f"In progress:          {s['in_progress']}", file=sys.stderr)
    print(f"Not promotable:       {s['not_promotable']}", file=sys.stderr)

    # Show multi-build clusters
    multi = {
        k: v for k, v in result["clusters"].items() if len(v["builds"]) > 1
    }
    if multi:
        print(f"\nMulti-build clusters ({len(multi)}):", file=sys.stderr)
        for cid, c in sorted(multi.items()):
            canonical = c["canonical"]
            print(
                f"  {cid}: {c['builds']} → canonical={canonical} [{c['promotion_status']}]",
                file=sys.stderr,
            )

    if args.json:
        json.dump(result, sys.stdout, indent=2, default=str)
    else:
        # Print promotable clusters
        promotable = {
            k: v
            for k, v in result["clusters"].items()
            if v["promotion_status"] == "promotable"
        }
        if promotable:
            print(f"\nPromotable builds:", file=sys.stderr)
            for cid, c in sorted(promotable.items()):
                canonical = c["canonical"]
                b = result["builds"].get(canonical, {})
                print(
                    f"  {canonical}: {b.get('title', canonical)} [{b.get('status')}]",
                    file=sys.stderr,
                )

    return 0


def cmd_cluster(args):
    """Show the cluster a specific build belongs to."""
    result = scan_all_builds()
    slug = args.slug

    cluster_id = result["slug_to_cluster"].get(slug)
    if not cluster_id:
        print(f"Build '{slug}' not found", file=sys.stderr)
        return 1

    cluster = result["clusters"][cluster_id]
    print(f"\n=== Cluster: {cluster_id} ===", file=sys.stderr)
    print(f"Builds: {cluster['builds']}", file=sys.stderr)
    print(f"Canonical: {cluster['canonical']}", file=sys.stderr)
    print(f"Existing skill: {cluster['existing_skill'] or 'none'}", file=sys.stderr)
    print(f"Promotion status: {cluster['promotion_status']}", file=sys.stderr)

    # Show details for each build in cluster
    print(f"\nBuild details:", file=sys.stderr)
    for s in cluster["builds"]:
        b = result["builds"].get(s, {})
        marker = " ← canonical" if s == cluster["canonical"] else ""
        print(
            f"  {s}: status={b.get('status', '?')}, "
            f"has_scripts={b.get('has_scripts')}, "
            f"has_artifacts={b.get('has_artifacts')}, "
            f"has_workspace={b.get('has_workspace')}"
            f"{marker}",
            file=sys.stderr,
        )

    if args.json:
        output = {
            "cluster": cluster,
            "builds": {
                s: result["builds"][s] for s in cluster["builds"] if s in result["builds"]
            },
        }
        json.dump(output, sys.stdout, indent=2, default=str)

    return 0


def cmd_promotable(args):
    """List builds that are candidates for promotion to Skills."""
    result = scan_all_builds()

    promotable = {
        k: v
        for k, v in result["clusters"].items()
        if v["promotion_status"] == "promotable"
    }

    if not promotable:
        print("No promotable builds found.", file=sys.stderr)
        return 0

    print(f"\n=== Promotable Builds ({len(promotable)}) ===", file=sys.stderr)
    items = []
    for cid, c in sorted(promotable.items()):
        canonical = c["canonical"]
        b = result["builds"].get(canonical, {})
        item = {
            "cluster_id": cid,
            "canonical_build": canonical,
            "title": b.get("title", canonical),
            "status": b.get("status", "unknown"),
            "builds_in_cluster": c["builds"],
            "has_scripts": b.get("has_scripts", False),
            "has_artifacts": b.get("has_artifacts", False),
            "has_workspace": b.get("has_workspace", False),
        }
        items.append(item)
        print(
            f"  {canonical}: {item['title']} "
            f"(cluster: {len(c['builds'])} build(s))",
            file=sys.stderr,
        )

    if args.json:
        json.dump(items, sys.stdout, indent=2, default=str)

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Analyze build lineage and identify promotable builds.",
    )
    parser.add_argument(
        "--json", action="store_true", help="Machine-readable JSON output to stdout"
    )
    subparsers = parser.add_subparsers(dest="command")

    p_scan = subparsers.add_parser("scan", help="Full analysis of all builds")
    p_scan.add_argument("--save", action="store_true", help="Save results to state/lineage.json")
    p_scan.add_argument("--json", action="store_true", dest="json", help="JSON output")

    p_cluster = subparsers.add_parser("cluster", help="Show cluster for a build")
    p_cluster.add_argument("slug", help="Build slug to look up")
    p_cluster.add_argument("--json", action="store_true", dest="json", help="JSON output")

    p_promotable = subparsers.add_parser("promotable", help="List promotable builds")
    p_promotable.add_argument("--json", action="store_true", dest="json", help="JSON output")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    commands = {
        "scan": cmd_scan,
        "cluster": cmd_cluster,
        "promotable": cmd_promotable,
    }
    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main() or 0)
