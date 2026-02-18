#!/usr/bin/env python3
"""
Test fixtures for Promotion Gate Engine
Contains edge cases, hard override scenarios, and validation test data.
"""

import json
from datetime import datetime, timezone
from typing import Dict, Any, List

# Test fixtures for various edge cases and scenarios
TEST_FIXTURES = {
    
    # Standard cases for each tier
    "tier_A_strategic_deliverable": {
        "candidate_type": "deliverable_record",
        "candidate_data": {
            "id": "del_test001",
            "deliverable_type": "strategic_analysis",
            "status": "committed",
            "commitment_details": {
                "promised_by": "John Smith",
                "deadline": "2026-03-01",
                "deliverable": "Complete market analysis report for Q1 strategy"
            },
            "evidence": {
                "quotes": [
                    "I'll have the strategic analysis ready by March 1st",
                    "This will guide our Q1 priorities and investment decisions"
                ],
                "context_windows": ["market_discussion", "strategic_planning"]
            },
            "confidence": 0.9
        },
        "source_meeting_id": "meet_12345",
        "meeting_context": {
            "participants": [
                {"name": "John Smith", "title": "VP Strategy"},
                {"name": "Sarah Johnson", "title": "CEO"}
            ],
            "meeting_type": "strategic_planning"
        },
        "conversation_id": "con_test001",
        "expected_tier": "A",
        "expected_score_range": [75, 95]
    },
    
    "tier_B_relationship_delta": {
        "candidate_type": "relationship_delta",
        "candidate_data": {
            "id": "rd_test002",
            "delta_type": "sentiment_shift",
            "old_state": {"sentiment": "neutral", "trust_level": "medium"},
            "new_state": {"sentiment": "positive", "trust_level": "high"},
            "confidence": 0.7,
            "evidence": {
                "quotes": ["I'm really impressed with the progress we've made"],
                "behavioral_changes": ["More proactive communication"]
            }
        },
        "source_meeting_id": "meet_12346",
        "conversation_id": "con_test002", 
        "expected_tier": "B",
        "expected_score_range": [50, 74]
    },
    
    "tier_C_low_confidence_general": {
        "candidate_type": "general_intelligence",
        "candidate_data": {
            "id": "gi_test003",
            "content": "Brief mention of potential project",
            "confidence": 0.3,
            "evidence": {
                "quotes": ["Maybe we should look into that sometime"],
                "context_windows": ["casual_discussion"]
            }
        },
        "source_meeting_id": "meet_12347",
        "conversation_id": "con_test003",
        "expected_tier": "C",
        "expected_score_range": [0, 49]
    },
    
    # Hard override test cases
    "hard_override_explicit_promise": {
        "candidate_type": "general_intelligence",
        "candidate_data": {
            "id": "gi_override001",
            "content": "I promise to deliver the initial proposal by Friday",
            "confidence": 0.4,
            "evidence": {
                "quotes": ["I promise to deliver the initial proposal by Friday"],
                "context_windows": ["commitment_discussion"]
            }
        },
        "source_meeting_id": "meet_override001",
        "conversation_id": "con_override001",
        "expected_tier": "A",  # Overridden to A
        "expected_override": {
            "applied": True,
            "reason": "explicit_promise",
            "trigger_keyword": "promise"
        }
    },
    
    "hard_override_critical_deadline": {
        "candidate_type": "org_delta",
        "candidate_data": {
            "id": "od_override002", 
            "delta_type": "priority_change",
            "old_state": {"priority": "medium"},
            "new_state": {"priority": "urgent"},
            "confidence": 0.6,
            "evidence": {
                "quotes": ["This is urgent - we need to address it immediately"],
                "context_windows": ["escalation_discussion"]
            }
        },
        "source_meeting_id": "meet_override002",
        "conversation_id": "con_override002",
        "expected_tier": "A",  # Overridden to A
        "expected_override": {
            "applied": True,
            "reason": "critical_deadline",
            "trigger_keyword": "urgent"
        }
    },
    
    "hard_override_introduction_request": {
        "candidate_type": "intro_opportunity",
        "candidate_data": {
            "id": "io_override003",
            "introducer": "Alice Cooper",
            "introducee": "Bob Wilson",
            "target_person": "Charlie Brown",
            "reason": "Business partnership opportunity",
            "priority": "medium",
            "recommended_approach": "I'd like you to introduce me to Charlie - we should connect on this partnership",
            "confidence": 0.8
        },
        "source_meeting_id": "meet_override003",
        "conversation_id": "con_override003",
        "expected_tier": "A",  # Overridden to A
        "expected_override": {
            "applied": True,
            "reason": "introduction_request",
            "trigger_keyword": "introduce"
        }
    },
    
    # Edge cases
    "edge_case_zero_evidence": {
        "candidate_type": "relationship_delta",
        "candidate_data": {
            "id": "rd_edge001",
            "delta_type": "communication_pattern_change",
            "old_state": {"frequency": "weekly"},
            "new_state": {"frequency": "daily"},
            "confidence": 0.5,
            "evidence": {
                "quotes": [],  # No quotes
                "behavioral_changes": []  # No behavioral evidence
            }
        },
        "source_meeting_id": "meet_edge001",
        "conversation_id": "con_edge001",
        "expected_tier": "C",  # Low score due to lack of evidence
        "expected_score_range": [0, 35]
    },
    
    "edge_case_boundary_score_74": {
        "candidate_type": "deliverable_record",
        "candidate_data": {
            "id": "del_boundary001",
            "deliverable_type": "analysis",
            "status": "identified",
            "commitment_details": {
                "promised_by": "Team Lead",
                "deliverable": "Basic analysis document"
            },
            "evidence": {
                "quotes": ["We'll put together an analysis"],
                "context_windows": ["planning_discussion"]
            },
            "confidence": 0.6
        },
        "source_meeting_id": "meet_boundary001",
        "conversation_id": "con_boundary001",
        "expected_tier": "B",  # Should be right at tier B boundary
        "expected_score_range": [72, 76]
    },
    
    "edge_case_multiple_override_triggers": {
        "candidate_type": "general_intelligence",
        "candidate_data": {
            "id": "gi_multi001",
            "content": "This is urgent - I promise to deliver the critical presentation to stakeholders immediately",
            "confidence": 0.5,
            "evidence": {
                "quotes": ["This is urgent - I promise to deliver the critical presentation to stakeholders immediately"],
                "context_windows": ["crisis_management"]
            }
        },
        "source_meeting_id": "meet_multi001",
        "conversation_id": "con_multi001",
        "expected_tier": "A",  # Should trigger on first match
        "expected_override": {
            "applied": True,
            "reason": "explicit_promise",  # Should match on 'promise' first
            "trigger_keyword": "promise"
        }
    },
    
    # Complex routing test cases
    "complex_routing_deliverable_with_relationships": {
        "candidate_type": "deliverable_record",
        "candidate_data": {
            "id": "del_complex001",
            "deliverable_type": "partnership_proposal",
            "status": "committed",
            "commitment_details": {
                "promised_by": "Partnership Manager",
                "deadline": "2026-02-28",
                "deliverable": "Strategic partnership proposal with trust-building components"
            },
            "evidence": {
                "quotes": [
                    "I'll draft the partnership proposal focusing on relationship building",
                    "This will strengthen our collaborative approach"
                ],
                "context_windows": ["partnership_strategy", "relationship_building"]
            },
            "confidence": 0.85
        },
        "source_meeting_id": "meet_complex001",
        "conversation_id": "con_complex001",
        "expected_tier": "A",
        "expected_routing": {
            "semantic_memory": True,
            "graph_edges": True,
            "crm_projection": True,
            "deliverables_db": True
        }
    }
}

