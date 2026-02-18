#!/usr/bin/env python3
"""
Promotion Gate Engine for Relationship Intelligence OS
Implements meeting and item-level scoring with Tier A/B/C routing and hard overrides.

This is the core engine that processes promotion candidates and determines:
1. Scoring across rubric dimensions
2. Tier assignment (A/B/C) based on scores
3. Hard override logic for critical items
4. Routing decisions to downstream systems
5. Dry-run audit reporting
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import sys
import logging

# Add schemas path to import validation helpers
sys.path.append('/home/workspace/N5/schemas')
from validation_helpers import IntelligenceValidator, PromotionGateValidator

logger = logging.getLogger(__name__)


@dataclass
class ScoringConfig:
    """Configuration for the promotion gate scoring system."""
    
    # Tier thresholds
    tier_a_threshold: int = 75  # Auto-promote
    tier_b_threshold: int = 50  # Review digest  
    tier_c_threshold: int = 0   # Archive
    
    # Score weights and maximums (must sum to 100)
    strategic_importance_max: int = 20
    relationship_delta_strength_max: int = 20
    commitment_clarity_max: int = 20
    evidence_quality_max: int = 15
    novelty_max: int = 15
    execution_value_max: int = 10
    
    # Hard override triggers
    hard_override_keywords: Dict[str, List[str]] = None
    
    # Routing configuration
    routing_rules: Dict[str, Dict[str, bool]] = None
    
    def __post_init__(self):
        if self.hard_override_keywords is None:
            self.hard_override_keywords = {
                'explicit_promise': ['promise', 'commit', 'will deliver', 'guarantee'],
                'named_deliverable': ['proposal', 'presentation', 'report', 'analysis', 'strategy'],
                'introduction_request': ['introduce', 'connect', 'intro', 'meet'],
                'critical_deadline': ['urgent', 'asap', 'critical', 'deadline', 'immediately'],
                'stakeholder_request': ['stakeholder', 'executive', 'board', 'leadership']
            }
        
        if self.routing_rules is None:
            self.routing_rules = {
                'A': {
                    'semantic_memory': True,
                    'graph_edges': True,
                    'crm_projection': True,
                    'deliverables_db': True
                },
                'B': {
                    'semantic_memory': False,
                    'graph_edges': True,
                    'crm_projection': True,
                    'deliverables_db': True
                },
                'C': {
                    'semantic_memory': False,
                    'graph_edges': False,
                    'crm_projection': False,
                    'deliverables_db': False
                }
            }
    
    def validate(self) -> List[str]:
        """Validate scoring configuration."""
        errors = []
        
        # Check score maximums sum to 100
        total_max = (self.strategic_importance_max + 
                    self.relationship_delta_strength_max + 
                    self.commitment_clarity_max + 
                    self.evidence_quality_max + 
                    self.novelty_max + 
                    self.execution_value_max)
        
        if total_max != 100:
            errors.append(f"Score maximums must sum to 100, got {total_max}")
        
        # Check tier thresholds are logical
        if not (0 <= self.tier_c_threshold < self.tier_b_threshold < self.tier_a_threshold <= 100):
            errors.append(f"Invalid tier thresholds: C={self.tier_c_threshold}, B={self.tier_b_threshold}, A={self.tier_a_threshold}")
        
        return errors


@dataclass
class ScoringInput:
    """Input data for scoring a promotion candidate."""
    
    # Basic metadata
    candidate_type: str
    candidate_data: Dict[str, Any]
    source_meeting_id: str
    
    # Context for scoring
    meeting_context: Optional[Dict[str, Any]] = None
    existing_memory: Optional[List[Dict[str, Any]]] = None
    relationships: Optional[Dict[str, Any]] = None
    
    # Processing metadata
    conversation_id: str = ""
    processing_mode: str = "production"
    source_blocks: List[str] = None
    
    def __post_init__(self):
        if self.source_blocks is None:
            self.source_blocks = []


@dataclass
class ScoringResult:
    """Result of scoring a promotion candidate."""
    
    # Core scores
    strategic_importance: float
    relationship_delta_strength: float
    commitment_clarity: float
    evidence_quality: float
    novelty: float
    execution_value: float
    
    # Derived values
    total_score: float
    tier: str
    confidence: float
    
    # Override information
    hard_override: Optional[Dict[str, Any]] = None
    
    # Explanations
    score_explanations: Dict[str, str] = None
    
    def __post_init__(self):
        if self.score_explanations is None:
            self.score_explanations = {}


@dataclass
class RoutingDecision:
    """Routing decision for a promotion event."""
    
    # Routing targets
    semantic_memory: bool
    graph_edges: bool
    crm_projection: bool
    deliverables_db: bool
    
    # Status
    status: str  # 'promoted', 'queued_for_review', 'archived', 'blocked'
    reasoning: str


class PromotionGateScorer:
    """Core scoring engine for promotion candidates."""
    
    def __init__(self, config: ScoringConfig):
        self.config = config
        self.validator = IntelligenceValidator()
    
    def score_candidate(self, input_data: ScoringInput) -> ScoringResult:
        """Score a promotion candidate across all rubric dimensions."""
        
        # Score each dimension
        strategic_score = self._score_strategic_importance(input_data)
        relationship_score = self._score_relationship_delta(input_data)
        commitment_score = self._score_commitment_clarity(input_data)
        evidence_score = self._score_evidence_quality(input_data)
        novelty_score = self._score_novelty(input_data)
        execution_score = self._score_execution_value(input_data)
        
        # Calculate total
        total_score = (strategic_score + relationship_score + commitment_score + 
                      evidence_score + novelty_score + execution_score)
        
        # Determine tier based on score
        tier = self._assign_tier(total_score)
        
        # Check for hard overrides
        hard_override = self._check_hard_override(input_data, tier)
        if hard_override and hard_override['applied']:
            tier = 'A'  # Hard overrides always promote to A
        
        # Calculate confidence
        confidence = self._calculate_confidence(input_data, total_score)
        
        # Generate explanations
        explanations = self._generate_explanations(input_data, {
            'strategic_importance': strategic_score,
            'relationship_delta_strength': relationship_score,
            'commitment_clarity': commitment_score,
            'evidence_quality': evidence_score,
            'novelty': novelty_score,
            'execution_value': execution_score
        })
        
        return ScoringResult(
            strategic_importance=strategic_score,
            relationship_delta_strength=relationship_score,
            commitment_clarity=commitment_score,
            evidence_quality=evidence_score,
            novelty=novelty_score,
            execution_value=execution_score,
            total_score=total_score,
            tier=tier,
            confidence=confidence,
            hard_override=hard_override,
            score_explanations=explanations
        )
    
    def _extract_text_content(self, data: Dict[str, Any]) -> str:
        """Extract all text content from a candidate data structure."""
        content_parts = []
        
        # Extract from various text fields
        text_fields = ['content', 'description', 'summary', 'deliverable', 'reason']
        
        for field in text_fields:
            if field in data and isinstance(data[field], str):
                content_parts.append(data[field])
        
        # Extract from nested commitment details
        if 'commitment_details' in data:
            commitment = data['commitment_details']
            if isinstance(commitment, dict):
                for field in ['deliverable', 'description', 'details']:
                    if field in commitment and isinstance(commitment[field], str):
                        content_parts.append(commitment[field])
        
        # Extract from evidence quotes
        if 'evidence' in data and isinstance(data['evidence'], dict):
            evidence = data['evidence']
            quotes = evidence.get('quotes', [])
            for quote in quotes:
                if isinstance(quote, str):
                    content_parts.append(quote)
                elif isinstance(quote, dict) and 'text' in quote:
                    content_parts.append(quote['text'])
        
        # Extract from recommended approach
        if 'recommended_approach' in data and isinstance(data['recommended_approach'], str):
            content_parts.append(data['recommended_approach'])
        
        return ' '.join(content_parts)
    
    def _score_strategic_importance(self, input_data: ScoringInput) -> float:
        """Score strategic importance (0-20)."""
        score = 0.0
        
        candidate = input_data.candidate_data
        
        # Check for strategic keywords and context
        strategic_indicators = [
            'strategy', 'strategic', 'vision', 'roadmap', 'priorities',
            'investment', 'budget', 'acquisition', 'partnership',
            'competitive', 'market', 'growth', 'expansion'
        ]
        
        # Analyze candidate content for strategic signals
        content_text = self._extract_text_content(candidate)
        strategic_matches = sum(1 for indicator in strategic_indicators 
                               if indicator.lower() in content_text.lower())
        
        # Base score from strategic keyword density
        if strategic_matches >= 3:
            score += 15
        elif strategic_matches >= 1:
            score += 8
        else:
            score += 2
        
        # Bonus for executive/leadership involvement
        if input_data.meeting_context:
            participants = input_data.meeting_context.get('participants', [])
            executive_titles = ['ceo', 'cto', 'cfo', 'vp', 'director', 'head', 'lead']
            
            has_executives = any(any(title in participant.get('title', '').lower() 
                                   for title in executive_titles)
                               for participant in participants)
            
            if has_executives:
                score += 3
        
        # Cap at maximum
        score = min(score, self.config.strategic_importance_max)
        
        return score
    
    def _score_relationship_delta(self, input_data: ScoringInput) -> float:
        """Score relationship delta strength (0-20)."""
        score = 0.0
        
        candidate = input_data.candidate_data
        candidate_type = input_data.candidate_type
        
        # Base score depends on candidate type
        if candidate_type == 'relationship_delta':
            # Direct relationship delta - score based on significance
            delta_type = candidate.get('delta_type', '')
            
            significant_deltas = [
                'sentiment_shift', 'trust_change', 'authority_change',
                'decision_making_change', 'communication_pattern_change'
            ]
            
            if delta_type in significant_deltas:
                score += 12
            else:
                score += 6
            
            # Bonus for strong confidence
            confidence = candidate.get('confidence', 0)
            if confidence >= 0.8:
                score += 4
            elif confidence >= 0.6:
                score += 2
            
            # Bonus for evidence quality
            evidence = candidate.get('evidence', {})
            quotes = evidence.get('quotes', [])
            if len(quotes) >= 2:
                score += 4
            elif len(quotes) >= 1:
                score += 2
        
        elif candidate_type in ['org_delta', 'deliverable_record', 'intro_opportunity']:
            # Indirect relationship impact
            score += 8
            
            # Check for relationship implications in content
            content_text = self._extract_text_content(candidate)
            relationship_terms = ['trust', 'relationship', 'partnership', 'collaboration']
            
            relationship_matches = sum(1 for term in relationship_terms 
                                     if term in content_text.lower())
            score += min(relationship_matches * 2, 6)
        
        else:
            # General intelligence - minimal relationship delta
            score += 3
        
        # Cap at maximum
        score = min(score, self.config.relationship_delta_strength_max)
        
        return score
    
    def _score_commitment_clarity(self, input_data: ScoringInput) -> float:
        """Score commitment clarity (0-20)."""
        score = 0.0
        
        candidate = input_data.candidate_data
        candidate_type = input_data.candidate_type
        
        # Look for commitment indicators
        if candidate_type == 'deliverable_record':
            # Deliverables inherently have commitment structure
            score += 10
            
            # Bonus for clear commitment details
            commitment_details = candidate.get('commitment_details', {})
            if commitment_details:
                if 'promised_by' in commitment_details:
                    score += 3
                if 'deadline' in commitment_details:
                    score += 3
                if 'deliverable' in commitment_details and len(commitment_details['deliverable']) > 20:
                    score += 4
        
        elif candidate_type == 'intro_opportunity':
            # Introductions have moderate commitment clarity
            score += 6
            
            # Bonus for clear approach and priority
            if 'recommended_approach' in candidate:
                score += 4
            if candidate.get('priority') in ['high', 'medium']:
                score += 2
        
        else:
            # Look for commitment language in content
            content_text = self._extract_text_content(candidate)
            commitment_indicators = ['will', 'commit', 'promise', 'deliver', 'deadline', 'by', 'when']
            
            commitment_matches = sum(1 for indicator in commitment_indicators 
                                   if indicator.lower() in content_text.lower())
            
            if commitment_matches >= 3:
                score += 8
            elif commitment_matches >= 1:
                score += 4
            else:
                score += 1
        
        # Cap at maximum
        score = min(score, self.config.commitment_clarity_max)
        
        return score
    
    def _score_evidence_quality(self, input_data: ScoringInput) -> float:
        """Score evidence quality (0-15)."""
        score = 0.0
        
        candidate = input_data.candidate_data
        
        # Check for evidence structure
        evidence = candidate.get('evidence', {})
        
        if evidence:
            quotes = evidence.get('quotes', [])
            block_refs = evidence.get('block_references', [])
            
            # Score based on quote quantity and quality
            if len(quotes) >= 3:
                score += 8
            elif len(quotes) >= 2:
                score += 6  
            elif len(quotes) >= 1:
                score += 4
            
            # Score based on quote specificity
            if quotes:
                # Handle both string quotes and dict quotes with 'text' field
                quote_lengths = []
                for q in quotes:
                    if isinstance(q, str):
                        quote_lengths.append(len(q))
                    elif isinstance(q, dict):
                        quote_lengths.append(len(q.get('text', '')))
                    else:
                        quote_lengths.append(0)
                
                if quote_lengths:
                    avg_quote_length = sum(quote_lengths) / len(quote_lengths)
                    if avg_quote_length >= 50:
                        score += 3
                    elif avg_quote_length >= 20:
                        score += 2
                    else:
                        score += 1
            
            # Bonus for multiple block references
            if len(block_refs) >= 2:
                score += 2
            elif len(block_refs) >= 1:
                score += 1
            
            # Speaker diversity bonus
            speakers = set()
            for q in quotes:
                if isinstance(q, str):
                    speakers.add('unknown')
                elif isinstance(q, dict):
                    speakers.add(q.get('speaker', 'unknown'))
                else:
                    speakers.add('unknown')
            
            if len(speakers) >= 2:
                score += 2
        
        else:
            # No structured evidence - minimal score
            score = 1
        
        # Cap at maximum
        score = min(score, self.config.evidence_quality_max)
        
        return score
    
    def _score_novelty(self, input_data: ScoringInput) -> float:
        """Score novelty vs existing memory (0-15)."""
        score = 10  # Default assumption of medium novelty
        
        # Check against existing memory if provided
        existing_memory = input_data.existing_memory
        
        if existing_memory:
            # Compare candidate content against existing memory
            candidate_content = self._extract_text_content(input_data.candidate_data)
            
            # Simple similarity check (in real implementation, would use embeddings)
            similarity_count = 0
            for memory_item in existing_memory:
                memory_content = self._extract_text_content(memory_item)
                
                # Count overlapping words (simplified similarity)
                candidate_words = set(candidate_content.lower().split())
                memory_words = set(memory_content.lower().split())
                
                overlap = len(candidate_words.intersection(memory_words))
                if overlap > 5:  # Arbitrary threshold
                    similarity_count += 1
            
            # Adjust score based on similarity
            if similarity_count >= 3:
                score = 2  # Highly redundant
            elif similarity_count >= 1:
                score = 6  # Some redundancy
            else:
                score = 14  # Novel
        
        # Cap at maximum
        score = min(score, self.config.novelty_max)
        
        return score
    
    def _score_execution_value(self, input_data: ScoringInput) -> float:
        """Score execution value (0-10)."""
        score = 0.0
        
        candidate = input_data.candidate_data
        candidate_type = input_data.candidate_type
        
        # Score based on actionability
        if candidate_type == 'deliverable_record':
            # Deliverables have high execution value
            score += 6
            
            # Bonus for clear status and next steps
            if candidate.get('status') in ['identified', 'committed']:
                score += 2
            
            if 'next_steps' in candidate or 'commitment_details' in candidate:
                score += 2
        
        elif candidate_type == 'intro_opportunity':
            # Introductions are moderately actionable
            score += 4
            
            # Bonus for clear approach
            if 'recommended_approach' in candidate:
                score += 3
            
            if candidate.get('priority') == 'high':
                score += 2
            elif candidate.get('priority') == 'medium':
                score += 1
        
        elif candidate_type in ['relationship_delta', 'org_delta']:
            # Information has moderate execution value
            score += 3
            
            # Bonus for high confidence actionable intelligence
            confidence = candidate.get('confidence', 0)
            if confidence >= 0.8:
                score += 3
            elif confidence >= 0.6:
                score += 2
            elif confidence >= 0.4:
                score += 1
        
        else:
            # General intelligence has lower execution value
            score += 2
        
        # Cap at maximum  
        score = min(score, self.config.execution_value_max)
        
        return score
    
    def _assign_tier(self, total_score: float) -> str:
        """Assign tier based on total score."""
        if total_score >= self.config.tier_a_threshold:
            return 'A'
        elif total_score >= self.config.tier_b_threshold:
            return 'B'
        else:
            return 'C'
    
    def _check_hard_override(self, input_data: ScoringInput, current_tier: str) -> Optional[Dict[str, Any]]:
        """Check for hard override conditions."""
        
        candidate = input_data.candidate_data
        content_text = self._extract_text_content(candidate)
        
        # Check each override type
        for override_type, keywords in self.config.hard_override_keywords.items():
            for keyword in keywords:
                if keyword.lower() in content_text.lower():
                    return {
                        'applied': True,
                        'reason': override_type,
                        'original_tier': current_tier,
                        'trigger_keyword': keyword
                    }
        
        # No override found
        return {'applied': False}
    
    def _calculate_confidence(self, input_data: ScoringInput, total_score: float) -> float:
        """Calculate overall confidence in the scoring assessment."""
        
        confidence_factors = []
        
        # Evidence quality contributes to confidence
        evidence = input_data.candidate_data.get('evidence', {})
        if evidence:
            quotes_count = len(evidence.get('quotes', []))
            evidence_confidence = min(quotes_count * 0.2, 0.6)
            confidence_factors.append(evidence_confidence)
        else:
            confidence_factors.append(0.2)
        
        # Candidate type confidence
        type_confidence = {
            'relationship_delta': 0.8,
            'org_delta': 0.7,
            'deliverable_record': 0.9,
            'intro_opportunity': 0.7,
            'general_intelligence': 0.5
        }
        confidence_factors.append(type_confidence.get(input_data.candidate_type, 0.5))
        
        # Score consistency confidence (higher scores more confident)
        score_confidence = min(total_score / 100, 0.9)
        confidence_factors.append(score_confidence)
        
        # Return average of confidence factors
        return sum(confidence_factors) / len(confidence_factors)
    
    def _generate_explanations(self, input_data: ScoringInput, scores: Dict[str, float]) -> Dict[str, str]:
        """Generate human-readable explanations for scores."""
        
        explanations = {}
        candidate_type = input_data.candidate_type
        
        # Strategic importance explanation
        strategic_score = scores['strategic_importance']
        if strategic_score >= 15:
            explanations['strategic_importance'] = "High strategic relevance with clear business impact"
        elif strategic_score >= 8:
            explanations['strategic_importance'] = "Moderate strategic relevance"
        else:
            explanations['strategic_importance'] = "Limited strategic significance"
        
        # Relationship delta explanation
        relationship_score = scores['relationship_delta_strength']
        if candidate_type == 'relationship_delta':
            if relationship_score >= 15:
                explanations['relationship_delta_strength'] = "Strong relationship change with high confidence"
            elif relationship_score >= 8:
                explanations['relationship_delta_strength'] = "Notable relationship shift"
            else:
                explanations['relationship_delta_strength'] = "Minor relationship impact"
        else:
            if relationship_score >= 10:
                explanations['relationship_delta_strength'] = "Significant relationship implications"
            elif relationship_score >= 5:
                explanations['relationship_delta_strength'] = "Some relationship impact"
            else:
                explanations['relationship_delta_strength'] = "Minimal relationship effects"
        
        # Add explanations for other dimensions
        explanations['commitment_clarity'] = self._explain_commitment_score(scores['commitment_clarity'])
        explanations['evidence_quality'] = self._explain_evidence_score(scores['evidence_quality'])
        explanations['novelty'] = self._explain_novelty_score(scores['novelty'])
        explanations['execution_value'] = self._explain_execution_score(scores['execution_value'], candidate_type)
        
        return explanations
    
    def _explain_commitment_score(self, score: float) -> str:
        """Generate explanation for commitment clarity score."""
        if score >= 15:
            return "Clear commitments with specific details"
        elif score >= 10:
            return "Some commitment clarity"
        elif score >= 5:
            return "Vague or weak commitments"
        else:
            return "Unclear or no commitments"
    
    def _explain_evidence_score(self, score: float) -> str:
        """Generate explanation for evidence quality score."""
        if score >= 10:
            return "Strong evidence with multiple quotes"
        elif score >= 6:
            return "Moderate evidence quality"
        elif score >= 3:
            return "Some supporting evidence"
        else:
            return "Weak or no evidence"
    
    def _explain_novelty_score(self, score: float) -> str:
        """Generate explanation for novelty score."""
        if score >= 12:
            return "Novel information not in memory"
        elif score >= 8:
            return "Somewhat new information"
        elif score >= 5:
            return "Mixed new and existing information"
        else:
            return "Largely redundant with existing memory"
    
    def _explain_execution_score(self, score: float, candidate_type: str) -> str:
        """Generate explanation for execution value score."""
        if candidate_type == 'deliverable_record':
            if score >= 8:
                return "High actionability with clear next steps"
            elif score >= 6:
                return "Good actionability"
            else:
                return "Limited actionability"
        else:
            if score >= 6:
                return "High execution value"
            elif score >= 4:
                return "Moderate execution value"
            else:
                return "Low execution value"


class PromotionGateRouter:
    """Routing logic for promotion events."""
    
    def __init__(self, config: ScoringConfig):
        self.config = config
    
    def determine_routing(self, scoring_result: ScoringResult, candidate_type: str) -> RoutingDecision:
        """Determine routing for a scored promotion candidate."""
        
        tier = scoring_result.tier
        
        # Get base routing for tier
        base_routing = self.config.routing_rules[tier].copy()
        
        # Determine status based on tier
        if tier == 'A':
            status = 'promoted'
        elif tier == 'B':
            status = 'queued_for_review'
        else:  # tier == 'C'
            status = 'archived'
        
        # Apply hard override routing logic
        if scoring_result.hard_override and scoring_result.hard_override.get('applied'):
            # Hard overrides get Tier A routing
            base_routing = self.config.routing_rules['A'].copy()
            status = 'promoted'
            reasoning = f"Hard override: {scoring_result.hard_override['reason']}"
        else:
            reasoning = f"Tier {tier} routing based on score {scoring_result.total_score}"
        
        # Apply candidate-type specific routing adjustments
        routing = self._apply_candidate_type_routing(base_routing, candidate_type)
        
        return RoutingDecision(
            semantic_memory=routing['semantic_memory'],
            graph_edges=routing['graph_edges'],
            crm_projection=routing['crm_projection'],
            deliverables_db=routing['deliverables_db'],
            status=status,
            reasoning=reasoning
        )
    
    def _apply_candidate_type_routing(self, base_routing: Dict[str, bool], candidate_type: str) -> Dict[str, bool]:
        """Apply candidate type specific routing logic."""
        
        routing = base_routing.copy()
        
        # Type-specific adjustments
        if candidate_type == 'deliverable_record':
            # Deliverables always go to deliverables DB if any routing is active
            if any(base_routing.values()):
                routing['deliverables_db'] = True
        
        elif candidate_type == 'intro_opportunity':
            # Intros don't need deliverables DB
            routing['deliverables_db'] = False
        
        elif candidate_type in ['relationship_delta', 'org_delta']:
            # Deltas always update graphs and CRM if any routing is active
            if any(base_routing.values()):
                routing['graph_edges'] = True
                routing['crm_projection'] = True
        
        return routing


class PromotionGateEngine:
    """Main promotion gate engine that orchestrates scoring and routing."""
    
    def __init__(self, config: Optional[ScoringConfig] = None):
        self.config = config or ScoringConfig()
        self.scorer = PromotionGateScorer(self.config)
        self.router = PromotionGateRouter(self.config)
        self.validator = IntelligenceValidator()
        self.promotion_validator = PromotionGateValidator()
        
        # Validate configuration
        config_errors = self.config.validate()
        if config_errors:
            raise ValueError(f"Invalid configuration: {config_errors}")
    
    def process_candidate(self, 
                         input_data: ScoringInput,
                         dry_run: bool = False) -> Dict[str, Any]:
        """Process a promotion candidate through the gate."""
        
        try:
            # Step 1: Score the candidate
            scoring_result = self.scorer.score_candidate(input_data)
            
            # Step 2: Determine routing
            routing_decision = self.router.determine_routing(scoring_result, input_data.candidate_type)
            
            # Step 3: Create promotion event
            promotion_event = self._create_promotion_event(
                input_data, scoring_result, routing_decision, dry_run
            )
            
            # Step 4: Validate the event
            is_valid, validation_errors = self.promotion_validator.validate_promotion_event(promotion_event)
            
            if not is_valid:
                logger.warning(f"Promotion event validation failed: {validation_errors}")
                # Continue processing but mark issues
                promotion_event['validation_errors'] = validation_errors
            
            # Step 5: Generate audit report if dry run
            if dry_run:
                audit_report = self._generate_audit_report(input_data, scoring_result, routing_decision)
                promotion_event['audit_report'] = audit_report
            
            return promotion_event
            
        except Exception as e:
            logger.error(f"Error processing candidate: {str(e)}")
            return {
                'error': str(e),
                'input_data': asdict(input_data),
                'processing_failed': True
            }
    
    def _create_promotion_event(self, 
                               input_data: ScoringInput,
                               scoring_result: ScoringResult,
                               routing_decision: RoutingDecision,
                               dry_run: bool) -> Dict[str, Any]:
        """Create a complete promotion event record."""
        
        # Generate unique event ID
        event_id = self.validator.generate_id("pe_")
        
        # Create the core event
        promotion_event = {
            'event_id': event_id,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'source_meeting_id': input_data.source_meeting_id,
            'candidate_type': input_data.candidate_type,
            'candidate_id': input_data.candidate_data.get('id', ''),
            'score': scoring_result.total_score,
            'score_breakdown': {
                'strategic_importance': scoring_result.strategic_importance,
                'relationship_delta_strength': scoring_result.relationship_delta_strength,
                'commitment_clarity': scoring_result.commitment_clarity,
                'evidence_quality': scoring_result.evidence_quality,
                'novelty': scoring_result.novelty,
                'execution_value': scoring_result.execution_value
            },
            'tier': scoring_result.tier,
            'hard_override': scoring_result.hard_override or {'applied': False},
            'deduplication': {'checked': False},  # TODO: Implement deduplication
            'status': routing_decision.status,
            'routing': {
                'semantic_memory': routing_decision.semantic_memory,
                'graph_edges': routing_decision.graph_edges,
                'crm_projection': routing_decision.crm_projection,
                'deliverables_db': routing_decision.deliverables_db
            },
            'idempotency_key': f"{input_data.source_meeting_id}_{input_data.candidate_type}_{event_id}",
            'processing_mode': 'dry_run' if dry_run else input_data.processing_mode,
            'provenance': self.validator.create_provenance(
                processor_version="1.0.0",
                conversation_id=input_data.conversation_id,
                processing_mode='dry_run' if dry_run else input_data.processing_mode,
                source_blocks=input_data.source_blocks
            ),
            'confidence': scoring_result.confidence
        }
        
        # Add score explanations as metadata (will trigger validation warning but that's expected)
        if scoring_result.score_explanations:
            promotion_event['score_explanations'] = scoring_result.score_explanations
        
        # Add routing reasoning  
        promotion_event['routing_reasoning'] = routing_decision.reasoning
        
        return promotion_event
    
    def _generate_audit_report(self, 
                              input_data: ScoringInput,
                              scoring_result: ScoringResult,
                              routing_decision: RoutingDecision) -> Dict[str, Any]:
        """Generate detailed audit report for dry run mode."""
        
        return {
            'input_summary': {
                'candidate_type': input_data.candidate_type,
                'source_meeting_id': input_data.source_meeting_id,
                'processing_mode': input_data.processing_mode
            },
            'scoring_details': {
                'total_score': scoring_result.total_score,
                'tier_assigned': scoring_result.tier,
                'confidence': scoring_result.confidence,
                'score_breakdown': {
                    'strategic_importance': {
                        'score': scoring_result.strategic_importance,
                        'max_possible': self.config.strategic_importance_max,
                        'explanation': scoring_result.score_explanations.get('strategic_importance', '')
                    },
                    'relationship_delta_strength': {
                        'score': scoring_result.relationship_delta_strength,
                        'max_possible': self.config.relationship_delta_strength_max,
                        'explanation': scoring_result.score_explanations.get('relationship_delta_strength', '')
                    },
                    'commitment_clarity': {
                        'score': scoring_result.commitment_clarity,
                        'max_possible': self.config.commitment_clarity_max,
                        'explanation': scoring_result.score_explanations.get('commitment_clarity', '')
                    },
                    'evidence_quality': {
                        'score': scoring_result.evidence_quality,
                        'max_possible': self.config.evidence_quality_max,
                        'explanation': scoring_result.score_explanations.get('evidence_quality', '')
                    },
                    'novelty': {
                        'score': scoring_result.novelty,
                        'max_possible': self.config.novelty_max,
                        'explanation': scoring_result.score_explanations.get('novelty', '')
                    },
                    'execution_value': {
                        'score': scoring_result.execution_value,
                        'max_possible': self.config.execution_value_max,
                        'explanation': scoring_result.score_explanations.get('execution_value', '')
                    }
                }
            },
            'hard_override_analysis': {
                'applied': scoring_result.hard_override.get('applied', False) if scoring_result.hard_override else False,
                'details': scoring_result.hard_override if scoring_result.hard_override and scoring_result.hard_override.get('applied') else None
            },
            'routing_decision': {
                'status': routing_decision.status,
                'reasoning': routing_decision.reasoning,
                'targets': {
                    'semantic_memory': routing_decision.semantic_memory,
                    'graph_edges': routing_decision.graph_edges,
                    'crm_projection': routing_decision.crm_projection,
                    'deliverables_db': routing_decision.deliverables_db
                }
            },
            'configuration_used': {
                'tier_thresholds': {
                    'A': self.config.tier_a_threshold,
                    'B': self.config.tier_b_threshold,
                    'C': self.config.tier_c_threshold
                },
                'score_maximums': {
                    'strategic_importance': self.config.strategic_importance_max,
                    'relationship_delta_strength': self.config.relationship_delta_strength_max,
                    'commitment_clarity': self.config.commitment_clarity_max,
                    'evidence_quality': self.config.evidence_quality_max,
                    'novelty': self.config.novelty_max,
                    'execution_value': self.config.execution_value_max
                }
            }
        }


# CLI Interface for testing and development
def main():
    """CLI interface for the promotion gate engine."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Promotion Gate Engine')
    parser.add_argument('--config', type=str, help='Path to configuration file')
    parser.add_argument('--input', type=str, required=True, help='Path to input JSON file')
    parser.add_argument('--output', type=str, help='Path to output file (default: stdout)')
    parser.add_argument('--dry-run', action='store_true', help='Run in dry-run mode with audit report')
    parser.add_argument('--verbose', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    # Set up logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Load configuration
        config = ScoringConfig()
        if args.config:
            with open(args.config, 'r') as f:
                config_data = json.load(f)
                # Update config with loaded data
                for key, value in config_data.items():
                    if hasattr(config, key):
                        setattr(config, key, value)
        
        # Load input data
        with open(args.input, 'r') as f:
            input_data_dict = json.load(f)
        
        # Convert to ScoringInput
        input_data = ScoringInput(**input_data_dict)
        
        # Create engine and process
        engine = PromotionGateEngine(config)
        result = engine.process_candidate(input_data, dry_run=args.dry_run)
        
        # Output result
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"Result written to {args.output}")
        else:
            print(json.dumps(result, indent=2))
    
    except Exception as e:
        logger.error(f"CLI execution failed: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()