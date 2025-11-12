#!/usr/bin/env python3
"""
SESSION_STATE Manager - Manage conversation state files

Commands:
  init    - Initialize SESSION_STATE.md for a conversation
  update  - Update a field in SESSION_STATE.md
  check   - Display current SESSION_STATE.md

Usage:
  python3 session_state_manager.py init --convo-id con_XXX [--type build|research|discussion|planning]
  python3 session_state_manager.py update --convo-id con_XXX --field status --value active
  python3 session_state_manager.py check --convo-id con_XXX
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime, timezone
import re


class SessionStateManager:
    """Manage SESSION_STATE.md files for conversations."""
    
    WORKSPACE_BASE = Path("/home/.z/workspaces")
    
    # Auto-classification keywords
    CLASSIFICATION_KEYWORDS = {
        "build": ["implement", "code", "script", "create", "develop", "build", "fix", "refactor"],
        "research": ["research", "analyze", "learn", "study", "investigate", "explore", "find"],
        "discussion": ["discuss", "think", "brainstorm", "consider", "talk", "conversation"],
        "planning": ["plan", "strategy", "decide", "organize", "roadmap", "design", "architect"]
    }
    
    def __init__(self, convo_id: str):
        self.convo_id = convo_id
        self.workspace_path = self.WORKSPACE_BASE / convo_id
        self.session_state_path = self.workspace_path / "SESSION_STATE.md"
    
    def init(self, conv_type: str = None, mode: str = None, user_message: str = None) -> bool:
        """
        Initialize SESSION_STATE.md for the conversation.
        
        Args:
            conv_type: Type of conversation (build|research|discussion|planning). Auto-detected if None.
            mode: Specific mode within the type
            user_message: First user message for auto-classification
            
        Returns:
            bool: True if successful
        """
        # Auto-classify if no type provided
        if not conv_type and user_message:
            conv_type = self._classify_conversation(user_message)
        elif not conv_type:
            conv_type = "discussion"  # Default
        
        # Ensure workspace exists
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        
        # Generate template based on type
        template = self._get_template(conv_type, mode)
        
        # Write SESSION_STATE.md
        self.session_state_path.write_text(template)
        
        print(f"✓ Initialized SESSION_STATE.md for {self.convo_id}")
        print(f"  Type: {conv_type}")
        print(f"  Path: {self.session_state_path}")
        
        # Auto-sync to conversations.db
        self._sync_to_db()
        
        return True
    
    def update(self, field: str, value: str) -> bool:
        """
        Update a field in SESSION_STATE.md.
        
        Args:
            field: Field name to update (status, focus, progress, etc.)
            value: New value for the field
            
        Returns:
            bool: True if successful
        """
        if not self.session_state_path.exists():
            print(f"✗ SESSION_STATE.md not found for {self.convo_id}", file=sys.stderr)
            return False
        
        content = self.session_state_path.read_text()
        
        # Update YAML frontmatter if applicable
        frontmatter_fields = ['status', 'type', 'mode']
        if field.lower() in frontmatter_fields:
            # Update in frontmatter
            pattern_yaml = rf"^({field.lower()}:\s*)([^\n]+)"
            content = re.sub(pattern_yaml, rf"\g<1>{value}", content, flags=re.MULTILINE)
        
        # Update the field in markdown section using regex
        # Pattern: - **FieldName:** current_value
        pattern = rf"(- \*\*{field.capitalize()}:\*\*\s+)([^\n]+)"
        
        if re.search(pattern, content, re.IGNORECASE):
            content = re.sub(pattern, rf"\1{value}", content, flags=re.IGNORECASE)
        else:
            # Field not found, add it to Metadata section
            metadata_marker = "## Metadata"
            if metadata_marker in content:
                insert_pos = content.find(metadata_marker) + len(metadata_marker)
                content = content[:insert_pos] + f"\n- **{field.capitalize()}:** {value}" + content[insert_pos:]
            else:
                print(f"✗ Could not find field '{field}' or Metadata section", file=sys.stderr)
                return False
        
        # Update last_updated timestamp
        now = datetime.now(timezone.utc).isoformat()
        content = re.sub(
            r"(last_updated:\s*)([^\n]+)",
            rf"\g<1>{now}",
            content
        )
        
        self.session_state_path.write_text(content)
        print(f"✓ Updated {field} = {value}")
        
        # Auto-sync to conversations.db
        self._sync_to_db()
        
        return True
    
    def check(self) -> str:
        """
        Display current SESSION_STATE.md content.
        
        Returns:
            str: Content of SESSION_STATE.md or error message
        """
        if not self.session_state_path.exists():
            msg = f"✗ SESSION_STATE.md not found for {self.convo_id}"
            print(msg, file=sys.stderr)
            return msg
        
        content = self.session_state_path.read_text()
        print(content)
        return content
    
    def get_field(self, field: str) -> str:
        """
        Get a single field value from SESSION_STATE.md.
        
        Args:
            field: Field name (case-insensitive)
            
        Returns:
            str: Field value or "Not specified" if not found
        """
        if not self.session_state_path.exists():
            return "Not specified"
        
        content = self.session_state_path.read_text()
        
        # Try markdown format: - **FieldName:** value
        pattern = rf"- \*\*{re.escape(field)}:\*\*\s+(.+?)(?:\n|$)"
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            return self._clean_field_value(value)
        
        # Try YAML frontmatter: field: value
        pattern_yaml = rf"^{re.escape(field.lower())}:\s*(.+?)$"
        match = re.search(pattern_yaml, content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        
        return "Not specified"
    
    def get_metadata(self) -> dict:
        """
        Get all metadata fields from SESSION_STATE.md.
        
        Returns:
            dict: Metadata fields (focus, objective, status, type, mode)
        """
        if not self.session_state_path.exists():
            return {}
        
        metadata = {
            "focus": self.get_field("Focus"),
            "objective": self._get_objective(),
            "status": self.get_field("Status"),
            "type": self.get_field("Type"),
            "mode": self.get_field("Mode"),
        }
        
        return metadata
    
    def get_section(self, section_name: str) -> str:
        """
        Extract an entire markdown section from SESSION_STATE.md.
        
        Args:
            section_name: Section header (without ##)
            
        Returns:
            str: Section content (excluding header) or empty string if not found
        """
        if not self.session_state_path.exists():
            return ""
        
        content = self.session_state_path.read_text()
        lines = content.split("\n")
        in_section = False
        section_lines = []
        
        for line in lines:
            if line.strip().startswith(f"## {section_name}"):
                in_section = True
                continue
            elif in_section:
                if line.strip().startswith("##"):  # Next section
                    break
                section_lines.append(line)
        
        return "\n".join(section_lines).strip()
    
    def append_to_section(self, section_name: str, content_to_add: str) -> bool:
        """
        Append content to a markdown section in SESSION_STATE.md.
        Creates section if it doesn't exist.
        
        Args:
            section_name: Section header (without ##)
            content_to_add: Content to append (should include leading newline if needed)
            
        Returns:
            bool: True if successful
        """
        if not self.session_state_path.exists():
            print(f"✗ SESSION_STATE.md not found for {self.convo_id}", file=sys.stderr)
            return False
        
        content = self.session_state_path.read_text()
        
        if f"## {section_name}" in content:
            # Find the section and insert after header
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if line.strip() == f"## {section_name}":
                    # Insert after header (skip blank line if present)
                    insert_pos = i + 1
                    if insert_pos < len(lines) and lines[insert_pos].strip() == "":
                        insert_pos += 1
                    lines.insert(insert_pos, content_to_add)
                    break
            content = "\n".join(lines)
        else:
            # Add new section at end
            content += f"\n\n## {section_name}\n\n{content_to_add}\n"
        
        # Update last_updated timestamp
        now = datetime.now(timezone.utc).isoformat()
        content = re.sub(
            r"(last_updated:\s*)([^\n]+)",
            rf"\g<1>{now}",
            content
        )
        
        self.session_state_path.write_text(content)
        print(f"✓ Appended to section '{section_name}'")
        
        # Auto-sync to conversations.db
        self._sync_to_db()
        
        return True
    
    def _get_objective(self) -> str:
        """
        Get objective with Goal field fallback (matches spawn_worker logic).
        
        Returns:
            str: Objective value
        """
        if not self.session_state_path.exists():
            return "Not specified"
        
        content = self.session_state_path.read_text()
        
        # Try Goal field first (inside Objective section)
        pattern = r"^(?:\*\*\s*)?Goal:(?:\s*\*\*)?\s*(.+?)$"
        match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
        if match:
            value = self._clean_field_value(match.group(1))
            # Skip placeholders
            if value and not (value.startswith("What") and "?" in value):
                return value
        
        # Fallback to Objective field
        return self.get_field("Objective")
    
    def _clean_field_value(self, value: str) -> str:
        """
        Clean field value by removing markdown artifacts.
        
        Args:
            value: Raw field value
            
        Returns:
            str: Cleaned value
        """
        value = value.strip()
        # Remove leading/trailing asterisks
        value = re.sub(r"^\*+\s*", "", value)
        value = re.sub(r"\s*\*+$", "", value)
        return value.strip()
    
    def _sync_to_db(self):
        """Sync this conversation to conversations.db."""
        try:
            from conversation_sync import ConversationSync
            syncer = ConversationSync()
            syncer.sync_conversation(self.convo_id)
            syncer.close()
        except Exception as e:
            # Non-fatal - log but don't fail
            print(f"  (Note: DB sync skipped: {e})", file=sys.stderr)
    
    def _classify_conversation(self, message: str) -> str:
        """
        Auto-classify conversation type based on user message keywords.
        
        Args:
            message: User's first message
            
        Returns:
            str: Conversation type (build|research|discussion|planning)
        """
        message_lower = message.lower()
        scores = {conv_type: 0 for conv_type in self.CLASSIFICATION_KEYWORDS}
        
        for conv_type, keywords in self.CLASSIFICATION_KEYWORDS.items():
            for keyword in keywords:
                if keyword in message_lower:
                    scores[conv_type] += 1
        
        # Return type with highest score, or "discussion" if tie
        max_score = max(scores.values())
        if max_score == 0:
            return "discussion"
        
        return max(scores, key=scores.get)
    
    def _get_template(self, conv_type: str, mode: str = None) -> str:
        """
        Get SESSION_STATE template for conversation type.
        
        Args:
            conv_type: Type of conversation
            mode: Specific mode (optional)
            
        Returns:
            str: Formatted template
        """
        now = datetime.now(timezone.utc).isoformat()
        
        base_template = f"""---
conversation_id: {self.convo_id}
type: {conv_type}
mode: {mode or 'general'}
status: active
created: {now}
last_updated: {now}
---

# SESSION STATE

## Metadata
- **Type:** {conv_type.capitalize()}
- **Mode:** {mode or 'general'}
- **Focus:** TBD
- **Objective:** TBD
- **Status:** active

## Progress
- **Overall:** 0%
- **Current Phase:** initialization
- **Next Actions:** TBD

## Covered
- Session initialized

## Topics
- TBD

## Key Insights
- TBD

## Decisions Made
- TBD

## Open Questions
- TBD

## Artifacts
*Files created during this conversation*
- SESSION_STATE.md (permanent, conversation workspace)

## Tags
#{conv_type} #initialization
"""
        
        # Add type-specific sections
        if conv_type == "build":
            base_template += """
## Build-Specific

### Architectural Decisions
- TBD

### Files Modified
- TBD

### Tests
- [ ] Unit tests written
- [ ] Tests passing
- [ ] Edge cases covered

### Quality Checks
- [ ] Error handling implemented
- [ ] Documentation complete
- [ ] No false completion (P15)
"""
        elif conv_type == "research":
            base_template += """
## Research-Specific

### Research Questions
- TBD

### Sources Consulted
- TBD

### Findings
- TBD

### Knowledge Gaps
- TBD
"""
        
        return base_template


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="SESSION_STATE Manager - Manage conversation state files"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize SESSION_STATE.md")
    init_parser.add_argument("--convo-id", required=True, help="Conversation ID (con_XXX)")
    init_parser.add_argument("--type", choices=["build", "research", "discussion", "planning"], 
                            help="Conversation type (auto-detected if omitted)")
    init_parser.add_argument("--mode", help="Specific mode within type")
    init_parser.add_argument("--message", help="User message for auto-classification")
    
    # Update command
    update_parser = subparsers.add_parser("update", help="Update a field")
    update_parser.add_argument("--convo-id", required=True, help="Conversation ID (con_XXX)")
    update_parser.add_argument("--field", required=True, help="Field to update")
    update_parser.add_argument("--value", required=True, help="New value")
    
    # Check command
    check_parser = subparsers.add_parser("check", help="Display SESSION_STATE.md")
    check_parser.add_argument("--convo-id", required=True, help="Conversation ID (con_XXX)")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    manager = SessionStateManager(args.convo_id)
    
    if args.command == "init":
        success = manager.init(args.type, args.mode, args.message)
        sys.exit(0 if success else 1)
    
    elif args.command == "update":
        success = manager.update(args.field, args.value)
        sys.exit(0 if success else 1)
    
    elif args.command == "check":
        manager.check()
        sys.exit(0)


if __name__ == "__main__":
    main()





