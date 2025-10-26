#!/usr/bin/env python3
"""
Closure Tracker - Manages conversation closure history and delta detection.

Tracks when endConversation is triggered to enable delta-only processing
on subsequent closures within the same conversation.
"""

import argparse
import json
import logging
import re
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

try:
    import jsonschema
    from jsonschema import validate, ValidationError
    HAVE_JSONSCHEMA = True
except ImportError:
    HAVE_JSONSCHEMA = False
    logger.warning("jsonschema not installed, schema validation disabled")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)


class ClosureTracker:
    """Manages closure history for a conversation."""
    
    def __init__(self, convo_workspace: Path):
        self.workspace = convo_workspace
        self.manifest_path = self.workspace / "CLOSURE_MANIFEST.jsonl"
        self.session_state_path = self.workspace / "SESSION_STATE.md"
        self.schema_path = Path("/home/workspace/N5/schemas/closure-manifest.schema.json")
        self.schema = self.load_schema()
    
    def load_schema(self) -> Optional[Dict[str, Any]]:
        """Load and return closure manifest schema."""
        if not HAVE_JSONSCHEMA:
            return None
        
        if not self.schema_path.exists():
            logger.warning(f"Schema not found: {self.schema_path}")
            return None
        
        try:
            with open(self.schema_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load schema: {e}")
            return None
    
    def validate_record(self, record: Dict[str, Any]) -> bool:
        """
        Validate closure record against schema.
        
        Returns:
            True if valid or validation unavailable, False if invalid
        """
        if not HAVE_JSONSCHEMA or not self.schema:
            return True  # Skip validation if unavailable
        
        try:
            validate(instance=record, schema=self.schema)
            return True
        except ValidationError as e:
            logger.error(f"Schema validation failed: {e.message}")
            return False
    
    def repair_corrupted_manifest(self) -> int:
        """
        Repair corrupted CLOSURE_MANIFEST.jsonl by removing invalid entries.
        
        Returns:
            Number of entries removed
        """
        if not self.manifest_path.exists():
            return 0
        
        backup_path = self.manifest_path.with_suffix('.jsonl.backup')
        self.manifest_path.rename(backup_path)
        logger.info(f"✓ Backed up manifest to {backup_path.name}")
        
        valid_records = []
        invalid_count = 0
        
        with open(backup_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                if not line.strip():
                    continue
                
                try:
                    record = json.loads(line)
                    
                    # Basic validation
                    required = ['closure_num', 'timestamp', 'event_range', 'archive_path']
                    if all(k in record for k in required):
                        if self.validate_record(record):
                            valid_records.append(record)
                        else:
                            logger.warning(f"Line {line_num}: Failed schema validation")
                            invalid_count += 1
                    else:
                        missing = [k for k in required if k not in record]
                        logger.warning(f"Line {line_num}: Missing required fields: {missing}")
                        invalid_count += 1
                
                except json.JSONDecodeError as e:
                    logger.warning(f"Line {line_num}: Invalid JSON: {e}")
                    invalid_count += 1
        
        # Write valid records back
        with open(self.manifest_path, 'w') as f:
            for record in valid_records:
                f.write(json.dumps(record) + '\n')
        
        logger.info(f"✓ Repaired manifest: {len(valid_records)} valid, {invalid_count} removed")
        return invalid_count
    
    def extract_last_user_timestamp(self, convo_workspace: Optional[Path] = None) -> Optional[str]:
        """
        Extract timestamp of last user message from conversation logs.
        
        Looks for:
        1. Zo conversation exports (conversation-*.md files)
        2. Message logs with timestamps
        3. Falls back to current time if not found
        
        Args:
            convo_workspace: Override workspace path (default: self.workspace)
        
        Returns:
            ISO 8601 timestamp string or None if not found
        """
        workspace = convo_workspace or self.workspace
        
        # Pattern 1: Look for conversation export files
        export_files = list(workspace.glob("conversation-*.md"))
        if export_files:
            # Use most recent export
            latest_export = max(export_files, key=lambda p: p.stat().st_mtime)
            logger.info(f"Found conversation export: {latest_export.name}")
            
            content = latest_export.read_text()
            
            # Parse for last user message with timestamp
            # Format: ## User (YYYY-MM-DD HH:MM:SS)
            pattern = r'## User.*?\((\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\)'
            matches = re.findall(pattern, content)
            
            if matches:
                last_timestamp_str = matches[-1]  # Last match = most recent user message
                try:
                    # Convert to ISO 8601 with timezone
                    dt = datetime.strptime(last_timestamp_str, '%Y-%m-%d %H:%M:%S')
                    # Assume ET/EST timezone (UTC-5 or UTC-4)
                    # For safety, use UTC
                    iso_ts = dt.replace(tzinfo=timezone.utc).isoformat()
                    logger.info(f"✓ Extracted timestamp: {iso_ts}")
                    return iso_ts
                except ValueError as e:
                    logger.warning(f"Failed to parse timestamp '{last_timestamp_str}': {e}")
        
        # Pattern 2: Check SESSION_STATE.md for timestamps
        if self.session_state_path.exists():
            content = self.session_state_path.read_text()
            
            # Look for ISO timestamps in state file
            iso_pattern = r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2}))'
            matches = re.findall(iso_pattern, content)
            
            if matches:
                # Use most recent timestamp found
                logger.info(f"✓ Using timestamp from SESSION_STATE.md")
                return matches[-1]
        
        logger.warning("Could not extract timestamp from conversation, falling back to current time")
        return datetime.now(timezone.utc).isoformat()
    
    def get_closure_count(self) -> int:
        """Get total number of closures recorded."""
        if not self.manifest_path.exists():
            return 0
        
        count = 0
        with open(self.manifest_path, 'r') as f:
            for line in f:
                if line.strip():
                    count += 1
        return count
    
    def get_last_closure(self) -> Optional[Dict[str, Any]]:
        """Get most recent closure record."""
        if not self.manifest_path.exists():
            return None
        
        last_record = None
        with open(self.manifest_path, 'r') as f:
            for line in f:
                if line.strip():
                    last_record = json.loads(line)
        
        return last_record
    
    def record_closure(
        self,
        timestamp: str,
        event_range: str,
        archive_path: str,
        summary: str
    ) -> Dict[str, Any]:
        """
        Record a new closure event.
        
        Args:
            timestamp: ISO timestamp of last user message before closure
            event_range: String like "1-30" or "31-45"
            archive_path: Path to closure directory (e.g., "closure-2")
            summary: Brief summary of what was done in this closure
        
        Returns:
            The closure record that was written
        """
        closure_num = self.get_closure_count() + 1
        
        record = {
            "closure_num": closure_num,
            "timestamp": timestamp,
            "event_range": event_range,
            "is_delta": closure_num > 1,
            "archive_path": archive_path,
            "summary": summary,
            "recorded_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Append to manifest
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.manifest_path, 'a') as f:
            f.write(json.dumps(record) + '\n')
        
        logger.info(f"✓ Recorded closure #{closure_num}: {event_range}")
        return record
    
    def update_session_state(self, closure_record: Dict[str, Any]) -> None:
        """Update SESSION_STATE.md with closure tracking info."""
        if not self.session_state_path.exists():
            logger.warning("SESSION_STATE.md not found, skipping update")
            return
        
        content = self.session_state_path.read_text()
        
        # Add or update closure section
        closure_section = f"""
## Closure Tracking

**Total Closures:** {closure_record['closure_num']}  
**Last Closure:** {closure_record['timestamp']}  
**Last Event Range:** {closure_record['event_range']}  
**Is Delta Mode:** {'Yes' if closure_record['is_delta'] else 'No'}
"""
        
        # Check if closure section exists
        if "## Closure Tracking" in content:
            # Replace existing section
            lines = content.split('\n')
            start_idx = None
            end_idx = None
            
            for i, line in enumerate(lines):
                if line.strip() == "## Closure Tracking":
                    start_idx = i
                elif start_idx is not None and line.startswith("## "):
                    end_idx = i
                    break
            
            if start_idx is not None:
                if end_idx is None:
                    end_idx = len(lines)
                lines[start_idx:end_idx] = closure_section.strip().split('\n')
                content = '\n'.join(lines)
        else:
            # Append new section
            content = content.rstrip() + '\n' + closure_section
        
        self.session_state_path.write_text(content)
        logger.info("✓ Updated SESSION_STATE.md with closure tracking")
    
    def get_delta_info(self) -> Dict[str, Any]:
        """
        Get information about current delta state.
        
        Returns:
            Dict with keys: is_delta, previous_closure, closure_num
        """
        last = self.get_last_closure()
        count = self.get_closure_count()
        
        return {
            "is_delta": count > 0,
            "previous_closure": last,
            "next_closure_num": count + 1
        }
    
    def generate_index_content(
        self,
        convo_id: str,
        archive_dir: Path,
        title: str = "Conversation Archive"
    ) -> str:
        """Generate INDEX.md content for archive directory."""
        if not self.manifest_path.exists():
            return f"# {title}\n\nNo closures recorded yet.\n"
        
        closures = []
        with open(self.manifest_path, 'r') as f:
            for line in f:
                if line.strip():
                    closures.append(json.loads(line))
        
        content = [
            f"# {title}",
            "",
            f"**Conversation:** {convo_id}",
            f"**Archive Created:** {closures[0]['timestamp'].split('T')[0]}",
            f"**Total Closures:** {len(closures)}",
            "",
            "## Closure History",
            ""
        ]
        
        for closure in closures:
            delta_marker = " (Delta)" if closure['is_delta'] else ""
            content.extend([
                f"### Closure {closure['closure_num']}{delta_marker}",
                f"- **Timestamp:** {closure['timestamp']}",
                f"- **Events:** {closure['event_range']}",
                f"- **Summary:** {closure['summary']}",
                f"- **Artifacts:** See `{closure['archive_path']}/README.md`",
                ""
            ])
        
        return '\n'.join(content)


