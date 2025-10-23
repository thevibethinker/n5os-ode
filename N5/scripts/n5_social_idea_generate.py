#!/usr/bin/env python3
"""
Generate social media content from captured ideas

Loads stable/semi-stable context + beliefs/values for highly relevant generation.
Auto-imports generated drafts to tracking system.
"""

import argparse
import sys
import re
import subprocess
from pathlib import Path
from datetime import datetime, timezone
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)

# Paths
WORKSPACE = Path("/home/workspace")
IDEAS_LIST = WORKSPACE / "Lists/social-media-ideas.md"
KNOWLEDGE = WORKSPACE / "Knowledge"
GENERATOR = WORKSPACE / "N5/scripts/n5_linkedin_post_generate.py"
IMPORTER = WORKSPACE / "N5/scripts/n5_social_post.py"

# Context files for generation
CONTEXT_FILES = [
    KNOWLEDGE / "stable/bio.md",
    KNOWLEDGE / "stable/company.md",
    KNOWLEDGE / "semi_stable/positioning_current.md",
    KNOWLEDGE / "semi_stable/product_current.md",
]


def load_context() -> str:
    """Load stable/semi-stable context + beliefs for generation"""
    context_parts = []
    
    # Load stable info
    for file in CONTEXT_FILES:
        if file.exists():
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        context_parts.append(f"## {file.stem}\n\n{content}")
                        logger.info(f"✓ Loaded context: {file.relative_to(WORKSPACE)}")
            except Exception as e:
                logger.warning(f"Could not load {file.name}: {e}")
    
    # Look for beliefs/values
    beliefs_dir = KNOWLEDGE / "V-Beliefs"
    if beliefs_dir.exists():
        for belief_file in beliefs_dir.glob("*.md"):
            try:
                with open(belief_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        context_parts.append(f"## {belief_file.stem}\n\n{content}")
                        logger.info(f"✓ Loaded beliefs: {belief_file.name}")
            except Exception as e:
                logger.warning(f"Could not load {belief_file.name}: {e}")
    
    if not context_parts:
        logger.warning("No context files loaded - generation will lack background")
        return ""
    
    return "\n\n---\n\n".join(context_parts)


def extract_ideas(idea_ids: list) -> dict:
    """Extract idea content from ideas list"""
    if not IDEAS_LIST.exists():
        logger.error(f"Ideas list not found: {IDEAS_LIST}")
        return {}
    
    with open(IDEAS_LIST, 'r', encoding='utf-8') as f:
        content = f.read()
    
    ideas = {}
    
    for idea_id in idea_ids:
        # Find the idea block
        pattern = rf'\*\*ID:\*\*\s+{re.escape(idea_id)}.*?(?=\*\*ID:\*\*|\Z)'
        match = re.search(pattern, content, re.DOTALL)
        
        if not match:
            logger.warning(f"Idea not found: {idea_id}")
            continue
        
        idea_block = match.group(0)
        
        # Extract title
        title_match = re.search(r'\*\*Title:\*\*\s+(.+?)(?:\n|$)', idea_block)
        title = title_match.group(1).strip() if title_match else "Untitled"
        
        # Extract body
        body_match = re.search(r'\*\*Body:\*\*\s*\n\n(.*?)(?:\n\n\*\*|$)', idea_block, re.DOTALL)
        body = body_match.group(1).strip() if body_match else ""
        
        # Extract tags
        tags_match = re.search(r'\*\*Tags:\*\*\s+(.+?)(?:\n|$)', idea_block)
        tags = tags_match.group(1).strip() if tags_match else ""
        
        ideas[idea_id] = {
            'title': title,
            'body': body,
            'tags': tags,
            'full_block': idea_block
        }
        
        logger.info(f"✓ Extracted: {idea_id} - {title}")
    
    return ideas


def combine_ideas(ideas: dict, context: str) -> str:
    """Combine ideas + context into seed content for generation"""
    if not ideas:
        return ""
    
    seed_parts = []
    
    # Add context header
    if context:
        seed_parts.append("# Context: Who I Am\n\n" + context)
    
    # Add ideas
    seed_parts.append("\n\n# Ideas to Synthesize\n")
    
    for idea_id, idea in ideas.items():
        seed_parts.append(f"\n## {idea['title']} ({idea_id})\n\n{idea['body']}")
        if idea['tags']:
            seed_parts.append(f"\n{idea['tags']}")
    
    # Add synthesis instruction
    if len(ideas) > 1:
        seed_parts.append("\n\n# Instruction\n\nSynthesize these ideas into a single, coherent LinkedIn post that connects the themes while staying authentic to my voice and context.")
    else:
        seed_parts.append("\n\n# Instruction\n\nTransform this idea into a LinkedIn post that's authentic to my voice and context.")
    
    return "\n".join(seed_parts)


def generate_post(seed_content: str, dry_run: bool = False) -> tuple:
    """Generate LinkedIn post using the generator"""
    if dry_run:
        logger.info("[DRY RUN] Would generate post with seed content")
        logger.info(f"Seed length: {len(seed_content)} chars")
        return None, None
    
    # Save seed to temp file
    temp_seed = WORKSPACE / ".temp_idea_seed.md"
    with open(temp_seed, 'w', encoding='utf-8') as f:
        f.write(seed_content)
    
    # Run generator
    cmd = [
        "python3", str(GENERATOR),
        "--seed", str(temp_seed),
        "--mode", "authentic",
        "--output-format", "markdown"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        # Clean up temp file
        temp_seed.unlink(missing_ok=True)
        
        if result.returncode != 0:
            logger.error(f"Generator failed: {result.stderr}")
            return None, None
        
        # Find generated files
        # Generator saves to Knowledge/personal-brand/social-content/linkedin/
        linkedin_dir = KNOWLEDGE / "personal-brand/social-content/linkedin"
        
        # Get most recent draft file
        draft_files = sorted(linkedin_dir.glob("*-post-draft.md"), key=lambda p: p.stat().st_mtime, reverse=True)
        
        if not draft_files:
            logger.error("No draft file found after generation")
            return None, None
        
        draft_file = draft_files[0]
        
        # Look for metadata file
        metadata_file = draft_file.with_name(draft_file.stem.replace("-post-draft", "-post-metadata") + ".json")
        
        return draft_file, metadata_file if metadata_file.exists() else None
    
    except subprocess.TimeoutExpired:
        logger.error("Generator timed out")
        temp_seed.unlink(missing_ok=True)
        return None, None
    except Exception as e:
        logger.error(f"Generation error: {e}")
        temp_seed.unlink(missing_ok=True)
        return None, None


def import_to_registry(draft_file: Path, dry_run: bool = False) -> str:
    """Import generated draft to tracking system"""
    if dry_run:
        logger.info(f"[DRY RUN] Would import: {draft_file.name}")
        return "dry-run-id"
    
    cmd = [
        "python3", str(IMPORTER),
        "add", str(draft_file),
        "--platform", "linkedin",
        "--status", "draft",
        "--source", "generated"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            logger.error(f"Import failed: {result.stderr}")
            return None
        
        # Extract post ID from output
        post_id_match = re.search(r'post_[a-f0-9]+', result.stderr)
        post_id = post_id_match.group(0) if post_id_match else None
        
        if post_id:
            logger.info(f"✓ Imported to registry: {post_id}")
        
        return post_id
    
    except Exception as e:
        logger.error(f"Import error: {e}")
        return None


def mark_ideas_processed(idea_ids: list, post_id: str, dry_run: bool = False):
    """Move ideas to Processed section"""
    if dry_run:
        logger.info(f"[DRY RUN] Would mark {len(idea_ids)} idea(s) as processed")
        return
    
    if not IDEAS_LIST.exists():
        return
    
    with open(IDEAS_LIST, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract each idea block
    for idea_id in idea_ids:
        pattern = rf'\*\*ID:\*\*\s+{re.escape(idea_id)}.*?---\n'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            idea_block = match.group(0)
            
            # Remove from current location
            content = content.replace(idea_block, '')
            
            # Add to Processed section with post link
            processed_entry = f"{idea_block.rstrip()}\n**Status:** Generated → [post_{post_id}]\n\n---\n"
            
            # Find Processed section
            processed_marker = "## Processed"
            if processed_marker in content:
                processed_pos = content.find(processed_marker)
                # Find end of header comment
                comment_end = content.find("-->", processed_pos)
                if comment_end != -1:
                    insert_pos = comment_end + 4
                    content = content[:insert_pos] + "\n\n" + processed_entry + content[insert_pos:]
    
    # Write back
    with open(IDEAS_LIST, 'w', encoding='utf-8') as f:
        f.write(content)
    
    logger.info(f"✓ Marked {len(idea_ids)} idea(s) as processed")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate social media content from captured ideas"
    )
    parser.add_argument('--id', action='append', dest='idea_ids', required=True,
                        help='Idea ID (can specify multiple)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Preview without generating')
    
    args = parser.parse_args()
    
    try:
        logger.info(f"Starting generation for {len(args.idea_ids)} idea(s)")
        
        # Load context
        logger.info("Loading stable/semi-stable context + beliefs...")
        context = load_context()
        
        # Extract ideas
        ideas = extract_ideas(args.idea_ids)
        
        if not ideas:
            logger.error("No valid ideas found")
            return 1
        
        # Combine into seed content
        seed_content = combine_ideas(ideas, context)
        
        # Generate post
        logger.info("Generating LinkedIn post...")
        draft_file, metadata_file = generate_post(seed_content, dry_run=args.dry_run)
        
        if not draft_file and not args.dry_run:
            logger.error("Generation failed")
            return 1
        
        # Import to registry
        if not args.dry_run:
            logger.info("Importing to tracking system...")
            post_id = import_to_registry(draft_file)
            
            if not post_id:
                logger.error("Import failed")
                return 1
            
            # Mark ideas as processed
            mark_ideas_processed(args.idea_ids, post_id)
            
            logger.info(f"\n✓ Complete!")
            logger.info(f"  Post ID: {post_id}")
            logger.info(f"  Draft: {draft_file.relative_to(WORKSPACE)}")
            logger.info(f"  Ideas processed: {', '.join(args.idea_ids)}")
        else:
            logger.info("[DRY RUN] Complete - no changes made")
        
        return 0
    
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
