#!/usr/bin/env python3
"""
Test fixtures for Promotion Gate Engine
Provides edge cases, override scenarios, and validation test cases.
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List
from dataclasses import asdict

import sys
sys.path.append('/home/workspace/N5/schemas')
from validation_helpers import IntelligenceValidator

from promotion_gate_engine import ScoringInput, ScoringConfig, PromotionGateEngine


class PromotionGateTestFixtures:
    """Test fixture generator for promotion gate scenarios."""
    
    def __init__(self):
        self.validator = IntelligenceValidator()
    
    def generate_all_fixtures(self) -> Dict[str, Dict[str, Any]]:
        """Generate all test fixtures organized by category."""
        
        fixtures = {
            'basic_scenarios': self.get_basic_scenarios(),
            'hard_override_scenarios': self.get_hard_override_scenarios(),
            'edge_cases': self.get_edge_cases(),
            'validation_test_cases': self.get_validation_test_cases(),
            'scoring_boundary_tests': self.get_scoring_boundary_tests(),
            'routing_scenarios': self.get_routing_scenarios()
        }
        
        return fixtures
    
    def get_basic_scenarios(self) -> Dict[str, Dict[str, Any]]:
        """Basic scoring scenarios across different tiers."""
        
        scenarios = {}
        
        # Tier A - High scoring relationship delta
        scenarios['tier_a_relationship_delta'] = {
            'input': ScoringInput(
                candidate_type='relationship_delta',
                candidate_data={
                    'delta_id': self.validator.generate_id('rd_'),
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'source_meeting_id': 'meeting_456',
                    'person_id': 'person_123',
                    'delta_type': 'sentiment_shift',
                    'trend': 'increasing',
                    'current_state': {
                        'value': 'very_positive',
                        'confidence': 0.92
                    },
                    'evidence': {
                        'quotes': [
                            {'text': 'This partnership opportunity aligns perfectly with our strategic roadmap', 'speaker': 'CEO Jane Smith'},
                            {'text': 'I support this initiative and will personally help with the implementation', 'speaker': 'CEO Jane Smith'},
                            {'text': 'We need this completed by end of Q1 for our planning cycle', 'speaker': 'CEO Jane Smith'}
                        ],
                        'block_references': ['B03_strategic_alignment', 'B05_commitment_details']
                    },
                    'confidence': 0.92
                },
                source_meeting_id='meeting_456',
                conversation_id='con_test123',
                meeting_context={
                    'participants': [
                        {'name': 'Jane Smith', 'title': 'CEO', 'organization': 'TechCorp'},
                        {'name': 'V', 'title': 'Consultant', 'organization': 'Careerspan'}
                    ]
                },
                existing_memory=[]
            ),
            'expected_tier': 'B',
            'expected_score_range': [65, 75],
            'description': 'High-confidence relationship delta with strategic content and executive involvement'
        }
        
        # Tier B - Medium scoring deliverable
        scenarios['tier_b_deliverable'] = {
            'input': ScoringInput(
                candidate_type='deliverable_record',
                candidate_data={
                    'deliverable_id': self.validator.generate_id('del_'),
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'source_meeting_id': 'meeting_789',
                    'client_id': 'client_456',
                    'deliverable_type': 'analysis',
                    'title': 'Marketing Strategy Analysis',
                    'status': 'identified',
                    'commitment_details': {
                        'commitment_type': 'deliverable_request',
                        'owner': 'V',
                        'requestor': 'Marketing Director'
                    },
                    'evidence': {
                        'quotes': [
                            {'text': 'We would like a comprehensive marketing analysis', 'speaker': 'Marketing Director'}
                        ],
                        'block_references': ['B08_deliverable_request']
                    },
                    'confidence': 0.75
                },
                source_meeting_id='meeting_789',
                conversation_id='con_test456',
                meeting_context={
                    'participants': [
                        {'name': 'Tom Wilson', 'title': 'Marketing Director', 'organization': 'ClientCorp'},
                        {'name': 'V', 'title': 'Consultant', 'organization': 'Careerspan'}
                    ]
                }
            ),
            'expected_tier': 'C',
            'expected_score_range': [35, 50],
            'description': 'Standard deliverable request with moderate clarity'
        }
        
        # Tier C - Low scoring general intelligence  
        scenarios['tier_c_general_info'] = {
            'input': ScoringInput(
                candidate_type='general_intelligence',
                candidate_data={
                    'notes': 'Casual conversation about industry trends',
                    'evidence': {
                        'quotes': [
                            {'text': 'The market seems to be shifting', 'speaker': 'Industry Contact'}
                        ],
                        'block_references': ['B12_general_discussion']
                    },
                    'confidence': 0.45
                },
                source_meeting_id='meeting_321',
                conversation_id='con_test789'
            ),
            'expected_tier': 'C',
            'expected_score_range': [20, 45],
            'description': 'General information with limited strategic value'
        }
        
        # Convert ScoringInput to dict for JSON serialization
        for key, scenario in scenarios.items():
            scenario['input'] = asdict(scenario['input'])
        
        return scenarios
    
    def get_hard_override_scenarios(self) -> Dict[str, Dict[str, Any]]:
        """Test cases for hard override conditions."""
        
        scenarios = {}
        
        # Explicit promise override
        scenarios['explicit_promise_override'] = {
            'input': ScoringInput(
                candidate_type='general_intelligence',
                candidate_data={
                    'notes': 'Low-priority discussion that would normally be Tier C',
                    'evidence': {
                        'quotes': [
                            {'text': 'I promise to get you that contract review by tomorrow', 'speaker': 'Client'},
                            {'text': 'This is a firm commitment from our side', 'speaker': 'Client'}
                        ],
                        'block_references': ['B15_promise_made']
                    },
                    'confidence': 0.4  # Intentionally low to test override
                },
                source_meeting_id='meeting_override_1',
                conversation_id='con_override_test1'
            ),
            'expected_tier': 'A',  # Should be overridden to A
            'expected_override': True,
            'expected_override_reason': 'explicit_promise',
            'description': 'Low-scoring content promoted due to explicit promise'
        }
        
        # Named deliverable override
        scenarios['named_deliverable_override'] = {
            'input': ScoringInput(
                candidate_type='general_intelligence',
                candidate_data={
                    'notes': 'Brief discussion',
                    'evidence': {
                        'quotes': [
                            {'text': 'Can you prepare a comprehensive strategy proposal for our Q2 planning?', 'speaker': 'Client CEO'},
                            {'text': 'We need the full analysis document ready for the board meeting', 'speaker': 'Client CEO'}
                        ],
                        'block_references': ['B20_deliverable_mention']
                    },
                    'confidence': 0.3
                },
                source_meeting_id='meeting_override_2',
                conversation_id='con_override_test2'
            ),
            'expected_tier': 'A',
            'expected_override': True,
            'expected_override_reason': 'named_deliverable',
            'description': 'Generic content promoted due to named deliverable'
        }
        
        # Introduction request override
        scenarios['introduction_request_override'] = {
            'input': ScoringInput(
                candidate_type='general_intelligence',
                candidate_data={
                    'notes': 'Social discussion',
                    'evidence': {
                        'quotes': [
                            {'text': 'Could you introduce me to your contact at TechCorp?', 'speaker': 'Network Contact'},
                            {'text': 'I would really value that connection', 'speaker': 'Network Contact'}
                        ],
                        'block_references': ['B25_intro_request']
                    },
                    'confidence': 0.35
                },
                source_meeting_id='meeting_override_3',
                conversation_id='con_override_test3'
            ),
            'expected_tier': 'A',
            'expected_override': True,
            'expected_override_reason': 'introduction_request',
            'description': 'Casual content promoted due to introduction request'
        }
        
        # Critical deadline override
        scenarios['critical_deadline_override'] = {
            'input': ScoringInput(
                candidate_type='general_intelligence',
                candidate_data={
                    'notes': 'Standard project discussion',
                    'evidence': {
                        'quotes': [
                            {'text': 'This is urgent - we need this immediately for the investor meeting', 'speaker': 'Startup CEO'},
                            {'text': 'This is critical for our funding round', 'speaker': 'Startup CEO'}
                        ],
                        'block_references': ['B30_urgent_request']
                    },
                    'confidence': 0.5
                },
                source_meeting_id='meeting_override_4',
                conversation_id='con_override_test4'
            ),
            'expected_tier': 'A',
            'expected_override': True,
            'expected_override_reason': 'critical_deadline',
            'description': 'Standard content promoted due to critical deadline'
        }
        
        # Convert to dict format
        for key, scenario in scenarios.items():
            scenario['input'] = asdict(scenario['input'])
        
        return scenarios
    
    def get_edge_cases(self) -> Dict[str, Dict[str, Any]]:
        """Edge cases and boundary conditions."""
        
        cases = {}
        
        # Missing evidence
        cases['missing_evidence'] = {
            'input': ScoringInput(
                candidate_type='relationship_delta',
                candidate_data={
                    'delta_id': self.validator.generate_id('rd_'),
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'source_meeting_id': 'meeting_edge_1',
                    'person_id': 'person_edge',
                    'delta_type': 'sentiment_shift',
                    'trend': 'increasing',
                    'current_state': {
                        'value': 'positive',
                        'confidence': 0.8
                    },
                    # No evidence field
                    'confidence': 0.8
                },
                source_meeting_id='meeting_edge_1',
                conversation_id='con_edge_test1'
            ),
            'expected_issues': ['low_evidence_score'],
            'description': 'Candidate with no evidence structure'
        }
        
        # Empty quotes in evidence
        cases['empty_evidence_quotes'] = {
            'input': ScoringInput(
                candidate_type='deliverable_record',
                candidate_data={
                    'deliverable_id': self.validator.generate_id('del_'),
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'source_meeting_id': 'meeting_edge_2',
                    'client_id': 'client_edge',
                    'deliverable_type': 'analysis',
                    'title': 'Market Research',
                    'status': 'identified',
                    'evidence': {
                        'quotes': [],  # Empty quotes
                        'block_references': ['B40_reference']
                    },
                    'confidence': 0.7
                },
                source_meeting_id='meeting_edge_2',
                conversation_id='con_edge_test2'
            ),
            'expected_issues': ['minimal_evidence_score'],
            'description': 'Evidence structure with empty quotes array'
        }
        
        # Boundary tier scores
        cases['tier_boundary_74_point_9'] = {
            'input': ScoringInput(
                candidate_type='org_delta',
                candidate_data={
                    'delta_id': self.validator.generate_id('od_'),
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'source_meeting_id': 'meeting_boundary',
                    'organization_id': 'org_boundary',
                    'delta_type': 'priority_shift',
                    'change_description': 'Moderate priority adjustment in strategic focus areas with some evidence',
                    'impact_scope': 'department_level',
                    'current_state': {
                        'description': 'Adjusted priorities',
                        'confidence': 0.74
                    },
                    'evidence': {
                        'quotes': [
                            {'text': 'We are adjusting our strategic priorities', 'speaker': 'Department Head'},
                            {'text': 'This affects our execution roadmap', 'speaker': 'Department Head'}
                        ],
                        'block_references': ['B45_priority_change']
                    },
                    'confidence': 0.74
                },
                source_meeting_id='meeting_boundary',
                conversation_id='con_boundary_test'
            ),
            'expected_tier': 'B',
            'expected_score_range': [70, 76],
            'description': 'Score right at tier B/A boundary'
        }
        
        # Very high confidence with mediocre content
        cases['high_confidence_mediocre_content'] = {
            'input': ScoringInput(
                candidate_type='general_intelligence',
                candidate_data={
                    'notes': 'Basic information exchange',
                    'evidence': {
                        'quotes': [
                            {'text': 'We discussed the weather and general business conditions', 'speaker': 'Contact'},
                            {'text': 'Business is going well', 'speaker': 'Contact'},
                            {'text': 'We should stay in touch', 'speaker': 'Contact'}
                        ],
                        'block_references': ['B50_general_chat', 'B51_small_talk']
                    },
                    'confidence': 0.95  # Very high confidence, low value content
                },
                source_meeting_id='meeting_confidence_test',
                conversation_id='con_confidence_test'
            ),
            'expected_tier': 'C',
            'description': 'High confidence but low-value content should remain Tier C'
        }
        
        # Convert to dict format
        for key, case in cases.items():
            case['input'] = asdict(case['input'])
        
        return cases
    
    def get_validation_test_cases(self) -> Dict[str, Dict[str, Any]]:
        """Test cases for validation edge cases."""
        
        cases = {}
        
        # Invalid candidate type
        cases['invalid_candidate_type'] = {
            'input': {
                'candidate_type': 'invalid_type',
                'candidate_data': {'id': 'test'},
                'source_meeting_id': 'meeting_val_1',
                'conversation_id': 'con_val_test1'
            },
            'should_fail_validation': True,
            'expected_error_type': 'invalid_candidate_type',
            'description': 'Invalid candidate type should fail validation'
        }
        
        # Missing required fields
        cases['missing_required_fields'] = {
            'input': {
                'candidate_type': 'relationship_delta',
                'candidate_data': {
                    'delta_id': self.validator.generate_id('rd_'),
                    # Missing required fields like person_id, delta_type
                },
                'source_meeting_id': 'meeting_val_2'
                # Missing conversation_id
            },
            'should_fail_validation': True,
            'expected_error_type': 'missing_required_fields',
            'description': 'Missing required fields should fail validation'
        }
        
        # Malformed evidence structure
        cases['malformed_evidence'] = {
            'input': ScoringInput(
                candidate_type='relationship_delta',
                candidate_data={
                    'delta_id': self.validator.generate_id('rd_'),
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'source_meeting_id': 'meeting_val_3',
                    'person_id': 'person_val',
                    'delta_type': 'sentiment_shift',
                    'trend': 'increasing',
                    'current_state': {
                        'value': 'positive',
                        'confidence': 0.7
                    },
                    'evidence': {
                        'quotes': [
                            {'text': 'Quote without speaker'},
                            {'speaker': 'Speaker without text'}
                        ],
                        'block_references': []
                    },
                    'confidence': 0.7
                },
                source_meeting_id='meeting_val_3',
                conversation_id='con_val_test3'
            ),
            'should_fail_validation': True,
            'expected_error_type': 'malformed_evidence',
            'description': 'Malformed evidence structure should be handled gracefully'
        }
        
        # Convert to dict format where needed
        for key, case in cases.items():
            if 'input' in case and not isinstance(case['input'], dict):
                case['input'] = asdict(case['input'])
        
        return cases
    
    def get_scoring_boundary_tests(self) -> Dict[str, Dict[str, Any]]:
        """Test cases for scoring boundary conditions."""
        
        tests = {}
        
        # Maximum possible score
        tests['maximum_score_candidate'] = {
            'input': ScoringInput(
                candidate_type='deliverable_record',
                candidate_data={
                    'deliverable_id': self.validator.generate_id('del_'),
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'source_meeting_id': 'meeting_max_score',
                    'client_id': 'client_max',
                    'deliverable_type': 'strategic_proposal',
                    'title': 'Comprehensive Strategic Partnership and Investment Roadmap Analysis',
                    'status': 'committed',
                    'commitment_details': {
                        'commitment_type': 'firm_commitment',
                        'owner': 'V',
                        'due_date': '2026-03-15',
                        'scope': 'Complete strategic analysis with implementation roadmap',
                        'requestor': 'CEO'
                    },
                    'evidence': {
                        'quotes': [
                            {'text': 'This strategic partnership analysis is critical for our board presentation and investment roadmap decisions', 'speaker': 'CEO Alice Johnson'},
                            {'text': 'We need the comprehensive proposal delivered by March 15th for our strategic planning cycle', 'speaker': 'CEO Alice Johnson'},
                            {'text': 'This analysis will drive our competitive positioning and market expansion strategy', 'speaker': 'CEO Alice Johnson'},
                            {'text': 'I commit to providing all necessary resources and stakeholder access for this deliverable', 'speaker': 'CEO Alice Johnson'}
                        ],
                        'block_references': ['B60_strategic_commitment', 'B61_executive_priority', 'B62_deadline_confirmed']
                    },
                    'confidence': 0.95
                },
                source_meeting_id='meeting_max_score',
                conversation_id='con_max_score_test',
                meeting_context={
                    'participants': [
                        {'name': 'Alice Johnson', 'title': 'CEO', 'organization': 'TechCorp'},
                        {'name': 'Bob Smith', 'title': 'CTO', 'organization': 'TechCorp'},
                        {'name': 'V', 'title': 'Strategic Consultant', 'organization': 'Careerspan'}
                    ]
                },
                existing_memory=[]  # Completely novel
            ),
            'expected_tier': 'A',
            'expected_score_range': [90, 100],
            'description': 'Near-perfect candidate with all scoring elements maximized'
        }
        
        # Minimum possible score
        tests['minimum_score_candidate'] = {
            'input': ScoringInput(
                candidate_type='general_intelligence',
                candidate_data={
                    'notes': 'Brief pleasantries',
                    'confidence': 0.1
                },
                source_meeting_id='meeting_min_score',
                conversation_id='con_min_score_test'
            ),
            'expected_tier': 'C',
            'expected_score_range': [5, 20],
            'description': 'Minimal content with lowest possible scores'
        }
        
        # Score exactly at tier boundaries
        tests['exact_tier_a_boundary'] = {
            'input': ScoringInput(
                candidate_type='deliverable_record',
                candidate_data={
                    'deliverable_id': self.validator.generate_id('del_'),
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'source_meeting_id': 'meeting_tier_boundary',
                    'client_id': 'client_boundary',
                    'deliverable_type': 'report',
                    'title': 'Project Status Report',
                    'status': 'identified',
                    'commitment_details': {
                        'commitment_type': 'deliverable_request',
                        'owner': 'V',
                        'requestor': 'Project Manager'
                    },
                    'evidence': {
                        'quotes': [
                            {'text': 'We need a comprehensive status report for the project', 'speaker': 'Project Manager'},
                            {'text': 'This should include strategic recommendations for next phase', 'speaker': 'Project Manager'}
                        ],
                        'block_references': ['B65_status_request']
                    },
                    'confidence': 0.75
                },
                source_meeting_id='meeting_tier_boundary',
                conversation_id='con_tier_boundary_test',
                meeting_context={
                    'participants': [
                        {'name': 'Jane Doe', 'title': 'Project Manager', 'organization': 'ClientCorp'},
                        {'name': 'V', 'title': 'Consultant', 'organization': 'Careerspan'}
                    ]
                }
            ),
            'expected_tier': 'A',
            'target_score': 75,  # Exactly at boundary
            'description': 'Candidate designed to score exactly at Tier A boundary (75)'
        }
        
        # Convert to dict format
        for key, test in tests.items():
            test['input'] = asdict(test['input'])
        
        return tests
    
    def get_routing_scenarios(self) -> Dict[str, Dict[str, Any]]:
        """Test cases for different routing scenarios."""
        
        scenarios = {}
        
        # Tier A routing - all systems
        scenarios['tier_a_full_routing'] = {
            'input': ScoringInput(
                candidate_type='relationship_delta',
                candidate_data={
                    'delta_id': self.validator.generate_id('rd_'),
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'source_meeting_id': 'meeting_routing_a',
                    'person_id': 'person_routing',
                    'delta_type': 'sentiment_shift',
                    'trend': 'increasing',
                    'current_state': {
                        'value': 'very_positive',
                        'confidence': 0.9
                    },
                    'evidence': {
                        'quotes': [
                            {'text': 'This partnership is exactly what we need for our strategic growth', 'speaker': 'CEO Partner'},
                            {'text': 'I am personally committed to making this successful', 'speaker': 'CEO Partner'}
                        ],
                        'block_references': ['B70_strategic_alignment']
                    },
                    'confidence': 0.9
                },
                source_meeting_id='meeting_routing_a',
                conversation_id='con_routing_test_a'
            ),
            'expected_tier': 'A',
            'expected_routing': {
                'semantic_memory': True,
                'graph_edges': True,
                'crm_projection': True,
                'deliverables_db': True  # Relationship delta affects all systems
            },
            'expected_status': 'promoted',
            'description': 'Tier A candidate should route to all systems'
        }
        
        # Tier B selective routing
        scenarios['tier_b_selective_routing'] = {
            'input': ScoringInput(
                candidate_type='intro_opportunity',
                candidate_data={
                    'opportunity_id': self.validator.generate_id('io_'),
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'source_meeting_id': 'meeting_routing_b',
                    'introducer_id': 'person_v',
                    'introducee_a': {
                        'person_id': 'person_a',
                        'name': 'Alice Brown',
                        'title': 'VP Sales',
                        'organization': 'SalesCorp'
                    },
                    'introducee_b': {
                        'person_id': 'person_b',
                        'name': 'Bob Green',
                        'title': 'Head of Partnerships',
                        'organization': 'PartnerCorp'
                    },
                    'opportunity_type': 'business_collaboration',
                    'mutual_value': {
                        'value_to_a': 'Access to new customer segments',
                        'value_to_b': 'Partnership opportunity',
                        'shared_benefits': 'Market expansion'
                    },
                    'evidence': {
                        'quotes': [
                            {'text': 'We are looking for partnership opportunities in this space', 'speaker': 'Bob Green'}
                        ],
                        'block_references': ['B75_intro_context']
                    },
                    'priority': 'medium',
                    'status': 'identified',
                    'confidence': 0.65
                },
                source_meeting_id='meeting_routing_b',
                conversation_id='con_routing_test_b'
            ),
            'expected_tier': 'B',
            'expected_routing': {
                'semantic_memory': False,  # B tier doesn't go to semantic memory
                'graph_edges': True,
                'crm_projection': True,
                'deliverables_db': False  # Intro opportunities don't need deliverables DB
            },
            'expected_status': 'queued_for_review',
            'description': 'Tier B intro opportunity should have selective routing'
        }
        
        # Tier C minimal routing
        scenarios['tier_c_minimal_routing'] = {
            'input': ScoringInput(
                candidate_type='general_intelligence',
                candidate_data={
                    'notes': 'General discussion about market trends',
                    'evidence': {
                        'quotes': [
                            {'text': 'The market is doing well overall', 'speaker': 'Industry Contact'}
                        ],
                        'block_references': ['B80_general_chat']
                    },
                    'confidence': 0.4
                },
                source_meeting_id='meeting_routing_c',
                conversation_id='con_routing_test_c'
            ),
            'expected_tier': 'C',
            'expected_routing': {
                'semantic_memory': False,
                'graph_edges': False,
                'crm_projection': False,
                'deliverables_db': False
            },
            'expected_status': 'archived',
            'description': 'Tier C candidate should not route to any systems'
        }
        
        # Convert to dict format
        for key, scenario in scenarios.items():
            scenario['input'] = asdict(scenario['input'])
        
        return scenarios
    
    def save_fixtures_to_files(self, output_dir: str = '/home/workspace/N5/builds/relationship-intelligence-os/artifacts/test_fixtures/'):
        """Save all fixtures to organized JSON files."""
        
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        fixtures = self.generate_all_fixtures()
        
        for category, category_fixtures in fixtures.items():
            output_file = os.path.join(output_dir, f"{category}.json")
            
            with open(output_file, 'w') as f:
                json.dump(category_fixtures, f, indent=2, default=str)
            
            print(f"Saved {len(category_fixtures)} fixtures to {output_file}")
        
        # Save a combined index file
        index_file = os.path.join(output_dir, "fixture_index.json")
        
        index = {
            'categories': list(fixtures.keys()),
            'total_fixtures': sum(len(cat) for cat in fixtures.values()),
            'descriptions': {
                'basic_scenarios': 'Standard scoring scenarios across different tiers',
                'hard_override_scenarios': 'Test cases for hard override conditions',
                'edge_cases': 'Edge cases and boundary conditions',
                'validation_test_cases': 'Test cases for validation edge cases',
                'scoring_boundary_tests': 'Test cases for scoring boundary conditions',
                'routing_scenarios': 'Test cases for different routing scenarios'
            },
            'generated_at': datetime.now(timezone.utc).isoformat()
        }
        
        with open(index_file, 'w') as f:
            json.dump(index, f, indent=2)
        
        print(f"Saved fixture index to {index_file}")


def create_sample_config() -> Dict[str, Any]:
    """Create a sample configuration for testing."""
    
    config = ScoringConfig()
    return {
        'tier_a_threshold': config.tier_a_threshold,
        'tier_b_threshold': config.tier_b_threshold, 
        'tier_c_threshold': config.tier_c_threshold,
        'strategic_importance_max': config.strategic_importance_max,
        'relationship_delta_strength_max': config.relationship_delta_strength_max,
        'commitment_clarity_max': config.commitment_clarity_max,
        'evidence_quality_max': config.evidence_quality_max,
        'novelty_max': config.novelty_max,
        'execution_value_max': config.execution_value_max,
        'hard_override_keywords': config.hard_override_keywords,
        'routing_rules': config.routing_rules
    }


def run_fixture_validation_tests():
    """Run validation tests on all fixtures to ensure they work correctly."""
    
    fixtures_gen = PromotionGateTestFixtures()
    engine = PromotionGateEngine()
    
    all_fixtures = fixtures_gen.generate_all_fixtures()
    
    results = {
        'total_tests': 0,
        'passed_tests': 0,
        'failed_tests': 0,
        'failures': []
    }
    
    for category_name, category_fixtures in all_fixtures.items():
        print(f"\nTesting {category_name}:")
        
        for fixture_name, fixture_data in category_fixtures.items():
            results['total_tests'] += 1
            
            try:
                # Convert dict back to ScoringInput if needed
                if isinstance(fixture_data['input'], dict):
                    input_data = ScoringInput(**fixture_data['input'])
                else:
                    input_data = fixture_data['input']
                
                # Process the candidate
                result = engine.process_candidate(input_data, dry_run=True)
                
                # Check if processing succeeded
                if 'error' in result:
                    results['failed_tests'] += 1
                    results['failures'].append({
                        'category': category_name,
                        'fixture': fixture_name,
                        'error': result['error'],
                        'type': 'processing_error'
                    })
                    print(f"  ✗ {fixture_name}: Processing error - {result['error']}")
                    continue
                
                # Validate expected outcomes where specified
                passed = True
                
                if 'expected_tier' in fixture_data:
                    actual_tier = result.get('tier')
                    expected_tier = fixture_data['expected_tier']
                    
                    if actual_tier != expected_tier:
                        passed = False
                        results['failures'].append({
                            'category': category_name,
                            'fixture': fixture_name,
                            'expected': expected_tier,
                            'actual': actual_tier,
                            'type': 'tier_mismatch'
                        })
                
                if 'expected_score_range' in fixture_data:
                    actual_score = result.get('score', 0)
                    min_score, max_score = fixture_data['expected_score_range']
                    
                    if not (min_score <= actual_score <= max_score):
                        passed = False
                        results['failures'].append({
                            'category': category_name,
                            'fixture': fixture_name,
                            'expected_range': fixture_data['expected_score_range'],
                            'actual_score': actual_score,
                            'type': 'score_range_mismatch'
                        })
                
                if 'expected_override' in fixture_data:
                    hard_override = result.get('hard_override', {})
                    expected_override = fixture_data['expected_override']
                    actual_override = hard_override.get('applied', False)
                    
                    if actual_override != expected_override:
                        passed = False
                        results['failures'].append({
                            'category': category_name,
                            'fixture': fixture_name,
                            'expected_override': expected_override,
                            'actual_override': actual_override,
                            'type': 'override_mismatch'
                        })
                
                if passed:
                    results['passed_tests'] += 1
                    print(f"  ✓ {fixture_name}")
                else:
                    results['failed_tests'] += 1
                    print(f"  ✗ {fixture_name}: Validation failed")
            
            except Exception as e:
                results['failed_tests'] += 1
                results['failures'].append({
                    'category': category_name,
                    'fixture': fixture_name,
                    'error': str(e),
                    'type': 'exception'
                })
                print(f"  ✗ {fixture_name}: Exception - {str(e)}")
    
    # Print summary
    print(f"\n=== TEST RESULTS ===")
    print(f"Total tests: {results['total_tests']}")
    print(f"Passed: {results['passed_tests']}")
    print(f"Failed: {results['failed_tests']}")
    print(f"Success rate: {results['passed_tests']/results['total_tests']*100:.1f}%")
    
    if results['failures']:
        print(f"\n=== FAILURES ===")
        for failure in results['failures'][:5]:  # Show first 5 failures
            print(f"- {failure['category']}/{failure['fixture']}: {failure['type']}")
            if 'error' in failure:
                print(f"  Error: {failure['error']}")
    
    return results


if __name__ == '__main__':
    # Generate and save all test fixtures
    fixtures_gen = PromotionGateTestFixtures()
    fixtures_gen.save_fixtures_to_files()
    
    # Save sample configuration
    sample_config = create_sample_config()
    config_file = '/home/workspace/N5/builds/relationship-intelligence-os/artifacts/sample_config.json'
    
    with open(config_file, 'w') as f:
        json.dump(sample_config, f, indent=2)
    
    print(f"Saved sample configuration to {config_file}")
    
    # Run validation tests
    print("\n" + "="*50)
    print("RUNNING FIXTURE VALIDATION TESTS")
    print("="*50)
    
    test_results = run_fixture_validation_tests()