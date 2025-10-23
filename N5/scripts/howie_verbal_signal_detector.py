#!/usr/bin/env python3
"""
Howie Verbal Signal Detector

Detects natural language patterns from meeting transcripts that indicate
Howie tag preferences. Maps verbal breadcrumbs to specific V-OS tags.

Based on: N5/docs/howie-verbal-signals.md
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum


class SignalConfidence(Enum):
    """Confidence levels for detected signals"""
    HIGH = 0.9  # Explicit, unambiguous
    MEDIUM = 0.7  # Contextual clues
    LOW = 0.5  # Vague or ambiguous


@dataclass
class DetectedSignal:
    """A detected verbal signal"""
    signal_type: str  # urgency, accommodation, priority, etc.
    value: str  # specific value (urgent, high, A-2, GPT-E, etc.)
    confidence: float
    matched_phrase: str
    reasoning: str


@dataclass
class SignalAnalysis:
    """Complete analysis of verbal signals"""
    signals: List[DetectedSignal] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)
    overall_confidence: float = 0.0
    
    def get_signals_by_type(self, signal_type: str) -> List[DetectedSignal]:
        """Get all signals of a specific type"""
        return [s for s in self.signals if s.signal_type == signal_type]
    
    def get_best_signal(self, signal_type: str) -> Optional[DetectedSignal]:
        """Get highest confidence signal of a type"""
        type_signals = self.get_signals_by_type(signal_type)
        if not type_signals:
            return None
        return max(type_signals, key=lambda s: s.confidence)


class HowieVerbalSignalDetector:
    """Detects verbal signals for Howie tag generation"""
    
    # Signal patterns: (pattern, signal_type, value, confidence, reasoning)
    SIGNAL_PATTERNS = [
        # === URGENCY SIGNALS ===
        
        # High confidence urgent
        (r'\b(urgent|asap|immediately|emergency|critical|time[- ]sensitive)\b',
         'urgency', 'urgent', SignalConfidence.HIGH,
         'Explicit urgency language'),
        
        (r'\b(this week ideally (tomorrow|next day|in the next (day|two)))\b',
         'urgency', 'urgent', SignalConfidence.HIGH,
         'Very tight timeline specified'),
        
        (r'\b(next (48 hours|two days|couple days))\b',
         'urgency', 'urgent', SignalConfidence.HIGH,
         'Explicit 48-hour window'),
        
        # Medium confidence high urgency
        (r'\b(this week|next few days|sooner rather than later|pressing|soon)\b',
         'urgency', 'high', SignalConfidence.MEDIUM,
         'Time-sensitive but not emergency'),
        
        (r'\b(by (end of|this) week|before friday|by friday)\b',
         'urgency', 'high', SignalConfidence.MEDIUM,
         'Explicit week deadline'),
        
        # Low/normal urgency
        (r'\b(no (particular )?rush|no hurry|whenever|next week or two)\b',
         'urgency', 'normal', SignalConfidence.HIGH,
         'Explicit "no rush" signal'),
        
        (r'\b((next|in the) (week or two|couple weeks))\b',
         'urgency', 'normal', SignalConfidence.MEDIUM,
         'Flexible 1-2 week window'),
        
        # === ACCOMMODATION SIGNALS ===
        
        # High accommodation (A-2)
        (r'\b(work around your schedule|whatever works (best )?for you|totally flexible|super flexible)\b',
         'accommodation', 'A-2', SignalConfidence.HIGH,
         'Explicit high accommodation language'),
        
        (r'\b(make it work|i\'?ll make one of them (work|happen))\b',
         'accommodation', 'A-2', SignalConfidence.MEDIUM,
         'Commitment to accommodate'),
        
        # Balanced accommodation (A-1)
        (r'\b(let me know (what|some times) (that work|works for you))\b',
         'accommodation', 'A-1', SignalConfidence.MEDIUM,
         'Requesting their availability'),
        
        (r'\b(send (me|you) some (times|options))\b',
         'accommodation', 'A-1', SignalConfidence.MEDIUM,
         'Proposing times'),
        
        (r'\b(i\'?ll (send|propose) )\b',
         'accommodation_proactive', 'propose_times', SignalConfidence.MEDIUM,
         'Proactive scheduling (Howie proposes)'),
        
        (r'\b(my assistant will (reach out|send|contact))\b',
         'accommodation_proactive', 'propose_times', SignalConfidence.HIGH,
         'Assistant will propose times'),
        
        # Minimal accommodation (A-0)
        (r'\b(on our terms|when (it works|we\'?re available) for us|if we have availability)\b',
         'accommodation', 'A-0', SignalConfidence.HIGH,
         'Minimal accommodation, our convenience only'),
        
        (r'\b(i\'?ll check (my|our) calendar and let you know)\b',
         'accommodation', 'A-0', SignalConfidence.MEDIUM,
         'Internal-first scheduling'),
        
        # === PRIORITY SIGNALS ===
        
        # External priority (GPT-E)
        (r'\b(what does your schedule look like|what times (are )?good for you)\b',
         'priority', 'GPT-E', SignalConfidence.HIGH,
         'Deferring to external preferences'),
        
        (r'\b(work around your|accommodate you|your convenience)\b',
         'priority', 'GPT-E', SignalConfidence.HIGH,
         'Prioritizing external stakeholder'),
        
        # Founders priority (GPT-F)
        (r'\b(both (of us|founders)|founders should|the founders)\b',
         'priority', 'GPT-F', SignalConfidence.HIGH,
         'Both founders mentioned'),
        
        # Internal priority (GPT-I)
        (r'\b((when|if) (it works|we have time) for us)\b',
         'priority', 'GPT-I', SignalConfidence.HIGH,
         'Internal-first priority'),
        
        # === ALIGNMENT SIGNALS ===
        
        # Logan
        (r'\b(logan should (join|be (there|on|included)))\b',
         'alignment', 'LOG', SignalConfidence.HIGH,
         'Explicit Logan inclusion'),
        
        (r'\b(get logan (on|involved)|see when logan is free|check with logan)\b',
         'alignment', 'LOG', SignalConfidence.HIGH,
         'Need Logan availability'),
        
        (r'\blogan\b(?! ?@)',  # "logan" but not "logan@email"
         'alignment', 'LOG', SignalConfidence.MEDIUM,
         'Logan mentioned in scheduling context'),
        
        # Ilias
        (r'\b(ilias should (join|be (there|on|included)))\b',
         'alignment', 'ILS', SignalConfidence.HIGH,
         'Explicit Ilias inclusion'),
        
        (r'\b(check with ilias|see when ilias is free)\b',
         'alignment', 'ILS', SignalConfidence.HIGH,
         'Need Ilias availability'),
        
        # === STAKEHOLDER TYPE SIGNALS ===
        
        # Investor (LD-INV)
        (r'\b(investor|funding|fundraising|our (seed|series|round)|raise|pitch deck)\b',
         'stakeholder_type', 'investor', SignalConfidence.HIGH,
         'Investor-related language'),
        
        (r'\b(vc|venture capital|investment opportunity)\b',
         'stakeholder_type', 'investor', SignalConfidence.HIGH,
         'Investor/VC context'),
        
        # Hiring (LD-HIR)
        (r'\b(interview|candidate|role|position|hire|hiring|job)\b',
         'stakeholder_type', 'hire', SignalConfidence.MEDIUM,
         'Hiring/recruiting context'),
        
        (r'\b(technical co-founder search|looking for (a )?co-founder)\b',
         'stakeholder_type', 'hire', SignalConfidence.HIGH,
         'Co-founder search'),
        
        # Community (LD-COM)
        (r'\b((let\'?s )?explore (a )?partnership|collaboration opportunity|work together)\b',
         'stakeholder_type', 'community', SignalConfidence.HIGH,
         'Partnership/collaboration language'),
        
        (r'\b(ecosystem|community|founder|startup community)\b',
         'stakeholder_type', 'community', SignalConfidence.MEDIUM,
         'Community/ecosystem context'),
        
        # Networking (LD-NET)
        (r'\b(pick your brain|get your (thoughts|feedback|perspective)|would love your (input|advice))\b',
         'stakeholder_type', 'networking', SignalConfidence.HIGH,
         'Advisory/networking language'),
        
        (r'\b(coffee chat|quick chat|informational)\b',
         'stakeholder_type', 'networking', SignalConfidence.MEDIUM,
         'Casual networking context'),
        
        # === FOLLOW-UP SIGNALS ===
        
        # Explicit follow-up with timeline
        (r'\b(i\'?ll follow up in (\d+) days?)\b',
         'follow_up', 'F-\\2', SignalConfidence.HIGH,
         'Explicit follow-up timeline'),
        
        (r'\b(if (i|we) don\'?t hear back (by|in) (\d+) days?)\b',
         'follow_up', 'F-\\4', SignalConfidence.HIGH,
         'Conditional follow-up with timeline'),
        
        (r'\b(i\'?ll (check back|reconnect) (next week|in a week))\b',
         'follow_up', 'F-7', SignalConfidence.MEDIUM,
         '"Next week" follow-up'),
        
        (r'\b(i\'?ll ping you again|follow up again|circle back)\b',
         'follow_up', 'follow_up_needed', SignalConfidence.MEDIUM,
         'Follow-up needed (timeline unclear)'),
        
        # === FLEXIBILITY SIGNALS ===
        
        # Same-day flexibility (FLX)
        (r'\b(totally flexible|anytime that day|morning or afternoon both work|super flexible)\b',
         'flexibility', 'FLX', SignalConfidence.HIGH,
         'Explicit same-day flexibility'),
        
        # Weekend signals
        (r'\b(weekend works|saturday (or )?sunday (could work|works))\b',
         'flexibility', 'WEX', SignalConfidence.HIGH,
         'Weekend acceptable'),
        
        (r'\b(prefer (a )?weekend|weekends are (actually )?easier)\b',
         'flexibility', 'WEP', SignalConfidence.HIGH,
         'Weekend preferred'),
        
        # === TERMINATION SIGNALS ===
        
        # Terminate (TERM)
        (r'\b(put (a )?pin in this|not the right time|let\'?s revisit|put this on hold)\b',
         'termination', 'TERM', SignalConfidence.HIGH,
         'Explicit termination of scheduling'),
        
        (r'\b(let\'?s reconnect in (a few months|q\d))\b',
         'termination', 'TERM', SignalConfidence.HIGH,
         'Long-term deferral'),
        
        # Ignore (INC)
        (r'\b((doesn\'?t|don\'?t) need a meeting|handle (this|it) over email|no need to meet)\b',
         'termination', 'INC', SignalConfidence.HIGH,
         'Meeting not necessary'),
        
        # === CRM PREFERENCE SIGNALS ===
        
        # Store preference
        (r'\b(make a note that (they|he|she) prefer[s]?)\b',
         'crm_action', 'store_preference', SignalConfidence.HIGH,
         'Explicit preference storage request'),
        
        (r'\b(they\'?re in (.+) time)\b',
         'crm_action', 'store_timezone', SignalConfidence.HIGH,
         'Timezone information'),
        
        (r'\b(flag this as (a )?(warm|hot|high[- ]priority) (lead|relationship))\b',
         'crm_action', 'update_relationship_stage', SignalConfidence.HIGH,
         'Relationship classification'),
    ]
    
    def __init__(self):
        self.compiled_patterns = [
            (re.compile(pattern, re.IGNORECASE), sig_type, value, conf, reason)
            for pattern, sig_type, value, conf, reason in self.SIGNAL_PATTERNS
        ]
    
    def analyze_text(self, text: str) -> SignalAnalysis:
        """Analyze text for verbal signals"""
        analysis = SignalAnalysis()
        
        # Detect all signals
        for pattern, sig_type, value, confidence, reasoning in self.compiled_patterns:
            matches = pattern.finditer(text)
            for match in matches:
                # Interpolate captured groups into value (for F-X patterns)
                interpolated_value = value
                for i, group in enumerate(match.groups(), 1):
                    if group:
                        interpolated_value = interpolated_value.replace(f'\\{i}', group)
                
                signal = DetectedSignal(
                    signal_type=sig_type,
                    value=interpolated_value,
                    confidence=confidence.value,
                    matched_phrase=match.group(0),
                    reasoning=reasoning
                )
                analysis.signals.append(signal)
        
        # Detect conflicts
        analysis.conflicts = self._detect_conflicts(analysis.signals)
        
        # Calculate overall confidence
        if analysis.signals:
            analysis.overall_confidence = sum(s.confidence for s in analysis.signals) / len(analysis.signals)
        
        return analysis
    
    def _detect_conflicts(self, signals: List[DetectedSignal]) -> List[str]:
        """Detect conflicting signals"""
        conflicts = []
        
        # Check urgency conflicts
        urgency_signals = [s for s in signals if s.signal_type == 'urgency']
        urgency_values = set(s.value for s in urgency_signals)
        if 'urgent' in urgency_values and 'normal' in urgency_values:
            conflicts.append("CONFLICT: Both 'urgent' and 'no rush' detected")
        
        # Check accommodation conflicts
        acc_signals = [s for s in signals if s.signal_type == 'accommodation']
        acc_values = set(s.value for s in acc_signals)
        if 'A-0' in acc_values and 'A-2' in acc_values:
            conflicts.append("CONFLICT: Both 'on our terms' and 'work around their schedule' detected")
        
        # Check priority conflicts
        pri_signals = [s for s in signals if s.signal_type == 'priority']
        pri_values = set(s.value for s in pri_signals)
        if 'GPT-I' in pri_values and 'GPT-E' in pri_values:
            conflicts.append("CONFLICT: Both 'internal priority' and 'external priority' detected")
        
        return conflicts
    
    def generate_recommendations(self, analysis: SignalAnalysis) -> Dict[str, any]:
        """Generate Howie tag recommendations from detected signals"""
        recommendations = {
            'tags': [],
            'confidence': analysis.overall_confidence,
            'reasoning': [],
            'conflicts': analysis.conflicts,
            'crm_actions': []
        }
        
        # Urgency
        urgency_signal = analysis.get_best_signal('urgency')
        if urgency_signal:
            if urgency_signal.value == 'urgent':
                recommendations['tags'].append('!!')
                recommendations['reasoning'].append(f"Urgent: {urgency_signal.matched_phrase}")
            elif urgency_signal.value == 'high':
                recommendations['tags'].append('D5')
                recommendations['reasoning'].append(f"High urgency: {urgency_signal.matched_phrase}")
            else:
                recommendations['tags'].append('D5+')
                recommendations['reasoning'].append(f"Normal timeline: {urgency_signal.matched_phrase}")
        
        # Stakeholder type
        stakeholder_signal = analysis.get_best_signal('stakeholder_type')
        if stakeholder_signal:
            type_map = {
                'investor': 'LD-INV',
                'hire': 'LD-HIR',
                'community': 'LD-COM',
                'networking': 'LD-NET'
            }
            tag = type_map.get(stakeholder_signal.value, 'LD-GEN')
            recommendations['tags'].append(tag)
            recommendations['reasoning'].append(f"Type: {stakeholder_signal.matched_phrase}")
        
        # Priority
        priority_signal = analysis.get_best_signal('priority')
        if priority_signal:
            recommendations['tags'].append(priority_signal.value)
            recommendations['reasoning'].append(f"Priority: {priority_signal.matched_phrase}")
        
        # Accommodation
        acc_signal = analysis.get_best_signal('accommodation')
        if acc_signal:
            recommendations['tags'].append(acc_signal.value)
            recommendations['reasoning'].append(f"Accommodation: {acc_signal.matched_phrase}")
        
        # Alignment
        alignment_signals = analysis.get_signals_by_type('alignment')
        for sig in alignment_signals:
            if sig.value not in recommendations['tags']:
                recommendations['tags'].append(sig.value)
                recommendations['reasoning'].append(f"Align with: {sig.matched_phrase}")
        
        # Follow-up
        followup_signal = analysis.get_best_signal('follow_up')
        if followup_signal and followup_signal.value.startswith('F-'):
            recommendations['tags'].append(followup_signal.value)
            recommendations['reasoning'].append(f"Follow-up: {followup_signal.matched_phrase}")
        
        # Flexibility
        flex_signals = analysis.get_signals_by_type('flexibility')
        for sig in flex_signals:
            if sig.value not in recommendations['tags']:
                recommendations['tags'].append(sig.value)
                recommendations['reasoning'].append(f"Flexibility: {sig.matched_phrase}")
        
        # Termination
        term_signal = analysis.get_best_signal('termination')
        if term_signal:
            recommendations['tags'] = [term_signal.value]  # Override all other tags
            recommendations['reasoning'] = [f"Termination: {term_signal.matched_phrase}"]
        
        # CRM actions
        crm_signals = analysis.get_signals_by_type('crm_action')
        for sig in crm_signals:
            recommendations['crm_actions'].append({
                'action': sig.value,
                'context': sig.matched_phrase,
                'confidence': sig.confidence
            })
        
        # Add activation symbol if we have tags
        if recommendations['tags'] and recommendations['tags'][0] not in ['TERM', 'INC']:
            recommendations['tags'].append('*')
        
        return recommendations


def main():
    """CLI for testing verbal signal detection"""
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="Detect Howie verbal signals from text")
    parser.add_argument('--text', help="Text to analyze")
    parser.add_argument('--file', help="File containing text to analyze")
    parser.add_argument('--output-format', choices=['text', 'json'], default='text')
    
    args = parser.parse_args()
    
    if args.text:
        text = args.text
    elif args.file:
        with open(args.file) as f:
            text = f.read()
    else:
        # Example text
        text = "This is urgent - we need to meet this week. Logan should join, and I'm happy to work around your schedule."
    
    detector = HowieVerbalSignalDetector()
    analysis = detector.analyze_text(text)
    recommendations = detector.generate_recommendations(analysis)
    
    if args.output_format == 'json':
        output = {
            'signals': [
                {
                    'type': s.signal_type,
                    'value': s.value,
                    'confidence': s.confidence,
                    'matched': s.matched_phrase,
                    'reasoning': s.reasoning
                }
                for s in analysis.signals
            ],
            'recommendations': recommendations
        }
        print(json.dumps(output, indent=2))
    else:
        print("=" * 60)
        print("DETECTED SIGNALS")
        print("=" * 60)
        
        if not analysis.signals:
            print("No signals detected")
        else:
            for signal in analysis.signals:
                print(f"\n{signal.signal_type.upper()}: {signal.value}")
                print(f"  Matched: \"{signal.matched_phrase}\"")
                print(f"  Confidence: {signal.confidence:.0%}")
                print(f"  Reasoning: {signal.reasoning}")
        
        if analysis.conflicts:
            print("\n" + "=" * 60)
            print("⚠️  CONFLICTS DETECTED")
            print("=" * 60)
            for conflict in analysis.conflicts:
                print(f"- {conflict}")
        
        print("\n" + "=" * 60)
        print("RECOMMENDED TAGS")
        print("=" * 60)
        print(" ".join(f"[{tag}]" if tag != "*" else tag for tag in recommendations['tags']))
        
        if recommendations['reasoning']:
            print("\nReasoning:")
            for reason in recommendations['reasoning']:
                print(f"  - {reason}")
        
        if recommendations['crm_actions']:
            print("\nCRM Actions:")
            for action in recommendations['crm_actions']:
                print(f"  - {action['action']}: {action['context']}")
        
        print(f"\nOverall Confidence: {recommendations['confidence']:.0%}")


if __name__ == "__main__":
    main()
