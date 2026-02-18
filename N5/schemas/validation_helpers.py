#!/usr/bin/env python3
"""
Validation helper utilities for Relationship Intelligence OS schemas.
Provides reusable validation functions and utilities for integration with the promotion gate.
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple, Union
import re
from pathlib import Path

from validate_schemas import SchemaValidator


class IntelligenceValidator:
    """
    High-level validation utilities for relationship intelligence payloads.
    Provides convenience methods and integration helpers.
    """
    
    def __init__(self):
        self.schema_validator = SchemaValidator()
    
    def generate_id(self, prefix: str) -> str:
        """
        Generate a valid ID for intelligence records.
        
        Args:
            prefix: One of 'pe_', 'rd_', 'od_', 'del_', 'io_'
            
        Returns:
            Valid ID string like 'pe_a1b2c3d4'
        """
        if prefix not in ['pe_', 'rd_', 'od_', 'del_', 'io_']:
            raise ValueError(f"Invalid prefix: {prefix}")
        
        # Generate 8 character alphanumeric suffix
        suffix = uuid.uuid4().hex[:8].lower()
        return f"{prefix}{suffix}"
    
    def create_provenance(self, 
                         processor_version: str,
                         conversation_id: str,
                         processing_mode: str = "production",
                         source_blocks: Optional[List[str]] = None,
                         version_field: str = "processor_version") -> Dict[str, Any]:
        """
        Create a valid provenance object.
        
        Args:
            processor_version: Version of the processor/extractor
            conversation_id: Conversation ID (must start with 'con_')
            processing_mode: One of 'production', 'dry_run', 'test'
            source_blocks: Optional list of source block IDs
            version_field: Name of the version field ('processor_version' or 'extractor_version')
            
        Returns:
            Valid provenance dictionary
        """
        if not conversation_id.startswith('con_'):
            raise ValueError(f"conversation_id must start with 'con_', got: {conversation_id}")
        
        if processing_mode not in ['production', 'dry_run', 'test']:
            raise ValueError(f"Invalid processing_mode: {processing_mode}")
        
        provenance = {
            version_field: processor_version,
            "conversation_id": conversation_id,
            "processing_mode": processing_mode
        }
        
        if source_blocks:
            provenance["source_blocks"] = source_blocks
        
        return provenance
    
    def create_evidence(self, 
                       quotes: List[Dict[str, str]], 
                       block_references: List[str]) -> Dict[str, Any]:
        """
        Create a valid evidence object.
        
        Args:
            quotes: List of quote dictionaries with 'text' and 'speaker'
            block_references: List of block ID references
            
        Returns:
            Valid evidence dictionary
        """
        if not quotes:
            raise ValueError("Evidence must contain at least one quote")
        
        if not block_references:
            raise ValueError("Evidence must contain at least one block reference")
        
        # Validate quote structure
        for quote in quotes:
            if 'text' not in quote or 'speaker' not in quote:
                raise ValueError("Each quote must have 'text' and 'speaker' fields")
        
        return {
            "quotes": quotes,
            "block_references": block_references
        }
    
    def validate_and_normalize(self, 
                              payload: Dict[str, Any], 
                              schema_type: str,
                              auto_fix: bool = False) -> Tuple[bool, List[str], Dict[str, Any]]:
        """
        Validate a payload and optionally apply automatic fixes.
        
        Args:
            payload: The payload to validate
            schema_type: The schema type to validate against
            auto_fix: Whether to apply automatic fixes where possible
            
        Returns:
            Tuple of (is_valid, errors, normalized_payload)
        """
        normalized = payload.copy()
        
        if auto_fix:
            # Auto-fix common issues
            normalized = self._apply_auto_fixes(normalized, schema_type)
        
        is_valid, errors = self.schema_validator.validate_payload(normalized, schema_type)
        return is_valid, errors, normalized
    
    def _apply_auto_fixes(self, payload: Dict[str, Any], schema_type: str) -> Dict[str, Any]:
        """Apply automatic fixes to common validation issues."""
        fixed = payload.copy()
        
        # Add timestamp if missing
        if 'timestamp' not in fixed:
            fixed['timestamp'] = datetime.now(timezone.utc).isoformat()
        
        # Generate ID if missing
        id_field = self._get_id_field(schema_type)
        if id_field and id_field not in fixed:
            prefix = self._get_id_prefix(schema_type)
            fixed[id_field] = self.generate_id(prefix)
        
        # Ensure confidence is in valid range
        if 'confidence' in fixed:
            confidence = fixed['confidence']
            if isinstance(confidence, (int, float)):
                fixed['confidence'] = max(0.0, min(1.0, float(confidence)))
        
        return fixed
    
    def _get_id_field(self, schema_type: str) -> Optional[str]:
        """Get the ID field name for a schema type."""
        id_fields = {
            'promotion_event': 'event_id',
            'relationship_delta': 'delta_id',
            'org_delta': 'delta_id',
            'deliverable_record': 'deliverable_id',
            'intro_opportunity': 'opportunity_id'
        }
        return id_fields.get(schema_type)
    
    def _get_id_prefix(self, schema_type: str) -> str:
        """Get the ID prefix for a schema type."""
        prefixes = {
            'promotion_event': 'pe_',
            'relationship_delta': 'rd_',
            'org_delta': 'od_',
            'deliverable_record': 'del_',
            'intro_opportunity': 'io_'
        }
        return prefixes[schema_type]


class PromotionGateValidator:
    """
    Specialized validator for the promotion gate system.
    Handles tier assignment validation and score consistency checks.
    """
    
    def __init__(self):
        self.validator = IntelligenceValidator()
    
    def validate_promotion_event(self, payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate a promotion event with specialized business logic.
        
        Args:
            payload: The promotion event payload
            
        Returns:
            Tuple of (is_valid, errors)
        """
        is_valid, errors, _ = self.validator.validate_and_normalize(
            payload, 'promotion_event', auto_fix=False
        )
        
        # Additional promotion-specific validation
        errors.extend(self._validate_score_consistency(payload))
        errors.extend(self._validate_tier_assignment(payload))
        errors.extend(self._validate_hard_override_logic(payload))
        
        return len(errors) == 0, errors
    
    def _validate_score_consistency(self, payload: Dict[str, Any]) -> List[str]:
        """Validate that score breakdown is consistent with total score."""
        errors = []
        
        if 'score' not in payload or 'score_breakdown' not in payload:
            return errors
        
        total_score = payload['score']
        breakdown = payload['score_breakdown']
        
        # Check that all required rubric categories are present
        required_categories = [
            'strategic_importance', 'relationship_delta_strength', 
            'commitment_clarity', 'evidence_quality', 'novelty', 'execution_value'
        ]
        
        for category in required_categories:
            if category not in breakdown:
                errors.append(f"Missing score breakdown category: {category}")
        
        # Check score ranges for each category
        score_limits = {
            'strategic_importance': 20,
            'relationship_delta_strength': 20,
            'commitment_clarity': 20,
            'evidence_quality': 15,
            'novelty': 15,
            'execution_value': 10
        }
        
        for category, max_score in score_limits.items():
            if category in breakdown:
                score = breakdown[category]
                if not isinstance(score, (int, float)) or score < 0 or score > max_score:
                    errors.append(f"{category} score must be between 0 and {max_score}, got {score}")
        
        # Check total consistency (with 1 point tolerance for rounding)
        breakdown_total = sum(breakdown.values())
        if abs(breakdown_total - total_score) > 1:
            errors.append(f"Score breakdown total ({breakdown_total}) doesn't match total score ({total_score})")
        
        return errors
    
    def _validate_tier_assignment(self, payload: Dict[str, Any]) -> List[str]:
        """Validate that tier assignment matches score."""
        errors = []
        
        if 'score' not in payload or 'tier' not in payload:
            return errors
        
        score = payload['score']
        tier = payload['tier']
        
        # Check tier assignment rules
        if score >= 75 and tier != 'A':
            errors.append(f"Score {score} should be tier A, got {tier}")
        elif 50 <= score < 75 and tier != 'B':
            errors.append(f"Score {score} should be tier B, got {tier}")
        elif score < 50 and tier != 'C':
            errors.append(f"Score {score} should be tier C, got {tier}")
        
        return errors
    
    def _validate_hard_override_logic(self, payload: Dict[str, Any]) -> List[str]:
        """Validate hard override logic."""
        errors = []
        
        hard_override = payload.get('hard_override', {})
        if not hard_override.get('applied', False):
            return errors
        
        # If override is applied, must have reason and original tier
        if 'reason' not in hard_override:
            errors.append("Hard override must include reason when applied")
        
        if 'original_tier' not in hard_override:
            errors.append("Hard override must include original_tier when applied")
        
        # Check that override reason is valid
        valid_reasons = [
            'explicit_promise', 'named_deliverable', 'introduction_request',
            'critical_deadline', 'stakeholder_request'
        ]
        
        if hard_override.get('reason') not in valid_reasons:
            errors.append(f"Invalid hard override reason: {hard_override.get('reason')}")
        
        return errors


