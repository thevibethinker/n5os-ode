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
from typing import Dict, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)

CONVO_WORKSPACES_ROOT = Path("/home/.z/workspaces")
TEMPLATE_FILE = Path("/home/.z/workspaces/con_AFQURXo7KW89yWVw/SESSION_STATE_TEMPLATE.md")


class SessionStateManager:
    def __init__(self, convo_id: str):
        self.convo_id = convo_id
        self.workspace = CONVO_WORKSPACES_ROOT / convo_id
        self.state_file = self.workspace / "SESSION_STATE.md"
        
        self.workspace.mkdir(parents=True, exist_ok=True)
    
    def init(self, convo_type: str = "build", mode: str = "implementation") -> bool:
        """Initialize SESSION_STATE.md from template."""
        try:
            if self.state_file.exists():
                logger.info(f"SESSION_STATE.md already exists for {self.convo_id}")
                return True
            
            now = datetime.now(timezone.utc)
            now_et = now.astimezone().strftime("%Y-%m-%d %H:%M ET")
            
            content = f"""# Session State
**Auto-generated | Updated continuously**

---

## Metadata
**Conversation ID:** {self.convo_id}  
**Started:** {now_et}  
**Last Updated:** {now_et}  
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
**[{now_et}]** Decision 1 - Rationale

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

**[{now_et}]** Started conversation, initialized state

---

## Tags
#{convo_type} #active

---

## Notes
*Free-form observations, reminders, context*
"""
            
            self.state_file.write_text(content)
            logger.info(f"✓ Initialized SESSION_STATE.md for {self.convo_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize SESSION_STATE.md: {e}", exc_info=True)
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


def main():
    parser = argparse.ArgumentParser(description="Session State Manager")
    parser.add_argument("action", choices=["init", "update", "read"])
    parser.add_argument("--convo-id", required=True)
    parser.add_argument("--type", default="build", choices=["build", "research", "discussion", "planning"])
    parser.add_argument("--mode", default="implementation")
    parser.add_argument("--field", help="Field to update")
    parser.add_argument("--value", help="New value for field")
    
    args = parser.parse_args()
    
    manager = SessionStateManager(args.convo_id)
    
    if args.action == "init":
        success = manager.init(convo_type=args.type, mode=args.mode)
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
