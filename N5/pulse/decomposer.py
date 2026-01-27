#!/usr/bin/env python3
"""
Decomposition strategies for different task types.
Each strategy converts a seeded interview into a structured plan with Drops.
"""

import json
from dataclasses import dataclass, asdict
from typing import List

@dataclass
class Drop:
    id: str
    name: str
    stream: int
    depends_on: List[str]
    description: str
    deliverables: List[str]
    spawn_mode: str = "auto"

@dataclass
class Plan:
    title: str
    task_type: str
    objective: str
    streams: int
    drops: List[Drop]
    success_criteria: List[str]

def decompose_content(title: str, synthesis: dict) -> Plan:
    """Decomposition strategy for content tasks."""
    drops = [
        Drop(
            id="D1.1",
            name="Outline",
            stream=1,
            depends_on=[],
            description="Create detailed outline with key points, structure, and tone guidelines",
            deliverables=["outline.md"]
        ),
        Drop(
            id="D1.2",
            name="Research & Examples",
            stream=1,
            depends_on=[],
            description="Gather supporting materials, examples, references",
            deliverables=["research_notes.md"]
        ),
        Drop(
            id="D2.1",
            name="First Draft",
            stream=2,
            depends_on=["D1.1", "D1.2"],
            description="Write complete first draft following outline",
            deliverables=["draft_v1.md"]
        ),
        Drop(
            id="D3.1",
            name="Edit & Polish",
            stream=3,
            depends_on=["D2.1"],
            description="Edit for clarity, tone, length constraints",
            deliverables=["final.md"]
        )
    ]
    
    return Plan(
        title=title,
        task_type="content",
        objective=synthesis.get("combined_text", "")[:200],
        streams=3,
        drops=drops,
        success_criteria=[
            "Outline covers all key points from interview",
            "Draft matches specified tone and audience",
            "Final meets length constraints",
            "No placeholder content remains"
        ]
    )

def decompose_research(title: str, synthesis: dict) -> Plan:
    """Decomposition strategy for research tasks."""
    drops = [
        Drop(
            id="D1.1",
            name="Scope Definition",
            stream=1,
            depends_on=[],
            description="Define research questions, sources, boundaries",
            deliverables=["research_scope.md"]
        ),
        Drop(
            id="D1.2",
            name="Primary Research",
            stream=1,
            depends_on=[],
            description="Web research, data gathering, source collection",
            deliverables=["raw_findings.md", "sources.json"]
        ),
        Drop(
            id="D1.3",
            name="Competitive Intel",
            stream=1,
            depends_on=[],
            description="Competitor-specific research if applicable",
            deliverables=["competitive_analysis.md"]
        ),
        Drop(
            id="D2.1",
            name="Synthesis",
            stream=2,
            depends_on=["D1.1", "D1.2", "D1.3"],
            description="Synthesize findings into patterns and insights",
            deliverables=["synthesis.md"]
        ),
        Drop(
            id="D3.1",
            name="Final Report",
            stream=3,
            depends_on=["D2.1"],
            description="Create formatted final deliverable",
            deliverables=["report.md"]
        )
    ]
    
    return Plan(
        title=title,
        task_type="research",
        objective=synthesis.get("combined_text", "")[:200],
        streams=3,
        drops=drops,
        success_criteria=[
            "All research questions addressed",
            "Sources cited properly",
            "Findings synthesized (not just data dump)",
            "Actionable insights identified"
        ]
    )

def decompose_analysis(title: str, synthesis: dict) -> Plan:
    """Decomposition strategy for analysis tasks."""
    drops = [
        Drop(
            id="D1.1",
            name="Data Collection",
            stream=1,
            depends_on=[],
            description="Gather and validate input data",
            deliverables=["data_inventory.md"]
        ),
        Drop(
            id="D2.1",
            name="Analysis",
            stream=2,
            depends_on=["D1.1"],
            description="Perform core analysis, identify patterns",
            deliverables=["analysis.md"]
        ),
        Drop(
            id="D2.2",
            name="Visualization",
            stream=2,
            depends_on=["D1.1"],
            description="Create supporting visualizations",
            deliverables=["charts/"]
        ),
        Drop(
            id="D3.1",
            name="Report",
            stream=3,
            depends_on=["D2.1", "D2.2"],
            description="Compile analysis into final report",
            deliverables=["analysis_report.md"]
        )
    ]
    
    return Plan(
        title=title,
        task_type="analysis",
        objective=synthesis.get("combined_text", "")[:200],
        streams=3,
        drops=drops,
        success_criteria=[
            "Data sources documented",
            "Analysis methodology clear",
            "Key findings highlighted",
            "Recommendations provided"
        ]
    )

def decompose_code_build(title: str, synthesis: dict) -> Plan:
    """Decomposition strategy for code build tasks (standard Pulse)."""
    # This delegates to existing Pulse decomposition
    drops = [
        Drop(
            id="D1.1",
            name="Foundation",
            stream=1,
            depends_on=[],
            description="Core infrastructure and setup",
            deliverables=["foundation code"]
        ),
        Drop(
            id="D2.1",
            name="Implementation",
            stream=2,
            depends_on=["D1.1"],
            description="Main feature implementation",
            deliverables=["feature code"]
        ),
        Drop(
            id="D3.1",
            name="Testing & Docs",
            stream=3,
            depends_on=["D2.1"],
            description="Tests and documentation",
            deliverables=["tests", "docs"]
        )
    ]
    
    return Plan(
        title=title,
        task_type="code_build",
        objective=synthesis.get("combined_text", "")[:200],
        streams=3,
        drops=drops,
        success_criteria=[
            "All requirements implemented",
            "Tests passing",
            "Documentation complete"
        ]
    )

def decompose_hybrid(title: str, synthesis: dict) -> Plan:
    """Decomposition strategy for hybrid tasks."""
    # Combine research + content patterns
    drops = [
        Drop(
            id="D1.1",
            name="Research Phase",
            stream=1,
            depends_on=[],
            description="Information gathering and analysis",
            deliverables=["research.md"]
        ),
        Drop(
            id="D2.1",
            name="Synthesis",
            stream=2,
            depends_on=["D1.1"],
            description="Synthesize research into key insights",
            deliverables=["synthesis.md"]
        ),
        Drop(
            id="D3.1",
            name="Output Creation",
            stream=3,
            depends_on=["D2.1"],
            description="Create final deliverable",
            deliverables=["output.md"]
        )
    ]
    
    return Plan(
        title=title,
        task_type="hybrid",
        objective=synthesis.get("combined_text", "")[:200],
        streams=3,
        drops=drops,
        success_criteria=[
            "Research complete",
            "Synthesis coherent",
            "Output meets requirements"
        ]
    )

STRATEGIES = {
    "content": decompose_content,
    "research": decompose_research,
    "analysis": decompose_analysis,
    "code_build": decompose_code_build,
    "hybrid": decompose_hybrid
}

def decompose(title: str, task_type: str, synthesis: dict) -> Plan:
    """Decompose a task into a plan using type-appropriate strategy."""
    strategy = STRATEGIES.get(task_type, decompose_hybrid)
    return strategy(title, synthesis)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Task Decomposer")
    parser.add_argument("title", help="Task title")
    parser.add_argument("--type", default="hybrid", choices=list(STRATEGIES.keys()))
    parser.add_argument("--synthesis", default="{}", help="Synthesis JSON")
    
    args = parser.parse_args()
    synthesis = json.loads(args.synthesis)
    plan = decompose(args.title, args.type, synthesis)
    
    print(json.dumps(asdict(plan), indent=2))

if __name__ == "__main__":
    main()