class BatchValidator:
    """
    Validator for processing batches of intelligence records.
    Useful for bulk validation and migration scenarios.
    """
    
    def __init__(self):
        self.validator = IntelligenceValidator()
        self.promotion_validator = PromotionGateValidator()
    
    def validate_batch(self, 
                      records: List[Dict[str, Any]], 
                      schema_types: Union[str, List[str]],
                      auto_fix: bool = False,
                      stop_on_error: bool = False) -> Dict[str, Any]:
        """
        Validate a batch of records.
        
        Args:
            records: List of records to validate
            schema_types: Schema type(s) - single string or list matching records
            auto_fix: Whether to apply automatic fixes
            stop_on_error: Whether to stop on first error
            
        Returns:
            Validation results summary
        """
        results = {
            'total_records': len(records),
            'valid_records': 0,
            'invalid_records': 0,
            'errors': [],
            'normalized_records': []
        }
        
        # Handle single schema type for all records
        if isinstance(schema_types, str):
            schema_types = [schema_types] * len(records)
        
        if len(schema_types) != len(records):
            raise ValueError("schema_types must be single string or list matching records length")
        
        for i, (record, schema_type) in enumerate(zip(records, schema_types)):
            try:
                if schema_type == 'promotion_event':
                    is_valid, errors = self.promotion_validator.validate_promotion_event(record)
                    normalized = record  # Promotion validator doesn't return normalized
                else:
                    is_valid, errors, normalized = self.validator.validate_and_normalize(
                        record, schema_type, auto_fix=auto_fix
                    )
                
                if is_valid:
                    results['valid_records'] += 1
                    results['normalized_records'].append(normalized)
                else:
                    results['invalid_records'] += 1
                    results['errors'].append({
                        'record_index': i,
                        'schema_type': schema_type,
                        'errors': errors
                    })
                    results['normalized_records'].append(None)
                
                if not is_valid and stop_on_error:
                    break
                    
            except Exception as e:
                results['invalid_records'] += 1
                results['errors'].append({
                    'record_index': i,
                    'schema_type': schema_type,
                    'errors': [f"Validation exception: {str(e)}"]
                })
                results['normalized_records'].append(None)
                
                if stop_on_error:
                    break
        
        results['success_rate'] = results['valid_records'] / results['total_records']
        return results
    
    def export_errors(self, validation_results: Dict[str, Any], output_file: str) -> None:
        """
        Export validation errors to a file for review.
        
        Args:
            validation_results: Results from validate_batch
            output_file: Path to output file
        """
        error_report = {
            'summary': {
                'total_records': validation_results['total_records'],
                'valid_records': validation_results['valid_records'], 
                'invalid_records': validation_results['invalid_records'],
                'success_rate': validation_results['success_rate']
            },
            'errors': validation_results['errors']
        }
        
        with open(output_file, 'w') as f:
            json.dump(error_report, f, indent=2)


