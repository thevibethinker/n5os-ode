#!/usr/bin/env python3
"""
Orchestrator Rubric Generator - Create evaluation rubrics for worker conversations

Generates structured rubrics that define success criteria, deliverables, and quality gates
for worker conversations in orchestrated builds.

Usage:
    python3 orchestrator_rubric_generator.py create --worker-id con_XXX --title "Session State Manager" --objective "Build session state tracking system"
    python3 orchestrator_rubric_generator.py update --rubric-file RUBRIC.md --field status --value COMPLETE
    python3 orchestrator_rubric_generator.py validate --rubric-file RUBRIC.md --worker-id con_XXX
"""

import argparse
import json
import logging
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

WORKSPACE_ROOT = Path("/home/.z/workspaces")
BUILD_ROOT = Path("/home/workspace/N5/builds")
TEMPLATE_PATH = Path("/home/workspace/N5/builds/orchestrator-enhancements-v1/templates/WORKER_RUBRIC_TEMPLATE.md")


class RubricGenerator:
    def __init__(self, orchestrator_id: Optional[str] = None, dry_run: bool = False):
        self.orchestrator_id = orchestrator_id or self._detect_orchestrator()
        self.dry_run = dry_run
        
    def _detect_orchestrator(self) -> str:
        """Attempt to detect orchestrator conversation ID from environment"""
        import os
        conv_id = os.getenv("CONVERSATION_ID", "con_UNKNOWN")
        return conv_id
    
    def create(
        self,
        worker_id: str,
        title: str,
        objective: str,
        deliverables: Optional[List[Dict[str, str]]] = None,
        behaviors: Optional[List[str]] = None,
        integrations: Optional[List[str]] = None,
        success_criteria: Optional[List[str]] = None,
        test_commands: Optional[List[str]] = None,
        output_path: Optional[Path] = None
    ) -> Path:
        """
        Create a rubric for a worker conversation
        
        Args:
            worker_id: Worker conversation ID (con_XXX)
            title: Short title for the work
            objective: High-level objective description
            deliverables: List of {"path": str, "description": str}
            behaviors: List of expected behaviors
            integrations: List of integration requirements
            success_criteria: List of success criteria
            test_commands: List of test commands to validate
            output_path: Where to write rubric (defaults to worker workspace)
        
        Returns:
            Path to generated rubric file
        """
        if not TEMPLATE_PATH.exists():
            logger.error(f"Template not found: {TEMPLATE_PATH}")
            sys.exit(1)
        
        template = TEMPLATE_PATH.read_text()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        deliverables = deliverables or []
        behaviors = behaviors or ["Script executes without error"]
        integrations = integrations or ["No external integrations required"]
        success_criteria = success_criteria or ["All deliverables complete", "All tests pass"]
        test_commands = test_commands or []
        
        worker_num = worker_id.split("_")[-1][:3] if "_" in worker_id else "1"
        
        rubric_content = template.replace("{{N}}", worker_num)
        rubric_content = rubric_content.replace("{{Title}}", title)
        rubric_content = rubric_content.replace("{{orchestrator_id}}", self.orchestrator_id)
        rubric_content = rubric_content.replace("{{worker_id}}", worker_id)
        rubric_content = rubric_content.replace("{{timestamp}}", timestamp)
        rubric_content = rubric_content.replace("{{objective}}", objective)
        
        deliverable_lines = []
        for i, d in enumerate(deliverables, 1):
            path = d.get("path", f"file_{i}.py")
            desc = d.get("description", "No description")
            deliverable_lines.append(f"- `{path}` - {desc}")
        
        if deliverable_lines:
            rubric_content = rubric_content.replace(
                "-  - {{description_1}}\n-  - {{description_2}}",
                "\n".join(deliverable_lines)
            )
        
        behavior_lines = []
        for b in behaviors:
            if "Script executes without error" not in b:
                behavior_lines.append(f"- {b}")
        
        if behavior_lines:
            rubric_content = rubric_content.replace(
                "- {{specific_behavior_1}}\n- {{specific_behavior_2}}",
                "\n".join(behavior_lines)
            )
        else:
            rubric_content = rubric_content.replace(
                "- {{specific_behavior_1}}\n- {{specific_behavior_2}}",
                ""
            )
        
        integration_lines = [f"- {i}" for i in integrations]
        rubric_content = rubric_content.replace(
            "- {{integration_req_1}}\n- {{integration_req_2}}",
            "\n".join(integration_lines)
        )
        
        test_section = "\n".join([f"```bash\n{cmd}\n```" for cmd in test_commands]) if test_commands else "No automated tests defined"
        rubric_content = rubric_content.replace("## Test Commands\n\n", f"## Test Commands\n\n{test_section}\n\n")
        
        criteria_lines = "\n".join([f"- {c}" for c in success_criteria])
        rubric_content = rubric_content.replace(
            "{{criteria_1}}\n{{criteria_2}}",
            criteria_lines
        )
        
        if output_path is None:
            worker_workspace = WORKSPACE_ROOT / worker_id
            if not worker_workspace.exists():
                logger.warning(f"Worker workspace not found: {worker_workspace}")
                output_path = Path(f"./{worker_id}_RUBRIC.md")
            else:
                output_path = worker_workspace / "RUBRIC.md"
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would write rubric to: {output_path}")
            print(rubric_content)
            return output_path
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rubric_content)
        logger.info(f"Created rubric: {output_path}")
        
        return output_path
    
    def update(self, rubric_file: Path, field: str, value: str) -> bool:
        """
        Update a field in an existing rubric
        
        Args:
            rubric_file: Path to rubric markdown file
            field: Field to update (status, objective, etc.)
            value: New value
        
        Returns:
            True if successful
        """
        if not rubric_file.exists():
            logger.error(f"Rubric file not found: {rubric_file}")
            return False
        
        content = rubric_file.read_text()
        
        if field == "status":
            pattern = r"\*\*Status:\*\* \w+"
            if re.search(pattern, content):
                content = re.sub(pattern, f"**Status:** {value}", content)
            else:
                content = content.rstrip() + f"\n\n**Status:** {value}\n"
        
        elif field.startswith("quality_gate_"):
            gate_text = field.replace("quality_gate_", "").replace("_", " ")
            pattern = rf"- \[ \] {re.escape(gate_text)}"
            if value.lower() in ["true", "complete", "done", "yes"]:
                content = re.sub(pattern, f"- [x] {gate_text}", content)
        
        else:
            logger.warning(f"Unknown field: {field}")
            return False
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would update {rubric_file}")
            print(content)
            return True
        
        rubric_file.write_text(content)
        logger.info(f"Updated rubric: {rubric_file}")
        return True
    
    def validate(self, rubric_file: Path, worker_id: str) -> Dict[str, any]:
        """
        Validate a worker's completion against their rubric
        
        Args:
            rubric_file: Path to rubric markdown file
            worker_id: Worker conversation ID
        
        Returns:
            Dict with validation results
        """
        if not rubric_file.exists():
            logger.error(f"Rubric file not found: {rubric_file}")
            return {"valid": False, "error": "Rubric not found"}
        
        content = rubric_file.read_text()
        
        results = {
            "rubric_file": str(rubric_file),
            "worker_id": worker_id,
            "timestamp": datetime.now().isoformat(),
            "quality_gates": {},
            "status": "UNKNOWN",
            "valid": False
        }
        
        status_match = re.search(r"\*\*Status:\*\* (\w+)", content)
        if status_match:
            results["status"] = status_match.group(1)
        
        gate_pattern = r"- \[([ x])\] (.+)"
        gates = re.findall(gate_pattern, content)
        
        for checked, gate_text in gates:
            is_complete = checked.lower() == "x"
            results["quality_gates"][gate_text] = is_complete
        
        total_gates = len(results["quality_gates"])
        passed_gates = sum(1 for v in results["quality_gates"].values() if v)
        
        results["gates_passed"] = passed_gates
        results["gates_total"] = total_gates
        results["valid"] = (passed_gates == total_gates) and results["status"] == "COMPLETE"
        
        return results
    
    def list_rubrics(self, build_path: Optional[Path] = None) -> List[Dict[str, str]]:
        """
        List all rubrics in a build or across all worker workspaces
        
        Args:
            build_path: Optional path to specific build directory
        
        Returns:
            List of rubric metadata
        """
        rubrics = []
        
        if build_path and build_path.exists():
            for rubric_file in build_path.rglob("RUBRIC.md"):
                rubrics.append(self._extract_metadata(rubric_file))
        else:
            for workspace in WORKSPACE_ROOT.iterdir():
                if workspace.is_dir() and workspace.name.startswith("con_"):
                    rubric_file = workspace / "RUBRIC.md"
                    if rubric_file.exists():
                        rubrics.append(self._extract_metadata(rubric_file))
        
        return rubrics
    
    def _extract_metadata(self, rubric_file: Path) -> Dict[str, str]:
        """Extract key metadata from a rubric file"""
        content = rubric_file.read_text()
        
        metadata = {
            "path": str(rubric_file),
            "worker_id": "UNKNOWN",
            "title": "UNKNOWN",
            "status": "UNKNOWN"
        }
        
        worker_match = re.search(r"\*\*Worker:\*\* (con_\w+)", content)
        if worker_match:
            metadata["worker_id"] = worker_match.group(1)
        
        title_match = re.search(r"# Worker \d+ Rubric - (.+)", content)
        if title_match:
            metadata["title"] = title_match.group(1).strip()
        
        status_match = re.search(r"\*\*Status:\*\* (\w+)", content)
        if status_match:
            metadata["status"] = status_match.group(1)
        
        return metadata