def main() -> int:
    """CLI interface for closure tracker."""
    parser = argparse.ArgumentParser(description="Closure Tracker")
    parser.add_argument(
        "command",
        choices=["record", "status", "delta-info", "generate-index", "repair", "extract-timestamp"],
        help="Command to execute"
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        required=True,
        help="Conversation workspace path"
    )
    parser.add_argument("--timestamp", help="ISO timestamp for closure")
    parser.add_argument("--event-range", help="Event range (e.g., '1-30')")
    parser.add_argument("--archive-path", help="Path to closure directory")
    parser.add_argument("--summary", help="Closure summary")
    parser.add_argument("--convo-id", help="Conversation ID for index")
    parser.add_argument("--title", help="Archive title for index")
    parser.add_argument("--output", type=Path, help="Output path for index")
    
    args = parser.parse_args()
    
    tracker = ClosureTracker(args.workspace)
    
    try:
        if args.command == "record":
            if not all([args.timestamp, args.event_range, args.archive_path, args.summary]):
                logger.error("record requires: --timestamp, --event-range, --archive-path, --summary")
                return 1
            
            record = tracker.record_closure(
                args.timestamp,
                args.event_range,
                args.archive_path,
                args.summary
            )
            tracker.update_session_state(record)
            print(json.dumps(record, indent=2))
        
        elif args.command == "status":
            count = tracker.get_closure_count()
            last = tracker.get_last_closure()
            
            print(f"Total closures: {count}")
            if last:
                print(f"Last closure: {last['timestamp']}")
                print(f"Last events: {last['event_range']}")
        
        elif args.command == "delta-info":
            info = tracker.get_delta_info()
            print(json.dumps(info, indent=2))
        
        elif args.command == "generate-index":
            if not args.convo_id:
                logger.error("generate-index requires --convo-id")
                return 1
            
            content = tracker.generate_index_content(
                args.convo_id,
                args.workspace,
                args.title or "Conversation Archive"
            )
            
            if args.output:
                args.output.write_text(content)
                logger.info(f"✓ Generated index at {args.output}")
            else:
                print(content)
        
        elif args.command == "repair":
            if not tracker.manifest_path.exists():
                logger.error("No manifest file found to repair")
                return 1
            
            removed = tracker.repair_corrupted_manifest()
            print(f"Repair complete: {removed} invalid entries removed")
        
        elif args.command == "extract-timestamp":
            timestamp = tracker.extract_last_user_timestamp()
            if timestamp:
                print(timestamp)
                logger.info(f"✓ Extracted: {timestamp}")
            else:
                logger.error("Failed to extract timestamp")
                return 1
        
        return 0
    
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit(main())
