#!/usr/bin/env python3
"""
Analyze N5 conversations.db to tune persona router
Extract objectives and titles to understand actual usage patterns
"""

import sqlite3
import json
from collections import defaultdict, Counter
from pathlib import Path

def categorize_objective(text: str) -> list[str]:
    """Categorize what persona should handle this objective"""
    if not text:
        return ['operator']
    
    text_lower = text.lower()
    personas = []
    
    # Researcher patterns
    research_patterns = [
        'research', 'find', 'search', 'scan', 'look up', 'investigate', 
        'explore', 'discover', 'gather', 'collect information', 'analyze data'
    ]
    if any(p in text_lower for p in research_patterns):
        personas.append('researcher')
    
    # Strategist patterns
    strategy_patterns = [
        'strategy', 'should we', 'should i', 'decision', 'options', 'approach',
        'recommend', 'best way', 'choose', 'plan', 'roadmap', 'framework'
    ]
    if any(p in text_lower for p in strategy_patterns):
        personas.append('strategist')
    
    # Teacher patterns
    teaching_patterns = [
        'explain', 'how does', 'what is', 'understand', 'learn', 'teach me',
        'why does', 'clarify', 'help me understand', 'walk me through'
    ]
    if any(p in text_lower for p in teaching_patterns):
        personas.append('teacher')
    
    # Builder patterns
    builder_patterns = [
        'build', 'create', 'implement', 'develop', 'code', 'write script',
        'make', 'construct', 'set up', 'install', 'configure', 'deploy'
    ]
    if any(p in text_lower for p in builder_patterns):
        personas.append('builder')
    
    # Writer patterns
    writer_patterns = [
        'write', 'draft', 'compose', 'document', 'summarize', 'email',
        'post', 'article', 'blog', 'content', 'copy'
    ]
    if any(p in text_lower for p in writer_patterns):
        personas.append('writer')
    
    # Debugger patterns
    debugger_patterns = [
        'debug', 'fix', 'error', 'bug', 'broken', 'not working', 'issue',
        'troubleshoot', 'diagnose', 'repair', 'resolve'
    ]
    if any(p in text_lower for p in debugger_patterns):
        personas.append('debugger')
    
    # Architect patterns
    architect_patterns = [
        'design', 'architecture', 'system design', 'structure', 'organize',
        'framework', 'pattern', 'model', 'schema'
    ]
    if any(p in text_lower for p in architect_patterns):
        personas.append('architect')
    
    # Operator patterns (execution, coordination)
    operator_patterns = [
        'execute', 'run', 'move', 'copy', 'delete', 'organize files',
        'workflow', 'orchestrate', 'coordinate'
    ]
    if any(p in text_lower for p in operator_patterns):
        personas.append('operator')
    
    return personas if personas else ['operator']

def extract_keywords(text: str, min_word_len=4) -> list[str]:
    """Extract significant keywords from text"""
    if not text:
        return []
    
    # Simple keyword extraction
    words = text.lower().split()
    keywords = []
    
    # Common words to skip
    skip_words = {
        'the', 'and', 'with', 'for', 'from', 'this', 'that', 'these', 'those',
        'have', 'been', 'will', 'only', 'also', 'more', 'than', 'into', 'such',
        'over', 'some', 'them', 'about', 'after', 'before', 'through'
    }
    
    for word in words:
        # Clean word
        word = word.strip('.,;:!?"\'()[]{}')
        if len(word) >= min_word_len and word not in skip_words:
            keywords.append(word)
    
    return keywords

def main():
    db_path = "/home/workspace/N5/data/conversations.db"
    
    print("Analyzing N5 conversations database...\n")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get recent conversations with objectives
    cursor.execute("""
        SELECT id, title, objective, focus, type, created_at 
        FROM conversations 
        WHERE objective IS NOT NULL AND objective != ''
        ORDER BY created_at DESC 
        LIMIT 50
    """)
    
    conversations = cursor.fetchall()
    print(f"Analyzing {len(conversations)} conversations with objectives\n")
    
    persona_distribution = Counter()
    persona_samples = defaultdict(list)
    keyword_by_persona = defaultdict(Counter)
    
    for conv in conversations:
        conv_id, title, objective, focus, conv_type, created_at = conv
        
        personas = categorize_objective(objective)
        keywords = extract_keywords(objective)
        
        for persona in personas:
            persona_distribution[persona] += 1
            persona_samples[persona].append({
                'id': conv_id,
                'title': title,
                'objective': objective[:150],
                'keywords': keywords[:5]
            })
            
            # Track keywords for each persona
            for kw in keywords:
                keyword_by_persona[persona][kw] += 1
    
    # Print results
    print("="*70)
    print("PERSONA DISTRIBUTION (from 50 real conversations)")
    print("="*70)
    
    for persona, count in persona_distribution.most_common():
        percentage = (count / len(conversations)) * 100
        print(f"\n{persona.upper()}: {count} conversations ({percentage:.1f}%)")
        print("-" * 50)
        
        # Show top 3 examples
        for i, sample in enumerate(persona_samples[persona][:3], 1):
            print(f"{i}. {sample['objective']}")
            if sample['keywords']:
                print(f"   Keywords: {', '.join(sample['keywords'])}")
    
    # Print top keywords per persona
    print("\n" + "="*70)
    print("TOP KEYWORDS BY PERSONA")
    print("="*70)
    
    for persona in ['researcher', 'strategist', 'builder', 'debugger', 'writer', 'teacher']:
        if persona in keyword_by_persona:
            top_keywords = keyword_by_persona[persona].most_common(10)
            print(f"\n{persona.upper()}:")
            print(", ".join([f"{kw} ({count})" for kw, count in top_keywords]))
    
    # Save detailed results
    output = {
        'total_analyzed': len(conversations),
        'persona_distribution': dict(persona_distribution),
        'samples_by_persona': {k: v[:5] for k, v in persona_samples.items()},
        'top_keywords_by_persona': {
            persona: dict(keywords.most_common(15))
            for persona, keywords in keyword_by_persona.items()
        }
    }
    
    output_path = Path("/home/.z/workspaces/con_MkzEBdTNQKB8hgj2/conversation_analysis_results.json")
    output_path.write_text(json.dumps(output, indent=2))
    
    print(f"\n\nDetailed results saved to: {output_path}")
    print("\nUse these patterns to enhance persona_router.py triggers")
    
    conn.close()

if __name__ == "__main__":
    main()
