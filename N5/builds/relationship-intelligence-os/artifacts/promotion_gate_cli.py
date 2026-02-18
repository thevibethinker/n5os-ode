#!/usr/bin/env python3
"""
CLI tool for the Promotion Gate Engine
Provides command-line interface for scoring, routing, and auditing promotion candidates.
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import logging

# Add paths for imports
sys.path.append('/home/workspace/N5/schemas')
sys.path.append('/home/workspace/N5/builds/relationship-intelligence-os/artifacts')

from promotion_gate_engine import (
    PromotionGateEngine, 
    ScoringConfig, 
    ScoringInput
)
from promotion_gate_test_fixtures import (
    PromotionGateTestFixtures,
    run_fixture_validation_tests,
    create_sample_config
)


class PromotionGateCLI:
    """Command-line interface for the Promotion Gate Engine."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def setup_logging(self, verbose: bool = False):
        """Setup logging configuration."""
        level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def load_config(self, config_path: Optional[str] = None) -> ScoringConfig:
        """Load scoring configuration from file or use defaults."""
        
        if config_path and Path(config_path).exists():
            self.logger.info(f"Loading configuration from {config_path}")
            
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            
            # Create config with loaded parameters
            config = ScoringConfig()
            for key, value in config_data.items():
                if hasattr(config, key):
                    setattr(config, key, value)
                    
            return config
        
        else:
            if config_path:
                self.logger.warning(f"Config file {config_path} not found, using defaults")
            else:
                self.logger.info("Using default configuration")
            
            return ScoringConfig()
    
    def load_input_data(self, input_path: str) -> ScoringInput:
        """Load scoring input from JSON file."""
        
        self.logger.info(f"Loading input data from {input_path}")
        
        with open(input_path, 'r') as f:
            input_data = json.load(f)
        
        return ScoringInput(**input_data)
    
    def process_single_candidate(self, args) -> int:
        """Process a single promotion candidate."""
        
        try:
            # Load configuration
            config = self.load_config(args.config)
            
            # Load input data
            input_data = self.load_input_data(args.input)
            
            # Create engine and process
            engine = PromotionGateEngine(config)
            result = engine.process_candidate(input_data, dry_run=args.dry_run)
            
            # Output result
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(result, f, indent=2, default=str)
                self.logger.info(f"Result written to {args.output}")
            else:
                print(json.dumps(result, indent=2, default=str))
            
            # Summary output to stderr for piping
            if 'error' in result:
                self.logger.error(f"Processing failed: {result['error']}")
                return 1
            else:
                tier = result.get('tier', 'Unknown')
                score = result.get('score', 0)
                status = result.get('status', 'Unknown')
                
                self.logger.info(f"Processed candidate: Tier {tier} (score: {score:.1f}, status: {status})")
                
                if args.dry_run and 'audit_report' in result:
                    audit = result['audit_report']
                    routing = audit.get('routing_decision', {})
                    self.logger.info(f"Routing: {routing.get('reasoning', 'No reasoning')}")
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Error processing candidate: {str(e)}")
            return 1
    
    def process_batch_candidates(self, args) -> int:
        """Process a batch of promotion candidates."""
        
        try:
            # Load configuration
            config = self.load_config(args.config)
            
            # Load batch input data
            self.logger.info(f"Loading batch data from {args.input}")
            
            with open(args.input, 'r') as f:
                batch_data = json.load(f)
            
            if not isinstance(batch_data, list):
                self.logger.error("Batch input must be a JSON array of candidate objects")
                return 1
            
            # Create engine
            engine = PromotionGateEngine(config)
            
            # Process each candidate
            results = []
            stats = {'processed': 0, 'errors': 0, 'tier_counts': {'A': 0, 'B': 0, 'C': 0}}
            
            for i, candidate_data in enumerate(batch_data):
                try:
                    # Convert to ScoringInput
                    input_data = ScoringInput(**candidate_data)
                    
                    # Process candidate
                    result = engine.process_candidate(input_data, dry_run=args.dry_run)
                    results.append(result)
                    
                    # Update stats
                    stats['processed'] += 1
                    
                    if 'error' in result:
                        stats['errors'] += 1
                    else:
                        tier = result.get('tier', 'C')
                        if tier in stats['tier_counts']:
                            stats['tier_counts'][tier] += 1
                    
                    if args.verbose:
                        tier = result.get('tier', 'Error')
                        score = result.get('score', 0)
                        self.logger.info(f"Candidate {i+1}: Tier {tier} (score: {score:.1f})")
                
                except Exception as e:
                    self.logger.error(f"Error processing candidate {i+1}: {str(e)}")
                    results.append({'error': str(e), 'candidate_index': i})
                    stats['errors'] += 1
            
            # Create batch result
            batch_result = {
                'batch_stats': stats,
                'results': results,
                'processed_at': datetime.now(timezone.utc).isoformat(),
                'config_used': {
                    'tier_a_threshold': config.tier_a_threshold,
                    'tier_b_threshold': config.tier_b_threshold,
                    'dry_run_mode': args.dry_run
                }
            }
            
            # Output batch result
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(batch_result, f, indent=2, default=str)
                self.logger.info(f"Batch result written to {args.output}")
            else:
                print(json.dumps(batch_result, indent=2, default=str))
            
            # Summary to stderr
            self.logger.info(f"Batch processing complete: {stats['processed']} candidates processed")
            self.logger.info(f"Tier distribution: A={stats['tier_counts']['A']}, B={stats['tier_counts']['B']}, C={stats['tier_counts']['C']}")
            self.logger.info(f"Errors: {stats['errors']}")
            
            return 0 if stats['errors'] == 0 else 1
            
        except Exception as e:
            self.logger.error(f"Error processing batch: {str(e)}")
            return 1
    
    def generate_test_fixtures(self, args) -> int:
        """Generate test fixtures."""
        
        try:
            self.logger.info(f"Generating test fixtures to {args.output_dir}")
            
            # Create output directory
            output_dir = Path(args.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate fixtures
            fixtures_gen = PromotionGateTestFixtures()
            fixtures_gen.save_fixtures_to_files(str(output_dir))
            
            # Generate sample config
            sample_config = create_sample_config()
            config_file = output_dir / "sample_config.json"
            
            with open(config_file, 'w') as f:
                json.dump(sample_config, f, indent=2)
            
            self.logger.info(f"Sample configuration saved to {config_file}")
            self.logger.info("Test fixtures generation complete")
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Error generating test fixtures: {str(e)}")
            return 1
    
    def validate_fixtures(self, args) -> int:
        """Run validation tests on fixtures."""
        
        try:
            self.logger.info("Running fixture validation tests...")
            
            results = run_fixture_validation_tests()
            
            # Save detailed results if requested
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(results, f, indent=2, default=str)
                self.logger.info(f"Detailed results written to {args.output}")
            
            # Return exit code based on success rate
            success_rate = results['passed_tests'] / results['total_tests']
            return 0 if success_rate >= 0.9 else 1
            
        except Exception as e:
            self.logger.error(f"Error validating fixtures: {str(e)}")
            return 1
    
    def generate_audit_report(self, args) -> int:
        """Generate a comprehensive audit report."""
        
        try:
            # Load configuration
            config = self.load_config(args.config)
            
            # Load input data (can be single candidate or batch)
            self.logger.info(f"Loading data for audit report from {args.input}")
            
            with open(args.input, 'r') as f:
                input_data = json.load(f)
            
            # Create engine
            engine = PromotionGateEngine(config)
            
            # Process data
            if isinstance(input_data, list):
                # Batch audit
                audit_results = []
                for candidate_data in input_data:
                    input_obj = ScoringInput(**candidate_data)
                    result = engine.process_candidate(input_obj, dry_run=True)
                    audit_results.append(result)
            else:
                # Single candidate audit
                input_obj = ScoringInput(**input_data)
                result = engine.process_candidate(input_obj, dry_run=True)
                audit_results = [result]
            
            # Generate comprehensive audit report
            audit_report = self._generate_comprehensive_audit(audit_results, config)
            
            # Output audit report
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(audit_report, f, indent=2, default=str)
                self.logger.info(f"Audit report written to {args.output}")
            else:
                print(json.dumps(audit_report, indent=2, default=str))
            
            # Summary
            total_candidates = len(audit_results)
            tier_counts = audit_report['summary']['tier_distribution']
            
            self.logger.info(f"Audit report generated for {total_candidates} candidates")
            self.logger.info(f"Distribution: A={tier_counts['A']}, B={tier_counts['B']}, C={tier_counts['C']}")
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Error generating audit report: {str(e)}")
            return 1
    
    def _generate_comprehensive_audit(self, results: List[Dict[str, Any]], config: ScoringConfig) -> Dict[str, Any]:
        """Generate comprehensive audit report from processing results."""
        
        # Calculate summary statistics
        total_candidates = len(results)
        tier_counts = {'A': 0, 'B': 0, 'C': 0}
        score_distribution = []
        override_count = 0
        routing_stats = {
            'semantic_memory': 0,
            'graph_edges': 0,
            'crm_projection': 0,
            'deliverables_db': 0
        }
        
        for result in results:
            if 'tier' in result:
                tier = result['tier']
                tier_counts[tier] += 1
            
            if 'score' in result:
                score_distribution.append(result['score'])
            
            if result.get('hard_override', {}).get('applied'):
                override_count += 1
            
            routing = result.get('routing', {})
            for target, enabled in routing.items():
                if enabled and target in routing_stats:
                    routing_stats[target] += 1
        
        # Calculate score statistics
        if score_distribution:
            avg_score = sum(score_distribution) / len(score_distribution)
            min_score = min(score_distribution)
            max_score = max(score_distribution)
        else:
            avg_score = min_score = max_score = 0
        
        # Generate comprehensive report
        audit_report = {
            'audit_metadata': {
                'generated_at': datetime.now(timezone.utc).isoformat(),
                'total_candidates': total_candidates,
                'configuration_version': '1.0.0'
            },
            'summary': {
                'tier_distribution': tier_counts,
                'score_statistics': {
                    'average': round(avg_score, 2),
                    'minimum': min_score,
                    'maximum': max_score,
                    'distribution': score_distribution
                },
                'hard_overrides': {
                    'count': override_count,
                    'percentage': round((override_count / total_candidates) * 100, 1) if total_candidates > 0 else 0
                },
                'routing_statistics': {
                    'semantic_memory': f"{routing_stats['semantic_memory']}/{total_candidates}",
                    'graph_edges': f"{routing_stats['graph_edges']}/{total_candidates}",
                    'crm_projection': f"{routing_stats['crm_projection']}/{total_candidates}",
                    'deliverables_db': f"{routing_stats['deliverables_db']}/{total_candidates}"
                }
            },
            'configuration_analysis': {
                'thresholds': {
                    'tier_a': config.tier_a_threshold,
                    'tier_b': config.tier_b_threshold,
                    'tier_c': config.tier_c_threshold
                },
                'score_weights': {
                    'strategic_importance': config.strategic_importance_max,
                    'relationship_delta_strength': config.relationship_delta_strength_max,
                    'commitment_clarity': config.commitment_clarity_max,
                    'evidence_quality': config.evidence_quality_max,
                    'novelty': config.novelty_max,
                    'execution_value': config.execution_value_max
                },
                'hard_override_triggers': list(config.hard_override_keywords.keys())
            },
            'detailed_results': []
        }
        
        # Add detailed results for each candidate
        for i, result in enumerate(results):
            if 'audit_report' in result:
                audit_data = result['audit_report']
                
                detailed_result = {
                    'candidate_index': i,
                    'tier': result.get('tier', 'Unknown'),
                    'score': result.get('score', 0),
                    'confidence': result.get('confidence', 0),
                    'hard_override': result.get('hard_override', {}).get('applied', False),
                    'routing_decision': audit_data.get('routing_decision', {}),
                    'score_explanations': result.get('score_explanations', {})
                }
                
                audit_report['detailed_results'].append(detailed_result)
        
        return audit_report


def main():
    """Main CLI entry point."""
    
    cli = PromotionGateCLI()
    
    # Create argument parser
    parser = argparse.ArgumentParser(
        description='Promotion Gate Engine CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process single candidate
  %(prog)s process --input candidate.json --output result.json --dry-run
  
  # Process batch with custom config
  %(prog)s batch --input batch.json --config custom_config.json --output results.json
  
  # Generate test fixtures
  %(prog)s fixtures --output-dir ./test_data/
  
  # Validate fixtures
  %(prog)s validate --output validation_report.json
  
  # Generate audit report
  %(prog)s audit --input candidates.json --output audit.json --config config.json
        """
    )
    
    # Global arguments
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Process single candidate
    process_parser = subparsers.add_parser('process', help='Process a single promotion candidate')
    process_parser.add_argument('--input', '-i', required=True, help='Input JSON file with candidate data')
    process_parser.add_argument('--output', '-o', help='Output file (default: stdout)')
    process_parser.add_argument('--config', '-c', help='Configuration file')
    process_parser.add_argument('--dry-run', action='store_true', help='Run in dry-run mode with audit report')
    
    # Process batch candidates
    batch_parser = subparsers.add_parser('batch', help='Process multiple promotion candidates')
    batch_parser.add_argument('--input', '-i', required=True, help='Input JSON file with array of candidates')
    batch_parser.add_argument('--output', '-o', help='Output file (default: stdout)')
    batch_parser.add_argument('--config', '-c', help='Configuration file')
    batch_parser.add_argument('--dry-run', action='store_true', help='Run in dry-run mode with audit reports')
    
    # Generate test fixtures
    fixtures_parser = subparsers.add_parser('fixtures', help='Generate test fixtures')
    fixtures_parser.add_argument('--output-dir', '-o', 
                                default='/home/workspace/N5/builds/relationship-intelligence-os/artifacts/test_fixtures/',
                                help='Output directory for fixtures')
    
    # Validate fixtures
    validate_parser = subparsers.add_parser('validate', help='Validate test fixtures')
    validate_parser.add_argument('--output', '-o', help='Output file for detailed results')
    
    # Generate audit report
    audit_parser = subparsers.add_parser('audit', help='Generate comprehensive audit report')
    audit_parser.add_argument('--input', '-i', required=True, help='Input JSON file with candidate data')
    audit_parser.add_argument('--output', '-o', help='Output file (default: stdout)')
    audit_parser.add_argument('--config', '-c', help='Configuration file')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Setup logging
    cli.setup_logging(args.verbose)
    
    # Execute command
    if args.command == 'process':
        return cli.process_single_candidate(args)
    elif args.command == 'batch':
        return cli.process_batch_candidates(args)
    elif args.command == 'fixtures':
        return cli.generate_test_fixtures(args)
    elif args.command == 'validate':
        return cli.validate_fixtures(args)
    elif args.command == 'audit':
        return cli.generate_audit_report(args)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())