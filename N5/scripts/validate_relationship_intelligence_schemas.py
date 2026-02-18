#!/usr/bin/env python3
"""
Relationship Intelligence OS Schema Validator

Validates all relationship intelligence schemas and provides helper utilities
for testing and validation of schema compliance.
"""

import json
import sys
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
import jsonschema
from datetime import datetime, timezone
import uuid

# Paths
ROOT = Path(__file__).resolve().parents[1]
SCHEMAS_DIR = ROOT / "schemas"
SAMPLE_DATA_DIR = ROOT / "test_data" / "relationship_intelligence"

# Schema mappings
SCHEMAS = {
    "promotion_event": "promotion-event.schema.json",
    "relationship_delta": "relationship-delta.schema.json", 
    "org_delta": "org-delta.schema.json",
    "deliverable_record": "deliverable-record.schema.json",
    "intro_opportunity": "intro-opportunity.schema.json"
}

class RelationshipIntelligenceValidator:
    """Validator for Relationship Intelligence OS schemas"""
    
    def __init__(self):
        self.schemas = {}
        self.load_schemas()
        
    def load_schemas(self) -> None:
        """Load all relationship intelligence schemas"""
        for schema_name, filename in SCHEMAS.items():
            schema_path = SCHEMAS_DIR / filename
            if not schema_path.exists():
                print(f"Warning: Schema file not found: {schema_path}")
                continue
                
            try:
                with open(schema_path, 'r') as f:
                    self.schemas[schema_name] = json.load(f)
                print(f"Loaded schema: {schema_name}")
            except Exception as e:
                print(f"Error loading schema {schema_name}: {e}")
    
    def validate_payload(self, schema_name: str, payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate a payload against a schema"""
        if schema_name not in self.schemas:
            return False, [f"Schema {schema_name} not found"]
        
        errors = []
        try:
            jsonschema.validate(instance=payload, schema=self.schemas[schema_name])
            return True, []
        except jsonschema.exceptions.ValidationError as e:
            return False, [str(e)]
        except Exception as e:
            return False, [f"Validation error: {str(e)}"]
    
    def generate_sample_payloads(self) -> Dict[str, Dict[str, Any]]:
        """Generate valid sample payloads for all schemas"""
        samples = {}
        
        # Sample promotion event
        samples["promotion_event"] = {
            "promotion_id": "prom_abc123def456",
            "meeting_id": "mtg001",
            "block_ids": ["B08", "B03"],
            "memory_type": "relationship_delta",
            "score": 85,
            "score_breakdown": {
                "strategic_importance": 18,
                "relationship_delta_strength": 16,
                "commitment_clarity": 15,
                "evidence_quality": 14,
                "novelty": 12,
                "execution_value": 10
            },
            "tier": "A",
            "status": "auto_promoted",
            "hard_overrides": ["explicit_promise"],
            "deduplication": {
                "status": "new",
                "checked_at": datetime.now(timezone.utc).isoformat()
            },
            "memory_writes": {
                "semantic_memory": {"status": "success", "entity_ids": ["ent_123"]},
                "graph_edges": {"status": "success", "edge_ids": ["edge_456"]},
                "crm_projection": {"status": "success", "profile_ids": ["prof_789"]}
            },
            "created_at": datetime.now(timezone.utc).isoformat(),
            "promoted_at": datetime.now(timezone.utc).isoformat(),
            "provenance": {
                "conversation_id": "con_abc123",
                "pipeline_run_id": "run_def456",
                "script_path": "N5/scripts/promotion_engine.py",
                "version": "1.0.0",
                "idempotency_key": str(uuid.uuid4())
            },
            "confidence": {
                "overall": 0.85,
                "scoring_confidence": 0.9,
                "extraction_confidence": 0.8,
                "deduplication_confidence": 0.95
            }
        }
        
        # Sample relationship delta
        samples["relationship_delta"] = {
            "delta_id": "rdelta_abc123def456",
            "person_id": "person_xyz789abc123",
            "organization_id": "org_def456ghi789",
            "delta_type": "trust_increase",
            "strength": 4,
            "trend": "positive",
            "context": {
                "previous_state": "Professional acquaintance",
                "current_state": "Trusted advisor relationship",
                "trigger_event": "Successful project delivery exceeded expectations",
                "duration_estimate": "long_term"
            },
            "evidence": [
                {
                    "type": "verbal_statement",
                    "content": "Really appreciate your insight on this - you've become someone I trust for strategic decisions",
                    "weight": 0.8,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "source_block_id": "B08"
                }
            ],
            "mutual_connections": [
                {
                    "person_id": "person_mutual123456",
                    "relationship_type": "colleague", 
                    "strength": 3,
                    "discovered_at": datetime.now(timezone.utc).isoformat()
                }
            ],
            "impact_assessment": {
                "business_value": 8,
                "strategic_importance": 7,
                "urgency": "medium",
                "recommended_actions": ["Schedule regular check-ins", "Explore partnership opportunities"]
            },
            "created_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": (datetime.now(timezone.utc).replace(month=12, day=31)).isoformat(),
            "provenance": {
                "meeting_id": "mtg001",
                "block_ids": ["B08", "B03"],
                "conversation_id": "con_abc123",
                "extraction_version": "1.0.0",
                "pipeline_run_id": "run_def456"
            },
            "confidence": {
                "overall": 0.82,
                "evidence_quality": 0.85,
                "interpretation_accuracy": 0.78,
                "person_identification": 0.95
            }
        }
        
        # Sample org delta
        samples["org_delta"] = {
            "delta_id": "odelta_abc123def456",
            "organization_id": "org_xyz789abc123",
            "organization_name": "TechCorp Inc",
            "delta_type": "priority_shift",
            "impact_level": 3,
            "temporal_scope": "quarterly",
            "change_details": {
                "previous_state": "Focus on cost reduction and efficiency",
                "current_state": "Pivoting to growth and market expansion",
                "trigger_factors": ["Strong Q3 results", "New funding secured", "Market opportunity identified"],
                "affected_departments": ["Product", "Sales", "Marketing"],
                "key_stakeholders": [
                    {
                        "person_id": "person_ceo123abc456",
                        "role_in_change": "decision_maker",
                        "influence_level": 5
                    }
                ]
            },
            "business_implications": {
                "revenue_impact": "positive",
                "operational_impact": "positive", 
                "strategic_alignment": "aligned",
                "opportunity_score": 8,
                "risk_score": 3,
                "recommended_actions": [
                    {
                        "action": "Present growth partnership proposal",
                        "priority": "high",
                        "timeline": "weeks",
                        "owner": "Business Development"
                    }
                ]
            },
            "evidence": [
                {
                    "type": "direct_statement",
                    "content": "We're shifting from cost-cutting mode to aggressive growth - looking for partners who can help us scale",
                    "reliability": 0.9,
                    "source": "primary_stakeholder",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "source_block_id": "B08"
                }
            ],
            "competitive_intelligence": {
                "market_position_change": "strengthening",
                "competitive_threats": ["BigTech Corp", "StartupX"],
                "differentiation_factors": ["Speed to market", "Customer service excellence"],
                "market_dynamics": "Growing demand for enterprise solutions"
            },
            "created_at": datetime.now(timezone.utc).isoformat(),
            "effective_date": "2026-01-01",
            "review_date": "2026-04-01",
            "provenance": {
                "meeting_id": "mtg001",
                "block_ids": ["B08", "B32"],
                "conversation_id": "con_abc123",
                "extraction_version": "1.0.0",
                "pipeline_run_id": "run_def456"
            },
            "confidence": {
                "overall": 0.88,
                "evidence_quality": 0.9,
                "interpretation_accuracy": 0.85,
                "org_identification": 0.95,
                "temporal_accuracy": 0.8
            }
        }
        
        # Sample deliverable record
        samples["deliverable_record"] = {
            "deliverable_id": "deliv_abc123def456",
            "client_id": "org_client123456",
            "client_name": "FinanceCorp Ltd",
            "deliverable_type": "strategy_doc",
            "title": "Digital Transformation Strategy 2026",
            "description": "Comprehensive digital transformation roadmap including technology assessment, process redesign, and implementation timeline",
            "scope": {
                "overview": "End-to-end digital transformation strategy for financial services organization",
                "key_components": [
                    "Current state assessment",
                    "Technology gap analysis", 
                    "Process redesign recommendations",
                    "Implementation roadmap",
                    "Change management plan"
                ],
                "complexity_level": "high",
                "estimated_effort_hours": 120,
                "required_expertise": ["Strategy consulting", "Financial services", "Digital transformation"],
                "dependencies": ["IT systems audit", "Stakeholder interviews", "Market analysis"]
            },
            "status": "scoped",
            "timeline": {
                "promised_date": "2026-03-15",
                "target_date": "2026-03-10"
            },
            "ownership": {
                "primary_owner": "Senior Consultant A",
                "collaborators": ["Strategy Analyst B", "Research Associate C"],
                "reviewer": "Partner D",
                "approver": "Partner D"
            },
            "similarity_analysis": {
                "status": "similar_found",
                "similar_deliverables": [
                    {
                        "deliverable_id": "deliv_similar12345",
                        "similarity_score": 0.75,
                        "reuse_recommendation": "adapt",
                        "similarity_factors": ["Industry sector", "Transformation scope", "Client size"],
                        "adaptation_notes": "Adapt framework for specific regulatory requirements"
                    }
                ],
                "checked_at": datetime.now(timezone.utc).isoformat()
            },
            "context": {
                "business_context": "Client struggling with legacy systems and manual processes, needs to modernize to compete",
                "client_objectives": [
                    "Reduce operational costs by 20%",
                    "Improve customer experience scores",
                    "Enable new digital products"
                ],
                "success_criteria": [
                    "Clear roadmap with defined milestones",
                    "Buy-in from all key stakeholders",
                    "Implementation plan within budget constraints"
                ],
                "constraints": ["Limited budget", "Regulatory compliance requirements", "Legacy system constraints"],
                "assumptions": ["Management commitment to change", "Access to required stakeholders", "Stable regulatory environment"]
            },
            "created_at": datetime.now(timezone.utc).isoformat(),
            "provenance": {
                "meeting_id": "mtg002",
                "block_ids": ["B33", "B02"],
                "conversation_id": "con_def789",
                "extraction_version": "1.0.0",
                "pipeline_run_id": "run_ghi123"
            },
            "confidence": {
                "overall": 0.87,
                "scope_clarity": 0.9,
                "timeline_accuracy": 0.8,
                "client_identification": 0.95,
                "similarity_analysis": 0.85
            }
        }
        
        # Sample intro opportunity
        samples["intro_opportunity"] = {
            "opportunity_id": "intro_abc123def456",
            "requester_id": "person_request12345",
            "requester_name": "John Smith",
            "target_id": "person_target123456",
            "target_name": "Jane Doe",
            "mutual_path": [
                {
                    "person_id": "person_mutual123456",
                    "person_name": "Bob Wilson",
                    "relationship_strength": 4,
                    "relationship_type": "colleague",
                    "last_interaction": "2026-01-15",
                    "interaction_frequency": "monthly"
                }
            ],
            "intent": {
                "purpose": "partnership",
                "description": "Looking to explore potential partnership between our companies for market expansion",
                "expected_outcome": "Initial partnership discussion and mutual interest assessment",
                "urgency": "medium",
                "context": "Both companies expanding into similar markets, potential for synergies"
            },
            "status": "evaluating",
            "feasibility_assessment": {
                "strength_score": 7,
                "likelihood_success": 0.75,
                "potential_value": 8,
                "risk_factors": ["Competitive overlap in some areas"],
                "success_factors": ["Strong mutual connection", "Complementary strengths", "Market timing"]
            },
            "timing": {
                "optimal_timing": "weeks",
                "timing_rationale": "Both parties are currently in strategic planning phase",
                "deadline": "2026-03-01"
            },
            "preparation": {
                "requester_prep": ["Prepare company overview", "Identify specific partnership areas"],
                "target_prep": ["Research requester's company", "Consider strategic fit"],
                "context_to_share": ["Mutual connection background", "Partnership exploration purpose"],
                "suggested_format": "video_call"
            },
            "created_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": (datetime.now(timezone.utc).replace(month=6, day=1)).isoformat(),
            "provenance": {
                "meeting_id": "mtg003",
                "block_ids": ["B05"],
                "conversation_id": "con_ghi789",
                "extraction_version": "1.0.0",
                "pipeline_run_id": "run_jkl456"
            },
            "confidence": {
                "overall": 0.78,
                "mutual_path_accuracy": 0.85,
                "intent_clarity": 0.8,
                "person_identification": 0.9,
                "feasibility_assessment": 0.7
            }
        }
        
        return samples
    
    def validate_all_samples(self) -> bool:
        """Validate all generated sample payloads"""
        samples = self.generate_sample_payloads()
        all_valid = True
        
        print(f"\nValidating {len(samples)} sample payloads...\n")
        
        for schema_name, payload in samples.items():
            is_valid, errors = self.validate_payload(schema_name, payload)
            
            if is_valid:
                print(f"✅ {schema_name}: VALID")
            else:
                print(f"❌ {schema_name}: INVALID")
                for error in errors:
                    print(f"   Error: {error}")
                all_valid = False
        
        return all_valid
    
    def generate_sample_files(self) -> None:
        """Generate sample payload files for testing"""
        samples = self.generate_sample_payloads()
        
        # Create sample data directory
        SAMPLE_DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        for schema_name, payload in samples.items():
            sample_file = SAMPLE_DATA_DIR / f"sample_{schema_name}.json"
            with open(sample_file, 'w') as f:
                json.dump(payload, f, indent=2)
            print(f"Generated sample file: {sample_file}")
    
    def check_required_fields(self) -> None:
        """Check that all schemas have required provenance and confidence fields"""
        print("\nChecking required fields...")
        
        for schema_name, schema in self.schemas.items():
            required = schema.get('required', [])
            properties = schema.get('properties', {})
            
            # Check provenance field
            if 'provenance' not in required:
                print(f"❌ {schema_name}: Missing required 'provenance' field")
            elif 'provenance' in properties:
                provenance_schema = properties.get('provenance', {})
                provenance_required = provenance_schema.get('required', [])
                if 'conversation_id' not in provenance_required:
                    print(f"⚠️  {schema_name}: Provenance missing required 'conversation_id'")
                else:
                    print(f"✅ {schema_name}: Provenance field valid")
            
            # Check confidence field  
            if 'confidence' not in required:
                print(f"❌ {schema_name}: Missing required 'confidence' field")
            elif 'confidence' in properties:
                confidence_schema = properties.get('confidence', {})
                confidence_required = confidence_schema.get('required', [])
                if 'overall' not in confidence_required:
                    print(f"⚠️  {schema_name}: Confidence missing required 'overall'")
                else:
                    print(f"✅ {schema_name}: Confidence field valid")


def main():
    """Main validation function"""
    validator = RelationshipIntelligenceValidator()
    
    if not validator.schemas:
        print("❌ No schemas loaded. Make sure schema files exist in N5/schemas/")
        return 1
    
    print(f"Loaded {len(validator.schemas)} schemas: {list(validator.schemas.keys())}")
    
    # Check required fields
    validator.check_required_fields()
    
    # Validate sample payloads
    if validator.validate_all_samples():
        print("\n🎉 All sample payloads are valid!")
    else:
        print("\n❌ Some sample payloads failed validation")
        return 1
    
    # Generate sample files
    print("\nGenerating sample payload files...")
    validator.generate_sample_files()
    
    print(f"\n✅ Schema validation complete!")
    print(f"📁 Sample files saved to: {SAMPLE_DATA_DIR}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())