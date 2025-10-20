#!/usr/bin/env python3
"""
Style Guide Manager
Manages style guides for consistent output generation and validation.
"""
import argparse
import json
import logging
from pathlib import Path
from datetime import datetime, UTC
from typing import Dict, List, Optional, Any
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# Paths
WORKSPACE = Path("/home/workspace")
STYLE_GUIDES_DIR = WORKSPACE / "N5" / "style_guides"
EXEMPLARS_DIR = WORKSPACE / "N5" / "exemplars"
MAPPING_FILE = WORKSPACE / "N5" / "config" / "output_type_mapping.jsonl"

# Style guide template
STYLE_GUIDE_TEMPLATE = """---
output_type: {output_type}
version: 1.0
created: {created}
updated: {updated}
source_output: {source_output}
---

# Style Guide: {output_type_display}

## Purpose
What this output type is for

## Structure
Required sections/components in order

## Length
- Target: X words / Y paragraphs
- Maximum: Z words
- Minimum: A words

## Tone
Voice characteristics (casual, formal, warm, direct, etc.)

## Style
- Sentence structure preferences
- Paragraph length
- Formatting conventions

## Required Elements
Must-have components (checklist)
- [ ] Element 1
- [ ] Element 2

## Forbidden Elements
What to avoid explicitly
- ❌ Thing 1
- ❌ Thing 2

## Validation Criteria
Pass/fail checklist with specific thresholds
- [ ] Length within bounds
- [ ] Required elements present
- [ ] Tone consistent
- [ ] Structure followed

## Examples
Brief inline examples or references to exemplar files

## Notes
Additional context, edge cases, when to deviate
"""


