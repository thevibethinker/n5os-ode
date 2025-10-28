#!/usr/bin/env python3
"""
Build Validation Module
Proactive detection of stubs, placeholders, broken references, and contract issues.

Usage:
    python3 validation.py scan /path/to/project
    python3 validation.py check-contracts /path/to/project
    python3 validation.py sweep /path/to/project --all
"""

import argparse
import ast
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Set, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)


@dataclass
class ValidationIssue:
    """Single validation issue found in code."""
    severity: str  # "error", "warning", "info"
    category: str  # "stub", "placeholder", "broken_import", "contract"
    file_path: Path
    line_number: Optional[int] = None
    message: str = ""
    context: str = ""


@dataclass
class ValidationReport:
    """Aggregated validation results."""
    project_path: Path
    issues: List[ValidationIssue] = field(default_factory=list)
    files_scanned: int = 0
    
    @property
    def errors(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == "error"]
    
    @property
    def warnings(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == "warning"]
    
    @property
    def has_critical_issues(self) -> bool:
        return len(self.errors) > 0
    
    def summary(self) -> str:
        """Generate human-readable summary."""
        lines = [
            f"Validation Report: {self.project_path}",
            f"Files scanned: {self.files_scanned}",
            f"Errors: {len(self.errors)}",
            f"Warnings: {len(self.warnings)}",
            ""
        ]
        
        if self.errors:
            lines.append("ERRORS:")
            for issue in self.errors:
                lines.append(f"  [{issue.category}] {issue.file_path.name}:{issue.line_number or '?'} - {issue.message}")
        
        if self.warnings:
            lines.append("\nWARNINGS:")
            for issue in self.warnings:
                lines.append(f"  [{issue.category}] {issue.file_path.name}:{issue.line_number or '?'} - {issue.message}")
        
        if not self.errors and not self.warnings:
            lines.append("✓ No issues found")
        
        return "\n".join(lines)


