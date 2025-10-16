#!/usr/bin/env python3
"""
Task Deconstructor - Intelligently decompose complex tasks into worker conversations

Analyzes orchestrator SESSION_STATE and conversation context to generate:
- Worker assignments (ASSIGNMENT.md for each)
- Execution plan (parallel batches + sequence)
- Dependency graph
- Risk assessment

Usage:
  python3 task_deconstructor.py --orchestrator con_ORCH_123
  python3 task_deconstructor.py --orchestrator con_ORCH_123 --dry-run
  python3 task_deconstructor.py --orchestrator con_ORCH_123 --output /path/to/output/
"""

import argparse
import json
import logging
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)

CONVO_WORKSPACES_ROOT = Path("/home/.z/workspaces")


@dataclass
class Module:
    """Represents a decomposed work module."""
    name: str
    description: str
    files_to_modify: List[str]
    files_to_read: List[str] = field(default_factory=list)
    dependencies: Set[str] = field(default_factory=set)
    interfaces: List[str] = field(default_factory=list)
    estimated_loc: int = 0
    complexity: str = "medium"  # low, medium, high
    risk_factors: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)


@dataclass
class ExecutionPlan:
    """Represents the execution plan for all workers."""
    batches: List[List[str]]  # List of parallel batches, each containing module names
    critical_path: List[str]
    estimated_duration: str
    risk_summary: Dict[str, int]


