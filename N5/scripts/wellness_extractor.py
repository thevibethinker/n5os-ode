#!/usr/bin/env python3
"""
Simple LLM Extractor
Extracts structured wellness metrics from natural language journal entries using a simple heuristic/rule-based approach first,
but architected to swap in a real LLM call if the user installs one.

For now, this uses a robust "Pseudo-LLM" keyword matching system to fulfill the user's request for "flexible trust"
without needing an external API key configured immediately.

Metrics:
- Mood Score (-1, 0, 1)
- Diet Score (1-5)
- Late Night Eating (0, 1)
"""

import re
import sys
import json

def extract_mood_score(text: str, emoji_char: str = None) -> int:
    """
    Extract mood score (-1, 0, 1) from text or emoji.
    Priority: Explicit score > Emoji > Sentiment Keywords
    """
    text = text.lower()
    
    # 1. Explicit Score? (e.g. "mood was -1", "mood: 1")
    # Matches "mood is/was/:" followed by optional space/sign and 0 or 1 or -1
    match = re.search(r'mood\s*(?:was|is|:)?\s*(-?1|0)', text)
    if match:
        return int(match.group(1))

    # 2. Emoji Mapping
    positive_emojis = ["🙂", "😀", "😃", "😄", "😁", "😆", "😅", "😂", "🤣", "😊", "😇", "🙂", "🙃", "😉", "😌", "😍", "🥰", "😘", "😗", "😙", "😚", "😋", "😛", "😝", "😜", "🤪", "🤨", "🧐", "🤓", "😎", "🤩", "🥳", "😏", "😒", "😞", "😔", "😟", "😕", "🙁", "☹️", "😣", "😖", "😫", "😩", "🥺", "😢", "😭", "😤", "😠", "😡", "🤬", "🤯", "😳", "🥵", "🥶", "😱", "😨", "😰", "😥", "😓", "🤗", "🤔", "🤭", "🤫", "🤥", "😶", "😐", "😑", "😬", "🙄", "😯", "😦", "😧", "😮", "😲", "🥱", "😴", "🤤", "😪", "😵", "🤐", "🥴", "🤢", "🤮", "🤧", "😷", "🤒", "🤕", "🤑", "🤠", "😈", "👿", "👹", "👺", "🤡", "💩", "👻", "💀", "☠️", "👽", "👾", "🤖", "🎃", "😺", "😸", "😹", "😻", "😼", "😽", "🙀", "😿", "😾"]
    # Simple mapping (refined list)
    pos_set = {"🙂", "😀", "😃", "😄", "😁", "😆", "😊", "😇", "😉", "😌", "😍", "🥰", "😎", "🤩", "🥳", "💪", "⚡", "🔥", "🚀", "☀️", "📈", "✅"}
    neg_set = {"😡", "🤬", "😠", "😤", "😭", "😢", "☹️", "🙁", "😕", "😟", "😔", "😞", "😒", "😫", "😩", "😖", "😣", "🥀", "📉", "❌", "🤒", "🤢", "🤮"}
    
    if emoji_char:
        if emoji_char in pos_set: return 1
        if emoji_char in neg_set: return -1
        return 0 # Default to neutral for others

    # 3. Sentiment Keywords
    pos_words = ["great", "good", "happy", "excited", "focused", "productive", "energetic", "awesome", "excellent"]
    neg_words = ["bad", "sad", "angry", "frustrated", "tired", "exhausted", "stressed", "anxious", "terrible", "awful"]
    
    pos_count = sum(1 for w in pos_words if w in text)
    neg_count = sum(1 for w in neg_words if w in text)
    
    if pos_count > neg_count: return 1
    if neg_count > pos_count: return -1
    return 0

def extract_diet_score(text: str) -> int:
    """
    Extract diet score (1-5) from text.
    Priority: Explicit score > Keyword heuristic
    """
    text = text.lower()
    
    # 1. Explicit Score? (e.g. "diet: 4/5", "score 3")
    match = re.search(r'(?:diet|food|eating)\s*(?:was|is|:)?\s*([1-5])\s*(?:/|out of)?\s*5?', text)
    if match:
        return int(match.group(1))
    
    # 2. Heuristic Scoring
    # Base score = 3
    score = 3
    
    healthy_words = ["salad", "vegetables", "veggies", "fruit", "chicken", "fish", "salmon", "clean", "healthy", "water", "protein", "oats", "oatmeal"]
    junk_words = ["pizza", "burger", "fries", "sugar", "candy", "chocolate", "cake", "alcohol", "beer", "wine", "fried", "greasy", "fast food", "soda", "coke"]
    
    # Adjust
    if any(w in text for w in healthy_words): score += 1
    if any(w in text for w in junk_words): score -= 1
    
    # Cap
    return max(1, min(5, score))

def extract_late_night(text: str) -> int:
    """
    Extract late night eating (0 or 1).
    """
    text = text.lower()
    
    # Explicit negation
    if "no late night" in text or "didn't eat late" in text:
        return 0
        
    # Explicit confirmation
    if "late night snack" in text or "ate late" in text or "midnight snack" in text:
        return 1
        
    return 0

def process_entry(entry_text: str, mood_emoji: str = None):
    """Main extraction pipeline."""
    return {
        "mood_score": extract_mood_score(entry_text, mood_emoji),
        "diet_score": extract_diet_score(entry_text),
        "late_night": extract_late_night(entry_text)
    }

if __name__ == "__main__":
    # Test mode
    if len(sys.argv) > 1:
        text = sys.argv[1]
        emoji = sys.argv[2] if len(sys.argv) > 2 else None
        print(json.dumps(process_entry(text, emoji), indent=2))