class Validator:
    """Main validation engine."""
    
    # Patterns to detect
    STUB_PATTERNS = [
        r'raise\s+NotImplementedError',
        r'def\s+\w+\([^)]*\)\s*:\s*pass\s*$',
        r'def\s+\w+\([^)]*\)\s*:\s*\.\.\.\s*$',
    ]
    
    PLACEHOLDER_PATTERNS = [
        r'TODO(?:\s*:|\s+)',
        r'FIXME(?:\s*:|\s+)',
        r'XXX(?:\s*:|\s+)',
        r'PLACEHOLDER(?:\s*:|\s+)',
        r'STUB(?:\s*:|\s+)',
        r'HACK(?:\s*:|\s+)',
    ]
    
    UNSAFE_PATTERNS = [
        r'\.env\s*=.*["\'][^"\']*["\']',  # Hardcoded secrets
        r'password\s*=\s*["\'][^"\']+["\']',
    ]
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.report = ValidationReport(project_path=project_path)
    
    def scan_all(self) -> ValidationReport:
        """Run all validators."""
        logger.info(f"Scanning {self.project_path}...")
        
        self.scan_stubs()
        self.scan_placeholders()
        self.scan_broken_imports()
        self.scan_contracts()
        
        logger.info(f"✓ Scan complete: {self.report.files_scanned} files, {len(self.report.errors)} errors, {len(self.report.warnings)} warnings")
        return self.report
    
    def scan_stubs(self) -> None:
        """Find stub implementations."""
        for py_file in self.project_path.rglob("*.py"):
            self.report.files_scanned += 1
            try:
                content = py_file.read_text()
                lines = content.split("\n")
                
                for i, line in enumerate(lines, start=1):
                    for pattern in self.STUB_PATTERNS:
                        if re.search(pattern, line):
                            self.report.issues.append(ValidationIssue(
                                severity="error",
                                category="stub",
                                file_path=py_file,
                                line_number=i,
                                message="Stub implementation detected",
                                context=line.strip()
                            ))
            except Exception as e:
                logger.debug(f"Error scanning {py_file}: {e}")
    
    def scan_placeholders(self) -> None:
        """Find placeholder comments."""
        for py_file in self.project_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                lines = content.split("\n")
                
                for i, line in enumerate(lines, start=1):
                    for pattern in self.PLACEHOLDER_PATTERNS:
                        if re.search(pattern, line, re.IGNORECASE):
                            self.report.issues.append(ValidationIssue(
                                severity="warning",
                                category="placeholder",
                                file_path=py_file,
                                line_number=i,
                                message="Placeholder comment found",
                                context=line.strip()
                            ))
            except Exception as e:
                logger.debug(f"Error scanning {py_file}: {e}")
    
    def scan_broken_imports(self) -> None:
        """Check for broken imports using AST parsing."""
        for py_file in self.project_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                tree = ast.parse(content, filename=str(py_file))
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if not self._can_resolve_import(alias.name, py_file):
                                self.report.issues.append(ValidationIssue(
                                    severity="error",
                                    category="broken_import",
                                    file_path=py_file,
                                    line_number=node.lineno,
                                    message=f"Cannot resolve import: {alias.name}",
                                    context=f"import {alias.name}"
                                ))
                    
                    elif isinstance(node, ast.ImportFrom):
                        if node.module and not self._can_resolve_import(node.module, py_file):
                            self.report.issues.append(ValidationIssue(
                                severity="error",
                                category="broken_import",
                                file_path=py_file,
                                line_number=node.lineno,
                                message=f"Cannot resolve module: {node.module}",
                                context=f"from {node.module} import ..."
                            ))
            
            except SyntaxError as e:
                self.report.issues.append(ValidationIssue(
                    severity="error",
                    category="syntax",
                    file_path=py_file,
                    line_number=e.lineno,
                    message=f"Syntax error: {e.msg}",
                    context=""
                ))
            except Exception as e:
                logger.debug(f"Error parsing {py_file}: {e}")
    
    def scan_contracts(self) -> None:
        """Validate function contracts (signatures, type hints)."""
        for py_file in self.project_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                tree = ast.parse(content, filename=str(py_file))
                
                # Find all function definitions
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Check for missing return type hints (warning only)
                        if node.returns is None and node.name not in ["__init__", "__str__", "__repr__"]:
                            self.report.issues.append(ValidationIssue(
                                severity="info",
                                category="contract",
                                file_path=py_file,
                                line_number=node.lineno,
                                message=f"Function '{node.name}' missing return type hint",
                                context=f"def {node.name}(...)"
                            ))
                        
                        # Check for functions with no docstring (public functions only)
                        if not ast.get_docstring(node) and not node.name.startswith("_"):
                            self.report.issues.append(ValidationIssue(
                                severity="info",
                                category="contract",
                                file_path=py_file,
                                line_number=node.lineno,
                                message=f"Public function '{node.name}' missing docstring",
                                context=f"def {node.name}(...)"
                            ))
            
            except Exception as e:
                logger.debug(f"Error analyzing contracts in {py_file}: {e}")
    
    def _can_resolve_import(self, module_name: str, from_file: Path) -> bool:
        """Check if an import can be resolved (basic heuristic)."""
        # Standard library (common ones)
        stdlib = {
            "os", "sys", "re", "json", "pathlib", "typing", "datetime", 
            "argparse", "logging", "subprocess", "collections", "itertools",
            "functools", "dataclasses", "asyncio", "concurrent", "threading",
            "multiprocessing", "sqlite3", "csv", "unittest", "ast"
        }
        
        first_part = module_name.split(".")[0]
        if first_part in stdlib:
            return True
        
        # Check if it's a relative import within project
        if "." in module_name:
            # Try to find corresponding .py file
            parts = module_name.split(".")
            potential_file = self.project_path / "/".join(parts[:-1]) / f"{parts[-1]}.py"
            if potential_file.exists():
                return True
        
        # Check if module exists as file in project
        potential_file = self.project_path / f"{first_part}.py"
        if potential_file.exists():
            return True
        
        # Check if it's a directory with __init__.py
        potential_package = self.project_path / first_part / "__init__.py"
        if potential_package.exists():
            return True
        
        # Otherwise, assume it's installed (can't check without runtime)
        # Only flag as error if it looks like a local import
        if not first_part[0].isupper():  # Not likely to be third-party
            return False
        
        return True  # Assume third-party packages are installed


def main():
    parser = argparse.ArgumentParser(description="Build Validation Tools")
    parser.add_argument("action", choices=["scan", "check-contracts", "sweep"])
    parser.add_argument("project_path", type=Path, help="Path to project directory")
    parser.add_argument("--all", action="store_true", help="Run all checks (for sweep)")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    
    args = parser.parse_args()
    
    if not args.project_path.exists():
        logger.error(f"Project path not found: {args.project_path}")
        return 1
    
    validator = Validator(args.project_path)
    
    if args.action == "scan":
        validator.scan_stubs()
        validator.scan_broken_imports()
    elif args.action == "check-contracts":
        validator.scan_contracts()
    elif args.action == "sweep":
        validator.scan_all()
    
    # Output results
    if args.json:
        import json
        output = {
            "project": str(validator.report.project_path),
            "files_scanned": validator.report.files_scanned,
            "errors": len(validator.report.errors),
            "warnings": len(validator.report.warnings),
            "issues": [
                {
                    "severity": i.severity,
                    "category": i.category,
                    "file": str(i.file_path),
                    "line": i.line_number,
                    "message": i.message,
                    "context": i.context
                }
                for i in validator.report.issues
            ]
        }
        print(json.dumps(output, indent=2))
    else:
        print(validator.report.summary())
    
    # Return non-zero if critical issues found
    return 1 if validator.report.has_critical_issues else 0


if __name__ == "__main__":
    exit(main())