class TaskDeconstructor:
    def __init__(self, orchestrator_convo_id: str):
        self.orchestrator_id = orchestrator_convo_id
        self.workspace = CONVO_WORKSPACES_ROOT / orchestrator_convo_id
        self.state_file = self.workspace / "SESSION_STATE.md"
        self.modules: Dict[str, Module] = {}
        self.session_state = {}
        
    def load_session_state(self) -> bool:
        """Load SESSION_STATE.md from orchestrator."""
        try:
            if not self.state_file.exists():
                logger.error(f"SESSION_STATE.md not found for {self.orchestrator_id}")
                return False
            
            content = self.state_file.read_text()
            
            # Parse key sections
            self.session_state = {
                "objective": self._extract_section(content, "## Objective"),
                "context": self._extract_section(content, "## Context"),
                "files": self._extract_files(content),
                "decisions": self._extract_section(content, "## Insights & Decisions"),
            }
            
            logger.info(f"✓ Loaded SESSION_STATE.md for {self.orchestrator_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading session state: {e}", exc_info=True)
            return False
    
    def _extract_section(self, content: str, heading: str) -> str:
        """Extract content between heading and next ## heading."""
        pattern = rf"{re.escape(heading)}(.*?)(?=\n## |\Z)"
        match = re.search(pattern, content, re.DOTALL)
        return match.group(1).strip() if match else ""
    
    def _extract_files(self, content: str) -> List[str]:
        """Extract file mentions from content."""
        # Match file 'path' mentions
        file_pattern = r"file\s+['\"]([^'\"]+)['\"]"
        files = re.findall(file_pattern, content)
        
        # Also check Files in Context section
        context_section = self._extract_section(content, "## Context")
        files.extend(re.findall(r"[-*]\s*`?([^`\n]+\.(py|js|ts|go|rs|md|json))`?", context_section))
        
        return list(set(f[0] if isinstance(f, tuple) else f for f in files))
    
    def analyze_modules(self) -> bool:
        """Analyze task and identify natural module boundaries."""
        try:
            objective = self.session_state.get("objective", "")
            files = self.session_state.get("files", [])
            
            if not objective:
                logger.error("No objective found in SESSION_STATE.md")
                return False
            
            logger.info("Analyzing task for module boundaries...")
            
            # Strategy 1: If files specified, group by directory/purpose
            if files:
                self.modules = self._decompose_by_files(files, objective)
            else:
                # Strategy 2: Parse objective for natural subtasks
                self.modules = self._decompose_by_objective(objective)
            
            if not self.modules:
                logger.error("Could not identify modules. Need more context.")
                return False
            
            logger.info(f"✓ Identified {len(self.modules)} modules")
            return True
            
        except Exception as e:
            logger.error(f"Error analyzing modules: {e}", exc_info=True)
            return False
    
    def _decompose_by_files(self, files: List[str], objective: str) -> Dict[str, Module]:
        """Decompose by grouping related files."""
        modules = {}
        
        # Group files by directory or purpose
        groups = defaultdict(list)
        for file in files:
            path = Path(file)
            # Group by parent directory
            key = path.parent.name if path.parent.name else "root"
            groups[key].append(file)
        
        # Create module per group
        for idx, (group_name, group_files) in enumerate(groups.items(), 1):
            # Limit to 2 files per module (P0 Rule-of-Two)
            for batch_idx, i in enumerate(range(0, len(group_files), 2), 1):
                batch = group_files[i:i+2]
                module_name = f"{group_name}_module_{batch_idx}" if len(group_files) > 2 else f"{group_name}_module"
                
                modules[module_name] = Module(
                    name=module_name,
                    description=f"Implement changes for {', '.join(batch)}",
                    files_to_modify=batch,
                    estimated_loc=200 * len(batch),  # Rough estimate
                    complexity=self._estimate_complexity(batch),
                    assumptions=[f"Files exist and are modifiable", f"No breaking changes to public APIs"]
                )
        
        return modules
    
    def _decompose_by_objective(self, objective: str) -> Dict[str, Module]:
        """Decompose by parsing objective for subtasks."""
        modules = {}
        
        # Look for list items or natural breakpoints
        lines = objective.split('\n')
        subtasks = []
        
        for line in lines:
            # Match list items: -, *, 1., etc.
            if re.match(r'^\s*[-*\d.]+\s+', line):
                subtasks.append(line.strip())
        
        if not subtasks:
            # Fallback: create single module
            modules["main_module"] = Module(
                name="main_module",
                description=objective[:200],
                files_to_modify=[],
                estimated_loc=300,
                complexity="medium",
                assumptions=["Scope to be refined during implementation"]
            )
        else:
            # Create module per subtask
            for idx, task in enumerate(subtasks, 1):
                clean_task = re.sub(r'^\s*[-*\d.]+\s+', '', task)
                modules[f"module_{idx}"] = Module(
                    name=f"module_{idx}",
                    description=clean_task,
                    files_to_modify=[],
                    estimated_loc=200,
                    complexity="medium",
                    assumptions=["Files and dependencies TBD"]
                )
        
        return modules
    
    def _estimate_complexity(self, files: List[str]) -> str:
        """Estimate complexity based on file patterns."""
        # Simple heuristic
        risk_indicators = ["test", "config", "schema", "migration"]
        complex_indicators = ["api", "auth", "database", "integration"]
        
        for file in files:
            file_lower = file.lower()
            if any(ind in file_lower for ind in complex_indicators):
                return "high"
            if any(ind in file_lower for ind in risk_indicators):
                return "medium"
        
        return "low" if len(files) == 1 else "medium"
    
    def build_dependency_graph(self) -> Dict[str, Set[str]]:
        """Build dependency graph between modules."""
        graph = defaultdict(set)
        
        # Analyze file dependencies
        for mod_name, module in self.modules.items():
            for other_name, other_module in self.modules.items():
                if mod_name == other_name:
                    continue
                
                # If module reads files that another modifies, it depends on that module
                for read_file in module.files_to_read:
                    if read_file in other_module.files_to_modify:
                        graph[mod_name].add(other_name)
                        module.dependencies.add(other_name)
        
        return dict(graph)
    
    def generate_execution_plan(self) -> ExecutionPlan:
        """Generate execution plan with parallel batches."""
        graph = self.build_dependency_graph()
        
        # Topological sort to get sequence
        batches = []
        completed = set()
        
        while len(completed) < len(self.modules):
            # Find modules with no incomplete dependencies
            batch = []
            for mod_name, module in self.modules.items():
                if mod_name in completed:
                    continue
                if module.dependencies.issubset(completed):
                    batch.append(mod_name)
            
            if not batch:
                # Circular dependency or error
                remaining = set(self.modules.keys()) - completed
                logger.warning(f"Possible circular dependency: {remaining}")
                batch = list(remaining)
            
            batches.append(batch)
            completed.update(batch)
        
        # Calculate critical path (longest chain)
        critical_path = self._calculate_critical_path(graph)
        
        # Risk summary
        risk_summary = {
            "low": sum(1 for m in self.modules.values() if m.complexity == "low"),
            "medium": sum(1 for m in self.modules.values() if m.complexity == "medium"),
            "high": sum(1 for m in self.modules.values() if m.complexity == "high"),
        }
        
        # Estimate duration (rough: 30min per module in critical path)
        est_hours = len(critical_path) * 0.5
        estimated_duration = f"{est_hours:.1f} hours" if est_hours < 8 else f"{est_hours/8:.1f} days"
        
        return ExecutionPlan(
            batches=batches,
            critical_path=critical_path,
            estimated_duration=estimated_duration,
            risk_summary=risk_summary
        )
    
    def _calculate_critical_path(self, graph: Dict[str, Set[str]]) -> List[str]:
        """Find longest dependency chain."""
        def dfs_longest(node: str, visited: Set[str]) -> List[str]:
            if node in visited:
                return []
            visited.add(node)
            
            deps = graph.get(node, set())
            if not deps:
                return [node]
            
            longest = []
            for dep in deps:
                path = dfs_longest(dep, visited.copy())
                if len(path) > len(longest):
                    longest = path
            
            return longest + [node]
        
        all_paths = []
        for module_name in self.modules:
            path = dfs_longest(module_name, set())
            if len(path) > len(all_paths):
                all_paths = path
        
        return all_paths
    
    def generate_worker_assignments(self, plan: ExecutionPlan, output_dir: Optional[Path] = None) -> List[Path]:
        """Generate ASSIGNMENT.md for each worker."""
        if output_dir is None:
            output_dir = self.workspace / "worker_assignments"
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        assignment_files = []
        
        for batch_idx, batch in enumerate(plan.batches, 1):
            for module_name in batch:
                module = self.modules[module_name]
                
                # Determine dependencies
                deps_text = ""
                if module.dependencies:
                    deps_text = "\n**Dependencies:** This module depends on:\n"
                    for dep in module.dependencies:
                        deps_text += f"- {dep} (must complete first)\n"
                
                # Generate assignment
                assignment_content = f"""# Worker Assignment: {module_name}

**Batch:** {batch_idx} of {len(plan.batches)}  
**Complexity:** {module.complexity}  
**Estimated LOC:** {module.estimated_loc}  
**Date:** {datetime.now().strftime("%Y-%m-%d")}

---

## Objective

{module.description}

---

## Files to Modify

{chr(10).join(f"- `{f}`" for f in module.files_to_modify) if module.files_to_modify else "*To be determined during implementation*"}

---

## Files for Reference (Read-Only)

{chr(10).join(f"- `{f}`" for f in module.files_to_read) if module.files_to_read else "*None specified*"}

---

## Dependencies
{deps_text if deps_text else "*No dependencies - can start immediately*"}

---

## Interface Contracts

{chr(10).join(f"- {iface}" for iface in module.interfaces) if module.interfaces else "*Define interfaces as needed, document in code*"}

---

## Success Criteria

{chr(10).join(f"- [ ] {criterion}" for criterion in module.success_criteria) if module.success_criteria else """- [ ] Implementation complete
- [ ] Code follows N5 principles (P0, P7, P19)
- [ ] Tests pass (if applicable)
- [ ] Documentation updated"""}

---

## Assumptions

{chr(10).join(f"- {assumption}" for assumption in module.assumptions) if module.assumptions else "- No special assumptions"}

---

## Risk Factors

{chr(10).join(f"- {risk}" for risk in module.risk_factors) if module.risk_factors else "*Low risk*"}

---

## Principles to Follow

- **P0 (Rule-of-Two):** Max 2 files actively modified
- **P7 (Dry-Run):** Test approach before full implementation
- **P19 (Error Handling):** Include try/except and logging
- **P15 (Complete):** Verify all criteria met before marking complete

---

## Communication

**Orchestrator:** {self.orchestrator_id}

**Report progress:**
```bash
python3 /home/workspace/N5/scripts/session_state_manager.py update \\
  --convo-id <YOUR_WORKER_CONVO_ID> \\
  --field "Current Task" \\
  --value "Working on {module_name}: <status>"
```

**Ask questions:**
```bash
python3 /home/workspace/N5/scripts/message_queue.py send \\
  --from <YOUR_WORKER_CONVO_ID> \\
  --to {self.orchestrator_id} \\
  --content "Question about {module_name}: ..." \\
  --type question
```

---

*Generated by task_deconstructor.py*  
*Orchestrator: {self.orchestrator_id}*
"""
                
                # Write assignment
                assignment_file = output_dir / f"{module_name}_ASSIGNMENT.md"
                assignment_file.write_text(assignment_content)
                assignment_files.append(assignment_file)
                logger.info(f"✓ Generated assignment: {assignment_file.name}")
        
        return assignment_files
    
    def generate_report(self, plan: ExecutionPlan, assignment_files: List[Path]) -> str:
        """Generate human-readable decomposition report."""
        report = f"""# Task Decomposition Report

**Orchestrator:** {self.orchestrator_id}  
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M ET")}  
**Total Modules:** {len(self.modules)}  
**Execution Batches:** {len(plan.batches)}

---

## Execution Plan

### Parallel Batches

"""
        
        for batch_idx, batch in enumerate(plan.batches, 1):
            report += f"\n**Batch {batch_idx}:** ({len(batch)} workers in parallel)\n"
            for module_name in batch:
                module = self.modules[module_name]
                report += f"- `{module_name}` - {module.description[:60]}{'...' if len(module.description) > 60 else ''} [{module.complexity} complexity]\n"
        
        report += f"""

### Critical Path

The longest dependency chain (determines minimum time):

{' → '.join(plan.critical_path)}

**Estimated Duration:** {plan.estimated_duration}

---

## Risk Summary

- **Low Complexity:** {plan.risk_summary['low']} modules
- **Medium Complexity:** {plan.risk_summary['medium']} modules
- **High Complexity:** {plan.risk_summary['high']} modules

**Recommendation:** Start high-complexity modules first to fail fast.

---

## Module Details

"""
        
        for module_name, module in self.modules.items():
            report += f"\n### {module_name}\n\n"
            report += f"**Description:** {module.description}\n\n"
            report += f"**Complexity:** {module.complexity} | **Est. LOC:** {module.estimated_loc}\n\n"
            
            if module.files_to_modify:
                report += f"**Files:** {', '.join(module.files_to_modify)}\n\n"
            
            if module.dependencies:
                report += f"**Depends on:** {', '.join(module.dependencies)}\n\n"
        
        report += f"""

---

## Next Steps

1. **Review this plan** - Adjust if needed
2. **Create worker conversations** - One per module
3. **Copy assignments** - Put ASSIGNMENT.md in each worker conversation
4. **Execute by batch** - Start Batch 1, then Batch 2 when Batch 1 completes
5. **Monitor progress** - Use `python3 N5/scripts/build_tracker.py --orchestrator {self.orchestrator_id}`

---

## Generated Assignments

{chr(10).join(f"- {f.name}" for f in assignment_files)}

**Location:** `{assignment_files[0].parent if assignment_files else 'N/A'}`

---

*Generated by task_deconstructor.py*
"""
        
        return report


