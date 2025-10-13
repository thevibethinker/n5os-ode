#!/usr/bin/env python3
"""
Fix multiple issues in the lists system:
1. Add dual-write to n5_lists_add.py (call docgen after write)
2. Fix commands.jsonl workflow field (single-shot → appropriate value)
3. Restore lists-create.md to proper format

Principles Applied: P5 (backups), P7 (dry-run), P18 (verify), P19 (error handling)
"""
import json
import logging
import subprocess
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

ROOT = Path("/home/workspace")
N5 = ROOT / "N5"
COMMANDS_JSONL = N5 / "commands.jsonl"
LISTS_ADD_SCRIPT = N5 / "scripts" / "n5_lists_add.py"
LISTS_CREATE_MD = N5 / "commands" / "lists-create.md"

# Workflow mapping for schema compliance
WORKFLOW_MAP = {
    "careerspan-timeline-add": "data",
    "careerspan-timeline": "data",
    "core-audit": "ops",
    "digest-runs": "ops",
    "docgen-with-schedule-wrapper": "automation",
    "docgen": "automation",
    "file-protector": "ops",
    "flow-run": "automation",
    "git-audit": "ops",
    "git-check": "ops",
    "grep-search-command-creation": "ops",
    "hygiene-preflight": "ops",
    "index-rebuild": "index",
    "index-update": "index",
    "jobs-add": "data",
    "jobs-review": "data",
    "jobs-scrape": "data",
    "knowledge-add": "knowledge",
    "knowledge-find": "knowledge",
    "knowledge-ingest": "knowledge",
    "lists-add": "lists",
    "lists-create": "lists",
    "lists-docgen": "lists",
    "lists-export": "lists",
    "lists-find": "lists",
    "lists-move": "lists",
    "lists-pin": "lists",
    "lists-promote": "lists",
    "lists-set": "lists",
    "system-timeline-add": "data",
    "system-timeline": "data",
    "transcript-ingest": "data",
    "deep-research-due-diligence": "research",
    "functions-b2c-marketing-and-sales-collateral-generator-job-seeker": "writing",
    "jtbd-plus-interview-extractor": "research",
    "pr-intel-extractor": "research",
    "stakeholder-pain-point-extractor": "research",
    "stakeholder-qa-extractor-and-analyzer": "research",
    "follow-up-email-generator": "email",
    "conversation-end": "automation",
    "deliverable-generate": "writing",
    "meeting-approve": "ops",
    "deliverable-review": "ops",
}

def backup_file(filepath: Path) -> Path:
    """Create timestamped backup"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = filepath.parent / f"{filepath.name}.backup_{timestamp}"
    backup.write_bytes(filepath.read_bytes())
    logger.info(f"Backup created: {backup}")
    return backup

def fix_commands_jsonl(dry_run: bool = False) -> dict:
    """Fix workflow field in commands.jsonl"""
    logger.info("Fixing commands.jsonl workflow fields...")
    
    if not COMMANDS_JSONL.exists():
        return {"error": "commands.jsonl not found"}
    
    # Backup
    if not dry_run:
        backup_file(COMMANDS_JSONL)
    
    commands = []
    fixed_count = 0
    
    with open(COMMANDS_JSONL) as f:
        for line in f:
            if not line.strip():
                continue
            cmd = json.loads(line)
            
            if cmd.get("workflow") == "single-shot":
                name = cmd.get("name")
                new_workflow = WORKFLOW_MAP.get(name, "misc")
                logger.info(f"  {name}: single-shot → {new_workflow}")
                cmd["workflow"] = new_workflow
                fixed_count += 1
            
            commands.append(cmd)
    
    if not dry_run:
        with open(COMMANDS_JSONL, 'w') as f:
            for cmd in commands:
                f.write(json.dumps(cmd, separators=(',', ':')) + '\n')
        
        logger.info(f"✓ Fixed {fixed_count} workflow values in commands.jsonl")
    else:
        logger.info(f"[DRY RUN] Would fix {fixed_count} workflow values")
    
    return {"fixed": fixed_count, "total": len(commands)}

def add_dual_write_to_lists_add(dry_run: bool = False) -> dict:
    """Add dual-write call to n5_lists_add.py"""
    logger.info("Adding dual-write to n5_lists_add.py...")
    
    if not LISTS_ADD_SCRIPT.exists():
        return {"error": "n5_lists_add.py not found"}
    
    content = LISTS_ADD_SCRIPT.read_text()
    
    # Check if already added
    if "n5_lists_docgen.py" in content:
        logger.info("  Dual-write already present")
        return {"status": "already_present"}
    
    # Backup
    if not dry_run:
        backup_file(LISTS_ADD_SCRIPT)
    
    # Find the location to insert (after write_jsonl call)
    insertion_point = content.find('write_jsonl(jsonl_file, items)')
    if insertion_point == -1:
        return {"error": "Could not find insertion point"}
    
    # Find end of that block (after the print statements)
    after_write = content.find('print(f"File: {jsonl_file}")', insertion_point)
    if after_write == -1:
        return {"error": "Could not find print statement"}
    
    # Insert after this line
    end_of_line = content.find('\n', after_write)
    
    dual_write_code = '''
            # Dual-write: Update markdown view (P18: State Verification)
            logger.info("Updating markdown view...")
            docgen_script = Path(__file__).parent / "n5_lists_docgen.py"
            result = subprocess.run(
                [sys.executable, str(docgen_script), "--list", slug],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                logger.warning(f"MD generation failed: {result.stderr}")
            else:
                logger.info("✓ MD view updated")'''
    
    new_content = content[:end_of_line+1] + dual_write_code + content[end_of_line+1:]
    
    # Add imports at top
    if "import subprocess" not in new_content:
        import_pos = new_content.find("import sys\n") + len("import sys\n")
        new_content = new_content[:import_pos] + "import subprocess\n" + new_content[import_pos:]
    
    if not dry_run:
        LISTS_ADD_SCRIPT.write_text(new_content)
        logger.info("✓ Added dual-write to n5_lists_add.py")
    else:
        logger.info("[DRY RUN] Would add dual-write code")
    
    return {"status": "added"}

def restore_lists_create_md(dry_run: bool = False) -> dict:
    """Restore lists-create.md to proper format"""
    logger.info("Restoring lists-create.md...")
    
    if not LISTS_CREATE_MD.exists():
        return {"error": "lists-create.md not found"}
    
    # Backup
    if not dry_run:
        backup_file(LISTS_CREATE_MD)
    
    proper_content = """---
