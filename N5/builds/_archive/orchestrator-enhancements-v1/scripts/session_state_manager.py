#!/usr/bin/env python3
"""
Session State Manager - Central state tracking for conversations
Manages SESSION_STATE.md files with registry integration

Usage:
    python3 session_state_manager.py init --convo-id con_XXX --type build
    python3 session_state_manager.py update --convo-id con_XXX --field Focus --value "New focus"
    python3 session_state_manager.py link-parent --convo-id con_WORKER --parent con_ORCH
    python3 session_state_manager.py declare-artifact --convo-id con_XXX --path /path/to/file --status draft
    python3 session_state_manager.py list-artifacts --convo-id con_XXX
"""

import argparse
import logging
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

WORKSPACE_ROOT = Path("/home/.z/workspaces")
USER_WORKSPACE = Path("/home/workspace")


class SessionStateManager:
    def __init__(self, convo_id: str, dry_run: bool = False):
        self.convo_id = convo_id
        self.workspace = WORKSPACE_ROOT / convo_id
        self.state_file = self.workspace / "SESSION_STATE.md"
        self.dry_run = dry_run
        
        if not self.workspace.exists():
            logger.warning(f"Workspace not found: {self.workspace}")
    
    def init(self, convo_type: str = "build", load_system: bool = False) -> bool:
        """Initialize SESSION_STATE.md for conversation"""
        try:
            if self.state_file.exists():
                logger.info(f"SESSION_STATE.md already exists: {self.state_file}")
                return True
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            content = f"""# Session State

**Conversation ID:** {self.convo_id}  
**Primary Type:** {convo_type}  
**Status:** active  
**Started:** {timestamp}  
**Parent:** (none)

## Focus
(To be determined)

## Objective
(To be defined)

## Progress
- Session initialized

## Topics Covered
(None yet)

## Artifacts
(None yet)

## Tags
{convo_type}

---
**Last Updated:** {timestamp}
"""
            
            if not self.dry_run:
                self.workspace.mkdir(parents=True, exist_ok=True)
                self.state_file.write_text(content)
                logger.info(f"✓ Initialized SESSION_STATE.md: {self.state_file}")
            else:
                logger.info(f"[DRY-RUN] Would create: {self.state_file}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize SESSION_STATE.md: {e}", exc_info=True)
            return False
    
    def update(self, field: str, value: str) -> bool:
        """Update a field in SESSION_STATE.md"""
        try:
            if not self.state_file.exists():
                logger.error(f"SESSION_STATE.md not found: {self.state_file}")
                return False
            
            content = self.state_file.read_text()
            lines = content.split("\n")
            
            # Find and update field
            field_found = False
            for i, line in enumerate(lines):
                if line.startswith(f"## {field}"):
                    field_found = True
                    # Replace content until next ## or end
                    j = i + 1
                    while j < len(lines) and not lines[j].startswith("##"):
                        j += 1
                    # Replace with new value
                    lines = lines[:i+1] + [value, ""] + lines[j:]
                    break
            
            if not field_found:
                logger.warning(f"Field '{field}' not found, appending")
                # Insert before last line (---...)
                for i in range(len(lines)-1, -1, -1):
                    if lines[i].startswith("---"):
                        lines.insert(i, f"\n## {field}\n{value}\n")
                        break
            
            # Update timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for i, line in enumerate(lines):
                if line.startswith("**Last Updated:**"):
                    lines[i] = f"**Last Updated:** {timestamp}"
                    break
            
            content = "\n".join(lines)
            
            if not self.dry_run:
                self.state_file.write_text(content)
                logger.info(f"✓ Updated {field} in SESSION_STATE.md")
            else:
                logger.info(f"[DRY-RUN] Would update {field}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update SESSION_STATE.md: {e}", exc_info=True)
            return False
    
    def link_parent(self, parent_id: str) -> bool:
        """Link conversation to parent orchestrator"""
        try:
            if not self.state_file.exists():
                logger.error(f"SESSION_STATE.md not found: {self.state_file}")
                return False
            
            content = self.state_file.read_text()
            lines = content.split("\n")
            
            # Find Parent line
            parent_line = f"**Parent:** {parent_id}"
            for i, line in enumerate(lines):
                if line.startswith("**Parent:**"):
                    lines[i] = parent_line
                    break
            
            content = "\n".join(lines)
            
            if not self.dry_run:
                self.state_file.write_text(content)
                logger.info(f"✓ Linked to parent: {parent_id}")
            else:
                logger.info(f"[DRY-RUN] Would link to {parent_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to link parent: {e}", exc_info=True)
            return False
    
    def declare_artifact(self, path: str, status: str = "draft", artifact_type: str = "code") -> bool:
        """Declare an artifact in SESSION_STATE.md"""
        try:
            if not self.state_file.exists():
                logger.error(f"SESSION_STATE.md not found: {self.state_file}")
                return False
            
            content = self.state_file.read_text()
            lines = content.split("\n")
            
            # Find Artifacts section
            artifact_entry = f"- `{path}` (status: {status}, type: {artifact_type})"
            
            in_artifacts = False
            insert_idx = None
            for i, line in enumerate(lines):
                if line.startswith("## Artifacts"):
                    in_artifacts = True
                    continue
                if in_artifacts:
                    if line.startswith("##"):
                        # Found next section, insert before it
                        insert_idx = i
                        break
                    if line.strip() == "(None yet)":
                        # Replace placeholder
                        lines[i] = artifact_entry
                        insert_idx = None
                        break
                    if line.startswith("- `") and path in line:
                        logger.info(f"Artifact already declared: {path}")
                        return True
            
            if insert_idx is not None:
                lines.insert(insert_idx, artifact_entry)
            
            content = "\n".join(lines)
            
            if not self.dry_run:
                self.state_file.write_text(content)
                logger.info(f"✓ Declared artifact: {path}")
            else:
                logger.info(f"[DRY-RUN] Would declare: {path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to declare artifact: {e}", exc_info=True)
            return False
    
    def list_artifacts(self) -> List[Dict]:
        """List all artifacts from SESSION_STATE.md"""
        try:
            if not self.state_file.exists():
                logger.error(f"SESSION_STATE.md not found: {self.state_file}")
                return []
            
            content = self.state_file.read_text()
            artifacts = []
            
            in_artifacts = False
            for line in content.split("\n"):
                if line.startswith("## Artifacts"):
                    in_artifacts = True
                    continue
                if in_artifacts:
                    if line.startswith("##"):
                        break
                    if line.startswith("- `"):
                        # Parse: - `path` (status: X, type: Y)
                        match = re.match(r'- `(.+?)` \(status: (.+?), type: (.+?)\)', line)
                        if match:
                            artifacts.append({
                                "path": match.group(1),
                                "status": match.group(2),
                                "type": match.group(3)
                            })
            
            return artifacts
            
        except Exception as e:
            logger.error(f"Failed to list artifacts: {e}", exc_info=True)
            return []


