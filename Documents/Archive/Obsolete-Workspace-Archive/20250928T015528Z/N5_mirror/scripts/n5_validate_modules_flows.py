#!/usr/bin/env python3
"""
N5 OS Modules and Flows Validator

Validates module and flow specifications:
- No cycles in flows
- Version compatibility
- Module atomicity
- Flow chaining rules
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Optional
import argparse

class N5Validator:
    def __init__(self, n5_root: str):
        self.n5_root = Path(n5_root)
        self.modules_dir = self.n5_root / "modules"
        self.flows_dir = self.n5_root / "flows"
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def load_module_specs(self) -> Dict[str, Dict]:
        """Load all module specifications."""
        modules = {}
        if not self.modules_dir.exists():
            return modules

        for md_file in self.modules_dir.glob("*.md"):
            module_name = md_file.stem
            try:
                content = md_file.read_text()
                version = self.extract_version(content)
                modules[module_name] = {
                    "version": version,
                    "path": str(md_file),
                    "content": content
                }
            except Exception as e:
                self.errors.append(f"Failed to load module {module_name}: {e}")

        return modules

    def load_flow_specs(self) -> Dict[str, Dict]:
        """Load all flow specifications."""
        flows = {}
        if not self.flows_dir.exists():
            return flows

        for md_file in self.flows_dir.glob("*.md"):
            flow_name = md_file.stem
            try:
                content = md_file.read_text()
                steps = self.extract_steps(content)
                flows[flow_name] = {
                    "steps": steps,
                    "path": str(md_file),
                    "content": content
                }
            except Exception as e:
                self.errors.append(f"Failed to load flow {flow_name}: {e}")

        return flows

    def extract_version(self, content: str) -> str:
        """Extract version from markdown content."""
        match = re.search(r'^## Version\s*\n(\S+)', content, re.MULTILINE)
        return match.group(1) if match else "0.0.0"

    def extract_steps(self, content: str) -> List[str]:
        """Extract module steps from flow content."""
        steps = []
        # Look for lines like **module-name**: description
        for line in content.split('\n'):
            stripped = line.strip()
            if '**' in stripped and '**: ' in stripped:
                # Extract between ** and **:
                start = stripped.find('**') + 2
                end = stripped.find('**:')
                if start < end:
                    module_name = stripped[start:end].strip()
                    steps.append(module_name)
        return steps

    def validate_no_cycles(self, flows: Dict[str, Dict]) -> None:
        """Check for cycles in flow dependencies."""
        for flow_name, flow_data in flows.items():
            steps = flow_data["steps"]
            # Simple cycle detection: if a module appears more than once
            seen = set()
            for step in steps:
                if step in seen:
                    self.errors.append(f"Cycle detected in flow {flow_name}: {step} appears multiple times")
                seen.add(step)

            # More complex cycles would require dependency graphs, but for now simple check

    def validate_version_compatibility(self, modules: Dict[str, Dict], flows: Dict[str, Dict]) -> None:
        """Check version compatibility between modules in flows."""
        for flow_name, flow_data in flows.items():
            steps = flow_data["steps"]
            for step in steps:
                if step not in modules:
                    self.errors.append(f"Flow {flow_name} references unknown module {step}")
                else:
                    # Simple version check: ensure major version is 0 (pre-1.0)
                    version = modules[step]["version"]
                    if not version.startswith("0."):
                        self.warnings.append(f"Module {step} version {version} may not be compatible with flow {flow_name}")

    def validate_module_atomicity(self, modules: Dict[str, Dict]) -> None:
        """Validate that modules are atomic (basic check)."""
        for module_name, module_data in modules.items():
            content = module_data["content"]
            # Check if content mentions "composite" or similar non-atomic terms
            if re.search(r'\b(composite|workflow|flow)\b', content, re.IGNORECASE):
                self.warnings.append(f"Module {module_name} may not be atomic (mentions composite/workflow)")

    def validate_flow_chaining(self, flows: Dict[str, Dict]) -> None:
        """Validate that flows properly chain modules."""
        for flow_name, flow_data in flows.items():
            steps = flow_data["steps"]
            if len(steps) < 2:
                self.warnings.append(f"Flow {flow_name} has only {len(steps)} steps, may not be a proper chain")

    def run_validation(self) -> bool:
        """Run all validations."""
        modules = self.load_module_specs()
        flows = self.load_flow_specs()

        self.validate_no_cycles(flows)
        self.validate_version_compatibility(modules, flows)
        self.validate_module_atomicity(modules)
        self.validate_flow_chaining(flows)

        return len(self.errors) == 0

    def report(self) -> None:
        """Print validation report."""
        if self.errors:
            print("❌ VALIDATION ERRORS:")
            for error in self.errors:
                print(f"  - {error}")
        else:
            print("✅ No validation errors found.")

        if self.warnings:
            print("\n⚠️  VALIDATION WARNINGS:")
            for warning in self.warnings:
                print(f"  - {warning}")

def main():
    parser = argparse.ArgumentParser(description="Validate N5 OS modules and flows")
    parser.add_argument("--n5-root", default="/home/workspace/N5", help="N5 root directory")
    args = parser.parse_args()

    validator = N5Validator(args.n5_root)
    success = validator.run_validation()
    validator.report()

    return 0 if success else 1

if __name__ == "__main__":
    exit(main())