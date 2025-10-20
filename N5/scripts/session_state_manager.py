#!/usr/bin/env python3
"""
Session State Manager
Auto-initializes and updates SESSION_STATE.md for all conversations.

Usage:
    python3 session_state_manager.py init --convo-id con_XXX [--type build|research|discussion|planning]
    python3 session_state_manager.py update --convo-id con_XXX --field status --value active
    python3 session_state_manager.py read --convo-id con_XXX
"""

import argparse
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional, Tuple
import pytz
import re

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)

CONVO_WORKSPACES_ROOT = Path("/home/.z/workspaces")
TEMPLATE_FILE = Path("/home/.z/workspaces/con_AFQURXo7KW89yWVw/SESSION_STATE_TEMPLATE.md")
TEMPLATES_DIR = Path("/home/workspace/N5/templates/session_state")


class SessionStateManager:
    def __init__(self, convo_id: str):
        self.convo_id = convo_id
        self.workspace = CONVO_WORKSPACES_ROOT / convo_id
        self.state_file = self.workspace / "SESSION_STATE.md"
        
        self.workspace.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def classify_conversation(message: str) -> Tuple[str, float]:
        """
        Auto-classify conversation type from first user message.
        
        Returns: (type, confidence_score)
        Types: build, research, discussion, planning
        """
        message_lower = message.lower()
        
        # Build indicators
        build_keywords = [
            "build", "implement", "code", "script", "create", "develop",
            "write", "program", "function", "class", "api", "database",
            "refactor", "debug", "fix", "error", "bug"
        ]
        build_score = sum(1 for kw in build_keywords if kw in message_lower)
        
        # Research indicators
        research_keywords = [
            "research", "analyze", "learn", "study", "investigate",
            "understand", "explain", "how does", "what is", "compare",
            "evaluate", "review", "explore options"
        ]
        research_score = sum(1 for kw in research_keywords if kw in message_lower)
        
        # Discussion indicators
        discussion_keywords = [
            "discuss", "think", "explore", "brainstorm", "consider",
            "thoughts on", "what do you think", "perspective", "opinion",
            "talk about", "let's explore"
        ]
        discussion_score = sum(1 for kw in discussion_keywords if kw in message_lower)
        
        # Planning indicators
        planning_keywords = [
            "plan", "strategy", "decide", "organize", "roadmap",
            "schedule", "timeline", "prioritize", "outline", "design",
            "architecture", "approach", "steps"
        ]
        planning_score = sum(1 for kw in planning_keywords if kw in message_lower)
        
        scores = {
            "build": build_score,
            "research": research_score,
            "discussion": discussion_score,
            "planning": planning_score
        }
        
        max_type = max(scores, key=scores.get)
        max_score = scores[max_type]
        total_score = sum(scores.values())
        
        # Confidence: ratio of max score to total
        confidence = max_score / total_score if total_score > 0 else 0.0
        
        # Default to discussion if no strong signals
        if total_score == 0:
            return "discussion", 0.0
        
        return max_type, round(confidence, 2)
    
    def init(self, convo_type: Optional[str] = None, mode: str = "", load_system: bool = False, user_message: str = "") -> bool:
        """Initialize SESSION_STATE.md for this conversation."""
        try:
            if self.state_file.exists():
                logger.info(f"SESSION_STATE.md already exists for {self.convo_id}")
                return True
            
            # Auto-classify if no type provided and user message available
            if not convo_type and user_message:
                detected_type, confidence = self.classify_conversation(user_message)
                logger.info(f"Auto-classified as '{detected_type}' (confidence: {confidence})")
                convo_type = detected_type
            
            # Default to discussion
            if not convo_type:
                convo_type = "discussion"
            
            now = datetime.now(timezone.utc)
            now_et = now.astimezone(pytz.timezone('America/New_York'))
            start_time = now_et.strftime('%Y-%m-%d %H:%M ET')
            
            # Check for type-specific template
            template_path = TEMPLATES_DIR / f"{convo_type}.md"
            if template_path.exists():
                logger.info(f"Using {convo_type} template")
                content = template_path.read_text()
                # Replace placeholders
                content = content.replace("{convo_id}", self.convo_id)
                content = content.replace("{start_time}", start_time)
                content = content.replace("{last_updated}", start_time)
                content = content.replace("{mode}", mode)
                content = content.replace("{focus}", "*What is this conversation specifically about?*")
                content = content.replace("{objective}", "*What are we trying to accomplish?*")
            else:
                # Use generic template
                content = f"""# Session State
**Auto-generated | Updated continuously**

---

## Metadata
**Conversation ID:** {self.convo_id}  
**Started:** {start_time}  
**Last Updated:** {start_time}  
**Status:** active  

---

## Type & Mode
**Primary Type:** {convo_type}  
**Mode:** {mode}  
**Focus:** *What is this conversation specifically about?*

---

## Objective
**Goal:** *What are we trying to accomplish?*

**Success Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2

---

## Progress

### Current Task
*What is actively being worked on right now*

### Completed
- ✅ Item 1

### Blocked
- ⛔ Item (reason)

### Next Actions
1. Action 1
2. Action 2

---

## Insights & Decisions

### Key Insights
*Important realizations discovered during this session*

### Decisions Made
**[{start_time}]** Decision 1 - Rationale

### Open Questions
- Question 1?
- Question 2?

---

## Outputs
**Artifacts Created:**
- `path/to/file` - Description

**Knowledge Generated:**
- Key concept or pattern

---

## Relationships

### Related Conversations
*Links to other conversations on this topic*
- con_XXX - Description

### Dependencies
**Depends on:**
- Thing 1

**Blocks:**
- Thing 2

---

## Context

### Files in Context
*What files/docs are actively being used*

### Principles Active
*Which N5 principles are guiding this work*

---

## Timeline
*High-level log of major updates*

**[{start_time}]** Started conversation, initialized state

---

## Tags
#{convo_type} #active

---

## Notes
*Free-form observations, reminders, context*
"""
            
            self.state_file.write_text(content)
            logger.info(f"✓ Initialized SESSION_STATE.md for {self.convo_id}")
            
            if load_system:
                logger.info("System files to load:")
                logger.info("  - file 'Documents/N5.md'")
                logger.info("  - file 'N5/prefs/prefs.md'")
            
            return True
        except Exception as e:
            logger.error(f"Failed to initialize SESSION_STATE: {e}")
            return False
    
    def read(self) -> Optional[Dict]:
        """Read and parse SESSION_STATE.md into dict."""
        try:
            if not self.state_file.exists():
                return None
            
            content = self.state_file.read_text()
            
            # Parse basic fields
            state = {
                "convo_id": self.convo_id,
                "exists": True,
                "content": content
            }
            
            # Extract key fields
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if line.startswith("**Status:**"):
                    state["status"] = line.split("**Status:**")[1].strip()
                elif line.startswith("**Primary Type:**"):
                    state["type"] = line.split("**Primary Type:**")[1].strip()
                elif line.startswith("**Mode:**"):
                    state["mode"] = line.split("**Mode:**")[1].strip()
                elif line.startswith("**Focus:**"):
                    state["focus"] = line.split("**Focus:**")[1].strip().strip("*")
            
            return state
            
        except Exception as e:
            logger.error(f"Failed to read SESSION_STATE.md: {e}", exc_info=True)
            return None
    
    def update_field(self, field: str, value: str) -> bool:
        """Update a specific field in SESSION_STATE.md."""
        try:
            if not self.state_file.exists():
                logger.error("SESSION_STATE.md does not exist, run init first")
                return False
            
            content = self.state_file.read_text()
            lines = content.split("\n")
            
            # Update timestamp
            now_et = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M ET")
            
            # Find and update field
            updated = False
            for i, line in enumerate(lines):
                if field == "status" and line.startswith("**Status:**"):
                    lines[i] = f"**Status:** {value}  "
                    updated = True
                elif field == "last_updated" and line.startswith("**Last Updated:**"):
                    lines[i] = f"**Last Updated:** {now_et}  "
                    updated = True
                elif field == "type" and line.startswith("**Primary Type:**"):
                    lines[i] = f"**Primary Type:** {value}  "
                    updated = True
                elif field == "mode" and line.startswith("**Mode:**"):
                    lines[i] = f"**Mode:** {value}  "
                    updated = True
                elif field == "focus" and line.startswith("**Focus:**"):
                    lines[i] = f"**Focus:** {value}"
                    updated = True
            
            if updated:
                # Also update last_updated timestamp
                for i, line in enumerate(lines):
                    if line.startswith("**Last Updated:**"):
                        lines[i] = f"**Last Updated:** {now_et}  "
                
                self.state_file.write_text("\n".join(lines))
                logger.info(f"✓ Updated {field} = {value}")
                return True
            else:
                logger.warning(f"Field '{field}' not found in SESSION_STATE.md")
                return False
            
        except Exception as e:
            logger.error(f"Failed to update SESSION_STATE.md: {e}", exc_info=True)
            return False
    
    def add_decision(self, decision: str, rationale: str, alternatives: str = "") -> bool:
        """Add an architectural decision to the log."""
        try:
            if not self.state_file.exists():
                logger.error("SESSION_STATE.md does not exist")
                return False
            
            content = self.state_file.read_text()
            now_et = datetime.now(timezone.utc).astimezone(pytz.timezone('America/New_York')).strftime("%Y-%m-%d %H:%M ET")
            
            # Format decision entry
            entry = f"\n**[{now_et}] {decision}**\n"
            entry += f"- Rationale: {rationale}\n"
            if alternatives:
                entry += f"- Alternatives: {alternatives}\n"
            
            # Find Architectural Decisions section
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if line.strip() == "## Architectural Decisions":
                    # Skip header and description
                    insert_pos = i + 3
                    # Skip "No decisions" if present
                    if insert_pos < len(lines) and "No decisions" in lines[insert_pos]:
                        lines[insert_pos] = entry.strip()
                    else:
                        lines.insert(insert_pos, entry)
                    break
            
            self.state_file.write_text("\n".join(lines))
            logger.info(f"✓ Added decision: {decision}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add decision: {e}", exc_info=True)
            return False
    
    def update_phase(self, phase: str, progress: int = None) -> bool:
        """Update build phase and optional progress percentage."""
        valid_phases = ["design", "implementation", "testing", "deployment", "complete"]
        if phase not in valid_phases:
            logger.error(f"Invalid phase: {phase}. Must be one of {valid_phases}")
            return False
        
        try:
            if not self.state_file.exists():
                logger.error("SESSION_STATE.md does not exist")
                return False
            
            content = self.state_file.read_text()
            lines = content.split("\n")
            
            for i, line in enumerate(lines):
                if line.startswith("**Current Phase:**"):
                    lines[i] = f"**Current Phase:** {phase}"
                elif progress is not None and line.startswith("**Progress:**"):
                    lines[i] = f"**Progress:** {progress}% complete"
            
            self.state_file.write_text("\n".join(lines))
            logger.info(f"✓ Updated phase: {phase}" + (f" ({progress}%)" if progress else ""))
            return True
            
        except Exception as e:
            logger.error(f"Failed to update phase: {e}", exc_info=True)
            return False
    
    def add_file(self, filepath: str, status: str = "not started") -> bool:
        """Add a file to the manifest with status."""
        status_icons = {
            "not started": "⏳",
            "in progress": "🔄",
            "complete": "✅",
            "blocked": "⛔",
            "tested": "✓"
        }
        
        try:
            if not self.state_file.exists():
                logger.error("SESSION_STATE.md does not exist")
                return False
            
            icon = status_icons.get(status, "⏳")
            content = self.state_file.read_text()
            lines = content.split("\n")
            
            # Find Files section
            for i, line in enumerate(lines):
                if line.strip() == "## Files":
                    # Find insertion point (after header, before legend)
                    insert_pos = i + 3
                    # Skip "No files" if present
                    if insert_pos < len(lines) and "No files" in lines[insert_pos]:
                        lines[insert_pos] = f"- {icon} `{filepath}` - {status}"
                    else:
                        # Insert before legend
                        for j in range(insert_pos, len(lines)):
                            if lines[j].startswith("**Status Legend:**"):
                                lines.insert(j, f"- {icon} `{filepath}` - {status}")
                                break
                    break
            
            self.state_file.write_text("\n".join(lines))
            logger.info(f"✓ Added file: {filepath} ({status})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add file: {e}", exc_info=True)
            return False
    
    def update_file_status(self, filepath: str, new_status: str) -> bool:
        """Update status of an existing file."""
        status_icons = {
            "not started": "⏳",
            "in progress": "🔄",
            "complete": "✅",
            "blocked": "⛔",
            "tested": "✓"
        }
        
        try:
            if not self.state_file.exists():
                logger.error("SESSION_STATE.md does not exist")
                return False
            
            icon = status_icons.get(new_status, "⏳")
            content = self.state_file.read_text()
            lines = content.split("\n")
            
            updated = False
            for i, line in enumerate(lines):
                if f"`{filepath}`" in line and line.strip().startswith("-"):
                    lines[i] = f"- {icon} `{filepath}` - {new_status}"
                    updated = True
                    break
            
            if updated:
                self.state_file.write_text("\n".join(lines))
                logger.info(f"✓ Updated file status: {filepath} → {new_status}")
                return True
            else:
                logger.warning(f"File not found: {filepath}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to update file status: {e}", exc_info=True)
            return False
    
    def add_test(self, test_name: str, status: str = "not written") -> bool:
        """Add a test to the checklist."""
        icon = "✅" if status == "passing" else "⏳"
        checked = "[x]" if status == "passing" else "[ ]"
        
        try:
            if not self.state_file.exists():
                logger.error("SESSION_STATE.md does not exist")
                return False
            
            content = self.state_file.read_text()
            lines = content.split("\n")
            
            # Find Tests section
            for i, line in enumerate(lines):
                if line.strip() == "## Tests":
                    insert_pos = i + 3
                    # Skip "No tests" if present
                    if insert_pos < len(lines) and "No tests" in lines[insert_pos]:
                        lines[insert_pos] = f"- {checked} {test_name} ({status})"
                    else:
                        # Find next section header
                        for j in range(insert_pos, len(lines)):
                            if lines[j].startswith("##"):
                                lines.insert(j - 1, f"- {checked} {test_name} ({status})")
                                break
                    break
            
            self.state_file.write_text("\n".join(lines))
            logger.info(f"✓ Added test: {test_name} ({status})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add test: {e}", exc_info=True)
            return False
    
    def update_rollback_plan(self, plan: str) -> bool:
        """Update or set the rollback plan."""
        try:
            if not self.state_file.exists():
                logger.error("SESSION_STATE.md does not exist")
                return False
            
            content = self.state_file.read_text()
            lines = content.split("\n")
            
            # Find Rollback Plan section
            for i, line in enumerate(lines):
                if line.strip() == "## Rollback Plan":
                    # Replace next non-empty line
                    insert_pos = i + 3
                    if insert_pos < len(lines):
                        lines[insert_pos] = plan
                    break
            
            self.state_file.write_text("\n".join(lines))
            logger.info(f"✓ Updated rollback plan")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update rollback plan: {e}", exc_info=True)
            return False

    def link_parent(self, parent_convo_id: str) -> bool:
        """Link this worker conversation to its parent."""
        try:
            if not self.state_file.exists():
                logger.error(f"SESSION_STATE.md not found. Run init first.")
                return False
            
            content = self.state_file.read_text()
            
            # Find or create Parent Conversation section
            parent_line = f"**Parent Conversation:** {parent_convo_id}"
            
            if "## Metadata" in content:
                lines = content.split("\n")
                for i, line in enumerate(lines):
                    if line.startswith("## Metadata"):
                        # Find end of existing metadata (next blank line or section)
                        insert_idx = i + 1
                        while insert_idx < len(lines) and lines[insert_idx].strip() != "" and not lines[insert_idx].startswith("##"):
                            insert_idx += 1
                        lines.insert(insert_idx, parent_line + "  ")
                        break
                content = "\n".join(lines)
            else:
                # Add new section after metadata header
                content = content.replace("## Metadata", f"## Metadata\n\n{parent_line}", 1)
            
            self.state_file.write_text(content)
            logger.info(f"✓ Linked to parent: {parent_convo_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to link parent: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description="Session State Manager")
    parser.add_argument("action", choices=["init", "update", "read", "link-parent"])
    parser.add_argument("--convo-id", help="Conversation ID (required for init/update/read)")
    parser.add_argument("--type", default=None, choices=["build", "research", "discussion", "planning"])
    parser.add_argument("--mode", type=str, default="", help="Specific mode within type")
    parser.add_argument("--load-system", action="store_true", help="Output system files to load")
    parser.add_argument("--message", type=str, default="", help="User message for auto-classification")
    parser.add_argument("--field", type=str, help="Field to update")
    parser.add_argument("--value", help="New value for field")
    parser.add_argument("--parent", type=str, help="Parent conversation ID (for link-parent action)")
    
    args = parser.parse_args()
    
    if args.action == "link-parent":
        if not args.parent:
            logger.error("--parent required for link-parent action")
            return 1
        # Get current convo ID from environment or workspace
        import os
        current_convo = os.environ.get("ZO_CONVERSATION_ID", "")
        if not current_convo:
            logger.error("Cannot determine current conversation ID. Please run from within a Zo conversation.")
            return 1
        manager = SessionStateManager(current_convo)
        success = manager.link_parent(args.parent)
        return 0 if success else 1
    
    if not args.convo_id:
        logger.error("--convo-id required for this action")
        return 1
    
    manager = SessionStateManager(args.convo_id)
    
    if args.action == "init":
        success = manager.init(convo_type=args.type, mode=args.mode, load_system=args.load_system, user_message=args.message)
        return 0 if success else 1
    
    elif args.action == "read":
        state = manager.read()
        if state:
            print(json.dumps(state, indent=2))
            return 0
        return 1
    
    elif args.action == "update":
        if not args.field or not args.value:
            logger.error("--field and --value required for update action")
            return 1
        success = manager.update_field(args.field, args.value)
        return 0 if success else 1
    
    return 0


if __name__ == "__main__":
    exit(main())