def main():
    parser = argparse.ArgumentParser(description="Session State Manager")
    parser.add_argument("command", choices=["init", "update", "link-parent", "declare-artifact", "list-artifacts"])
    parser.add_argument("--convo-id", required=True, help="Conversation ID")
    parser.add_argument("--type", default="build", help="Conversation type (for init)")
    parser.add_argument("--load-system", action="store_true", help="Load system context (for init)")
    parser.add_argument("--field", help="Field name (for update)")
    parser.add_argument("--value", help="Field value (for update)")
    parser.add_argument("--parent", help="Parent conversation ID (for link-parent)")
    parser.add_argument("--path", help="Artifact path (for declare-artifact)")
    parser.add_argument("--status", default="draft", help="Artifact status")
    parser.add_argument("--type-artifact", default="code", dest="type_artifact", help="Artifact type")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    
    args = parser.parse_args()
    
    manager = SessionStateManager(args.convo_id, dry_run=args.dry_run)
    success = False
    
    if args.command == "init":
        success = manager.init(args.type, args.load_system)
    elif args.command == "update":
        if not args.field or not args.value:
            logger.error("--field and --value required for update")
            return 1
        success = manager.update(args.field, args.value)
    elif args.command == "link-parent":
        if not args.parent:
            logger.error("--parent required for link-parent")
            return 1
        success = manager.link_parent(args.parent)
    elif args.command == "declare-artifact":
        if not args.path:
            logger.error("--path required for declare-artifact")
            return 1
        success = manager.declare_artifact(args.path, args.status, args.type_artifact)
    elif args.command == "list-artifacts":
        artifacts = manager.list_artifacts()
        if artifacts:
            print("\nArtifacts:")
            for art in artifacts:
                print(f"  - {art['path']} (status: {art['status']}, type: {art['type']})")
        else:
            print("No artifacts declared")
        success = True
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