def create_sample_payloads() -> Dict[str, Dict[str, Any]]:
    """
    Create sample payloads for testing and examples.
    
    Returns:
        Dictionary of schema_type -> sample_payload
    """
    validator = IntelligenceValidator()
    
    samples = {}
    
    # Promotion Event
    samples['promotion_event'] = {
        "event_id": validator.generate_id("pe_"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_meeting_id": "meeting_123",
        "candidate_type": "relationship_delta",
        "score": 78,
        "score_breakdown": {
            "strategic_importance": 16,
            "relationship_delta_strength": 15,
            "commitment_clarity": 18,
            "evidence_quality": 12,
            "novelty": 11,
            "execution_value": 6
        },
        "tier": "A",
        "status": "promoted",
        "provenance": validator.create_provenance("1.0.0", "con_example123"),
        "confidence": 0.87
    }
    
    # Relationship Delta (uses extractor_version)
    samples['relationship_delta'] = {
        "delta_id": validator.generate_id("rd_"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_meeting_id": "meeting_123",
        "person_id": "person_456",
        "delta_type": "sentiment_shift",
        "trend": "increasing",
        "current_state": {
            "value": "positive",
            "confidence": 0.85
        },
        "evidence": validator.create_evidence(
            quotes=[{"text": "I'm really excited about this project", "speaker": "John Smith"}],
            block_references=["block_789"]
        ),
        "provenance": validator.create_provenance("1.0.0", "con_example123", version_field="extractor_version"),
        "confidence": 0.85
    }
    
    # Organization Delta (uses extractor_version)
    samples['org_delta'] = {
        "delta_id": validator.generate_id("od_"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_meeting_id": "meeting_123",
        "organization_id": "org_789",
        "delta_type": "priority_shift",
        "change_description": "Company is prioritizing digital transformation initiatives",
        "impact_scope": "company_wide",
        "current_state": {
            "description": "High priority focus on digital transformation",
            "confidence": 0.9
        },
        "evidence": validator.create_evidence(
            quotes=[{"text": "We're shifting all our focus to digital transformation", "speaker": "CEO Jane Doe"}],
            block_references=["block_456"]
        ),
        "provenance": validator.create_provenance("1.0.0", "con_example123", version_field="extractor_version"),
        "confidence": 0.9
    }
    
    # Deliverable Record (uses extractor_version)
    samples['deliverable_record'] = {
        "deliverable_id": validator.generate_id("del_"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_meeting_id": "meeting_123",
        "client_id": "client_789",
        "deliverable_type": "proposal",
        "title": "Digital Transformation Strategy Proposal",
        "status": "identified",
        "commitment_details": {
            "commitment_type": "deliverable_request",
            "owner": "V",
            "requestor": "Client Manager"
        },
        "evidence": validator.create_evidence(
            quotes=[{"text": "We need a comprehensive strategy proposal by next month", "speaker": "Client Manager"}],
            block_references=["block_123"]
        ),
        "provenance": validator.create_provenance("1.0.0", "con_example123", version_field="extractor_version"),
        "confidence": 0.88
    }
    
    # Introduction Opportunity (uses detector_version)
    samples['intro_opportunity'] = {
        "opportunity_id": validator.generate_id("io_"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_meeting_id": "meeting_123",
        "introducer_id": "person_v",
        "introducee_a": {
            "person_id": "person_123",
            "name": "Alice Johnson",
            "title": "VP Engineering",
            "organization": "TechCorp"
        },
        "introducee_b": {
            "person_id": "person_456",
            "name": "Bob Smith", 
            "title": "CTO",
            "organization": "StartupInc"
        },
        "opportunity_type": "partnership_potential",
        "mutual_value": {
            "value_to_a": "Access to startup innovation",
            "value_to_b": "Enterprise customer validation",
            "shared_benefits": "Technology partnership opportunity"
        },
        "connection_analysis": {
            "connection_strength": "medium",
            "path_length": 1,
            "mutual_connections": []
        },
        "recommended_approach": {
            "introduction_method": "email",
            "timing_recommendation": "immediate"
        },
        "evidence": validator.create_evidence(
            quotes=[{"text": "We're looking for partnership opportunities with enterprise companies", "speaker": "Bob Smith"}],
            block_references=["block_789"]
        ),
        "priority": "medium",
        "status": "identified",
        "provenance": validator.create_provenance("1.0.0", "con_example123", version_field="detector_version"),
        "confidence": 0.82
    }
    
    return samples


if __name__ == "__main__":
    # Example usage
    validator = IntelligenceValidator()
    
    # Generate sample payloads
    samples = create_sample_payloads()
    
    # Test validation
    for schema_type, payload in samples.items():
        is_valid, errors, normalized = validator.validate_and_normalize(payload, schema_type)
        print(f"{schema_type}: {'✓ Valid' if is_valid else '✗ Invalid'}")
        if errors:
            for error in errors:
                print(f"  - {error}")