def main():
    parser = argparse.ArgumentParser(description="Generate and manage orchestrator rubrics")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without writing")
    parser.add_argument("--orchestrator-id", help="Orchestrator conversation ID")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    create_parser = subparsers.add_parser("create", help="Create a new rubric")
    create_parser.add_argument("--worker-id", required=True, help="Worker conversation ID")
    create_parser.add_argument("--title", required=True, help="Short title for the work")
    create_parser.add_argument("--objective", required=True, help="High-level objective")
    create_parser.add_argument("--deliverables", help="JSON string of deliverables")
    create_parser.add_argument("--behaviors", help="JSON array of expected behaviors")
    create_parser.add_argument("--integrations", help="JSON array of integration requirements")
    create_parser.add_argument("--success-criteria", help="JSON array of success criteria")
    create_parser.add_argument("--test-commands", help="JSON array of test commands")
    create_parser.add_argument("--output", help="Output path for rubric")
    
    update_parser = subparsers.add_parser("update", help="Update an existing rubric")
    update_parser.add_argument("--rubric-file", required=True, help="Path to rubric file")
    update_parser.add_argument("--field", required=True, help="Field to update")
    update_parser.add_argument("--value", required=True, help="New value")
    
    validate_parser = subparsers.add_parser("validate", help="Validate worker against rubric")
    validate_parser.add_argument("--rubric-file", required=True, help="Path to rubric file")
    validate_parser.add_argument("--worker-id", required=True, help="Worker conversation ID")
    
    list_parser = subparsers.add_parser("list", help="List all rubrics")
    list_parser.add_argument("--build-path", help="Path to specific build directory")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    generator = RubricGenerator(orchestrator_id=args.orchestrator_id, dry_run=args.dry_run)
    
    if args.command == "create":
        deliverables = json.loads(args.deliverables) if args.deliverables else None
        behaviors = json.loads(args.behaviors) if args.behaviors else None
        integrations = json.loads(args.integrations) if args.integrations else None
        success_criteria = json.loads(args.success_criteria) if args.success_criteria else None
        test_commands = json.loads(args.test_commands) if args.test_commands else None
        output = Path(args.output) if args.output else None
        
        rubric_path = generator.create(
            worker_id=args.worker_id,
            title=args.title,
            objective=args.objective,
            deliverables=deliverables,
            behaviors=behaviors,
            integrations=integrations,
            success_criteria=success_criteria,
            test_commands=test_commands,
            output_path=output
        )
        
        print(f"Created: {rubric_path}")
    
    elif args.command == "update":
        success = generator.update(
            rubric_file=Path(args.rubric_file),
            field=args.field,
            value=args.value
        )
        sys.exit(0 if success else 1)
    
    elif args.command == "validate":
        result = generator.validate(
            rubric_file=Path(args.rubric_file),
            worker_id=args.worker_id
        )
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["valid"] else 1)
    
    elif args.command == "list":
        build_path = Path(args.build_path) if args.build_path else None
        rubrics = generator.list_rubrics(build_path=build_path)
        
        if not rubrics:
            logger.info("No rubrics found")
            sys.exit(0)
        
        for rubric in rubrics:
            print(f"{rubric['worker_id']}: {rubric['title']} [{rubric['status']}]")
            print(f"  {rubric['path']}")


if __name__ == "__main__":
    main()