# Configuration test fixtures
CONFIG_TEST_FIXTURES = {
    "default_config": {
        "tier_a_threshold": 75,
        "tier_b_threshold": 50,
        "tier_c_threshold": 0,
        "strategic_importance_max": 20,
        "relationship_delta_strength_max": 20,
        "commitment_clarity_max": 20,
        "evidence_quality_max": 15,
        "novelty_max": 15,
        "execution_value_max": 10
    },
    
    "strict_config": {
        "tier_a_threshold": 85,
        "tier_b_threshold": 65,
        "tier_c_threshold": 0,
        "strategic_importance_max": 25,
        "relationship_delta_strength_max": 25,
        "commitment_clarity_max": 15,
        "evidence_quality_max": 15,
        "novelty_max": 10,
        "execution_value_max": 10
    },
    
    "lenient_config": {
        "tier_a_threshold": 60,
        "tier_b_threshold": 30,
        "tier_c_threshold": 0,
        "strategic_importance_max": 15,
        "relationship_delta_strength_max": 15,
        "commitment_clarity_max": 25,
        "evidence_quality_max": 20,
        "novelty_max": 15,
        "execution_value_max": 10
    }
}

# Validation error test cases
VALIDATION_ERROR_FIXTURES = {
    "invalid_candidate_type": {
        "candidate_type": "invalid_type",
        "candidate_data": {"id": "test001"},
        "source_meeting_id": "meet_001",
        "conversation_id": "con_001",
        "expected_error": "Invalid candidate type"
    },
    
    "missing_required_fields": {
        "candidate_type": "deliverable_record",
        "candidate_data": {
            "id": "del_missing001"
            # Missing required fields like status, deliverable_type
        },
        "source_meeting_id": "meet_missing001",
        "conversation_id": "con_missing001",
        "expected_error": "Missing required fields"
    },
    
    "invalid_confidence_range": {
        "candidate_type": "relationship_delta",
        "candidate_data": {
            "id": "rd_invalid001",
            "delta_type": "sentiment_shift",
            "confidence": 1.5,  # Invalid - should be 0-1
            "evidence": {"quotes": ["test"]}
        },
        "source_meeting_id": "meet_invalid001",
        "conversation_id": "con_invalid001",
        "expected_error": "Invalid confidence value"
    }
}


