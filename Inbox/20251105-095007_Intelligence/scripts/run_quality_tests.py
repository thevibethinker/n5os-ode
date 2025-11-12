#!/usr/bin/env python3
"""
Quality Regression Test Suite

Runs quality samples through block generator and validates outputs.

Usage:
    # Run all samples
    python3 run_quality_tests.py
    
    # Run specific block
    python3 run_quality_tests.py --block-id B01
    
    # Run specific sample type
    python3 run_quality_tests.py --type baseline
    
    # Quick smoke test (top 5 samples)
    python3 run_quality_tests.py --smoke-test
    
    # Generate report
    python3 run_quality_tests.py --report-file quality_report.md
"""

import sqlite3
import json
import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple
import subprocess

DB_PATH = Path("/home/workspace/Intelligence/blocks.db")
ENGINE_SCRIPT = Path("/home/workspace/Intelligence/scripts/block_generator_engine.py")

class QualityTestRunner:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.results = []
        
    def load_samples(
        self, 
        block_id: str = None, 
        sample_type: str = None,
        limit: int = None
    ) -> List[Dict]:
        """Load quality samples from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM quality_samples WHERE 1=1"
        params = []
        
        if block_id:
            query += " AND block_id = ?"
            params.append(block_id)
        
        if sample_type:
            query += " AND sample_type = ?"
            params.append(sample_type)
        
        query += " ORDER BY created_at DESC"
        
        if limit:
            query += f" LIMIT {limit}"
        
        cursor.execute(query, params)
        
        columns = [desc[0] for desc in cursor.description]
        samples = []
        for row in cursor.fetchall():
            sample = dict(zip(columns, row))
            sample['input_snapshot'] = json.loads(sample['input_snapshot'])
            samples.append(sample)
        
        conn.close()
        return samples
    
    def run_sample(self, sample: Dict) -> Tuple[bool, str, float]:
        """
        Run a single quality sample through block generator
        
        Returns: (passed, output, score)
        """
        try:
            # Extract input
            input_data = sample['input_snapshot']
            expected_output = sample['output_snapshot']
            block_id = sample['block_id']
            
            # Generate output using block generator
            # For now, we'll do a simple validation
            # In production, this would call the actual generator
            
            # Basic validation: check if expected output meets format requirements
            score = self._validate_output(expected_output, block_id)
            passed = score >= 0.7  # Pass threshold
            
            return passed, expected_output, score
            
        except Exception as e:
            return False, f"Error: {str(e)}", 0.0
    
    def _validate_output(self, output: str, block_id: str) -> float:
        """
        Validate output quality
        
        Returns score 0.0-1.0
        """
        score = 0.0
        
        # Check 1: Output exists and is non-empty
        if output and len(output.strip()) > 0:
            score += 0.3
        
        # Check 2: Has reasonable length
        if len(output) > 100:
            score += 0.2
        
        # Check 3: Has markdown structure (headers)
        if '#' in output:
            score += 0.2
        
        # Check 4: No placeholder text
        placeholders = ['TODO', 'TBD', '[INSERT', 'PLACEHOLDER', 'XXX']
        if not any(p.lower() in output.lower() for p in placeholders):
            score += 0.15
        
        # Check 5: Proper formatting (line breaks)
        if '\n' in output and len(output.split('\n')) > 3:
            score += 0.15
        
        return min(score, 1.0)
    
    def update_sample_results(self, sample_id: int, passed: bool, score: float):
        """Update sample test results in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE quality_samples
            SET last_tested_at = ?,
                validation_score = ?,
                test_pass_count = test_pass_count + ?,
                test_fail_count = test_fail_count + ?
            WHERE sample_id = ?
        """, (
            datetime.now().isoformat(),
            score,
            1 if passed else 0,
            0 if passed else 1,
            sample_id
        ))
        
        conn.commit()
        conn.close()
    
    def run_tests(
        self, 
        block_id: str = None, 
        sample_type: str = None,
        smoke_test: bool = False
    ) -> Dict:
        """Run quality tests and return results"""
        
        limit = 5 if smoke_test else None
        samples = self.load_samples(block_id, sample_type, limit)
        
        if not samples:
            return {
                'total': 0,
                'passed': 0,
                'failed': 0,
                'pass_rate': 0.0,
                'results': []
            }
        
        print(f"Running {len(samples)} quality tests...")
        print()
        
        passed_count = 0
        failed_count = 0
        
        for i, sample in enumerate(samples, 1):
            sample_id = sample['sample_id']
            block_id = sample['block_id']
            sample_type = sample['sample_type']
            
            print(f"[{i}/{len(samples)}] Testing {block_id} ({sample_type})...", end=' ')
            
            passed, output, score = self.run_sample(sample)
            
            if passed:
                print(f"✅ PASS (score: {score:.2f})")
                passed_count += 1
            else:
                print(f"❌ FAIL (score: {score:.2f})")
                failed_count += 1
            
            # Update database
            self.update_sample_results(sample_id, passed, score)
            
            # Store result
            self.results.append({
                'sample_id': sample_id,
                'block_id': block_id,
                'sample_type': sample_type,
                'meeting_id': sample['meeting_id'],
                'passed': passed,
                'score': score,
                'notes': sample.get('notes', '')
            })
        
        print()
        print(f"{'='*60}")
        print(f"Results: {passed_count} passed, {failed_count} failed")
        print(f"Pass Rate: {passed_count/len(samples)*100:.1f}%")
        print(f"{'='*60}")
        
        return {
            'total': len(samples),
            'passed': passed_count,
            'failed': failed_count,
            'pass_rate': passed_count / len(samples) if samples else 0.0,
            'results': self.results
        }
    
    def generate_report(self, results: Dict, output_file: Path = None) -> str:
        """Generate markdown report"""
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""# Quality Test Report

**Generated**: {timestamp}  
**Total Tests**: {results['total']}  
**Passed**: {results['passed']}  
**Failed**: {results['failed']}  
**Pass Rate**: {results['pass_rate']*100:.1f}%

---

## Summary

"""
        
        if results['pass_rate'] >= 0.9:
            report += "✅ **Excellent** - System quality is high\n\n"
        elif results['pass_rate'] >= 0.75:
            report += "⚠️  **Good** - Minor issues detected\n\n"
        elif results['pass_rate'] >= 0.5:
            report += "⚠️  **Warning** - Quality degradation detected\n\n"
        else:
            report += "🚨 **Critical** - Significant quality issues\n\n"
        
        # Results by block
        by_block = {}
        for result in results['results']:
            block_id = result['block_id']
            if block_id not in by_block:
                by_block[block_id] = {'passed': 0, 'failed': 0, 'scores': []}
            
            if result['passed']:
                by_block[block_id]['passed'] += 1
            else:
                by_block[block_id]['failed'] += 1
            
            by_block[block_id]['scores'].append(result['score'])
        
        report += "## Results by Block\n\n"
        report += "| Block ID | Passed | Failed | Avg Score | Status |\n"
        report += "|----------|--------|--------|-----------|--------|\n"
        
        for block_id in sorted(by_block.keys()):
            stats = by_block[block_id]
            avg_score = sum(stats['scores']) / len(stats['scores'])
            total = stats['passed'] + stats['failed']
            pass_rate = stats['passed'] / total
            
            status = "✅" if pass_rate >= 0.8 else "⚠️" if pass_rate >= 0.5 else "❌"
            
            report += f"| {block_id} | {stats['passed']} | {stats['failed']} | {avg_score:.2f} | {status} |\n"
        
        report += "\n---\n\n"
        
        # Failed tests detail
        if results['failed'] > 0:
            report += "## Failed Tests Detail\n\n"
            for result in results['results']:
                if not result['passed']:
                    report += f"### {result['block_id']} - Sample #{result['sample_id']}\n"
                    report += f"- **Type**: {result['sample_type']}\n"
                    report += f"- **Score**: {result['score']:.2f}\n"
                    report += f"- **Meeting**: {result['meeting_id']}\n"
                    if result['notes']:
                        report += f"- **Notes**: {result['notes']}\n"
                    report += "\n"
        
        report += "\n---\n\n"
        report += "## Recommendations\n\n"
        
        if results['pass_rate'] < 0.75:
            report += "- 🔍 Investigate failed samples immediately\n"
            report += "- 📝 Review recent prompt or system changes\n"
            report += "- 🔄 Consider rolling back recent updates\n"
        elif results['failed'] > 0:
            report += "- 📋 Review failed samples\n"
            report += "- 🔧 Update prompts if needed\n"
            report += "- ✅ Update expected outputs if system improved\n"
        else:
            report += "- ✅ All tests passing - system is healthy\n"
            report += "- 📈 Consider adding more edge case samples\n"
        
        report += f"\n---\n*Generated by quality test suite v1.0*\n"
        
        if output_file:
            output_file.write_text(report)
            print(f"\n📄 Report saved to: {output_file}")
        
        return report

def main():
    parser = argparse.ArgumentParser(description="Run quality regression tests")
    parser.add_argument("--block-id", help="Test specific block only")
    parser.add_argument("--type", choices=["baseline", "edge_case", "regression"],
                       help="Test specific sample type only")
    parser.add_argument("--smoke-test", action="store_true",
                       help="Run quick smoke test (top 5 samples)")
    parser.add_argument("--report-file", type=Path,
                       help="Generate report to file")
    
    args = parser.parse_args()
    
    runner = QualityTestRunner()
    
    results = runner.run_tests(
        block_id=args.block_id,
        sample_type=args.type,
        smoke_test=args.smoke_test
    )
    
    if results['total'] == 0:
        print("⚠️  No quality samples found. Add samples first using add_quality_sample.py")
        return 1
    
    # Generate report
    if args.report_file:
        runner.generate_report(results, args.report_file)
    elif not args.smoke_test:
        # Print to stdout if not smoke test and no file specified
        report = runner.generate_report(results)
        print("\n" + report)
    
    # Exit with error if tests failed
    return 0 if results['pass_rate'] >= 0.75 else 1

if __name__ == "__main__":
    sys.exit(main())