date: '2025-09-20T22:24:55Z'
last-tested: '2025-10-13T20:00:00Z'
generated_date: '2025-10-13T20:00:00Z'
checksum: restored
tags: []
category: lists
priority: medium
related_files: []
anchors:
  input: null
  output: /home/workspace/N5/commands/lists-create.md
---

# `lists-create`

Version: 0.1.0

Summary: Create a new list registry entry with JSONL and MD files.

Workflow: lists

Tags: lists, registry

## Inputs
- slug : string (required) — List slug (lowercase, hyphens allowed)
- title : text (required) — List title
- tags : json — Tags

## Outputs
- registry : path — Path to index.jsonl
- jsonl : path — Path to JSONL file
- md : path — Path to MD file

## Side Effects
- writes:file
- modifies:file

## Examples
- N5: run lists-create slug=ideas title="My Ideas" --dry-run

## Related Components

**Related Commands**: [`lists-add`](../commands/lists-add.md), [`lists-set`](../commands/lists-set.md), [`lists-find`](../commands/lists-find.md), [`lists-docgen`](../commands/lists-docgen.md), [`lists-export`](../commands/lists-export.md)

**Knowledge Areas**: [List Management](../knowledge/list-management.md)

**Examples**: See [Examples Library](../examples/) for usage patterns
"""
    
    if not dry_run:
        LISTS_CREATE_MD.write_text(proper_content)
        logger.info("✓ Restored lists-create.md")
    else:
        logger.info("[DRY RUN] Would restore lists-create.md")
    
    return {"status": "restored"}

def verify_fixes() -> dict:
    """Verify all fixes applied correctly (P18)"""
    logger.info("Verifying fixes...")
    
    results = {}
    
    # 1. Check commands.jsonl has no single-shot
    with open(COMMANDS_JSONL) as f:
        has_single_shot = any("single-shot" in line for line in f)
    results["commands_jsonl_fixed"] = not has_single_shot
    
    # 2. Check lists-create.md has proper newlines
    content = LISTS_CREATE_MD.read_text()
    results["lists_create_md_fixed"] = "\\n" not in content and "## Inputs" in content
    
    # 3. Check n5_lists_add.py has dual-write
    add_content = LISTS_ADD_SCRIPT.read_text()
    results["dual_write_added"] = "n5_lists_docgen.py" in add_content
    
    all_good = all(results.values())
    if all_good:
        logger.info("✓ All fixes verified")
    else:
        logger.warning(f"Verification failed: {results}")
    
    return results

def main(dry_run: bool = False) -> int:
    """Main execution"""
    try:
        logger.info("=" * 60)
        logger.info("Lists System Comprehensive Fix")
        logger.info("=" * 60)
        
        if dry_run:
            logger.info("[DRY RUN MODE]")
        
        # Fix 1: commands.jsonl workflow fields
        result1 = fix_commands_jsonl(dry_run)
        logger.info(f"Commands JSONL: {result1}")
        
        # Fix 2: Add dual-write
        result2 = add_dual_write_to_lists_add(dry_run)
        logger.info(f"Dual-write: {result2}")
        
        # Fix 3: Restore lists-create.md
        result3 = restore_lists_create_md(dry_run)
        logger.info(f"Lists-create MD: {result3}")
        
        # Verify (only if not dry-run)
        if not dry_run:
            verify_results = verify_fixes()
            logger.info(f"Verification: {verify_results}")
            
            if not all(verify_results.values()):
                logger.error("❌ Verification failed")
                return 1
        
        logger.info("=" * 60)
        logger.info("✓ All fixes complete" if not dry_run else "✓ Dry run complete")
        logger.info("=" * 60)
        
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    exit(main(dry_run=args.dry_run))