def get_test_fixture(fixture_name: str) -> Dict[str, Any]:
    """Get a specific test fixture by name."""
    if fixture_name in TEST_FIXTURES:
        return TEST_FIXTURES[fixture_name].copy()
    elif fixture_name in CONFIG_TEST_FIXTURES:
        return CONFIG_TEST_FIXTURES[fixture_name].copy()
    elif fixture_name in VALIDATION_ERROR_FIXTURES:
        return VALIDATION_ERROR_FIXTURES[fixture_name].copy()
    else:
        raise ValueError(f"Unknown fixture: {fixture_name}")


def list_fixtures() -> Dict[str, List[str]]:
    """List all available test fixtures by category."""
    return {
        "test_cases": list(TEST_FIXTURES.keys()),
        "config_cases": list(CONFIG_TEST_FIXTURES.keys()),
        "validation_errors": list(VALIDATION_ERROR_FIXTURES.keys())
    }


def create_scoring_input_from_fixture(fixture_name: str) -> 'ScoringInput':
    """Create a ScoringInput object from a test fixture."""
    from promotion_gate_engine import ScoringInput
    
    fixture = get_test_fixture(fixture_name)
    
    return ScoringInput(
        candidate_type=fixture["candidate_type"],
        candidate_data=fixture["candidate_data"],
        source_meeting_id=fixture["source_meeting_id"],
        meeting_context=fixture.get("meeting_context"),
        existing_memory=fixture.get("existing_memory"),
        relationships=fixture.get("relationships"),
        conversation_id=fixture.get("conversation_id", ""),
        processing_mode=fixture.get("processing_mode", "test"),
        source_blocks=fixture.get("source_blocks", [])
    )


def validate_fixture_expectations(fixture_name: str, result: Dict[str, Any]) -> List[str]:
    """Validate that a processing result meets the fixture's expectations."""
    fixture = get_test_fixture(fixture_name)
    errors = []
    
    # Check expected tier
    expected_tier = fixture.get("expected_tier")
    if expected_tier and result.get("tier") != expected_tier:
        errors.append(f"Expected tier {expected_tier}, got {result.get('tier')}")
    
    # Check expected score range
    expected_range = fixture.get("expected_score_range")
    if expected_range:
        score = result.get("score", 0)
        if not (expected_range[0] <= score <= expected_range[1]):
            errors.append(f"Score {score} not in expected range {expected_range}")
    
    # Check expected override
    expected_override = fixture.get("expected_override")
    if expected_override:
        result_override = result.get("hard_override", {})
        if result_override.get("applied") != expected_override["applied"]:
            errors.append(f"Expected override applied={expected_override['applied']}, got {result_override.get('applied')}")
        
        if expected_override["applied"] and result_override.get("reason") != expected_override["reason"]:
            errors.append(f"Expected override reason {expected_override['reason']}, got {result_override.get('reason')}")
    
    # Check expected routing
    expected_routing = fixture.get("expected_routing")
    if expected_routing:
        result_routing = result.get("routing", {})
        for target, expected_value in expected_routing.items():
            if result_routing.get(target) != expected_value:
                errors.append(f"Expected routing.{target}={expected_value}, got {result_routing.get(target)}")
    
    return errors


if __name__ == '__main__':
    # Print available fixtures for reference
    fixtures = list_fixtures()
    print("Available test fixtures:")
    for category, fixture_list in fixtures.items():
        print(f"\n{category.upper()}:")
        for fixture in fixture_list:
            print(f"  - {fixture}")