class StyleGuideManager:
    """Manages style guides and output type mappings."""
    
    def __init__(self):
        self.style_guides_dir = STYLE_GUIDES_DIR
        self.exemplars_dir = EXEMPLARS_DIR
        self.mapping_file = MAPPING_FILE
        
        # Ensure directories exist
        self.style_guides_dir.mkdir(parents=True, exist_ok=True)
        self.exemplars_dir.mkdir(parents=True, exist_ok=True)
        self.mapping_file.parent.mkdir(parents=True, exist_ok=True)
        
        if not self.mapping_file.exists():
            self.mapping_file.write_text("")
    
    def load_mapping(self) -> Dict[str, Dict[str, Any]]:
        """Load output type mapping from JSONL file."""
        mapping = {}
        if not self.mapping_file.exists():
            return mapping
        
        with open(self.mapping_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    mapping[entry['output_type']] = entry
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse mapping line: {line} - {e}")
        
        return mapping
    
    def save_mapping(self, mapping: Dict[str, Dict[str, Any]]) -> None:
        """Save output type mapping to JSONL file."""
        with open(self.mapping_file, 'w') as f:
            for entry in mapping.values():
                f.write(json.dumps(entry) + '\n')
        logger.info(f"✓ Saved mapping to {self.mapping_file}")
    
    def create_style_guide(
        self,
        output_type: str,
        source_file: Optional[Path] = None,
        interactive: bool = False,
        dry_run: bool = False
    ) -> Path:
        """Create a new style guide."""
        style_guide_path = self.style_guides_dir / f"{output_type}.md"
        
        if style_guide_path.exists():
            logger.warning(f"Style guide already exists: {style_guide_path}")
            return style_guide_path
        
        # Generate style guide content
        now = datetime.now(UTC).isoformat()
        content = STYLE_GUIDE_TEMPLATE.format(
            output_type=output_type,
            output_type_display=output_type.replace('-', ' ').title(),
            created=now,
            updated=now,
            source_output=str(source_file) if source_file else "N/A"
        )
        
        if dry_run:
            logger.info(f"[DRY RUN] Would create style guide: {style_guide_path}")
            logger.info(f"[DRY RUN] Content preview:\n{content[:500]}...")
            return style_guide_path
        
        # Write style guide
        style_guide_path.write_text(content)
        logger.info(f"✓ Created style guide: {style_guide_path}")
        
        # Update mapping
        mapping = self.load_mapping()
        mapping[output_type] = {
            "output_type": output_type,
            "style_guide": str(style_guide_path.relative_to(WORKSPACE)),
            "enabled": True,
            "auto_detect_keywords": [],
            "created": now,
            "updated": now
        }
        self.save_mapping(mapping)
        
        # Create exemplar directory
        exemplar_dir = self.exemplars_dir / output_type
        exemplar_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"✓ Created exemplar directory: {exemplar_dir}")
        
        # Copy source file as first exemplar if provided
        if source_file and source_file.exists():
            timestamp = datetime.now(UTC).strftime("%Y-%m-%d-%H%M")
            exemplar_name = f"{timestamp}-original.md"
            exemplar_path = exemplar_dir / exemplar_name
            exemplar_path.write_text(source_file.read_text())
            logger.info(f"✓ Stored source as exemplar: {exemplar_path}")
        
        return style_guide_path
    
    def update_style_guide(
        self,
        output_type: str,
        updates: Dict[str, Any],
        dry_run: bool = False
    ) -> bool:
        """Update an existing style guide."""
        mapping = self.load_mapping()
        
        if output_type not in mapping:
            logger.error(f"Output type not found: {output_type}")
            return False
        
        style_guide_path = WORKSPACE / mapping[output_type]['style_guide']
        
        if not style_guide_path.exists():
            logger.error(f"Style guide file not found: {style_guide_path}")
            return False
        
        if dry_run:
            logger.info(f"[DRY RUN] Would update style guide: {style_guide_path}")
            logger.info(f"[DRY RUN] Updates: {updates}")
            return True
        
        # Update mapping metadata
        mapping[output_type]['updated'] = datetime.now(UTC).isoformat()
        for key, value in updates.items():
            if key in mapping[output_type]:
                mapping[output_type][key] = value
        
        self.save_mapping(mapping)
        logger.info(f"✓ Updated style guide mapping: {output_type}")
        
        return True
    
    def validate_output(
        self,
        output_type: str,
        content: str,
        file_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """Validate output against style guide."""
        mapping = self.load_mapping()
        
        if output_type not in mapping:
            return {
                "passed": False,
                "score": 0.0,
                "issues": [f"No style guide found for output type: {output_type}"]
            }
        
        if not mapping[output_type]['enabled']:
            return {
                "passed": True,
                "score": 1.0,
                "issues": [],
                "note": "Style guide disabled for this output type"
            }
        
        style_guide_path = WORKSPACE / mapping[output_type]['style_guide']
        
        if not style_guide_path.exists():
            return {
                "passed": False,
                "score": 0.0,
                "issues": [f"Style guide file not found: {style_guide_path}"]
            }
        
        # Basic validation (can be enhanced with more sophisticated checks)
        issues = []
        score = 1.0
        
        # Check length
        word_count = len(content.split())
        if word_count < 10:
            issues.append("Content too short (< 10 words)")
            score -= 0.3
        
        # Check structure (basic - can be enhanced)
        if not content.strip():
            issues.append("Empty content")
            score -= 1.0
        
        passed = score >= 0.7 and len(issues) == 0
        
        return {
            "passed": passed,
            "score": max(0.0, score),
            "issues": issues,
            "word_count": word_count,
            "style_guide": str(style_guide_path)
        }
    
    def list_style_guides(self) -> List[Dict[str, Any]]:
        """List all style guides."""
        mapping = self.load_mapping()
        return [
            {
                "output_type": entry['output_type'],
                "enabled": entry['enabled'],
                "created": entry['created'],
                "style_guide": entry['style_guide']
            }
            for entry in mapping.values()
        ]
    
    def show_style_guide(self, output_type: str) -> Optional[Dict[str, Any]]:
        """Show details for a specific style guide."""
        mapping = self.load_mapping()
        
        if output_type not in mapping:
            logger.error(f"Output type not found: {output_type}")
            return None
        
        entry = mapping[output_type]
        style_guide_path = WORKSPACE / entry['style_guide']
        
        if not style_guide_path.exists():
            logger.error(f"Style guide file not found: {style_guide_path}")
            return None
        
        content = style_guide_path.read_text()
        
        # Count exemplars
        exemplar_dir = self.exemplars_dir / output_type
        exemplar_count = len(list(exemplar_dir.glob("*.md"))) if exemplar_dir.exists() else 0
        
        return {
            **entry,
            "style_guide_path": str(style_guide_path),
            "exemplar_count": exemplar_count,
            "exemplar_dir": str(exemplar_dir),
            "content_preview": content[:500] + "..." if len(content) > 500 else content
        }
    
    def add_exemplar(
        self,
        output_type: str,
        content: str,
        name: Optional[str] = None,
        dry_run: bool = False
    ) -> Optional[Path]:
        """Add an exemplar for an output type."""
        mapping = self.load_mapping()
        
        if output_type not in mapping:
            logger.error(f"Output type not found: {output_type}")
            return None
        
        exemplar_dir = self.exemplars_dir / output_type
        exemplar_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now(UTC).strftime("%Y-%m-%d-%H%M")
        exemplar_name = f"{timestamp}-{name}.md" if name else f"{timestamp}.md"
        exemplar_path = exemplar_dir / exemplar_name
        
        if dry_run:
            logger.info(f"[DRY RUN] Would create exemplar: {exemplar_path}")
            return exemplar_path
        
        exemplar_path.write_text(content)
        logger.info(f"✓ Created exemplar: {exemplar_path}")
        
        return exemplar_path


def main(dry_run: bool = False) -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Manage style guides for consistent output generation"
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without executing")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new style guide")
    create_parser.add_argument("--output-type", required=True, help="Output type identifier (kebab-case)")
    create_parser.add_argument("--source-file", type=Path, help="Source file to base style guide on")
    create_parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    
    # Update command
    update_parser = subparsers.add_parser("update", help="Update existing style guide")
    update_parser.add_argument("--output-type", required=True, help="Output type identifier")
    update_parser.add_argument("--enable", action="store_true", help="Enable style guide")
    update_parser.add_argument("--disable", action="store_true", help="Disable style guide")
    
    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate output against style guide")
    validate_parser.add_argument("--output-type", required=True, help="Output type identifier")
    validate_parser.add_argument("--file", type=Path, required=True, help="File to validate")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all style guides")
    
    # Show command
    show_parser = subparsers.add_parser("show", help="Show style guide details")
    show_parser.add_argument("--output-type", required=True, help="Output type identifier")
    
    # Add exemplar command
    add_exemplar_parser = subparsers.add_parser("add-exemplar", help="Add exemplar")
    add_exemplar_parser.add_argument("--output-type", required=True, help="Output type identifier")
    add_exemplar_parser.add_argument("--file", type=Path, required=True, help="Exemplar file")
    add_exemplar_parser.add_argument("--name", help="Exemplar name (optional)")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    manager = StyleGuideManager()
    
    try:
        if args.command == "create":
            path = manager.create_style_guide(
                output_type=args.output_type,
                source_file=args.source_file,
                interactive=args.interactive,
                dry_run=args.dry_run
            )
            print(f"Style guide: {path}")
            return 0
        
        elif args.command == "update":
            updates = {}
            if args.enable:
                updates['enabled'] = True
            if args.disable:
                updates['enabled'] = False
            
            success = manager.update_style_guide(
                output_type=args.output_type,
                updates=updates,
                dry_run=args.dry_run
            )
            return 0 if success else 1
        
        elif args.command == "validate":
            if not args.file.exists():
                logger.error(f"File not found: {args.file}")
                return 1
            
            content = args.file.read_text()
            result = manager.validate_output(
                output_type=args.output_type,
                content=content,
                file_path=args.file
            )
            
            print(json.dumps(result, indent=2))
            return 0 if result['passed'] else 1
        
        elif args.command == "list":
            guides = manager.list_style_guides()
            if not guides:
                print("No style guides found")
                return 0
            
            print(f"\nStyle Guides ({len(guides)}):\n")
            for guide in guides:
                status = "✓" if guide['enabled'] else "✗"
                print(f"  {status} {guide['output_type']}")
                print(f"    Created: {guide['created']}")
                print(f"    Path: {guide['style_guide']}\n")
            
            return 0
        
        elif args.command == "show":
            details = manager.show_style_guide(args.output_type)
            if not details:
                return 1
            
            print(f"\nStyle Guide: {details['output_type']}")
            print(f"  Status: {'Enabled' if details['enabled'] else 'Disabled'}")
            print(f"  Created: {details['created']}")
            print(f"  Updated: {details.get('updated', 'N/A')}")
            print(f"  Path: {details['style_guide_path']}")
            print(f"  Exemplars: {details['exemplar_count']}")
            print(f"  Exemplar Dir: {details['exemplar_dir']}\n")
            
            return 0
        
        elif args.command == "add-exemplar":
            if not args.file.exists():
                logger.error(f"File not found: {args.file}")
                return 1
            
            content = args.file.read_text()
            path = manager.add_exemplar(
                output_type=args.output_type,
                content=content,
                name=args.name,
                dry_run=args.dry_run
            )
            
            if path:
                print(f"Exemplar: {path}")
                return 0
            return 1
        
        else:
            parser.print_help()
            return 1
    
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
