#!/usr/bin/env python3
"""
MemeBench Evaluation CLI
Run benchmark evaluations against AI models.
"""

import argparse
import json
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

import yaml
from models import get_model, list_models, EvaluationResult


def load_questions(path: Path) -> list[dict]:
    """Load questions from YAML file."""
    with open(path) as f:
        return yaml.safe_load(f)


def save_results(results: list[EvaluationResult], path: Path) -> None:
    """Save results to JSONL file."""
    with open(path, "a") as f:
        for result in results:
            record = {
                "question_id": result.question_id,
                "model_response": result.model_response,
                "scores": result.scores,
                "metadata": result.metadata,
            }
            f.write(json.dumps(record) + "\n")


def run_evaluation(
    questions: list[dict],
    model_name: str,
    dry_run: bool = False
) -> list[EvaluationResult]:
    """
    Run evaluation on questions.
    
    Args:
        questions: List of question dicts
        model_name: Model to use for evaluation
        dry_run: If True, validate only without running
        
    Returns:
        List of EvaluationResult objects
    """
    if dry_run:
        print(f"[DRY RUN] Would evaluate {len(questions)} questions with model '{model_name}'")
        print(f"[DRY RUN] Questions validated successfully")
        return []
    
    model = get_model(model_name)
    print(f"Evaluating {len(questions)} questions with model '{model.name}'...")
    
    results = []
    for i, question in enumerate(questions, 1):
        print(f"  [{i}/{len(questions)}] {question.get('id', 'unknown')}")
        result = model.evaluate(question)
        results.append(result)
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description="MemeBench: AI Cultural Zeitgeist Benchmark",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input data/sample.yaml --model mock --output results.jsonl
  %(prog)s --input data/sample.yaml --dry-run
  %(prog)s --list-models
        """
    )
    
    parser.add_argument(
        "--input", "-i",
        type=Path,
        help="Path to questions YAML file"
    )
    parser.add_argument(
        "--model", "-m",
        default="mock",
        help="Model to use for evaluation (default: mock)"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        help="Path to output JSONL file (appends if exists)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs without running evaluation"
    )
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="List available models and exit"
    )
    
    args = parser.parse_args()
    
    # Handle --list-models
    if args.list_models:
        print("Available models:")
        for name in list_models():
            print(f"  - {name}")
        return 0
    
    # Require --input for actual runs
    if not args.input:
        print("MemeBench evaluation harness ready.")
        print("Use --help for usage information.")
        return 0
    
    # Load questions
    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        return 1
    
    questions = load_questions(args.input)
    print(f"Loaded {len(questions)} questions from {args.input}")
    
    # Run evaluation
    results = run_evaluation(questions, args.model, args.dry_run)
    
    # Save results if not dry run and output specified
    if results and args.output:
        save_results(results, args.output)
        print(f"Results saved to {args.output}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

