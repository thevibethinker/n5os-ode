#!/usr/bin/env python3
"""
SESSION_STATE Manager v2.1 - Manage conversation state files

Commands:
  init    - Initialize SESSION_STATE.md for a conversation
  update  - Update a field in SESSION_STATE.md
  sync    - Bulk update multiple sections from JSON (for Librarian)
  check   - Display current SESSION_STATE.md
  audit   - Check for TBD placeholders and missing content

Usage:
  python3 session_state_manager.py init --convo-id con_XXX [--type build|research|discussion|planning|action]
  python3 session_state_manager.py init --convo-id con_XXX --build my-project --worker-num 1 --parent-topic "My Project"
  python3 session_state_manager.py update --convo-id con_XXX --field status --value active
  python3 session_state_manager.py sync --convo-id con_XXX --json '{"Progress": {...}, "Covered": [...]}'
  python3 session_state_manager.py check --convo-id con_XXX
  python3 session_state_manager.py audit --convo-id con_XXX
"""

import argparse
import sys
import json as json_module
from pathlib import Path
from datetime import datetime, timezone
import re


class SessionStateManager:
    """Manage SESSION_STATE.md files for conversations."""
    
    WORKSPACE_BASE = Path("/home/.z/workspaces")
    VALID_TYPES = {"build", "research", "discussion", "planning", "debug", "onboarding"}
    TYPE_ALIASES = {
        "action": "planning",
        "strategy": "planning",
        "strategic": "planning",
        "implement": "build",
        "implementation": "build",
        "coding": "build",
        "code": "build",
        "chat": "discussion",
        "talk": "discussion",
    }
    
    # Auto-classification keywords
    CLASSIFICATION_KEYWORDS = {
        "build": ["implement", "code", "script", "create", "develop", "build", "fix", "refactor"],
        "research": ["research", "analyze", "learn", "study", "investigate", "explore", "find"],
        "discussion": ["discuss", "think", "brainstorm", "consider", "talk", "conversation"],
        "planning": ["plan", "strategy", "decide", "organize", "roadmap", "design", "architect"]
    }
    
    # Schema for SESSION_STATE sections
    SCHEMA = {
        "Metadata": {
            "fields": ["Type", "Mode", "Focus", "Objective", "Status"],
            "required": ["Focus", "Objective"]
        },
        "Progress": {
            "fields": ["Overall", "Current Phase", "Next Actions"],
            "required": ["Overall", "Current Phase"]
        },
        "Covered": {"type": "list", "required": True},
        "Topics": {"type": "list", "required": False},
        "Key Insights": {"type": "list", "required": False},
        "Decisions Made": {"type": "list", "required": False},
        "Open Questions": {"type": "list", "required": False},
        "Artifacts": {"type": "artifact_list", "required": False}
    }
    
    def __init__(self, convo_id: str):
        self.convo_id = convo_id
        self.workspace_path = self.WORKSPACE_BASE / convo_id
        self.session_state_path = self.workspace_path / "SESSION_STATE.md"
    
    def init(self, conv_type: str = None, mode: str = None, user_message: str = None,
             focus: str = None, objective: str = None,
             build_id: str = None, worker_num: int = None, parent_topic: str = None) -> bool:
        """
        Initialize SESSION_STATE.md for the conversation.
        
        New params for worker support:
          build_id: Build project slug (e.g., "deal-meeting-intel")
          worker_num: Worker number within the build
          parent_topic: Human-readable topic for greppable tags
        """
        # Parse BUILD_CONTEXT from user_message if present
        if user_message and not build_id:
            parsed = self._parse_build_context(user_message)
            if parsed:
                build_id = parsed.get("build") or parsed.get("build_id")
                worker_num = parsed.get("worker") or parsed.get("worker_num")
                parent_topic = parsed.get("parent_topic") or parsed.get("topic")
        
        conv_type = self._normalize_type(conv_type, user_message)

        # Auto-classify if no type provided
        if not conv_type and user_message:
            conv_type = self._classify_conversation(user_message)
        elif not conv_type:
            conv_type = "discussion"
        
        # Infer mode - worker if we have build context
        if build_id and worker_num:
            mode = "worker"
        elif not mode:
            mode = self._infer_mode()
        
        # Derive focus from user_message if not explicitly provided
        derived_focus = focus
        if not derived_focus and user_message:
            derived_focus = self._derive_focus(user_message)
        
        # Ensure workspace exists
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        
        now = datetime.now(timezone.utc)
        
        # Build YAML frontmatter
        frontmatter_lines = [
            "---",
            f"conversation_id: {self.convo_id}",
            f"type: {conv_type}",
            f"mode: {mode}",
            f"status: active",
            f"created: {now.isoformat()}",
            f"last_updated: {now.isoformat()}",
        ]
        
        # Add build context to frontmatter if this is a worker
        if build_id:
            frontmatter_lines.append(f"build_id: {build_id}")
            frontmatter_lines.append(f"build_slug: {build_id}")  # Alias for router detection
        if worker_num:
            frontmatter_lines.append(f"worker_num: {worker_num}")
            frontmatter_lines.append(f"worker_id: W{worker_num}")  # Formatted ID for router detection
        if parent_topic:
            frontmatter_lines.append(f"parent_topic: {parent_topic}")
        
        frontmatter_lines.append("---")
        frontmatter = "\n".join(frontmatter_lines)
        
        # Build content sections
        content_parts = [frontmatter, ""]
        
        # Add Build Context section for workers
        if build_id and worker_num:
            content_parts.extend([
                "## Build Context",
                "",
                f"- **Build:** {build_id}",
                f"- **Worker:** {worker_num}",
                f"- **Parent Topic:** {parent_topic or build_id}",
                "",
            ])
        
        content_parts.extend([
            "## Metadata",
            "",
            f"- **Type:** {conv_type.title()}",
            f"- **Mode:** {mode}",
            f"- **Focus:** {derived_focus or 'TBD'}",
            f"- **Objective:** {objective or 'TBD - Session initialized'}",
            "",
            "## Progress",
            "",
            "- **Overall:** 0%",
            "- **Current Phase:** Initialization",
            "- **Next Actions:** TBD",
            "",
            "## Covered",
            "",
            "- Session initialized",
            "",
            "## Topics",
            "- TBD",
            "",
            "## Key Insights",
            "- TBD",
            "",
            "## Decisions Made",
            "- TBD",
            "",
            "## Open Questions",
            "- TBD",
            "",
            "## Artifacts",
            "",
            "*Files created during this conversation*",
            "- SESSION_STATE.md (permanent, conversation workspace)",
            "",
            "## Tags",
            f"#{conv_type} #initialization",
            "",
            "### Quality Checks",
            "- [ ] Error handling implemented",
            "- [ ] Documentation complete",
            "- [ ] No false completion (P15)",
            "",
        ])
        
        content = "\n".join(content_parts)
        self.session_state_path.write_text(content)
        
        print(f"✓ Initialized SESSION_STATE.md for {self.convo_id}")
        print(f"  Type: {conv_type}")
        if build_id:
            print(f"  Build: {build_id} (Worker {worker_num})")
        print(f"  Focus: {derived_focus or 'TBD'}...")
        print(f"  Path: {self.session_state_path}")
        
        self._sync_to_db()
        
        return True

    def _normalize_type(self, conv_type: str | None, user_message: str | None = None) -> str | None:
        """Normalize type aliases and gracefully downgrade unknown type tokens."""
        if not conv_type:
            return None

        raw = conv_type.strip().lower()
        normalized = self.TYPE_ALIASES.get(raw, raw)
        if normalized in self.VALID_TYPES:
            return normalized

        inferred = self._classify_conversation(user_message or "")
        print(
            f"⚠ Unknown --type '{conv_type}'. Falling back to inferred type '{inferred}'.",
            file=sys.stderr,
        )
        return inferred
    
    def _parse_build_context(self, message: str) -> dict:
        """
        Parse BUILD_CONTEXT block from user message.
        
        Looks for patterns like:
          BUILD_CONTEXT:
            build: deal-meeting-intel
            worker: 1
            parent_topic: Deal Intelligence
        
        Or inline: BUILD_CONTEXT: build=X worker=Y
        """
        result = {}
        
        # Try YAML-style block
        yaml_pattern = r"BUILD_CONTEXT:\s*\n((?:\s+\w+:\s*.+\n?)+)"
        match = re.search(yaml_pattern, message, re.IGNORECASE)
        if match:
            block = match.group(1)
            for line in block.strip().split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    result[key.strip().lower().replace("-", "_")] = value.strip()
            if result:
                return result
        
        # Try inline style: BUILD_CONTEXT: build=X worker=Y
        inline_pattern = r"BUILD_CONTEXT:\s*(.+?)(?:\n|$)"
        match = re.search(inline_pattern, message, re.IGNORECASE)
        if match:
            inline = match.group(1)
            for pair in re.findall(r"(\w+)=([^\s]+)", inline):
                result[pair[0].lower()] = pair[1]
            if result:
                return result
        
        return None
    
    def _infer_mode(self) -> str:
        """
        Infer conversation mode from environmental signals.

        Priority (first match wins):
        1. build_id + worker_num in SESSION_STATE → "worker"
        2. PARENT_ID or N5_PARENT_ID env var → "worker"
        3. SESSION_STATE contains "Build Context:" → "worker"
        4. SESSION_STATE contains "Parent Conversation:" → "worker"
        5. worker_updates/ directory exists with files → "orchestrator"
        6. N5_SCHEDULED=true env var → "scheduled"
        7. Default → "standalone"

        Returns: One of: standalone, worker, orchestrator, scheduled
        """
        import os

        # Signal 1: Worker detection via environment
        parent_id = os.environ.get("PARENT_ID") or os.environ.get("N5_PARENT_ID")
        if parent_id:
            return "worker"

        # Signal 2: Worker detection via SESSION_STATE content
        if self.session_state_path.exists():
            content = self.session_state_path.read_text()
            
            # Check for build_id in frontmatter
            if re.search(r"^build_id:\s*.+$", content, re.MULTILINE):
                return "worker"
            
            # Check for Build Context section
            if "## Build Context" in content:
                return "worker"
            
            # Legacy: Parent Conversation
            if "Parent Conversation:" in content:
                return "worker"

        # Signal 3: Orchestrator detection via worker_updates/
        worker_updates_dir = self.workspace_path / "worker_updates"
        if worker_updates_dir.exists() and any(worker_updates_dir.iterdir()):
            return "orchestrator"

        # Signal 4: Scheduled detection via environment
        if os.environ.get("N5_SCHEDULED", "").lower() == "true":
            return "scheduled"

        return "standalone"
    
    def update(self, field: str, value: str) -> bool:
        """Update a single field in SESSION_STATE.md."""
        if not self.session_state_path.exists():
            print(f"✗ SESSION_STATE.md not found for {self.convo_id}", file=sys.stderr)
            return False
        
        content = self.session_state_path.read_text()
        
        # Escape special regex characters in value for safe replacement
        escaped_value = value.replace("\\", "\\\\")
        
        # Update YAML frontmatter if applicable
        frontmatter_fields = ['status', 'type', 'mode']
        if field.lower() in frontmatter_fields:
            pattern_yaml = rf"^({field.lower()}:\s*)([^\n]+)"
            content = re.sub(pattern_yaml, rf"\g<1>{escaped_value}", content, flags=re.MULTILINE)
        
        # Update the field in markdown section
        pattern = rf"(- \*\*{field}:\*\*\s+)([^\n]+)"
        
        if re.search(pattern, content, re.IGNORECASE):
            # Use a function replacement to avoid regex interpretation of value
            def replacer(m):
                return m.group(1) + value
            content = re.sub(pattern, replacer, content, flags=re.IGNORECASE)
        else:
            metadata_marker = "## Metadata"
            if metadata_marker in content:
                insert_pos = content.find(metadata_marker) + len(metadata_marker)
                content = content[:insert_pos] + f"\n- **{field}:** {value}" + content[insert_pos:]
            else:
                print(f"✗ Could not find field '{field}' or Metadata section", file=sys.stderr)
                return False
        
        content = self._update_timestamp(content)
        self.session_state_path.write_text(content)
        print(f"✓ Updated {field} = {value}")
        
        self._sync_to_db()
        return True
    
    def sync(self, updates: dict) -> dict:
        """
        Bulk update multiple sections from a JSON structure.
        Designed for Librarian to update state efficiently.
        
        Args:
            updates: Dict with section names as keys, content as values.
                     Special keys:
                     - "Metadata": {"Focus": "...", "Objective": "..."}
                     - "Progress": {"Overall": "X%", "Current Phase": "...", "Next Actions": "..."}
                     - "Covered": ["item1", "item2", ...] (list of covered items)
                     - "Topics": ["topic1", "topic2", ...]
                     - "Key Insights": ["insight1", "insight2", ...]
                     - "Decisions Made": ["decision1", ...]
                     - "Open Questions": ["question1", ...]
                     - "Artifacts": [{"name": "...", "classification": "...", "path": "..."}]
        
        Returns:
            dict: {"success": bool, "updated": [sections], "errors": [errors]}
        """
        if not self.session_state_path.exists():
            return {"success": False, "updated": [], "errors": [f"SESSION_STATE.md not found for {self.convo_id}"]}
        
        content = self.session_state_path.read_text()
        updated = []
        errors = []
        
        for section, value in updates.items():
            try:
                if section == "Metadata":
                    for field, val in value.items():
                        pattern = rf"(- \*\*{field}:\*\*\s+)([^\n]+)"
                        if re.search(pattern, content, re.IGNORECASE):
                            # Use function replacement to avoid regex interpretation
                            def make_replacer(replacement_val):
                                def replacer(m):
                                    return m.group(1) + replacement_val
                                return replacer
                            content = re.sub(pattern, make_replacer(val), content, flags=re.IGNORECASE)
                    updated.append("Metadata")
                
                elif section == "Progress":
                    for field, val in value.items():
                        pattern = rf"(- \*\*{field}:\*\*\s+)([^\n]+)"
                        if re.search(pattern, content, re.IGNORECASE):
                            # Use function replacement to avoid regex interpretation
                            def make_replacer(replacement_val):
                                def replacer(m):
                                    return m.group(1) + replacement_val
                                return replacer
                            content = re.sub(pattern, make_replacer(val), content, flags=re.IGNORECASE)
                    updated.append("Progress")
                
                elif section in ["Covered", "Topics", "Key Insights", "Decisions Made", "Open Questions"]:
                    if isinstance(value, list):
                        new_content = "\n".join(f"- {item}" for item in value)
                        content = self._replace_section_content(content, section, new_content)
                        updated.append(section)
                
                elif section == "Artifacts":
                    if isinstance(value, list):
                        lines = ["*Files created during this conversation*"]
                        for artifact in value:
                            if isinstance(artifact, dict):
                                name = artifact.get("name", "Unknown")
                                classification = artifact.get("classification", "temporary")
                                path = artifact.get("path", "")
                                lines.append(f"- {name} ({classification}, {path})")
                            else:
                                lines.append(f"- {artifact}")
                        content = self._replace_section_content(content, section, "\n".join(lines))
                        updated.append("Artifacts")
                
                else:
                    if isinstance(value, str):
                        content = self._replace_section_content(content, section, value)
                        updated.append(section)
                    elif isinstance(value, list):
                        new_content = "\n".join(f"- {item}" for item in value)
                        content = self._replace_section_content(content, section, new_content)
                        updated.append(section)
            
            except Exception as e:
                errors.append(f"{section}: {str(e)}")
        
        content = self._update_timestamp(content)
        self.session_state_path.write_text(content)
        self._sync_to_db()
        
        print(f"✓ Synced {len(updated)} sections: {', '.join(updated)}")
        if errors:
            print(f"✗ Errors: {'; '.join(errors)}", file=sys.stderr)
        
        return {"success": len(errors) == 0, "updated": updated, "errors": errors}
    
    def audit(self) -> dict:
        """
        Audit SESSION_STATE.md for TBD placeholders and missing content.
        
        Returns:
            dict: {"complete": bool, "tbd_count": int, "tbd_fields": [...], "empty_sections": [...]}
        """
        if not self.session_state_path.exists():
            return {"complete": False, "error": f"SESSION_STATE.md not found for {self.convo_id}"}
        
        content = self.session_state_path.read_text()
        
        # Find TBD placeholders
        tbd_pattern = r"- \*\*([^:]+):\*\*\s+TBD"
        tbd_matches = re.findall(tbd_pattern, content)
        
        # Also find bare "- TBD" lines
        bare_tbd = content.count("\n- TBD")
        
        # Find empty sections
        empty_sections = []
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("## ") and not line.startswith("## Build-Specific") and not line.startswith("## Research-Specific"):
                section_name = line[3:].strip()
                for j in range(i + 1, min(i + 5, len(lines))):
                    next_line = lines[j].strip()
                    if next_line and not next_line.startswith("*"):
                        if next_line.startswith("##"):
                            empty_sections.append(section_name)
                        break
        
        total_tbd = len(tbd_matches) + bare_tbd
        is_complete = total_tbd == 0 and len(empty_sections) == 0
        
        result = {
            "complete": is_complete,
            "tbd_count": total_tbd,
            "tbd_fields": tbd_matches,
            "bare_tbd_count": bare_tbd,
            "empty_sections": empty_sections
        }
        
        if is_complete:
            print("✓ SESSION_STATE is complete (no TBD placeholders)")
        else:
            print(f"⚠ SESSION_STATE has {total_tbd} TBD placeholders")
            if tbd_matches:
                print(f"  Fields with TBD: {', '.join(tbd_matches)}")
            if bare_tbd:
                print(f"  Bare '- TBD' entries: {bare_tbd}")
            if empty_sections:
                print(f"  Empty sections: {', '.join(empty_sections)}")
        
        return result
    
    def check(self) -> str:
        """Display current SESSION_STATE.md content."""
        if not self.session_state_path.exists():
            msg = f"✗ SESSION_STATE.md not found for {self.convo_id}"
            print(msg, file=sys.stderr)
            return msg
        
        content = self.session_state_path.read_text()
        print(content)
        return content
    
    def get_field(self, field: str) -> str:
        """Get a single field value from SESSION_STATE.md."""
        if not self.session_state_path.exists():
            return "Not specified"
        
        content = self.session_state_path.read_text()
        
        pattern = rf"- \*\*{re.escape(field)}:\*\*\s+(.+?)(?:\n|$)"
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            return self._clean_field_value(value)
        
        pattern_yaml = rf"^{re.escape(field.lower())}:\s*(.+?)$"
        match = re.search(pattern_yaml, content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        
        return "Not specified"
    
    def get_metadata(self) -> dict:
        """Get all metadata fields from SESSION_STATE.md."""
        if not self.session_state_path.exists():
            return {}
        
        return {
            "focus": self.get_field("Focus"),
            "objective": self._get_objective(),
            "status": self.get_field("Status"),
            "type": self.get_field("Type"),
            "mode": self.get_field("Mode"),
        }
    
    def get_section(self, section_name: str) -> str:
        """Extract an entire markdown section from SESSION_STATE.md."""
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
                if line.strip().startswith("##"):
                    break
                section_lines.append(line)
        
        return "\n".join(section_lines).strip()
    
    def append_to_section(self, section_name: str, content_to_add: str) -> bool:
        """Append content to a markdown section in SESSION_STATE.md."""
        if not self.session_state_path.exists():
            print(f"✗ SESSION_STATE.md not found for {self.convo_id}", file=sys.stderr)
            return False
        
        content = self.session_state_path.read_text()
        
        if f"## {section_name}" in content:
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if line.strip() == f"## {section_name}":
                    insert_pos = i + 1
                    if insert_pos < len(lines) and lines[insert_pos].strip() == "":
                        insert_pos += 1
                    lines.insert(insert_pos, content_to_add)
                    break
            content = "\n".join(lines)
        else:
            content += f"\n\n## {section_name}\n\n{content_to_add}\n"
        
        content = self._update_timestamp(content)
        self.session_state_path.write_text(content)
        print(f"✓ Appended to section '{section_name}'")
        
        self._sync_to_db()
        return True
    
    def _replace_section_content(self, content: str, section_name: str, new_content: str) -> str:
        """Replace the content of a section (between header and next header)."""
        lines = content.split("\n")
        result = []
        in_section = False
        section_replaced = False
        
        for line in lines:
            if line.strip() == f"## {section_name}":
                in_section = True
                result.append(line)
                result.append("")
                result.append(new_content)
                section_replaced = True
                continue
            
            if in_section:
                if line.strip().startswith("##"):
                    in_section = False
                    result.append("")
                    result.append(line)
                continue
            
            result.append(line)
        
        if not section_replaced:
            result.append("")
            result.append(f"## {section_name}")
            result.append("")
            result.append(new_content)
        
        return "\n".join(result)
    
    def _update_timestamp(self, content: str) -> str:
        """Update last_updated timestamp in content."""
        now = datetime.now(timezone.utc).isoformat()
        return re.sub(
            r"(last_updated:\s*)([^\n]+)",
            rf"\g<1>{now}",
            content
        )
    
    def _get_objective(self) -> str:
        """Get objective with Goal field fallback."""
        if not self.session_state_path.exists():
            return "Not specified"
        
        content = self.session_state_path.read_text()
        
        pattern = r"^(?:\*\*\s*)?Goal:(?:\s*\*\*)?\s*(.+?)$"
        match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
        if match:
            value = self._clean_field_value(match.group(1))
            if value and not (value.startswith("What") and "?" in value):
                return value
        
        return self.get_field("Objective")
    
    def _clean_field_value(self, value: str) -> str:
        """Clean field value by removing markdown artifacts."""
        value = value.strip()
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
            print(f"  (Note: DB sync skipped: {e})", file=sys.stderr)
    
    def _classify_conversation(self, message: str) -> str:
        """Auto-classify conversation type based on user message keywords."""
        message_lower = message.lower()
        scores = {conv_type: 0 for conv_type in self.CLASSIFICATION_KEYWORDS}
        
        for conv_type, keywords in self.CLASSIFICATION_KEYWORDS.items():
            for keyword in keywords:
                if keyword in message_lower:
                    scores[conv_type] += 1
        
        max_score = max(scores.values())
        if max_score == 0:
            return "discussion"
        
        return max(scores, key=scores.get)

    def _get_template(self, conv_type: str, mode: str = None) -> str:
        """Get SESSION_STATE template for conversation type."""
        now = datetime.now(timezone.utc).isoformat()
        # Infer mode if not explicitly provided
        effective_mode = mode or self._infer_mode()

        base_template = f"""---
conversation_id: {self.convo_id}
type: {conv_type}
mode: {effective_mode}
status: active
created: {now}
last_updated: {now}
---

# SESSION STATE

## Metadata
- **Type:** {conv_type.capitalize()}
- **Mode:** {effective_mode}
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
    
    def _derive_focus(self, user_message: str, max_length: int = 120) -> str:
        """Derive a focus statement from the user's message."""
        if not user_message:
            return ""
        
        focus = user_message.strip()
        
        prefixes_to_remove = [
            "i want to ", "i need to ", "please ", "can you ", "help me ",
            "let's ", "we need to ", "i'd like to ", "could you "
        ]
        focus_lower = focus.lower()
        for prefix in prefixes_to_remove:
            if focus_lower.startswith(prefix):
                focus = focus[len(prefix):]
                break
        
        if focus:
            focus = focus[0].upper() + focus[1:]
        
        if len(focus) > max_length:
            truncated = focus[:max_length]
            last_space = truncated.rfind(' ')
            if last_space > max_length // 2:
                focus = truncated[:last_space] + "..."
            else:
                focus = truncated + "..."
        
        return focus


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="SESSION_STATE Manager v2.0 - Manage conversation state files"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize SESSION_STATE.md")
    init_parser.add_argument("--convo-id", required=True, help="Conversation ID (con_XXX)")
    init_parser.add_argument(
        "--type",
        help=(
            "Conversation type (auto-detected if omitted). "
            "Supports aliases like 'action'->'planning'."
        ),
    )
    init_parser.add_argument("--mode", help="Specific mode within type")
    init_parser.add_argument("--message", help="User message for auto-classification")
    init_parser.add_argument("--focus", help="Explicit focus override")
    init_parser.add_argument("--objective", help="Explicit objective override")
    # Worker context args
    init_parser.add_argument("--build", dest="build_id", help="Build project slug (e.g., deal-meeting-intel)")
    init_parser.add_argument("--worker-num", type=str, help="Worker number within the build (e.g., 1, 2.1)")
    init_parser.add_argument("--parent-topic", help="Human-readable topic for greppable tags")
    
    # Update command
    update_parser = subparsers.add_parser("update", help="Update a field")
    update_parser.add_argument("--convo-id", required=True, help="Conversation ID (con_XXX)")
    update_parser.add_argument("--field", required=True, help="Field to update")
    update_parser.add_argument("--value", required=True, help="New value")
    
    # Sync command
    sync_parser = subparsers.add_parser("sync", help="Bulk update sections from JSON")
    sync_parser.add_argument("--convo-id", required=True, help="Conversation ID (con_XXX)")
    sync_parser.add_argument("--json", required=True, help="JSON string with updates")
    
    # Audit command
    audit_parser = subparsers.add_parser("audit", help="Check for TBD placeholders")
    audit_parser.add_argument("--convo-id", required=True, help="Conversation ID (con_XXX)")
    
    # Check command
    check_parser = subparsers.add_parser("check", help="Display SESSION_STATE.md")
    check_parser.add_argument("--convo-id", required=True, help="Conversation ID (con_XXX)")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    manager = SessionStateManager(args.convo_id)
    
    if args.command == "init":
        build_id = getattr(args, 'build_id', None)
        worker_num = getattr(args, 'worker_num', None)
        parent_topic = getattr(args, 'parent_topic', None)
        success = manager.init(
            args.type, args.mode, args.message, args.focus, args.objective,
            build_id=build_id, worker_num=worker_num, parent_topic=parent_topic
        )
        sys.exit(0 if success else 1)
    
    elif args.command == "update":
        success = manager.update(args.field, args.value)
        sys.exit(0 if success else 1)
    
    elif args.command == "sync":
        try:
            updates = json_module.loads(args.json)
            result = manager.sync(updates)
            sys.exit(0 if result["success"] else 1)
        except json_module.JSONDecodeError as e:
            print(f"✗ Invalid JSON: {e}", file=sys.stderr)
            sys.exit(1)
    
    elif args.command == "audit":
        result = manager.audit()
        sys.exit(0 if result.get("complete", False) else 1)
    
    elif args.command == "check":
        manager.check()
        sys.exit(0)


if __name__ == "__main__":
    main()


