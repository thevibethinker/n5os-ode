#!/usr/bin/env python3
"""
Spawn Worker Thread - Parallel Conversation Forking

Creates a lightweight worker assignment that forks current conversation context
into a parallel thread. Worker and parent remain aware of each other through
session state linkage.

Usage:
    python3 spawn_worker.py --parent con_ABC --instruction "Research OAuth alternatives"
    python3 spawn_worker.py --parent con_ABC  # Agnostic spawn
    python3 spawn_worker.py --parent con_ABC --instruction "..." --dry-run
"""

import argparse
import json
import logging
import sys
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)

WORKSPACE = Path("/home/workspace")
CONVERSATION_WORKSPACE_BASE = Path("/home/.z/workspaces")


class WorkerSpawner:
    """Handles creation of parallel worker threads with context handoff."""
    
    def __init__(self, parent_convo_id: str, instruction: Optional[str], dry_run: bool = False):
        self.parent_convo_id = parent_convo_id
        self.instruction = instruction
        self.dry_run = dry_run
        self.parent_workspace = CONVERSATION_WORKSPACE_BASE / parent_convo_id
        self.parent_session_state = self.parent_workspace / "SESSION_STATE.md"
        
    def validate_inputs(self) -> bool:
        """Validate parent conversation exists and has session state."""
        if not self.parent_workspace.exists():
            logger.error(f"Parent conversation workspace not found: {self.parent_workspace}")
            return False
            
        if not self.parent_session_state.exists():
            logger.error(f"Parent SESSION_STATE.md not found: {self.parent_session_state}")
            logger.info("Run: python3 N5/scripts/session_state_manager.py init --convo-id {self.parent_convo_id}")
            return False
            
        return True
    
    # --- NEW helpers for robust parsing ---
    def _extract_value(self, content: str, pattern: str) -> str:
        """Return first regex group match or 'Not specified'."""
        for line in content.split("\n"):
            m = re.match(pattern, line.strip())
            if m:
                val = m.group(1).strip()
                return self._clean_value(val)
        return "Not specified"

    def _clean_value(self, val: str) -> str:
        # Remove leading/trailing markdown artifacts like ** or *
        val = val.strip()
        val = re.sub(r"^\*+\s*", "", val)  # leading asterisks
        val = re.sub(r"\s*\*+$", "", val)  # trailing asterisks
        return val.strip()

    def _extract_focus(self, content: str) -> str:
        # Try explicit Focus field under Type & Mode
        val = self._extract_value(content, r"^\*\*Focus:\*\*\s*(.+)$")
        if val != "Not specified":
            # Filter placeholder question
            if "?" in val and val.startswith("What "):
                return "Not specified (placeholder not filled)"
            return val
        return "Not specified"

    def _extract_objective(self, content: str) -> str:
        # Prefer Objective → Goal line inside the Objective section
        # Matches '**Goal:** something' or 'Goal: something'
        for line in content.split("\n"):
            m = re.match(r"^(?:\*\*\s*)?Goal:(?:\s*\*\*)?\s*(.+)$", line.strip(), re.IGNORECASE)
            if m:
                val = self._clean_value(m.group(1))
                if val and not ("?" in val and val.lower().startswith("what")):
                    return val
        # Backward-compat: '**Objective:** value' if present
        val = self._extract_value(content, r"^\*\*Objective:\*\*\s*(.+)$")
        return val

    def read_parent_session_state(self) -> dict:
        """Extract key info from parent SESSION_STATE.md."""
        try:
            content = self.parent_session_state.read_text()
            state = {
                "focus": self._extract_focus(content),
                "objective": self._extract_objective(content),
                "status": self._extract_value(content, r"^\*\*Status:\*\*\s*(.+)$"),
                # SESSION_STATE uses 'Primary Type' instead of 'Conversation Type'
                "conversation_type": self._extract_value(content, r"^\*\*Primary Type:\*\*\s*(.+)$"),
            }
            logger.info(f"Extracted parent state fields: focus='{state['focus']}', objective='{state['objective']}', status='{state['status']}', type='{state['conversation_type']}'")
            return state
        except Exception as e:
            logger.error(f"Failed to read parent session state: {e}")
            return {}

    def _extract_section(self, content: str, section_name: str) -> str:
        """Extract entire section from markdown content."""
        lines = content.split("\n")
        in_section = False
        section_lines = []
        
        for line in lines:
            if line.startswith(f"## {section_name}"):
                in_section = True
                continue
            elif in_section:
                if line.startswith("##"):  # Next section
                    break
                section_lines.append(line)
        
        return "\n".join(section_lines).strip()

    
    def gather_context(self) -> dict:
        """Gather context from parent conversation workspace.
        
        Strategy:
        1. Try SESSION_STATE first (structured metadata)
        2. If placeholders detected, fall back to workspace intelligence
        3. Infer context from artifacts, file patterns, and content
        """
        parent_state = self.read_parent_session_state()
        has_placeholders = any(
            "placeholder" in str(v).lower() or "not specified" in str(v).lower()
            for v in parent_state.values()
        )
        
        context = {
            "parent_convo_id": self.parent_convo_id,
            "spawn_timestamp": datetime.now(timezone.utc).isoformat(),
            "parent_state": parent_state,
            "recent_artifacts": [],
            "timeline_summary": "",
            "inferred_context": None,
        }
        
        # If SESSION_STATE has placeholders, do intelligent inference
        if has_placeholders:
            logger.info("SESSION_STATE has placeholders, inferring context from workspace...")
            context["inferred_context"] = self._infer_context_from_workspace()
        
        # Extract timeline summary from SESSION_STATE
        try:
            session_content = self.parent_session_state.read_text()
            timeline_section = self._extract_section(session_content, "Timeline")
            if timeline_section:
                context["timeline_summary"] = timeline_section
        except Exception as e:
            logger.warning(f"Could not extract timeline: {e}")
        
        # Find all recently created/modified files in parent workspace
        # Exclude hidden dirs, pycache, etc.
        exclude_patterns = {"__pycache__", ".git", ".pyc", "worker_updates"}
        
        try:
            all_files = []
            for item in self.parent_workspace.rglob("*"):
                if item.is_file():
                    # Skip excluded patterns
                    if any(excl in str(item) for excl in exclude_patterns):
                        continue
                    all_files.append((item, item.stat().st_mtime))
            
            # Sort by modification time, get most recent 15
            recent_files = sorted(all_files, key=lambda x: x[1], reverse=True)[:15]
            
            context["recent_artifacts"] = [
                {
                    "path": str(f[0].relative_to(self.parent_workspace)),
                    "size": f[0].stat().st_size,
                    "modified": datetime.fromtimestamp(f[1], timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
                }
                for f in recent_files
            ]
            
            logger.info(f"Found {len(context['recent_artifacts'])} recent artifacts")
        except Exception as e:
            logger.warning(f"Could not gather artifacts: {e}")
            
        return context
    
    def _infer_context_from_workspace(self) -> dict:
        """Infer conversation context from workspace artifacts when SESSION_STATE is empty."""
        inference = {
            "likely_topic": "Unknown",
            "work_type": "Unknown",
            "key_files": [],
            "summary": "",
        }
        
        try:
            # Gather all files
            exclude_patterns = {"__pycache__", ".git", ".pyc", "worker_updates", "SESSION_STATE"}
            files = []
            
            for item in self.parent_workspace.rglob("*"):
                if item.is_file() and not any(excl in str(item) for excl in exclude_patterns):
                    files.append(item)
            
            if not files:
                inference["summary"] = "Empty workspace, no artifacts found"
                return inference
            
            # Analyze file patterns
            file_analysis = self._analyze_file_patterns(files)
            inference["likely_topic"] = file_analysis["topic"]
            inference["work_type"] = file_analysis["work_type"]
            inference["key_files"] = file_analysis["key_files"][:5]  # Top 5
            
            # Generate summary
            summary_parts = []
            summary_parts.append(f"**Inferred work type:** {file_analysis['work_type']}")
            summary_parts.append(f"**Likely topic:** {file_analysis['topic']}")
            
            if file_analysis['key_files']:
                summary_parts.append(f"**Key artifacts:** {', '.join(f'`{f}`' for f in file_analysis['key_files'][:3])}")
            
            inference["summary"] = "\n".join(summary_parts)
            
            logger.info(f"Inferred: {file_analysis['work_type']} related to {file_analysis['topic']}")
            
        except Exception as e:
            logger.warning(f"Could not infer context: {e}")
            inference["summary"] = "Could not infer context from workspace"
        
        return inference
    
    def _analyze_file_patterns(self, files: list) -> dict:
        """Analyze file patterns to infer what's being worked on."""
        extensions = {}
        keywords = {}
        largest_files = []
        
        # Count file types and keywords
        for f in files:
            ext = f.suffix.lower()
            extensions[ext] = extensions.get(ext, 0) + 1
            
            # Extract keywords from filename
            name_lower = f.stem.lower()
            for keyword in ['bootstrap', 'export', 'auth', 'api', 'test', 'config', 'script', 
                          'worker', 'build', 'deploy', 'database', 'schema', 'migration']:
                if keyword in name_lower:
                    keywords[keyword] = keywords.get(keyword, 0) + 1
            
            # Track largest files
            try:
                size = f.stat().st_size
                largest_files.append((f.name, size))
            except:
                pass
        
        largest_files.sort(key=lambda x: x[1], reverse=True)
        
        # Infer work type from extensions
        work_type = "General development"
        if '.py' in extensions:
            work_type = "Python development"
        if '.js' in extensions or '.ts' in extensions:
            work_type = "JavaScript/TypeScript development"
        if '.md' in extensions and extensions.get('.md', 0) > 3:
            work_type = "Documentation/planning"
        if '.json' in extensions:
            if work_type == "General development":
                work_type = "Configuration/data work"
        
        # Infer topic from keywords
        topic = "unspecified"
        if keywords:
            top_keyword = max(keywords.items(), key=lambda x: x[1])[0]
            topic = top_keyword.replace('_', ' ').title()
        
        # If still unclear, use largest file names
        if topic == "unspecified" and largest_files:
            topic = largest_files[0][0].replace('_', ' ').replace('-', ' ').title()
        
        return {
            "work_type": work_type,
            "topic": topic,
            "key_files": [f[0] for f in largest_files[:5]],
            "file_count": len(files),
        }
    
    def generate_worker_assignment(self, context: dict) -> str:
        """Generate worker assignment markdown content."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        worker_id = self.parent_convo_id[-4:]  # Last 4 chars of parent ID
        
        assignment = f"""# Worker Assignment - Parallel Thread

**Generated:** {context['spawn_timestamp']}  
**Parent Conversation:** {self.parent_convo_id}  
**Worker ID:** WORKER_{worker_id}_{timestamp}

---

## Your Mission

"""
        
        if self.instruction:
            assignment += f"""{self.instruction}

---

## Parent Context

"""
        else:
            assignment += """This is an **agnostic worker spawn**. You have full context from the parent conversation below, but no specific directive.

Work in parallel with the parent thread on whatever makes sense given the context.

---

## Parent Context

"""
        
        assignment += f"""**What parent is working on:**  
{context['parent_state'].get('focus', 'Not specified')}

**Parent objective:**  
{context['parent_state'].get('objective', 'Not specified')}

**Parent status:**  
{context['parent_state'].get('status', 'Not specified')}

**Parent conversation type:**  
{context['parent_state'].get('conversation_type', 'Not specified')}

"""
        
        # Add inferred context if available
        if context.get('inferred_context'):
            inferred = context['inferred_context']
            assignment += f"""\n### 🔍 Inferred Context (from workspace analysis)

{inferred['summary']}
"""
        
        assignment += "\n---\n\n## Recent Activity in Parent Thread\n\n"
        
        if context['recent_artifacts']:
            assignment += "**Recently generated files:**\n\n"
            for artifact in context['recent_artifacts']:
                path = artifact['path']
                size = artifact['size']
                modified = artifact['modified']
                # Format size nicely
                if size < 1024:
                    size_str = f"{size}B"
                elif size < 1024 * 1024:
                    size_str = f"{size/1024:.1f}KB"
                else:
                    size_str = f"{size/(1024*1024):.1f}MB"
                assignment += f"- `{path}` ({size_str}, modified {modified})\n"
        else:
            assignment += "*No recent artifacts in parent workspace*\n"
        
        # Add timeline if available
        if context.get('timeline_summary'):
            assignment += f"\n**Parent Activity Timeline:**\n\n{context['timeline_summary']}\n"
        
        assignment += """
---

## Instructions for This Worker Thread

1. **Initialize your own session state:**
   ```bash
   python3 /home/workspace/N5/scripts/session_state_manager.py init \\
       --convo-id <YOUR_CONVERSATION_ID> \\
       --load-system
   ```

2. **Link back to parent:**
   ```bash
   python3 /home/workspace/N5/scripts/session_state_manager.py link-parent \\
       --parent """ + self.parent_convo_id + """
   ```

3. **Write status updates to parent workspace:**
   - Location: `""" + str(self.parent_workspace / "worker_updates" / "WORKER_<YOUR_ID>_status.md") + """`
   - Format: Brief status, what you're working on, blockers if any
   - Frequency: At natural checkpoints (milestones, completions, errors)

4. **Report test results:**
   - Create: `""" + str(self.parent_workspace / "worker_updates" / "WORKER_<YOUR_ID>_test_results.json") + """`
   - Format: JSON with `{"tests_run": N, "passed": N, "failed": N, "details": [...]}`
   - When: Immediately after running test suite

5. **Dump completion report:**
   - Create: `""" + str(self.parent_workspace / "worker_updates" / "WORKER_<YOUR_ID>_completion.md") + """`
   - Format: Full summary, what was built, test results, lessons learned
   - When: When work is 100% complete

6. **Store generated artifacts:**
   - Directory: `""" + str(self.parent_workspace / "worker_updates" / "WORKER_<YOUR_ID>_artifacts") + """`
   - Structure: Organize by type (code, docs, data, etc.)
   - Include: All files you generate (scripts, configs, documents, etc.)

7. **Work independently:**
   - You're running in parallel, not sequentially
   - Parent may or may not be actively working
   - Coordinate through workspace writes, not direct communication

---

## Communication Protocol

**You → Parent:** Write status updates to parent's workspace (path above)  
**Parent → You:** Parent may update your assignment or provide input via your workspace

**Both of you know about each other** through SESSION_STATE linkage.

---

**Ready to work in parallel!**

*Generated by spawn_worker.py v1.1*
"""
        
        return assignment
    
    def write_assignment_file(self, content: str) -> Path:
        """Write worker assignment to Records/Temporary/."""
        # Use microseconds for uniqueness when spawning multiple workers rapidly
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
        worker_id = self.parent_convo_id[-4:]
        
        filename = f"WORKER_ASSIGNMENT_{timestamp}_{worker_id}.md"
        output_path = WORKSPACE / "Records" / "Temporary" / filename
        
        # Ensure directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would write to: {output_path}")
            logger.info(f"[DRY RUN] Content preview:\n{content[:500]}...")
            return output_path
        
        output_path.write_text(content)
        logger.info(f"✓ Worker assignment created: {output_path}")
        
        return output_path
    
    def update_parent_session_state(self, worker_file: Path) -> bool:
        """Add spawned worker reference to parent SESSION_STATE.md."""
        try:
            content = self.parent_session_state.read_text()
            
            # Find or create Spawned Workers section
            worker_entry = f"- {worker_file.name} (spawned {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC)"
            
            if "## Spawned Workers" in content:
                # Append to existing section
                lines = content.split("\n")
                for i, line in enumerate(lines):
                    if line.startswith("## Spawned Workers"):
                        # Insert after section header
                        lines.insert(i + 2, worker_entry)
                        break
                content = "\n".join(lines)
            else:
                # Add new section at end
                content += f"\n\n## Spawned Workers\n\n{worker_entry}\n"
            
            if self.dry_run:
                logger.info(f"[DRY RUN] Would update parent SESSION_STATE with: {worker_entry}")
                return True
            
            self.parent_session_state.write_text(content)
            logger.info(f"✓ Updated parent SESSION_STATE: {worker_entry}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update parent SESSION_STATE: {e}")
            return False
    
    def create_worker_updates_dir(self) -> bool:
        """Create worker_updates directory in parent workspace."""
        updates_dir = self.parent_workspace / "worker_updates"
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would create directory: {updates_dir}")
            return True
        
        try:
            updates_dir.mkdir(exist_ok=True)
            logger.info(f"✓ Created worker updates directory: {updates_dir}")
            return True
        except Exception as e:
            logger.error(f"Failed to create worker_updates directory: {e}")
            return False
    
    def verify_state(self, assignment_path: Path) -> bool:
        """Verify assignment file was created correctly."""
        if self.dry_run:
            return True
            
        if not assignment_path.exists():
            logger.error(f"Verification failed: {assignment_path} does not exist")
            return False
        
        size = assignment_path.stat().st_size
        if size < 100:
            logger.error(f"Verification failed: {assignment_path} is too small ({size} bytes)")
            return False
        
        logger.info(f"✓ Verification passed: {assignment_path} ({size} bytes)")
        return True
    
    def spawn(self) -> int:
        """Main spawn workflow."""
        try:
            # Validate
            if not self.validate_inputs():
                return 1
            
            # Gather context
            logger.info("Gathering context from parent conversation...")
            context = self.gather_context()
            
            # Generate assignment
            logger.info("Generating worker assignment...")
            assignment_content = self.generate_worker_assignment(context)
            
            # Write assignment file
            assignment_path = self.write_assignment_file(assignment_content)
            
            # Update parent session state
            if not self.update_parent_session_state(assignment_path):
                logger.warning("Failed to update parent SESSION_STATE, but assignment file created")
            
            # Create worker updates directory
            if not self.create_worker_updates_dir():
                logger.warning("Failed to create worker_updates directory")
            
            # Verify
            if not self.verify_state(assignment_path):
                return 1
            
            if not self.dry_run:
                logger.info(f"\n✓ Worker spawned successfully!")
                logger.info(f"📄 Open this file in a new conversation: {assignment_path}")
            
            return 0
            
        except Exception as e:
            logger.error(f"Spawn failed: {e}", exc_info=True)
            return 1


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Spawn parallel worker thread with context handoff"
    )
    parser.add_argument(
        "--parent",
        required=True,
        help="Parent conversation ID (e.g., con_ABC123)"
    )
    parser.add_argument(
        "--instruction",
        help="Specific instruction for worker (optional, spawns agnostic if omitted)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without making changes"
    )
    
    args = parser.parse_args()
    
    spawner = WorkerSpawner(
        parent_convo_id=args.parent,
        instruction=args.instruction,
        dry_run=args.dry_run
    )
    
    return spawner.spawn()


if __name__ == "__main__":
    sys.exit(main())

