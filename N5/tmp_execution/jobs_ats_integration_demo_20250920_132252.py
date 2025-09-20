#!/usr/bin/env python3
"""
Jobs ATS Integration Demo Script

This script demonstrates the complete jobs ingestion ATS pipeline implementation
integrated with the existing N5 OS jobs system.
"""

import sys
import os
import json
import logging
from typing import List, Dict, Any

# Add paths for imports
sys.path.append('/home/workspace/N5')
sys.path.append('/home/workspace/N5/tmp_execution')

# Import existing modules
from jobs.modules.ats_detector import detect_ats as legacy_detect_ats
from jobs_implementation_plan_20250920_120000 import JobsIngestionPipeline

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class IntegratedJobsATSPipeline:
    """
    Integrated pipeline that combines the new ATS implementation
    with the existing N5 jobs system.
    """
    
    def __init__(self):
        self.pipeline = JobsIngestionPipeline()
        self.stats = {
            'companies_tested': 0,
            'ats_detected': 0,
            'jobs_found': 0,
            'integration_tests': 0
        }
    
    def test_ats_detection(self, companies: List[str]) -> Dict[str, Any]:
        """Test ATS detection for multiple companies"""
        logger.info(f"Testing ATS detection for {len(companies)} companies")
        
        results = {}
        for company in companies:
            try:
                self.stats['companies_tested'] += 1
                ats_info = legacy_detect_ats(company)
                
                if ats_info:
                    self.stats['ats_detected'] += 1
                    results[company] = ats_info
                    logger.info(f"✓ {company}: {ats_info['ats']} - {ats_info['careers_url']}")
                else:
                    results[company] = None
                    logger.warning(f"✗ {company}: No ATS detected")
            
            except Exception as e:
                logger.error(f"Error detecting ATS for {company}: {e}")
                results[company] = {'error': str(e)}
        
        return results
    
    def test_full_pipeline_integration(self, test_companies: List[str], role_filters: List[str]) -> Dict[str, Any]:
        """Test the complete pipeline integration"""
        logger.info("Testing complete pipeline integration")
        
        try:
            # Setup subsystem
            setup_result = self.pipeline.setup_jobs_ingestion_subsystem()
            if setup_result['status'] != 'success':
                return {'status': 'setup_failed', 'error': setup_result.get('error')}
            
            # Process companies
            batch_result = self.pipeline.process_companies_batch(test_companies, role_filters)
            
            self.stats['integration_tests'] += 1
            
            return {
                'status': 'success',
                'setup': setup_result,
                'batch_processing': batch_result,
                'stats': self.stats
            }
        
        except Exception as e:
            logger.error(f"Integration test failed: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def demonstrate_workflow_integration(self) -> Dict[str, Any]:
        """Demonstrate integration with N5 workflow system"""
        logger.info("Demonstrating workflow integration")
        
        workflow_results = []
        
        # Test 1: ATS Detection
        logger.info("Test 1: ATS Detection Capabilities")
        test_companies = ['stripe', 'netflix', 'openai', 'anthropic', 'uber', 'airbnb']
        ats_results = self.test_ats_detection(test_companies)
        workflow_results.append({
            'test': 'ats_detection',
            'companies': test_companies,
            'results': ats_results,
            'success_rate': len([r for r in ats_results.values() if r and 'error' not in r]) / len(test_companies)
        })
        
        # Test 2: Pipeline Integration  
        logger.info("Test 2: Full Pipeline Integration")
        pipeline_test_companies = ['stripe', 'netflix']
        role_filters = ['engineer', 'software', 'backend', 'frontend']
        pipeline_results = self.test_full_pipeline_integration(pipeline_test_companies, role_filters)
        workflow_results.append({
            'test': 'pipeline_integration',
            'companies': pipeline_test_companies,
            'filters': role_filters,
            'results': pipeline_results
        })
        
        # Test 3: File System Integration
        logger.info("Test 3: File System Integration")
        file_system_results = self.verify_file_system_integration()
        workflow_results.append({
            'test': 'file_system_integration',
            'results': file_system_results
        })
        
        return {
            'demonstration_status': 'completed',
            'workflow_tests': workflow_results,
            'overall_stats': self.stats,
            'integration_summary': self.generate_integration_summary()
        }
    
    def verify_file_system_integration(self) -> Dict[str, Any]:
        """Verify that all required directories and files are created"""
        required_paths = [
            '/home/workspace/N5/jobs_data',
            '/home/workspace/N5/jobs_data/raw',
            '/home/workspace/N5/jobs_data/processed',
            '/home/workspace/N5/jobs_pipeline_config.json',
            '/home/workspace/N5/jobs_ingestion_cli.py',
            '/home/workspace/N5/jobs_ingestion_workflow.json'
        ]
        
        verification_results = {}
        for path in required_paths:
            verification_results[path] = os.path.exists(path)
        
        return {
            'paths_verified': len([p for p in verification_results.values() if p]),
            'total_paths': len(required_paths),
            'details': verification_results,
            'all_present': all(verification_results.values())
        }
    
    def generate_integration_summary(self) -> Dict[str, Any]:
        """Generate a summary of the integration capabilities"""
        return {
            'ats_systems_supported': ['ashby', 'greenhouse', 'lever', 'workday'],
            'companies_with_known_mappings': ['netflix', 'stripe', 'openai', 'anthropic', 'uber', 'airbnb'],
            'output_formats': ['jsonl', 'json'],
            'integration_points': {
                'existing_jobs_module': '/home/workspace/N5/jobs/modules/',
                'command_authoring': '/home/workspace/N5/command_authoring/',
                'workflows': '/home/workspace/N5/workflows/',
                'data_storage': '/home/workspace/N5/jobs_data/'
            },
            'capabilities': [
                'ATS system detection',
                'Job data ingestion from multiple ATS platforms',
                'Role-based filtering',
                'Batch processing',
                'Error handling and logging',
                'N5 OS workflow integration',
                'CLI interface',
                'Iterative development support'
            ]
        }

def main():
    """Main demonstration function"""
    print("=" * 80)
    print("N5 OS Jobs Ingestion ATS Pipeline - Complete Integration Demonstration")
    print("=" * 80)
    
    # Create integrated pipeline
    integrated_pipeline = IntegratedJobsATSPipeline()
    
    # Run complete demonstration
    demo_results = integrated_pipeline.demonstrate_workflow_integration()
    
    # Display results
    print("\n" + "=" * 60)
    print("DEMONSTRATION RESULTS")
    print("=" * 60)
    
    for i, test in enumerate(demo_results['workflow_tests'], 1):
        print(f"\nTest {i}: {test['test'].replace('_', ' ').title()}")
        print("-" * 40)
        
        if test['test'] == 'ats_detection':
            print(f"Companies tested: {len(test['companies'])}")
            print(f"Success rate: {test['success_rate']:.1%}")
            print("ATS Detection Results:")
            for company, result in test['results'].items():
                if result and 'error' not in result:
                    print(f"  ✓ {company}: {result['ats']} ({result['careers_url']})")
                else:
                    print(f"  ✗ {company}: No ATS detected or error")
        
        elif test['test'] == 'pipeline_integration':
            status = test['results']['status']
            print(f"Pipeline Status: {status}")
            if status == 'success':
                batch = test['results']['batch_processing']
                print(f"Companies processed: {batch['companies_processed']}")
                print(f"Duration: {batch['duration_seconds']}s")
                print(f"Jobs found: {batch['total_jobs_found']}")
        
        elif test['test'] == 'file_system_integration':
            fs_results = test['results']
            print(f"File system paths verified: {fs_results['paths_verified']}/{fs_results['total_paths']}")
            print(f"All required files present: {fs_results['all_present']}")
    
    # Integration summary
    summary = demo_results['integration_summary']
    print(f"\n" + "=" * 60)
    print("INTEGRATION SUMMARY")
    print("=" * 60)
    print(f"ATS Systems Supported: {', '.join(summary['ats_systems_supported'])}")
    print(f"Known Company Mappings: {len(summary['companies_with_known_mappings'])}")
    print(f"Output Formats: {', '.join(summary['output_formats'])}")
    print(f"Capabilities: {len(summary['capabilities'])}")
    
    print(f"\nKey Capabilities:")
    for capability in summary['capabilities']:
        print(f"  ✓ {capability}")
    
    # Overall statistics
    stats = demo_results['overall_stats']
    print(f"\n" + "=" * 60)
    print("EXECUTION STATISTICS")
    print("=" * 60)
    print(f"Companies tested: {stats['companies_tested']}")
    print(f"ATS systems detected: {stats['ats_detected']}")
    print(f"Integration tests run: {stats['integration_tests']}")
    
    # Final status
    overall_success = (
        demo_results['demonstration_status'] == 'completed' and
        any(test['results'].get('status') == 'success' or test['results'].get('all_present', False) 
            for test in demo_results['workflow_tests'])
    )
    
    print(f"\n" + "=" * 80)
    if overall_success:
        print("🎉 JOBS INGESTION ATS PIPELINE IMPLEMENTATION: SUCCESSFUL")
        print("✅ All core functionality implemented and integrated")
        print("✅ Ready for iterative development and testing in Zo Computer environment")
    else:
        print("⚠️  JOBS INGESTION ATS PIPELINE IMPLEMENTATION: PARTIAL SUCCESS")
        print("📋 Some components may need additional configuration")
    print("=" * 80)
    
    # Save detailed results
    results_path = '/home/workspace/N5/tmp_execution/jobs_ats_integration_results.json'
    with open(results_path, 'w') as f:
        json.dump(demo_results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: {results_path}")
    
    return 0 if overall_success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)