#!/usr/bin/env python3
"""
Candidate Synthesis Pipeline
----------------------------
Orchestrates the 5-step synthesis process:
1. Gather inputs (Airtable, GDrive, local files)
2. Generate/validate Hiring POV
3. Cluster stories
4. Diff resume vs Careerspan
5. Generate final narrative

Usage:
    python3 run_pipeline.py --candidate-id rec... --output-dir ./output/
    python3 run_pipeline.py --decomposer-dir ./inbox/hardik-flowfuse/ --employer-name "Docsum" --output-dir ./output/
"""

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Add parent for imports
sys.path.insert(0, str(Path(__file__).parent))

from step1_gather import gather_inputs
from step2_hiring_pov import ensure_hiring_pov
from step3_cluster import cluster_stories
from step4_resume_diff import diff_resume
from step5_narrate import generate_narrative


def run_pipeline(
    candidate_id: str = None,
    decomposer_dir: str = None,
    employer_name: str = None,
    output_dir: str = None,
    skip_pov_generation: bool = False,
    verbose: bool = True
) -> dict:
    """
    Run the full synthesis pipeline.
    
    Args:
        candidate_id: Airtable candidate record ID (preferred)
        decomposer_dir: Path to decomposer output directory (alternative)
        employer_name: Employer name (required if using decomposer_dir)
        output_dir: Where to save intermediate and final outputs
        skip_pov_generation: Skip Hiring POV generation if missing
        verbose: Print progress
    
    Returns:
        SynthesizedNarrative dict ready for meta-resume-generator
    """
    
    if not output_dir:
        output_dir = Path(__file__).parent.parent / "output" / datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    def log(msg):
        if verbose:
            print(f"[SYNTHESIS] {msg}")
    
    # =========================================================================
    # STEP 1: Gather Inputs
    # =========================================================================
    log("Step 1: Gathering inputs...")
    
    gathered = gather_inputs(
        candidate_id=candidate_id,
        decomposer_dir=decomposer_dir,
        employer_name=employer_name
    )
    
    # Save intermediate output
    (output_dir / "step1_gathered.json").write_text(json.dumps(gathered, indent=2, default=str))
    log(f"  → Candidate: {gathered['candidate']['name']}")
    log(f"  → Employer: {gathered['employer']['name']}")
    log(f"  → Job Opening: {gathered['job_opening']['title']}")
    log(f"  → Skills count: {len(gathered['decomposer']['skills'])}")
    
    # =========================================================================
    # STEP 2: Ensure Hiring POV
    # =========================================================================
    log("Step 2: Ensuring Hiring POV exists...")
    
    hiring_pov = ensure_hiring_pov(
        gathered=gathered,
        skip_generation=skip_pov_generation
    )
    
    (output_dir / "step2_hiring_pov.json").write_text(json.dumps(hiring_pov, indent=2))
    log(f"  → POV status: {'generated' if hiring_pov.get('generated') else 'existing'}")
    log(f"  → Explicit requirements: {len(hiring_pov.get('explicit_requirements', []))}")
    log(f"  → Implicit filters: {len(hiring_pov.get('implicit_filters', []))}")
    
    # =========================================================================
    # STEP 3: Cluster Stories
    # =========================================================================
    log("Step 3: Clustering stories...")
    
    clusters = cluster_stories(
        skills=gathered['decomposer']['skills'],
        hiring_pov=hiring_pov
    )
    
    (output_dir / "step3_clusters.json").write_text(json.dumps(clusters, indent=2))
    log(f"  → Story clusters: {len(clusters.get('story_clusters', []))}")
    log(f"  → Cross-cutting patterns: {len(clusters.get('cross_cutting_patterns', []))}")
    
    # =========================================================================
    # STEP 4: Resume Diff
    # =========================================================================
    log("Step 4: Diffing resume vs Careerspan...")
    
    resume_diff = diff_resume(
        resume_text=gathered.get('resume_text', ''),
        skills=gathered['decomposer']['skills'],
        clusters=clusters
    )
    
    (output_dir / "step4_resume_diff.json").write_text(json.dumps(resume_diff, indent=2))
    log(f"  → Substantiated: {len(resume_diff.get('substantiated_beyond_resume', []))}")
    log(f"  → Revealed: {len(resume_diff.get('revealed_beyond_resume', []))}")
    log(f"  → Unverified: {len(resume_diff.get('unverified_claims', []))}")
    
    # =========================================================================
    # STEP 5: Generate Narrative
    # =========================================================================
    log("Step 5: Generating final narrative...")
    
    narrative = generate_narrative(
        candidate=gathered['candidate'],
        employer=gathered['employer'],
        job_opening=gathered['job_opening'],
        hiring_pov=hiring_pov,
        clusters=clusters,
        resume_diff=resume_diff,
        scores=gathered['decomposer']['scores']
    )
    
    (output_dir / "step5_narrative.json").write_text(json.dumps(narrative, indent=2))
    log(f"  → Verdict: {narrative['verdict']['action']} ({narrative['verdict']['score']}/100)")
    log(f"  → Up spikes: {len(narrative['spikes']['up'])}")
    log(f"  → Down spikes: {len(narrative['spikes']['down'])}")
    
    # =========================================================================
    # Final Output
    # =========================================================================
    
    # Also save as synthesized_narrative.json for meta-resume-generator
    final_path = output_dir / "synthesized_narrative.json"
    final_path.write_text(json.dumps(narrative, indent=2))
    
    log(f"\n✓ Pipeline complete!")
    log(f"  Output dir: {output_dir}")
    log(f"  Final narrative: {final_path}")
    
    return narrative


def main():
    parser = argparse.ArgumentParser(description="Run candidate synthesis pipeline")
    
    # Input options (mutually exclusive groups)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--candidate-id", help="Airtable candidate record ID")
    input_group.add_argument("--decomposer-dir", help="Path to decomposer output directory")
    
    # Additional args
    parser.add_argument("--employer-name", help="Employer name (required with --decomposer-dir)")
    parser.add_argument("--output-dir", help="Output directory for intermediate files")
    parser.add_argument("--skip-pov", action="store_true", help="Skip Hiring POV generation")
    parser.add_argument("--quiet", action="store_true", help="Suppress progress output")
    
    args = parser.parse_args()
    
    # Validation
    if args.decomposer_dir and not args.employer_name:
        parser.error("--employer-name is required when using --decomposer-dir")
    
    try:
        result = run_pipeline(
            candidate_id=args.candidate_id,
            decomposer_dir=args.decomposer_dir,
            employer_name=args.employer_name,
            output_dir=args.output_dir,
            skip_pov_generation=args.skip_pov,
            verbose=not args.quiet
        )
        
        # Print final verdict to stdout
        print(f"\n{'='*60}")
        print(f"VERDICT: {result['verdict']['action']}")
        print(f"SCORE: {result['verdict']['score']}/100")
        print(f"SUMMARY: {result['verdict']['summary']}")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"[ERROR] Pipeline failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
