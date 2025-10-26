#!/usr/bin/env python3
"""
Content Type Detection
Automatically detects content type from context and request patterns.

Part of system-wide voice transformation system.
"""

import re
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class DetectionResult:
    """Result of content type detection"""
    content_type: str
    confidence: float
    signals: List[str]
    metadata: Dict


class ContentTypeDetector:
    """
    Detects content type from user request and context.
    
    Supported types:
    - email: Professional emails, messages
    - blog: Blog posts, articles, long-form
    - doc: Documents, notes, internal memos
    - social: LinkedIn, Twitter, social media
    - note: Quick notes, jottings, scratch
    """
    
    # Pattern definitions for detection
    PATTERNS = {
        "email": {
            "keywords": [
                "email", "message", "send to", "reply", "respond",
                "draft email", "write email", "compose"
            ],
            "indicators": [
                r"send.*to\s+\w+@",  # email addresses
                r"reply.*to",
                r"subject:",
                r"dear\s+\w+",
                r"hi\s+\w+",
            ],
            "file_extensions": [".eml", ".msg"],
        },
        "blog": {
            "keywords": [
                "blog", "article", "post", "write about",
                "long-form", "essay", "piece"
            ],
            "indicators": [
                r"publish",
                r"blog post",
                r"article about",
                r"\d+\s*words?",  # word count mentions
            ],
            "file_extensions": [".md", ".html"],
        },
        "doc": {
            "keywords": [
                "document", "memo", "note", "doc", "internal",
                "write down", "record", "document"
            ],
            "indicators": [
                r"internal\s+memo",
                r"document.*for",
                r"take notes",
                r"meeting notes",
            ],
            "file_extensions": [".md", ".txt", ".docx", ".gdoc"],
        },
        "social": {
            "keywords": [
                "linkedin", "twitter", "social", "tweet",
                "post", "share", "thread"
            ],
            "indicators": [
                r"linkedin post",
                r"twitter thread",
                r"social media",
                r"#\w+",  # hashtags
            ],
            "file_extensions": [],
        },
        "note": {
            "keywords": [
                "note", "jot", "quick", "reminder",
                "scratch", "draft"
            ],
            "indicators": [
                r"quick note",
                r"jot down",
                r"reminder",
            ],
            "file_extensions": [".txt", ".md"],
        },
    }
    
    def __init__(self):
        """Initialize detector"""
        self.type_priority = ["social", "email", "blog", "doc", "note"]
    
    def detect(
        self,
        user_request: str,
        context: Optional[Dict] = None
    ) -> DetectionResult:
        """
        Detect content type from user request and context.
        
        Args:
            user_request: The user's request text
            context: Optional context (file path, conversation history, etc)
            
        Returns:
            DetectionResult with type and confidence
        """
        logger.info(f"Detecting content type from: '{user_request[:100]}'")
        
        if context is None:
            context = {}
        
        # Score each type
        scores = {}
        all_signals = {}
        
        for content_type, patterns in self.PATTERNS.items():
            score, signals = self._score_type(
                user_request, context, content_type, patterns
            )
            scores[content_type] = score
            all_signals[content_type] = signals
        
        # Get best match
        best_type = max(scores, key=scores.get)
        best_score = scores[best_type]
        
        # Normalize confidence (0-1)
        confidence = min(best_score / 10.0, 1.0)
        
        # If confidence too low, default to "doc"
        if confidence < 0.3:
            logger.warning(f"Low confidence ({confidence}), defaulting to 'doc'")
            best_type = "doc"
            confidence = 0.5
        
        logger.info(f"✓ Detected: {best_type} (confidence: {confidence:.2f})")
        
        return DetectionResult(
            content_type=best_type,
            confidence=confidence,
            signals=all_signals[best_type],
            metadata={
                "all_scores": scores,
                "request_length": len(user_request)
            }
        )
    
    def _score_type(
        self,
        request: str,
        context: Dict,
        content_type: str,
        patterns: Dict
    ) -> Tuple[float, List[str]]:
        """
        Score how well a content type matches the request.
        
        Returns:
            (score, list_of_matching_signals)
        """
        score = 0.0
        signals = []
        
        request_lower = request.lower()
        
        # Check keywords
        for keyword in patterns["keywords"]:
            if keyword in request_lower:
                score += 3.0
                signals.append(f"keyword: {keyword}")
        
        # Check regex indicators
        for pattern in patterns["indicators"]:
            if re.search(pattern, request_lower):
                score += 2.0
                signals.append(f"pattern: {pattern}")
        
        # Check file extension context
        if "file_path" in context:
            file_ext = context["file_path"].split(".")[-1]
            if f".{file_ext}" in patterns["file_extensions"]:
                score += 4.0
                signals.append(f"file_ext: .{file_ext}")
        
        # Check explicit type mention
        if content_type in request_lower:
            score += 5.0
            signals.append(f"explicit: {content_type}")
        
        return score, signals
    
    def detect_from_file_path(self, file_path: str) -> str:
        """
        Quick detection from file path alone.
        
        Useful for batch processing.
        """
        file_lower = file_path.lower()
        
        if "linkedin" in file_lower or "twitter" in file_lower or "social" in file_lower:
            return "social"
        elif "email" in file_lower or ".eml" in file_lower:
            return "email"
        elif "blog" in file_lower or "article" in file_lower:
            return "blog"
        elif "note" in file_lower or "scratch" in file_lower:
            return "note"
        else:
            return "doc"


def main():
    """Test/demo of detector"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Content Type Detector")
    parser.add_argument("request", help="User request to analyze")
    parser.add_argument("--file", help="File path context (optional)")
    
    args = parser.parse_args()
    
    detector = ContentTypeDetector()
    
    context = {}
    if args.file:
        context["file_path"] = args.file
    
    result = detector.detect(args.request, context)
    
    print("\n" + "="*80)
    print("DETECTION RESULT")
    print("="*80)
    print(f"\nType: {result.content_type}")
    print(f"Confidence: {result.confidence:.2f}")
    print(f"\nSignals:")
    for signal in result.signals:
        print(f"  - {signal}")
    print(f"\nAll Scores:")
    for type_name, score in result.metadata["all_scores"].items():
        print(f"  {type_name}: {score:.1f}")
    print("\n" + "="*80)
    
    return 0


if __name__ == "__main__":
    exit(main())
