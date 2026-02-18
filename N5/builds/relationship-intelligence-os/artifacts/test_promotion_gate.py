#!/usr/bin/env python3
"""
Test runner for Promotion Gate Engine
Validates functionality against test fixtures and edge cases.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List
import logging

# Add current directory to import path
sys.path.append(str(Path(__file__).parent))

from promotion_gate_engine import PromotionGateEngine, ScoringConfig
from test_fixtures import (
    TEST_FIXTURES, CONFIG_TEST_FIXTURES, VALIDATION_ERROR_FIXTURES,
    create_scoring_input_from_fixture, validate_fixture_expectations,
    list_fixtures
)

logger = logging.getLogger(__name__)


class PromotionGateTestRunner:
    """Test runner for the promotion gate engine."""
    
    def __init__(self):
        self.results = {
            "passed": [],
            "failed": [],
            "errors": []
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all test fixtures and return comprehensive results."""
        
        print("🔬 Running Promotion Gate Engine Test Suite")
        print("=" * 60)
        
        # Test default configuration
        print("\n📋 Testing with default configuration...")
        default_results = self._test_fixture_group(TEST_FIXTURES, ScoringConfig())
        
        # Test alternate configurations
        print("\n⚙️  Testing with strict configuration...")
        strict_config = ScoringConfig(**CONFIG_TEST_FIXTURES["strict_config"])
        strict_results = self._test_fixture_group(TEST_FIXTURES, strict_config, suffix="_strict")
        
        # Test dry-run mode
        print("\n🧪 Testing dry-run mode...")
        dry_run_results = self._test_dry_run_mode()
        
        # Test edge cases and error handling
        print("\n⚠️  Testing error handling...")
        error_results = self._test_error_cases()
        
        # Compile final results
        all_results = {
            "summary": {
                "total_tests": len(self.results["passed"]) + len(self.results["failed"]) + len(self.results["errors"]),
                "passed": len(self.results["passed"]),
                "failed": len(self.results["failed"]),
                "errors": len(self.results["errors"]),
                "success_rate": len(self.results["passed"]) / max(1, len(self.results["passed"]) + len(self.results["failed"]) + len(self.results["errors"])) * 100
            },
            "test_results": {
                "default_config": default_results,
                "strict_config": strict_results,
                "dry_run_mode": dry_run_results,
                "error_handling": error_results
            },
            "detailed_results": {
                "passed": self.results["passed"],
                "failed": self.results["failed"],
                "errors": self.results["errors"]
            }
        }
        
        self._print_summary(all_results)
        return all_results
    
    def _test_fixture_group(self, fixtures: Dict[str, Any], config: ScoringConfig, suffix: str = "") -> Dict[str, Any]:
        """Test a group of fixtures with a specific configuration."""
        
        engine = PromotionGateEngine(config)
        group_results = {}
        
        for fixture_name, fixture_data in fixtures.items():
            test_name = f"{fixture_name}{suffix}"
            print(f"  Testing {test_name}...")
            
            try:
                # Create input from fixture
                scoring_input = create_scoring_input_from_fixture(fixture_name)
                
                # Process through engine
                result = engine.process_candidate(scoring_input, dry_run=False)
                
                # Validate expectations
                validation_errors = validate_fixture_expectations(fixture_name, result)
                
                if validation_errors:
                    self.results["failed"].append({
                        "test_name": test_name,
                        "fixture": fixture_name,
                        "errors": validation_errors,
                        "result": result
                    })
                    group_results[test_name] = {
                        "status": "FAILED",
                        "errors": validation_errors
                    }
                    print(f"    ❌ FAILED: {', '.join(validation_errors)}")
                else:
                    self.results["passed"].append({
                        "test_name": test_name,
                        "fixture": fixture_name,
                        "result": result
                    })
                    group_results[test_name] = {
                        "status": "PASSED",
                        "score": result.get("score"),
                        "tier": result.get("tier"),
                        "routing": result.get("routing")
                    }
                    print(f"    ✅ PASSED (Score: {result.get('score', 0):.1f}, Tier: {result.get('tier')})")
                
            except Exception as e:
                self.results["errors"].append({
                    "test_name": test_name,
                    "fixture": fixture_name,
                    "error": str(e)
                })
                group_results[test_name] = {
                    "status": "ERROR",
                    "error": str(e)
                }
                print(f"    💥 ERROR: {str(e)}")
        
        return group_results
    
    def _test_dry_run_mode(self) -> Dict[str, Any]:
        """Test dry-run mode functionality."""
        
        engine = PromotionGateEngine()
        dry_run_results = {}
        
        # Test a few key fixtures in dry-run mode
        test_fixtures = [
            "tier_A_strategic_deliverable",
            "hard_override_explicit_promise",
            "edge_case_boundary_score_74"
        ]
        
        for fixture_name in test_fixtures:
            test_name = f"{fixture_name}_dry_run"
            print(f"  Testing {test_name}...")
            
            try:
                scoring_input = create_scoring_input_from_fixture(fixture_name)
                result = engine.process_candidate(scoring_input, dry_run=True)
                
                # Verify dry-run specific features
                validation_errors = []
                
                if result.get("processing_mode") != "dry_run":
                    validation_errors.append("Processing mode not set to dry_run")
                
                if "audit_report" not in result:
                    validation_errors.append("Missing audit_report in dry_run mode")
                
                # Check audit report structure
                audit_report = result.get("audit_report", {})
                required_sections = ["input_summary", "scoring_details", "routing_decision", "configuration_used"]
                for section in required_sections:
                    if section not in audit_report:
                        validation_errors.append(f"Missing {section} in audit_report")
                
                if validation_errors:
                    dry_run_results[test_name] = {
                        "status": "FAILED",
                        "errors": validation_errors
                    }
                    print(f"    ❌ FAILED: {', '.join(validation_errors)}")
                else:
                    dry_run_results[test_name] = {
                        "status": "PASSED",
                        "audit_sections": list(audit_report.keys())
                    }
                    print(f"    ✅ PASSED (Audit report: {len(audit_report)} sections)")
                
            except Exception as e:
                dry_run_results[test_name] = {
                    "status": "ERROR",
                    "error": str(e)
                }
                print(f"    💥 ERROR: {str(e)}")
        
        return dry_run_results
    
    def _test_error_cases(self) -> Dict[str, Any]:
        """Test error handling and edge cases."""
        
        engine = PromotionGateEngine()
        error_results = {}
        
        # Test configuration validation
        print("  Testing invalid configuration...")
        try:
            # Invalid config - scores don't sum to 100
            invalid_config = ScoringConfig(
                strategic_importance_max=30,  # Sum = 110, invalid
                relationship_delta_strength_max=20,
                commitment_clarity_max=20,
                evidence_quality_max=15,
                novelty_max=15,
                execution_value_max=10
            )
            PromotionGateEngine(invalid_config)
            error_results["invalid_config"] = {
                "status": "FAILED",
                "error": "Should have raised ValueError for invalid config"
            }
        except ValueError as e:
            error_results["invalid_config"] = {
                "status": "PASSED",
                "error_caught": str(e)
            }
            print(f"    ✅ PASSED: Caught expected config error")
        except Exception as e:
            error_results["invalid_config"] = {
                "status": "ERROR",
                "unexpected_error": str(e)
            }
        
        # Test validation error fixtures
        for fixture_name, fixture_data in VALIDATION_ERROR_FIXTURES.items():
            print(f"  Testing {fixture_name}...")
            try:
                # These should either fail gracefully or produce warnings
                scoring_input = create_scoring_input_from_fixture(fixture_name)
                result = engine.process_candidate(scoring_input)
                
                # Check if validation errors were detected
                if "validation_errors" in result or "error" in result:
                    error_results[fixture_name] = {
                        "status": "PASSED",
                        "error_detected": True
                    }
                    print(f"    ✅ PASSED: Error detected and handled")
                else:
                    error_results[fixture_name] = {
                        "status": "WARNING",
                        "message": "No validation errors detected - may need stricter validation"
                    }
                    print(f"    ⚠️  WARNING: Error not detected")
                
            except Exception as e:
                error_results[fixture_name] = {
                    "status": "PASSED",
                    "exception_caught": str(e)
                }
                print(f"    ✅ PASSED: Exception caught: {str(e)[:50]}...")
        
        return error_results
    
    def _print_summary(self, results: Dict[str, Any]):
        """Print test results summary."""
        
        print("\n" + "=" * 60)
        print("🎯 TEST SUMMARY")
        print("=" * 60)
        
        summary = results["summary"]
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed']} ✅")
        print(f"Failed: {summary['failed']} ❌")
        print(f"Errors: {summary['errors']} 💥")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        
        if summary["failed"] > 0:
            print(f"\n⚠️  FAILURES ({summary['failed']}):")
            for failure in results["detailed_results"]["failed"]:
                print(f"  - {failure['test_name']}: {', '.join(failure['errors'])}")
        
        if summary["errors"] > 0:
            print(f"\n💥 ERRORS ({summary['errors']}):")
            for error in results["detailed_results"]["errors"]:
                print(f"  - {error['test_name']}: {error['error']}")
        
        print("\n" + "=" * 60)
    
    def save_results(self, results: Dict[str, Any], output_file: str):
        """Save test results to file."""
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"📁 Results saved to {output_file}")


def main():
    """Main CLI interface for test runner."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Promotion Gate Engine')
    parser.add_argument('--output', type=str, help='Output file for detailed results')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--list', action='store_true', help='List available fixtures')
    parser.add_argument('--fixture', type=str, help='Run specific fixture only')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    
    if args.list:
        fixtures = list_fixtures()
        print("Available test fixtures:")
        for category, fixture_list in fixtures.items():
            print(f"\n{category.upper()}:")
            for fixture in fixture_list:
                print(f"  - {fixture}")
        return
    
    runner = PromotionGateTestRunner()
    
    if args.fixture:
        # Run single fixture
        print(f"Running single fixture: {args.fixture}")
        engine = PromotionGateEngine()
        try:
            scoring_input = create_scoring_input_from_fixture(args.fixture)
            result = engine.process_candidate(scoring_input)
            print(json.dumps(result, indent=2, default=str))
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        # Run full test suite
        results = runner.run_all_tests()
        
        if args.output:
            runner.save_results(results, args.output)
        
        # Exit with error code if tests failed
        if results["summary"]["failed"] > 0 or results["summary"]["errors"] > 0:
            sys.exit(1)


if __name__ == '__main__':
    main()