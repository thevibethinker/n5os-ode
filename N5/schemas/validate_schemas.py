#!/usr/bin/env python3
"""
Validation utilities for Relationship Intelligence OS schemas.
Provides validation functions for all five data products with confidence and provenance checking.
"""

import json
import jsonschema
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import re
import sys
import os

# Add N5 to path for imports
sys.path.insert(0, '/home/workspace')

SCHEMA_DIR = Path(__file__).parent
SCHEMA_FILES = {
    'promotion_event': 'promotion_event.schema.json',
    'relationship_delta': 'relationship_delta.schema.json', 
    'org_delta': 'org_delta.schema.json',
    'deliverable_record': 'deliverable_record.schema.json',
    'intro_opportunity': 'intro_opportunity.schema.json'
}

class SchemaValidator:
    """Validates payloads against Relationship Intelligence OS schemas."""
    
    def __init__(self):
        self.schemas = {}
        self._load_schemas()
    
    def _load_schemas(self):
        """Load all schema files into memory."""
        for schema_name, filename in SCHEMA_FILES.items():
            schema_path = SCHEMA_DIR / filename
            if schema_path.exists():
                with open(schema_path) as f:
                    self.schemas[schema_name] = json.load(f)
            else:
                print(f"Warning: Schema file {filename} not found")
    
    def validate_payload(self, payload: Dict[Any, Any], schema_type: str) -> Tuple[bool, List[str]]:
        """
        Validate a payload against its schema.
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        if schema_type not in self.schemas:
            return False, [f"Unknown schema type: {schema_type}"]
        
        schema = self.schemas[schema_type]
        errors = []
        
        try:
            jsonschema.validate(instance=payload, schema=schema)
            
            # Additional validation checks
            additional_errors = self._additional_validation(payload, schema_type)
            errors.extend(additional_errors)
            
            return len(errors) == 0, errors
            
        except jsonschema.ValidationError as e:
            errors.append(f"Schema validation error: {e.message}")
            return False, errors
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
            return False, errors
    
    def _additional_validation(self, payload: Dict[Any, Any], schema_type: str) -> List[str]:
        """Additional validation beyond basic JSON schema."""
        errors = []
        
        # Universal checks
        errors.extend(self._validate_provenance(payload))
        errors.extend(self._validate_confidence(payload))
        
        # Schema-specific checks
        if schema_type == 'promotion_event':
            errors.extend(self._validate_promotion_event(payload))
        elif schema_type == 'relationship_delta':
            errors.extend(self._validate_relationship_delta(payload))
        elif schema_type == 'org_delta':
            errors.extend(self._validate_org_delta(payload))
        elif schema_type == 'deliverable_record':
            errors.extend(self._validate_deliverable_record(payload))
        elif schema_type == 'intro_opportunity':
            errors.extend(self._validate_intro_opportunity(payload))
        
        return errors
    
    def _validate_provenance(self, payload: Dict[Any, Any]) -> List[str]:
        """Validate provenance field requirements."""
        errors = []
        
        if 'provenance' not in payload:
            errors.append("Missing required 'provenance' field")
            return errors
        
        provenance = payload['provenance']
        
        # Check conversation_id format
        if 'conversation_id' in provenance:
            conv_id = provenance['conversation_id']
            if not re.match(r'^con_[A-Za-z0-9]+$', conv_id):
                errors.append(f"Invalid conversation_id format: {conv_id}")
        
        return errors
    
    def _validate_confidence(self, payload: Dict[Any, Any]) -> List[str]:
        """Validate confidence score is present and in valid range."""
        errors = []
        
        if 'confidence' not in payload:
            errors.append("Missing required 'confidence' field")
            return errors
        
        confidence = payload['confidence']
        if not isinstance(confidence, (int, float)):
            errors.append("Confidence must be a number")
        elif confidence < 0 or confidence > 1:
            errors.append(f"Confidence must be between 0 and 1, got {confidence}")
        
        return errors
    
    def _validate_promotion_event(self, payload: Dict[Any, Any]) -> List[str]:
        """Additional validation for promotion events."""
        errors = []
        
        # Validate score breakdown adds up to total score
        if 'score_breakdown' in payload:
            breakdown = payload['score_breakdown']
            total = sum(breakdown.values())
            expected_score = payload.get('score', 0)
            if abs(total - expected_score) > 1:  # Allow 1 point tolerance
                errors.append(f"Score breakdown ({total}) doesn't match total score ({expected_score})")
        
        # Validate tier matches score
        score = payload.get('score', 0)
        tier = payload.get('tier', '')
        if score >= 75 and tier != 'A':
            errors.append(f"Score {score} should be tier A, got {tier}")
        elif 50 <= score < 75 and tier != 'B':
            errors.append(f"Score {score} should be tier B, got {tier}")
        elif score < 50 and tier != 'C':
            errors.append(f"Score {score} should be tier C, got {tier}")
        
        return errors
    
    def _validate_relationship_delta(self, payload: Dict[Any, Any]) -> List[str]:
        """Additional validation for relationship deltas."""
        errors = []
        
        # Validate evidence structure
        if 'evidence' in payload:
            evidence = payload['evidence']
            if 'quotes' not in evidence or 'block_references' not in evidence:
                errors.append("Evidence must contain both 'quotes' and 'block_references'")
        
        return errors
    
    def _validate_org_delta(self, payload: Dict[Any, Any]) -> List[str]:
        """Additional validation for org deltas."""
        errors = []
        
        # Validate current_state has required fields
        if 'current_state' in payload:
            current_state = payload['current_state']
            if 'description' not in current_state:
                errors.append("current_state must contain 'description'")
            if 'confidence' not in current_state:
                errors.append("current_state must contain 'confidence'")
        
        return errors
    
    def _validate_deliverable_record(self, payload: Dict[Any, Any]) -> List[str]:
        """Additional validation for deliverable records."""
        errors = []
        
        # Validate timeline consistency
        if 'timeline' in payload:
            timeline = payload['timeline']
            created_at = timeline.get('created_at')
            started_at = timeline.get('started_at')
            completed_at = timeline.get('completed_at')
            
            # Convert string dates for comparison if present
            dates = []
            for date_str in [created_at, started_at, completed_at]:
                if date_str:
                    try:
                        dates.append(datetime.fromisoformat(date_str.replace('Z', '+00:00')))
                    except ValueError:
                        errors.append(f"Invalid datetime format: {date_str}")
            
            # Check chronological order
            for i in range(len(dates) - 1):
                if dates[i] > dates[i + 1]:
                    errors.append("Timeline dates must be in chronological order")
        
        return errors
    
    def _validate_intro_opportunity(self, payload: Dict[Any, Any]) -> List[str]:
        """Additional validation for intro opportunities."""
        errors = []
        
        # Validate introducees are different people
        introducee_a = payload.get('introducee_a', {})
        introducee_b = payload.get('introducee_b', {})
        
        if introducee_a.get('person_id') == introducee_b.get('person_id'):
            errors.append("introducee_a and introducee_b cannot be the same person")
        
        return errors

def validate_sample_payloads():
    """Test validation with sample payloads for each schema type."""
    
    validator = SchemaValidator()
    
    # Sample payloads
    samples = {
        'promotion_event': {
            "event_id": "pe_test1234",
            "timestamp": "2026-02-16T20:35:00Z",
            "source_meeting_id": "abc123",
            "candidate_type": "relationship_delta",
            "score": 85,
            "score_breakdown": {
                "strategic_importance": 18,
                "relationship_delta_strength": 16,
                "commitment_clarity": 19,
                "evidence_quality": 13,
                "novelty": 12,
                "execution_value": 7
            },
            "tier": "A",
            "status": "promoted",
            "provenance": {
                "processor_version": "1.0.0",
                "conversation_id": "con_test123"
            },
            "confidence": 0.9
        },
        'relationship_delta': {
            "delta_id": "rd_test1234", 
            "timestamp": "2026-02-16T20:35:00Z",
            "source_meeting_id": "abc123",
            "person_id": "person_123",
            "delta_type": "sentiment_shift",
            "trend": "increasing",
            "current_state": {
                "value": "positive",
                "confidence": 0.8
            },
            "evidence": {
                "quotes": [{
                    "text": "Sample quote",
                    "speaker": "John Doe"
                }],
                "block_references": ["block_123"]
            },
            "provenance": {
                "extractor_version": "1.0.0",
                "conversation_id": "con_test123"
            },
            "confidence": 0.85
        },
        'org_delta': {
            "delta_id": "od_test1234",
            "timestamp": "2026-02-16T20:35:00Z", 
            "source_meeting_id": "abc123",
            "organization_id": "org_123",
            "delta_type": "priority_shift",
            "change_description": "Shifted focus to digital transformation",
            "impact_scope": "company_wide",
            "current_state": {
                "description": "High priority on digital transformation",
                "confidence": 0.9
            },
            "evidence": {
                "quotes": [{
                    "text": "Sample quote",
                    "speaker": "Jane Smith"
                }],
                "block_references": ["block_456"]
            },
            "provenance": {
                "extractor_version": "1.0.0",
                "conversation_id": "con_test123"
            },
            "confidence": 0.88
        },
        'deliverable_record': {
            "deliverable_id": "del_test1234",
            "timestamp": "2026-02-16T20:35:00Z",
            "source_meeting_id": "abc123",
            "client_id": "client_123",
            "deliverable_type": "proposal",
            "title": "Test Proposal for Digital Transformation",
            "status": "identified",
            "commitment_details": {
                "commitment_type": "explicit_promise"
            },
            "evidence": {
                "quotes": [{
                    "text": "Sample quote", 
                    "speaker": "Client"
                }],
                "block_references": ["block_789"]
            },
            "provenance": {
                "extractor_version": "1.0.0",
                "conversation_id": "con_test123"
            },
            "confidence": 0.92
        },
        'intro_opportunity': {
            "opportunity_id": "io_test1234",
            "timestamp": "2026-02-16T20:35:00Z",
            "source_meeting_id": "abc123",
            "introducer_id": "intro_123",
            "introducee_a": {
                "person_id": "person_a123"
            },
            "introducee_b": {
                "person_id": "person_b456"
            },
            "opportunity_type": "business_development",
            "mutual_value": {
                "description": "Both could benefit from partnership"
            },
            "connection_analysis": {
                "connection_path": "direct",
                "relationship_strength": {
                    "introducer_to_a": "strong",
                    "introducer_to_b": "moderate"
                }
            },
            "recommended_approach": {
                "introduction_method": "email_introduction",
                "timing_recommendation": "within_week"
            },
            "evidence": {
                "quotes": [{
                    "text": "Sample quote",
                    "speaker": "Someone"
                }],
                "block_references": ["block_999"]
            },
            "priority": "medium",
            "status": "identified",
            "provenance": {
                "detector_version": "1.0.0",
                "conversation_id": "con_test123"
            },
            "confidence": 0.75
        }
    }
    
    print("Validating sample payloads...\n")
    
    all_valid = True
    for schema_type, payload in samples.items():
        is_valid, errors = validator.validate_payload(payload, schema_type)
        
        if is_valid:
            print(f"✓ {schema_type}: Valid")
        else:
            print(f"✗ {schema_type}: Invalid")
            for error in errors:
                print(f"  - {error}")
            all_valid = False
    
    print(f"\nOverall validation: {'✓ PASS' if all_valid else '✗ FAIL'}")
    return all_valid

def main():
    """Main validation command interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate Relationship Intelligence OS schema payloads')
    parser.add_argument('--test-samples', action='store_true', 
                       help='Test validation with sample payloads')
    parser.add_argument('--schema', choices=list(SCHEMA_FILES.keys()),
                       help='Validate a specific schema type')
    parser.add_argument('--file', type=str,
                       help='JSON file to validate')
    
    args = parser.parse_args()
    
    if args.test_samples:
        success = validate_sample_payloads()
        sys.exit(0 if success else 1)
    
    if args.file and args.schema:
        validator = SchemaValidator()
        
        try:
            with open(args.file) as f:
                payload = json.load(f)
            
            is_valid, errors = validator.validate_payload(payload, args.schema)
            
            if is_valid:
                print(f"✓ {args.file} is valid for schema {args.schema}")
                sys.exit(0)
            else:
                print(f"✗ {args.file} is invalid for schema {args.schema}")
                for error in errors:
                    print(f"  - {error}")
                sys.exit(1)
        
        except FileNotFoundError:
            print(f"Error: File {args.file} not found")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in {args.file}: {e}")
            sys.exit(1)
    
    parser.print_help()

if __name__ == '__main__':
    main()