def main(orchestrator_id: str, output_dir: Optional[Path] = None, dry_run: bool = False) -> int:
    """Main execution."""
    try:
        if dry_run:
            logger.info("[DRY RUN] Would analyze and decompose task")
            return 0
        
        deconstructor = TaskDeconstructor(orchestrator_id)
        
        # Load session state
        if not deconstructor.load_session_state():
            return 1
        
        # Analyze modules
        if not deconstructor.analyze_modules():
            return 1
        
        # Generate execution plan
        plan = deconstructor.generate_execution_plan()
        logger.info(f"✓ Generated execution plan: {len(plan.batches)} batches")
        
        # Generate worker assignments
        assignment_files = deconstructor.generate_worker_assignments(plan, output_dir)
        logger.info(f"✓ Generated {len(assignment_files)} worker assignments")
        
        # Generate report
        report = deconstructor.generate_report(plan, assignment_files)
        report_file = (output_dir or deconstructor.workspace / "worker_assignments") / "DECOMPOSITION_REPORT.md"
        report_file.write_text(report)
        logger.info(f"✓ Generated report: {report_file}")
        
        print(f"\n{report}\n")
        
        return 0
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deconstruct task into worker conversations")
    parser.add_argument("--orchestrator", required=True, help="Orchestrator conversation ID")
    parser.add_argument("--output", type=Path, help="Output directory for assignments")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    
    args = parser.parse_args()
    
    sys.exit(main(args.orchestrator, args.output, args.dry_run))
