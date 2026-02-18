#!/usr/bin/env python3
"""
Zo Documentation Freshness Checker
---
created: 2026-02-17
last_edited: 2026-02-17
version: 1.0
provenance: con_korOfWz5bTYqA9FI
---

Compares the live docs.zocomputer.com sitemap against our local knowledge base.
Detects:
1. NEW pages added to the sitemap that we don't have coverage for
2. UPDATED pages (via lastmod timestamps) since our last check
3. Skills registry changes (new skills added)

Outputs a report to stdout for the scheduled agent to relay.
"""

import hashlib
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

KNOWLEDGE_DIR = Path("/home/workspace/Knowledge/zo-hotline/96-zo-platform")
STATE_FILE = Path("/home/workspace/N5/config/zo_docs_freshness_state.json")
SITEMAP_URL = "https://docs.zocomputer.com/sitemap.xml"
SKILLS_MANIFEST_URL = "https://raw.githubusercontent.com/zocomputer/skills/main/manifest.json"

EXCLUDE_PREFIXES = [
    "/api-reference/",
    "/tools/",
    "/information/",
]

KNOWN_COVERAGE = {
    "intro": "what-is-zo.md",
    "desktop": "desktop-app.md",
    "integrations": "integrations.md",
    "files": "files-and-storage.md",
    "scheduled-tasks": "scheduled-tasks.md",
    "sites": "sites-and-hosting.md",
    "spaces": "zo-space.md",
    "browser": "browser-use.md",
    "sell": "selling-on-zo.md",
    "billing": "billing-subscription.md",
    "gifts": "gifts.md",
    "faq": "faq.md",
    "prompting": "prompting-tips.md",
    "tools": "zo-tools-overview.md",
    "tools-overview": "zo-tools-overview.md",
    "bio": "bio-setup.md",
    "rules": "rules.md",
    "personas": "personas.md",
    "skills": "skills.md",
    "custom-domains": "custom-domains.md",
    "servers": "what-is-zo.md",
    "sync-files": "sync-files.md",
    "github": "github-and-ssh.md",
    "ssh-zo": "ssh-into-zo.md",
    "ssh-computer": "ssh-control-computer.md",
    "api": "zo-api.md",
    "mcp-server": "mcp-server.md",
    "byok": "byok-models.md",
    "claude-code": "claude-code-provider.md",
    "codex": "codex-provider.md",
}


def fetch_url(url: str) -> str:
    result = subprocess.run(
        ["curl", "-sfL", "--max-time", "15", url],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"Failed to fetch {url}: {result.stderr}")
    return result.stdout


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"last_check": None, "page_hashes": {}, "skills_count": 0, "known_pages": []}


def save_state(state: dict):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


def parse_sitemap(xml_text: str) -> list[dict]:
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    root = ET.fromstring(xml_text)
    pages = []
    for url_elem in root.findall("s:url", ns):
        loc = url_elem.find("s:loc", ns)
        lastmod = url_elem.find("s:lastmod", ns)
        if loc is not None:
            path = loc.text.replace("https://docs.zocomputer.com", "")
            if not path:
                path = "/"
            pages.append({
                "path": path,
                "lastmod": lastmod.text if lastmod is not None else None,
                "url": loc.text,
            })
    return pages


def main():
    state = load_state()
    issues = []
    info = []

    # 1. Fetch and parse sitemap
    try:
        sitemap_xml = fetch_url(SITEMAP_URL)
        pages = parse_sitemap(sitemap_xml)
    except Exception as e:
        print(f"❌ Failed to fetch sitemap: {e}")
        sys.exit(1)

    # Filter to core doc pages only
    core_pages = [
        p for p in pages
        if not any(p["path"].startswith(prefix) for prefix in EXCLUDE_PREFIXES)
    ]

    info.append(f"📄 Sitemap: {len(core_pages)} core pages, {len(pages)} total")

    # 2. Check for NEW pages
    previous_paths = set(state.get("known_pages", []))
    current_paths = {p["path"] for p in core_pages}
    new_pages = current_paths - previous_paths

    if new_pages:
        for np in sorted(new_pages):
            slug = np.lstrip("/")
            if slug in KNOWN_COVERAGE:
                continue
            issues.append(f"🆕 NEW PAGE: {np} — needs knowledge file")

    # 3. Check for UPDATED pages (lastmod changed)
    prev_hashes = state.get("page_hashes", {})
    current_hashes = {}
    for p in core_pages:
        h = hashlib.md5((p.get("lastmod") or "").encode()).hexdigest()[:8]
        current_hashes[p["path"]] = h
        if p["path"] in prev_hashes and prev_hashes[p["path"]] != h:
            slug = p["path"].lstrip("/")
            coverage = KNOWN_COVERAGE.get(slug, "???")
            issues.append(f"🔄 UPDATED: {p['path']} (covers: {coverage}) — verify content still accurate")

    # 4. Check for missing coverage
    for p in core_pages:
        slug = p["path"].lstrip("/")
        if slug not in KNOWN_COVERAGE and slug != "/":
            # Check if any file roughly matches
            matches = [f.name for f in KNOWLEDGE_DIR.glob("*.md") if slug.replace("-", "") in f.stem.replace("-", "")]
            if not matches:
                issues.append(f"⚠️ NO COVERAGE: {p['path']} — no matching knowledge file")

    # 5. Check skills registry
    try:
        skills_json = fetch_url(SKILLS_MANIFEST_URL)
        skills_data = json.loads(skills_json)
        current_count = len(skills_data.get("skills", []))
        prev_count = state.get("skills_count", 0)

        if prev_count > 0 and current_count > prev_count:
            issues.append(f"🧩 SKILLS: {current_count - prev_count} new skills added (was {prev_count}, now {current_count})")

        info.append(f"🧩 Skills registry: {current_count} skills")
        state["skills_count"] = current_count
    except Exception as e:
        info.append(f"⚠️ Skills check failed: {e}")

    # 6. Update state
    state["last_check"] = datetime.now(timezone.utc).isoformat()
    state["page_hashes"] = current_hashes
    state["known_pages"] = sorted(current_paths)
    save_state(state)

    # 7. Output report
    print("# Zo Docs Freshness Check")
    print(f"**Run:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print()

    for i in info:
        print(i)
    print()

    if issues:
        print(f"## ⚠️ {len(issues)} Issue(s) Found\n")
        for issue in issues:
            print(f"- {issue}")
        print()
        print("**Action needed:** Review the flagged pages and update knowledge files as needed.")
    else:
        print("## ✅ All Clear\n")
        print("No new pages, no content changes detected, skills registry unchanged.")
        print("Knowledge base is current.")


if __name__ == "__main__":
    main()
